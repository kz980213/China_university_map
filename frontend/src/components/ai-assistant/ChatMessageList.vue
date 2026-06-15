<script setup lang="ts">
import type { ChatMessage } from '@/types/ai'
import type { School } from '@/types/school'
import AiSchoolResultCard from './AiSchoolResultCard.vue'

defineProps<{
  messages: ChatMessage[]
}>()

const emit = defineEmits<{
  clickSchool: [school: School]
  applyFilter: [suggestedFilter: ChatMessage['suggestedFilter']]
}>()
</script>

<template>
  <div class="chat-messages">
    <div
      v-for="msg in messages"
      :key="msg.id"
      :class="['message-item', msg.role === 'user' ? 'message-user' : 'message-assistant']"
    >
      <div class="message-bubble" v-html="msg.content.replace(/\n/g, '<br>')" />

      <!-- 相关学校卡片 -->
      <div v-if="msg.relatedSchools && msg.relatedSchools.length > 0" class="message-schools">
        <AiSchoolResultCard
          v-for="school in msg.relatedSchools"
          :key="school.id"
          :school="school"
          @click="emit('clickSchool', school)"
        />
      </div>

      <!-- 应用到筛选条件按钮 -->
      <div v-if="msg.suggestedFilter" class="message-apply">
        <el-button size="small" type="primary" plain @click="emit('applyFilter', msg.suggestedFilter)">
          应用到筛选条件
        </el-button>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
@use '@/styles/variables' as *;

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message-item {
  display: flex;
  flex-direction: column;
}

.message-bubble {
  max-width: 100%;
  padding: 10px 14px;
  border-radius: $radius-md;
  font-size: 14px;
  line-height: 1.7;
  word-break: break-word;
}

.message-user {
  align-items: flex-end;

  .message-bubble {
    background: $color-primary;
    color: #ffffff;
    border-bottom-right-radius: 4px;
  }
}

.message-assistant {
  align-items: flex-start;

  .message-bubble {
    background: $bg-main;
    color: $text-primary;
    border-bottom-left-radius: 4px;
  }
}

.message-schools {
  margin-top: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.message-apply {
  margin-top: 8px;
}
</style>