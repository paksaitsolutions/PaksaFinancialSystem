import { ref } from 'vue';
import { useToast } from 'primevue/usetoast';

export function useErrorHandler() {
  const toast = useToast();
  const error = ref<string | null>(null);

  const handleError = (err: any, customMessage?: string) => {
    const message = customMessage || err?.message || 'An unexpected error occurred';
    
    error.value = message;
    
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: message,
      life: 5000
    });
    
    console.error('Error handled:', err);
  };

  const clearError = () => {
    error.value = null;
  };

  const withErrorHandling = async <T>(
    operation: () => Promise<T>,
    customMessage?: string
  ): Promise<T | null> => {
    try {
      clearError();
      return await operation();
    } catch (err) {
      handleError(err, customMessage);
      return null;
    }
  };

  return {
    error,
    handleError,
    clearError,
    withErrorHandling
  };
}