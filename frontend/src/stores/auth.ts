import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

interface User {
  id: string;
  email: string;
  name: string;
  role: string;
  permissions: string[];
}

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
  async function login(credentials: { email: string; password: string; rememberMe?: boolean }) {
    try {
      loading.value = true;
      error.value = null;
      
      // Mock login for demo
      if (credentials.email === 'admin@example.com' && credentials.password === 'password') {
        const mockUser = {
          id: '1',
          email: credentials.email,
          name: 'Admin User',
          role: 'admin',
          permissions: ['*']
        };
        
        user.value = mockUser;
        
        // Store user data based on remember me preference
        if (credentials.rememberMe) {
          localStorage.setItem('user', JSON.stringify(mockUser));
          localStorage.setItem('token', 'mock-jwt-token');
        } else {
          sessionStorage.setItem('user', JSON.stringify(mockUser));
          sessionStorage.setItem('token', 'mock-jwt-token');
        }
        
        return true;
      } else {
        error.value = 'Invalid email or password';
        return false;
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Login failed';
      return false;
    } finally {
      loading.value = false;
    }
  }

  async function logout() {
    try {
      loading.value = true;
      // Clear user data from both storage types
      user.value = null;
      localStorage.removeItem('user');
      localStorage.removeItem('token');
      sessionStorage.removeItem('user');
      sessionStorage.removeItem('token');
      return true;
    } catch (err) {
      console.error('Logout error:', err);
      return false;
    } finally {
      loading.value = false;
    }
  }

  async function checkAuth() {
    try {
      loading.value = true;
      
      // If we have a token but no user, fetch the profile
      const token = localStorage.getItem('token') || sessionStorage.getItem('token');
      if (token && !user.value) {
        // In a real app, we would fetch the user profile from the API
        // For demo, we'll just use the stored user
        const storedUser = localStorage.getItem('user') || sessionStorage.getItem('user');
        if (storedUser) {
          user.value = JSON.parse(storedUser);
        }
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
    logout,
    checkAuth,
    hasPermission
  };
});