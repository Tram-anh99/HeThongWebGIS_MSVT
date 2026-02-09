import { createI18n } from 'vue-i18n'
import vi from './locales/vi.json'
import en from './locales/en.json'
import zh from './locales/zh.json'

// Get saved language from localStorage or default to Vietnamese
const savedLocale = localStorage.getItem('language') || 'vi'

const i18n = createI18n({
    legacy: false, // Use Composition API mode
    locale: savedLocale,
    fallbackLocale: 'vi',
    messages: {
        vi,
        en,
        zh
    }
})

export default i18n
