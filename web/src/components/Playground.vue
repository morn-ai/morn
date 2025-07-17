<template>
  <div class="playground-container">
    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 左侧配置面板 -->
      <div class="config-panel">
        <div class="config-section">
          <div class="section-header">
            <span class="section-title">System Message</span>
            <n-icon class="sparkle-icon">
              <SparklesOutline />
            </n-icon>
          </div>
          <n-input
            v-model:value="systemMessage"
            type="textarea"
            placeholder="Describe desired model behavior (tone, tool usage, response style)"
            :autosize="{ minRows: 8, maxRows: 16 }"
            class="system-message-input"
          />
        </div>

        <div class="config-section">
          <div class="section-header">
            <span class="section-title">Settings</span>
          </div>
          <n-space vertical>
            <n-switch v-model:value="useStream" size="small">
              <template #checked>流式响应</template>
              <template #unchecked>普通响应</template>
            </n-switch>
          </n-space>
        </div>
      </div>

      <!-- 右侧对话区域 -->
      <ChatPanel
        url="/api/v1/chat/completions"
        :systemMessage="systemMessage"
        :useStream="useStream"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { SparklesOutline } from "@vicons/ionicons5";
import ChatPanel from "./ChatPanel.vue";

// 响应式数据
const systemMessage = ref("");
const useStream = ref(true);
</script>

<style scoped lang="less">
.playground-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: white;
}

.main-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.config-panel {
  width: 300px;
  background: #f8f9fa;
  border-right: 1px solid #e1e5e9;
  padding: 24px;
  overflow-y: auto;

  .config-section {
    .section-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 12px;

      .section-title {
        font-size: 14px;
        font-weight: 600;
        color: #1a1a1a;
      }

      .sparkle-icon {
        color: #666;
        cursor: pointer;

        &:hover {
          color: #333;
        }
      }
    }

    .system-message-input {
      :deep(.n-input__textarea-el) {
        font-size: 14px;
        line-height: 1.5;
      }
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .main-content {
    flex-direction: column;
  }

  .config-panel {
    width: 100%;
    height: 200px;
    border-right: none;
    border-bottom: 1px solid #e1e5e9;
  }
}
</style>
