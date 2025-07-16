<template>
  <div class="login-container">
    <div class="left">
      <img src="../assets/morn_500.svg" alt="morn logo" />
    </div>
    <div class="right">
      <n-card class="login-card" title="用户登录" :bordered="false" size="huge">
        <n-form
          ref="formRef"
          :model="formValue"
          :rules="rules"
          label-placement="left"
          label-width="auto"
          require-mark-placement="right-hanging"
          size="large"
        >
          <n-form-item label="用户名" path="username">
            <n-input
              v-model:value="formValue.username"
              placeholder="请输入用户名"
              clearable
            >
              <template #prefix>
                <n-icon><PersonOutline /></n-icon>
              </template>
            </n-input>
          </n-form-item>

          <n-form-item label="密码" path="password">
            <n-input
              v-model:value="formValue.password"
              type="password"
              placeholder="请输入密码"
              clearable
              show-password-on="click"
            >
              <template #prefix>
                <n-icon><LockClosedOutline /></n-icon>
              </template>
            </n-input>
          </n-form-item>

          <n-form-item class="form-btn">
            <n-space vertical :size="24">

              <n-button
                type="primary"
                size="large"
                block
                :loading="loading"
                @click="handleSubmit"
              >
                登录
              </n-button>
            </n-space>
          </n-form-item>
        </n-form>
      </n-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from "vue";
import { useMessage } from "naive-ui";
import { PersonOutline, LockClosedOutline } from "@vicons/ionicons5";

const message = useMessage();

// 表单引用
const formRef = ref();

// 加载状态
const loading = ref(false);

// 表单数据
const formValue = reactive({
  username: "",
  password: "",
  rememberMe: false,
});

// 表单验证规则
const rules = {
  username: [
    {
      required: true,
      message: "请输入用户名",
      trigger: "blur",
    },
    {
      min: 3,
      max: 20,
      message: "用户名长度在 3 到 20 个字符",
      trigger: "blur",
    },
  ],
  password: [
    {
      required: true,
      message: "请输入密码",
      trigger: "blur",
    },
    {
      min: 6,
      max: 20,
      message: "密码长度在 6 到 20 个字符",
      trigger: "blur",
    },
  ],
};

// 提交表单
const handleSubmit = (e: MouseEvent) => {
  e.preventDefault();

  formRef.value?.validate(async (errors: any) => {
    if (!errors) {
      loading.value = true;
      const url = import.meta.env.MODE === "development" ? '/auth/login' : '/login'
      const result = await (
        await fetch(url, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            username: formValue.username,
            password: formValue.password,
          }),
        })
      ).json();
      if (result.access_token) {
        localStorage.setItem("access_token", result.access_token);
      }
      // 模拟登录请求
      loading.value = false;
      message.success("登录成功！");
    } else {
      message.error("请检查输入信息");
    }
  });
};
</script>

<style scoped lang="less">
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;

  .left {
    flex: 1;
    display: flex;
    justify-content: center;
    align-items: center;
  }
  .right {
    width: 600px;
  }
}

.login-card {
  width: 100%;
  max-width: 400px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border-radius: 16px;

  .form-btn {
    :deep(.n-form-item-blank) {
      justify-content: end;
    }
  }
}

.login-card :deep(.n-card-header) {
  text-align: center;
  font-size: 24px;
  font-weight: 600;
  color: #333;
  padding-bottom: 8px;
}

.login-links {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
}
:deep(.n-form-item-label) {
  font-weight: 500;
}

:deep(.n-input) {
  border-radius: 8px;
}

:deep(.n-button) {
  border-radius: 8px;
  font-weight: 500;
}
</style>
