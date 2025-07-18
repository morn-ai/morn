<template>
  <div class="chat-max-container">
    <ChatPanel
      url="/api/v1/chat"
      :thread_id="history.thread_id"
      :history-messages="history.messages"
    />
  </div>
</template>

<script setup lang="ts">
import { toRefs } from "vue";
import { useChatMaxStore } from "../stores/useChatMaxStore";
import ChatPanel from "./ChatPanel.vue";

const chatMaxStore = useChatMaxStore();

const { history } = toRefs(chatMaxStore);
</script>

<style scoped lang="less">
.chat-max-container {
  height: 100%;
  display: flex;
}
</style>
