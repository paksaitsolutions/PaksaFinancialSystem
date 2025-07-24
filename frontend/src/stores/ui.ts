import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useUIStore = defineStore('ui', () => {
  // Loading states
  const globalLoading = ref(false);
  const loadingStates = ref<Record<string, boolean>>({});

  // Navigation
  const sidebarCollapsed = ref(false);
  const currentModule = ref('dashboard');

  // Theme
  const darkMode = ref(false);
  const theme = ref('light');

  // Notifications
  const notifications = ref<Array<{
    id: string;
    type: 'info' | 'success' | 'warning' | 'error';
    title: string;
    message: string;
    timestamp: Date;
    read: boolean;
  }>>([]);

  // Computed
  const isLoading = computed(() => 
    globalLoading.value || Object.values(loadingStates.value).some(state => state)
  );

  const unreadNotifications = computed(() => 
    notifications.value.filter(n => !n.read)
  );

  // Actions
  const setGlobalLoading = (loading: boolean) => {
    globalLoading.value = loading;
  };

  const setLoadingState = (key: string, loading: boolean) => {
    loadingStates.value[key] = loading;
  };

  const toggleSidebar = () => {
    sidebarCollapsed.value = !sidebarCollapsed.value;
  };

  const setSidebarCollapsed = (collapsed: boolean) => {
    sidebarCollapsed.value = collapsed;
  };

  const setCurrentModule = (module: string) => {
    currentModule.value = module;
  };

  const toggleTheme = () => {
    darkMode.value = !darkMode.value;
    theme.value = darkMode.value ? 'dark' : 'light';
    
    // Apply theme to document
    document.documentElement.setAttribute('data-theme', theme.value);
  };

  const addNotification = (notification: Omit<typeof notifications.value[0], 'id' | 'timestamp' | 'read'>) => {
    notifications.value.unshift({
      ...notification,
      id: Date.now().toString(),
      timestamp: new Date(),
      read: false
    });
  };

  const markNotificationRead = (id: string) => {
    const notification = notifications.value.find(n => n.id === id);
    if (notification) {
      notification.read = true;
    }
  };

  const clearNotifications = () => {
    notifications.value = [];
  };

  return {
    // State
    globalLoading,
    loadingStates,
    sidebarCollapsed,
    currentModule,
    darkMode,
    theme,
    notifications,
    
    // Computed
    isLoading,
    unreadNotifications,
    
    // Actions
    setGlobalLoading,
    setLoadingState,
    toggleSidebar,
    setSidebarCollapsed,
    setCurrentModule,
    toggleTheme,
    addNotification,
    markNotificationRead,
    clearNotifications
  };
});