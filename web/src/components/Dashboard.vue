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

    <!-- 页签导航 -->
    <div class="tab-navigation">
      <n-tabs
        v-model:value="activeTab"
        type="line"
        size="large"
        class="main-tabs"
      >
        <n-tab-pane name="playground" tab="PlayGround">
          <div class="tab-content">
            <Playground />
          </div>
        </n-tab-pane>
      </n-tabs>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  NotificationsOutline,
  SettingsOutline,
  LogOutOutline
} from '@vicons/ionicons5'
import Playground from './Playground.vue'

const router = useRouter()
const activeTab = ref('playground')

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

  .right-section {
    .n-space {
      gap: 8px;
    }
  }
}

.tab-navigation {
  flex: 1;
  background: white;
  margin: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;

  .main-tabs {
    height: 100%;

    :deep(.n-tabs-nav) {
      padding: 0 24px;
      border-bottom: 1px solid #e1e5e9;
    }

    :deep(.n-tabs-tab-pad) {
      padding: 0;
    }

    :deep(.n-tab-pane) {
      height: calc(100vh - 140px);
      overflow-y: auto;
    }
  }
}

.tab-content {
  padding: 24px;
  height: 100%;
}


// 响应式设计
@media (max-width: 768px) {
  .top-bar {
    padding: 0 16px;

    .logo .logo-text {
      display: none;
    }
  }

  .tab-navigation {
    margin: 8px;
  }

  .tab-content {
    padding: 16px;
  }
}
</style>
