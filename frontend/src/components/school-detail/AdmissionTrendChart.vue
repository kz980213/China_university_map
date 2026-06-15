<script setup lang="ts">
import { nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import * as echarts from 'echarts'
import type { AdmissionScore } from '@/types/admission'

const props = defineProps<{
  scores: AdmissionScore[]
}>()

const container = ref<HTMLDivElement | null>(null)
type Chart = ReturnType<typeof echarts.init>
let chart: Chart | null = null
let resizeObserver: ResizeObserver | null = null

const COLORS = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899']

function getOption() {
  const data = [...props.scores].sort((a, b) => a.year - b.year)
  const years = [...new Set(data.map((s) => s.year))].sort((a, b) => a - b)

  // 按科类分组
  const bySubject = new Map<string, Map<number, number>>()
  for (const s of data) {
    if (!bySubject.has(s.subjectType)) bySubject.set(s.subjectType, new Map())
    bySubject.get(s.subjectType)!.set(s.year, s.minScore)
  }

  const multiSeries = bySubject.size > 1
  const series = [...bySubject.entries()].map(([subjectType, yearMap], i) => ({
    name: subjectType,
    type: 'line',
    data: years.map((y) => yearMap.get(y) ?? null),
    smooth: true,
    connectNulls: false,
    lineStyle: { color: COLORS[i % COLORS.length], width: 2 },
    itemStyle: { color: COLORS[i % COLORS.length] },
    areaStyle: i === 0 ? { color: `${COLORS[0]}1a` } : undefined,
  }))

  return {
    legend: multiSeries ? { top: 4, right: 8, textStyle: { fontSize: 11 } } : { show: false },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: years.map(String) },
    yAxis: {
      type: 'value',
      name: '最低分',
      min: (val: { min: number }) => Math.floor(val.min / 5) * 5 - 5,
    },
    series,
    grid: { top: multiSeries ? 36 : 20, right: 20, bottom: 30, left: 50 },
  }
}

onMounted(async () => {
  await nextTick()
  if (!container.value) return
  chart = echarts.init(container.value)
  chart.setOption(getOption())

  // 用 ResizeObserver 监听容器尺寸变化，在 Tab 切换可见时自动 resize
  resizeObserver = new ResizeObserver(() => {
    chart?.resize()
  })
  resizeObserver.observe(container.value)
  window.addEventListener('resize', resize)
})

onUnmounted(() => {
  window.removeEventListener('resize', resize)
  resizeObserver?.disconnect()
  resizeObserver = null
  chart?.dispose()
  chart = null
})

function resize() {
  chart?.resize()
}

watch(() => props.scores, async () => {
  await nextTick()
  chart?.setOption(getOption())
  chart?.resize()
}, { deep: true })
</script>

<template>
  <div ref="container" class="chart-container" />
</template>

<style scoped>
.chart-container { width: 100%; height: 220px; }
</style>