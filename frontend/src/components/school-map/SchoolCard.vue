<script setup lang="ts">
import type { School } from '@/types/school'
import { useSchoolCompare } from '@/composables/useSchoolCompare'

const props = defineProps<{
  school: School
}>()

defineEmits<{
  click: [school: School]
}>()

const { isInCompare, addToCompare, removeFromCompare, canAddMore } = useSchoolCompare()

function toggleCompare(e: MouseEvent) {
  e.stopPropagation()
  if (isInCompare(props.school.id)) {
    removeFromCompare(props.school.id)
  } else {
    addToCompare(props.school)
  }
}
</script>

<template>
  <div class="school-card" @click="$emit('click', school)">
    <div class="card-header">
      <h4 class="school-name">{{ school.name }}</h4>
      <div class="card-right">
        <div class="card-tags">
          <span v-if="school.is985" class="tag tag-985">985</span>
          <span v-if="school.is211" class="tag tag-211">211</span>
          <span v-if="school.isDoubleFirstClass" class="tag tag-double">双一流</span>
          <span class="tag tag-level">{{ school.level }}</span>
        </div>
        <button
          class="compare-btn"
          :class="{ 'compare-active': isInCompare(school.id) }"
          :disabled="!isInCompare(school.id) && !canAddMore"
          :title="isInCompare(school.id) ? '移出对比' : '加入对比'"
          @click="toggleCompare"
        >{{ isInCompare(school.id) ? '✓' : '+' }}</button>
      </div>
    </div>
    <div class="card-meta">
      <span class="meta-item">{{ school.province }} {{ school.city }}</span>
      <span class="meta-divider">|</span>
      <span class="meta-item">{{ school.schoolType }}</span>
      <span class="meta-divider">|</span>
      <span class="meta-item">{{ school.ownership }}</span>
    </div>
    <div class="card-majors">
      <span v-for="major in (school.popularMajors || []).slice(0, 3)" :key="major" class="major-tag">
        {{ major }}
      </span>
    </div>
  </div>
</template>

<style scoped lang="scss">
@use '@/styles/variables' as *;

.school-card {
  background: $bg-card;
  border: 1px solid $border-color;
  border-radius: $radius-md;
  padding: 14px 16px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    border-color: $color-primary-light;
    box-shadow: $shadow-md;
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.school-name {
  font-size: 15px;
  font-weight: 600;
  color: $text-primary;
  flex: 1;
  min-width: 0;
}

.card-right {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
  margin-left: 8px;
}

.card-tags {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}

.compare-btn {
  width: 22px;
  height: 22px;
  flex-shrink: 0;
  border-radius: 50%;
  border: 1.5px solid $border-color;
  background: $bg-card;
  color: $text-muted;
  font-size: 13px;
  line-height: 1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  transition: all 0.15s;

  &:hover:not(:disabled) {
    border-color: $color-primary-light;
    color: $color-primary-light;
  }

  &.compare-active {
    background: $color-primary;
    border-color: $color-primary;
    color: white;
  }

  &:disabled {
    opacity: 0.35;
    cursor: not-allowed;
  }
}

.tag {
  display: inline-block;
  padding: 1px 6px;
  border-radius: $radius-sm;
  font-size: 11px;
  font-weight: 500;
  line-height: 1.6;

  &.tag-985 {
    background: #fef2f2;
    color: $color-985;
  }
  &.tag-211 {
    background: #eff6ff;
    color: $color-211;
  }
  &.tag-double {
    background: #f5f3ff;
    color: $color-double-first;
  }
  &.tag-level {
    background: $bg-main;
    color: $text-secondary;
  }
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: $text-muted;
  margin-bottom: 10px;
}

.meta-divider {
  color: $border-color;
}

.card-majors {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.major-tag {
  display: inline-block;
  padding: 2px 8px;
  background: $color-primary-bg;
  color: $color-primary;
  border-radius: $radius-sm;
  font-size: 12px;
}
</style>