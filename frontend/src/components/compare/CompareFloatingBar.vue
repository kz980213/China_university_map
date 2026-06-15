<script setup lang="ts">
import { useSchoolCompare } from '@/composables/useSchoolCompare'

const { compareList, removeFromCompare, clearCompare, openCompareDrawer, MAX_COMPARE } = useSchoolCompare()
</script>

<template>
  <Transition name="bar-slide">
    <div v-if="compareList.length > 0" class="compare-bar">
      <div class="bar-content">
        <div class="bar-left">
          <span class="bar-hint">对比院校</span>
          <div class="chip-row">
            <div v-for="s in compareList" :key="s.id" class="chip chip-active">
              <span class="chip-name">{{ s.name }}</span>
              <button class="chip-del" @click.stop="removeFromCompare(s.id)" title="移除">×</button>
            </div>
            <div v-for="n in (MAX_COMPARE - compareList.length)" :key="`empty-${n}`" class="chip chip-empty">
              待添加
            </div>
          </div>
        </div>
        <div class="bar-right">
          <button class="btn-clear" @click="clearCompare">清空</button>
          <button
            class="btn-compare"
            :disabled="compareList.length < 2"
            @click="openCompareDrawer"
          >
            开始对比 ({{ compareList.length }}/{{ MAX_COMPARE }})
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped lang="scss">
@use '@/styles/variables' as *;

.compare-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 1200;
  background: $bg-card;
  border-top: 2px solid $color-primary;
  box-shadow: 0 -4px 16px rgba(0, 0, 0, 0.12);
  padding: 10px 24px;
}

.bar-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  max-width: 1400px;
  margin: 0 auto;
}

.bar-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
  overflow: hidden;
}

.bar-hint {
  font-size: 13px;
  font-weight: 600;
  color: $text-secondary;
  white-space: nowrap;
}

.chip-row {
  display: flex;
  gap: 8px;
  overflow: hidden;
}

.chip {
  display: flex;
  align-items: center;
  gap: 4px;
  border-radius: $radius-md;
  padding: 4px 10px;
  font-size: 13px;
  white-space: nowrap;

  &.chip-active {
    background: $color-primary-bg;
    border: 1px solid $color-primary-light;
    color: $color-primary;
  }

  &.chip-empty {
    background: $bg-main;
    border: 1px dashed $border-color;
    color: $text-muted;
    font-size: 12px;
  }
}

.chip-name {
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chip-del {
  background: none;
  border: none;
  color: $color-primary;
  cursor: pointer;
  font-size: 15px;
  line-height: 1;
  padding: 0;

  &:hover { color: $color-danger; }
}

.bar-right {
  display: flex;
  gap: 10px;
  flex-shrink: 0;
}

.btn-clear {
  background: none;
  border: 1px solid $border-color;
  border-radius: $radius-md;
  padding: 6px 14px;
  font-size: 13px;
  color: $text-secondary;
  cursor: pointer;

  &:hover { background: $bg-main; }
}

.btn-compare {
  background: $color-primary;
  border: none;
  border-radius: $radius-md;
  padding: 6px 18px;
  font-size: 13px;
  font-weight: 600;
  color: white;
  cursor: pointer;
  transition: background 0.2s;

  &:hover:not(:disabled) { background: $color-primary-dark; }
  &:disabled { background: $text-muted; cursor: not-allowed; }
}

.bar-slide-enter-active,
.bar-slide-leave-active {
  transition: transform 0.25s ease;
}
.bar-slide-enter-from,
.bar-slide-leave-to {
  transform: translateY(100%);
}
</style>
