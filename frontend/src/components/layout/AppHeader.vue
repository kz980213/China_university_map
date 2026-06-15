<script setup lang="ts">
import { useRoute } from 'vue-router'

defineProps<{
  keyword: string
}>()

defineEmits<{
  'update:keyword': [value: string]
}>()

const route = useRoute()
</script>

<template>
  <header class="app-header">
    <div class="header-left">
      <div class="logo">
        <svg class="logo-icon" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect width="32" height="32" rx="8" fill="#1e40af"/>
          <path d="M16 6L6 12v2l4 2.5V28h12V16.5l4-2.5v-2L16 6z" fill="white"/>
          <circle cx="16" cy="14" r="3" fill="#1e40af"/>
        </svg>
        <span class="logo-text">全国高校地图</span>
      </div>
      <nav class="header-nav">
        <RouterLink to="/" class="nav-item" :class="{ active: route.path === '/' }">地图查询</RouterLink>
        <RouterLink to="/schools" class="nav-item" :class="{ active: route.path === '/schools' }">学校库</RouterLink>
        <RouterLink to="/scores" class="nav-item" :class="{ active: route.path === '/scores' }">分数线</RouterLink>
        <RouterLink to="/volunteer" class="nav-item" :class="{ active: route.path === '/volunteer' }">志愿辅助</RouterLink>
      </nav>
    </div>
    <div class="header-right">
      <div class="search-box">
        <svg class="search-icon" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M9 17A8 8 0 109 1a8 8 0 000 16zM19 19l-4.35-4.35" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
        <input
          class="search-input"
          type="text"
          placeholder="搜索学校 / 城市 / 专业"
          :value="keyword"
          @input="$emit('update:keyword', ($event.target as HTMLInputElement).value)"
        />
      </div>
    </div>
  </header>
</template>

<style scoped lang="scss">
@use '@/styles/variables' as *;

.app-header {
  height: $header-height;
  background: $bg-card;
  border-bottom: 1px solid $border-color;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  position: relative;
  z-index: 100;
  box-shadow: $shadow-sm;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 32px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-icon {
  width: 32px;
  height: 32px;
}

.logo-text {
  font-size: 18px;
  font-weight: 700;
  color: $color-primary;
  letter-spacing: 0.5px;
}

.header-nav {
  display: flex;
  gap: 8px;
}

.nav-item {
  padding: 6px 16px;
  border-radius: $radius-md;
  font-size: 14px;
  color: $text-secondary;
  cursor: pointer;
  transition: all 0.2s;
  text-decoration: none;

  &:hover {
    background: $bg-main;
    color: $text-primary;
  }

  &.active {
    background: $color-primary-bg;
    color: $color-primary;
    font-weight: 500;
  }
}

.header-right {
  display: flex;
  align-items: center;
}

.search-box {
  position: relative;
  width: 320px;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 18px;
  height: 18px;
  color: $text-muted;
}

.search-input {
  width: 100%;
  height: 40px;
  padding: 0 16px 0 40px;
  border: 1px solid $border-color;
  border-radius: $radius-md;
  font-size: 14px;
  color: $text-primary;
  background: $bg-main;
  outline: none;
  transition: border-color 0.2s;

  &::placeholder {
    color: $text-muted;
  }

  &:focus {
    border-color: $color-primary-light;
    background: $bg-card;
  }
}
</style>