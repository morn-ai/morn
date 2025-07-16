import { createRouter, createWebHashHistory } from "vue-router";
import LoginForm from "../components/LoginForm.vue";
import Dashboard from "../components/Dashboard.vue";
import Playground from "../components/factory/Playground.vue";

const routes = [
  {
    path: "/",
    name: "Login",
    component: LoginForm,
  },
  {
    path: "/factory",
    name: "Factory",
    component: Playground,
    meta: { requiresAuth: true }, // 标记需要登录的路由
  },
  {
    path: "/dashboard",
    name: "Dashboard",
    component: Dashboard,
    meta: { requiresAuth: true }, // 标记需要登录的路由
  },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

function isAuthenticated() {
  // 示例：检查本地存储的 token
  const token = localStorage.getItem("access_token");
  return !!token; // 返回 Boolean 值
}

// 全局前置守卫
router.beforeEach((to, from, next) => {
  if (to.matched.some((record) => record.meta.requiresAuth)) {
    // 检查目标路由是否需要登录
    if (!isAuthenticated()) {
      // 未登录则跳转到登录页
      next({ name: "Login" });
    } else {
      next(); // 已登录，放行
    }
  } else {
    next(); // 不需要登录的路由直接放行
  }
});

export default router;
