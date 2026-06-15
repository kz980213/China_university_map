<script setup lang="ts">
import type { School } from '@/types/school'
import { useSchoolCompare } from '@/composables/useSchoolCompare'

const props = defineProps<{ school: School }>()

const {
  compareList,
  isInCompare,
  addToCompare,
  removeFromCompare,
  canAddMore,
  openCompareDrawer,
  MAX_COMPARE,
} = useSchoolCompare()
</script>

<template>
  <div class="compare-tab">

    <!-- Current school action -->
    <div class="current-section">
      <div class="current-header">
        <span class="current-label">当前院校</span>
        <span class="current-name">{{ school.name }}</span>
      </div>
      <button
        v-if="isInCompare(school.id)"
        class="btn-in-compare"
        @click="removeFromCompare(school.id)"
      >
        ✓ 已加入对比 — 点击移除
      </button>
      <button
        v-else
        class="btn-add-compare"
        :disabled="!canAddMore"
        @click="addToCompare(school)"
      >
        {{ canAddMore ? '+ 加入对比' : '对比栏已满（最多 3 所）' }}
      </button>
    </div>

    <!-- Compare list -->
    <div class="list-section">
      <h4 class="list-title">当前对比栏</h4>
      <div v-if="compareList.length === 0" class="list-empty">
        尚未添加院校，请从列表或地图中选择
      </div>
      <div v-else class="chip-grid">
        <div v-for="s in compareList" :key="s.id" class="compare-chip">
          <span class="chip-name">{{ s.name }}</span>
          <button class="chip-del" @click="removeFromCompare(s.id)">×</button>
        </div>
        <div v-for="n in (MAX_COMPARE - compareList.length)" :key="`empty-${n}`" class="compare-chip compare-chip-empty">
          待添加
        </div>
      </div>
    </div>

    <!-- Start compare -->
    <button
      class="btn-start"
      :disabled="compareList.length < 2"
      @click="openCompareDrawer"
    >
      开始对比 ({{ compareList.length }}/{{ MAX_COMPARE }})
    </button>
    <p v-if="compareList.length < 2" class="start-hint">至少需要 2 所院校才能对比</p>
  </div>
</template>

<style scoped lang="scss">
@use '@/styles/variables' as *;

.compare-tab {
  padding: 4px 0;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.current-section {
  background: $bg-main;
  border-radius: $radius-md;
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.current-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.current-label {
  font-size: 12px;
  color: $text-muted;
}

.current-name {
  font-size: 14px;
  font-weight: 600;
  color: $text-primary;
}

.btn-add-compare,
.btn-in-compare {
  border-radius: $radius-md;
  padding: 7px 16px;
  font-size: 13px;
  cursor: pointer;
  width: 100%;
  text-align: center;
  transition: all 0.15s;
}

.btn-add-compare {
  background: $color-primary;
  border: none;
  color: white;
  font-weight: 600;

  &:hover:not(:disabled) { background: $color-primary-dark; }
  &:disabled { background: $text-muted; cursor: not-allowed; }
}

.btn-in-compare {
  background: $color-primary-bg;
  border: 1px solid $color-primary-light;
  color: $color-primary;
  font-weight: 500;

  &:hover { background: #dbeafe; }
}

.list-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.list-title {
  font-size: 13px;
  font-weight: 600;
  color: $text-secondary;
}

.list-empty {
  font-size: 13px;
  color: $text-muted;
  padding: 16px 0;
}

.chip-grid {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.compare-chip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 12px;
  border-radius: $radius-md;
  font-size: 13px;

  &:not(.compare-chip-empty) {
    background: $color-primary-bg;
    border: 1px solid $color-primary-light;
    color: $color-primary;
  }

  &.compare-chip-empty {
    background: $bg-main;
    border: 1px dashed $border-color;
    color: $text-muted;
  }
}

.chip-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chip-del {
  background: none;
  border: none;
  color: $color-primary;
  cursor: pointer;
  font-size: 15px;
  line-height: 1;
  padding: 0;
  flex-shrink: 0;

  &:hover { color: $color-danger; }
}

.btn-start {
  background: $color-primary;
  border: none;
  border-radius: $radius-md;
  padding: 10px;
  font-size: 14px;
  font-weight: 600;
  color: white;
  cursor: pointer;
  width: 100%;
  transition: background 0.2s;

  &:hover:not(:disabled) { background: $color-primary-dark; }
  &:disabled { background: $text-muted; cursor: not-allowed; }
}

.start-hint {
  font-size: 12px;
  color: $text-muted;
  text-align: center;
  margin: -12px 0 0;
}
</style>
