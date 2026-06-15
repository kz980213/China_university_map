import { ref, computed, watch, type Ref } from 'vue'
import type { School, SchoolFilter } from '@/types/school'
import { useSchoolData } from './useSchoolData'
import { mockSchools } from '@/mock/schools'

const defaultFilter = (): SchoolFilter => ({
  keyword: '',
  levels: [],
  tags: [],
  ownerships: [],
  schoolTypes: [],
  province: undefined,
  year: undefined,
  subjectType: undefined,
})

export function useSchoolFilter(schools: Ref<School[]> = ref(mockSchools)) {
  const filter = ref<SchoolFilter>(defaultFilter())
  const selectedProvince = ref<string | undefined>(undefined)
  const currentPage = ref(1)
  const pageSize = ref(30)

  // ── 从 useSchoolData 获取 API 数据 ──
  const {
    schools: apiSchools,
    schoolsTotal,
    schoolCounts,
    schoolsLoading,
    schoolsError,
    loadSchools,
    provinceStats,
    statsLoading,
    loadProvinceStats,
  } = useSchoolData()

  // 初始加载：省份统计 + 默认学校列表
  loadProvinceStats()
  loadSchools({ page: 1, page_size: pageSize.value })

  function buildParams(page: number) {
    const params: Record<string, unknown> = { page, page_size: pageSize.value }
    if (filter.value.keyword) params.keyword = filter.value.keyword
    if (filter.value.province) params.province = filter.value.province
    if (filter.value.levels.length === 1) params.level = filter.value.levels[0]
    if (filter.value.tags.length) {
      if (filter.value.tags.includes('985')) params.is_985 = 'true'
      if (filter.value.tags.includes('211')) params.is_211 = 'true'
      if (filter.value.tags.includes('双一流')) params.is_double_first_class = 'true'
    }
    if (filter.value.ownerships.length === 1) params.ownership = filter.value.ownerships[0]
    if (filter.value.schoolTypes.length === 1) params.school_type = filter.value.schoolTypes[0]
    return params
  }

  // 当 filter 变化时 → 回到第1页重新请求
  let debounceTimer: ReturnType<typeof setTimeout> | null = null
  watch(filter, () => {
    if (debounceTimer) clearTimeout(debounceTimer)
    debounceTimer = setTimeout(() => {
      currentPage.value = 1
      loadSchools(buildParams(1))
    }, 150)
  }, { deep: true })

  // 翻页
  function goToPage(page: number) {
    currentPage.value = page
    loadSchools(buildParams(page))
  }

  const totalPages = computed(() => Math.max(1, Math.ceil(schoolsTotal.value / pageSize.value)))

  const filteredSchools = computed<School[]>(() => apiSchools.value)

  const allSchools = computed<School[]>(() => schools.value)

  // 直接使用 API 返回的聚合计数，已反映所有筛选条件（省份、985/211、层次、类型等）
  const provinceStatCounts = computed(() => ({
    total: schoolsTotal.value,
    ...schoolCounts.value,
  }))

  const statCounts = computed(() => provinceStatCounts.value)

  function setKeyword(keyword: string) {
    filter.value.keyword = keyword
  }

  function setProvince(province: string | undefined) {
    filter.value.province = province
    selectedProvince.value = province
    filter.value.keyword = ''
  }

  function updateFilter(partial: Partial<SchoolFilter>) {
    Object.assign(filter.value, partial)
  }

  function setPageSize(size: number) {
    pageSize.value = size
    currentPage.value = 1
    loadSchools(buildParams(1))
  }

  function resetFilter() {
    filter.value = defaultFilter()
    selectedProvince.value = undefined
  }

  return {
    filter,
    selectedProvince,
    filteredSchools,
    allSchools,
    provinceStatCounts,
    statCounts,
    schoolsLoading,
    schoolsError,
    schoolsTotal,
    provinceStats,
    currentPage,
    pageSize,
    totalPages,
    goToPage,
    setPageSize,
    setKeyword,
    setProvince,
    updateFilter,
    resetFilter,
    loadSchools,
  }
}