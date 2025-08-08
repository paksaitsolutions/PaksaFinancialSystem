import { defineStore } from 'pinia';
import axios from 'axios';
import { apiClient } from '@/utils/apiClient';

// Get environment variables with fallbacks using bracket notation for TypeScript
const env = import.meta.env as {
  VITE_API_BASE_URL?: string;
  VITE_API_PREFIX?: string;
  VITE_AUTH_TOKEN_KEY?: string;
  VITE_AUTH_REFRESH_TOKEN_KEY?: string;
};

const API_BASE_URL = env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_PREFIX = env.VITE_API_PREFIX || '/api/v1';
const AUTH_TOKEN_KEY = env.VITE_AUTH_TOKEN_KEY || 'paksa_auth_token';
const AUTH_REFRESH_TOKEN_KEY = env.VITE_AUTH_REFRESH_TOKEN_KEY || 'paksa_refresh_token';

interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  is_superuser: boolean;
}

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    accessToken: localStorage.getItem(AUTH_TOKEN_KEY),
    refreshToken: localStorage.getItem(AUTH_REFRESH_TOKEN_KEY),
    user: null,
    isAuthenticated: !!localStorage.getItem(AUTH_TOKEN_KEY),
    loading: false,
    error: null,
  }),
  
  getters: {
    isLoggedIn: (state) => state.isAuthenticated && !!state.accessToken,
    isSuperuser: (state) => state.user?.is_superuser || false,
    userFullName: (state) => state.user?.full_name || '',
  },
  
  actions: {
    async login(email: string, password: string) {
      this.loading = true;
      this.error = null;
      
      try {
        // Use direct axios call with form data to match backend expectations
        const formData = new FormData();
        formData.append('username', email);
        formData.append('password', password);
        
        const response = await axios.post(`${API_BASE_URL}/auth/token`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        
        const { access_token, refresh_token } = response.data;
        
        // Fetch user profile after successful login
        const userResponse = await axios.get(`${API_BASE_URL}/auth/me`, {
          headers: {
            'Authorization': `Bearer ${access_token}`
          }
        });
        
        const user = userResponse.data;
        
        // Store tokens
        this.accessToken = access_token;
        this.refreshToken = refresh_token;
        this.user = user;
        this.isAuthenticated = true;
        
        // Save to localStorage
        localStorage.setItem(AUTH_TOKEN_KEY, access_token);
        localStorage.setItem(AUTH_REFRESH_TOKEN_KEY, refresh_token);
        
        return true;
      } catch (error: any) {
        console.error('Login error:', error);
        if (error.response) {
          // The request was made and the server responded with a status code
          // that falls out of the range of 2xx
          console.error('Response data:', error.response.data);
          console.error('Response status:', error.response.status);
          console.error('Response headers:', error.response.headers);
          this.error = error.response.data?.detail || 
                     error.response.data?.message || 
                     `Server error: ${error.response.status} ${error.response.statusText}`;
        } else if (error.request) {
          // The request was made but no response was received
          console.error('No response received:', error.request);
          this.error = 'No response from server. Please check your connection.';
        } else {
          // Something happened in setting up the request that triggered an Error
          console.error('Error:', error.message);
          this.error = error.message || 'An unexpected error occurred';
        }
        return false;
      } finally {
        this.loading = false;
      }
    },
    
    async refreshAccessToken() {
      if (!this.refreshToken) {
        throw new Error('No refresh token available');
      }
      
      try {
        const formData = new FormData();
        formData.append('refresh_token', this.refreshToken);
        
        const response = await axios.post(
          `${API_BASE_URL}/auth/token`,
          formData,
          {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
          }
        );
        
        const { access_token, refresh_token } = response.data;
        this.accessToken = access_token;
        this.refreshToken = refresh_token || this.refreshToken;
        
        // Update stored tokens
        localStorage.setItem(AUTH_TOKEN_KEY, access_token);
        if (refresh_token) {
          localStorage.setItem(AUTH_REFRESH_TOKEN_KEY, refresh_token);
        }
        
        return access_token;
      } catch (error) {
        await this.logout();
        throw error;
      }
    },
    
    async fetchUserProfile() {
      if (!this.accessToken) {
        return null;
      }
      
      try {
        const user = await apiClient.get<User>('/users/me');
        this.user = user;
        return user;
      } catch (error) {
        console.error('Failed to fetch user profile:', error);
        return null;
      }
    },
    
    logout() {
      // Clear state
      this.accessToken = null;
      this.refreshToken = null;
      this.user = null;
      this.isAuthenticated = false;
      
      // Clear localStorage
      localStorage.removeItem(AUTH_TOKEN_KEY);
      localStorage.removeItem(AUTH_REFRESH_TOKEN_KEY);
    },
    
    async checkAuth() {
      if (!this.accessToken) {
        return false;
      }
      
      try {
        await this.fetchUserProfile();
        return true;
      } catch (error) {
        // If token is invalid, try to refresh
        try {
          await this.refreshAccessToken();
          await this.fetchUserProfile();
          return true;
        } catch (refreshError) {
          this.logout();
          return false;
        }
      }
    },
  },
});