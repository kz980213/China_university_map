<script setup lang="ts">
import type { School } from '@/types/school'

defineProps<{
  school: School
}>()

defineEmits<{
  click: [school: School]
}>()
</script>

<template>
  <div class="ai-school-card" @click="$emit('click', school)">
    <div class="ai-card-header">
      <span class="ai-school-name">{{ school.name }}</span>
      <span v-if="school.is985" class="ai-tag ai-tag-985">985</span>
      <span v-if="school.is211" class="ai-tag ai-tag-211">211</span>
      <span v-if="school.isDoubleFirstClass" class="ai-tag ai-tag-double">双一流</span>
    </div>
    <div class="ai-card-meta">
      {{ school.province }} · {{ school.schoolType }} · {{ school.level }}
    </div>
  </div>
</template>

<style scoped lang="scss">
@use '@/styles/variables' as *;

.ai-school-card {
  background: $bg-card;
  border: 1px solid $border-color;
  border-radius: $radius-md;
  padding: 10px 14px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    border-color: $color-primary-light;
    background: $color-primary-bg;
  }
}

.ai-card-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 4px;
}

.ai-school-name {
  font-size: 14px;
  font-weight: 600;
  color: $text-primary;
}

.ai-tag {
  padding: 1px 5px;
  border-radius: 3px;
  font-size: 10px;
  font-weight: 600;

  &.ai-tag-985 {
    background: #fef2f2;
    color: $color-985;
  }
  &.ai-tag-211 {
    background: #eff6ff;
    color: $color-211;
  }
  &.ai-tag-double {
    background: #f5f3ff;
    color: $color-double-first;
  }
}

.ai-card-meta {
  font-size: 12px;
  color: $text-muted;
}
</style>