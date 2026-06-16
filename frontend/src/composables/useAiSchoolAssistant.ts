import { ref } from 'vue'
import type { School } from '@/types/school'
import type { ChatMessage, ChatRole } from '@/types/ai'

const _API_BASE = (import.meta.env.VITE_API_BASE_URL ?? '') + '/api'

const _PROVINCES = [
  '北京', '上海', '天津', '重庆',
  '河北', '山西', '辽宁', '吉林', '黑龙江',
  '江苏', '浙江', '安徽', '福建', '江西', '山东',
  '河南', '湖北', '湖南', '广东', '海南',
  '四川', '贵州', '云南', '陕西', '甘肃', '青海',
  '内蒙古', '广西', '西藏', '新疆', '宁夏',
]
const _TAGS = ['985', '211', '双一流']
const _LEVELS = ['本科', '专科', '高职']
const _SCHOOL_TYPES = ['综合类', '理工类', '师范类', '医药类', '财经类', '政法类', '艺术类', '体育类', '其他']
const _MAJOR_KEYWORDS = ['计算机', '人工智能', '软件工程', '物理', '金融', '医学', '法学', '师范']

export type AiProvider = 'claude' | 'deepseek'

function generateId(): string {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 8)
}

function extractSuggestedFilter(input: string): ChatMessage['suggestedFilter'] {
  const province = _PROVINCES.find((p) => input.includes(p))
  const tags = _TAGS.filter((t) => input.includes(t))
  const levels = _LEVELS.filter((l) => input.includes(l))
  const schoolTypes = _SCHOOL_TYPES.filter((t) => input.includes(t))
  const keyword = _MAJOR_KEYWORDS.find((m) => input.includes(m))

  const filter: ChatMessage['suggestedFilter'] = {}
  if (province) filter!.province = province
  if (tags.length) filter!.tags = tags
  if (levels.length) filter!.levels = levels as School['level'][]
  if (schoolTypes.length) filter!.schoolTypes = schoolTypes as School['schoolType'][]
  if (keyword) filter!.keyword = keyword

  return Object.keys(filter!).length > 0 ? filter : undefined
}

export function useAiSchoolAssistant() {
  const messages = ref<ChatMessage[]>([])
  const isThinking = ref(false)
  const provider = ref<AiProvider>('deepseek')

  function addUserMessage(text: string): ChatMessage {
    const msg: ChatMessage = {
      id: generateId(),
      role: 'user' as ChatRole,
      content: text,
      createdAt: Date.now(),
    }
    messages.value.push(msg)
    return msg
  }

  async function processQuery(input: string): Promise<ChatMessage> {
    isThinking.value = true

    // 历史消息：当前 messages 末尾已有新 user 消息，取其之前的所有条目
    const history = messages.value
      .slice(0, -1)
      .map((m) => ({ role: m.role, content: m.content }))

    // 预先推入一条空的 assistant 消息，内容随流式数据逐步填充
    const assistantMsg: ChatMessage = {
      id: generateId(),
      role: 'assistant' as ChatRole,
      content: '',
      createdAt: Date.now(),
      suggestedFilter: extractSuggestedFilter(input),
    }
    messages.value.push(assistantMsg)

    try {
      const resp = await fetch(`${_API_BASE}/ai/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input, history, provider: provider.value }),
      })

      if (!resp.ok || !resp.body) {
        assistantMsg.content = `请求失败（${resp.status}），请稍后重试。`
        isThinking.value = false
        return assistantMsg
      }

      // 连接成功，关闭 thinking 指示器，开始展示流式内容
      isThinking.value = false

      const reader = resp.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const parts = buffer.split('\n\n')
        buffer = parts.pop() ?? ''
        for (const part of parts) {
          if (!part.startsWith('data: ')) continue
          const data = part.slice(6)
          if (data === '[DONE]') break
          try {
            const parsed = JSON.parse(data)
            if (parsed.chunk) assistantMsg.content += parsed.chunk
          } catch {
            // 忽略格式异常的数据块
          }
        }
      }
    } catch {
      assistantMsg.content = '网络错误，请检查连接后重试。'
      isThinking.value = false
    }

    return assistantMsg
  }

  function clearMessages() {
    messages.value = []
  }

  return {
    messages,
    isThinking,
    provider,
    addUserMessage,
    processQuery,
    clearMessages,
  }
}
