export type SubjectType = '理科' | '文科' | '物理类' | '历史类' | '综合改革'

export interface AdmissionScore {
  id: number
  schoolId?: number
  majorId?: number
  year: number
  studentProvince: string
  subjectType: SubjectType
  batch?: string
  majorName?: string
  minScore: number
  minRank?: number          // 源数据自带真实位次（大多空），不可被派生值覆盖
  avgScore?: number
  maxScore?: number
  enrollmentCount?: number
  remark?: string
  /** 由一分一段换算的估算位次 */
  estimatedRank?: number
  /** ConversionResult.reason: ok / floored / out_of_range / no_data */
  estimatedRankReason?: string
  isSchoolLevel: boolean    // 院校线 vs 专业线
  matchStatus?: string      // matched / partial / unmatched
}
