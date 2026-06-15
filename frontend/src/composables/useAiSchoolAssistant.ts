import { ref } from 'vue'
import type { School } from '@/types/school'
import type { ChatMessage, ChatRole, AiQueryResult } from '@/types/ai'
import { mockSchools } from '@/mock/schools'
import { mockSchoolMajors } from '@/mock/schoolMajors'
import { mockMajors } from '@/mock/majors'
import { mockAdmissionScores } from '@/mock/admissionScores'

const ALL_PROVINCES = ['北京', '上海', '江苏', '广东', '浙江', '湖北', '四川']

const ALL_TAGS = ['985', '211', '双一流']

const ALL_LEVELS: School['level'][] = ['本科', '专科', '高职']

const ALL_SCHOOL_TYPES: School['schoolType'][] = [
  '综合类', '理工类', '师范类', '医药类', '财经类', '政法类', '艺术类', '体育类', '其他',
]

const MAJOR_KEYWORDS = [
  '计算机', '人工智能', '软件工程', '物理', '金融', '医学', '法学', '师范',
]

function buildQuickReply(): string {
  return '你可以问我：江苏有哪些985？或者：有哪些学校有计算机专业？'
}

function generateId(): string {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 8)
}

function identifyProvince(input: string): string | undefined {
  return ALL_PROVINCES.find((p) => input.includes(p))
}

function identifyTags(input: string): string[] {
  return ALL_TAGS.filter((t) => input.includes(t))
}

function identifyLevels(input: string): School['level'][] {
  return ALL_LEVELS.filter((l) => input.includes(l))
}

function identifySchoolTypes(input: string): School['schoolType'][] {
  return ALL_SCHOOL_TYPES.filter((t) => input.includes(t))
}

function identifyMajorKeyword(input: string): string | undefined {
  return MAJOR_KEYWORDS.find((m) => input.includes(m))
}

function identifySchoolName(input: string): School | undefined {
  return mockSchools.find((s) => input.includes(s.name))
}

function querySchoolMajors(input: string): { school: School; majors: string[] } | undefined {
  const school = identifySchoolName(input)
  if (!school) return undefined
  const schoolMajors = mockSchoolMajors.filter((sm) => sm.schoolId === school.id)
  if (schoolMajors.length === 0) return { school, majors: [] }
  const majorNames = schoolMajors
    .map((sm) => {
      const major = mockMajors.find((m) => m.id === sm.majorId)
      return major?.name
    })
    .filter(Boolean) as string[]
  return { school, majors: majorNames }
}

function querySchoolAdmission(input: string): { school: School; scores: number[]; ranks: number[] } | undefined {
  const school = identifySchoolName(input)
  if (!school) return undefined
  const scores = mockAdmissionScores.filter((s) => s.schoolId === school.id)
  if (scores.length === 0) return undefined
  const minScores = scores.map((s) => s.minScore)
  const minRanks = scores.map((s) => s.minRank).filter((r): r is number => r != null)
  return { school, scores: minScores, ranks: minRanks }
}

function searchSchools(conditions: {
  province?: string
  tags?: string[]
  levels?: string[]
  schoolTypes?: string[]
  majorKeyword?: string
}): School[] {
  let result = [...mockSchools]

  if (conditions.province) {
    result = result.filter((s) => s.province === conditions.province)
  }
  if (conditions.tags && conditions.tags.length > 0) {
    result = result.filter((s) =>
      conditions.tags!.some((tag) => {
        if (tag === '985') return s.is985
        if (tag === '211') return s.is211
        if (tag === '双一流') return s.isDoubleFirstClass
        return false
      })
    )
  }
  if (conditions.levels && conditions.levels.length > 0) {
    result = result.filter((s) => conditions.levels!.includes(s.level))
  }
  if (conditions.schoolTypes && conditions.schoolTypes.length > 0) {
    result = result.filter((s) => conditions.schoolTypes!.includes(s.schoolType))
  }
  if (conditions.majorKeyword) {
    const kw = conditions.majorKeyword.toLowerCase()
    result = result.filter((s) =>
      s.popularMajors.some((m) => m.toLowerCase().includes(kw))
    )
  }

  return result
}

function buildAnswerText(
  schools: School[],
  province: string | undefined,
  tags: string[],
  levels: string[],
  schoolTypes: string[],
  majorKeyword: string | undefined
): string {
  const parts: string[] = []

  if (province) {
    parts.push(province)
  }
  if (tags.length > 0) {
    parts.push(tags.join('、'))
  }
  if (levels.length > 0) {
    parts.push(levels.join('、'))
  }
  if (schoolTypes.length > 0) {
    parts.push(schoolTypes.join('、'))
  }
  if (majorKeyword) {
    parts.push(`有${majorKeyword}专业`)
  }

  const condition = parts.length > 0 ? parts.join('') + '的' : ''

  if (schools.length > 0) {
    const schoolNames = schools.map((s) => s.name).join('、')
    return `根据当前数据，${condition}高校有 ${schools.length} 所：${schoolNames}。`
  }

  return `暂时没有在当前数据中找到匹配${condition}学校。你可以尝试换一个地区、学校属性或专业关键词。`
}

function createAssistantMessage(result: AiQueryResult): ChatMessage {
  return {
    id: generateId(),
    role: 'assistant' as ChatRole,
    content: result.answer + '\n\n*（当前结果基于 MVP mock 数据，后续接入真实数据库后会更完整。）*',
    createdAt: Date.now(),
    relatedSchools: result.relatedSchools,
    suggestedFilter: result.suggestedFilter,
  }
}

export function useAiSchoolAssistant() {
  const messages = ref<ChatMessage[]>([])
  const isThinking = ref(false)

  function addUserMessage(text: string): ChatMessage {
    const msg: ChatMessage = {
      id: generateId(),
      role: 'user',
      content: text,
      createdAt: Date.now(),
    }
    messages.value.push(msg)
    return msg
  }

  function processQuery(input: string): Promise<ChatMessage> {
    isThinking.value = true

    return new Promise((resolve) => {
      // 模拟异步延迟
      setTimeout(() => {
        const province = identifyProvince(input)
        const tags = identifyTags(input)
        const levels = identifyLevels(input)
        const schoolTypes = identifySchoolTypes(input)
        const majorKeyword = identifyMajorKeyword(input)
        const namedSchool = identifySchoolName(input)

        // 检查是否在问学校专业
        if (input.includes('专业')) {
          const majorResult = querySchoolMajors(input)
          if (majorResult) {
            if (majorResult.majors.length > 0) {
              const answer = `根据当前 mock 数据，${majorResult.school.name}包含 ${majorResult.majors.slice(0, 8).join('、')} 等专业。`
              const result: AiQueryResult = { answer, relatedSchools: [majorResult.school] }
              const msg = createAssistantMessage(result)
              messages.value.push(msg)
              isThinking.value = false
              resolve(msg)
              return
            } else {
              const answer = `目前 ${majorResult.school.name} 暂无专业 mock 数据。`
              const result: AiQueryResult = { answer, relatedSchools: [majorResult.school] }
              const msg = createAssistantMessage(result)
              messages.value.push(msg)
              isThinking.value = false
              resolve(msg)
              return
            }
          }
        }

        // 检查是否在问分数线
        if (input.includes('分数线') || input.includes('分数') || input.includes('近五年')) {
          const admissionResult = querySchoolAdmission(input)
          if (admissionResult) {
            const minScore = Math.min(...admissionResult.scores)
            const maxScore = Math.max(...admissionResult.scores)
            const minRank = Math.min(...admissionResult.ranks)
            const maxRank = Math.max(...admissionResult.ranks)
            const answer = `根据当前 mock 数据，${admissionResult.school.name}近 5 年最低分大致在 ${minScore}-${maxScore} 区间，最低位次在 ${minRank}-${maxRank} 区间。具体请打开学校详情的「录取分数」Tab 查看。`
            const result: AiQueryResult = { answer, relatedSchools: [admissionResult.school] }
            const msg = createAssistantMessage(result)
            messages.value.push(msg)
            isThinking.value = false
            resolve(msg)
            return
          }
        }

        // 如果问题中包含学校名称，直接返回该学校信息
        if (namedSchool) {
          const answer = `${namedSchool.name}位于${namedSchool.province}${namedSchool.city}${namedSchool.district ?? ''}，是一所${namedSchool.level}院校，办学性质为${namedSchool.ownership}，类型为${namedSchool.schoolType}。`
          const result: AiQueryResult = {
            answer,
            relatedSchools: [namedSchool],
          }
          const msg = createAssistantMessage(result)
          messages.value.push(msg)
          isThinking.value = false
          resolve(msg)
          return
        }

        const hasAnyCondition = province || tags.length > 0 || levels.length > 0 || schoolTypes.length > 0 || majorKeyword

        if (!hasAnyCondition) {
          const answer = buildQuickReply()
          const result: AiQueryResult = {
            answer,
            relatedSchools: [],
          }
          const msg = createAssistantMessage(result)
          messages.value.push(msg)
          isThinking.value = false
          resolve(msg)
          return
        }

        const schools = searchSchools({
          province,
          tags,
          levels,
          schoolTypes,
          majorKeyword,
        })

        const answer = buildAnswerText(schools, province, tags, levels, schoolTypes, majorKeyword)

        const suggestedFilter: {
          province?: string
          tags?: string[]
          levels?: string[]
          schoolTypes?: string[]
          keyword?: string
        } = {}
        if (province) suggestedFilter.province = province
        if (tags.length > 0) suggestedFilter.tags = tags
        if (levels.length > 0) suggestedFilter.levels = levels
        if (schoolTypes.length > 0) suggestedFilter.schoolTypes = schoolTypes
        if (majorKeyword) suggestedFilter.keyword = majorKeyword

        const result: AiQueryResult = {
          answer,
          relatedSchools: schools,
          suggestedFilter: Object.keys(suggestedFilter).length > 0 ? suggestedFilter : undefined,
        }

        const msg = createAssistantMessage(result)
        messages.value.push(msg)
        isThinking.value = false
        resolve(msg)
      }, 500)
    })
  }

  function clearMessages() {
    messages.value = []
  }

  return {
    messages,
    isThinking,
    addUserMessage,
    processQuery,
    clearMessages,
  }
}