import type { School } from './school'

export type ChatRole = 'user' | 'assistant'

export interface ChatMessage {
  id: string
  role: ChatRole
  content: string
  createdAt: number
  relatedSchools?: School[]
  suggestedFilter?: {
    province?: string
    tags?: string[]
    levels?: string[]
    schoolTypes?: string[]
    keyword?: string
  }
}

export interface AiQueryResult {
  answer: string
  relatedSchools: School[]
  suggestedFilter?: {
    province?: string
    tags?: string[]
    levels?: string[]
    schoolTypes?: string[]
    keyword?: string
  }
}