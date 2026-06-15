<script setup lang="ts">
</script>

<template>
  <div class="compare-tab">
    <div class="placeholder-card">
      <div class="placeholder-icon">📊</div>
      <h3>学校对比功能</h3>
      <p>后续将支持将当前学校加入对比，从城市、学校层次、专业设置、录取分数线、位次趋势等维度进行横向比较。</p>
      <el-button type="primary" disabled>加入对比</el-button>
      <p class="hint">（该功能将在后续阶段实现）</p>
    </div>
  </div>
</template>

<style scoped lang="scss">
@use '@/styles/variables' as *;

.compare-tab {
  padding: 4px 0;
}

.placeholder-card {
  background: $bg-main;
  border-radius: $radius-lg;
  padding: 48px 24px;
  text-align: center;
  border: 2px dashed $border-color;
}

.placeholder-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

h3 {
  font-size: 16px;
  font-weight: 600;
  color: $text-primary;
  margin-bottom: 12px;
}

p {
  font-size: 14px;
  color: $text-secondary;
  line-height: 1.8;
  max-width: 400px;
  margin: 0 auto 20px;
}

.hint {
  font-size: 12px;
  color: $text-muted;
  margin-top: 8px;
}
</style>