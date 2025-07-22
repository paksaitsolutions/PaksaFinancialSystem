import axios, { AxiosError, type AxiosInstance, type InternalAxiosRequestConfig } from 'axios';
import { useRouter } from 'vue-router';

// Create axios instance with base configuration
const createApiClient = (): AxiosInstance => {
  const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
    },
    withCredentials: true, // Important for cookies, authorization headers with HTTPS
  });

  // Request interceptor for API calls
  api.interceptors.request.use(
    async (config) => {
      const authStore = useAuthStore();
      
      // If we have a token, use it
      if (authStore.token) {
        const tokenType = localStorage.getItem('token_type') || 'Bearer';
        config.headers.Authorization = `${tokenType} ${authStore.token}`;
      }
      
      // Add request timestamp for caching
      config.headers['X-Request-Timestamp'] = Date.now();
      
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  // Response interceptor for API calls
  api.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
      const originalRequest = error.config as any;
      const authStore = useAuthStore();
      
      // If the error is 401 and we haven't tried to refresh yet
      if (error.response?.status === 401 && !originalRequest._retry) {
        
        // If we're already refreshing, add the request to the queue
        if (isRefreshing) {
          return new Promise((resolve, reject) => {
            refreshAndRetryQueue.push(() => {
              originalRequest.headers.Authorization = `Bearer ${authStore.token}`;
              resolve(api(originalRequest));
            });
          });
        }
        
        originalRequest._retry = true;
        isRefreshing = true;
        
        try {
          // Try to refresh the token
          const refreshToken = localStorage.getItem('refresh_token');
          
          if (refreshToken) {
            const response = await axios.post(
              `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/auth/refresh-token`,
              { refresh_token: refreshToken }
            );
            
            const { access_token, token_type, expires_in } = response.data;
            
            // Update the auth store with the new token
            authStore.token = access_token;
            localStorage.setItem('token', access_token);
            localStorage.setItem('token_type', token_type || 'Bearer');
            
            // Update the authorization header
            originalRequest.headers.Authorization = `${token_type || 'Bearer'} ${access_token}`;
            
            // Process the queue
            processQueue(null, access_token);
            
            // Retry the original request
            return api(originalRequest);
          } else {
            // No refresh token available, redirect to login
            await authStore.logout();
            router.push({ name: 'login', query: { redirect: router.currentRoute.value.fullPath } });
            return Promise.reject(error);
            if (refreshToken) {
              const formData = new URLSearchParams();
              formData.append('refresh_token', refreshToken);
              formData.append('grant_type', 'refresh_token');
              
              const response = await axios.post(
                `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/v1/auth/refresh`,
                formData,
                {
                  headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': 'application/json'
                  }
                }
              );
              
              const { access_token, token_type } = response.data;
              
              if (access_token) {
                // Update tokens in storage
                localStorage.setItem('token', access_token);
                localStorage.setItem('token_type', token_type || 'bearer');
                
                // Update the Authorization header for the original request
                if (originalRequest.headers) {
                  originalRequest.headers.Authorization = `${token_type || 'Bearer'} ${access_token}`;
                }
                
                // Retry the original request with the new token
                return api(originalRequest);
              }
            }
          } catch (refreshError) {
            console.error('Token refresh failed:', refreshError);
            // Continue to logout if refresh fails
          }
        }
        
        // If we get here, token refresh failed or was not possible
        // Clear auth data and redirect to login
        const authStore = useAuthStore?.();
        if (authStore) {
          authStore.clearAuthData();
        } else {
          // Fallback if store is not available
          localStorage.removeItem('token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('token_type');
          localStorage.removeItem('user');
          sessionStorage.removeItem('user');
        }
        
        // Don't redirect if we're already on the login page
        if (!window.location.pathname.includes('/auth/login')) {
          const returnTo = window.location.pathname + window.location.search;
          window.location.href = `/auth/login?redirect=${encodeURIComponent(returnTo)}`;
        }
        
        return Promise.reject({
          message: 'Your session has expired. Please log in again.',
          requiresLogin: true
        });
      }
      
      // Handle other error statuses
      if (status >= 500) {
        console.error('Server Error:', data);
        return Promise.reject({
          message: 'The server encountered an error. Please try again later.',
          details: data,
          isServerError: true
        });
      }
      
      // Handle 4xx errors
      if (status >= 400) {
        return Promise.reject({
          message: data?.detail || data?.message || 'An error occurred',
          details: data,
          isClientError: true,
          statusCode: status
        });
      }
      
      // For any other errors, just reject with the error
      return Promise.reject(error);
    }
  );
  
  return api;
};

// Create and export the API client instance
export const api = createApiClient();

export default api;