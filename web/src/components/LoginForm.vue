<template>
  <div class="login-container">
    <div class="left">
      <img src="../assets/morn_500.svg" alt="morn logo" />
    </div>
    <div class="right">
      <n-card class="login-card" title="User Login" :bordered="false" size="huge">
        <n-form
          ref="formRef"
          :model="formValue"
          :rules="rules"
          label-placement="left"
          label-width="auto"
          require-mark-placement="right-hanging"
          size="large"
        >
          <n-form-item label="Username" path="username">
            <n-input
              v-model:value="formValue.username"
              placeholder="Please enter username"
              clearable
            >
              <template #prefix>
                <n-icon><PersonOutline /></n-icon>
              </template>
            </n-input>
          </n-form-item>

          <n-form-item label="Password" path="password">
            <n-input
              v-model:value="formValue.password"
              type="password"
              placeholder="Please enter password"
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
                Login
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
import { useRouter } from "vue-router";
import { PersonOutline, LockClosedOutline } from "@vicons/ionicons5";

const message = useMessage();
const router = useRouter();

// Form reference
const formRef = ref();

// Loading state
const loading = ref(false);

// Form data
const formValue = reactive({
  username: "",
  password: "",
  rememberMe: false,
});

// Form validation rules
const rules = {
  username: [
    {
      required: true,
      message: "Please enter username",
      trigger: "blur",
    },
    {
      min: 3,
      max: 20,
      message: "Username length should be between 3 and 20 characters",
      trigger: "blur",
    },
  ],
  password: [
    {
      required: true,
      message: "Please enter password",
      trigger: "blur",
    },
    {
      min: 6,
      max: 20,
      message: "Password length should be between 6 and 20 characters",
      trigger: "blur",
    },
  ],
};

// Submit form
const handleSubmit = (e: MouseEvent) => {
  e.preventDefault();

  formRef.value?.validate(async (errors: any) => {
    if (!errors) {
      loading.value = true;
      const url = '/api/v1/login'

      try {
        const response = await fetch(url, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            username: formValue.username,
            password: formValue.password,
          }),
        });

        if (response.ok) {
          const result = await response.json();
          console.log('Login response:', result);
          if (result.access_token) {
            localStorage.setItem("access_token", result.access_token);
            console.log('Token saved to localStorage:', result.access_token);
            console.log('Token length:', result.access_token.length);
            message.success("Login successful!");
            // Navigate to dashboard
            router.push('/dashboard');
          } else {
            console.error('No access_token in response');
            message.error("Login response error");
          }
        } else {
          const errorData = await response.json();
          console.error('Login error:', errorData);

          if (response.status === 429) {
            // Rate limited or account locked
            message.error(errorData.detail || "Too many login attempts, please try again later");
          } else if (response.status === 401) {
            // Invalid credentials
            message.error(errorData.detail || "Invalid username or password");
          } else {
            message.error(errorData.detail || "Login failed, please try again");
          }
        }
      } catch (error) {
        console.error('Network error:', error);
        message.error("Network error, please check your connection");
      } finally {
        loading.value = false;
      }
    } else {
      message.error("Please check your input");
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
