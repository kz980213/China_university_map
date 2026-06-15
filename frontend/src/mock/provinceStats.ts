import type { ProvinceStat } from '@/types/school'
import { mockSchools } from './schools'

function computeProvinceStats(): ProvinceStat[] {
  const provinceMap = new Map<string, {
    total: number
    undergraduateCount: number
    juniorCollegeCount: number
    count985: number
    count211: number
    doubleFirstClassCount: number
  }>()

  for (const school of mockSchools) {
    const item = provinceMap.get(school.province) || {
      total: 0,
      undergraduateCount: 0,
      juniorCollegeCount: 0,
      count985: 0,
      count211: 0,
      doubleFirstClassCount: 0,
    }

    item.total++
    if (school.level === '本科') {
      item.undergraduateCount++
    } else {
      item.juniorCollegeCount++
    }
    if (school.is985) item.count985++
    if (school.is211) item.count211++
    if (school.isDoubleFirstClass) item.doubleFirstClassCount++

    provinceMap.set(school.province, item)
  }

  const result: ProvinceStat[] = []
  for (const [province, stats] of provinceMap) {
    result.push({
      province,
      ...stats,
    })
  }
  return result
}

export const mockProvinceStats: ProvinceStat[] = computeProvinceStats()