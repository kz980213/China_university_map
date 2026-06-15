<script setup lang="ts">
</script>

<template>
  <div class="map-legend">
    <div class="legend-item">
      <span class="legend-dot dot-985" />
      <span class="legend-label">985 高校</span>
    </div>
    <div class="legend-item">
      <span class="legend-dot dot-211" />
      <span class="legend-label">211 高校</span>
    </div>
    <div class="legend-item">
      <span class="legend-dot dot-double" />
      <span class="legend-label">双一流高校</span>
    </div>
    <div class="legend-item">
      <span class="legend-dot dot-other" />
      <span class="legend-label">其他本科/专科</span>
    </div>
  </div>
</template>

<style scoped lang="scss">
@use '@/styles/variables' as *;

.map-legend {
  position: absolute;
  bottom: 16px;
  left: 16px;
  background: $bg-card;
  border-radius: $radius-md;
  padding: 12px 16px;
  box-shadow: $shadow-md;
  display: flex;
  gap: 20px;
  z-index: 10;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: $text-secondary;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.dot-985 {
  background: $color-985;
}
.dot-211 {
  background: $color-211;
}
.dot-double {
  background: $color-double-first;
}
.dot-other {
  background: $text-muted;
}
</style>