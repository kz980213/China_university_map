<script setup lang="ts">
import { ref } from 'vue'
import type { School } from '@/types/school'
import StatCards from './StatCards.vue'
import SchoolCard from './SchoolCard.vue'

const props = defineProps<{
  schools: School[]
  total: number
  undergraduateCount: number
  juniorCollegeCount: number
  count985: number
  count211: number
  doubleFirstClassCount: number
  selectedProvince?: string
  loading?: boolean
  currentPage?: number
  totalPages?: number
  pageSize?: number
}>()

const emit = defineEmits<{
  selectSchool: [school: School]
  'update:page': [page: number]
  'update:pageSize': [size: number]
}>()

const PAGE_SIZE_OPTIONS = [10, 30, 50]
const jumpInput = ref<number | ''>('')

function handleJump() {
  const page = Number(jumpInput.value)
  if (!page || page < 1 || page > (props.totalPages ?? 1)) return
  emit('update:page', page)
  jumpInput.value = ''
}

function onPageSizeChange(e: Event) {
  const size = Number((e.target as HTMLSelectElement).value)
  emit('update:pageSize', size)
}
</script>

<template>
  <aside class="result-panel">
    <div class="result-header">
      <h3 class="result-title">
        {{ selectedProvince ? selectedProvince : '全国' }} · 高校列表
      </h3>
      <span class="result-total">共 {{ total }} 所</span>
    </div>

    <StatCards
      :total="total"
      :undergraduate-count="undergraduateCount"
      :junior-college-count="juniorCollegeCount"
      :count985="count985"
      :count211="count211"
      :double-first-class-count="doubleFirstClassCount"
    />

    <div class="school-list">
      <div v-if="loading" class="loading-state">加载中…</div>
      <template v-else>
        <SchoolCard
          v-for="school in schools"
          :key="school.id"
          :school="school"
          @click="emit('selectSchool', school)"
        />
        <div v-if="schools.length === 0" class="empty-state">
          <p>没有找到匹配的学校</p>
          <p class="empty-hint">请尝试调整筛选条件或搜索关键词</p>
        </div>
      </template>
    </div>

    <!-- 分页栏 -->
    <div class="pagination-bar">
      <div class="pagination-controls">
        <!-- 上一页 -->
        <button
          class="page-btn arrow-btn"
          :disabled="currentPage === 1"
          @click="emit('update:page', (currentPage ?? 1) - 1)"
        >‹</button>

        <!-- 页码信息 -->
        <span class="page-info">{{ currentPage ?? 1 }} / {{ totalPages ?? 1 }}</span>

        <!-- 下一页 -->
        <button
          class="page-btn arrow-btn"
          :disabled="currentPage === totalPages"
          @click="emit('update:page', (currentPage ?? 1) + 1)"
        >›</button>

        <!-- 每页条数 -->
        <span class="page-size-row">
          每页
          <select class="page-size-select" :value="pageSize ?? 30" @change="onPageSizeChange">
            <option v-for="s in PAGE_SIZE_OPTIONS" :key="s" :value="s">{{ s }}</option>
          </select>
          条
        </span>

        <!-- 跳转 -->
        <span class="jump-to">
          跳至
          <input
            v-model.number="jumpInput"
            class="jump-input"
            type="number"
            :min="1"
            :max="totalPages"
            placeholder="页"
            @keydown.enter="handleJump"
          />
          <button class="jump-btn" @click="handleJump">GO</button>
        </span>

      </div>
    </div>
  </aside>
</template>

<style scoped lang="scss">
@use '@/styles/variables' as *;

.result-panel {
  width: $result-panel-width;
  background: $bg-card;
  border-left: 1px solid $border-color;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid $border-light;
}

.result-title {
  font-size: 15px;
  font-weight: 600;
  color: $text-primary;
}

.result-total {
  font-size: 12px;
  color: $text-muted;
  white-space: nowrap;
}

.school-list {
  flex: 1;
  overflow-y: auto;
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.loading-state {
  text-align: center;
  padding: 40px 0;
  color: $text-muted;
  font-size: 14px;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: $text-secondary;

  .empty-hint {
    font-size: 13px;
    color: $text-muted;
    margin-top: 8px;
  }
}

/* ── 分页栏 ── */
.pagination-bar {
  flex-shrink: 0;
  padding: 10px 16px 12px;
  border-top: 1px solid $border-light;
  background: $bg-card;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: nowrap;
}

.page-btn {
  height: 28px;
  padding: 0 8px;
  border: 1px solid $border-color;
  border-radius: $radius-sm;
  font-size: 13px;
  color: $text-secondary;
  background: $bg-card;
  cursor: pointer;
  transition: all 0.15s;
  white-space: nowrap;

  &:hover:not(:disabled) {
    border-color: $color-primary-light;
    color: $color-primary;
    background: $color-primary-bg;
  }

  &:disabled {
    color: $text-muted;
    background: $bg-main;
    cursor: not-allowed;
    border-color: $border-light;
  }
}

.arrow-btn {
  width: 28px;
  padding: 0;
  font-size: 18px;
  line-height: 1;
  text-align: center;
}

.page-info {
  font-size: 13px;
  color: $text-secondary;
  min-width: 46px;
  text-align: center;
  flex-shrink: 0;
}

.page-size-row {
  display: flex;
  align-items: center;
  gap: 3px;
  font-size: 12px;
  color: $text-muted;
  margin-left: 2px;
}

.page-size-select {
  height: 26px;
  padding: 0 2px;
  border: 1px solid $border-color;
  border-radius: $radius-sm;
  font-size: 12px;
  color: $text-secondary;
  background: $bg-main;
  cursor: pointer;
  outline: none;

  &:focus { border-color: $color-primary-light; }
}

.jump-to {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: $text-muted;
}

.jump-input {
  width: 36px;
  height: 26px;
  text-align: center;
  border: 1px solid $border-color;
  border-radius: $radius-sm;
  font-size: 12px;
  color: $text-primary;
  background: $bg-main;
  outline: none;
  -moz-appearance: textfield;
  &::-webkit-inner-spin-button,
  &::-webkit-outer-spin-button { display: none; }

  &:focus { border-color: $color-primary-light; background: $bg-card; }
}

.jump-btn {
  height: 26px;
  padding: 0 7px;
  border: 1px solid $color-primary-light;
  border-radius: $radius-sm;
  font-size: 12px;
  color: $color-primary;
  background: $color-primary-bg;
  cursor: pointer;
  transition: all 0.15s;

  &:hover {
    background: $color-primary;
    color: #fff;
    border-color: $color-primary;
  }
}

</style>
