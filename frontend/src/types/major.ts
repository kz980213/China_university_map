export interface Major {
  id: number
  name: string
  code: string
  category: string
  discipline: string
  degree: string
  duration: string
  description: string
  employmentDirection: string[]
}

export interface SchoolMajor {
  id: number
  schoolId: number
  majorId: number
  collegeName: string
  tuition?: number
  duration: string
  subjectRequirement?: string
  isNationalFirstClass: boolean
  isProvincialFirstClass: boolean
}