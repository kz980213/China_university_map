<script setup lang="ts">
import { nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import * as echarts from 'echarts'
import type { School } from '@/types/school'
import type { AdmissionScore } from '@/types/admission'

interface SchoolScores {
  school: School
  scores: AdmissionScore[]
}

const props = defineProps<{
  data: SchoolScores[]
}>()

const container = ref<HTMLDivElement | null>(null)
type Chart = ReturnType<typeof echarts.init>
let chart: Chart | null = null
let ro: ResizeObserver | null = null

const COLORS = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6']

function getOption() {
  const allYears = new Set<number>()
  for (const { scores } of props.data) {
    for (const s of scores) allYears.add(s.year)
  }
  const years = [...allYears].sort((a, b) => a - b)

  const series = props.data.map(({ school, scores }, i) => {
    // Take minimum score per year across all subject types
    const byYear = new Map<number, number>()
    for (const s of scores) {
      const existing = byYear.get(s.year)
      if (existing === undefined || s.minScore < existing) {
        byYear.set(s.year, s.minScore)
      }
    }
    return {
      name: school.name,
      type: 'line',
      data: years.map(y => byYear.get(y) ?? null),
      smooth: true,
      connectNulls: false,
      lineStyle: { color: COLORS[i % COLORS.length], width: 2.5 },
      itemStyle: { color: COLORS[i % COLORS.length] },
      symbolSize: 6,
    }
  })

  return {
    legend: { top: 6, textStyle: { fontSize: 12 } },
    tooltip: {
      trigger: 'axis',
      formatter: (params: any[]) => {
        const year = params[0]?.name
        const lines = params
          .filter(p => p.value != null)
          .map(p => `<span style="color:${p.color}">●</span> ${p.seriesName}: <b>${p.value}</b>`)
        return `${year} 年<br>${lines.join('<br>') || '暂无数据'}`
      },
    },
    xAxis: { type: 'category', data: years.map(String) },
    yAxis: {
      type: 'value',
      name: '最低分',
      min: (val: { min: number }) => Math.floor(val.min / 10) * 10 - 10,
    },
    series,
    grid: { top: 44, right: 24, bottom: 32, left: 58 },
  }
}

onMounted(async () => {
  await nextTick()
  if (!container.value) return
  chart = echarts.init(container.value)
  chart.setOption(getOption())
  ro = new ResizeObserver(() => chart?.resize())
  ro.observe(container.value)
  window.addEventListener('resize', onResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', onResize)
  ro?.disconnect()
  chart?.dispose()
  chart = null
})

function onResize() { chart?.resize() }

watch(() => props.data, async () => {
  await nextTick()
  chart?.setOption(getOption(), true)
  chart?.resize()
}, { deep: true })
</script>

<template>
  <div ref="container" class="compare-chart" />
</template>

<style scoped>
.compare-chart { width: 100%; height: 300px; }
</style>
