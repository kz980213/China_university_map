<script setup lang="ts">
import type { School } from '@/types/school'

defineProps<{ school: School }>()

const platforms = [
  {
    name: '阳光高考',
    desc: '教育部官方平台，数据权威',
    url: (name: string) => `https://gaokao.chsi.com.cn/sch/search--ss-1-school_name-${encodeURIComponent(name)}.dhtml`,
    color: '#e85d26',
  },
  {
    name: '掌上高考',
    desc: '专业列表、选科要求、学费',
    url: (name: string) => `https://www.zsgkw.com/search/?keyword=${encodeURIComponent(name)}`,
    color: '#1677ff',
  },
  {
    name: '百度搜索',
    desc: '快速查找官网招生简章',
    url: (name: string) => `https://www.baidu.com/s?wd=${encodeURIComponent(name + ' 专业设置 招生简章')}`,
    color: '#3064d3',
  },
]
</script>

<template>
  <div class="majors-tab">
    <div class="notice">
      <span class="notice-icon">📋</span>
      <span>专业数据需实时更新，建议直接前往以下官方平台查询 <b>{{ school.name }}</b> 的最新专业信息</span>
    </div>

    <div class="platform-list">
      <a
        v-for="p in platforms"
        :key="p.name"
        :href="p.url(school.name)"
        target="_blank"
        rel="noopener"
        class="platform-card"
      >
        <div class="platform-left">
          <span class="platform-name" :style="{ color: p.color }">{{ p.name }}</span>
          <span class="platform-desc">{{ p.desc }}</span>
        </div>
        <span class="platform-arrow">→</span>
      </a>
    </div>

    <p class="hint">点击后在新标签页打开，已自动带入学校名称搜索</p>
  </div>
</template>

<style scoped lang="scss">
@use '@/styles/variables' as *;

.majors-tab { padding: 8px 0; }

.notice {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: $radius-md;
  padding: 12px 16px;
  font-size: 14px;
  color: $text-secondary;
  line-height: 1.6;
  margin-bottom: 20px;

  .notice-icon { font-size: 18px; flex-shrink: 0; }
  b { color: $text-primary; }
}

.platform-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 16px;
}

.platform-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 18px;
  background: $bg-card;
  border: 1px solid $border-color;
  border-radius: $radius-md;
  text-decoration: none;
  transition: all 0.15s;

  &:hover {
    border-color: $color-primary-light;
    box-shadow: $shadow-md;
    transform: translateX(2px);
  }
}

.platform-left {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.platform-name {
  font-size: 15px;
  font-weight: 600;
}

.platform-desc {
  font-size: 12px;
  color: $text-muted;
}

.platform-arrow {
  font-size: 18px;
  color: $text-muted;
}

.hint {
  font-size: 12px;
  color: $text-muted;
  text-align: center;
}
</style>
