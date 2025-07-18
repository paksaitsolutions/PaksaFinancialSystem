import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(null);
  const error = ref(null);
  const loading = ref(false);

  // Actions
  async function login(credentials) {
    try {
      loading.value = true;
      error.value = null;
      
      console.log('Login attempt with:', credentials.email);
      
      // Mock login for demo
      if (credentials.email === 'admin@example.com' && credentials.password === 'password') {
        const mockUser = {
          id: '1',
          email: credentials.email,
          name: 'Admin User',
          role: 'admin',
        };
        
        user.value = mockUser;
        localStorage.setItem('user', JSON.stringify(mockUser));
        localStorage.setItem('token', 'mock-jwt-token');
        
        return true;
      } else {
        error.value = 'Invalid email or password';
        return false;
      }
    } catch (err) {
      console.error('Login error:', err);
      error.value = err.message || 'Login failed';
      return false;
    } finally {
      loading.value = false;
    }
  }

  async function logout() {
    user.value = null;
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    return true;
  }

  async function checkAuth() {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      try {
        user.value = JSON.parse(storedUser);
      } catch (e) {
        localStorage.removeItem('user');
      }
    }
    return !!user.value;
  }

  return {
    user,
    error,
    loading,
    login,
    logout,
    checkAuth,
    get userName() { return user.value?.name || null; }
  };
});