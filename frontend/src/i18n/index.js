import { createI18n } from 'vue-i18n';
import en from './en';
import ur from './ur';
import ar from './ar';

// Available languages with their display names and RTL flag
export const availableLocales = [
  {
    code: 'en',
    name: 'English',
    rtl: false,
    flag: '🇬🇧',
  },
  {
    code: 'ur',
    name: 'اردو',
    rtl: false,
    flag: '🇵🇰',
  },
  {
    code: 'ar',
    name: 'العربية',
    rtl: true,
    flag: '🇸🇦',
  },
];

// Default locale
const defaultLocale = 'en';

// Detect user's preferred language
const getBrowserLocale = () => {
  const browserLocale = navigator.language || navigator.userLanguage || defaultLocale;
  return browserLocale.split('-')[0]; // Extract language code (e.g., 'en' from 'en-US')
};

// Get initial locale from localStorage or browser settings
const initialLocale = localStorage.getItem('user-locale') || getBrowserLocale();

// Create i18n instance
export const i18n = createI18n({
  legacy: false, // Use Composition API
  locale: availableLocales.some(locale => locale.code === initialLocale) 
    ? initialLocale 
    : defaultLocale,
  fallbackLocale: defaultLocale,
  globalInjection: true,
  messages: { en, ur, ar },
});

// Set HTML direction based on RTL status
const updateHtmlDirection = (locale) => {
  const html = document.documentElement;
  const isRTL = availableLocales.find(l => l.code === locale)?.rtl || false;
  
  html.setAttribute('dir', isRTL ? 'rtl' : 'ltr');
  html.setAttribute('lang', locale);
};

// Listen for locale changes
i18n.global.locale.value = i18n.locale.value;
updateHtmlDirection(i18n.locale.value);

export default i18n;
