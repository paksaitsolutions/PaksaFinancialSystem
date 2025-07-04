import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useI18n } from 'vue-i18n';

type Theme = 'light' | 'dark' | 'system';
type Layout = 'vertical' | 'horizontal';
type Toast = {
  severity: 'success' | 'info' | 'warn' | 'error' | 'secondary' | 'contrast';
  summary: string;
  detail: string;
  life?: number;
};

export const useAppStore = defineStore('app', () => {
  const toast = useToast();
  const { t } = useI18n();
  
  // State
  const loading = ref(false);
  const loadingText = ref('');
  const theme = ref<Theme>('light');
  const layout = ref<Layout>('vertical');
  const isSidebarCollapsed = ref(false);
  const isMobileMenuOpen = ref(false);
  const isRTL = ref(false);
  const locale = ref('en');
  const pageTitle = ref('');
  const breadcrumbs = ref<Array<{ label: string; to?: string }>>([]);
  
  // Getters
  const isLoading = computed(() => loading.value);
  const currentTheme = computed(() => theme.value);
  const currentLayout = computed(() => layout.value);
  const sidebarCollapsed = computed(() => isSidebarCollapsed.value);
  const mobileMenuOpen = computed(() => isMobileMenuOpen.value);
  const direction = computed(() => isRTL.value ? 'rtl' : 'ltr');
  const currentLocale = computed(() => locale.value);
  const currentBreadcrumbs = computed(() => breadcrumbs.value);
  
  // Actions
  function setLoading(isLoading: boolean, text: string = '') {
    loading.value = isLoading;
    loadingText.value = text;
  }
  
  function toggleSidebar() {
    isSidebarCollapsed.value = !isSidebarCollapsed.value;
    localStorage.setItem('sidebarCollapsed', String(isSidebarCollapsed.value));
  }
  
  function toggleMobileMenu() {
    isMobileMenuOpen.value = !isMobileMenuOpen.value;
  }
  
  function setTheme(newTheme: Theme) {
    theme.value = newTheme;
    localStorage.setItem('theme', newTheme);
    applyTheme(newTheme);
  }
  
  function setLayout(newLayout: Layout) {
    layout.value = newLayout;
    localStorage.setItem('layout', newLayout);
  }
  
  function setRTL(rtl: boolean) {
    isRTL.value = rtl;
    document.documentElement.dir = rtl ? 'rtl' : 'ltr';
    localStorage.setItem('rtl', String(rtl));
  }
  
  function setLocale(newLocale: string) {
    locale.value = newLocale;
    localStorage.setItem('locale', newLocale);
    document.documentElement.lang = newLocale;
  }
  
  function setPageTitle(title: string) {
    pageTitle.value = title;
    document.title = `${title} | Paksa Financial System`;
  }
  
  function setBreadcrumbs(items: Array<{ label: string; to?: string }>) {
    breadcrumbs.value = items;
  }
  
  function showToast({ severity, summary, detail, life = 3000 }: Toast) {
    toast.add({ severity, summary, detail, life });
  }
  
  function showSuccess(message: string) {
    showToast({
      severity: 'success',
      summary: t('common.success'),
      detail: message,
    });
  }
  
  function showError(message: string) {
    showToast({
      severity: 'error',
      summary: t('common.error'),
      detail: message,
    });
  }
  
  function showWarning(message: string) {
    showToast({
      severity: 'warn',
      summary: t('common.warning'),
      detail: message,
    });
  }
  
  function showInfo(message: string) {
    showToast({
      severity: 'info',
      summary: t('common.info'),
      detail: message,
    });
  }
  
  // Initialize app settings
  function initialize() {
    // Load theme preference
    const savedTheme = localStorage.getItem('theme') as Theme | null;
    if (savedTheme) {
      setTheme(savedTheme);
    } else {
      // Default to system preference
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      setTheme(prefersDark ? 'dark' : 'light');
    }
    
    // Load layout preference
    const savedLayout = localStorage.getItem('layout') as Layout | null;
    if (savedLayout) {
      setLayout(savedLayout);
    }
    
    // Load RTL preference
    const savedRTL = localStorage.getItem('rtl');
    if (savedRTL !== null) {
      setRTL(savedRTL === 'true');
    }
    
    // Load sidebar state
    const savedSidebarState = localStorage.getItem('sidebarCollapsed');
    if (savedSidebarState !== null) {
      isSidebarCollapsed.value = savedSidebarState === 'true';
    }
    
    // Set up theme change listener
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      if (theme.value === 'system') {
        setTheme(e.matches ? 'dark' : 'light');
      }
    });
  }
  
  // Helper methods
  function applyTheme(themeMode: Theme) {
    const root = document.documentElement;
    
    if (themeMode === 'system') {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      root.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
    } else {
      root.setAttribute('data-theme', themeMode);
    }
  }
  
  return {
    // State
    loading,
    loadingText,
    theme,
    layout,
    isSidebarCollapsed,
    isMobileMenuOpen,
    isRTL,
    locale,
    pageTitle,
    breadcrumbs,
    
    // Getters
    isLoading,
    currentTheme,
    currentLayout,
    sidebarCollapsed,
    mobileMenuOpen,
    direction,
    currentLocale,
    currentBreadcrumbs,
    
    // Actions
    setLoading,
    toggleSidebar,
    toggleMobileMenu,
    setTheme,
    setLayout,
    setRTL,
    setLocale,
    setPageTitle,
    setBreadcrumbs,
    showToast,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    initialize,
  };
});
