import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { api } from '@/utils/api';

export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
}

export interface Company {
  id: string;
  company_name: string;
  company_code: string;
  default_currency: string;
  default_language: string;
  timezone: string;
  fiscal_year_start: string;
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null);
  const currentCompany = ref<Company | null>(null);
  const token = ref<string | null>(localStorage.getItem('token'));
  const companies = ref<Company[]>([]);

  const isAuthenticated = computed(() => !!token.value && !!user.value);

  const login = async (email: string, password: string) => {
    try {
      const response = await api.post('/auth/login', { email, password });
      token.value = response.data.access_token;
      user.value = response.data.user;
      
      localStorage.setItem('token', token.value);
      
      // Load user companies
      await loadUserCompanies();
      
      return response.data;
    } catch (error) {
      throw error;
    }
  };

  const logout = () => {
    token.value = null;
    user.value = null;
    currentCompany.value = null;
    companies.value = [];
    localStorage.removeItem('token');
    localStorage.removeItem('currentCompany');
  };

  const loadUserCompanies = async () => {
    if (!user.value) return;
    
    try {
      const response = await api.get(`/company/user/${user.value.id}/companies`);
      companies.value = response.data;
      
      // Set current company from localStorage or first company
      const savedCompanyId = localStorage.getItem('currentCompany');
      if (savedCompanyId) {
        const savedCompany = companies.value.find(c => c.id === savedCompanyId);
        if (savedCompany) {
          currentCompany.value = savedCompany;
        }
      }
      
      if (!currentCompany.value && companies.value.length > 0) {
        currentCompany.value = companies.value[0];
        localStorage.setItem('currentCompany', currentCompany.value.id);
      }
    } catch (error) {
      console.error('Error loading user companies:', error);
    }
  };

  const setCurrentCompany = (company: Company) => {
    currentCompany.value = company;
    localStorage.setItem('currentCompany', company.id);
  };

  const initializeAuth = async () => {
    if (!token.value) return;
    
    try {
      const response = await api.get('/auth/me');
      user.value = response.data;
      await loadUserCompanies();
    } catch (error) {
      logout();
    }
  };

  return {
    user,
    currentCompany,
    token,
    companies,
    isAuthenticated,
    login,
    logout,
    loadUserCompanies,
    setCurrentCompany,
    initializeAuth
  };
});