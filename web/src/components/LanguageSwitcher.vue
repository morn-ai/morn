<template>
  <n-dropdown
    :options="languageOptions"
    @select="handleLanguageChange"
    trigger="click"
  >
    <n-button quaternary size="small">
      <template #icon>
        <n-icon>
          <LanguageOutline />
        </n-icon>
      </template>
      {{ currentLanguageLabel }}
    </n-button>
  </n-dropdown>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { LanguageOutline } from '@vicons/ionicons5'

const { locale, t } = useI18n()

const currentLanguageLabel = computed(() => {
  return locale.value === 'zh' ? t('common.chinese') : t('common.english')
})

const languageOptions = computed(() => [
  {
    label: t('common.chinese'),
    key: 'zh',
    icon: '🇨🇳'
  },
  {
    label: t('common.english'),
    key: 'en',
    icon: '🇺🇸'
  }
])

const handleLanguageChange = (key: string) => {
  locale.value = key
  localStorage.setItem('locale', key)
}
</script>

<style scoped>
.n-button {
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>
