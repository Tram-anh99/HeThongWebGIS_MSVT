<template>
  <div class="language-switcher relative">
    <!-- Language Icon Buttons with Tooltip -->
    <div class="flex items-center space-x-2">
      <button
        v-for="lang in languages"
        :key="lang.code"
        @click="changeLocale(lang.code)"
        :class="[
          'text-2xl transition-all duration-200 relative group',
          currentLocale === lang.code ? 'opacity-100 scale-110' : 'opacity-50 hover:opacity-100'
        ]"
        :title="lang.name"
      >
        {{ lang.flag }}
        <!-- Tooltip below on hover -->
        <span class="absolute top-full left-1/2 transform -translate-x-1/2 mt-2 px-2 py-1 bg-gray-900 text-white text-xs rounded whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50">
          {{ lang.name }}
        </span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

const { locale } = useI18n()
const currentLocale = ref(locale.value)

const languages = [
  { code: 'vi', flag: '🇻🇳', name: 'Tiếng Việt' },
  { code: 'en', flag: '🇬🇧', name: 'English' },
  { code: 'zh', flag: '🇨🇳', name: '中文' }
]

const changeLocale = (langCode) => {
  // Show development alert
  alert('⚠️ Tính năng đa ngôn ngữ đang được hoàn thiện\n\nLanguage switching feature is under development')
  // Commented out for now
  // currentLocale.value = langCode
  // locale.value = langCode
  // localStorage.setItem('language', langCode)
}

// Watch for external locale changes
watch(locale, (newLocale) => {
  currentLocale.value = newLocale
})
</script>

<style scoped>
.language-switcher {
  display: inline-block;
}
</style>
