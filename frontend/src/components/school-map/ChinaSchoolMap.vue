<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import * as echarts from 'echarts'
import type { School } from '@/types/school'
import { normalizeProvinceName, toMapProvinceName } from '@/utils/province'
import MapLegend from './MapLegend.vue'

export interface ProvinceStatItem {
  province: string
  total: number
  undergraduateCount: number
  juniorCollegeCount: number
  count985: number
  count211: number
  doubleFirstClassCount: number
}

const props = defineProps<{
  schools: School[]
  filteredSchools?: School[]
  selectedProvince?: string
  provinceStats?: ProvinceStatItem[]
}>()

const emit = defineEmits<{
  selectProvince: [province: string]
}>()

// ========== 完整统计数据（用于 ECharts 地图，直接使用外部传入的 provinceStats） ==========
const fullProvinceStats = computed(() => {
  if (!props.provinceStats || props.provinceStats.length === 0) return []
  const result: Array<{
    mapName: string
    shortName: string
    total: number
    undergraduateCount: number
    juniorCollegeCount: number
    count985: number
    count211: number
    countDouble: number
  }> = []

  for (const s of props.provinceStats) {
    result.push({
      mapName: toMapProvinceName(s.province),
      shortName: s.province,
      total: s.total,
      undergraduateCount: s.undergraduateCount,
      juniorCollegeCount: s.juniorCollegeCount,
      count985: s.count985,
      count211: s.count211,
      countDouble: s.doubleFirstClassCount,
    })
  }

  return result
})

// ========== ECharts 相关 ==========
const mapContainer = ref<HTMLDivElement | null>(null)
type EChartsInstance = ReturnType<typeof echarts.init>
let chartInstance: EChartsInstance | null = null
let resizeObserver: ResizeObserver | null = null
let chartInitialized = false
const mapDataReady = ref(false)
const mapLoadFailed = ref(false)

function getVisualMapRange() {
  const totals = fullProvinceStats.value.map((s) => s.total)
  if (totals.length === 0) return [0, 100]
  return [Math.min(...totals), Math.max(...totals)]
}

function getMapOption() {
  const statsByName = new Map<string, (typeof fullProvinceStats.value)[number]>()
  for (const s of fullProvinceStats.value) {
    statsByName.set(s.shortName, s)
  }

  const [minVal, maxVal] = getVisualMapRange()

  return {
    title: {
      text: '全国高校分布',
      left: 'center',
      top: 8,
      textStyle: {
        fontSize: 18,
        fontWeight: 600,
        color: '#1f2937',
      },
    },
    tooltip: {
      trigger: 'item',
      backgroundColor: '#ffffff',
      borderColor: '#e5e7eb',
      borderWidth: 1,
      padding: 12,
      textStyle: {
        color: '#1f2937',
        fontSize: 13,
      },
      formatter(params: { name: string; value?: number }) {
        if (!params || params.value === undefined) return ''
        const mapProvinceName = params.name
        const shortName = normalizeProvinceName(mapProvinceName)
        const stats = statsByName.get(shortName)
        if (!stats) {
          return `<div style="font-weight:600;font-size:14px;margin-bottom:4px">${mapProvinceName}</div>
            <div style="color:#9ca3af">暂无数据</div>`
        }
        return `<div style="font-weight:600;font-size:14px;margin-bottom:6px">${mapProvinceName}</div>
          <div style="line-height:1.8">
            <div>高校总数：<b>${stats.total}</b> 所</div>
            <div>本科：<b>${stats.undergraduateCount}</b> 所</div>
            <div>专科/高职：<b>${stats.juniorCollegeCount}</b> 所</div>
            <div>985 高校：<b>${stats.count985}</b> 所</div>
            <div>211 高校：<b>${stats.count211}</b> 所</div>
            <div>双一流：<b>${stats.countDouble}</b> 所</div>
          </div>`
      },
    },
    visualMap: {
      min: minVal,
      max: maxVal,
      left: -10,
      bottom: 40,
      text: ['多', '少'],
      inRange: {
        color: ['#eff6ff', '#bfdbfe', '#3b82f6', '#1e40af'],
      },
      calculable: true,
      textStyle: {
        color: '#6b7280',
        fontSize: 12,
      },
    },
    series: [
      {
        name: '高校数量',
        type: 'map',
        map: 'china',
        roam: true,
        selectedMode: false,
        label: {
          show: true,
          color: '#374151',
          fontSize: 10,
          formatter(params: { name?: string }): string {
            return params.name ? normalizeProvinceName(params.name) : ''
          },
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 13,
            formatter(params: { name?: string }): string {
              return params.name ? normalizeProvinceName(params.name) : ''
            },
            fontWeight: 'bold',
            color: '#1e40af',
          },
          itemStyle: {
            areaColor: '#dbeafe',
            borderColor: '#1e40af',
            borderWidth: 2,
          },
        },
        itemStyle: {
          borderColor: '#9ca3af',
          borderWidth: 0.5,
          areaColor: '#eff6ff',
        },
        data: fullProvinceStats.value.map((s) => ({
          name: s.mapName,
          value: s.total,
        })),
      },
    ],
  }
}

function onMapClick(params: { name: string }) {
  if (!params || !params.name) return
  // 点击省份时，将 GeoJSON 省份名称（如 "江苏省"）归一化为 "江苏"
  const shortName = normalizeProvinceName(params.name)
  emit('selectProvince', shortName)
}

function onMapDblClick() {
  // 双击空白区域清除省份筛选
  emit('selectProvince', '')
}

async function initMap() {
  if (!mapContainer.value) return

  try {
    // 尝试动态加载本地 GeoJSON
    const geoModule = await import('@/assets/maps/china.json')
    const rawGeoJson = geoModule.default ?? geoModule

    // 直接使用原始 GeoJSON，保留原始名称（如 "北京市"、"甘肃省"）
    // 不做任何名称修改，避免影响 ECharts 标签定位
    echarts.registerMap('china', rawGeoJson as unknown as Parameters<typeof echarts.registerMap>[1])

    // 初始化 ECharts
    chartInstance = echarts.init(mapContainer.value)

    // 绑定 click 事件
    chartInstance.on('click', onMapClick)
    chartInstance.on('dblclick', onMapDblClick)

    // 设置地图选项
    chartInstance.setOption(getMapOption())

    mapDataReady.value = true
  } catch (err) {
    console.warn('当前未检测到本地中国地图 GeoJSON，已切换为省份卡片模式。')
    console.warn(err instanceof Error ? err.message : String(err))
    mapLoadFailed.value = true
  }
}

function resizeChart() {
  if (chartInstance && !chartInstance.isDisposed()) {
    chartInstance.resize()
  }
}

// 当选中省份变化时，更新地图高亮
watch(
  () => props.selectedProvince,
  () => {
    if (!chartInstance || chartInstance.isDisposed()) return
    // 取消所有选中
    chartInstance.dispatchAction({ type: 'unselect', seriesIndex: 0 })
    // 如果选中了省份，在 ECharts 中高亮
    if (props.selectedProvince) {
      // 将短名反向映射为 GeoJSON 中的完整名称（如 "甘肃" → "甘肃省"）
      const fullName = toMapProvinceName(props.selectedProvince!)
      chartInstance.dispatchAction({ type: 'select', seriesIndex: 0, name: fullName })
    }
  }
)

// 当数据变化时，更新图表
watch(
  () => props.schools,
  () => {
    if (chartInstance && !chartInstance.isDisposed()) {
      chartInstance.setOption(getMapOption())
    }
  },
  { deep: true }
)

onMounted(() => {
  if (mapContainer.value) {
    // ResizeObserver 在浏览器完成 flex 布局后才触发，可拿到真实像素尺寸。
    // 比 nextTick 更可靠：ECharts init() 需要容器已有非零高度。
    resizeObserver = new ResizeObserver((entries) => {
      const height = entries[0]?.contentRect.height ?? 0
      if (height === 0) return
      if (!chartInitialized) {
        chartInitialized = true
        initMap()
      } else {
        resizeChart()
      }
    })
    resizeObserver.observe(mapContainer.value)
  }
})

onUnmounted(() => {
  resizeObserver?.disconnect()
  resizeObserver = null
  if (chartInstance) {
    chartInstance.off('click', onMapClick)
    chartInstance.off('dblclick', onMapDblClick)
    chartInstance.dispose()
    chartInstance = null
  }
})

// ========== 降级方案：省份卡片模式 ==========
const provinceList = ['北京', '上海', '江苏', '广东', '浙江', '湖北', '四川']

// 将传入的 provinceStats 数组转为按省份名 lookup
const provinceStatsMap = computed(() => {
  const map = new Map<string, ProvinceStatItem>()
  if (props.provinceStats) {
    for (const s of props.provinceStats) {
      map.set(s.province, s)
    }
  }
  return map
})
</script>

<template>
  <div class="china-map-area">
    <!-- 顶部标题及按钮 -->
    <div class="map-toolbar">
      <div class="map-header">
        <h2 class="map-title">全国高校分布</h2>
        <span class="map-subtitle">点击省份查看详情</span>
      </div>
      <button
        v-if="selectedProvince"
        class="btn-view-all"
        type="button"
        @click="emit('selectProvince', '')"
      >
        查看全国
      </button>
    </div>

    <!-- ECharts 地图容器 -->
    <div
      ref="mapContainer"
      class="echarts-map-container"
      :class="{ hidden: !mapDataReady || mapLoadFailed }"
    />

    <!-- 降级方案：省份卡片 -->
    <div v-show="!mapDataReady || mapLoadFailed" class="fallback-area">
      <p v-if="mapLoadFailed" class="fallback-hint">
        当前未检测到本地中国地图 GeoJSON，已切换为省份卡片模式。
      </p>
      <div class="map-grid">
        <div
          v-for="province in provinceList"
          :key="province"
          class="province-card"
          :class="{ active: province === selectedProvince }"
          @click="emit('selectProvince', province)"
        >
          <div class="province-name">{{ province }}</div>
          <div class="province-stats">
            <template v-if="provinceStatsMap.get(province)">
              <span class="stat-item">共 {{ provinceStatsMap.get(province)!.total }} 所</span>
              <span v-if="provinceStatsMap.get(province)!.count985 > 0" class="stat-item tag-985">
                985: {{ provinceStatsMap.get(province)!.count985 }}
              </span>
              <span v-if="provinceStatsMap.get(province)!.count211 > 0" class="stat-item tag-211">
                211: {{ provinceStatsMap.get(province)!.count211 }}
              </span>
            </template>
            <span v-else class="stat-item empty">暂无数据</span>
          </div>
        </div>
      </div>
    </div>

    <MapLegend />
  </div>
</template>

<style scoped lang="scss">
@use '@/styles/variables' as *;

.china-map-area {
  flex: 1;
  position: relative;
  display: flex;
  flex-direction: column;
  padding: 24px;
  overflow: hidden;
}

.map-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.map-header {
  .map-title {
    font-size: 18px;
    font-weight: 600;
    color: $text-primary;
    margin-bottom: 4px;
  }
  .map-subtitle {
    font-size: 13px;
    color: $text-muted;
  }
}

.btn-view-all {
  padding: 6px 16px;
  background: $color-primary;
  color: #ffffff;
  border: none;
  border-radius: $radius-md;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.2s;
  white-space: nowrap;

  &:hover {
    background: $color-primary-dark;
  }
}

.echarts-map-container {
  flex: 1;
  min-height: 0;   /* 允许 flex 向下收缩，去掉固定最小高度 */
  background: $bg-card;
  border-radius: $radius-lg;
  box-shadow: $shadow-sm;
}

.fallback-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.fallback-hint {
  font-size: 13px;
  color: $text-muted;
  background: #fef3c7;
  border: 1px solid #fcd34d;
  border-radius: $radius-md;
  padding: 8px 16px;
  margin-bottom: 20px;
}

.map-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  width: 100%;
  max-width: 700px;
}

.province-card {
  background: $bg-card;
  border: 1px solid $border-color;
  border-radius: $radius-md;
  padding: 16px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    border-color: $color-primary-light;
    box-shadow: $shadow-md;
    transform: translateY(-2px);
  }

  &.active {
    border-color: $color-primary;
    background: rgba($color-primary, 0.08);
    box-shadow: 0 0 0 2px rgba($color-primary, 0.3);

    .province-name {
      color: $color-primary;
    }
  }
}

.province-name {
  font-size: 16px;
  font-weight: 600;
  color: $text-primary;
  margin-bottom: 8px;
}

.province-stats {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-item {
  font-size: 12px;
  color: $text-secondary;

  &.tag-985 {
    color: $color-985;
    font-weight: 500;
  }
  &.tag-211 {
    color: $color-211;
    font-weight: 500;
  }
  &.empty {
    color: $text-muted;
    font-style: italic;
  }
}
</style>