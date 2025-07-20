import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import type { ApiError } from '@/types/global';

/**
 * Composable for handling API errors consistently across the application
 */
export function useApiError() {
  const { t } = useI18n();
  const error = ref<string | null>(null);
  const validationErrors = ref<Record<string, string[]>>({});

  /**
   * Handle API error and extract relevant information
   */
  const handleError = (err: any): string => {
    // Reset previous errors
    error.value = null;
    validationErrors.value = {};

    // Handle Axios error response
    if (err.response) {
      const { status, data } = err.response;
      
      // Handle validation errors (422 Unprocessable Entity)
      if (status === 422 && data.errors) {
        validationErrors.value = data.errors;
        return t('errors.validation_failed');
      }
      
      // Handle 401 Unauthorized
      if (status === 401) {
        return t('errors.unauthorized');
      }
      
      // Handle 403 Forbidden
      if (status === 403) {
        return t('errors.forbidden');
      }
      
      // Handle 404 Not Found
      if (status === 404) {
        return t('errors.not_found');
      }
      
      // Handle 429 Too Many Requests
      if (status === 429) {
        return t('errors.too_many_requests');
      }
      
      // Handle 500 Internal Server Error
      if (status >= 500) {
        return t('errors.server_error');
      }
      
      // Handle custom error message from API
      if (data?.message) {
        return data.message;
      }
    }
    
    // Handle network errors
    if (err.message === 'Network Error') {
      return t('errors.network_error');
    }
    
    // Handle request cancellation
    if (err.code === 'ECONNABORTED') {
      return t('errors.request_timeout');
    }
    
    // Fallback to generic error message
    return err.message || t('errors.unknown_error');
  };

  /**
   * Set error message
   */
  const setError = (message: string) => {
    error.value = message;
  };

  /**
   * Clear all errors
   */
  const clearErrors = () => {
    error.value = null;
    validationErrors.value = {};
  };

  /**
   * Get validation error for a specific field
   */
  const getValidationError = (field: string): string | null => {
    return validationErrors.value[field]?.[0] || null;
  };

  /**
   * Check if a field has validation error
   */
  const hasValidationError = (field: string): boolean => {
    return !!validationErrors.value[field];
  };

  return {
    error,
    validationErrors,
    handleError,
    setError,
    clearErrors,
    getValidationError,
    hasValidationError,
  };
}

export type UseApiErrorReturn = ReturnType<typeof useApiError>;
