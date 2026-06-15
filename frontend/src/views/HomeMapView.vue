<script setup lang="ts">
import { ref } from 'vue'
import type { School, SchoolFilter } from '@/types/school'
import type { ChatMessage } from '@/types/ai'
import { useSchoolFilter } from '@/composables/useSchoolFilter'
import AppHeader from '@/components/layout/AppHeader.vue'
import FilterPanel from '@/components/school-map/FilterPanel.vue'
import ChinaSchoolMap from '@/components/school-map/ChinaSchoolMap.vue'
import ResultPanel from '@/components/school-map/ResultPanel.vue'
import SchoolDetailDrawer from '@/components/school-map/SchoolDetailDrawer.vue'
import AiAssistantButton from '@/components/ai-assistant/AiAssistantButton.vue'
import AiAssistantDrawer from '@/components/ai-assistant/AiAssistantDrawer.vue'
import CompareFloatingBar from '@/components/compare/CompareFloatingBar.vue'
import SchoolCompareDrawer from '@/components/compare/SchoolCompareDrawer.vue'

const {
  filter,
  filteredSchools,
  allSchools,
  provinceStatCounts,
  statCounts,
  provinceStats,
  schoolsLoading,
  schoolsError,
  currentPage,
  pageSize,
  totalPages,
  goToPage,
  setPageSize,
  setKeyword,
  setProvince,
  updateFilter,
  resetFilter,
} = useSchoolFilter()

const selectedSchool = ref<School | null>(null)
const detailVisible = ref(false)
const aiVisible = ref(false)
const filterCollapsed = ref(false)

function showSchoolDetail(school: School) {
  selectedSchool.value = school
  detailVisible.value = true
}

function handleProvinceSelect(province: string) {
  setProvince(province)
}

function handleAiApplyFilter(suggestedFilter: ChatMessage['suggestedFilter']) {
  if (!suggestedFilter) return

  const updated: Partial<SchoolFilter> = {
    keyword: suggestedFilter.keyword ?? '',
    tags: suggestedFilter.tags ?? [],
    levels: suggestedFilter.levels ?? [],
    schoolTypes: suggestedFilter.schoolTypes ?? [],
    province: suggestedFilter.province,
  }
  updateFilter(updated)
}
</script>

<template>
  <div class="home-page">
    <AppHeader :keyword="filter.keyword" @update:keyword="setKeyword" />

    <div class="main-content">
      <div class="filter-area" :class="{ collapsed: filterCollapsed }">
        <div class="filter-panel-inner">
          <FilterPanel :model-value="filter" @update:model-value="updateFilter" @reset="resetFilter" />
        </div>
        <button
          class="filter-toggle-btn"
          type="button"
          @click="filterCollapsed = !filterCollapsed"
        >
          {{ filterCollapsed ? '▸' : '◂' }}
        </button>
      </div>

      <div v-if="schoolsError" class="global-error">载入失败: {{ schoolsError }}</div>
      <template v-else>
      <ChinaSchoolMap
        :schools="allSchools"
        :filtered-schools="filteredSchools"
        :selected-province="filter.province"
        :province-stats="provinceStats"
        @select-province="handleProvinceSelect"
      />
      <ResultPanel
        :schools="filteredSchools"
        :total="provinceStatCounts.total"
        :undergraduate-count="provinceStatCounts.undergraduateCount"
        :junior-college-count="provinceStatCounts.juniorCollegeCount"
        :count985="provinceStatCounts.count985"
        :count211="provinceStatCounts.count211"
        :double-first-class-count="provinceStatCounts.doubleFirstClassCount"
        :selected-province="filter.province"
        :loading="schoolsLoading"
        :current-page="currentPage"
        :total-pages="totalPages"
        :page-size="pageSize"
        @update:page="goToPage"
        @update:page-size="setPageSize"
        @select-school="showSchoolDetail"
      />
      </template>
    </div>

    <SchoolDetailDrawer
      :visible="detailVisible"
      :school="selectedSchool"
      @close="detailVisible = false"
    />

    <AiAssistantButton @click="aiVisible = true" />

    <AiAssistantDrawer
      :visible="aiVisible"
      @close="aiVisible = false"
      @select-school="showSchoolDetail"
      @apply-filter="handleAiApplyFilter"
    />

    <CompareFloatingBar />
    <SchoolCompareDrawer />
  </div>
</template>

<style scoped lang="scss">
@use '@/styles/variables' as *;

.home-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.main-content {
  flex: 1;
  display: flex;
  overflow: hidden;
  position: relative;
}

.filter-area {
  display: flex;
  flex-shrink: 0;
  align-items: stretch;

  &.collapsed .filter-panel-inner {
    width: 0;
  }
}

.filter-panel-inner {
  width: $filter-panel-width;
  overflow: hidden;
  transition: width 0.25s ease;
}

.filter-toggle-btn {
  flex-shrink: 0;
  width: 26px;
  height: 100px;
  align-self: center;
  background: $bg-card;
  border: 1px solid $border-color;
  border-left: none;
  border-radius: 0 $radius-md $radius-md 0;
  font-size: 14px;
  color: $text-secondary;
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;

  &:hover {
    background: $color-primary-bg;
    color: $color-primary;
  }
}
</style>