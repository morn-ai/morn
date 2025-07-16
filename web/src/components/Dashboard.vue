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
          <n-breadcrumb-item v-for="(item, index) in breadcrumbItems" :key="index">
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
          <n-button quaternary size="small" @click="logout">
            <template #icon>
              <n-icon>
                <LogOutOutline />
              </n-icon>
            </template>
            退出登录
          </n-button>
        </n-space>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 侧边栏 -->
      <div class="sidebar" :class="{ collapsed }">
        <div class="sidebar-header" :class="{ collapsed }">
          <n-button quaternary size="small" @click="toggleSidebar" class="collapse-btn">
            <template #icon>
              <n-icon>
                <MenuOutline />
              </n-icon>
            </template>
          </n-button>
        </div>
        <n-menu
          v-model:value="activeKey"
          :options="menuOptions"
          :collapsed="collapsed"
          :collapsed-width="64"
          :collapsed-icon-size="22"
          :indent="18"
          class="sidebar-menu"
        />
      </div>

      <!-- 内容区域 -->
      <div class="content-area">
        <div class="content-wrapper">
          <Playground v-if="activeKey === 'playground-chat'" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, h } from 'vue'
import { useRouter } from 'vue-router'
import { NIcon } from 'naive-ui'
import {
  NotificationsOutline,
  SettingsOutline,
  LogOutOutline,
  PlayCircleOutline,
  ChatbubbleOutline,
  HomeOutline,
  MenuOutline
} from '@vicons/ionicons5'
import Playground from './Playground.vue'

const router = useRouter()
const activeKey = ref('playground-chat')
const collapsed = ref(false)

// 菜单配置
const menuOptions = [
  {
    label: 'PlayGround',
    key: 'playground',
    icon: renderIcon(PlayCircleOutline),
    children: [
      {
        label: 'Chat',
        key: 'playground-chat',
        icon: renderIcon(ChatbubbleOutline)
      }
    ]
  }
]

// 面包屑导航
const breadcrumbItems = computed(() => {
  const items = ['PlayGround']
  if (activeKey.value === 'playground-chat') {
    items.push('Chat')
  }
  return items
})

// 渲染图标的辅助函数
function renderIcon(icon: any) {
  return () => h(NIcon, null, { default: () => h(icon) })
}

// 切换侧边栏
const toggleSidebar = () => {
  collapsed.value = !collapsed.value
}

// 登出功能
const logout = () => {
  localStorage.removeItem('access_token')
  router.push('/')
}
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
    background: white;
    margin: 16px;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    overflow: hidden;
    transition: margin-left 0.3s ease;

    .content-wrapper {
      flex: 1;
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
