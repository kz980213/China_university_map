<script setup lang="ts">
import { ref } from 'vue'

const emit = defineEmits<{
  send: [text: string]
}>()

const inputText = ref('')

function handleSend() {
  const text = inputText.value.trim()
  if (!text) return
  emit('send', text)
  inputText.value = ''
}
</script>

<template>
  <div class="chat-input">
    <input
      v-model="inputText"
      class="input-field"
      placeholder="输入问题，例如：江苏有哪些985？"
      @keyup.enter="handleSend"
    />
    <button class="send-btn" :disabled="!inputText.trim()" @click="handleSend">
      发送
    </button>
  </div>
</template>

<style scoped lang="scss">
@use '@/styles/variables' as *;

.chat-input {
  display: flex;
  gap: 8px;
  padding: 16px;
  border-top: 1px solid $border-light;
}

.input-field {
  flex: 1;
  height: 40px;
  padding: 0 14px;
  border: 1px solid $border-color;
  border-radius: $radius-md;
  font-size: 14px;
  color: $text-primary;
  background: $bg-main;
  outline: none;
  transition: border-color 0.2s;

  &::placeholder {
    color: $text-muted;
    font-size: 13px;
  }

  &:focus {
    border-color: $color-primary-light;
    background: $bg-card;
  }
}

.send-btn {
  padding: 0 20px;
  height: 40px;
  background: $color-primary;
  color: #ffffff;
  border: none;
  border-radius: $radius-md;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
  white-space: nowrap;

  &:hover:not(:disabled) {
    background: $color-primary-light;
  }

  &:disabled {
    background: $text-muted;
    cursor: not-allowed;
  }
}
</style>