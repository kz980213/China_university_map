export interface School {
  id: number
  name: string
  englishName?: string
  schoolCode: string
  province: string
  city: string
  district?: string
  address?: string
  longitude?: number
  latitude?: number
  level: '本科' | '专科' | '高职'
  schoolType: '综合类' | '理工类' | '师范类' | '医药类' | '财经类' | '政法类' | '艺术类' | '体育类' | '其他'
  ownership: '公办' | '民办' | '中外合作'
  is985: boolean
  is211: boolean
  isDoubleFirstClass: boolean
  website?: string
  admissionWebsite?: string
  description?: string
  popularMajors: string[]
}

export interface ProvinceStat {
  province: string
  total: number
  undergraduateCount: number
  juniorCollegeCount: number
  count985: number
  count211: number
  doubleFirstClassCount: number
}

export interface SchoolFilter {
  keyword: string
  levels: string[]
  tags: string[]
  ownerships: string[]
  schoolTypes: string[]
  province?: string
  year?: number
  subjectType?: string
}
