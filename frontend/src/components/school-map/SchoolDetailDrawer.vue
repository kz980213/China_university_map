<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import type { School } from '@/types/school'
import { useSchoolData } from '@/composables/useSchoolData'
import SchoolOverviewTab from '@/components/school-detail/SchoolOverviewTab.vue'
import SchoolMajorsTab from '@/components/school-detail/SchoolMajorsTab.vue'
import SchoolAdmissionTab from '@/components/school-detail/SchoolAdmissionTab.vue'
import SchoolLocationTab from '@/components/school-detail/SchoolLocationTab.vue'
import SchoolCompareTab from '@/components/school-detail/SchoolCompareTab.vue'

const props = defineProps<{
  visible: boolean
  school: School | null
}>()

const emit = defineEmits<{
  close: []
}>()

const activeTab = ref('overview')

const { schoolDetail, detailLoading, loadSchoolDetail } = useSchoolData()

// 每次打开 / 切换学校时，拉取完整详情（含 address/longitude/website/description 等）
watch(
  [() => props.visible, () => props.school?.id],
  ([visible, id]) => {
    if (visible && id) {
      activeTab.value = 'overview'
      loadSchoolDetail(id)
    }
  },
  { immediate: true }
)

// 完整数据优先；未加载完毕时回退到列表数据（避免闪烁）
const school = computed<School | null>(() =>
  schoolDetail.value?.id === props.school?.id ? schoolDetail.value : props.school
)
</script>

<template>
  <el-drawer
    :model-value="visible"
    direction="rtl"
    size="720px"
    @close="emit('close')"
    :with-header="!!school"
  >
    <template v-if="props.school" #header>
      <div class="drawer-header">
        <h3 class="drawer-title">{{ school?.name }}</h3>
        <div class="drawer-tags">
          <span v-if="school?.is985" class="tag tag-985">985</span>
          <span v-if="school?.is211" class="tag tag-211">211</span>
          <span v-if="school?.isDoubleFirstClass" class="tag tag-double">双一流</span>
          <span class="tag tag-level">{{ school?.level }}</span>
          <span class="tag tag-ownership">{{ school?.ownership }}</span>
        </div>
      </div>
    </template>

    <div v-if="school">
      <el-tabs v-model="activeTab" class="detail-tabs">
        <el-tab-pane label="学校概览" name="overview">
          <SchoolOverviewTab :school="school" />
        </el-tab-pane>
        <el-tab-pane label="专业设置" name="majors">
          <SchoolMajorsTab :school="school" />
        </el-tab-pane>
        <el-tab-pane label="录取分数" name="admission">
          <SchoolAdmissionTab :school="school" />
        </el-tab-pane>
        <el-tab-pane label="地理位置" name="location">
          <SchoolLocationTab :school="school" />
        </el-tab-pane>
        <el-tab-pane label="学校对比" name="compare">
          <SchoolCompareTab :school="school" />
        </el-tab-pane>
      </el-tabs>
    </div>
  </el-drawer>
</template>

<style scoped lang="scss">
@use '@/styles/variables' as *;

.drawer-header {
  width: 100%;
}

.drawer-title {
  font-size: 20px;
  font-weight: 700;
  color: $text-primary;
  margin-bottom: 8px;
}

.drawer-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.tag {
  display: inline-block;
  padding: 2px 10px;
  border-radius: $radius-sm;
  font-size: 12px;
  font-weight: 500;

  &.tag-985 { background: #fef2f2; color: $color-985; }
  &.tag-211 { background: #eff6ff; color: $color-211; }
  &.tag-double { background: #f5f3ff; color: $color-double-first; }
  &.tag-level { background: $color-primary-bg; color: $color-primary; }
  &.tag-ownership { background: $bg-main; color: $text-secondary; }
}

.detail-tabs {
  :deep(.el-tabs__header) {
    margin-bottom: 16px;
  }
}
</style>