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

const COLORS = ['#7c3aed', '#2563eb', '#059669', '#d97706', '#db2777']

function getOption() {
  const data = [...props.scores].sort((a, b) => a.year - b.year)
  const years = [...new Set(data.map((s) => s.year))].sort((a, b) => a - b)

  // 按科类分组
  const bySubject = new Map<string, Map<number, number | null>>()
  for (const s of data) {
    if (!bySubject.has(s.subjectType)) bySubject.set(s.subjectType, new Map())
    bySubject.get(s.subjectType)!.set(s.year, s.estimatedRank ?? null)
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
  }))

  return {
    legend: multiSeries ? { top: 4, right: 8, textStyle: { fontSize: 11 } } : { show: false },
    tooltip: {
      trigger: 'axis',
      formatter(params: unknown) {
        const list = params as Array<{ seriesName: string; axisValue: string; data: number | null; color: string }>
        const year = list[0]?.axisValue ?? ''
        const lines = list.map((p) => {
          const val = p.data != null ? `<b>${p.data}</b>` : '暂无'
          return `<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:${p.color};margin-right:4px"></span>${p.seriesName}：${val}`
        }).join('<br/>')
        return `${year}年<br/>${lines}<br/><span style="color:#9ca3af;font-size:11px">（位次仅供参考）</span>`
      },
    },
    xAxis: { type: 'category', data: years.map(String) },
    yAxis: { type: 'value', name: '估算位次', inverse: true },
    series,
    grid: { top: multiSeries ? 36 : 20, right: 20, bottom: 30, left: 70 },
  }
}

onMounted(async () => {
  await nextTick()
  if (!container.value) return
  chart = echarts.init(container.value)
  chart.setOption(getOption())

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

function resize() { chart?.resize() }

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