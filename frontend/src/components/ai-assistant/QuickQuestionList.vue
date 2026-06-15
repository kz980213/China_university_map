<script setup lang="ts">
defineEmits<{
  select: [question: string]
}>()

const quickQuestions = [
  '江苏有哪些985？',
  '北京有哪些双一流？',
  '广东有哪些本科院校？',
  '有哪些学校有计算机专业？',
  '上海有哪些理工类大学？',
  '浙江大学有哪些热门专业？',
]
</script>

<template>
  <div class="quick-questions">
    <p class="quick-title">快捷提问</p>
    <div class="quick-list">
      <button
        v-for="q in quickQuestions"
        :key="q"
        class="quick-item"
        @click="$emit('select', q)"
      >
        {{ q }}
      </button>
    </div>
  </div>
</template>

<style scoped lang="scss">
@use '@/styles/variables' as *;

.quick-questions {
  padding: 16px;
  border-bottom: 1px solid $border-light;
}

.quick-title {
  font-size: 12px;
  font-weight: 600;
  color: $text-muted;
  margin-bottom: 10px;
  text-transform: uppercase;
}

.quick-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.quick-item {
  padding: 6px 14px;
  font-size: 13px;
  background: $bg-main;
  border: 1px solid $border-color;
  border-radius: 16px;
  color: $text-secondary;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    border-color: $color-primary-light;
    color: $color-primary;
    background: $color-primary-bg;
  }
}
</style>