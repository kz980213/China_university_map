"""AI 问答服务：从数据库构建上下文，支持 Claude 和 DeepSeek 流式回答。"""

import json
from typing import AsyncGenerator

import anthropic
import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.models.school import School

_PROVINCES = [
    '北京', '上海', '天津', '重庆',
    '河北', '山西', '辽宁', '吉林', '黑龙江',
    '江苏', '浙江', '安徽', '福建', '江西', '山东',
    '河南', '湖北', '湖南', '广东', '海南',
    '四川', '贵州', '云南', '陕西', '甘肃', '青海',
    '内蒙古', '广西', '西藏', '新疆', '宁夏',
]


def _extract_entities(message: str) -> dict:
    province = next((p for p in _PROVINCES if p in message), None)
    tags: list[str] = []
    if '985' in message:
        tags.append('985')
    if '211' in message:
        tags.append('211')
    if '双一流' in message:
        tags.append('双一流')
    return {'province': province, 'tags': tags}


def _build_context(db: Session, province: str | None, tags: list[str]) -> str:
    q = db.query(School)
    if province:
        q = q.filter(School.province == province)
    if '985' in tags:
        q = q.filter(School.is_985 == True)  # noqa: E712
    elif '211' in tags:
        q = q.filter(School.is_211 == True)  # noqa: E712
    elif '双一流' in tags:
        q = q.filter(School.is_double_first_class == True)  # noqa: E712

    schools = q.limit(30).all()
    if not schools:
        schools = db.query(School).limit(20).all()

    lines = []
    for s in schools:
        tag_parts = []
        if s.is_985:
            tag_parts.append('985')
        if s.is_211:
            tag_parts.append('211')
        if s.is_double_first_class:
            tag_parts.append('双一流')
        tag_str = ('，' + '/'.join(tag_parts)) if tag_parts else ''
        lines.append(
            f"- {s.name}（{s.province}{s.city}，{s.level}，{s.school_type}，{s.ownership}{tag_str}）"
        )

    return '\n'.join(lines) if lines else '（暂无匹配院校数据）'


def _build_system_prompt(context: str) -> str:
    return f"""你是一个专业的中国高校信息助手，帮助学生了解全国各院校情况。
以下是与本次问题相关的院校数据（可能是筛选后的子集）：

{context}

回答要求：
1. 基于上述数据给出准确、简洁的中文回答。
2. 涉及多所学校时，逐条列举，每校单独一行。
3. 数据不足以回答时，如实说明并建议使用平台筛选功能进一步查询。
4. 不要编造数据中没有的学校或信息。
5. 回答控制在 300 字以内，重点突出。"""


def _build_history(history: list[dict], message: str) -> list[dict]:
    """整理对话历史，最多保留最近 6 轮（12 条）。"""
    api_messages: list[dict] = []
    for h in history[-12:]:
        role = h.get('role')
        content = h.get('content', '').strip()
        if role in ('user', 'assistant') and content:
            api_messages.append({'role': role, 'content': content})
    api_messages.append({'role': 'user', 'content': message})
    return api_messages


async def _stream_claude(
    system: str,
    messages: list[dict],
) -> AsyncGenerator[str, None]:
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    async with client.messages.stream(
        model='claude-opus-4-8',
        max_tokens=4096,
        thinking={'type': 'adaptive'},
        system=system,
        messages=messages,
    ) as stream:
        async for text in stream.text_stream:
            yield f"data: {json.dumps({'chunk': text}, ensure_ascii=False)}\n\n"


async def _stream_deepseek(
    system: str,
    messages: list[dict],
) -> AsyncGenerator[str, None]:
    # DeepSeek 兼容 OpenAI 格式；system 作为第一条消息传入
    api_messages = [{'role': 'system', 'content': system}] + messages
    async with httpx.AsyncClient(timeout=60) as client:
        async with client.stream(
            'POST',
            'https://api.deepseek.com/chat/completions',
            headers={
                'Authorization': f'Bearer {settings.deepseek_api_key}',
                'Content-Type': 'application/json',
            },
            json={
                'model': 'deepseek-v4-pro',
                'messages': api_messages,
                'stream': True,
            },
        ) as resp:
            async for line in resp.aiter_lines():
                if not line.startswith('data: '):
                    continue
                data = line[6:]
                if data == '[DONE]':
                    break
                try:
                    parsed = json.loads(data)
                    text = parsed['choices'][0]['delta'].get('content', '')
                    if text:
                        yield f"data: {json.dumps({'chunk': text}, ensure_ascii=False)}\n\n"
                except Exception:
                    pass


async def stream_chat(
    db: Session,
    message: str,
    history: list[dict],
    provider: str = 'claude',
) -> AsyncGenerator[str, None]:
    """主入口：按 provider 路由到对应 LLM，统一输出 SSE 格式。"""
    entities = _extract_entities(message)
    context = _build_context(db, entities['province'], entities['tags'])
    system = _build_system_prompt(context)
    messages = _build_history(history, message)

    if provider == 'deepseek':
        gen = _stream_deepseek(system, messages)
    else:
        gen = _stream_claude(system, messages)

    async for chunk in gen:
        yield chunk

    yield 'data: [DONE]\n\n'
