<script setup lang="ts">
import { ref } from 'vue'
import type { School } from '@/types/school'
import type { ChatMessage } from '@/types/ai'
import { useAiSchoolAssistant } from '@/composables/useAiSchoolAssistant'
import QuickQuestionList from './QuickQuestionList.vue'
import ChatMessageList from './ChatMessageList.vue'
import ChatInputBox from './ChatInputBox.vue'

defineProps<{
  visible: boolean
}>()

const emit = defineEmits<{
  close: []
  selectSchool: [school: School]
  applyFilter: [filter: ChatMessage['suggestedFilter']]
}>()

const { messages, isThinking, addUserMessage, processQuery, clearMessages } = useAiSchoolAssistant()

async function handleQuestion(text: string) {
  addUserMessage(text)
  await processQuery(text)
}

function handleApplyFilter(suggestedFilter: ChatMessage['suggestedFilter'] | undefined) {
  if (suggestedFilter) {
    emit('applyFilter', suggestedFilter)
  }
}

function handleClose() {
  clearMessages()
  emit('close')
}
</script>

<template>
  <el-drawer
    :model-value="visible"
    direction="rtl"
    size="460px"
    @close="handleClose"
    :with-header="true"
  >
    <template #header>
      <div class="drawer-header">
        <h3 class="drawer-title">AI 高校查询助手</h3>
        <p class="drawer-subtitle">基于当前高校数据，帮你快速筛选学校</p>
      </div>
    </template>

    <div class="ai-drawer-content">
      <QuickQuestionList @select="handleQuestion" />

      <ChatMessageList
        :messages="messages"
        @click-school="emit('selectSchool', $event)"
        @apply-filter="handleApplyFilter"
      />

      <div v-if="isThinking" class="thinking">AI 正在思考...</div>

      <ChatInputBox @send="handleQuestion" />
    </div>
  </el-drawer>
</template>

<style scoped lang="scss">
@use '@/styles/variables' as *;

.drawer-header {
  width: 100%;
}

.drawer-title {
  font-size: 18px;
  font-weight: 700;
  color: $text-primary;
  margin-bottom: 4px;
}

.drawer-subtitle {
  font-size: 13px;
  color: $text-muted;
}

.ai-drawer-content {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.thinking {
  padding: 8px 16px;
  font-size: 13px;
  color: $text-muted;
  font-style: italic;
  background: $bg-main;
}
</style>