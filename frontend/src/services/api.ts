import axios, { AxiosError } from 'axios';
import { useRouter } from 'vue-router';

// Create axios instance with base configuration
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
  },
  withCredentials: true,
  timeout: 10000
});

// Request interceptor for API calls
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    const tokenType = localStorage.getItem('token_type') || 'Bearer';
    
    if (token) {
      config.headers.Authorization = `${tokenType} ${token}`;
    }
    
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
    const router = useRouter();
    
    // Handle network errors
    if (!error.response) {
      console.error('Network Error:', error.message);
      return Promise.reject({ message: 'Network error. Please check your connection.' });
    }
    
    const { status, data } = error.response;
    
    // Handle 401 Unauthorized errors (token expired)
    if (status === 401) {
      if (originalRequest.url?.includes('auth/token')) {
        // If this is a login request, just reject
        return Promise.reject(error);
      }
      
      if (!originalRequest._retry) {
        originalRequest._retry = true;
        
        try {
          // Attempt to refresh the token
          const refreshToken = localStorage.getItem('refresh_token');
          if (refreshToken) {
            const formData = new URLSearchParams();
            formData.append('refresh_token', refreshToken);
            formData.append('grant_type', 'refresh_token');
            
            const response = await axios.post(
              `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/v1/auth/refresh`,
              formData,
              {
                headers: {
                  'Content-Type': 'application/x-www-form-urlencoded'
                }
              }
            );
            
            const { access_token, token_type } = response.data;
            
            // Update tokens in storage
            localStorage.setItem('token', access_token);
            localStorage.setItem('token_type', token_type);
            
            // Update the Authorization header
            originalRequest.headers.Authorization = `${token_type} ${access_token}`;
            
            // Retry the original request
            return api(originalRequest);
          }
        } catch (refreshError) {
          console.error('Token refresh failed:', refreshError);
          // Continue to logout if refresh fails
        }
      }
      
      // If we get here, token refresh failed or was not possible
      localStorage.removeItem('token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('token_type');
      
      // Redirect to login with redirect back to current page
      const returnTo = window.location.pathname + window.location.search;
      router.push(`/auth/login?redirect=${encodeURIComponent(returnTo)}`);
      
      return Promise.reject(error);
    }
    
    // Handle other error statuses
    if (status >= 500) {
      console.error('Server Error:', data);
      return Promise.reject({
        message: 'Server error. Please try again later.',
        details: data
      });
    }
    
    // For 4xx errors, pass through the error response
    return Promise.reject({
      message: data?.detail || data?.message || 'An error occurred',
      details: data
    });
      } catch (refreshError) {
        // If refresh token fails, redirect to login
        localStorage.removeItem('token');
        window.location.href = '/auth/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;