/**
 * Application-wide configuration constants
 */

/**
 * Application metadata
 */
export const APP_METADATA = {
  NAME: 'Paksa Financial System',
  VERSION: '1.0.0',
  DESCRIPTION: 'Comprehensive financial management solution for modern businesses',
  COPYRIGHT: `© ${new Date().getFullYear()} Paksa IT Solutions. All rights reserved.`,
  SUPPORT_EMAIL: 'support@paksa.com.pk',
  COMPANY_WEBSITE: 'https://www.paksa.com.pk',
} as const;

/**
 * Feature flags
 */
export const FEATURE_FLAGS = {
  ENABLE_ANALYTICS: import.meta.env.VITE_ENABLE_ANALYTICS === 'true',
  ENABLE_DEBUG: import.meta.env.DEV,
  ENABLE_MAINTENANCE_MODE: import.meta.env.VITE_MAINTENANCE_MODE === 'true',
} as const;

/**
 * Application settings
 */
export const APP_SETTINGS = {
  // UI Settings
  DEFAULT_THEME: 'light', // light | dark | system
  DEFAULT_LANGUAGE: 'en',
  ITEMS_PER_PAGE: 25,
  MAX_UPLOAD_SIZE: 10 * 1024 * 1024, // 10MB
  
  // Session & Security
  SESSION_TIMEOUT: 30 * 60 * 1000, // 30 minutes
  TOKEN_REFRESH_INTERVAL: 15 * 60 * 1000, // 15 minutes
  PASSWORD_MIN_LENGTH: 8,
  PASSWORD_MAX_ATTEMPTS: 5,
  PASSWORD_LOCKOUT_TIME: 15 * 60 * 1000, // 15 minutes
  
  // Notifications
  NOTIFICATION_TIMEOUT: 5000, // 5 seconds
  MAX_NOTIFICATIONS: 5,
  
  // Search & Filter
  DEBOUNCE_DELAY: 300, // ms
  MIN_SEARCH_LENGTH: 2,
  MAX_SEARCH_RESULTS: 50,
  
  // Export & Reports
  MAX_EXPORT_ROWS: 10000,
  EXPORT_CHUNK_SIZE: 1000,
  
  // Cache
  CACHE_PREFIX: 'paksa_',
  CACHE_TTL: 24 * 60 * 60 * 1000, // 24 hours
} as const;

/**
 * Date & Time formats
 */
export const DATE_TIME_FORMATS = {
  DATE: 'yyyy-MM-dd',
  DATE_TIME: 'yyyy-MM-dd HH:mm',
  DATE_TIME_SECONDS: 'yyyy-MM-dd HH:mm:ss',
  TIME: 'HH:mm',
  TIME_SECONDS: 'HH:mm:ss',
  MONTH_YEAR: 'MMMM yyyy',
  SHORT_DATE: 'MM/dd/yyyy',
  ISO_DATE: 'yyyy-MM-dd',
  ISO_DATE_TIME: "yyyy-MM-dd'T'HH:mm:ss.SSSxxx",
  DISPLAY_DATE: 'PP', // Localized date format
  DISPLAY_DATE_TIME: 'PPpp', // Localized date and time format
} as const;

/**
 * Application routes configuration
 */
export const ROUTE_CONFIG = {
  // Authentication
  LOGIN: '/auth/login',
  LOGOUT: '/auth/logout',
  FORGOT_PASSWORD: '/auth/forgot-password',
  RESET_PASSWORD: '/auth/reset-password',
  
  // Dashboard
  DASHBOARD: '/dashboard',
  
  // Modules
  GENERAL_LEDGER: '/gl',
  ACCOUNTS_PAYABLE: '/ap',
  ACCOUNTS_RECEIVABLE: '/ar',
  PAYROLL: '/payroll',
  INVENTORY: '/inventory',
  
  // Settings
  SETTINGS: '/settings',
  USER_PROFILE: '/settings/profile',
  USER_PREFERENCES: '/settings/preferences',
  
  // Error pages
  NOT_FOUND: '/404',
  UNAUTHORIZED: '/401',
  SERVER_ERROR: '/500',
  MAINTENANCE: '/maintenance',
} as const;

/**
 * Supported locales
 */
export const SUPPORTED_LOCALES = [
  { code: 'en', name: 'English', flag: '🇬🇧' },
  { code: 'ur', name: 'اردو', flag: '🇵🇰' },
  { code: 'ar', name: 'العربية', flag: '🇸🇦', rtl: true },
] as const;

/**
 * Currency configuration
 */
export const CURRENCY = {
  DEFAULT: 'PKR',
  SYMBOL: '₨',
  DECIMALS: 2,
  THOUSAND_SEPARATOR: ',',
  DECIMAL_SEPARATOR: '.',
  SYMBOL_POSITION: 'before', // 'before' or 'after'
  DISPLAY_FORMAT: '{symbol}{amount} {code}', // {symbol} {amount} {code} => $ 100.00 USD
} as const;

/**
 * Application breakpoints (in pixels)
 */
export const BREAKPOINTS = {
  XS: 0,
  SM: 576,
  MD: 768,
  LG: 992,
  XL: 1200,
  XXL: 1400,
} as const;
