<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import type { School } from '@/types/school'
import {
  fetchVolunteerRecommend,
  fetchFilterProvinces,
  fetchFilterYears,
  fetchFilterSubjects,
} from '@/api'
import AppHeader from '@/components/layout/AppHeader.vue'
import SchoolDetailDrawer from '@/components/school-map/SchoolDetailDrawer.vue'
import CompareFloatingBar from '@/components/compare/CompareFloatingBar.vue'
import SchoolCompareDrawer from '@/components/compare/SchoolCompareDrawer.vue'
import { useSchoolCompare } from '@/composables/useSchoolCompare'

interface VolunteerItem {
  schoolId: number
  schoolName: string
  schoolProvince: string
  schoolCity: string
  is985: boolean
  is211: boolean
  isDoubleFirstClass: boolean
  minScore: number
  schoolRank: number
  rankDiff: number  // 正=余量，负=差距
}

interface VolunteerResult {
  score: number
  province: string
  year: number
  subjectType: string
  userRank: number | null
  userRankReason: string
  error: string | null
  reach: VolunteerItem[]
  target: VolunteerItem[]
  safety: VolunteerItem[]
}

// ── 输入 ─────────────────────────────────────────────────────────────────────
const score = ref<number | null>(null)
const province = ref('')
const year = ref<number | null>(null)
const subjectType = ref('')

// ── 下拉选项 ──────────────────────────────────────────────────────────────────
const provinces = ref<{ id: number; name: string }[]>([])
const yearOptions = ref<number[]>([])
const subjectOptions = ref<string[]>([])

// ── 结果 ─────────────────────────────────────────────────────────────────────
const result = ref<VolunteerResult | null>(null)
const loading = ref(false)
const errorMsg = ref('')

// ── 学校详情抽屉 ──────────────────────────────────────────────────────────────
const detailVisible = ref(false)
const selectedSchool = ref<School | null>(null)

const { addToCompare, removeFromCompare, isInCompare, canAddMore } = useSchoolCompare()

// ── 初始化 ────────────────────────────────────────────────────────────────────
onMounted(async () => {
  const [provs, yrRange] = await Promise.all([
    fetchFilterProvinces(),
    fetchFilterYears(),
  ])
  provinces.value = provs
  const { minYear, maxYear } = yrRange
  if (minYear && maxYear) {
    for (let y = maxYear; y >= minYear; y--) yearOptions.value.push(y)
    // 默认最新有一分一段数据的年份（2023-2025）
    year.value = Math.min(maxYear, 2025)
  }
})

watch([province, year], async ([prov, y]) => {
  subjectOptions.value = []
  subjectType.value = ''
  if (prov && y) {
    const res = await fetchFilterSubjects(prov, y)
    subjectOptions.value = res.tracks
    if (res.tracks.length === 1) subjectType.value = res.tracks[0]
  }
})

// ── 查询 ─────────────────────────────────────────────────────────────────────
async function query() {
  if (!score.value || !province.value || !year.value || !subjectType.value) return
  errorMsg.value = ''
  loading.value = true
  try {
    const res = await fetchVolunteerRecommend({
      score: score.value,
      province: province.value,
      year: year.value,
      subjectType: subjectType.value,
    })
    if (res.error) {
      errorMsg.value = errorLabel(res.error)
      result.value = null
    } else {
      result.value = res
    }
  } catch (e) {
    errorMsg.value = '查询失败，请稍后重试'
    result.value = null
  } finally {
    loading.value = false
  }
}

function errorLabel(code: string): string {
  if (code === 'no_data') return `${year.value} 年 ${province.value} ${subjectType.value} 暂无一分一段数据，无法估算位次`
  if (code === 'out_of_range') return '分数超出一分一段表范围，请确认分数是否正确'
  if (code === 'no_province') return '未找到该省份数据'
  return `数据异常（${code}），请联系管理员`
}

// ── 交互 ─────────────────────────────────────────────────────────────────────
function openDetail(item: VolunteerItem) {
  selectedSchool.value = {
    id: item.schoolId,
    name: item.schoolName,
    province: item.schoolProvince,
    city: item.schoolCity,
    is985: item.is985,
    is211: item.is211,
    isDoubleFirstClass: item.isDoubleFirstClass,
    schoolCode: '', level: '本科', schoolType: '综合类', ownership: '公办', popularMajors: [],
  } as School
  detailVisible.value = true
}

function toggleCompare(e: MouseEvent, item: VolunteerItem) {
  e.stopPropagation()
  const school = {
    id: item.schoolId,
    name: item.schoolName,
    province: item.schoolProvince,
    city: item.schoolCity,
    is985: item.is985, is211: item.is211, isDoubleFirstClass: item.isDoubleFirstClass,
    schoolCode: '', level: '本科', schoolType: '综合类', ownership: '公办', popularMajors: [],
  } as School
  if (isInCompare(item.schoolId)) removeFromCompare(item.schoolId)
  else addToCompare(school)
}

function formatRank(r: number): string {
  if (r >= 10000) return (r / 10000).toFixed(1) + ' 万'
  return r.toLocaleString()
}

const canQuery = () => !!score.value && score.value >= 100 && score.value <= 750
  && !!province.value && !!year.value && !!subjectType.value
</script>

<template>
  <div class="volunteer-page">
    <AppHeader :keyword="''" @update:keyword="() => {}" />

    <!-- 输入区 -->
    <div class="input-section">
      <div class="input-card">
        <div class="input-card-title">
          <span class="title-icon">🎯</span>
          志愿辅助 · 智能推荐
        </div>
        <div class="input-card-sub">根据您的高考分数，智能匹配冲一冲 / 稳一稳 / 保一保院校</div>
        <div class="algo-note">
          <span class="algo-note-label">评估方式</span>
          将您的分数通过<b>一分一段表</b>换算为全省位次，与院校历年最低录取位次对比（位次越小成绩越好）：
          <span class="algo-chips">
            <span class="chip chip-reach">冲：院校位次比您好，差距&nbsp;&lt;&nbsp;30%</span>
            <span class="chip chip-target">稳：您的位次优于录取线，余量&nbsp;0–30%</span>
            <span class="chip chip-safety">保：余量&nbsp;30%–150%</span>
          </span>
        </div>
        <div class="input-row">
          <div class="input-item">
            <label class="input-label">高考分数</label>
            <input
              v-model.number="score"
              class="score-input"
              type="number"
              placeholder="请输入分数"
              min="100" max="750"
              @keydown.enter="canQuery() && query()"
            />
          </div>
          <div class="input-item">
            <label class="input-label">生源省份</label>
            <el-select v-model="province" placeholder="请选择" size="default" style="width: 140px">
              <el-option v-for="p in provinces" :key="p.id" :label="p.name" :value="p.name" />
            </el-select>
          </div>
          <div class="input-item">
            <label class="input-label">年份</label>
            <el-select v-model="year" placeholder="年份" size="default" style="width: 100px" :disabled="!province">
              <el-option v-for="y in yearOptions" :key="y" :label="String(y)" :value="y" />
            </el-select>
          </div>
          <div class="input-item">
            <label class="input-label">科类</label>
            <el-select v-model="subjectType" placeholder="科类" size="default" style="width: 120px" :disabled="!province || !year">
              <el-option v-for="s in subjectOptions" :key="s" :label="s" :value="s" />
            </el-select>
          </div>
          <button
            class="btn-query"
            :disabled="!canQuery() || loading"
            @click="query"
          >
            <span v-if="loading">查询中…</span>
            <span v-else>开始推荐</span>
          </button>
        </div>

        <!-- 错误提示 -->
        <div v-if="errorMsg" class="error-msg">⚠️ {{ errorMsg }}</div>

        <!-- 用户位次信息 -->
        <div v-if="result && result.userRank" class="rank-info">
          您的分数 <b>{{ result.score }} 分</b>，估算位次 第
          <b class="rank-num">{{ formatRank(result.userRank) }}</b> 名
          <span class="rank-meta">（{{ result.year }} 年 · {{ result.province }} · {{ result.subjectType }}）</span>
          <span v-if="result.userRankReason === 'floored'" class="rank-note">位次为近似值</span>
        </div>
      </div>
    </div>

    <!-- 空态 -->
    <div v-if="!result && !loading" class="empty-state">
      <div class="empty-cols">
        <div class="empty-col reach-col">
          <div class="col-header">冲一冲</div>
          <div class="col-criteria">院校录取线位次优于您，但差距 &lt; 30%</div>
          <div class="col-desc">分数略有不足、胜算不高，但差距可控，适合以小博大、争取超常发挥的志愿。</div>
        </div>
        <div class="empty-col target-col">
          <div class="col-header">稳一稳</div>
          <div class="col-criteria">您的位次优于录取线，余量 0–30%</div>
          <div class="col-desc">成绩与录取线匹配，在正常发挥下录取把握较大，是志愿填报的核心梯队。</div>
        </div>
        <div class="empty-col safety-col">
          <div class="col-header">保一保</div>
          <div class="col-criteria">您的位次优于录取线，余量 30–150%</div>
          <div class="col-desc">成绩明显高于录取线，录取概率高，作为保底院校可为整体志愿方案兜底。</div>
        </div>
      </div>
    </div>

    <!-- 结果区 -->
    <div v-if="result" class="results-section">
      <div class="results-cols">

        <!-- 冲一冲 -->
        <div class="result-col">
          <div class="col-head reach-head">
            <span class="col-label">冲一冲</span>
            <span class="col-count">{{ result.reach.length }} 所</span>
          </div>
          <div class="col-desc">院校录取位次优于您，差距 &lt; 30%，风险较高但值得一搏</div>
          <div class="school-list">
            <div
              v-for="item in result.reach"
              :key="item.schoolId"
              class="school-card"
              @click="openDetail(item)"
            >
              <div class="card-main">
                <div class="card-name">
                  {{ item.schoolName }}
                  <span v-if="item.is985" class="badge badge-985">985</span>
                  <span v-if="item.is211" class="badge badge-211">211</span>
                  <span v-if="item.isDoubleFirstClass" class="badge badge-dfc">双一流</span>
                </div>
                <div class="card-loc">{{ item.schoolProvince }} {{ item.schoolCity }}</div>
              </div>
              <div class="card-stats">
                <div class="stat-block">
                  <div class="stat-val">{{ item.minScore }}</div>
                  <div class="stat-lbl">历史最低分</div>
                </div>
                <div class="stat-block">
                  <div class="stat-val">{{ formatRank(item.schoolRank) }}</div>
                  <div class="stat-lbl">历史位次</div>
                </div>
                <div class="stat-block">
                  <div class="stat-val reach-diff">差 {{ formatRank(-item.rankDiff) }} 位</div>
                  <div class="stat-lbl">位次差距</div>
                </div>
              </div>
              <div class="card-actions">
                <button
                  class="cmp-btn"
                  :class="{ 'cmp-active': isInCompare(item.schoolId) }"
                  :disabled="!isInCompare(item.schoolId) && !canAddMore"
                  @click="(e) => toggleCompare(e, item)"
                >{{ isInCompare(item.schoolId) ? '✓' : '+' }}</button>
              </div>
            </div>
            <div v-if="result.reach.length === 0" class="empty-list">
              该区间暂无符合条件的院校数据
            </div>
          </div>
        </div>

        <!-- 稳一稳 -->
        <div class="result-col">
          <div class="col-head target-head">
            <span class="col-label">稳一稳</span>
            <span class="col-count">{{ result.target.length }} 所</span>
          </div>
          <div class="col-desc">您的位次优于录取线，余量 0–30%，录取把握较大</div>
          <div class="school-list">
            <div
              v-for="item in result.target"
              :key="item.schoolId"
              class="school-card"
              @click="openDetail(item)"
            >
              <div class="card-main">
                <div class="card-name">
                  {{ item.schoolName }}
                  <span v-if="item.is985" class="badge badge-985">985</span>
                  <span v-if="item.is211" class="badge badge-211">211</span>
                  <span v-if="item.isDoubleFirstClass" class="badge badge-dfc">双一流</span>
                </div>
                <div class="card-loc">{{ item.schoolProvince }} {{ item.schoolCity }}</div>
              </div>
              <div class="card-stats">
                <div class="stat-block">
                  <div class="stat-val">{{ item.minScore }}</div>
                  <div class="stat-lbl">历史最低分</div>
                </div>
                <div class="stat-block">
                  <div class="stat-val">{{ formatRank(item.schoolRank) }}</div>
                  <div class="stat-lbl">历史位次</div>
                </div>
                <div class="stat-block">
                  <div class="stat-val target-diff">余 {{ formatRank(item.rankDiff) }} 位</div>
                  <div class="stat-lbl">位次余量</div>
                </div>
              </div>
              <div class="card-actions">
                <button
                  class="cmp-btn"
                  :class="{ 'cmp-active': isInCompare(item.schoolId) }"
                  :disabled="!isInCompare(item.schoolId) && !canAddMore"
                  @click="(e) => toggleCompare(e, item)"
                >{{ isInCompare(item.schoolId) ? '✓' : '+' }}</button>
              </div>
            </div>
            <div v-if="result.target.length === 0" class="empty-list">
              该区间暂无符合条件的院校数据
            </div>
          </div>
        </div>

        <!-- 保一保 -->
        <div class="result-col">
          <div class="col-head safety-head">
            <span class="col-label">保一保</span>
            <span class="col-count">{{ result.safety.length }} 所</span>
          </div>
          <div class="col-desc">您的位次优于录取线，余量 30%–150%，录取稳妥</div>
          <div class="school-list">
            <div
              v-for="item in result.safety"
              :key="item.schoolId"
              class="school-card"
              @click="openDetail(item)"
            >
              <div class="card-main">
                <div class="card-name">
                  {{ item.schoolName }}
                  <span v-if="item.is985" class="badge badge-985">985</span>
                  <span v-if="item.is211" class="badge badge-211">211</span>
                  <span v-if="item.isDoubleFirstClass" class="badge badge-dfc">双一流</span>
                </div>
                <div class="card-loc">{{ item.schoolProvince }} {{ item.schoolCity }}</div>
              </div>
              <div class="card-stats">
                <div class="stat-block">
                  <div class="stat-val">{{ item.minScore }}</div>
                  <div class="stat-lbl">历史最低分</div>
                </div>
                <div class="stat-block">
                  <div class="stat-val">{{ formatRank(item.schoolRank) }}</div>
                  <div class="stat-lbl">历史位次</div>
                </div>
                <div class="stat-block">
                  <div class="stat-val safety-diff">余 {{ formatRank(item.rankDiff) }} 位</div>
                  <div class="stat-lbl">位次余量</div>
                </div>
              </div>
              <div class="card-actions">
                <button
                  class="cmp-btn"
                  :class="{ 'cmp-active': isInCompare(item.schoolId) }"
                  :disabled="!isInCompare(item.schoolId) && !canAddMore"
                  @click="(e) => toggleCompare(e, item)"
                >{{ isInCompare(item.schoolId) ? '✓' : '+' }}</button>
              </div>
            </div>
            <div v-if="result.safety.length === 0" class="empty-list">
              该区间暂无符合条件的院校数据
            </div>
          </div>
        </div>

      </div>
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

.volunteer-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: $bg-main;
}

/* ── 输入区 ─────────────────────────────────────────────────────────────────── */
.input-section {
  background: $bg-card;
  border-bottom: 1px solid $border-color;
  padding: 16px 24px;
  flex-shrink: 0;
}

.input-card-title {
  font-size: 17px;
  font-weight: 700;
  color: $text-primary;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  gap: 6px;

  .title-icon { font-size: 18px; }
}

.input-card-sub {
  font-size: 13px;
  color: $text-muted;
  margin-bottom: 8px;
}

.algo-note {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
  font-size: 12px;
  color: $text-secondary;
  background: $bg-main;
  border: 1px solid $border-color;
  border-radius: $radius-md;
  padding: 7px 12px;
  margin-bottom: 14px;
  line-height: 1.5;

  b { color: $text-primary; }
}

.algo-note-label {
  font-size: 11px;
  font-weight: 600;
  color: $text-muted;
  background: $border-color;
  padding: 1px 7px;
  border-radius: $radius-sm;
  flex-shrink: 0;
}

.algo-chips {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.chip {
  font-size: 11px;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: 20px;
  white-space: nowrap;
}

.chip-reach  { background: #fff7ed; color: #c2410c; border: 1px solid #fed7aa; }
.chip-target { background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; }
.chip-safety { background: #f0fdf4; color: #15803d; border: 1px solid #bbf7d0; }

.input-row {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  flex-wrap: wrap;
}

.input-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.input-label {
  font-size: 12px;
  color: $text-secondary;
  font-weight: 500;
}

.score-input {
  width: 130px;
  height: 36px;
  padding: 0 12px;
  border: 1px solid $border-color;
  border-radius: $radius-md;
  font-size: 15px;
  font-weight: 600;
  color: $text-primary;
  background: $bg-main;
  outline: none;
  transition: border-color 0.2s;

  &:focus { border-color: $color-primary-light; background: $bg-card; }
  &::placeholder { color: $text-muted; font-weight: 400; font-size: 13px; }
  // hide spinner
  &::-webkit-inner-spin-button, &::-webkit-outer-spin-button { -webkit-appearance: none; }
}

.btn-query {
  height: 36px;
  padding: 0 24px;
  background: $color-primary;
  color: white;
  border: none;
  border-radius: $radius-md;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.15s;
  align-self: flex-end;

  &:disabled { opacity: 0.45; cursor: not-allowed; }
  &:not(:disabled):hover { opacity: 0.88; }
}

.error-msg {
  margin-top: 10px;
  font-size: 13px;
  color: #dc2626;
}

.rank-info {
  margin-top: 10px;
  font-size: 13px;
  color: $text-secondary;

  b { color: $text-primary; }

  .rank-num {
    font-size: 16px;
    color: $color-primary;
  }

  .rank-meta { color: $text-muted; margin-left: 4px; }

  .rank-note {
    margin-left: 8px;
    font-size: 11px;
    color: $text-muted;
    background: $bg-main;
    padding: 1px 6px;
    border-radius: $radius-sm;
  }
}

/* ── 空态 ────────────────────────────────────────────────────────────────────── */
.empty-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 24px;
}

.empty-cols {
  display: flex;
  gap: 16px;
  width: 100%;
  max-width: 900px;
}

.empty-col {
  flex: 1;
  border-radius: $radius-lg;
  padding: 28px 20px;
  text-align: center;
  border: 2px dashed;

  .col-header {
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 6px;
  }
  .col-criteria {
    font-size: 12px;
    font-weight: 600;
    margin-bottom: 10px;
  }
  .col-desc { font-size: 13px; color: $text-muted; line-height: 1.6; }
}

.reach-col  .col-criteria { color: #c2410c; }
.target-col .col-criteria { color: #1d4ed8; }
.safety-col .col-criteria { color: #15803d; }

.reach-col { border-color: #fed7aa; background: #fff7ed; .col-header { color: #ea580c; } }
.target-col { border-color: #bfdbfe; background: #eff6ff; .col-header { color: $color-primary; } }
.safety-col { border-color: #bbf7d0; background: #f0fdf4; .col-header { color: #16a34a; } }

/* ── 结果区 ──────────────────────────────────────────────────────────────────── */
.results-section {
  flex: 1;
  overflow: hidden;
  padding: 12px 24px;
}

.results-cols {
  display: flex;
  gap: 12px;
  height: 100%;
}

.result-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: $bg-card;
  border: 1px solid $border-color;
  border-radius: $radius-lg;
  overflow: hidden;
}

.col-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;

  .col-label {
    font-size: 15px;
    font-weight: 700;
    color: white;
  }

  .col-count {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.8);
    background: rgba(255, 255, 255, 0.2);
    padding: 1px 8px;
    border-radius: 20px;
  }
}

.reach-head  { background: linear-gradient(135deg, #f97316, #ea580c); }
.target-head { background: linear-gradient(135deg, #3b82f6, #2563eb); }
.safety-head { background: linear-gradient(135deg, #22c55e, #16a34a); }

.col-desc {
  font-size: 11px;
  color: $text-muted;
  padding: 6px 14px;
  background: $bg-main;
  border-bottom: 1px solid $border-color;
}

.school-list {
  flex: 1;
  overflow-y: auto;
  padding: 6px 0;
}

/* ── 学校卡片 ─────────────────────────────────────────────────────────────────── */
.school-card {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  cursor: pointer;
  border-bottom: 1px solid $border-color;
  transition: background 0.12s;

  &:last-child { border-bottom: none; }
  &:hover { background: $bg-main; }
}

.card-main {
  flex: 1;
  min-width: 0;
}

.card-name {
  font-size: 13px;
  font-weight: 600;
  color: $text-primary;
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
}

.card-loc {
  font-size: 11px;
  color: $text-muted;
  margin-top: 2px;
}

.card-stats {
  display: flex;
  gap: 10px;
  flex-shrink: 0;
}

.stat-block {
  text-align: center;
  min-width: 52px;
}

.stat-val {
  font-size: 13px;
  font-weight: 600;
  color: $text-primary;
  line-height: 1.3;
}

.stat-lbl {
  font-size: 10px;
  color: $text-muted;
  white-space: nowrap;
}

.reach-diff  { color: #ea580c; }
.target-diff { color: $color-primary; }
.safety-diff { color: #16a34a; }

.card-actions {
  flex-shrink: 0;
}

.cmp-btn {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  border: 1.5px solid $border-color;
  background: $bg-card;
  color: $text-secondary;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;

  &:hover:not(:disabled) { border-color: $color-primary-light; color: $color-primary; }
  &.cmp-active { background: $color-primary-bg; border-color: $color-primary-light; color: $color-primary; }
  &:disabled { opacity: 0.4; cursor: not-allowed; }
}

.badge {
  display: inline-block;
  padding: 1px 5px;
  border-radius: $radius-sm;
  font-size: 10px;
  font-weight: 600;
  line-height: 1.5;

  &.badge-985 { background: #fef2f2; color: $color-985; }
  &.badge-211 { background: #eff6ff; color: $color-211; }
  &.badge-dfc { background: #f5f3ff; color: $color-double-first; }
}

.empty-list {
  text-align: center;
  color: $text-muted;
  font-size: 13px;
  padding: 32px 16px;
}
</style>
