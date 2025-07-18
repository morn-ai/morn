import { defineStore } from "pinia";
import { ref } from "vue";
import logout from "../common/useLogout";
export const useApisStore = defineStore("apis", () => {
  const threads = ref<any[]>([]);
  async function getThreads() {
    // 调用API
    const response = await fetch("/api/v1/threads", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${localStorage.getItem("access_token")}`,
      },
    });

    console.log("Response status:", response.status);
    console.log("Response headers:", response.headers);

    if (!response.ok) {
      logout();
    }

    const result = await response.json();
    threads.value = result.threads;
  }

  return {
    threads,
    getThreads,
  };
});
