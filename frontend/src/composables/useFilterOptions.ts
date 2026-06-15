import { ref, watch, computed } from 'vue'
import { useApiMode } from './useApiMode'
import { fetchFilterProvinces, fetchFilterSubjects, fetchFilterYears } from '@/api'

const MOCK_PROVINCES = ['北京', '上海', '江苏', '广东', '浙江', '湖北', '四川']
const MOCK_SUBJECTS = ['理科', '文科', '物理类', '历史类', '综合改革']

export function useFilterOptions() {
  const { isApiMode } = useApiMode()

  // ── 省份 ──
  const provinceOptions = ref<string[]>([])
  const provincesLoading = ref(false)
  async function loadProvinces() {
    provincesLoading.value = true
    try {
      if (isApiMode.value) {
        const data = await fetchFilterProvinces()
        provinceOptions.value = data.map((p: any) => p.name)
      } else {
        provinceOptions.value = [...MOCK_PROVINCES]
      }
    } catch {
      provinceOptions.value = [...MOCK_PROVINCES]
    } finally {
      provincesLoading.value = false
    }
  }

  // ── 科类（动态，随省份+年份变化）──
  const subjectOptions = ref<string[]>([])
  const subjectsLoading = ref(false)
  let subjectProvince = ''
  let subjectYear = 2024

  function loadSubjects(province: string, year: number) {
    subjectProvince = province
    subjectYear = year
    subjectsLoading.value = true
    try {
      if (isApiMode.value && province && year) {
        fetchFilterSubjects(province, year).then(data => {
          subjectOptions.value = data.tracks
          subjectsLoading.value = false
        }).catch(() => {
          subjectOptions.value = [...MOCK_SUBJECTS]
          subjectsLoading.value = false
        })
      } else {
        subjectOptions.value = [...MOCK_SUBJECTS]
        subjectsLoading.value = false
      }
    } catch {
      subjectOptions.value = [...MOCK_SUBJECTS]
      subjectsLoading.value = false
    }
  }

  // ── 年份 ──
  const yearRange = ref<{ min: number; max: number }>({ min: 2021, max: 2025 })
  const yearsLoading = ref(false)
  async function loadYears() {
    yearsLoading.value = true
    try {
      if (isApiMode.value) {
        const data = await fetchFilterYears()
        yearRange.value = { min: data.minYear!, max: data.maxYear! }
      }
    } catch {
      // keep mock defaults
    } finally {
      yearsLoading.value = false
    }
  }

  const yearOptions = computed(() => {
    const opts: number[] = []
    for (let y = yearRange.value.max; y >= yearRange.value.min; y--) {
      opts.push(y)
    }
    return opts
  })

  return {
    provinceOptions,
    provincesLoading,
    loadProvinces,
    subjectOptions,
    subjectsLoading,
    loadSubjects,
    yearOptions,
    yearsLoading,
    loadYears,
  }
}