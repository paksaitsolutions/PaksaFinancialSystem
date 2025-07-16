import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { User } from '@/types/auth';

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null);
  const isAuthenticated = computed(() => !!user.value);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Getters
  const userRole = computed(() => user.value?.role || null);
  const userId = computed(() => user.value?.id || null);
  const userName = computed(() => user.value?.name || null);

  // Actions
  async function login(credentials: { email: string; password: string }) {
    try {
      loading.value = true;
      error.value = null;
      
      // TODO: Replace with actual API call
      // const response = await api.post('/auth/login', credentials);
      // user.value = response.data.user;
      
      // Mock response for now
      user.value = {
        id: '1',
        email: credentials.email,
        name: 'Demo User',
        role: 'admin',
        permissions: ['*']
      };
      
      return true;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Login failed';
      return false;
    } finally {
      loading.value = false;
    }
  }

  async function logout() {
    try {
      // TODO: Call logout API
      // await api.post('/auth/logout');
    } finally {
      user.value = null;
      // Redirect to login page
      if (router) {
        router.push('/login');
      }
    }
  }

  async function checkAuth() {
    try {
      loading.value = true;
      // TODO: Verify token/refresh session
      // const response = await api.get('/auth/me');
      // user.value = response.data.user;
      return !!user.value;
    } catch (err) {
      user.value = null;
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
