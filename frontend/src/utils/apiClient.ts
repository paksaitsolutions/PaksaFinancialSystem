import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse, type AxiosError } from 'axios';
import { useAuthStore } from '@/store/auth';

// Get environment variables with fallbacks
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_PREFIX = import.meta.env.VITE_API_PREFIX || '/api/v1';

export class ApiClient {
  private static instance: ApiClient;
  private axiosInstance: AxiosInstance;
  private isRefreshing = false;
  private failedQueue: Array<{
    resolve: (value: unknown) => void;
    reject: (reason?: any) => void;
    config: AxiosRequestConfig;
  }> = [];

  private constructor() {
    this.axiosInstance = axios.create({
      baseURL: `${API_BASE_URL}${API_PREFIX}`,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000, // 30 seconds timeout
    });

    // Request interceptor for auth token
    this.axiosInstance.interceptors.request.use(
      (config) => {
        const authStore = useAuthStore();
        if (authStore.accessToken) {
          config.headers.Authorization = `Bearer ${authStore.accessToken}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    this.axiosInstance.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };
        const authStore = useAuthStore();

        // Handle 401 Unauthorized errors with token refresh
        if (error.response?.status === 401 && !originalRequest._retry && authStore.refreshToken) {
          if (this.isRefreshing) {
            // If a refresh is already in progress, queue this request
            return new Promise((resolve, reject) => {
              this.failedQueue.push({ resolve, reject, config: originalRequest });
            });
          }

          originalRequest._retry = true;
          this.isRefreshing = true;

          try {
            // Try to refresh the token
            await authStore.refreshAccessToken();
            
            // Process the queue of failed requests
            this.processQueue(null, authStore.accessToken);
            
            // Retry the original request with the new token
            if (originalRequest && originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${authStore.accessToken}`;
            }
            return this.axiosInstance(originalRequest);
          } catch (refreshError) {
            // If refresh fails, reject all queued requests
            this.processQueue(refreshError, null);
            
            // Logout and redirect to login
            authStore.logout();
            window.location.href = '/login';
            return Promise.reject(refreshError);
          } finally {
            this.isRefreshing = false;
          }
        }

        // Handle other errors
        return Promise.reject(error);
      }
    );
  }

  private processQueue(error: any, token: string | null): void {
    this.failedQueue.forEach(({ resolve, reject, config }) => {
      if (error) {
        reject(error);
      } else if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
        resolve(this.axiosInstance(config));
      }
    });
    this.failedQueue = [];
  }

  public static getInstance(): ApiClient {
    if (!ApiClient.instance) {
      ApiClient.instance = new ApiClient();
    }
    return ApiClient.instance;
  }

  public async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    try {
      const response = await this.axiosInstance.get<T>(url, config);
      return response.data;
    } catch (error) {
      this.handleError(error);
      throw error;
    }
  }

  public async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    try {
      const response = await this.axiosInstance.post<T>(url, data, config);
      return response.data;
    } catch (error) {
      this.handleError(error);
      throw error;
    }
  }

  public async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    try {
      const response = await this.axiosInstance.put<T>(url, data, config);
      return response.data;
    } catch (error) {
      this.handleError(error);
      throw error;
    }
  }

  public async patch<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    try {
      const response = await this.axiosInstance.patch<T>(url, data, config);
      return response.data;
    } catch (error) {
      this.handleError(error);
      throw error;
    }
  }

  public async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    try {
      const response = await this.axiosInstance.delete<T>(url, config);
      return response.data;
    } catch (error) {
      this.handleError(error);
      throw error;
    }
  }

  private handleError(error: any): void {
    // Log errors or send to monitoring service
    console.error('API Error:', error);
    
    // You could add additional error handling here
    // For example, showing notifications to the user
  }
}

export const apiClient = ApiClient.getInstance();