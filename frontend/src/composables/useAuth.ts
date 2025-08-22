import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useSnackbar } from './useSnackbar';
import type { LoginCredentials, RegistrationData } from '@/types/auth';

export function useAuth() {
  const router = useRouter();
  const authStore = useAuthStore();
  const snackbar = useSnackbar();

  const isAuthenticated = computed(() => authStore.isAuthenticated);
  const user = computed(() => authStore.user);
  const loading = computed(() => authStore.loading);
  const error = computed(() => authStore.error);

  const login = async (credentials: LoginCredentials) => {
    try {
      const success = await authStore.login(credentials);
      
      if (success) {
        snackbar.success('Login successful');
        return true;
      } else {
        snackbar.error(authStore.error || 'Login failed');
        return false;
      }
    } catch (err) {
      console.error('Login error:', err);
      snackbar.error('An unexpected error occurred');
      return false;
    }
  };

  const register = async (userData: RegistrationData) => {
    try {
      const success = await authStore.register(userData);
      
      if (success) {
        snackbar.success('Registration successful');
        return true;
      } else {
        snackbar.error(authStore.error || 'Registration failed');
        return false;
      }
    } catch (err) {
      console.error('Registration error:', err);
      snackbar.error('An unexpected error occurred');
      return false;
    }
  };

  const forgotPassword = async (email: string) => {
    try {
      const success = await authStore.forgotPassword(email);
      
      if (success) {
        snackbar.success('Password reset instructions sent to your email');
        return true;
      } else {
        snackbar.error(authStore.error || 'Failed to send reset instructions');
        return false;
      }
    } catch (err) {
      console.error('Forgot password error:', err);
      snackbar.error('An unexpected error occurred');
      return false;
    }
  };

  const resetPassword = async (token: string, password: string) => {
    try {
      const success = await authStore.resetPassword(token, password);
      
      if (success) {
        snackbar.success('Password reset successful');
        return true;
      } else {
        snackbar.error(authStore.error || 'Password reset failed');
        return false;
      }
    } catch (err) {
      console.error('Reset password error:', err);
      snackbar.error('An unexpected error occurred');
      return false;
    }
  };

  const logout = async () => {
    try {
      await authStore.logout();
      snackbar.info('You have been logged out');
      router.push('/auth/login');
    } catch (err) {
      console.error('Logout error:', err);
      snackbar.error('Logout failed');
    }
  };

  const checkAuth = async () => {
    try {
      return await authStore.checkAuth();
    } catch (err) {
      console.error('Auth check error:', err);
      return false;
    }
  };

  const hasPermission = (permission: string) => {
    return authStore.hasPermission(permission);
  };

  return {
    isAuthenticated,
    user,
    loading,
    error,
    login,
    register,
    forgotPassword,
    resetPassword,
    logout,
    checkAuth,
    hasPermission
  };
}