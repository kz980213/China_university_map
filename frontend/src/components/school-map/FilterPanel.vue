<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import type { SchoolFilter } from '@/types/school'
import { useFilterOptions } from '@/composables/useFilterOptions'

const props = defineProps<{
  modelValue: SchoolFilter
}>()

const emit = defineEmits<{
  'update:modelValue': [value: SchoolFilter]
  reset: []
}>()

const levelOptions = ['本科', '专科']
const tagOptions = ['985', '211', '双一流']
const ownershipOptions = ['公办', '民办']
const schoolTypeOptions = ['综合类', '理工类', '师范类', '医药类', '财经类', '政法类', '艺术类', '体育类', '其他']

const collapsed = ref<Record<string, boolean>>({})

const {
  provinceOptions, provincesLoading, loadProvinces,
  subjectOptions, subjectsLoading, loadSubjects,
  yearOptions, yearsLoading, loadYears,
} = useFilterOptions()

onMounted(() => {
  loadProvinces()
  loadYears()
  if (props.modelValue.province && props.modelValue.year) {
    loadSubjects(props.modelValue.province, props.modelValue.year)
  }
})

let lastYear = props.modelValue.year
watch(() => props.modelValue.province, (newProvince) => {
  if (newProvince && lastYear) {
    loadSubjects(newProvince, lastYear)
  }
})
watch(() => props.modelValue.year, (newYear) => {
  lastYear = newYear
  if (props.modelValue.province && newYear) {
    loadSubjects(props.modelValue.province, newYear)
  }
})

function toggleSection(key: string) {
  collapsed.value[key] = !collapsed.value[key]
}

function updateLevels(val: string) {
  const next = props.modelValue.levels[0] === val ? [] : [val]
  emit('update:modelValue', { ...props.modelValue, levels: next })
}
function updateTags(val: string) {
  const current = [...props.modelValue.tags]
  const idx = current.indexOf(val)
  if (idx >= 0) current.splice(idx, 1)
  else current.push(val)
  emit('update:modelValue', { ...props.modelValue, tags: current })
}
function updateOwnerships(val: string) {
  const next = props.modelValue.ownerships[0] === val ? [] : [val]
  emit('update:modelValue', { ...props.modelValue, ownerships: next })
}
function updateSchoolTypes(val: string) {
  const next = props.modelValue.schoolTypes[0] === val ? [] : [val]
  emit('update:modelValue', { ...props.modelValue, schoolTypes: next })
}
function toggleProvince(p: string) {
  const newProvince = props.modelValue.province === p ? undefined : p
  emit('update:modelValue', { ...props.modelValue, province: newProvince })
}
function setYear(y: number) {
  emit('update:modelValue', { ...props.modelValue, year: y })
}
function setSubjectType(st: string) {
  emit('update:modelValue', { ...props.modelValue, subjectType: st === props.modelValue.subjectType ? undefined : st })
}
</script>

<template>
  <aside class="filter-panel">
    <div class="filter-header">
      <h3 class="filter-title">筛选条件</h3>
      <button class="reset-btn" @click="emit('reset')">重置</button>
    </div>

    <!-- 年份 -->
    <div class="filter-section">
      <h4 class="section-title" :class="{ collapsed: collapsed['year'] }" @click="toggleSection('year')">
        <span class="section-arrow">{{ collapsed['year'] ? '▸' : '▾' }}</span>
        年份
      </h4>
      <div v-show="!collapsed['year']" class="section-body">
        <div class="year-list" v-if="!yearsLoading">
          <button
            v-for="y in yearOptions"
            :key="y"
            :class="['province-tag', { active: modelValue.year === y }]"
            @click="setYear(y)"
          >{{ y }}</button>
        </div>
        <span v-else class="loading-text">加载中…</span>
      </div>
    </div>

    <!-- 地区 -->
    <div class="filter-section">
      <h4 class="section-title" :class="{ collapsed: collapsed['province'] }" @click="toggleSection('province')">
        <span class="section-arrow">{{ collapsed['province'] ? '▸' : '▾' }}</span>
        地区筛选
      </h4>
      <div v-show="!collapsed['province']" class="section-body">
        <div class="province-list" v-if="!provincesLoading">
          <button
            v-for="p in provinceOptions"
            :key="p"
            :class="['province-tag', { active: modelValue.province === p }]"
            @click="toggleProvince(p)"
          >{{ p }}</button>
        </div>
        <span v-else class="loading-text">加载中…</span>
      </div>
    </div>

    <!-- 科类 -->
    <div class="filter-section">
      <h4 class="section-title" :class="{ collapsed: collapsed['subject'] }" @click="toggleSection('subject')">
        <span class="section-arrow">{{ collapsed['subject'] ? '▸' : '▾' }}</span>
        科类
        <span v-if="!modelValue.province" class="hint-text">（请先选择地区）</span>
      </h4>
      <div v-show="!collapsed['subject']" class="section-body">
        <div class="province-list" v-if="!subjectsLoading && modelValue.province && modelValue.year">
          <button
            v-for="st in subjectOptions"
            :key="st"
            :class="['province-tag', { active: modelValue.subjectType === st }]"
            @click="setSubjectType(st)"
          >{{ st }}</button>
        </div>
        <span v-else-if="subjectsLoading" class="loading-text">加载中…</span>
        <span v-else class="hint-text">请选择地区和年份</span>
      </div>
    </div>

    <!-- 院校层次（单选） -->
    <div class="filter-section">
      <h4 class="section-title" :class="{ collapsed: collapsed['level'] }" @click="toggleSection('level')">
        <span class="section-arrow">{{ collapsed['level'] ? '▸' : '▾' }}</span>
        院校层次
      </h4>
      <div v-show="!collapsed['level']" class="section-body">
        <div class="option-list">
          <button
            v-for="l in levelOptions"
            :key="l"
            :class="['filter-tag', { active: modelValue.levels[0] === l }]"
            @click="updateLevels(l)"
          >{{ l }}</button>
        </div>
      </div>
    </div>

    <!-- 院校属性（多选） -->
    <div class="filter-section">
      <h4 class="section-title" :class="{ collapsed: collapsed['tag'] }" @click="toggleSection('tag')">
        <span class="section-arrow">{{ collapsed['tag'] ? '▸' : '▾' }}</span>
        院校属性
      </h4>
      <div v-show="!collapsed['tag']" class="section-body">
        <div class="option-list">
          <button
            v-for="t in tagOptions"
            :key="t"
            :class="['filter-tag', { active: modelValue.tags.includes(t) }]"
            @click="updateTags(t)"
          >
            <span :class="`tag-dot tag-${t === '985' ? '985' : t === '211' ? '211' : 'double'}`" />
            {{ t }}
          </button>
        </div>
      </div>
    </div>

    <!-- 办学性质（单选） -->
    <div class="filter-section">
      <h4 class="section-title" :class="{ collapsed: collapsed['ownership'] }" @click="toggleSection('ownership')">
        <span class="section-arrow">{{ collapsed['ownership'] ? '▸' : '▾' }}</span>
        办学性质
      </h4>
      <div v-show="!collapsed['ownership']" class="section-body">
        <div class="option-list">
          <button
            v-for="o in ownershipOptions"
            :key="o"
            :class="['filter-tag', { active: modelValue.ownerships[0] === o }]"
            @click="updateOwnerships(o)"
          >{{ o }}</button>
        </div>
      </div>
    </div>

    <!-- 院校类型（单选） -->
    <div class="filter-section">
      <h4 class="section-title" :class="{ collapsed: collapsed['type'] }" @click="toggleSection('type')">
        <span class="section-arrow">{{ collapsed['type'] ? '▸' : '▾' }}</span>
        院校类型
      </h4>
      <div v-show="!collapsed['type']" class="section-body">
        <div class="option-list">
          <button
            v-for="s in schoolTypeOptions"
            :key="s"
            :class="['filter-tag', { active: modelValue.schoolTypes[0] === s }]"
            @click="updateSchoolTypes(s)"
          >{{ s }}</button>
        </div>
      </div>
    </div>
  </aside>
</template>

<style scoped lang="scss">
@use '@/styles/variables' as *;

.filter-panel {
  width: $filter-panel-width;
  background: $bg-card;
  border-right: 1px solid $border-color;
  overflow-y: auto;
  height: 100%;
  padding-bottom: 24px;
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 20px 16px;
  border-bottom: 1px solid $border-light;
}

.filter-title {
  font-size: 16px;
  font-weight: 600;
  color: $text-primary;
}

.reset-btn {
  font-size: 13px;
  color: $color-primary-light;
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: $radius-sm;

  &:hover {
    background: $color-primary-bg;
  }
}

.filter-section {
  padding: 16px 20px;
  border-bottom: 1px solid $border-light;
}

.option-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.filter-tag {
  padding: 5px 12px;
  font-size: 12px;
  border: 1px solid $border-color;
  border-radius: $radius-md;
  background: $bg-main;
  color: $text-secondary;
  cursor: pointer;
  transition: all 0.15s;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  white-space: nowrap;

  &:hover {
    border-color: $color-primary-light;
    color: $color-primary;
    background: $color-primary-bg;
  }

  &.active {
    background: $color-primary;
    color: #ffffff;
    border-color: $color-primary;

    .tag-dot {
      box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.6);
    }
  }
}

.section-title {
  font-size: 13px;
  font-weight: 600;
  color: $text-secondary;
  margin-bottom: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  cursor: pointer;
  user-select: none;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: color 0.2s;

  &:hover {
    color: $color-primary;
  }

  &.collapsed {
    margin-bottom: 4px;
  }
}

.section-arrow {
  font-size: 12px;
  width: 14px;
  flex-shrink: 0;
  color: $text-muted;
}

.section-body {
  padding-top: 4px;
}

.tag-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 4px;
  vertical-align: middle;

  &.tag-985 {
    background: $color-985;
  }
  &.tag-211 {
    background: $color-211;
  }
  &.tag-double {
    background: $color-double-first;
  }
}

.province-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.province-tag {
  padding: 6px 14px;
  font-size: 13px;
  border: 1px solid $border-color;
  border-radius: $radius-md;
  background: $bg-card;
  color: $text-secondary;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    border-color: $color-primary-light;
    color: $color-primary;
  }

  &.active {
    background: $color-primary;
    color: #ffffff;
    border-color: $color-primary;
  }
}

.year-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.loading-text, .hint-text {
  font-size: 12px;
  color: $text-muted;
}
</style>