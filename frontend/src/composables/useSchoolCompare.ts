import { computed, ref } from 'vue'
import type { School } from '@/types/school'

const MAX_COMPARE = 3
const compareList = ref<School[]>([])
const compareDrawerOpen = ref(false)

export function useSchoolCompare() {
  function isInCompare(id: number) {
    return compareList.value.some(s => s.id === id)
  }

  function addToCompare(school: School) {
    if (isInCompare(school.id) || compareList.value.length >= MAX_COMPARE) return
    compareList.value = [...compareList.value, school]
  }

  function removeFromCompare(id: number) {
    compareList.value = compareList.value.filter(s => s.id !== id)
  }

  function clearCompare() {
    compareList.value = []
  }

  function openCompareDrawer() {
    compareDrawerOpen.value = true
  }

  function closeCompareDrawer() {
    compareDrawerOpen.value = false
  }

  const canAddMore = computed(() => compareList.value.length < MAX_COMPARE)

  return {
    compareList,
    compareDrawerOpen,
    isInCompare,
    addToCompare,
    removeFromCompare,
    clearCompare,
    openCompareDrawer,
    closeCompareDrawer,
    canAddMore,
    MAX_COMPARE,
  }
}
