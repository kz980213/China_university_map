<script setup lang="ts">
import type { School } from '@/types/school'

defineProps<{
  school: School
}>()
</script>

<template>
  <div class="overview-tab">
    <div v-if="school.description" class="description-section">
      <h4 class="section-label">学校简介</h4>
      <p class="description-text">{{ school.description }}</p>
    </div>

    <div class="info-cards">
      <div class="info-card">
        <span class="info-label">学校代码</span>
        <span class="info-value">{{ school.schoolCode }}</span>
      </div>
      <div class="info-card">
        <span class="info-label">所在省市</span>
        <span class="info-value">{{ school.province }} {{ school.city }}</span>
      </div>
      <div class="info-card">
        <span class="info-label">办学层次</span>
        <span class="info-value">{{ school.level }}</span>
      </div>
      <div class="info-card">
        <span class="info-label">学校类型</span>
        <span class="info-value">{{ school.schoolType }}</span>
      </div>
      <div class="info-card">
        <span class="info-label">办学性质</span>
        <span class="info-value">{{ school.ownership }}</span>
      </div>
      <div class="info-card">
        <span class="info-label">院校标签</span>
        <span class="info-value">
          <template v-if="school.is985">985 </template>
          <template v-if="school.is211">211 </template>
          <template v-if="school.isDoubleFirstClass">双一流</template>
          <template v-if="!school.is985 && !school.is211 && !school.isDoubleFirstClass">暂无</template>
        </span>
      </div>
    </div>

    <div class="link-section">
      <div class="link-item">
        <span class="link-label">官网</span>
        <a v-if="school.website" :href="school.website" target="_blank" class="link">{{ school.website }}</a>
        <span v-else class="link-na">暂无</span>
      </div>
    </div>

    <div class="majors-section">
      <h4 class="section-label">热门专业</h4>
      <div class="major-tags">
        <span v-for="major in (school.popularMajors ?? [])" :key="major" class="major-tag">{{ major }}</span>
        <span v-if="!school.popularMajors?.length" class="link-na">暂无</span>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
@use '@/styles/variables' as *;

.overview-tab {
  padding: 4px 0;
}

.description-section {
  margin-bottom: 16px;
}

.section-label {
  font-size: 14px;
  font-weight: 600;
  color: $text-primary;
  margin-bottom: 8px;
}

.description-text {
  font-size: 14px;
  line-height: 1.8;
  color: $text-secondary;
}

.info-cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 16px;
}

.info-card {
  background: $bg-main;
  border-radius: $radius-md;
  padding: 10px 14px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.info-label {
  font-size: 12px;
  color: $text-muted;
}

.info-value {
  font-size: 14px;
  color: $text-primary;
  font-weight: 500;
}

.link-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}

.link-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.link-label {
  color: $text-muted;
  min-width: 60px;
}

.link {
  color: $color-primary-light;
  word-break: break-all;
  &:hover { color: $color-primary; }
}

.link-na {
  color: $text-muted;
}

.majors-section {
  margin-bottom: 8px;
}

.major-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.major-tag {
  display: inline-block;
  padding: 4px 12px;
  background: $color-primary-bg;
  color: $color-primary;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
}
</style>