<template>
  <div class="dashboard-container">
    <!-- 顶部导航栏 -->
    <div class="top-bar">
      <div class="left-section">
        <div class="logo">
          <img src="../assets/morn_500.svg" alt="morn logo" />
          <span class="logo-text">Morn</span>
        </div>
      </div>
      <div class="center-section">
        <n-breadcrumb>
          <n-breadcrumb-item
            v-for="(item, index) in breadcrumbItems"
            :key="index"
          >
            {{ item }}
          </n-breadcrumb-item>
        </n-breadcrumb>
      </div>
      <div class="right-section">
        <n-space>
          <n-button quaternary size="small">
            <template #icon>
              <n-icon>
                <NotificationsOutline />
              </n-icon>
            </template>
          </n-button>
          <n-button quaternary size="small">
            <template #icon>
              <n-icon>
                <SettingsOutline />
              </n-icon>
            </template>
          </n-button>
          <LanguageSwitcher />
          <n-button quaternary size="small" @click="logout">
            <template #icon>
              <n-icon>
                <LogOutOutline />
              </n-icon>
            </template>
            {{ t("common.logout") }}
          </n-button>
        </n-space>
      </div>
    </div>

    <n-layout has-sider>
      <n-layout-sider
        bordered
        collapse-mode="width"
        :collapsed-width="64"
        :width="240"
        :collapsed="collapsed"
        show-trigger
        @collapse="collapsed = true"
        @expand="collapsed = false"
      >
        <div class="left-side">
          <div class="top-menu-container">
            <n-menu
              v-model:value="activeKey"
              :options="topMenuOptions"
              :collapsed="collapsed"
              :collapsed-width="64"
              :default-expanded-keys="defaultExpandedKeys"
              :indent="18"
              class="sidebar-menu"
            />
          </div>
          <div class="history-container">
            <div
              v-for="(q, index) in questions"
              :class="['question', { active: currqIndex === index }]"
              @click="showChatMax(q, index)"
            >
              <n-ellipsis>
                {{ q.content }}
              </n-ellipsis>
            </div>
          </div>
          <div class="bottom-menu-container">
            <n-menu
              v-model:value="activeKey"
              :options="bottomMenuOptions"
              :collapsed="collapsed"
              :collapsed-width="64"
              :default-expanded-keys="defaultExpandedKeys"
              :indent="18"
              class="sidebar-menu"
            />
          </div>
        </div>
      </n-layout-sider>
      <n-layout>
        <!-- 主要内容区域 -->
        <!-- 内容区域 -->
        <div class="content-area">
          <div class="content-wrapper">
            <KeepAlive>
              <component :is="rightComponent" />
            </KeepAlive>
          </div>
        </div>
      </n-layout>
    </n-layout>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, h, onMounted, toRefs, watch } from "vue";
import { NIcon } from "naive-ui";
import { useI18n } from "vue-i18n";
import {
  NotificationsOutline,
  SettingsOutline,
  LogOutOutline,
  PlayCircleOutline,
  ChatbubbleOutline,
  ChatbubbleEllipsesOutline,
  CubeOutline,
} from "@vicons/ionicons5";
import Playground from "./Playground.vue";
import ChatMax from "./ChatMax.vue";
import Embeddings from "./Embeddings.vue";
import LanguageSwitcher from "./LanguageSwitcher.vue";
import logout from "../common/useLogout";
import { useApisStore } from "../stores/useApisStore";
import { useChatMaxStore } from "../stores/useChatMaxStore";
import ChatHistory from "./ChatHistory.vue";

const apisStore = useApisStore();
const chatMaxStore = useChatMaxStore();

const { threads } = toRefs(apisStore);
const { history } = toRefs(chatMaxStore);

const { t } = useI18n();
const activeKey = ref("chat");
const collapsed = ref(false);
const defaultExpandedKeys = ref(["playground"]);
const historyTitle = ref("");

const currqIndex = ref(-1);

const rightComponent = computed(() => {
  return {
    chat: ChatMax,
    "playground-chat": Playground,
    "playground-embeddings": Embeddings,
    history: ChatHistory,
  }[activeKey.value];
});

// 菜单配置
const topMenuOptions = [
  {
    label: t("common.chat"),
    key: "chat",
    icon: renderIcon(ChatbubbleEllipsesOutline),
  },
];
const bottomMenuOptions = [
  {
    label: t("common.playground"),
    key: "playground",
    icon: renderIcon(PlayCircleOutline),
    children: [
      {
        label: t("common.chat"),
        key: "playground-chat",
        icon: renderIcon(ChatbubbleOutline),
      },
      {
        label: t("common.embeddings"),
        key: "playground-embeddings",
        icon: renderIcon(CubeOutline),
      },
    ],
  },
];

// 面包屑导航
const breadcrumbItems = computed(() => {
  return {
    "playground-chat": [t("common.playground"), t("common.chat")],
    "playground-embeddings": [t("common.playground"), t("common.embeddings")],
    chat: [t("common.chat")],
    history: [historyTitle.value],
  }[activeKey.value];
});

const questions = computed(() => {
  const questions: any[] = [];
  const set = new Set();
  threads.value.forEach((thread) => {
    const q: any = { thread_id: thread[0].configurable.thread_id };
    thread.forEach((item) => {
      const channel_values = item?.channel_values;
      if (channel_values?.__start__) {
        if (!set.has(q.thread_id)) {
          q.content = channel_values?.__start__.messages[0].content;
          set.add(q.thread_id);
          questions.push(q);
        }
      }
    });
  });

  return questions;
});

// 渲染图标的辅助函数
function renderIcon(icon: any) {
  return () => h(NIcon, null, { default: () => h(icon) });
}

async function showChatMax(q: any, index: number) {
  currqIndex.value = index;
  historyTitle.value = q.content;
  await apisStore.getThreads();
  outerLoop: for (let k = 0; k < threads.value.length; k++) {
    const thread = threads.value[k];
    const thread_id = thread[0].configurable.thread_id;

    innerLoop: for (let i = 0; i < thread.length; i++) {
      if (q.thread_id === thread_id) {
        const channel_values = thread[i]?.channel_values;
        if (channel_values) {
          history.value = {
            thread_id: q.thread_id,
            messages: (channel_values?.messages ?? []).map((msg) => {
              return {
                role: msg.type === "human" ? "user" : "assistant",
                content: msg.content,
              };
            }),
          };
          break outerLoop;
        }
      }
    }
  }
  activeKey.value = "history";
}

onMounted(async () => {
  await apisStore.getThreads();
  console.log(threads.value);
});
</script>

<style scoped lang="less">
.dashboard-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f8f9fa;
}

.top-bar {
  height: 60px;
  background: white;
  border-bottom: 1px solid #e1e5e9;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  z-index: 1000;

  .left-section {
    .logo {
      display: flex;
      align-items: center;
      gap: 12px;

      img {
        height: 32px;
        width: auto;
      }

      .logo-text {
        font-size: 20px;
        font-weight: 600;
        color: #1a1a1a;
      }
    }
  }

  .center-section {
    flex: 1;
    display: flex;
    justify-content: center;
    margin: 0 24px;
  }

  .right-section {
    .n-space {
      gap: 8px;
    }
  }
}

.left-side {
  padding: 8px 0;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  .top-menu-container {
    height: 48px;
  }
  .history-container {
    flex: 1;
    overflow-x: hidden;
    overflow-y: auto;
    // padding: 0 12px;
    margin: 12px;
    // background: #f8f9fa;
    border-radius: 4px;
    .question {
      height: 36px;
      line-height: 36px;
      cursor: pointer;
      padding-left: 12px;
      border-radius: 40px;
      &.active {
        background-color: #edeff2;
      }
      &:not(.active):hover {
        background-color: #f8f9fa;
      }
    }
  }
  .bottom-menu-container {
    height: 144px;
  }
}

.main-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.sidebar {
  width: 240px;
  background: white;
  border-right: 1px solid #e1e5e9;
  overflow-y: auto;
  transition: width 0.3s ease;

  &.collapsed {
    width: 64px;
  }

  .sidebar-header {
    padding: 12px;
    border-bottom: 1px solid #e1e5e9;
    display: flex;
    justify-content: flex-end;

    .collapse-btn {
      transition: transform 0.3s ease;
    }

    &.collapsed .collapse-btn {
      transform: rotate(180deg);
    }
  }

  .sidebar-menu {
    height: calc(100% - 60px);

    :deep(.n-menu-item) {
      height: 48px;
      line-height: 48px;
    }

    :deep(.n-submenu) {
      .n-submenu-title {
        height: 48px;
        line-height: 48px;
      }
    }
  }
}

.content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: margin-left 0.3s ease;

  .content-wrapper {
    flex: 1;
    background: white;
    border-radius: 8px;
    overflow: hidden;
  }
}

// 响应式设计
@media (max-width: 768px) {
  .top-bar {
    padding: 0 16px;

    .logo .logo-text {
      display: none;
    }
  }

  .sidebar {
    width: 200px;
  }

  .content-area {
    margin: 8px;
  }
}
</style>
