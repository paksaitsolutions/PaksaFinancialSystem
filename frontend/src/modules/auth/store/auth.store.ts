import { defineStore } from 'pinia';
import { login as apiLogin, logout as apiLogout, isAuthenticated as checkAuth } from '@/services/api/authService';
import router from '@/router';
import type { User } from '@/types/auth';
import { ref, computed } from 'vue';
import axios from 'axios';

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null);
  const token = ref<string | null>(localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token'));
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token') || sessionStorage.getItem('refresh_token'));
  const error = ref<string | null>(null);
  const loading = ref(false);
  const isInitialized = ref(false);
  const rememberMe = ref(!!localStorage.getItem('auth_token'));

  // Getters
  const isAuthenticated = computed(() => {
    return !!token.value && !!user.value;
  });

  const currentUser = computed(() => user.value);
  const hasPermission = (permission: string) => {
    return user.value?.permissions?.includes(permission) || false;
  };

  // Helper function to set authentication data
  const setAuthData = (authData: { user: User; token: string; refreshToken?: string | null }, remember: boolean = false) => {
    user.value = authData.user;
    token.value = authData.token;
    
    if (authData.refreshToken != null) {
      refreshToken.value = authData.refreshToken;
    } else {
      refreshToken.value = null;
    }
    
    // Set axios default authorization header
    axios.defaults.headers.common['Authorization'] = `Bearer ${authData.token}`;
    
    // Store tokens in appropriate storage based on remember me
    const storage = remember ? localStorage : sessionStorage;
    storage.setItem('auth_token', authData.token);
    if (authData.refreshToken != null) {
      storage.setItem('refresh_token', authData.refreshToken);
    } else {
      storage.removeItem('refresh_token');
    }
    
    // Clear the other storage to prevent conflicts
    const otherStorage = remember ? sessionStorage : localStorage;
    otherStorage.removeItem('auth_token');
    otherStorage.removeItem('refresh_token');
  };

  // Actions
  interface LoginResponse {
    user: User;
    token: string;
    refresh_token: string | null;
  }

  const login = async (credentials: { email: string; password: string; rememberMe: boolean }): Promise<boolean> => {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await apiLogin(credentials.email, credentials.password) as LoginResponse;
      
      if (response?.user && response?.token) {
        setAuthData({
          user: response.user,
          token: response.token,
          refreshToken: response.refresh_token || null
        }, credentials.rememberMe);
        
        // Redirect to intended route or home
        const redirectPath = router.currentRoute.value.query['redirect']?.toString() || '/';
        await router.push(redirectPath);
        return true;
      }
      
      throw new Error('Invalid response from server');
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Login failed';
      return false;
    } finally {
      loading.value = false;
    }
  };

  const logout = async () => {
    try {
      loading.value = true;
      await apiLogout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear state
      user.value = null;
      token.value = null;
      refreshToken.value = null;
      
      // Clear storage
      ['auth_token', 'refresh_token', 'user'].forEach(key => {
        localStorage.removeItem(key);
        sessionStorage.removeItem(key);
      });
      
      // Clear axios auth header
      delete axios.defaults.headers.common['Authorization'];
      
      // Redirect to login
      if (router.currentRoute.value.path !== '/login') {
        await router.push('/login');
      }
      
      loading.value = false;
    }
  };

  const initialize = async () => {
    try {
      loading.value = true;
      
      // Check if we have a token
      const storedToken = localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token');
      const storedRefreshToken = localStorage.getItem('refresh_token') || sessionStorage.getItem('refresh_token');
      const storedUser = localStorage.getItem('user') || sessionStorage.getItem('user');
      
      if (storedToken && storedUser) {
        // Set the token in the axios header
        axios.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`;
        
        try {
          // Verify the token is still valid
          const isValid = await checkAuth();
          if (isValid) {
            // Token is valid, set user data
            user.value = JSON.parse(storedUser);
            token.value = storedToken;
            refreshToken.value = storedRefreshToken;
            isInitialized.value = true;
            return true;
          }
        } catch (error) {
          console.error('Token validation failed:', error);
          // Clear invalid tokens
          await logout();
        }
      }
      
      return false;
    } catch (error) {
      console.error('Auth initialization error:', error);
      // Clear invalid tokens
      await logout();
      return false;
    } finally {
      isInitialized.value = true;
      loading.value = false;
    }
  };

  // Initialize the store if we have a token
  if (!isInitialized.value) {
    initialize();
  }

  // Return the store
  return {
    // State
    user,
    token,
    error,
    loading,
    isInitialized,
    rememberMe,
    refreshToken,
    
    // Getters
    isAuthenticated,
    currentUser,
    hasPermission,
    
    // Actions
    login,
    logout,
    initialize,
    setAuthData
  };
});