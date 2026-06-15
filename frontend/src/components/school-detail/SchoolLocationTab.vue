<script setup lang="ts">
import { computed } from 'vue'
import type { School } from '@/types/school'

const props = defineProps<{
  school: School
}>()

const hasCoords = computed(() => !!props.school.latitude && !!props.school.longitude)

// 高德地图外链（无需 API Key）
const amapUrl = computed(() => {
  if (!hasCoords.value) return ''
  const { longitude: lng, latitude: lat, name } = props.school
  return `https://uri.amap.com/marker?position=${lng},${lat}&name=${encodeURIComponent(name)}&callnative=0`
})

// OpenStreetMap 嵌入（国内访问可能较慢，作为备用）
const osmEmbedUrl = computed(() => {
  if (!hasCoords.value) return ''
  const { longitude: lng, latitude: lat } = props.school
  const delta = 0.008
  return `https://www.openstreetmap.org/export/embed.html?bbox=${lng! - delta},${lat! - delta},${lng! + delta},${lat! + delta}&layer=mapnik&marker=${lat},${lng}`
})
</script>

<template>
  <div class="location-tab">
    <div class="info-grid">
      <div class="info-card full-width">
        <span class="info-label">学校地址</span>
        <span class="info-value">{{ school.address || (school.province + ' ' + school.city + (school.district ? ' ' + school.district : '')) }}</span>
      </div>
      <div class="info-card">
        <span class="info-label">所在省市</span>
        <span class="info-value">{{ school.province }} {{ school.city }}{{ school.district ? ' · ' + school.district : '' }}</span>
      </div>
      <div class="info-card">
        <span class="info-label">经度 / 纬度</span>
        <span class="info-value">
          {{ school.longitude?.toFixed(5) ?? '暂无' }} / {{ school.latitude?.toFixed(5) ?? '暂无' }}
        </span>
      </div>
    </div>

    <!-- 有坐标时显示地图 -->
    <template v-if="hasCoords">
      <div class="map-actions">
        <a :href="amapUrl" target="_blank" rel="noopener" class="map-link amap">
          在高德地图中查看
        </a>
      </div>

      <div class="map-embed-wrap">
        <iframe
          :src="osmEmbedUrl"
          class="map-iframe"
          loading="lazy"
          sandbox="allow-scripts allow-same-origin"
        />
        <p class="map-caption">地图数据来自 OpenStreetMap（国内访问较慢时请使用上方高德链接）</p>
      </div>
    </template>

    <!-- 无坐标占位 -->
    <div v-else class="map-placeholder">
      <div class="placeholder-icon">🗺️</div>
      <p class="placeholder-text">暂无地理坐标数据</p>
      <p class="placeholder-hint">导入学校数据后将自动显示地图</p>
    </div>
  </div>
</template>

<style scoped lang="scss">
@use '@/styles/variables' as *;

.location-tab { padding: 4px 0; }

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 16px;
}

.info-card {
  background: $bg-main;
  border-radius: $radius-md;
  padding: 10px 14px;
  display: flex;
  flex-direction: column;
  gap: 3px;

  &.full-width { grid-column: 1 / -1; }
}

.info-label { font-size: 12px; color: $text-muted; }
.info-value { font-size: 14px; color: $text-primary; font-weight: 500; line-height: 1.5; }

.map-actions {
  display: flex;
  gap: 10px;
  margin-bottom: 12px;
}

.map-link {
  display: inline-flex;
  align-items: center;
  padding: 6px 16px;
  border-radius: $radius-md;
  font-size: 13px;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.15s;

  &.amap {
    background: #1677ff;
    color: #fff;
    &:hover { background: #0958d9; }
  }
}

.map-embed-wrap {
  border-radius: $radius-lg;
  overflow: hidden;
  border: 1px solid $border-color;
}

.map-iframe {
  width: 100%;
  height: 340px;
  border: none;
  display: block;
}

.map-caption {
  font-size: 11px;
  color: $text-muted;
  text-align: center;
  padding: 6px;
  background: $bg-main;
}

.map-placeholder {
  background: $bg-main;
  border-radius: $radius-lg;
  padding: 48px 24px;
  text-align: center;
  border: 2px dashed $border-color;
}

.placeholder-icon { font-size: 40px; margin-bottom: 12px; }
.placeholder-text { font-size: 14px; font-weight: 600; color: $text-primary; margin-bottom: 4px; }
.placeholder-hint { font-size: 13px; color: $text-muted; }
</style>
