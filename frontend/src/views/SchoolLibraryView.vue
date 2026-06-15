<script setup lang="ts">
import { ref, nextTick } from 'vue'
import type { School } from '@/types/school'
import { useSchoolFilter } from '@/composables/useSchoolFilter'
import AppHeader from '@/components/layout/AppHeader.vue'
import SchoolDetailDrawer from '@/components/school-map/SchoolDetailDrawer.vue'
import CompareFloatingBar from '@/components/compare/CompareFloatingBar.vue'
import SchoolCompareDrawer from '@/components/compare/SchoolCompareDrawer.vue'
import { useSchoolCompare } from '@/composables/useSchoolCompare'

const {
  filter,
  filteredSchools,
  provinceStatCounts,
  schoolsLoading,
  currentPage,
  pageSize,
  totalPages,
  goToPage,
  setPageSize,
  setKeyword,
  updateFilter,
  resetFilter,
  schoolsTotal,
} = useSchoolFilter()

const { addToCompare, removeFromCompare, isInCompare, canAddMore } = useSchoolCompare()

// ── 列宽拖拽：freed width 等分给其余可调列 ─────────────────────────────────
const tableRef = ref()

function onHeaderDragend(newWidth: number, oldWidth: number, column: any) {
  const delta = oldWidth - newWidth
  if (Math.abs(delta) < 1) return
  nextTick(() => {
    const cols: any[] = tableRef.value?.columns ?? []
    const others = cols.filter((c: any) => c.id !== column.id && !c.fixed)
    if (!others.length) return
    const perCol = delta / others.length
    others.forEach((c: any) => {
      const cur = c.realWidth ?? c.width ?? (c.minWidth || 60)
      const next = Math.max(c.minWidth || 50, Math.round(cur + perCol))
      c.width = next
      c.realWidth = next
    })
    tableRef.value?.doLayout()
  })
}

const selectedSchool = ref<School | null>(null)
const detailVisible = ref(false)

const SCHOOL_TYPES = ['综合类', '理工类', '师范类', '医药类', '财经类', '政法类', '艺术类', '体育类', '其他']
const PROVINCES = [
  '北京', '天津', '上海', '重庆', '河北', '山西', '内蒙古', '辽宁', '吉林', '黑龙江',
  '江苏', '浙江', '安徽', '福建', '江西', '山东', '河南', '湖北', '湖南', '广东',
  '广西', '海南', '四川', '贵州', '云南', '西藏', '陕西', '甘肃', '青海', '宁夏', '新疆',
]

function openDetail(school: School) {
  selectedSchool.value = school
  detailVisible.value = true
}

function toggleCompare(e: MouseEvent, school: School) {
  e.stopPropagation()
  if (isInCompare(school.id)) {
    removeFromCompare(school.id)
  } else {
    addToCompare(school)
  }
}

function toggleTag(tag: string) {
  const tags = filter.value.tags
  if (tags.includes(tag)) {
    updateFilter({ tags: tags.filter(t => t !== tag) })
  } else {
    updateFilter({ tags: [...tags, tag] })
  }
}

const SORT_OPTIONS = [
  { label: '默认排序', value: '' },
  { label: '按名称 A→Z', value: 'name_asc' },
  { label: '按省份', value: 'province' },
]
const sortBy = ref('')
</script>

<template>
  <div class="library-page">

    <AppHeader :keyword="filter.keyword" @update:keyword="setKeyword" />

    <!-- Filter bar -->
    <div class="filter-bar">
      <div class="filter-left">
        <div class="search-wrap">
          <svg class="search-icon" viewBox="0 0 20 20" fill="none">
            <path d="M9 17A8 8 0 109 1a8 8 0 000 16zM19 19l-4.35-4.35" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
          <input
            class="search-input"
            placeholder="搜索院校 / 城市"
            :value="filter.keyword"
            @input="setKeyword(($event.target as HTMLInputElement).value)"
          />
        </div>

        <el-select
          :model-value="filter.province ?? ''"
          placeholder="全部省份"
          size="small"
          clearable
          style="width: 110px"
          @change="(v: string) => updateFilter({ province: v || undefined })"
        >
          <el-option v-for="p in PROVINCES" :key="p" :label="p" :value="p" />
        </el-select>

        <el-select
          :model-value="filter.levels[0] ?? ''"
          placeholder="办学层次"
          size="small"
          clearable
          style="width: 100px"
          @change="(v: string) => updateFilter({ levels: v ? [v] : [] })"
        >
          <el-option label="本科" value="本科" />
          <el-option label="专科/高职" value="专科,高职" />
        </el-select>

        <el-select
          :model-value="filter.schoolTypes[0] ?? ''"
          placeholder="院校类型"
          size="small"
          clearable
          style="width: 110px"
          @change="(v: string) => updateFilter({ schoolTypes: v ? [v] : [] })"
        >
          <el-option v-for="t in SCHOOL_TYPES" :key="t" :label="t" :value="t" />
        </el-select>

        <el-select
          :model-value="filter.ownerships[0] ?? ''"
          placeholder="办学性质"
          size="small"
          clearable
          style="width: 100px"
          @change="(v: string) => updateFilter({ ownerships: v ? [v] : [] })"
        >
          <el-option label="公办" value="公办" />
          <el-option label="民办" value="民办" />
          <el-option label="中外合作" value="中外合作" />
        </el-select>

        <div class="tag-toggles">
          <button
            v-for="tag in ['985', '211', '双一流']"
            :key="tag"
            class="tag-btn"
            :class="{ active: filter.tags.includes(tag), [`tag-${tag}`]: true }"
            @click="toggleTag(tag)"
          >{{ tag }}</button>
        </div>
      </div>

      <div class="filter-right">
        <button class="btn-reset" @click="resetFilter">重置</button>
      </div>
    </div>

    <!-- Stats + table controls -->
    <div class="table-toolbar">
      <div class="stats-strip">
        <span class="stat-item">全部：<b>{{ provinceStatCounts.total }}</b></span>
        <span class="stat-sep">|</span>
        <span class="stat-item">本科：<b>{{ provinceStatCounts.undergraduateCount }}</b></span>
        <span class="stat-sep">|</span>
        <span class="stat-item">专科/高职：<b>{{ provinceStatCounts.juniorCollegeCount }}</b></span>
        <span class="stat-sep">|</span>
        <span class="stat-item tag-985-text">985：<b>{{ provinceStatCounts.count985 }}</b></span>
        <span class="stat-sep">|</span>
        <span class="stat-item tag-211-text">211：<b>{{ provinceStatCounts.count211 }}</b></span>
        <span class="stat-sep">|</span>
        <span class="stat-item tag-dfc-text">双一流：<b>{{ provinceStatCounts.doubleFirstClassCount }}</b></span>
      </div>
    </div>

    <!-- Table -->
    <div class="table-wrap">
      <div class="table-card">
      <el-table
        ref="tableRef"
        :data="filteredSchools"
        v-loading="schoolsLoading"
        row-key="id"
        class="school-table"
        border
        :row-class-name="() => 'school-row'"
        @row-click="openDetail"
        @header-dragend="onHeaderDragend"
      >
        <el-table-column label="院校名称" min-width="220">
          <template #default="{ row }">
            <div class="name-cell">
              <span class="school-name">{{ row.name }}</span>
              <div class="row-tags">
                <span v-if="row.is985" class="badge badge-985">985</span>
                <span v-if="row.is211" class="badge badge-211">211</span>
                <span v-if="row.isDoubleFirstClass" class="badge badge-dfc">双一流</span>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="所在地" width="120" sortable sort-by="province">
          <template #default="{ row }">{{ row.province }} {{ row.city }}</template>
        </el-table-column>

        <el-table-column prop="level" label="层次" width="80">
          <template #default="{ row }">
            <span class="level-badge" :class="`level-${row.level === '本科' ? 'bk' : 'zk'}`">
              {{ row.level }}
            </span>
          </template>
        </el-table-column>

        <el-table-column prop="schoolType" label="类型" width="90" />

        <el-table-column prop="ownership" label="性质" width="80" />

        <el-table-column label="热门专业" min-width="160">
          <template #default="{ row }">
            <span
              v-for="major in (row.popularMajors ?? []).slice(0, 3)"
              :key="major"
              class="major-chip"
            >{{ major }}</span>
            <span v-if="!row.popularMajors?.length" class="no-data">—</span>
          </template>
        </el-table-column>

        <el-table-column label="" width="80" fixed="right" :resizable="false">
          <template #default="{ row }">
            <button
              class="cmp-btn"
              :class="{ 'cmp-active': isInCompare(row.id) }"
              :disabled="!isInCompare(row.id) && !canAddMore"
              :title="isInCompare(row.id) ? '移出对比' : '加入对比'"
              @click="(e: MouseEvent) => toggleCompare(e, row)"
            >
              {{ isInCompare(row.id) ? '✓ 已加入' : '+ 对比' }}
            </button>
          </template>
        </el-table-column>
      </el-table>
      </div>
    </div>

    <!-- Pagination -->
    <div class="pagination-bar">
      <el-pagination
        :current-page="currentPage"
        :page-size="pageSize"
        :total="schoolsTotal"
        :page-sizes="[10, 30, 50]"
        layout="sizes, prev, pager, next, jumper"
        @current-change="goToPage"
        @size-change="setPageSize"
      />
    </div>

    <SchoolDetailDrawer
      :visible="detailVisible"
      :school="selectedSchool"
      @close="detailVisible = false"
    />

    <CompareFloatingBar />
    <SchoolCompareDrawer />
  </div>
</template>

<style scoped lang="scss">
@use '@/styles/variables' as *;

.library-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: $bg-main;
}

/* Filter bar */
.filter-bar {
  background: $bg-card;
  border-bottom: 1px solid $border-color;
  padding: 10px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-shrink: 0;
}

.filter-left {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.search-wrap {
  position: relative;
}

.search-icon {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  width: 15px;
  height: 15px;
  color: $text-muted;
  pointer-events: none;
}

.search-input {
  width: 200px;
  height: 32px;
  padding: 0 12px 0 32px;
  border: 1px solid $border-color;
  border-radius: $radius-md;
  font-size: 13px;
  color: $text-primary;
  background: $bg-main;
  outline: none;

  &:focus {
    border-color: $color-primary-light;
    background: $bg-card;
  }

  &::placeholder { color: $text-muted; }
}

.tag-toggles {
  display: flex;
  gap: 4px;
}

.tag-btn {
  padding: 3px 10px;
  border-radius: $radius-sm;
  border: 1px solid $border-color;
  background: $bg-main;
  font-size: 12px;
  font-weight: 500;
  color: $text-secondary;
  cursor: pointer;
  transition: all 0.15s;

  &.tag-985.active { background: #fef2f2; border-color: $color-985; color: $color-985; }
  &.tag-211.active { background: #eff6ff; border-color: $color-211; color: $color-211; }
  &.tag-双一流.active { background: #f5f3ff; border-color: $color-double-first; color: $color-double-first; }
}

.btn-reset {
  background: none;
  border: 1px solid $border-color;
  border-radius: $radius-md;
  padding: 5px 12px;
  font-size: 13px;
  color: $text-secondary;
  cursor: pointer;
  &:hover { background: $bg-main; }
}

/* Toolbar */
.table-toolbar {
  padding: 8px 20px;
  background: $bg-card;
  border-bottom: 1px solid $border-color;
  flex-shrink: 0;
}

.stats-strip {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
}

.stat-item {
  color: $text-secondary;
  b { color: $text-primary; }
}

.stat-sep { color: $border-color; }

.tag-985-text b { color: $color-985; }
.tag-211-text b { color: $color-211; }
.tag-dfc-text b { color: $color-double-first; }

/* Table */
.table-wrap {
  flex: 1;
  overflow-y: auto;
  padding: 12px 20px 0;
}

.table-card {
  border: 1px solid $border-color;
  border-radius: $radius-md;
  overflow: hidden;
  background: $bg-card;
}

.school-table {
  width: 100%;

  :deep(.school-row) {
    cursor: pointer;
    &:hover td { background: $bg-main !important; }
  }

  :deep(.el-table__header th) {
    background: $bg-main;
    font-size: 13px;
    color: $text-secondary;
    font-weight: 600;
  }

  // 移除 el-table 自带的外边框，改由 .table-card 统一控制
  :deep(.el-table__border-left-patch),
  :deep(.el-table__inner-wrapper::before),
  :deep(.el-table__inner-wrapper::after) {
    display: none;
  }
}

.name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.school-name {
  font-size: 14px;
  font-weight: 600;
  color: $text-primary;
}

.row-tags {
  display: flex;
  gap: 3px;
}

.badge {
  display: inline-block;
  padding: 1px 5px;
  border-radius: $radius-sm;
  font-size: 11px;
  font-weight: 600;
  line-height: 1.5;

  &.badge-985 { background: #fef2f2; color: $color-985; }
  &.badge-211 { background: #eff6ff; color: $color-211; }
  &.badge-dfc { background: #f5f3ff; color: $color-double-first; }
}

.level-badge {
  display: inline-block;
  padding: 2px 7px;
  border-radius: $radius-sm;
  font-size: 12px;
  font-weight: 500;
  &.level-bk { background: $color-primary-bg; color: $color-primary; }
  &.level-zk { background: $bg-main; color: $text-secondary; }
}

.major-chip {
  display: inline-block;
  padding: 1px 7px;
  background: $color-primary-bg;
  color: $color-primary;
  border-radius: $radius-sm;
  font-size: 11px;
  margin-right: 4px;
}

.no-data { color: $text-muted; font-size: 13px; }

.cmp-btn {
  font-size: 12px;
  padding: 3px 8px;
  border-radius: $radius-sm;
  border: 1px solid $border-color;
  background: $bg-card;
  color: $text-secondary;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.15s;

  &:hover:not(:disabled) {
    border-color: $color-primary-light;
    color: $color-primary;
  }

  &.cmp-active {
    background: $color-primary-bg;
    border-color: $color-primary-light;
    color: $color-primary;
  }

  &:disabled { opacity: 0.4; cursor: not-allowed; }
}

/* Pagination */
.pagination-bar {
  padding: 10px 20px;
  background: $bg-card;
  border-top: 1px solid $border-color;
  flex-shrink: 0;
  display: flex;
  justify-content: flex-end;
  :deep(.el-select) {
    width: 65px;
  }
}
</style>
