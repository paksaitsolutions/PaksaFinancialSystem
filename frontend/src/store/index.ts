import { createPinia } from 'pinia';
import { markRaw } from 'vue';
import { useRouter } from 'vue-router';
import { useAppStore } from './app';
import { useAuthStore } from './auth';
import { useReconciliationStore } from './reconciliation';

// Create Pinia instance
const pinia = createPinia();

// Add router to all stores
pinia.use(({ store }) => {
  const router = useRouter();
  store.router = markRaw(router);
});

export { 
  useAppStore, 
  useAuthStore, 
  useReconciliationStore 
};

export default pinia;
