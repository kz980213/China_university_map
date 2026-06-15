<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

const emit = defineEmits<{ click: [] }>()

const btnEl = ref<HTMLButtonElement | null>(null)
const ready = ref(false)
const pos = ref({ x: 0, y: 0 })

let dragging = false
let dragMoved = false
let dragOffset = { x: 0, y: 0 }

const posStyle = computed(() => ({
  left: pos.value.x + 'px',
  top: pos.value.y + 'px',
}))

function clamp(v: number, min: number, max: number) {
  return Math.max(min, Math.min(max, v))
}

function initPos() {
  const saved = localStorage.getItem('aiButtonPos')
  if (saved) {
    try { pos.value = JSON.parse(saved); return } catch { /* ignore */ }
  }
  const el = btnEl.value
  const w = el?.offsetWidth ?? 160
  const h = el?.offsetHeight ?? 52
  pos.value = { x: window.innerWidth - w - 24, y: window.innerHeight - h - 32 }
}

function onMouseDown(e: MouseEvent) {
  dragging = true
  dragMoved = false
  dragOffset = { x: e.clientX - pos.value.x, y: e.clientY - pos.value.y }
  e.preventDefault()
}

function onMouseMove(e: MouseEvent) {
  if (!dragging) return
  dragMoved = true
  const el = btnEl.value
  const w = el?.offsetWidth ?? 160
  const h = el?.offsetHeight ?? 52
  pos.value = {
    x: clamp(e.clientX - dragOffset.x, 0, window.innerWidth - w),
    y: clamp(e.clientY - dragOffset.y, 0, window.innerHeight - h),
  }
}

function onMouseUp() {
  if (!dragging) return
  dragging = false
  if (!dragMoved) emit('click')
  else localStorage.setItem('aiButtonPos', JSON.stringify(pos.value))
}

onMounted(() => {
  initPos()
  ready.value = true
  document.addEventListener('mousemove', onMouseMove)
  document.addEventListener('mouseup', onMouseUp)
})

onUnmounted(() => {
  document.removeEventListener('mousemove', onMouseMove)
  document.removeEventListener('mouseup', onMouseUp)
})
</script>

<template>
  <button
    v-show="ready"
    ref="btnEl"
    class="ai-btn"
    :style="posStyle"
    @mousedown="onMouseDown"
  >
    <svg class="ai-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z" stroke="currentColor" stroke-width="2"/>
      <path d="M8 9.5a1.5 1.5 0 100-3 1.5 1.5 0 000 3zM16 9.5a1.5 1.5 0 100-3 1.5 1.5 0 000 3z" fill="currentColor"/>
      <path d="M8 14s1.5 2 4 2 4-2 4-2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
    </svg>
    <span>AI 问答</span>
  </button>
</template>

<style scoped lang="scss">
@use '@/styles/variables' as *;

.ai-btn {
  position: fixed;
  z-index: 200;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: linear-gradient(135deg, $color-primary, $color-primary-light);
  color: #ffffff;
  border: none;
  border-radius: 28px;
  font-size: 15px;
  font-weight: 600;
  cursor: grab;
  box-shadow: 0 4px 16px rgba($color-primary, 0.35);
  transition: box-shadow 0.2s, transform 0.2s;
  user-select: none;

  &:active {
    cursor: grabbing;
    box-shadow: 0 6px 24px rgba($color-primary, 0.45);
    transform: scale(1.03);
  }
}

.ai-icon {
  width: 20px;
  height: 20px;
  pointer-events: none;
}
</style>
