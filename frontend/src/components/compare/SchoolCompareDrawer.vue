<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'
import type { AdmissionScore } from '@/types/admission'
import type { School } from '@/types/school'
import { useSchoolCompare } from '@/composables/useSchoolCompare'
import { fetchAdmissionScores, fetchFilterProvinces } from '@/api'
import { useApiMode } from '@/composables/useApiMode'
import CompareScoreChart from './CompareScoreChart.vue'

const { compareList, compareDrawerOpen, removeFromCompare, clearCompare, closeCompareDrawer } = useSchoolCompare()
const { isApiMode } = useApiMode()

const overlayEl = ref<HTMLDivElement | null>(null)

const provinces = ref<string[]>([])
const selectedProvince = ref('')
const selectedSubjectType = ref('')

const SUBJECT_TYPES = ['理科', '文科', '物理类', '历史类', '综合改革']

interface SchoolScores { school: School; scores: AdmissionScore[] }
const scoreData = ref<SchoolScores[]>([])
const scoresLoading = ref(false)

async function loadProvinces() {
  if (!isApiMode.value) return
  try {
    const data = await fetchFilterProvinces()
    provinces.value = data.map((p: any) => (typeof p === 'string' ? p : (p.province ?? p.name ?? '')))
      .filter(Boolean)
  } catch {
    provinces.value = ['北京', '上海', '广东', '浙江', '江苏', '山东', '四川', '湖北', '湖南', '陕西', '河南', '河北', '天津', '重庆', '福建']
  }
}

async function loadScores() {
  if (!selectedProvince.value || compareList.value.length === 0) {
    scoreData.value = []
    return
  }
  scoresLoading.value = true
  try {
    const results = await Promise.all(
      compareList.value.map(async (school) => {
        const params: Record<string, unknown> = { student_province: selectedProvince.value }
        if (selectedSubjectType.value) params.subject_type = selectedSubjectType.value
        const scores = isApiMode.value ? await fetchAdmissionScores(school.id, params) : []
        return { school, scores }
      })
    )
    scoreData.value = results
  } catch {
    scoreData.value = []
  } finally {
    scoresLoading.value = false
  }
}

watch(compareDrawerOpen, async (open) => {
  if (open) {
    await nextTick()
    overlayEl.value?.focus()
    loadProvinces()
    if (selectedProvince.value) loadScores()
  }
})

watch([selectedProvince, selectedSubjectType], () => {
  if (compareDrawerOpen.value) loadScores()
})

watch(compareList, () => {
  if (compareDrawerOpen.value && selectedProvince.value) loadScores()
}, { deep: true })

const hasScoreData = computed(() => scoreData.value.some(d => d.scores.length > 0))

const INFO_ROWS: { label: string; key: keyof School | ((s: School) => string); isLink?: boolean }[] = [
  { label: '院校层次', key: 'level' },
  { label: '所在地', key: (s) => `${s.province} ${s.city}` },
  { label: '学校类型', key: 'schoolType' },
  { label: '办学性质', key: 'ownership' },
  { label: '985', key: (s) => s.is985 ? '✓' : '—' },
  { label: '211', key: (s) => s.is211 ? '✓' : '—' },
  { label: '双一流', key: (s) => s.isDoubleFirstClass ? '✓' : '—' },
  { label: '官网', key: 'website', isLink: true },
]

function cellValue(school: School, row: typeof INFO_ROWS[number]): string {
  if (typeof row.key === 'function') return row.key(school)
  return String((school as any)[row.key] ?? '—')
}

// Empty slot count
const emptySlots = computed(() => Math.max(0, 3 - compareList.value.length))
</script>

<template>
  <Transition name="overlay-fade">
    <div
      v-if="compareDrawerOpen"
      ref="overlayEl"
      class="compare-overlay"
      tabindex="-1"
      @keydown.esc="closeCompareDrawer"
    >
      <!-- Header -->
      <div class="cmp-header">
        <div class="cmp-header-left">
          <button class="btn-back" @click="closeCompareDrawer" title="返回">
            <svg viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 4l-6 6 6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            返回
          </button>
          <h2 class="cmp-title">学校对比</h2>
        </div>
        <div class="cmp-header-actions">
          <button class="btn-clear-hd" @click="clearCompare">清空对比</button>
        </div>
      </div>

      <!-- Scrollable body -->
      <div class="cmp-body">

        <!-- School slots row -->
        <div class="school-slots">
          <div v-for="school in compareList" :key="school.id" class="school-slot">
            <div class="slot-badges">
              <span v-if="school.is985" class="badge badge-985">985</span>
              <span v-if="school.is211" class="badge badge-211">211</span>
              <span v-if="school.isDoubleFirstClass" class="badge badge-dfc">双一流</span>
            </div>
            <div class="slot-name">{{ school.name }}</div>
            <div class="slot-meta">{{ school.province }} · {{ school.schoolType }} · {{ school.level }}</div>
            <button class="slot-remove" @click="removeFromCompare(school.id)">移除</button>
          </div>
          <div v-for="n in emptySlots" :key="`empty-slot-${n}`" class="school-slot school-slot-empty">
            <span class="empty-hint">从列表或地图<br>添加院校</span>
          </div>
        </div>

        <!-- Basic info table -->
        <div class="cmp-section">
          <h3 class="section-title">基本信息</h3>
          <div class="table-wrap">
            <table class="info-table">
              <thead>
                <tr>
                  <th class="th-label"></th>
                  <th v-for="school in compareList" :key="school.id" class="th-school">{{ school.name }}</th>
                  <th v-for="n in emptySlots" :key="`th-empty-${n}`" class="th-school th-empty">—</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in INFO_ROWS" :key="row.label">
                  <td class="td-label">{{ row.label }}</td>
                  <td
                    v-for="school in compareList"
                    :key="school.id"
                    class="td-value"
                    :class="{ 'td-check': cellValue(school, row) === '✓', 'td-dash': cellValue(school, row) === '—' }"
                  >
                    <template v-if="row.isLink && school.website">
                      <a :href="school.website" target="_blank" class="cell-link">查看</a>
                    </template>
                    <template v-else>{{ cellValue(school, row) }}</template>
                  </td>
                  <td v-for="n in emptySlots" :key="`td-empty-${n}`" class="td-value td-dash">—</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Score comparison -->
        <div class="cmp-section">
          <h3 class="section-title">录取分数线对比</h3>
          <div class="score-filters">
            <label class="filter-label">生源省份</label>
            <el-select v-model="selectedProvince" placeholder="请选择省份" size="small" clearable style="width: 130px">
              <el-option v-for="p in provinces" :key="p" :label="p" :value="p" />
            </el-select>
            <label class="filter-label">科类</label>
            <el-select v-model="selectedSubjectType" placeholder="全部" size="small" clearable style="width: 120px">
              <el-option v-for="t in SUBJECT_TYPES" :key="t" :label="t" :value="t" />
            </el-select>
          </div>
          <div v-if="!selectedProvince" class="score-placeholder">
            请选择生源省份以查看分数线趋势对比
          </div>
          <div v-else-if="scoresLoading" class="score-placeholder">加载中…</div>
          <div v-else-if="!hasScoreData" class="score-placeholder">
            当前省份暂无分数线数据
          </div>
          <CompareScoreChart v-else :data="scoreData" />
        </div>

        <!-- Popular majors comparison -->
        <div class="cmp-section">
          <h3 class="section-title">热门专业 / 双一流学科</h3>
          <div class="majors-grid">
            <div v-for="school in compareList" :key="school.id" class="majors-col">
              <div class="majors-col-hd">{{ school.name }}</div>
              <div class="major-tags">
                <span
                  v-for="major in (school.popularMajors ?? []).slice(0, 12)"
                  :key="major"
                  class="major-tag"
                >{{ major }}</span>
                <span v-if="!school.popularMajors?.length" class="major-none">暂无数据</span>
              </div>
            </div>
            <div v-for="n in emptySlots" :key="`majors-empty-${n}`" class="majors-col majors-col-empty">—</div>
          </div>
        </div>

      </div>
    </div>
  </Transition>
</template>

<style scoped lang="scss">
@use '@/styles/variables' as *;

.compare-overlay {
  position: fixed;
  inset: 0;
  z-index: 2000;
  background: $bg-card;
  display: flex;
  flex-direction: column;
  outline: none;
}

/* Header */
.cmp-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 56px;
  border-bottom: 1px solid $border-color;
  flex-shrink: 0;
  background: $bg-card;
}

.cmp-header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.btn-back {
  display: flex;
  align-items: center;
  gap: 5px;
  background: none;
  border: none;
  padding: 5px 8px;
  border-radius: $radius-md;
  font-size: 14px;
  color: $text-secondary;
  cursor: pointer;
  transition: all 0.15s;

  svg {
    width: 16px;
    height: 16px;
    flex-shrink: 0;
  }

  &:hover {
    background: $bg-main;
    color: $text-primary;
  }
}

.cmp-title {
  font-size: 18px;
  font-weight: 700;
  color: $text-primary;
}

.cmp-header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.btn-clear-hd {
  background: none;
  border: 1px solid $border-color;
  border-radius: $radius-md;
  padding: 5px 12px;
  font-size: 13px;
  color: $text-secondary;
  cursor: pointer;
  &:hover { background: $bg-main; }
}

/* Scrollable body */
.cmp-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 32px;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
}

/* School slots */
.school-slots {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.school-slot {
  background: $bg-main;
  border: 1px solid $border-color;
  border-radius: $radius-lg;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  position: relative;

  &.school-slot-empty {
    border-style: dashed;
    align-items: center;
    justify-content: center;
    min-height: 120px;
  }
}

.empty-hint {
  color: $text-muted;
  font-size: 13px;
  text-align: center;
  line-height: 1.8;
}

.slot-badges {
  display: flex;
  gap: 4px;
}

.badge {
  display: inline-block;
  padding: 1px 6px;
  border-radius: $radius-sm;
  font-size: 11px;
  font-weight: 500;
  &.badge-985 { background: #fef2f2; color: $color-985; }
  &.badge-211 { background: #eff6ff; color: $color-211; }
  &.badge-dfc { background: #f5f3ff; color: $color-double-first; }
}

.slot-name {
  font-size: 16px;
  font-weight: 700;
  color: $text-primary;
}

.slot-meta {
  font-size: 12px;
  color: $text-muted;
}

.slot-remove {
  margin-top: 8px;
  align-self: flex-start;
  background: none;
  border: 1px solid $border-color;
  border-radius: $radius-sm;
  padding: 3px 10px;
  font-size: 12px;
  color: $text-secondary;
  cursor: pointer;
  &:hover { border-color: $color-danger; color: $color-danger; }
}

/* Sections */
.cmp-section {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.section-title {
  font-size: 15px;
  font-weight: 700;
  color: $text-primary;
  padding-bottom: 10px;
  border-bottom: 2px solid $color-primary-bg;
}

/* Info table */
.table-wrap {
  overflow-x: auto;
}

.info-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;

  th, td {
    padding: 10px 14px;
    text-align: left;
    border-bottom: 1px solid $border-color;
  }

  th {
    font-weight: 600;
    color: $text-secondary;
    background: $bg-main;
    white-space: nowrap;
  }

  .th-label { width: 90px; }
  .th-school { min-width: 160px; }
  .th-empty { color: $text-muted; }

  tr:hover td { background: $bg-main; }

  .td-label {
    color: $text-muted;
    font-size: 12px;
    white-space: nowrap;
  }

  .td-value {
    color: $text-primary;
  }

  .td-check {
    color: $color-success;
    font-weight: 700;
  }

  .td-dash {
    color: $text-muted;
  }
}

.cell-link {
  color: $color-primary-light;
  text-decoration: none;
  &:hover { text-decoration: underline; }
}

/* Score filters */
.score-filters {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.filter-label {
  font-size: 13px;
  color: $text-secondary;
  white-space: nowrap;
}

.score-placeholder {
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  color: $text-muted;
  background: $bg-main;
  border-radius: $radius-md;
  border: 1px dashed $border-color;
}

/* Majors comparison */
.majors-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.majors-col {
  display: flex;
  flex-direction: column;
  gap: 10px;

  &.majors-col-empty {
    color: $text-muted;
    font-size: 13px;
    padding: 16px;
  }
}

.majors-col-hd {
  font-size: 13px;
  font-weight: 600;
  color: $text-secondary;
  padding-bottom: 6px;
  border-bottom: 1px solid $border-light;
}

.major-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.major-tag {
  display: inline-block;
  padding: 3px 10px;
  background: $color-primary-bg;
  color: $color-primary;
  border-radius: $radius-sm;
  font-size: 12px;
}

.major-none {
  font-size: 12px;
  color: $text-muted;
}

/* Transition */
.overlay-fade-enter-active,
.overlay-fade-leave-active {
  transition: opacity 0.2s ease;
}
.overlay-fade-enter-from,
.overlay-fade-leave-to {
  opacity: 0;
}
</style>
