import 'vue';
import { Store } from 'pinia';

/**
 * Global type declarations for the Paksa Financial System
 */

declare global {
  /**
   * Type for API response structure
   */
  interface ApiResponse<T = any> {
    data: T;
    message?: string;
    statusCode: number;
    success: boolean;
    timestamp: string;
    path?: string;
  }

  /**
   * Type for paginated API responses
   */
  interface PaginatedResponse<T> {
    items: T[];
    total: number;
    page: number;
    pageSize: number;
    totalPages: number;
    hasNext: boolean;
    hasPrevious: boolean;
  }

  /**
   * Type for pagination parameters
   */
  interface PaginationParams {
    page?: number;
    pageSize?: number;
    sortBy?: string;
    sortOrder?: 'asc' | 'desc';
    [key: string]: any; // For additional query parameters
  }

  /**
   * Type for error response from API
   */
  interface ApiError {
    message: string;
    statusCode: number;
    error?: string;
    timestamp?: string;
    path?: string;
    details?: Record<string, string[]>;
  }

  /**
   * Type for form validation error
   */
  interface ValidationError {
    field: string;
    message: string;
  }

  /**
   * Type for user authentication data
   */
  interface AuthUser {
    id: string | number;
    email: string;
    firstName?: string;
    lastName?: string;
    fullName: string;
    roles: string[];
    permissions: string[];
    avatar?: string;
  }

  /**
   * Type for application settings
   */
  interface AppSettings {
    theme: 'light' | 'dark' | 'system';
    locale: string;
    currency: string;
    timezone: string;
    dateFormat: string;
    timeFormat: string;
    notifications: {
      email: boolean;
      push: boolean;
      sound: boolean;
    };
  }

  /**
   * Type for breadcrumb navigation item
   */
  interface BreadcrumbItem {
    title: string;
    to?: string | Record<string, any>;
    disabled?: boolean;
  }

  /**
   * Extend Vue's ComponentCustomProperties to include global properties
   */
  interface ComponentCustomProperties {
    $filters: {
      formatDate: (date: string | Date, format?: string) => string;
      formatCurrency: (value: number, currency?: string) => string;
      truncate: (text: string, length: number, suffix?: string) => string;
    };
  }
}

/**
 * Declare module for environment variables
 */
declare module '*.env' {
  export const VITE_API_BASE_URL: string;
  export const VITE_APP_NAME: string;
  export const VITE_APP_VERSION: string;
  export const VITE_APP_ENV: 'development' | 'staging' | 'production';
  export const VITE_APP_DEBUG: boolean;
  export const VITE_APP_DEFAULT_LOCALE: string;
  export const VITE_APP_FALLBACK_LOCALE: string;
  export const VITE_APP_SUPPORTED_LOCALES: string;
}

/**
 * Declare module for Vue files
 */
declare module '*.vue' {
  import type { DefineComponent } from 'vue';
  const component: DefineComponent<{}, {}, any>;
  export default component;
}

/**
 * Declare module for image files
 */
declare module '*.png';
declare module '*.jpg';
declare module '*.jpeg';
declare module '*.gif';
declare module '*.svg';
declare module '*.webp';

/**
 * Declare module for CSS/SCSS modules
 */
declare module '*.module.css' {
  const classes: { readonly [key: string]: string };
  export default classes;
}

declare module '*.module.scss' {
  const classes: { readonly [key: string]: string };
  export default classes;
}

/**
 * Type for Pinia store with state, getters, and actions
 */
type PiniaStore<Id extends string, S, G, A> = Store<Id, S, G, A>;

/**
 * Type for defining Pinia store with better type inference
 */
type DefineStoreOptions<Id extends string, S, G, A> = {
  id: Id;
  state: () => S;
  getters: G;
  actions: A;
  persist?: boolean | {
    key?: string;
    storage?: 'local' | 'session';
    paths?: string[];
  };
};

/**
 * Type for defining Pinia store module
 */
type PiniaStoreModule<Id extends string, S, G, A> = {
  useStore: () => PiniaStore<Id, S, G, A>;
  [key: string]: any;
};

/**
 * Type for API service methods
 */
type ApiServiceMethods = {
  [key: string]: (...args: any[]) => Promise<any>;
};

/**
 * Type for API service with typed methods
 */
type ApiService<T extends ApiServiceMethods> = T & {
  baseUrl: string;
  defaultParams?: Record<string, any>;
  withAuth?: boolean;
};

export {};
