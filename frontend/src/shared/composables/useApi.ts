import { ref } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useI18n } from 'vue-i18n';

export function useApi<T>() {
  const loading = ref(false);
  const error = ref<Error | null>(null);
  const data = ref<T | null>(null);
  const toast = useToast();
  const { t } = useI18n();

  const execute = async (apiCall: () => Promise<T>) => {
    loading.value = true;
    error.value = null;
    
    try {
      const result = await apiCall();
      data.value = result;
      return result;
    } catch (err) {
      error.value = err as Error;
      toast.add({
        severity: 'error',
        summary: t('errors.error'),
        detail: err instanceof Error ? err.message : t('errors.unknown'),
        life: 5000,
      });
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const reset = () => {
    loading.value = false;
    error.value = null;
    data.value = null;
  };

  return {
    loading,
    error,
    data,
    execute,
    reset,
  };
}
