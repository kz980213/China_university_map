"""AI 问答路由：POST /api/ai/chat，返回 SSE 流式响应。"""

from typing import Literal

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.ai_service import stream_chat

router = APIRouter(prefix="/api/ai", tags=["ai"])


class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []
    provider: Literal['claude', 'deepseek'] = 'claude'


@router.post("/chat")
async def chat(req: ChatRequest, db: Session = Depends(get_db)):
    return StreamingResponse(
        stream_chat(db, req.message, req.history, req.provider),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
