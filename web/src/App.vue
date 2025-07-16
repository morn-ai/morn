<template>
  <n-config-provider :theme="theme">
    <n-message-provider>
      <n-loading-bar-provider>
        <n-dialog-provider>
          <n-notification-provider>
            <LoginForm />
          </n-notification-provider>
        </n-dialog-provider>
      </n-loading-bar-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup lang="ts">
import LoginForm from './components/LoginForm.vue'

// 使用亮色主题（你也可以选择 darkTheme 来使用暗色主题）
const theme = null
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}
</style>
