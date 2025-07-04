import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'primevue/usetoast';
import { useI18n } from 'vue-i18n';
import axios from 'axios';

type User = {
  id: string;
  email: string;
  name: string;
  role: string;
  permissions: string[];
  avatar?: string;
};

type LoginCredentials = {
  email: string;
  password: string;
  remember_me?: boolean;
};

type ResetPasswordData = {
  token: string;
  password: string;
  password_confirmation: string;
};

export const useAuthStore = defineStore('auth', () => {
  const router = useRouter();
  const toast = useToast();
  const { t } = useI18n();
  
  // State
  const user = ref<User | null>(null);
  const token = ref<string | null>(localStorage.getItem('auth_token'));
  const isAuthenticated = ref(!!token.value);
  const loading = ref(false);
  const permissions = ref<string[]>([]);
  
  // Getters
  const isAdmin = computed(() => user.value?.role === 'admin');
  const userInitials = computed(() => {
    if (!user.value?.name) return '';
    return user.value.name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase();
  });
  
  // Actions
  async function login(credentials: LoginCredentials) {
    try {
      loading.value = true;
      const response = await axios.post('/api/auth/login', credentials);
      
      // Set token and user data
      const { access_token, user: userData } = response.data.data;
      setAuthData(access_token, userData);
      
      // Show success message
      toast.add({
        severity: 'success',
        summary: t('auth.login.success'),
        detail: t('auth.login.welcome', { name: userData.name }),
        life: 3000,
      });
      
      // Redirect to dashboard or intended URL
      const redirect = router.currentRoute.value.query.redirect;
      router.push(redirect ? String(redirect) : { name: 'dashboard' });
      
      return true;
    } catch (error: any) {
      handleAuthError(error, 'login');
      return false;
    } finally {
      loading.value = false;
    }
  }
  
  async function logout() {
    try {
      await axios.post('/api/auth/logout', {}, {
        headers: { Authorization: `Bearer ${token.value}` }
      });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear auth data regardless of API call result
      clearAuthData();
      router.push({ name: 'login' });
    }
  }
  
  async function forgotPassword(email: string) {
    try {
      loading.value = true;
      await axios.post('/api/auth/forgot-password', { email });
      
      toast.add({
        severity: 'success',
        summary: t('auth.resetPassword.emailSent'),
        detail: t('auth.resetPassword.checkEmail'),
        life: 5000,
      });
      
      return true;
    } catch (error: any) {
      handleAuthError(error, 'forgotPassword');
      return false;
    } finally {
      loading.value = false;
    }
  }
  
  async function resetPassword(data: ResetPasswordData) {
    try {
      loading.value = true;
      await axios.post('/api/auth/reset-password', data);
      
      toast.add({
        severity: 'success',
        summary: t('auth.resetPassword.success'),
        detail: t('auth.resetPassword.loginWithNewPassword'),
        life: 5000,
      });
      
      router.push({ name: 'login' });
      return true;
    } catch (error: any) {
      handleAuthError(error, 'resetPassword');
      return false;
    } finally {
      loading.value = false;
    }
  }
  
  async function fetchUser() {
    try {
      loading.value = true;
      const response = await axios.get('/api/auth/me', {
        headers: { Authorization: `Bearer ${token.value}` }
      });
      
      user.value = response.data.data;
      permissions.value = user.value?.permissions || [];
      return user.value;
    } catch (error) {
      console.error('Failed to fetch user:', error);
      clearAuthData();
      throw error;
    } finally {
      loading.value = false;
    }
  }
  
  function initialize() {
    if (token.value) {
      // Set axios default auth header
      axios.defaults.headers.common['Authorization'] = `Bearer ${token.value}`;
      
      // Fetch user data if authenticated
      if (isAuthenticated.value) {
        fetchUser().catch(console.error);
      }
    }
  }
  
  // Helper methods
  function setAuthData(authToken: string, userData: User) {
    token.value = authToken;
    user.value = userData;
    permissions.value = userData.permissions || [];
    isAuthenticated.value = true;
    
    // Store token in localStorage
    localStorage.setItem('auth_token', authToken);
    
    // Set default axios auth header
    axios.defaults.headers.common['Authorization'] = `Bearer ${authToken}`;
  }
  
  function clearAuthData() {
    token.value = null;
    user.value = null;
    permissions.value = [];
    isAuthenticated.value = false;
    
    // Remove token from localStorage
    localStorage.removeItem('auth_token');
    
    // Remove axios auth header
    delete axios.defaults.headers.common['Authorization'];
  }
  
  function hasPermission(permission: string): boolean {
    if (!permissions.value.length) return false;
    return permissions.value.includes(permission) || isAdmin.value;
  }
  
  function hasAnyPermission(permissionsList: string[]): boolean {
    if (!permissions.value.length) return false;
    if (isAdmin.value) return true;
    return permissionsList.some(permission => permissions.value.includes(permission));
  }
  
  function handleAuthError(error: any, context: string) {
    console.error(`${context} error:`, error);
    
    let errorMessage = t('common.errors.unknown');
    
    if (error.response) {
      const { status, data } = error.response;
      
      if (status === 422 && data.errors) {
        // Handle validation errors
        errorMessage = Object.values(data.errors)
          .flat()
          .join(' ');
      } else if (data.message) {
        errorMessage = data.message;
      } else if (status === 401) {
        errorMessage = t('auth.errors.unauthorized');
        clearAuthData();
      } else if (status === 403) {
        errorMessage = t('auth.errors.forbidden');
      } else if (status === 404) {
        errorMessage = t('common.errors.notFound');
      } else if (status >= 500) {
        errorMessage = t('common.errors.serverError');
      }
    } else if (error.request) {
      errorMessage = t('common.errors.networkError');
    }
    
    toast.add({
      severity: 'error',
      summary: t('common.errors.error'),
      detail: errorMessage,
      life: 5000,
    });
    
    return errorMessage;
  }
  
  return {
    // State
    user,
    token,
    isAuthenticated,
    loading,
    permissions,
    
    // Getters
    isAdmin,
    userInitials,
    
    // Actions
    login,
    logout,
    forgotPassword,
    resetPassword,
    fetchUser,
    initialize,
    hasPermission,
    hasAnyPermission,
  };
});
