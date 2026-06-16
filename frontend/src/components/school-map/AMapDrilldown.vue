<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import AMapLoader from '@amap/amap-jsapi-loader'
import type { School } from '@/types/school'
import { normalizeProvinceName, toMapProvinceName } from '@/utils/province'
import { fetchProvinceCities, fetchMapSchools, fetchSchoolDetail } from '@/api'
export interface ProvinceStatItem {
  province: string
  total: number
  undergraduateCount: number
  juniorCollegeCount: number
  count985: number
  count211: number
  doubleFirstClassCount: number
}

interface CityStatItem {
  city: string
  count: number
  count985: number
  count211: number
  doubleFirstClass: number
  undergraduate: number
  juniorCollege: number
}

const props = defineProps<{
  schools: School[]
  selectedProvince?: string
  provinceStats?: ProvinceStatItem[]
}>()

const emit = defineEmits<{
  selectProvince: [province: string]
  selectSchool: [school: School]
}>()

type ViewLevel = 'country' | 'province' | 'city'

const KEY = import.meta.env.VITE_AMAP_KEY as string | undefined
const COLOR_STOPS = ['#eff6ff', '#bfdbfe', '#3b82f6', '#1e40af']
const GEO_BASE = (import.meta.env.VITE_API_BASE_URL ?? '') + '/api/map/geo'

const PROVINCE_ADCODE: Record<string, number> = {
  '北京市': 110000, '天津市': 120000, '河北省': 130000, '山西省': 140000,
  '内蒙古自治区': 150000, '辽宁省': 210000, '吉林省': 220000, '黑龙江省': 230000,
  '上海市': 310000, '江苏省': 320000, '浙江省': 330000, '安徽省': 340000,
  '福建省': 350000, '江西省': 360000, '山东省': 370000, '河南省': 410000,
  '湖北省': 420000, '湖南省': 430000, '广东省': 440000, '广西壮族自治区': 450000,
  '海南省': 460000, '重庆市': 500000, '四川省': 510000, '贵州省': 520000,
  '云南省': 530000, '西藏自治区': 540000, '陕西省': 610000, '甘肃省': 620000,
  '青海省': 630000, '宁夏回族自治区': 640000, '新疆维吾尔自治区': 650000,
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const geoCache = new Map<number, any>()

// eslint-disable-next-line @typescript-eslint/no-explicit-any
async function fetchGeo(adcode: number): Promise<any> {
  if (geoCache.has(adcode)) return geoCache.get(adcode)
  const res = await fetch(`${GEO_BASE}/${adcode}`)
  if (!res.ok) throw new Error(`边界数据加载失败 (${adcode})`)
  const data = await res.json()
  geoCache.set(adcode, data)
  return data
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function geoPaths(geometry: any): number[][][] {
  if (geometry.type === 'Polygon') return [geometry.coordinates[0]]
  if (geometry.type === 'MultiPolygon') return geometry.coordinates.map((p: number[][][]) => p[0])
  return []
}

// ─── Reactive state ───────────────────────────────────────────────────────────
const mapContainer = ref<HTMLDivElement | null>(null)
const viewLevel = ref<ViewLevel>('country')
const currentProvinceFull = ref('')
const currentCity = ref('')
const loading = ref(false)
const loadError = ref('')

// ─── AMap instances ───────────────────────────────────────────────────────────
// eslint-disable-next-line @typescript-eslint/no-explicit-any
let AMap: any = null
// eslint-disable-next-line @typescript-eslint/no-explicit-any
let map: any = null
// eslint-disable-next-line @typescript-eslint/no-explicit-any
let infoWindow: any = null
let resizeObserver: ResizeObserver | null = null
let mapInitStarted = false

// ─── Overlay layers (kept separate for targeted cleanup) ─────────────────────
// eslint-disable-next-line @typescript-eslint/no-explicit-any
let countryPolygons: any[] = []  // Province outlines — base, kept across views
// eslint-disable-next-line @typescript-eslint/no-explicit-any
let provincePolygons: any[] = [] // City outlines + labels for selected province
// eslint-disable-next-line @typescript-eslint/no-explicit-any
let cityMarkers: any[] = []      // School markers + city boundary highlight

// Province center cache populated during country view load
const provinceCenterCache = new Map<string, [number, number]>()

// City count-label tracker: city name → AMap.Text object (so we can remove on click)
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const cityLabelMap = new Map<string, any>()
// City polygon tracker: city name → polygon list (to dim on click)
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const cityPolygonMap = new Map<string, any[]>()
// Polygons belonging to the currently-selected city (restored on back)
// eslint-disable-next-line @typescript-eslint/no-explicit-any
let selectedCityPolygons: any[] = []

// Guard against concurrent country polygon builds
let _countryBuildPromise: Promise<void> | null = null

// ─── Color helpers ────────────────────────────────────────────────────────────
function lerpColor(c0: string, c1: string, t: number): string {
  const a = parseInt(c0.slice(1), 16)
  const b = parseInt(c1.slice(1), 16)
  const ar = (a >> 16) & 255, ag = (a >> 8) & 255, ab = a & 255
  const br = (b >> 16) & 255, bg = (b >> 8) & 255, bb = b & 255
  const r = Math.round(ar + (br - ar) * t)
  const g = Math.round(ag + (bg - ag) * t)
  const bl = Math.round(ab + (bb - ab) * t)
  return `rgb(${r}, ${g}, ${bl})`
}

function colorForValue(value: number, min: number, max: number): string {
  if (max <= min) return COLOR_STOPS[1]
  const t = (value - min) / (max - min)
  const segment = t * (COLOR_STOPS.length - 1)
  const idx = Math.max(0, Math.min(Math.floor(segment), COLOR_STOPS.length - 2))
  return lerpColor(COLOR_STOPS[idx], COLOR_STOPS[idx + 1], segment - idx)
}

function badgeColor(school: { is985: boolean; is211: boolean; isDoubleFirstClass: boolean }): string {
  if (school.is985) return '#dc2626'
  if (school.is211) return '#2563eb'
  if (school.isDoubleFirstClass) return '#7c3aed'
  return '#9ca3af'
}

// ─── Tooltip helpers ──────────────────────────────────────────────────────────
const TOOLTIP_STYLE = [
  'background:white', 'border-radius:8px', 'padding:10px 14px',
  'box-shadow:0 4px 12px rgba(0,0,0,0.15)', 'font-size:13px',
  'white-space:nowrap', 'pointer-events:none', 'line-height:1.6',
].join(';')

const TD_LABEL = 'style="color:#6b7280;padding:1px 12px 1px 0"'
const TD_VAL   = 'style="font-weight:600;text-align:right"'

function buildProvinceTooltip(stat?: ProvinceStatItem): string {
  return `<div style="${TOOLTIP_STYLE}">
    <table style="border-collapse:collapse">
      <tr><td ${TD_LABEL}>院校总数</td><td ${TD_VAL} style="color:#1f2937">${stat?.total ?? 0}</td></tr>
      <tr><td ${TD_LABEL}>985</td><td ${TD_VAL} style="color:#dc2626">${stat?.count985 ?? 0}</td></tr>
      <tr><td ${TD_LABEL}>211</td><td ${TD_VAL} style="color:#2563eb">${stat?.count211 ?? 0}</td></tr>
      <tr><td ${TD_LABEL}>双一流</td><td ${TD_VAL} style="color:#7c3aed">${stat?.doubleFirstClassCount ?? 0}</td></tr>
      <tr><td ${TD_LABEL}>本科</td><td ${TD_VAL} style="color:#059669">${stat?.undergraduateCount ?? 0}</td></tr>
      <tr><td ${TD_LABEL}>专科</td><td ${TD_VAL} style="color:#d97706">${stat?.juniorCollegeCount ?? 0}</td></tr>
    </table>
  </div>`
}

function buildCityTooltip(stat: CityStatItem): string {
  return `<div style="${TOOLTIP_STYLE}">
    <table style="border-collapse:collapse">
      <tr><td ${TD_LABEL}>院校总数</td><td ${TD_VAL} style="color:#1f2937">${stat.count ?? 0}</td></tr>
      <tr><td ${TD_LABEL}>985</td><td ${TD_VAL} style="color:#dc2626">${stat.count985 ?? 0}</td></tr>
      <tr><td ${TD_LABEL}>211</td><td ${TD_VAL} style="color:#2563eb">${stat.count211 ?? 0}</td></tr>
      <tr><td ${TD_LABEL}>双一流</td><td ${TD_VAL} style="color:#7c3aed">${stat.doubleFirstClass ?? 0}</td></tr>
      <tr><td ${TD_LABEL}>本科</td><td ${TD_VAL} style="color:#059669">${stat.undergraduate ?? 0}</td></tr>
      <tr><td ${TD_LABEL}>专科</td><td ${TD_VAL} style="color:#d97706">${stat.juniorCollege ?? 0}</td></tr>
    </table>
  </div>`
}

// Tooltip anchored to geographic center. Debounced hide prevents flicker when
// the mouse briefly enters the InfoWindow overlay (which sits above the polygon).
let _tooltipHideTimer: ReturnType<typeof setTimeout> | null = null

function showTooltipAt(html: string, center: [number, number]) {
  if (_tooltipHideTimer) { clearTimeout(_tooltipHideTimer); _tooltipHideTimer = null }
  if (!infoWindow) {
    infoWindow = new AMap.InfoWindow({ isCustom: true, autoMove: false, closeWhenClickMap: false })
  }
  infoWindow.setContent(html)
  infoWindow.open(map, center)
}

function hideTooltip() {
  _tooltipHideTimer = setTimeout(() => {
    infoWindow?.close()
    _tooltipHideTimer = null
  }, 150)
}

// ─── Selected-city overlay helpers ───────────────────────────────────────────
function restoreSelectedCityPolygons() {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  for (const p of selectedCityPolygons) (p as any).setOptions?.({ fillOpacity: 0.85 })
  selectedCityPolygons = []
}

// ─── Map init ─────────────────────────────────────────────────────────────────
async function ensureMap(): Promise<boolean> {
  if (map) return true
  if (!KEY) { loadError.value = '未配置高德地图 Key（VITE_AMAP_KEY）'; return false }
  if (!mapContainer.value) return false
  const loaded = await AMapLoader.load({ key: KEY, version: '2.0', plugins: [] })
  AMap = loaded
  map = new AMap.Map(mapContainer.value, {
    viewMode: '2D',
    zoom: 4,
    center: [104.5, 36],
    zooms: [3, 18],
    resizeEnable: true,
  })
  return true
}

function makeDistrictLabel(text: string, position: unknown) {
  return new AMap.Text({
    text,
    position,
    style: {
      'font-size': '12px',
      'font-weight': '600',
      color: '#1f2937',
      padding: '0',
      background: 'transparent',
      border: 'none',
      'box-shadow': 'none',
      'white-space': 'nowrap',
    },
    anchor: 'center',
    zIndex: 25,
  })
}

// ─── Country polygons (base layer, built once) ────────────────────────────────
async function _buildAndAddCountryPolygons(): Promise<void> {
  const statsByShort = new Map((props.provinceStats ?? []).map((s) => [s.province, s]))
  const totals = (props.provinceStats ?? []).map((s) => s.total)
  const min = totals.length ? Math.min(...totals) : 0
  const max = totals.length ? Math.max(...totals) : 1

  const geo = await fetchGeo(100000)

  for (const feature of geo.features ?? []) {
    const name: string = feature.properties?.name ?? ''
    const center = feature.properties?.center
    const shortName = normalizeProvinceName(name)
    const total = statsByShort.get(shortName)?.total ?? 0
    const fill = colorForValue(total, min, max)

    if (center) provinceCenterCache.set(name, center as [number, number])

    for (const path of geoPaths(feature.geometry)) {
      const polygon = new AMap.Polygon({
        path,
        fillColor: fill,
        fillOpacity: 0.85,
        strokeColor: '#ffffff',
        strokeWeight: 1,
        cursor: 'pointer',
        zIndex: 10,
      })
      polygon.on('click', () => selectProvince(name))
      const stat = statsByShort.get(shortName)
      polygon.on('mouseover', () => {
        if (center) showTooltipAt(buildProvinceTooltip(stat), center as [number, number])
      })
      polygon.on('mouseout', hideTooltip)
      countryPolygons.push(polygon)
    }
  }

  map.add(countryPolygons)
}

async function ensureCountryBase(): Promise<void> {
  if (countryPolygons.length > 0) return
  if (_countryBuildPromise) { await _countryBuildPromise; return }
  _countryBuildPromise = _buildAndAddCountryPolygons().finally(() => { _countryBuildPromise = null })
  await _countryBuildPromise
}

// ─── View loaders ─────────────────────────────────────────────────────────────
async function loadCountryView() {
  restoreSelectedCityPolygons()
  hideTooltip()
  if (map && provincePolygons.length) { map.remove(provincePolygons); provincePolygons = [] }
  if (map && cityMarkers.length) { map.remove(cityMarkers); cityMarkers = [] }
  viewLevel.value = 'country'
  currentProvinceFull.value = ''
  currentCity.value = ''

  try {
    const ok = await ensureMap()
    if (!ok) return

    if (countryPolygons.length) {
      // Already built — just animate back to full-China view
      map.setFitView(countryPolygons, true, [20, 20, 20, 20])
      return
    }

    loading.value = true
    loadError.value = ''
    await ensureCountryBase()
    loading.value = false
    map.setFitView(countryPolygons, false, [20, 20, 20, 20])
  } catch (err) {
    loading.value = false
    loadError.value = err instanceof Error ? err.message : '地图加载失败'
  }
}

async function loadProvinceView(provinceFull: string) {
  hideTooltip()
  if (map && provincePolygons.length) { map.remove(provincePolygons); provincePolygons = [] }
  if (map && cityMarkers.length) { map.remove(cityMarkers); cityMarkers = [] }
  cityLabelMap.clear()
  cityPolygonMap.clear()
  selectedCityPolygons = []
  viewLevel.value = 'province'
  currentProvinceFull.value = provinceFull
  currentCity.value = ''
  loading.value = true
  loadError.value = ''

  try {
    const ok = await ensureMap()
    if (!ok) { loading.value = false; return }

    // Always ensure country base is visible underneath
    await ensureCountryBase()

    const cities = await fetchProvinceCities(provinceFull)

    // Municipality shortcut: 北京/上海/天津/重庆 skip city-polygon step
    if (cities.length === 1 && cities[0].city === provinceFull) {
      await loadCityView(cities[0].city)
      return
    }

    const statByCity = new Map(cities.map((c) => [c.city, c]))
    const totals = cities.map((c) => c.count)
    const min = totals.length ? Math.min(...totals) : 0
    const max = totals.length ? Math.max(...totals) : 1

    const adcode = PROVINCE_ADCODE[provinceFull]
    if (!adcode) throw new Error(`未找到省份编码: ${provinceFull}`)

    const geo = await fetchGeo(adcode)
    const newPolygons: unknown[] = []
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const fitTargets: any[] = []

    for (const feature of geo.features ?? []) {
      const name: string = feature.properties?.name ?? ''
      const center: [number, number] | undefined = feature.properties?.center
      const stat = statByCity.get(name) ?? { city: name, count: 0, count985: 0, count211: 0, doubleFirstClass: 0, undergraduate: 0, juniorCollege: 0 }
      const fill = colorForValue(stat.count, min, max)

      const cityPolys: unknown[] = []
      for (const path of geoPaths(feature.geometry)) {
        const polygon = new AMap.Polygon({
          path,
          fillColor: fill,
          fillOpacity: 0.85,
          strokeColor: '#ffffff',
          strokeWeight: 1.5,
          cursor: 'pointer',
          zIndex: 20,
        })
        polygon.on('click', () => selectCity(name, feature))
        polygon.on('mouseover', () => {
          if (center) showTooltipAt(buildCityTooltip(stat), center)
        })
        polygon.on('mouseout', hideTooltip)
        newPolygons.push(polygon)
        fitTargets.push(polygon)
        cityPolys.push(polygon)
      }
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      cityPolygonMap.set(name, cityPolys as any[])

      if (center && stat.count > 0) {
        const label = makeDistrictLabel(String(stat.count), center)
        newPolygons.push(label)
        cityLabelMap.set(name, label)
      }
    }

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    provincePolygons = newPolygons as any[]
    loading.value = false
    map.add(provincePolygons)

    if (fitTargets.length) {
      map.setFitView(fitTargets, true, [100, 100, 100, 100])
    }
  } catch (err) {
    loading.value = false
    loadError.value = err instanceof Error ? err.message : '城市数据加载失败'
  }
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
async function loadCityView(city: string, cityFeature?: any) {
  hideTooltip()
  if (map && cityMarkers.length) { map.remove(cityMarkers); cityMarkers = [] }
  viewLevel.value = 'city'
  currentCity.value = city
  loading.value = true
  loadError.value = ''

  try {
    const ok = await ensureMap()
    if (!ok) { loading.value = false; return }

    const list = await fetchMapSchools({ city })
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const newMarkers: any[] = []
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const fitTargets: any[] = []

    // City boundary highlight — drawn first so it's below markers
    if (cityFeature) {
      for (const path of geoPaths(cityFeature.geometry)) {
        const boundary = new AMap.Polygon({
          path,
          fillColor: '#dbeafe',
          fillOpacity: 0.25,
          strokeColor: '#2563eb',
          strokeWeight: 2,
          cursor: 'default',
          zIndex: 25,
          bubble: true,
        })
        newMarkers.push(boundary)
        fitTargets.push(boundary)
      }
    }

    for (const item of list) {
      const color = badgeColor(item)
      const marker = new AMap.Marker({
        position: [item.lng, item.lat],
        title: item.name,
        content: `<div style="width:12px;height:12px;border-radius:50%;border:2px solid #fff;box-shadow:0 0 0 1px rgba(0,0,0,0.15);background:${color}"></div>`,
        offset: new AMap.Pixel(-7, -7),
        zIndex: 30,
      })
      marker.on('click', async () => {
        try {
          const school = (await fetchSchoolDetail(item.id)) as School
          emit('selectSchool', school)
        } catch {
          const fallback = props.schools.find((s) => s.id === item.id)
          if (fallback) emit('selectSchool', fallback)
        }
      })
      newMarkers.push(marker)
      fitTargets.push(marker)

      // School name label above the dot
      const nameLabel = new AMap.Text({
        text: item.name,
        position: [item.lng, item.lat],
        offset: new AMap.Pixel(0, -20),
        style: {
          'font-size': '11px',
          'font-weight': '500',
          color: '#1f2937',
          padding: '1px 4px',
          background: 'rgba(255,255,255,0.88)',
          border: 'none',
          'box-shadow': 'none',
          'border-radius': '2px',
          'white-space': 'nowrap',
          'pointer-events': 'none',
        },
        anchor: 'bottom-center',
        zIndex: 35,
      })
      newMarkers.push(nameLabel)
    }

    cityMarkers = newMarkers
    loading.value = false
    map.add(cityMarkers)

    if (fitTargets.length) {
      map.setFitView(fitTargets, true, [80, 80, 80, 80])
    }
  } catch (err) {
    loading.value = false
    loadError.value = err instanceof Error ? err.message : '学校数据加载失败'
  }
}

// ─── Navigation ───────────────────────────────────────────────────────────────
function selectProvince(provinceFull: string) {
  emit('selectProvince', normalizeProvinceName(provinceFull))
  loadProvinceView(provinceFull)
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function selectCity(city: string, feature?: any) {
  // Remove the count label for the clicked city
  const label = cityLabelMap.get(city)
  if (label && map) {
    map.remove(label)
    const idx = provincePolygons.indexOf(label)
    if (idx !== -1) provincePolygons.splice(idx, 1)
    cityLabelMap.delete(city)
  }
  // Make only the clicked city's polygon transparent; all others keep their fill
  restoreSelectedCityPolygons()
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const polys = cityPolygonMap.get(city) ?? []
  for (const p of polys) (p as any).setOptions?.({ fillOpacity: 0 })
  selectedCityPolygons = [...polys]

  loadCityView(city, feature)
}

function backToCountry() {
  emit('selectProvince', '')
  loadCountryView()
}

function backToProvince() {
  restoreSelectedCityPolygons()
  if (!currentProvinceFull.value) return
  hideTooltip()
  if (map && cityMarkers.length) { map.remove(cityMarkers); cityMarkers = [] }
  viewLevel.value = 'province'
  currentCity.value = ''
  // Re-fit to existing province polygons (already on map)
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const polygonsOnly = provincePolygons.filter((o: any) => !(o instanceof AMap.Text))
  if (map && polygonsOnly.length) {
    map.setFitView(polygonsOnly, true, [100, 100, 100, 100])
  }
}

// ─── Sync with filter panel province selection ────────────────────────────────
watch(
  () => props.selectedProvince,
  (val) => {
    if (!val) {
      if (viewLevel.value !== 'country') loadCountryView()
      return
    }
    const fullName = toMapProvinceName(val)
    if (fullName !== currentProvinceFull.value) {
      loadProvinceView(fullName)
    }
  },
)

// ─── Lifecycle ────────────────────────────────────────────────────────────────
onMounted(() => {
  if (!mapContainer.value) return
  resizeObserver = new ResizeObserver((entries) => {
    const height = entries[0]?.contentRect.height ?? 0
    if (height === 0) return
    if (!mapInitStarted) {
      mapInitStarted = true
      loadCountryView()
    } else if (map) {
      map.resize()
    }
  })
  resizeObserver.observe(mapContainer.value)
})

onUnmounted(() => {
  resizeObserver?.disconnect()
  resizeObserver = null
  infoWindow?.close()
  if (map) {
    map.remove([...countryPolygons, ...provincePolygons, ...cityMarkers])
    map.destroy()
    map = null
  }
  countryPolygons = []
  provincePolygons = []
  cityMarkers = []
})

// ─── Breadcrumb ───────────────────────────────────────────────────────────────
const breadcrumb = computed(() => {
  const parts: { label: string; action: () => void }[] = [{ label: '全国', action: backToCountry }]
  if (currentProvinceFull.value) {
    parts.push({ label: currentProvinceFull.value, action: backToProvince })
  }
  if (currentCity.value && currentCity.value !== currentProvinceFull.value) {
    parts.push({ label: currentCity.value, action: () => {} })
  }
  return parts
})
</script>

<template>
  <div class="amap-drilldown-area">
    <div class="map-toolbar">
      <div class="map-header">
        <h2 class="map-title">全国高校分布</h2>
        <div class="breadcrumb">
          <template v-for="(item, idx) in breadcrumb" :key="idx">
            <span
              class="crumb"
              :class="{ active: idx === breadcrumb.length - 1 }"
              @click="idx < breadcrumb.length - 1 && item.action()"
            >{{ item.label }}</span>
            <span v-if="idx < breadcrumb.length - 1" class="crumb-sep">/</span>
          </template>
        </div>
      </div>
      <button v-if="viewLevel !== 'country'" class="btn-view-all" type="button" @click="backToCountry">
        查看全国
      </button>
    </div>

    <div ref="mapContainer" class="amap-container" />

    <div v-if="loading" class="map-overlay-tip">加载中…</div>
    <div v-else-if="loadError" class="map-overlay-tip error">{{ loadError }}</div>
  </div>
</template>

<style scoped lang="scss">
@use '@/styles/variables' as *;

.amap-drilldown-area {
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
}

.breadcrumb {
  font-size: 13px;
  color: $text-muted;
}

.crumb {
  cursor: default;

  &:not(.active) {
    cursor: pointer;
    color: $color-primary;

    &:hover {
      text-decoration: underline;
    }
  }

  &.active {
    color: $text-secondary;
  }
}

.crumb-sep {
  margin: 0 4px;
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

.amap-container {
  flex: 1;
  min-height: 0;
  background: $bg-card;
  border-radius: $radius-lg;
  box-shadow: $shadow-sm;
}

.map-overlay-tip {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(255, 255, 255, 0.92);
  border-radius: $radius-md;
  padding: 10px 20px;
  font-size: 13px;
  color: $text-secondary;
  box-shadow: $shadow-md;
  z-index: 10;

  &.error {
    color: $color-danger;
  }
}
</style>
