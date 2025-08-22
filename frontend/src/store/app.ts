import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

/**
 * App store for managing application-wide state
 */
export const useAppStore = defineStore('app', () => {
  // State
  const isRTL = ref(false);
  const isDarkMode = ref(false);
  const isSidebarCollapsed = ref(false);
  const currentLocale = ref('en');
  const availableLocales = ref([
    { code: 'en', name: 'English' },
    { code: 'ar', name: 'العربية' },
    { code: 'ur', name: 'اردو' }
  ]);

  // Getters
  const direction = computed(() => isRTL.value ? 'rtl' : 'ltr');
  const htmlClass = computed(() => ({
    'rtl': isRTL.value,
    'dark': isDarkMode.value
  }));

  // Actions
  function toggleRTL() {
    isRTL.value = !isRTL.value;
    document.documentElement.dir = isRTL.value ? 'rtl' : 'ltr';
    localStorage.setItem('isRTL', String(isRTL.value));
  }

  function toggleDarkMode() {
    isDarkMode.value = !isDarkMode.value;
    if (isDarkMode.value) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    localStorage.setItem('darkMode', String(isDarkMode.value));
  }

  function toggleSidebar() {
    isSidebarCollapsed.value = !isSidebarCollapsed.value;
  }

  function setLocale(locale: string) {
    if (availableLocales.value.some(l => l.code === locale)) {
      currentLocale.value = locale;
      localStorage.setItem('locale', locale);
      // You might want to reload the page or update i18n here
    }
  }

  // Initialize from localStorage
  function initialize() {
    // Set RTL
    const savedRTL = localStorage.getItem('isRTL');
    if (savedRTL !== null) {
      isRTL.value = savedRTL === 'true';
      document.documentElement.dir = isRTL.value ? 'rtl' : 'ltr';
    }

    // Set dark mode
    const savedDarkMode = localStorage.getItem('darkMode');
    if (savedDarkMode !== null) {
      isDarkMode.value = savedDarkMode === 'true';
      if (isDarkMode.value) {
        document.documentElement.classList.add('dark');
      }
    }

    // Set locale
    const savedLocale = localStorage.getItem('locale');
    if (savedLocale && availableLocales.value.some(l => l.code === savedLocale)) {
      currentLocale.value = savedLocale;
    }
  }

  return {
    // State
    isRTL,
    isDarkMode,
    isSidebarCollapsed,
    currentLocale,
    availableLocales,
    
    // Getters
    direction,
    htmlClass,
    
    // Actions
    toggleRTL,
    toggleDarkMode,
    toggleSidebar,
    setLocale,
    initialize
  };
});
