import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useAppStore = defineStore('app', () => {
  const currentModule = ref<string>('');
  const isLoading = ref<boolean>(false);
  const error = ref<string | null>(null);

  function setCurrentModule(module: string) {
    currentModule.value = module;
  }

  function setLoading(loading: boolean) {
    isLoading.value = loading;
  }

  function setError(err: string | null) {
    error.value = err;
  }

  return {
    currentModule,
    isLoading,
    error,
    setCurrentModule,
    setLoading,
    setError
  };
});
