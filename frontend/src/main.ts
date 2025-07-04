import { createApp, type ComponentPublicInstance } from 'vue';
import { createPinia } from 'pinia';
import { createI18n, type I18n } from 'vue-i18n';
import { VueQueryPlugin } from '@tanstack/vue-query';
import PrimeVue from 'primevue/config';
import ToastService from 'primevue/toastservice';
import ConfirmationService from 'primevue/confirmationservice';
import Tooltip from 'primevue/tooltip';
import 'primevue/resources/themes/saga-blue/theme.css';
import 'primevue/resources/primevue.min.css';
import 'primeicons/primeicons.css';
import 'primeflex/primeflex.css';
import './assets/styles/main.scss';

import App from './App.vue';
import router from './router';
import { useAuthStore } from './store/auth';

// Create app
const app = createApp(App);

// Use plugins
app.use(createPinia());
app.use(router);
app.use(PrimeVue, { ripple: true });
app.use(ToastService);
app.use(ConfirmationService);
app.directive('tooltip', Tooltip);

// i18n configuration
const i18n: I18n = createI18n({
  legacy: false,
  locale: 'en',
  fallbackLocale: 'en',
  messages: {
    en: {
      // Will be loaded from separate files
    },
    ar: {
      // Will be loaded from separate files
    },
    ur: {
      // Will be loaded from separate files
    },
  },
});
app.use(i18n);

// Vue Query configuration
app.use(VueQueryPlugin, {
  queryClientConfig: {
    defaultOptions: {
      queries: {
        retry: 1,
        refetchOnWindowFocus: false,
        staleTime: 5 * 60 * 1000, // 5 minutes
      },
    },
  },
});

// Global error handler
app.config.errorHandler = (err: unknown, vm: ComponentPublicInstance | null, info: string) => {
  console.error('Global error:', { err, vm, info });
  // TODO: Log to error tracking service
  return false; // Prevent error from propagating further
};

// Initialize auth
const authStore = useAuthStore();
// Use nextTick to ensure the app is fully initialized
authStore.initialize().catch((error: Error) => {
  console.error('Failed to initialize auth:', error);
});

// Mount the app
app.mount('#app');
