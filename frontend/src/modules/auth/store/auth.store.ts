import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { api } from '../../../services/api';
import type { User, LoginCredentials } from '@/types/auth';
import { useSnackbar } from '../../../shared/composables/useSnackbar';

interface AuthState {
  user: User | null;
  token: string | null;
  loading: boolean;
  error: string | null;
  isInitialized: boolean;
}

interface AuthResponse {
  token: string;
  user: User;
}

export const useAuthStore = defineStore('auth', () => {
  const router = useRouter();
  const snackbar = useSnackbar();
  
  // State
  const user = ref<User | null>(null);
  const token = ref<string | null>(localStorage.getItem('auth_token'));
  const loading = ref(false);
  const error = ref<string | null>(null);
  const isInitialized = ref(false);

  // Getters
  const isAuthenticated = computed(() => !!token.value && !!user.value);
  const userRole = computed(() => user.value?.role || null);
  const userPermissions = computed(() => user.value?.permissions || []);

  // Actions
  const setAuth = (authData: AuthResponse) => {
    if (!authData?.token || !authData?.user) {
      throw new Error('Invalid authentication data');
    }
    
    token.value = authData.token;
    user.value = authData.user;
    
    try {
      // Store token in localStorage
      localStorage.setItem('token', authData.token);
      localStorage.setItem('user', JSON.stringify(authData.user));
      
      // Set auth header for API requests
      api.defaults.headers.common['Authorization'] = `Bearer ${authData.token}`;
    } catch (error) {
      console.error('Error storing auth data:', error);
      throw new Error('Failed to store authentication data');
    }
  };

  const clearAuth = () => {
    token.value = null;
    user.value = null;
    
    try {
      // Remove auth data from localStorage
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      
      // Remove auth header
      delete api.defaults.headers.common['Authorization'];
    } catch (error) {
      console.error('Error clearing auth data:', error);
      // Continue even if clearing storage fails
    }
  };

  const login = async (credentials: LoginCredentials): Promise<boolean> => {
    try {
      loading.value = true;
      error.value = null;
      
      const response = await api.post<AuthResponse>('/auth/login', credentials);
      setAuth(response.data);
      
      snackbar.showSuccess('Login successful');
      return true;
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || 'Login failed';
      error.value = errorMessage;
      snackbar.showError(errorMessage);
      return false;
    } finally {
      loading.value = false;
    }
  };

  const register = async (userData: any): Promise<boolean> => {
    try {
      loading.value = true;
      error.value = null;
      
      const response = await api.post<AuthResponse>('/auth/register', userData);
      setAuth(response.data);
      
      snackbar.showSuccess('Registration successful');
      return true;
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || 'Registration failed';
      error.value = errorMessage;
      snackbar.showError(errorMessage);
      return false;
    } finally {
      loading.value = false;
    }
  };

  const logout = () => {
    clearAuth();
    router.push('/auth/login');
  };

  const checkAuth = async (): Promise<boolean> => {
    if (!token.value) return false;
    
    try {
      // Try to get user data from localStorage first
      const storedUser = localStorage.getItem('user');
      if (storedUser) {
        try {
          user.value = JSON.parse(storedUser);
          // Validate the stored user data
          if (user.value?.id && user.value?.email) {
            // Verify with the server in the background
            api.get<User>('/auth/me')
              .then(response => {
                user.value = response.data;
                localStorage.setItem('user', JSON.stringify(response.data));
              })
              .catch(() => {
                // If verification fails, the token might be expired
                clearAuth();
              });
            return true;
          }
        } catch (e) {
          // Invalid stored user data, clear it
          console.error('Invalid stored user data:', e);
          localStorage.removeItem('user');
        }
      }
      
      // If no valid stored user, fetch from server
      const response = await api.get<User>('/auth/me');
      user.value = response.data;
      localStorage.setItem('user', JSON.stringify(response.data));
      return true;
    } catch (err) {
      console.error('Error checking auth:', err);
      clearAuth();
      return false;
    }
  };

  const initialize = async () => {
    if (isInitialized.value) return;
    
    try {
      // Check for existing token in localStorage
      const storedToken = localStorage.getItem('token');
      if (storedToken) {
        token.value = storedToken;
        // Set auth header for API requests
        api.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`;
        
        // Verify token and get user data
        const isAuthenticated = await checkAuth();
        if (!isAuthenticated) {
          // Clear invalid token
          clearAuth();
        }
      }
    } catch (error) {
      console.error('Error initializing auth:', error);
      // Clear any invalid auth state
      clearAuth();
    } finally {
      isInitialized.value = true;
    }
  };

  // Check permissions
  const hasPermission = (permission: string): boolean => {
    if (!user.value) return false;
    return user.value.permissions.includes(permission);
  };

  const hasAnyPermission = (permissions: string[]): boolean => {
    if (!user.value) return false;
    return permissions.some(permission => user.value?.permissions.includes(permission));
  };

  return {
    // State
    user,
    token,
    loading: computed(() => loading.value),
    error: computed(() => error.value),
    isAuthenticated,
    isInitialized: computed(() => isInitialized.value),
    userRole: computed(() => user.value?.role || null),
    userPermissions,
    
    // Actions
    setAuth,
    clearAuth,
    login,
    logout,
    checkAuth,
    initialize,
    hasPermission,
    hasAnyPermission
  };
}, {
  persist: {
    paths: ['user', 'token'],
    key: 'auth',
  },
});
