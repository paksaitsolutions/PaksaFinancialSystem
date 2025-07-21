import { defineStore } from 'pinia';
import router from '@/router';
import { login as apiLogin } from '../api';

interface AuthUser {
  id: number;
  name: string;
  email: string;
  permissions?: string[];
}

interface AuthState {
  user: AuthUser | null;
  token: string | null;
}

type AuthGetters = {
  isAuthenticated: boolean;
  userPermissions: string[];
};

type AuthActions = {
  login(username: string, password: string): Promise<boolean>;
  logout(): void;
  hasAnyPermission(requiredPermissions: string[]): boolean;
  hasAllPermissions(requiredPermissions: string[]): boolean;
};

export const useAuthStore = defineStore<string, AuthState, AuthGetters, AuthActions>('auth', {
  state: (): AuthState => ({
    user: null,
    token: null
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    userPermissions: (state) => state.user?.permissions || []
  },

  actions: {
    async login(username: string, password: string): Promise<boolean> {
      try {
        const response = await apiLogin(username, password);
        this.user = response.user;
        this.token = response.token;
        router.push('/');
        return true;
      } catch (error) {
        console.error('Login failed:', error);
        return false;
      }
    },

    logout(): void {
      this.user = null;
      this.token = null;
      router.push('/auth/login');
    },

    hasAnyPermission(requiredPermissions: string[]): boolean {
      const permissions = this.user?.permissions;
      if (!permissions) return false;
      return requiredPermissions.some(permission => permissions.includes(permission));
    },
    
    hasAllPermissions(requiredPermissions: string[]): boolean {
      const permissions = this.user?.permissions;
      if (!permissions) return false;
      return requiredPermissions.every(permission => permissions.includes(permission));
    }
  },
  
  persist: {
    key: 'auth-store',
    storage: localStorage,
    paths: ['user', 'token']
  }
});
