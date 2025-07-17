<template>
  <div class="chat-max-container">
    <ChatPanel url="/api/v1/chat" />
  </div>
</template>

<script setup lang="ts">
import ChatPanel from "./ChatPanel.vue";
</script>

<style scoped lang="less">
.chat-max-container {
  height: 100%;
  display: flex;
}
</style>
