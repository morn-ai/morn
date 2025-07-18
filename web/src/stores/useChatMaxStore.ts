import { defineStore } from "pinia";
import { ref } from "vue";
export const useChatMaxStore = defineStore("chatMax", () => {
  const history = ref({ thread_id: Date.now(), messages: [] });

  function reset() {
    history.value = { thread_id: Date.now(), messages: [] };
  }

  return {
    history,
    reset,
  };
});
