import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import { useAuthStore } from '@/modules/auth/store/auth';
import { useToast } from 'primevue/usetoast';
import { useI18n } from 'vue-i18n';

class BaseService {
  protected api: AxiosInstance;
  protected moduleName: string;
  protected toast = useToast();
  protected i18n = useI18n();

  constructor(modulePath: string) {
    this.moduleName = modulePath;
    this.api = axios.create({
      baseURL: `/api/${modulePath}`,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor
    this.api.interceptors.request.use(
      (config) => {
        const authStore = useAuthStore();
        if (authStore.token) {
          config.headers.Authorization = `Bearer ${authStore.token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.api.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        this.handleError(error);
        return Promise.reject(error);
      }
    );
  }

  protected handleError(error: AxiosError) {
    let message = this.i18n.t('errors.generic');
    
    if (error.response) {
      // Server responded with a status other than 2xx
      switch (error.response.status) {
        case 400:
          message = this.i18n.t('errors.badRequest');
          break;
        case 401:
          message = this.i18n.t('errors.unauthorized');
          // Redirect to login or refresh token
          break;
        case 403:
          message = this.i18n.t('errors.forbidden');
          break;
        case 404:
          message = this.i18n.t('errors.notFound');
          break;
        case 500:
          message = this.i18n.t('errors.serverError');
          break;
      }
    } else if (error.request) {
      // Request was made but no response was received
      message = this.i18n.t('errors.networkError');
    }

    this.toast.add({
      severity: 'error',
      summary: this.i18n.t('errors.error'),
      detail: message,
      life: 5000,
    });
  }

  // CRUD operations
  protected async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.api.get<T>(url, config);
    return response.data;
  }

  protected async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.api.post<T>(url, data, config);
    return response.data;
  }

  protected async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.api.put<T>(url, data, config);
    return response.data;
  }

  protected async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.api.delete<T>(url, config);
    return response.data;
  }
}

export default BaseService;
