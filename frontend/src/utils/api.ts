import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse, type AxiosError } from 'axios';
import { useAuthStore } from '@/stores/auth';
import { API_CONFIG, HTTP_STATUS } from '@/constants';
import { useNotifications } from '@/composables/useNotifications';

type RequestConfig = AxiosRequestConfig & {
  /**
   * Whether to include authentication token in the request
   * @default true
   */
  requireAuth?: boolean;
  
  /**
   * Whether to show error notifications
   * @default true
   */
  showError?: boolean;
  
  /**
   * Whether to show success notifications
   * @default false
   */
  showSuccess?: boolean;
  
  /**
   * Custom error message to show when the request fails
   */
  errorMessage?: string;
  
  /**
   * Custom success message to show when the request succeeds
   */
  successMessage?: string;
};

/**
 * Creates a configured axios instance with interceptors
 */
function createApiClient(baseURL: string): AxiosInstance {
  const instance = axios.create({
    baseURL,
    timeout: API_CONFIG.TIMEOUT,
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
  });

  // Request interceptor
  instance.interceptors.request.use(
    (config: RequestConfig) => {
      const authStore = useAuthStore();
      
      // Add auth token if required and available
      if (config.requireAuth !== false && authStore.isAuthenticated) {
        config.headers = config.headers || {};
        config.headers.Authorization = `Bearer ${authStore.token}`;
      }
      
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  // Response interceptor
  instance.interceptors.response.use(
    (response: AxiosResponse) => {
      const config = response.config as RequestConfig;
      const { showSuccess, successMessage } = config;
      const { success: showSuccessNotification } = useNotifications();
      
      // Show success message if enabled
      if (showSuccess) {
        const message = successMessage || response.data?.message || 'Operation completed successfully';
        showSuccessNotification(message);
      }
      
      return response.data;
    },
    async (error: AxiosError) => {
      const config = error.config as RequestConfig;
      const { showError = true, errorMessage } = config || {};
      const { error: showErrorNotification } = useNotifications();
      const authStore = useAuthStore();
      
      // Default error message
      let message = errorMessage || 'An error occurred';
      let status = error.response?.status;
      
      // Handle specific HTTP status codes
      if (error.response) {
        const responseData = error.response.data as Record<string, any>;
        
        // Extract error message from response
        if (responseData?.message) {
          message = responseData.message;
        } else if (typeof responseData === 'string') {
          message = responseData;
        } else if (Array.isArray(responseData?.errors)) {
          // Handle validation errors
          message = responseData.errors.map((e: any) => e.message).join('\n');
        }
        
        // Handle specific status codes
        switch (status) {
          case HTTP_STATUS.UNAUTHORIZED:
            // If we're already on the login page, don't redirect
            if (!window.location.pathname.includes('/auth/login')) {
              authStore.logout();
              // Redirect to login with return URL
              const returnUrl = encodeURIComponent(window.location.pathname + window.location.search);
              window.location.href = `/auth/login?returnUrl=${returnUrl}`;
            }
            break;
            
          case HTTP_STATUS.FORBIDDEN:
            message = 'You do not have permission to perform this action';
            break;
            
          case HTTP_STATUS.NOT_FOUND:
            message = 'The requested resource was not found';
            break;
            
          case HTTP_STATUS.TOO_MANY_REQUESTS:
            message = 'Too many requests. Please try again later.';
            break;
            
          case HTTP_STATUS.INTERNAL_SERVER_ERROR:
            message = 'An internal server error occurred. Please try again later.';
            break;
        }
      } else if (error.request) {
        // The request was made but no response was received
        message = 'No response from server. Please check your internet connection.';
      }
      
      // Show error notification if enabled
      if (showError) {
        showErrorNotification(message);
      }
      
      // Return a rejected promise with the error
      return Promise.reject({
        message,
        status,
        code: error.code,
        response: error.response,
        isAxiosError: error.isAxiosError,
        toJSON: error.toJSON,
      });
    }
  );

  return instance;
}

// Create the default API client
const api = createApiClient(import.meta.env.VITE_API_BASE_URL || '/api');

/**
 * API client with type-safe methods
 */
const apiClient = {
  /**
   * Perform a GET request
   */
  get<T = any>(
    url: string,
    config?: RequestConfig
  ): Promise<T> {
    return api.get(url, config);
  },
  
  /**
   * Perform a POST request
   */
  post<T = any>(
    url: string,
    data?: any,
    config?: RequestConfig
  ): Promise<T> {
    return api.post(url, data, config);
  },
  
  /**
   * Perform a PUT request
   */
  put<T = any>(
    url: string,
    data?: any,
    config?: RequestConfig
  ): Promise<T> {
    return api.put(url, data, config);
  },
  
  /**
   * Perform a PATCH request
   */
  patch<T = any>(
    url: string,
    data?: any,
    config?: RequestConfig
  ): Promise<T> {
    return api.patch(url, data, config);
  },
  
  /**
   * Perform a DELETE request
   */
  delete<T = any>(
    url: string,
    config?: RequestConfig
  ): Promise<T> {
    return api.delete(url, config);
  },
  
  /**
   * Perform a request with a custom method
   */
  request<T = any>(
    config: RequestConfig
  ): Promise<T> {
    return api.request(config);
  },
  
  /**
   * Set the base URL for all requests
   */
  setBaseURL(url: string): void {
    api.defaults.baseURL = url;
  },
  
  /**
   * Set a default header for all requests
   */
  setHeader(name: string, value: string): void {
    api.defaults.headers.common[name] = value;
  },
  
  /**
   * Remove a default header
   */
  removeHeader(name: string): void {
    delete api.defaults.headers.common[name];
  },
};

export { apiClient as api };

export default apiClient;
