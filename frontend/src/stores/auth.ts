import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { User } from '@/types/auth';
import authService from '@/services/api/authService';

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null);
  const isAuthenticated = computed(() => !!user.value);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Initialize from localStorage if available
  const storedUser = localStorage.getItem('user');
  if (storedUser) {
    try {
      user.value = JSON.parse(storedUser);
    } catch (e) {
      localStorage.removeItem('user');
    }
  }

  // Getters
  const userRole = computed(() => user.value?.role || null);
  const userId = computed(() => user.value?.id || null);
  const userName = computed(() => user.value?.name || null);

  // Actions
  async function login(credentials: { email: string; password: string }) {
    try {
      loading.value = true;
      error.value = null;
      
      const response = await authService.login(credentials.email, credentials.password);
      user.value = response.user;
      
      // Store user and token in localStorage
      localStorage.setItem('user', JSON.stringify(response.user));
      localStorage.setItem('token', response.token);
      
      return true;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Login failed';
      return false;
    } finally {
      loading.value = false;
    }
  }

  async function register(userData: any) {
    try {
      loading.value = true;
      error.value = null;
      
      await authService.register(userData);
      return true;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Registration failed';
      return false;
    } finally {
      loading.value = false;
    }
  }

  async function forgotPassword(email: string) {
    try {
      loading.value = true;
      error.value = null;
      
      await authService.forgotPassword(email);
      return true;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to send reset instructions';
      return false;
    } finally {
      loading.value = false;
    }
  }

  async function resetPassword(token: string, password: string) {
    try {
      loading.value = true;
      error.value = null;
      
      await authService.resetPassword(token, password);
      return true;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Password reset failed';
      return false;
    } finally {
      loading.value = false;
    }
  }

  async function logout() {
    try {
      loading.value = true;
      await authService.logout();
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      // Clear user data regardless of API success/failure
      user.value = null;
      localStorage.removeItem('user');
      localStorage.removeItem('token');
      loading.value = false;
      
      // Redirect to login page
      if (router) {
        router.push('/auth/login');
      }
    }
  }

  async function checkAuth() {
    try {
      loading.value = true;
      
      // If we have a token but no user, fetch the profile
      if (localStorage.getItem('token') && !user.value) {
        const profile = await authService.getProfile();
        user.value = profile;
        localStorage.setItem('user', JSON.stringify(profile));
      }
      
      return !!user.value;
    } catch (err) {
      user.value = null;
      localStorage.removeItem('user');
      localStorage.removeItem('token');
      return false;
    } finally {
      loading.value = false;
    }
  }

  function hasPermission(permission: string): boolean {
    if (!user.value) return false;
    if (user.value.permissions.includes('*')) return true;
    return user.value.permissions.includes(permission);
  }

  return {
    // State
    user,
    isAuthenticated,
    loading,
    error,
    
    // Getters
    userRole,
    userId,
    userName,
    
    // Actions
    login,
    register,
    forgotPassword,
    resetPassword,
    logout,
    checkAuth,
    hasPermission
  };
});

// This is a workaround for the circular dependency between router and store
let router: any = null;
export const setRouter = (r: any) => {
  router = r;
};
