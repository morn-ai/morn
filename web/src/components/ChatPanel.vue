<template>
  <!-- 右侧对话区域 -->
  <div class="chat-panel">
    <div class="chat-container">
      <div v-if="messages.length === 0" class="empty-state">
        <div class="empty-icon">
          <n-icon size="64">
            <ChatbubbleOutline />
          </n-icon>
        </div>
        <p class="empty-text">Your conversation will appear here</p>
      </div>

      <div v-else class="messages">
        <div
          v-for="(message, index) in messages"
          :key="index"
          :class="['message', message.role]"
        >
          <div class="message-content">
            <div class="message-header">
              <span class="role-label">{{
                message.role === "user" ? "User" : "Assistant"
              }}</span>
            </div>
            <div class="message-text">{{ message.content }}</div>
          </div>
        </div>
      </div>
    </div>

    <div class="chat-input-container">
      <div class="input-wrapper">
        <n-input
          v-model:value="inputMessage"
          placeholder="Chat with your prompt..."
          class="chat-input"
          size="large"
          @keyup.enter="sendMessage"
        >
          <template #suffix>
            <n-space>
              <!-- <n-button quaternary size="small" circle>
                <template #icon>
                  <n-icon>
                    <MicOutline />
                  </n-icon>
                </template>
              </n-button> -->
              <n-button circle size="small" @click="handleClear">
                <template #icon>
                  <n-icon>
                    <TrashOutline />
                  </n-icon>
                </template>
              </n-button>
              <n-button
                type="primary"
                size="small"
                circle
                :disabled="!inputMessage.trim()"
                @click="sendMessage"
              >
                <template #icon>
                  <n-icon>
                    <ArrowUpOutline />
                  </n-icon>
                </template>
              </n-button>
            </n-space>
          </template>
        </n-input>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import {
  ChatbubbleOutline,
  TrashOutline,
  ArrowUpOutline,
} from "@vicons/ionicons5";
import { useRouter } from "vue-router";
import logout from "../common/useLogout";

// 响应式数据
const {
  url,
  systemMessage = "",
  useStream = true,
} = defineProps<{
  url: string;
  systemMessage?: String;
  useStream?: boolean;
}>();
const inputMessage = ref("");
const messages = ref<Array<{ role: "user" | "assistant"; content: string }>>(
  []
);

const threadId = ref(Date.now());

// 发送消息
const sendMessage = async () => {
  if (!inputMessage.value.trim()) return;

  const userMessage = inputMessage.value.trim();

  // 添加用户消息
  messages.value.push({
    role: "user",
    content: userMessage,
  });

  // 清空输入框
  inputMessage.value = "";

  // 准备消息数组
  const messageArray = [];

  // 如果有系统消息，添加到开头
  if (systemMessage.trim()) {
    messageArray.push({
      role: "system",
      content: systemMessage.trim(),
    });
  }

  // 添加历史消息
  messageArray.push(
    ...messages.value.map((msg) => ({
      role: msg.role,
      content: msg.content,
    }))
  );

  // 添加一个空的assistant消息用于流式更新
  const assistantMessageIndex = messages.value.length;
  messages.value.push({
    role: "assistant",
    content: "",
  });

  try {
    const token = localStorage.getItem("access_token");
    console.log("Token from localStorage:", token);
    console.log("Token type:", typeof token);
    console.log("Token length:", token ? token.length : 0);

    if (!token) {
      logout();
      throw new Error("No access token found in localStorage");
    }

    console.log(
      "Request payload:",
      JSON.stringify(
        {
          messages: messageArray,
          stream: useStream,
        },
        null,
        2
      )
    );

    // 调用API
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        messages: messageArray,
        thread_id: String(threadId.value),
        stream: useStream,
      }),
    });

    console.log("Response status:", response.status);
    console.log("Response headers:", response.headers);

    if (!response.ok) {
      const errorText = await response.text();
      console.error("Response error:", errorText);
      logout();
      throw new Error(
        `HTTP error! status: ${response.status}, message: ${errorText}`
      );
    }

    if (useStream) {
      // 处理流式响应
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error("No response body reader available");
      }

      while (true) {
        const { done, value } = await reader.read();

        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const data = line.slice(6); // 移除 'data: ' 前缀

            if (data.trim() === "[DONE]") {
              console.log("Stream completed");
              return;
            }

            try {
              const jsonData = JSON.parse(data);
              console.log("Stream chunk:", jsonData);

              if (
                jsonData.choices &&
                jsonData.choices[0] &&
                jsonData.choices[0].delta &&
                jsonData.choices[0].delta.content
              ) {
                // 追加内容到当前assistant消息
                messages.value[assistantMessageIndex].content +=
                  jsonData.choices[0].delta.content;
              }
            } catch (e) {
              console.warn("Failed to parse stream chunk:", e);
            }
          }
        }
      }
    } else {
      // 处理非流式响应
      const data = await response.json();
      console.log("Response data:", data);

      // 更新assistant消息内容
      if (data.choices && data.choices[0] && data.choices[0].message) {
        messages.value[assistantMessageIndex].content =
          data.choices[0].message.content;
      } else {
        throw new Error("Invalid response format");
      }
    }
  } catch (error) {
    console.error("API调用失败:", error);
    // 如果调用失败，移除空的assistant消息
    if (
      messages.value[assistantMessageIndex] &&
      messages.value[assistantMessageIndex].content === ""
    ) {
      messages.value.splice(assistantMessageIndex, 1);
    }
    messages.value.push({
      role: "assistant",
      content: `抱歉，AI服务暂时不可用，请稍后重试。错误信息: ${error.message}`,
    });
  }
};

const handleClear = () => {
  threadId.value = Date.now();
  messages.value.length = 0;
};
</script>

<style scoped lang="less">
.chat-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #f8f9fa;

  .chat-container {
    flex: 1;
    padding: 24px;
    overflow-y: auto;

    .empty-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100%;
      color: #666;

      .empty-icon {
        margin-bottom: 16px;
        opacity: 0.5;
      }

      .empty-text {
        font-size: 16px;
        color: #999;
      }
    }

    .messages {
      .message {
        margin-bottom: 24px;

        &.user {
          .message-content {
            background: #f0f7ff;
            border-left: 4px solid #1890ff;
          }
        }

        &.assistant {
          .message-content {
            background: #f6f6f6;
            border-left: 4px solid #52c41a;
          }
        }

        .message-content {
          padding: 16px;
          border-radius: 8px;

          .message-header {
            margin-bottom: 8px;

            .role-label {
              font-size: 12px;
              font-weight: 600;
              color: #666;
              text-transform: uppercase;
            }
          }

          .message-text {
            font-size: 14px;
            line-height: 1.6;
            color: #1a1a1a;
          }
        }
      }
    }
  }

  .chat-input-container {
    padding: 24px;
    border-top: 1px solid #e1e5e9;

    .input-wrapper {
      .chat-input {
        :deep(.n-input__input-el) {
          font-size: 14px;
        }
      }
    }
  }
}
</style>
