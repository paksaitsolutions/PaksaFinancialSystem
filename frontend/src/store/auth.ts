import { defineStore } from 'pinia';
import axios from 'axios';
import { apiClient } from '@/utils/apiClient';

// Get environment variables with fallbacks
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_PREFIX = import.meta.env.VITE_API_PREFIX || '/api/v1';
const AUTH_TOKEN_KEY = import.meta.env.VITE_AUTH_TOKEN_KEY || 'paksa_auth_token';
const AUTH_REFRESH_TOKEN_KEY = import.meta.env.VITE_AUTH_REFRESH_TOKEN_KEY || 'paksa_refresh_token';

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
        // Use direct axios call to avoid circular dependency with apiClient
        const response = await axios.post(`${API_BASE_URL}${API_PREFIX}/auth/login`, {
          username: email, // API expects username field
          password,
        });
        
        const { access_token, refresh_token, user } = response.data;
        
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
        this.error = error.response?.data?.detail || 'Login failed. Please check your credentials.';
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
        // Use direct axios call to avoid circular dependency
        const response = await axios.post(`${API_BASE_URL}${API_PREFIX}/auth/refresh`, {
          refresh_token: this.refreshToken,
        });
        
        const { access_token } = response.data;
        
        // Update access token
        this.accessToken = access_token;
        localStorage.setItem(AUTH_TOKEN_KEY, access_token);
        
        return access_token;
      } catch (error) {
        // If refresh fails, clear auth state
        this.logout();
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