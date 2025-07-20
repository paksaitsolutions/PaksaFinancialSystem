import { ref } from 'vue';
import axios, { type AxiosRequestConfig, type AxiosResponse } from 'axios';
import { useApiError } from './useApiError';
import type { ApiResponse, PaginatedResponse } from '@/types/global';

interface ApiRequestOptions<T = any> extends AxiosRequestConfig {
  /**
   * Whether to show loading state
   * @default true
   */
  showLoading?: boolean;
  
  /**
   * Whether to handle errors automatically
   * @default true
   */
  handleError?: boolean;
  
  /**
   * Whether to transform the response
   * @default true
   */
  transformResponse?: boolean;
  
  /**
   * Custom error message
   */
  errorMessage?: string;
  
  /**
   * Success message to show
   */
  successMessage?: string;
  
  /**
   * Callback function to be called on success
   */
  onSuccess?: (data: T) => void;
  
  /**
   * Callback function to be called on error
   */
  onError?: (error: any) => void;
  
  /**
   * Callback function to be called when the request completes
   */
  onFinally?: () => void;
}

/**
 * Composable for making API requests with consistent error handling and loading states
 */
export function useApiRequest() {
  const { handleError, ...errorHandlers } = useApiError();
  const isLoading = ref(false);
  const isError = ref(false);
  const isSuccess = ref(false);
  const data = ref<any>(null);
  const error = ref<any>(null);
  
  /**
   * Make an API request
   */
  const request = async <T = any>(
    config: AxiosRequestConfig,
    options: ApiRequestOptions<T> = {}
  ): Promise<ApiResponse<T> | PaginatedResponse<T> | T | null> => {
    const {
      showLoading = true,
      handleError: shouldHandleError = true,
      transformResponse = true,
      errorMessage,
      successMessage,
      onSuccess,
      onError,
      onFinally,
      ...axiosConfig
    } = options;
    
    // Reset states
    isError.value = false;
    isSuccess.value = false;
    error.value = null;
    data.value = null;
    
    // Set loading state
    if (showLoading) {
      isLoading.value = true;
    }
    
    try {
      // Make the request
      const response: AxiosResponse<ApiResponse<T> | PaginatedResponse<T> | T> = await axios({
        ...config,
        ...axiosConfig,
      });
      
      // Handle successful response
      isSuccess.value = true;
      
      // Transform the response if needed
      let responseData: any = response.data;
      
      if (transformResponse) {
        // Handle standard API response format
        if (responseData && typeof responseData === 'object' && 'data' in responseData) {
          responseData = responseData.data;
        }
        
        // Handle paginated response
        if (Array.isArray((response as AxiosResponse<PaginatedResponse<T>>).data?.items)) {
          responseData = (response as AxiosResponse<PaginatedResponse<T>>).data;
        }
      }
      
      // Set the data
      data.value = responseData;
      
      // Call success callback
      if (onSuccess) {
        onSuccess(responseData);
      }
      
      // Show success message if provided
      if (successMessage) {
        // You can integrate with a notification system here
        console.log('Success:', successMessage);
      }
      
      return responseData;
    } catch (err: any) {
      // Handle error
      isError.value = true;
      error.value = err;
      
      // Call error callback
      if (onError) {
        onError(err);
      }
      
      // Handle error automatically if enabled
      if (shouldHandleError) {
        const errorMessage = handleError(err);
        
        // Show error message
        if (errorMessage) {
          // You can integrate with a notification system here
          console.error('Error:', errorMessage);
        }
      }
      
      // Re-throw the error if not handled
      throw err;
    } finally {
      // Reset loading state
      if (showLoading) {
        isLoading.value = false;
      }
      
      // Call finally callback
      if (onFinally) {
        onFinally();
      }
    }
  };
  
  /**
   * Make a GET request
   */
  const get = <T = any>(
    url: string,
    params?: any,
    options: Omit<ApiRequestOptions<T>, 'method'> = {}
  ) => {
    return request<T>(
      {
        method: 'GET',
        url,
        params,
      },
      options
    );
  };
  
  /**
   * Make a POST request
   */
  const post = <T = any>(
    url: string,
    data?: any,
    options: Omit<ApiRequestOptions<T>, 'method' | 'data'> = {}
  ) => {
    return request<T>(
      {
        method: 'POST',
        url,
        data,
      },
      options
    );
  };
  
  /**
   * Make a PUT request
   */
  const put = <T = any>(
    url: string,
    data?: any,
    options: Omit<ApiRequestOptions<T>, 'method' | 'data'> = {}
  ) => {
    return request<T>(
      {
        method: 'PUT',
        url,
        data,
      },
      options
    );
  };
  
  /**
   * Make a PATCH request
   */
  const patch = <T = any>(
    url: string,
    data?: any,
    options: Omit<ApiRequestOptions<T>, 'method' | 'data'> = {}
  ) => {
    return request<T>(
      {
        method: 'PATCH',
        url,
        data,
      },
      options
    );
  };
  
  /**
   * Make a DELETE request
   */
  const remove = <T = any>(
    url: string,
    options: Omit<ApiRequestOptions<T>, 'method'> = {}
  ) => {
    return request<T>(
      {
        method: 'DELETE',
        url,
      },
      options
    );
  };
  
  return {
    // State
    isLoading,
    isError,
    isSuccess,
    data,
    error,
    
    // Methods
    request,
    get,
    post,
    put,
    patch,
    delete: remove,
    
    // Error handling
    ...errorHandlers,
  };
}

export type UseApiRequestReturn = ReturnType<typeof useApiRequest>;
