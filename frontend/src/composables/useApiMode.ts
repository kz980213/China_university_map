import { ref, watch } from 'vue'

const STORAGE_KEY = 'china-uni-map-api-mode'

// Initialize from localStorage, default to API mode
const stored = localStorage.getItem(STORAGE_KEY)
const isApiMode = ref(stored !== null ? stored === 'true' : true)

watch(isApiMode, (val) => {
  localStorage.setItem(STORAGE_KEY, String(val))
})

export function useApiMode() {
  function toggle() {
    isApiMode.value = !isApiMode.value
  }

  return {
    isApiMode,
    toggle,
  }
}