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
  const token = ref<string | null>(localStorage.getItem('token') || sessionStorage.getItem('token'));
  const companies = ref<Company[]>([]);

  const isAuthenticated = computed(() => !!token.value && !!user.value);

  const login = async (credentials: { email: string; password: string; remember_me?: boolean }) => {
    try {
      console.log('Attempting login with:', { email: credentials.email, remember_me: credentials.remember_me });
      console.log('API base URL:', import.meta.env.VITE_API_BASE_URL);
      
      const response = await api.post('/auth/login', {
        email: credentials.email,
        password: credentials.password,
        remember_me: credentials.remember_me
      });
      
      console.log('Login response:', response);
      
      // The response should already be the data due to the response interceptor
      const responseData = response;
      
      if (!responseData || !responseData.access_token) {
        console.error('Invalid response structure:', responseData);
        throw new Error('Invalid response from server');
      }
      
      const { access_token, user: userData } = responseData;
      
      token.value = access_token;
      user.value = userData;
      
      if (credentials.remember_me) {
        localStorage.setItem('token', token.value);
      } else {
        sessionStorage.setItem('token', token.value);
      }
      
      console.log('Login successful, token stored');
      
      // Load user companies after successful login
      try {
        await loadUserCompanies();
      } catch (companyError) {
        console.warn('Failed to load companies:', companyError);
      }
      
      return { access_token, user: userData };
    } catch (error: any) {
      console.error('Login error details:', {
        message: error.message,
        response: error.response,
        request: error.request,
        status: error.response?.status,
        data: error.response?.data
      });
      
      // Handle different types of errors
      if (error.response) {
        // Server responded with error status
        const status = error.response.status;
        const message = error.response.data?.detail || error.response.data?.message;
        
        if (status === 401) {
          throw new Error('Invalid email or password');
        } else if (status === 422) {
          throw new Error('Please check your email and password format');
        } else if (status >= 500) {
          throw new Error('Server error. Please try again later');
        } else {
          throw new Error(message || 'Login failed');
        }
      } else if (error.request) {
        // Network error
        throw new Error('Network error. Please check your connection');
      } else {
        // Other error
        throw new Error(error.message || 'Login failed');
      }
    }
  };

  const logout = () => {
    token.value = null;
    user.value = null;
    currentCompany.value = null;
    companies.value = [];
    localStorage.removeItem('token');
    sessionStorage.removeItem('token');
    localStorage.removeItem('currentCompany');
  };

  const loadUserCompanies = async () => {
    if (!user.value) return;
    
    try {
      const response = await api.get<Company[]>(`/company/user/${user.value.id}/companies`);
      companies.value = response || [];
      
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
      const response = await api.get<User>('/auth/me');
      user.value = response;
      await loadUserCompanies();
    } catch (error: any) {
      console.error('Auth initialization error:', error);
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