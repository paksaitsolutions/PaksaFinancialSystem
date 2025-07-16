import { ref } from 'vue';
import { useSnackbar } from './useSnackbar';

export function useErrorHandling() {
  const { error: showError } = useSnackbar();
  const isLoading = ref(false);
  const error = ref<Error | null>(null);

  const handleError = (err: unknown, defaultMessage = 'An error occurred'): void => {
    // Log the error for debugging
    console.error('Error:', err);
    
    // Set the error ref
    if (err instanceof Error) {
      error.value = err;
      showError(err.message || defaultMessage);
    } else if (typeof err === 'string') {
      error.value = new Error(err);
      showError(err);
    } else {
      error.value = new Error(defaultMessage);
      showError(defaultMessage);
    }
  };

  const resetError = (): void => {
    error.value = null;
  };

  return {
    error,
    isLoading,
    handleError,
    resetError,
  };
}

export default useErrorHandling;
