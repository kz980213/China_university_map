<script setup lang="ts">
defineProps<{
  total: number
  undergraduateCount: number
  juniorCollegeCount: number
  count985: number
  count211: number
  doubleFirstClassCount: number
}>()
</script>

<template>
  <div class="stat-cards">
    <div class="stat-card">
      <div class="stat-value">{{ total }}</div>
      <div class="stat-label">高校总数</div>
    </div>
    <div class="stat-card">
      <div class="stat-value">{{ undergraduateCount }}</div>
      <div class="stat-label">本科</div>
    </div>
    <div class="stat-card">
      <div class="stat-value">{{ juniorCollegeCount }}</div>
      <div class="stat-label">专科/高职</div>
    </div>
    <div class="stat-card highlight-985">
      <div class="stat-value">{{ count985 }}</div>
      <div class="stat-label">985</div>
    </div>
    <div class="stat-card highlight-211">
      <div class="stat-value">{{ count211 }}</div>
      <div class="stat-label">211</div>
    </div>
    <div class="stat-card highlight-double">
      <div class="stat-value">{{ doubleFirstClassCount }}</div>
      <div class="stat-label">双一流</div>
    </div>
  </div>
</template>

<style scoped lang="scss">
@use '@/styles/variables' as *;

.stat-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  padding: 16px;
  background: $bg-main;
}

.stat-card {
  background: $bg-card;
  border-radius: $radius-md;
  padding: 12px;
  text-align: center;
  box-shadow: $shadow-sm;

  &.highlight-985 .stat-value {
    color: $color-985;
  }
  &.highlight-211 .stat-value {
    color: $color-211;
  }
  &.highlight-double .stat-value {
    color: $color-double-first;
  }
}

.stat-value {
  font-size: 22px;
  font-weight: 700;
  color: $text-primary;
  margin-bottom: 2px;
}

.stat-label {
  font-size: 12px;
  color: $text-muted;
}
</style>