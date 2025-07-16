import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { ref } from 'vue';

const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  withCredentials: true,
});

// Request interceptor to add auth token if available
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle common errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Handle specific HTTP status codes
      switch (error.response.status) {
        case 401:
          // Handle unauthorized access
          console.error('Unauthorized access - please login again');
          // Redirect to login or refresh token
          break;
        case 403:
          // Handle forbidden access
          console.error('You do not have permission to perform this action');
          break;
        case 404:
          // Handle not found
          console.error('The requested resource was not found');
          break;
        case 500:
          // Handle server error
          console.error('A server error occurred');
          break;
        default:
          console.error('An error occurred:', error.message);
      }
    } else if (error.request) {
      // The request was made but no response was received
      console.error('No response received from server');
    } else {
      // Something happened in setting up the request
      console.error('Error setting up request:', error.message);
    }
    return Promise.reject(error);
  }
);

export function useApi() {
  const loading = ref(false);
  const error = ref<Error | null>(null);

  const get = async <T = any>(url: string, config?: AxiosRequestConfig): Promise<T> => {
    return request<T>({ method: 'get', url, ...config });
  };

  const post = async <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> => {
    return request<T>({ method: 'post', url, data, ...config });
  };

  const put = async <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> => {
    return request<T>({ method: 'put', url, data, ...config });
  };

  const del = async <T = any>(url: string, config?: AxiosRequestConfig): Promise<T> => {
    return request<T>({ method: 'delete', url, ...config });
  };

  const request = async <T = any>(config: AxiosRequestConfig): Promise<T> => {
    loading.value = true;
    error.value = null;
    
    try {
      const response: AxiosResponse<T> = await apiClient(config);
      return response.data;
    } catch (err: any) {
      error.value = err;
      throw err;
    } finally {
      loading.value = false;
    }
  };

  return {
    loading,
    error,
    get,
    post,
    put,
    delete: del,
    request,
  };
}

export default useApi;
