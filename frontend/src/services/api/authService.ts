// frontend/src/services/api/authService.ts
import axios, { AxiosError, AxiosRequestConfig } from 'axios';
import type { AuthResponse, User } from '@/types/auth';
import { API_BASE_URL } from '@/config';

// Create axios instance with base config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

// Request interceptor to add auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // If error is 401 and we haven't already tried to refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Try to refresh the token
        const newToken = await refreshToken();
        if (newToken) {
          // Update the auth header
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          // Retry the original request
          return api(originalRequest);
        }
      } catch (refreshError) {
        // If refresh fails, clear auth and redirect to login
        await logout();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user_id: string;
  user_name?: string;
}

/**
 * Attempts to refresh the access token using the refresh token
 */
const refreshToken = async (): Promise<string | null> => {
  try {
    const refreshToken = localStorage.getItem('refresh_token') || sessionStorage.getItem('refresh_token');
    if (!refreshToken) return null;
    
    const response = await api.post<TokenResponse>(
      '/auth/refresh-token',
      { refresh_token: refreshToken }
    );
    
    if (response.data?.access_token) {
      const storage = localStorage.getItem('auth_token') ? localStorage : sessionStorage;
      storage.setItem('auth_token', response.data.access_token);
      return response.data.access_token;
    }
    return null;
  } catch (error) {
    console.error('Failed to refresh token:', error);
    await logout();
    return null;
  }
};

/**
 * Authenticates a user with the provided credentials
 * @param email - User's email address
 * @param password - User's password
 * @param rememberMe - Whether to persist the session
 * @returns Promise with user data and access token
 * @throws Error with message describing the failure reason
 */
export const login = async (email: string, password: string, rememberMe = false): Promise<AuthResponse> => {
  try {
    const response = await api.post<TokenResponse>(
      '/auth/token',
      new URLSearchParams({
        username: email,
        password,
        grant_type: 'password',
        scope: ''
      }),
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      }
    );

    if (!response.data?.access_token) {
      throw new Error('Authentication failed: No access token received');
    }

    // Store tokens based on remember me preference
    const storage = rememberMe ? localStorage : sessionStorage;
    storage.setItem('auth_token', response.data.access_token);
    if (response.data.refresh_token) {
      storage.setItem('refresh_token', response.data.refresh_token);
    }

    // Get user profile
    const userResponse = await api.get<User>('/auth/me');
    
    const user: User = {
      id: userResponse.data.id,
      email: userResponse.data.email,
      name: userResponse.data.name || email.split('@')[0],
      permissions: userResponse.data.permissions || [],
    };

    // Store user data
    storage.setItem('user', JSON.stringify(user));

    return {
      user,
      token: response.data.access_token,
      refreshToken: response.data.refresh_token
    };
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<{ detail?: string }>;
      const errorMessage = axiosError.response?.data?.detail || 
                         axiosError.message || 
                         'Login failed. Please check your credentials and try again.';
      throw new Error(errorMessage);
    }
    throw new Error('An unexpected error occurred during login');
  }
};

/**
 * Logs out the current user from both client and server
 */
export const logout = async (): Promise<void> => {
  try {
    // Try to revoke the token on the server
    await api.post('/auth/logout');
  } catch (error) {
    console.error('Error during logout:', error);
    // Continue with client-side cleanup even if server logout fails
  } finally {
    // Clear all auth-related data
    ['auth_token', 'refresh_token', 'user'].forEach(key => {
      localStorage.removeItem(key);
      sessionStorage.removeItem(key);
    });
    
    // Clear axios default headers
    delete api.defaults.headers.common['Authorization'];
    
    // Redirect to login page
    if (window.location.pathname !== '/login') {
      window.location.href = '/login';
    }
  }
};

/**
 * Verifies if the current user is authenticated
 * @returns Promise that resolves to a boolean indicating if the user is authenticated
 */
export const isAuthenticated = async (): Promise<boolean> => {
  const token = localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token');
  if (!token) return false;
  
  try {
    // Verify token validity with the server
    await api.get('/auth/verify-token');
    return true;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response?.status === 401) {
      // Token is invalid, clear auth data
      await logout();
    }
    return false;
  }
};