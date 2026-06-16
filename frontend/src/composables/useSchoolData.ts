import { ref } from 'vue'
import type { School } from '@/types/school'
import type { AdmissionScore } from '@/types/admission'
import type { SchoolMajor } from '@/types/major'
import { useApiMode } from './useApiMode'
import { fetchSchools, fetchSchoolDetail, fetchAdmissionScores, fetchSchoolMajors } from '@/api'
import { mockSchools } from '@/mock/schools'
import { mockAdmissionScores } from '@/mock/admissionScores'
import { mockSchoolMajors } from '@/mock/schoolMajors'
import { PROVINCE_STATS } from '@/constants/provinceStats'

export function useSchoolData() {
  const { isApiMode } = useApiMode()

  // ── 学校列表 ──
  const schools = ref<School[]>([])
  const schoolsTotal = ref(0)
  const schoolCounts = ref({
    undergraduateCount: 0,
    juniorCollegeCount: 0,
    count985: 0,
    count211: 0,
    doubleFirstClassCount: 0,
  })
  const schoolsLoading = ref(false)
  const schoolsError = ref<string | null>(null)

  async function loadSchools(params: Record<string, unknown> = {}) {
    schoolsLoading.value = true
    schoolsError.value = null
    try {
      if (isApiMode.value) {
        const data = await fetchSchools(params)
        schools.value = data.items
        schoolsTotal.value = data.total
        schoolCounts.value = {
          undergraduateCount: data.undergraduateCount ?? 0,
          juniorCollegeCount: data.juniorCollegeCount ?? 0,
          count985: data.count985 ?? 0,
          count211: data.count211 ?? 0,
          doubleFirstClassCount: data.doubleFirstClassCount ?? 0,
        }
      } else {
        // Mock mode: local filter
        let result = [...mockSchools]
        if (params.province) result = result.filter(s => s.province === params.province)
        if (params.keyword) {
          const kw = String(params.keyword).toLowerCase()
          result = result.filter(s => s.name.toLowerCase().includes(kw) || s.city?.toLowerCase().includes(kw))
        }
        if (params.is_985 === 'true') result = result.filter(s => s.is985)
        if (params.is_211 === 'true') result = result.filter(s => s.is211)
        if (params.is_double_first_class === 'true') result = result.filter(s => s.isDoubleFirstClass)
        if (params.level) result = result.filter(s => s.level === params.level)
        if (params.school_type) result = result.filter(s => s.schoolType === params.school_type)
        if (params.ownership) result = result.filter(s => s.ownership === params.ownership)
        const page = Number(params.page) || 1
        const size = Number(params.page_size) || 20
        schoolsTotal.value = result.length
        schoolCounts.value = {
          undergraduateCount: result.filter(s => s.level === '本科').length,
          juniorCollegeCount: result.filter(s => s.level !== '本科').length,
          count985: result.filter(s => s.is985).length,
          count211: result.filter(s => s.is211).length,
          doubleFirstClassCount: result.filter(s => s.isDoubleFirstClass).length,
        }
        schools.value = result.slice((page - 1) * size, page * size)
      }
    } catch (e: any) {
      schoolsError.value = e.message || '加载失败'
      schools.value = []
    } finally {
      schoolsLoading.value = false
    }
  }

  // ── 学校详情 ──
  const schoolDetail = ref<School | null>(null)
  const detailLoading = ref(false)
  const detailError = ref<string | null>(null)

  async function loadSchoolDetail(id: number) {
    detailLoading.value = true
    detailError.value = null
    try {
      if (isApiMode.value) {
        schoolDetail.value = await fetchSchoolDetail(id)
      } else {
        schoolDetail.value = mockSchools.find(s => s.id === id) || null
      }
    } catch (e: any) {
      detailError.value = e.message || '加载失败'
      schoolDetail.value = null
    } finally {
      detailLoading.value = false
    }
  }

  // ── 分数线 ──
  const admissionScores = ref<AdmissionScore[]>([])
  const scoresLoading = ref(false)
  const scoresError = ref<string | null>(null)

  async function loadAdmissionScores(schoolId: number, params: Record<string, unknown> = {}) {
    scoresLoading.value = true
    scoresError.value = null
    try {
      if (isApiMode.value) {
        admissionScores.value = await fetchAdmissionScores(schoolId, params)
      } else {
        let result = mockAdmissionScores.filter(s => s.schoolId === schoolId)
        if (params.student_province) result = result.filter(s => s.studentProvince === params.student_province)
        if (params.subject_type) result = result.filter(s => s.subjectType === params.subject_type)
        if (params.year_from) result = result.filter(s => s.year >= Number(params.year_from))
        if (params.year_to) result = result.filter(s => s.year <= Number(params.year_to))
        admissionScores.value = result.sort((a, b) => a.year - b.year)
      }
    } catch (e: any) {
      scoresError.value = e.message || '加载失败'
      admissionScores.value = []
    } finally {
      scoresLoading.value = false
    }
  }

  // ── 省份统计（前端常量，不走接口）──
  const provinceStats = ref(PROVINCE_STATS)
  const statsLoading = ref(false)

  function loadProvinceStats() {
    // 数据已内置为常量，无需异步请求
  }

  // ── 学校专业 ──
  const schoolMajors = ref<any[]>([])
  const majorsLoading = ref(false)
  const majorsError = ref<string | null>(null)

  async function loadSchoolMajors(schoolId: number) {
    majorsLoading.value = true
    majorsError.value = null
    try {
      if (isApiMode.value) {
        schoolMajors.value = await fetchSchoolMajors(schoolId)
      } else {
        schoolMajors.value = mockSchoolMajors.filter(sm => sm.schoolId === schoolId)
      }
    } catch (e: any) {
      majorsError.value = e.message || '加载失败'
      schoolMajors.value = []
    } finally {
      majorsLoading.value = false
    }
  }

  return {
    // school list
    schools, schoolsTotal, schoolCounts, schoolsLoading, schoolsError, loadSchools,
    // detail
    schoolDetail, detailLoading, detailError, loadSchoolDetail,
    // admission
    admissionScores, scoresLoading, scoresError, loadAdmissionScores,
    // stats
    provinceStats, statsLoading, loadProvinceStats,
    // majors
    schoolMajors, majorsLoading, majorsError, loadSchoolMajors,
  }
}