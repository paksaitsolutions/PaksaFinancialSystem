import { createPinia } from 'pinia';
import { markRaw } from 'vue';
import { useAppStore } from './app';
import { useAuthStore } from './auth';

// Create Pinia instance
const pinia = createPinia();

// Add router to all stores
pinia.use(({ store }) => {
  const router = useRouter();
  store.router = markRaw(router);
});

export { useAppStore, useAuthStore };
export default pinia;
