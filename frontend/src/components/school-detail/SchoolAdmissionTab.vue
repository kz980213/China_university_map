<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import type { School } from '@/types/school'
import type { AdmissionScore, SubjectType } from '@/types/admission'
import { useSchoolData } from '@/composables/useSchoolData'
import AdmissionTrendChart from './AdmissionTrendChart.vue'
import AdmissionRankChart from './AdmissionRankChart.vue'

const props = defineProps<{
  school: School
}>()

const filterProvince = ref('')
const filterSubject = ref<SubjectType | ''>('')
const filterYearFrom = ref<number | undefined>(undefined)
const filterYearTo = ref<number | undefined>(undefined)

const {
  admissionScores,
  scoresLoading,
  scoresError,
  loadAdmissionScores,
} = useSchoolData()

// 初次加载时缓存省份/科类/年份选项，筛选后不随结果收缩
const allProvinceOptions = ref<string[]>([])
const allSubjectOptions = ref<string[]>([])
const allYearOptions = ref<number[]>([])

// 切换学校时跳过 filter watch 的一次触发，避免重复请求
let skipFilterWatch = false

watch(() => props.school.id, async (id) => {
  if (!id) return
  skipFilterWatch = true
  filterProvince.value = ''
  filterSubject.value = ''
  filterYearFrom.value = undefined
  filterYearTo.value = undefined
  await loadAdmissionScores(id, {})
  allProvinceOptions.value = [...new Set(admissionScores.value.map(s => s.studentProvince))].sort()
  allSubjectOptions.value = [...new Set(admissionScores.value.map(s => s.subjectType))]
  allYearOptions.value = [...new Set(admissionScores.value.map(s => s.year))].sort((a, b) => b - a)
}, { immediate: true })

// 当筛选条件变化时重新请求
watch([filterProvince, filterSubject, filterYearFrom, filterYearTo], () => {
  if (skipFilterWatch) { skipFilterWatch = false; return }
  const params: Record<string, unknown> = {}
  if (filterProvince.value) params.student_province = filterProvince.value
  if (filterSubject.value) params.subject_type = filterSubject.value
  if (filterYearFrom.value) params.year_from = filterYearFrom.value
  if (filterYearTo.value) params.year_to = filterYearTo.value
  loadAdmissionScores(props.school.id, params)
})

const filteredScores = computed(() =>
  [...admissionScores.value].sort((a, b) => a.year - b.year || a.studentProvince.localeCompare(b.studentProvince))
)

// 只有在选择了生源省份时才有意义地渲染趋势图
const canShowChart = computed(() => !!filterProvince.value)

// ── rank 格式化 ──
function formatRank(score: AdmissionScore): string {
  switch (score.estimatedRankReason) {
    case 'no_data': return '暂无'
    case 'out_of_range': return score.estimatedRank != null ? `约 ${score.estimatedRank}` : '暂无'
    case 'floored': return score.estimatedRank != null ? `约 ${score.estimatedRank}` : '暂无'
    case 'ok': return score.estimatedRank != null ? String(score.estimatedRank) : '暂无'
    default: return score.minRank != null ? String(score.minRank) : '暂无'
  }
}

function rankClass(score: AdmissionScore): string {
  if (score.estimatedRankReason == null || score.estimatedRankReason === 'no_data') return 'rank-none'
  if (score.estimatedRankReason === 'floored') return 'rank-estimated'
  if (score.estimatedRankReason === 'out_of_range') return 'rank-estimated'
  return 'rank-exact'
}
</script>

<template>
  <div class="admission-tab">
    <!-- 初始加载中（尚未获取到任何数据） -->
    <div v-if="scoresLoading && allProvinceOptions.length === 0" class="loading-state">加载中…</div>

    <!-- Error -->
    <div v-else-if="scoresError && allProvinceOptions.length === 0" class="error-state">加载失败：{{ scoresError }}</div>

    <!-- 该学校确实没有数据（初始加载完成后仍为空） -->
    <div v-else-if="!scoresLoading && allProvinceOptions.length === 0" class="empty-state">
      <p>暂无录取分数线数据</p>
    </div>

    <!-- 有数据：始终显示筛选器；筛选无结果时在内容区提示 -->
    <div v-else class="content">
      <div class="filter-row">
        <el-select v-model="filterProvince" placeholder="生源省份" size="small" clearable style="width:120px">
          <el-option v-for="p in allProvinceOptions" :key="p" :label="p" :value="p" />
        </el-select>
        <el-select v-model="filterSubject" placeholder="科类" size="small" clearable style="width:110px">
          <el-option v-for="s in allSubjectOptions" :key="s" :label="s" :value="s" />
        </el-select>
        <el-select v-model="filterYearFrom" placeholder="起始年" size="small" clearable style="width:90px">
          <el-option v-for="y in allYearOptions" :key="'f'+y" :label="String(y)" :value="y" />
        </el-select>
        <el-select v-model="filterYearTo" placeholder="截止年" size="small" clearable style="width:90px">
          <el-option v-for="y in allYearOptions" :key="'t'+y" :label="String(y)" :value="y" />
        </el-select>
      </div>

      <!-- 筛选加载中 -->
      <div v-if="scoresLoading" class="loading-state" style="padding: 24px 0">加载中…</div>

      <!-- 筛选无结果 -->
      <div v-else-if="filteredScores.length === 0" class="empty-state">
        <p>当前筛选条件无匹配数据</p>
      </div>

      <template v-else>
        <div class="charts-row">
          <div class="chart-block">
            <h4>最低分趋势</h4>
            <div v-if="!canShowChart" class="chart-placeholder">请先选择「生源省份」以查看趋势图</div>
            <AdmissionTrendChart v-else :scores="filteredScores" />
          </div>
          <div class="chart-block">
            <h4>位次趋势（估算值，仅供参考）</h4>
            <div class="rank-hint">⚠️ 位次基于一分一段换算，跨年/跨省不可直接比较</div>
            <div v-if="!canShowChart" class="chart-placeholder">请先选择「生源省份」以查看趋势图</div>
            <AdmissionRankChart v-else :scores="filteredScores" />
          </div>
        </div>

        <h4 class="table-title">分数线明细</h4>
        <el-table :data="filteredScores" size="small" stripe max-height="400">
          <el-table-column prop="year" label="年份" width="60" />
          <el-table-column prop="studentProvince" label="生源省份" width="85" />
          <el-table-column prop="subjectType" label="科类" width="75" />
          <el-table-column prop="batch" label="批次" width="70">
            <template #default="{ row }">{{ row.batch || '-' }}</template>
          </el-table-column>
          <el-table-column prop="minScore" label="最低分" width="75" sortable />
          <el-table-column label="位次(估算)" width="100" sortable sort-prop="estimatedRank">
            <template #default="{ row }">
              <span :class="rankClass(row)">{{ formatRank(row) }}</span>
            </template>
          </el-table-column>
        </el-table>
      </template>
    </div>
  </div>
</template>

<style scoped lang="scss">
@use '@/styles/variables' as *;

.admission-tab { padding: 4px 0; }
.loading-state, .error-state, .empty-state {
  text-align: center; padding: 40px 0; color: $text-muted; font-size: 14px;
}
.error-state { color: #dc2626; }
.content { overflow-x: hidden; }
.filter-row { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 14px; }
.charts-row { display: flex; flex-direction: column; gap: 16px; margin-bottom: 16px; }
.chart-block {
  background: $bg-main; border-radius: $radius-md; padding: 12px;
  h4 { font-size: 13px; font-weight: 600; color: $text-primary; margin-bottom: 4px; }
}
.rank-hint { font-size: 11px; color: $text-muted; margin-bottom: 8px; font-style: italic; }
.chart-placeholder {
  height: 220px; display: flex; align-items: center; justify-content: center;
  font-size: 13px; color: $text-muted; background: $bg-card;
  border-radius: $radius-md; border: 1px dashed $border-color;
}
.table-title { font-size: 14px; font-weight: 600; color: $text-primary; margin-bottom: 8px; }

.rank-none { color: $text-muted; }
.rank-estimated { color: #d97706; &::before { content: '≈ '; } }
.rank-exact { color: $text-primary; }
</style>