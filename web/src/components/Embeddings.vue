<template>
  <div class="embeddings-container">
    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 左侧配置面板 -->
      <div class="config-panel">
        <div class="config-section">
          <div class="section-header">
            <span class="section-title">{{ t('embeddings.modelSettings') }}</span>
            <n-icon class="sparkle-icon">
              <SparklesOutline />
            </n-icon>
          </div>
          <n-select
            v-model:value="selectedModel"
            :options="modelOptions"
            :placeholder="t('embeddings.selectModel')"
            class="model-select"
          />
        </div>

        <div class="config-section">
          <div class="section-header">
            <span class="section-title">{{ t('embeddings.inputText') }}</span>
          </div>
          <n-input
            v-model:value="inputText"
            type="textarea"
            :placeholder="t('embeddings.inputPlaceholder')"
            :autosize="{ minRows: 8, maxRows: 16 }"
            class="input-textarea"
          />
        </div>

        <div class="config-section">
          <div class="section-header">
            <span class="section-title">{{ t('embeddings.actions') }}</span>
          </div>
          <n-space vertical>
            <n-button
              type="primary"
              :loading="isLoading"
              @click="generateEmbeddings"
              :disabled="!inputText.trim()"
            >
              {{ t('embeddings.generateEmbedding') }}
            </n-button>
            <n-button @click="clearResults" :disabled="!hasResults">
              {{ t('embeddings.clearResults') }}
            </n-button>
          </n-space>
        </div>
      </div>

      <!-- 右侧结果区域 -->
      <div class="results-panel">
        <div class="results-header">
          <span class="section-title">{{ t('embeddings.results') }}</span>
          <n-tag v-if="hasResults" type="success" size="small">
            {{ resultCount }} embedding{{ resultCount > 1 ? 's' : '' }} generated
          </n-tag>
        </div>

        <div v-if="isLoading" class="loading-container">
          <n-spin size="large">
            <template #description>
              {{ t('embeddings.generating') }}
            </template>
          </n-spin>
        </div>

        <div v-else-if="error" class="error-container">
          <n-alert type="error" :title="error" />
        </div>

        <div v-else-if="hasResults" class="results-content">
          <n-collapse>
            <n-collapse-item
              v-for="(embedding, index) in embeddings"
              :key="index"
              :title="`Embedding ${index + 1}`"
              :name="index"
            >
              <template #header>
                <div class="embedding-header">
                  <span>Embedding {{ index + 1 }}</span>
                  <n-tag size="small" type="info">
                    {{ embedding.embedding.length }} dimensions
                  </n-tag>
                </div>
              </template>

              <div class="embedding-details">
                <div class="detail-item">
                  <strong>Input:</strong>
                  <div class="input-preview">{{ getInputText(index) }}</div>
                </div>
                <div class="detail-item">
                  <strong>Vector (first 10 dimensions):</strong>
                  <div class="vector-preview">
                    [{{ embedding.embedding.slice(0, 10).map((v: number) => v.toFixed(4)).join(', ') }}{{ embedding.embedding.length > 10 ? '...' : '' }}]
                  </div>
                </div>
                <div class="detail-item">
                  <strong>Full Vector:</strong>
                  <n-button size="tiny" @click="copyVector(embedding.embedding)">
                    Copy Vector
                  </n-button>
                </div>
              </div>
            </n-collapse-item>
          </n-collapse>

          <div class="usage-info">
            <n-divider />
            <div class="usage-details">
              <div class="usage-item">
                <strong>Model:</strong> {{ selectedModel }}
              </div>
              <div class="usage-item">
                <strong>Prompt Tokens:</strong> {{ usage?.prompt_tokens || 0 }}
              </div>
              <div class="usage-item">
                <strong>Total Tokens:</strong> {{ usage?.total_tokens || 0 }}
              </div>
            </div>
          </div>
        </div>

        <div v-else class="empty-state">
          <n-empty :description="t('embeddings.noResults')">
            <template #icon>
              <n-icon size="64" color="#ccc">
                <CubeOutline />
              </n-icon>
            </template>
          </n-empty>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { useI18n } from "vue-i18n";
import { SparklesOutline, CubeOutline } from "@vicons/ionicons5";
import { useMessage } from "naive-ui";

const message = useMessage();
const { t } = useI18n();

// 响应式数据
const selectedModel = ref("BAAI/bge-large-zh-v1.5");
const inputText = ref("");
const isLoading = ref(false);
const error = ref("");
const embeddings = ref<any[]>([]);
const usage = ref<any>(null);

// 模型选项
const modelOptions = [
  { label: "BAAI/bge-large-zh-v1.5", value: "BAAI/bge-large-zh-v1.5" },
  { label: "BAAI/bge-large-en-v1.5", value: "BAAI/bge-large-en-v1.5" },
  { label: "netease-youdao/bce-embedding-base_v1", value: "netease-youdao/bce-embedding-base_v1" },
  { label: "BAAI/bge-m3", value: "BAAI/bge-m3" },
  { label: "Pro/BAAI/bge-m3", value: "Pro/BAAI/bge-m3" },
  { label: "Qwen/Qwen3-Embedding-8B", value: "Qwen/Qwen3-Embedding-8B" },
  { label: "Qwen/Qwen3-Embedding-4B", value: "Qwen/Qwen3-Embedding-4B" },
  { label: "Qwen/Qwen3-Embedding-0.6B", value: "Qwen/Qwen3-Embedding-0.6B" },
];

// 计算属性
const hasResults = computed(() => embeddings.value.length > 0);
const resultCount = computed(() => embeddings.value.length);

// 方法
const generateEmbeddings = async () => {
  if (!inputText.value.trim()) {
    message.error("Please enter some text");
    return;
  }

  isLoading.value = true;
  error.value = "";

  try {
    // 处理输入文本 - 支持单行或多行
    const inputs = inputText.value
      .split('\n')
      .map(line => line.trim())
      .filter(line => line.length > 0);

    const response = await fetch("/api/v1/embeddings", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${localStorage.getItem("token")}`,
      },
      body: JSON.stringify({
        model: selectedModel.value,
        input: inputs.length === 1 ? inputs[0] : inputs,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `HTTP ${response.status}`);
    }

    const data = await response.json();
    embeddings.value = data.data;
    usage.value = data.usage;
    message.success("Embeddings generated successfully!");
  } catch (err: any) {
    error.value = err.message || "Failed to generate embeddings";
    message.error(error.value);
  } finally {
    isLoading.value = false;
  }
};

const clearResults = () => {
  embeddings.value = [];
  usage.value = null;
  error.value = "";
  message.info("Results cleared");
};

const getInputText = (index: number) => {
  const inputs = inputText.value
    .split('\n')
    .map(line => line.trim())
    .filter(line => line.length > 0);
  return inputs[index] || "";
};

const copyVector = async (vector: number[]) => {
  try {
    await navigator.clipboard.writeText(JSON.stringify(vector));
    message.success("Vector copied to clipboard");
  } catch (err) {
    message.error("Failed to copy vector");
  }
};
</script>

<style scoped lang="less">
.embeddings-container {
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
    margin-bottom: 24px;

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

    .model-select {
      width: 100%;
    }

    .input-textarea {
      :deep(.n-input__textarea-el) {
        font-size: 14px;
        line-height: 1.5;
      }
    }
  }
}

.results-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 24px;
  overflow: hidden;

  .results-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;

    .section-title {
      font-size: 16px;
      font-weight: 600;
      color: #1a1a1a;
    }
  }

  .loading-container {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .error-container {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .results-content {
    flex: 1;
    overflow-y: auto;

    .embedding-header {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .embedding-details {
      .detail-item {
        margin-bottom: 12px;

        strong {
          display: block;
          margin-bottom: 4px;
          color: #666;
        }

        .input-preview {
          background: #f8f9fa;
          padding: 8px;
          border-radius: 4px;
          font-family: monospace;
          word-break: break-word;
        }

        .vector-preview {
          background: #f8f9fa;
          padding: 8px;
          border-radius: 4px;
          font-family: monospace;
          font-size: 12px;
          overflow-x: auto;
        }
      }
    }

    .usage-info {
      margin-top: 16px;

      .usage-details {
        display: flex;
        gap: 24px;
        flex-wrap: wrap;

        .usage-item {
          strong {
            color: #666;
          }
        }
      }
    }
  }

  .empty-state {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
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
