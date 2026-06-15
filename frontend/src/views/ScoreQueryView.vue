<script setup lang="ts">
import { ref, watch, onMounted, nextTick } from 'vue'
import type { School } from '@/types/school'
import {
  fetchAdmissionList,
  fetchFilterProvinces,
  fetchFilterYears,
  fetchFilterSubjects,
} from '@/api'
import AppHeader from '@/components/layout/AppHeader.vue'
import SchoolDetailDrawer from '@/components/school-map/SchoolDetailDrawer.vue'
import CompareFloatingBar from '@/components/compare/CompareFloatingBar.vue'
import SchoolCompareDrawer from '@/components/compare/SchoolCompareDrawer.vue'
import { useSchoolCompare } from '@/composables/useSchoolCompare'

interface AdmissionListItem {
  id: number
  schoolId: number
  schoolName: string
  schoolProvince: string
  schoolCity: string
  is985: boolean
  is211: boolean
  isDoubleFirstClass: boolean
  year: number
  batch: string | null
  subjectType: string
  minScore: number
  estimatedRank: number | null
}

// ── 筛选条件 ────────────────────────────────────────────────────────────────
const studentProvince = ref('')
const year = ref<number | null>(null)
const subjectType = ref('')
const keyword = ref('')
const tags = ref<string[]>([])
const currentPage = ref(1)
const pageSize = ref(20)

// ── 下拉选项 ────────────────────────────────────────────────────────────────
const provinces = ref<{ id: number; name: string }[]>([])
const yearOptions = ref<number[]>([])
const subjectOptions = ref<string[]>([])

// ── 结果 ────────────────────────────────────────────────────────────────────
const scoreList = ref<AdmissionListItem[]>([])
const total = ref(0)
const loading = ref(false)
const hasQueried = ref(false)

// ── 学校详情抽屉 ─────────────────────────────────────────────────────────────
const detailVisible = ref(false)
const selectedSchool = ref<School | null>(null)

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

// ── 初始化：拉取省份 + 年份范围 ───────────────────────────────────────────────
onMounted(async () => {
  const [provs, yrRange] = await Promise.all([
    fetchFilterProvinces(),
    fetchFilterYears(),
  ])
  provinces.value = provs
  const { minYear, maxYear } = yrRange
  if (minYear && maxYear) {
    for (let y = maxYear; y >= minYear; y--) yearOptions.value.push(y)
    year.value = maxYear
  }
})

// ── 省份/年份变化 → 重新拉取科类 ────────────────────────────────────────────
watch([studentProvince, year], async ([prov, y]) => {
  subjectOptions.value = []
  subjectType.value = ''
  if (prov && y) {
    const res = await fetchFilterSubjects(prov, y)
    subjectOptions.value = res.tracks
  }
})

// ── 筛选变化 → 重新查询（带 debounce） ──────────────────────────────────────
let debounceTimer: ReturnType<typeof setTimeout> | null = null

function scheduleLoad(immediate = false) {
  if (!studentProvince.value) return
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(loadScores, immediate ? 0 : 200)
}

watch([studentProvince, year, subjectType, tags], () => {
  currentPage.value = 1
  scheduleLoad()
}, { deep: true })

watch(keyword, () => {
  currentPage.value = 1
  scheduleLoad()
})

async function loadScores() {
  if (!studentProvince.value) return
  loading.value = true
  hasQueried.value = true
  try {
    const params: Record<string, unknown> = {
      studentProvince: studentProvince.value,
      page: currentPage.value,
      pageSize: pageSize.value,
    }
    if (year.value) params.year = year.value
    if (subjectType.value) params.subjectType = subjectType.value
    if (keyword.value) params.keyword = keyword.value
    if (tags.value.includes('985')) params['is_985'] = true
    if (tags.value.includes('211')) params['is_211'] = true
    if (tags.value.includes('双一流')) params['is_double_first_class'] = true

    const res = await fetchAdmissionList(params)
    scoreList.value = res.items as AdmissionListItem[]
    total.value = res.total
  } finally {
    loading.value = false
  }
}

function goToPage(page: number) {
  currentPage.value = page
  loadScores()
}

function setPageSize(size: number) {
  pageSize.value = size
  currentPage.value = 1
  loadScores()
}

function toggleTag(tag: string) {
  const idx = tags.value.indexOf(tag)
  if (idx >= 0) tags.value.splice(idx, 1)
  else tags.value.push(tag)
}

function resetFilter() {
  studentProvince.value = ''
  year.value = yearOptions.value[0] ?? null
  subjectType.value = ''
  keyword.value = ''
  tags.value = []
  scoreList.value = []
  total.value = 0
  hasQueried.value = false
}

function openDetail(row: AdmissionListItem) {
  selectedSchool.value = {
    id: row.schoolId,
    name: row.schoolName,
    province: row.schoolProvince,
    city: row.schoolCity,
    is985: row.is985,
    is211: row.is211,
    isDoubleFirstClass: row.isDoubleFirstClass,
    schoolCode: '',
    level: '本科',
    schoolType: '综合类',
    ownership: '公办',
    popularMajors: [],
  } as School
  detailVisible.value = true
}

function toggleCompare(e: MouseEvent, row: AdmissionListItem) {
  e.stopPropagation()
  const school = {
    id: row.schoolId,
    name: row.schoolName,
    province: row.schoolProvince,
    city: row.schoolCity,
    is985: row.is985,
    is211: row.is211,
    isDoubleFirstClass: row.isDoubleFirstClass,
    schoolCode: '',
    level: '本科',
    schoolType: '综合类',
    ownership: '公办',
    popularMajors: [],
  } as School
  if (isInCompare(row.schoolId)) removeFromCompare(row.schoolId)
  else addToCompare(school)
}

function formatRank(rank: number | null): string {
  if (rank == null) return '—'
  if (rank >= 10000) return (rank / 10000).toFixed(1) + ' 万'
  return rank.toLocaleString()
}
</script>

<template>
  <div class="score-page">
    <AppHeader :keyword="keyword" @update:keyword="keyword = $event" />

    <!-- Filter bar -->
    <div class="filter-bar">
      <div class="filter-left">
        <!-- 搜索院校 -->
        <div class="search-wrap">
          <svg class="search-icon" viewBox="0 0 20 20" fill="none">
            <path d="M9 17A8 8 0 109 1a8 8 0 000 16zM19 19l-4.35-4.35" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
          <input
            class="search-input"
            placeholder="搜索院校"
            :value="keyword"
            :disabled="!studentProvince"
            @input="keyword = ($event.target as HTMLInputElement).value"
          />
        </div>
        
        <!-- 生源省份（必填） -->
        <el-select
          v-model="studentProvince"
          placeholder="生源省份（必填）"
          size="small"
          clearable
          style="width: 140px"
        >
          <el-option
            v-for="p in provinces"
            :key="p.id"
            :label="p.name"
            :value="p.name"
          />
        </el-select>

        <!-- 年份 -->
        <el-select
          v-model="year"
          placeholder="年份"
          size="small"
          clearable
          style="width: 90px"
          :disabled="!studentProvince"
        >
          <el-option v-for="y in yearOptions" :key="y" :label="String(y)" :value="y" />
        </el-select>

        <!-- 科类 -->
        <el-select
          v-model="subjectType"
          placeholder="科类"
          size="small"
          clearable
          style="width: 100px"
          :disabled="!studentProvince || subjectOptions.length === 0"
        >
          <el-option v-for="s in subjectOptions" :key="s" :label="s" :value="s" />
        </el-select>


        <!-- 985 / 211 / 双一流 -->
        <div class="tag-toggles">
          <button
            v-for="tag in ['985', '211', '双一流']"
            :key="tag"
            class="tag-btn"
            :class="{ active: tags.includes(tag), [`tag-${tag}`]: true }"
            :disabled="!studentProvince"
            @click="toggleTag(tag)"
          >{{ tag }}</button>
        </div>
      </div>

      <div class="filter-right">
        <button class="btn-reset" @click="resetFilter">重置</button>
      </div>
    </div>

    <!-- 空态 / 结果区 -->
    <template v-if="!studentProvince && !hasQueried">
      <div class="empty-state">
        <svg class="empty-icon" viewBox="0 0 80 80" fill="none">
          <circle cx="40" cy="40" r="38" stroke="var(--color-border)" stroke-width="2"/>
          <path d="M26 52V32a4 4 0 014-4h20a4 4 0 014 4v20" stroke="var(--color-primary)" stroke-width="2" stroke-linecap="round"/>
          <path d="M22 52h36" stroke="var(--color-primary)" stroke-width="2" stroke-linecap="round"/>
          <path d="M36 28v-6M44 28v-6" stroke="var(--color-primary)" stroke-width="2" stroke-linecap="round"/>
          <rect x="34" y="37" width="12" height="15" rx="2" stroke="var(--color-primary)" stroke-width="2"/>
        </svg>
        <p class="empty-title">选择生源省份查看分数线</p>
        <p class="empty-sub">分数线按考生所在省份统计，请先在上方选择省份</p>
      </div>
    </template>

    <template v-else>
      <!-- Stats bar -->
      <div class="table-toolbar">
        <span class="stat-text" v-if="!loading">
          共 <b>{{ total.toLocaleString() }}</b> 条分数线记录
          <span v-if="studentProvince">（{{ studentProvince }}
            <template v-if="year"> · {{ year }} 年</template>
            <template v-if="subjectType"> · {{ subjectType }}</template>）
          </span>
        </span>
        <span class="stat-text" v-else>加载中…</span>
      </div>

      <!-- Table -->
      <div class="table-wrap">
        <div class="table-card">
          <el-table
            ref="tableRef"
            :data="scoreList"
            v-loading="loading"
            row-key="id"
            class="score-table"
            border
            :row-class-name="() => 'score-row'"
            @row-click="openDetail"
            @header-dragend="onHeaderDragend"
          >
            <!-- 院校名称 -->
            <el-table-column label="院校名称" min-width="200">
              <template #default="{ row }">
                <div class="name-cell">
                  <span class="school-name">{{ row.schoolName }}</span>
                  <div class="row-tags">
                    <span v-if="row.is985" class="badge badge-985">985</span>
                    <span v-if="row.is211" class="badge badge-211">211</span>
                    <span v-if="row.isDoubleFirstClass" class="badge badge-dfc">双一流</span>
                  </div>
                </div>
              </template>
            </el-table-column>

            <!-- 所在地 -->
            <el-table-column label="所在地" width="110">
              <template #default="{ row }">{{ row.schoolProvince }} {{ row.schoolCity }}</template>
            </el-table-column>

            <!-- 年份 -->
            <el-table-column prop="year" label="年份" width="70" />


            <!-- 科类 -->
            <el-table-column prop="subjectType" label="科类" width="80" />

            <!-- 最低分 -->
            <el-table-column label="最低分" width="90" sortable sort-by="minScore">
              <template #default="{ row }">
                <span class="score-val">{{ row.minScore }}</span>
              </template>
            </el-table-column>

            <!-- 估算位次 -->
            <el-table-column label="估算位次" width="100">
              <template #default="{ row }">
                <span class="rank-val">{{ formatRank(row.estimatedRank) }}</span>
              </template>
            </el-table-column>

            <!-- 对比 -->
            <el-table-column label="" width="80" fixed="right" :resizable="false">
              <template #default="{ row }">
                <button
                  class="cmp-btn"
                  :class="{ 'cmp-active': isInCompare(row.schoolId) }"
                  :disabled="!isInCompare(row.schoolId) && !canAddMore"
                  :title="isInCompare(row.schoolId) ? '移出对比' : '加入对比'"
                  @click="(e: MouseEvent) => toggleCompare(e, row)"
                >
                  {{ isInCompare(row.schoolId) ? '✓ 已加入' : '+ 对比' }}
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
          :total="total"
          :page-sizes="[20, 50, 100]"
          layout="sizes, prev, pager, next, jumper"
          @current-change="goToPage"
          @size-change="setPageSize"
        />
      </div>
    </template>

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

.score-page {
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
  width: 160px;
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
  &:disabled { opacity: 0.5; cursor: not-allowed; }
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

  &:disabled { opacity: 0.4; cursor: not-allowed; }
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

/* Empty state */
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.empty-icon {
  width: 80px;
  height: 80px;
  opacity: 0.5;
}

.empty-title {
  font-size: 16px;
  font-weight: 600;
  color: $text-primary;
  margin: 0;
}

.empty-sub {
  font-size: 13px;
  color: $text-muted;
  margin: 0;
}

/* Stats bar */
.table-toolbar {
  padding: 8px 20px;
  background: $bg-card;
  border-bottom: 1px solid $border-color;
  flex-shrink: 0;
}

.stat-text {
  font-size: 13px;
  color: $text-secondary;
  b { color: $text-primary; font-weight: 600; }
}

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

.score-table {
  width: 100%;

  :deep(.score-row) {
    cursor: pointer;
    &:hover td { background: $bg-main !important; }
  }

  :deep(.el-table__header th) {
    background: $bg-main;
    font-size: 13px;
    color: $text-secondary;
    font-weight: 600;
  }

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

.score-val {
  font-size: 15px;
  font-weight: 700;
  color: $color-primary;
}

.rank-val {
  font-size: 13px;
  color: $text-secondary;
}

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
}
</style>
