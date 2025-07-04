<template>
  <RouterView v-slot="{ Component }">
    <template v-if="Component">
      <Suspense>
        <template #default>
          <component :is="Component" />
        </template>
        <template #fallback>
          <div class="flex items-center justify-center min-h-screen">
            <ProgressSpinner />
          </div>
        </template>
      </Suspense>
    </template>
  </RouterView>
  <Toast position="top-right" />
  <ConfirmDialog />
  <DynamicDialog />
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router';
import { useAuthStore } from '@/store/auth';
import { onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useTheme } from '@/composables/useTheme';
import { useLoading } from '@/composables/useLoading';
import { useErrorHandler } from '@/composables/useErrorHandler';
import { useOnlineStatus } from '@/composables/useOnlineStatus';
import ProgressSpinner from 'primevue/progressspinner';
import Toast from 'primevue/toast';
import ConfirmDialog from 'primevue/confirmdialog';
import DynamicDialog from 'primevue/dynamicdialog';

const { locale } = useI18n();
const authStore = useAuthStore();
const { initTheme } = useTheme();
const { initLoading } = useLoading();
const { initErrorHandler } = useErrorHandler();
const { initOnlineStatus } = useOnlineStatus();

// Initialize app
onMounted(async () => {
  // Set initial language from localStorage or browser
  const savedLocale = localStorage.getItem('locale') || navigator.language.split('-')[0];
  if (['en', 'ar', 'ur'].includes(savedLocale)) {
    locale.value = savedLocale;
  }
  
  // Initialize theme
  initTheme();
  
  // Initialize loading state
  initLoading();
  
  // Initialize error handling
  initErrorHandler();
  
  // Initialize online status monitoring
  initOnlineStatus();
  
  // Initialize auth state
  if (authStore.isAuthenticated) {
    try {
      await authStore.fetchUser();
    } catch (error) {
      console.error('Failed to fetch user:', error);
      authStore.logout();
    }
  }
});
</script>

<style>
/* Global styles */
:root {
  --primary-color: #2563eb;
  --primary-dark: #1d4ed8;
  --secondary-color: #64748b;
  --success-color: #10b981;
  --danger-color: #ef4444;
  --warning-color: #f59e0b;
  --info-color: #3b82f6;
  --light-color: #f8fafc;
  --dark-color: #0f172a;
  --border-color: #e2e8f0;
  --border-radius: 0.375rem;
  --box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
  --transition: all 0.2s ease-in-out;
}

/* RTL support */
[dir='rtl'] {
  direction: rtl;
  text-align: right;
}

/* Global transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
