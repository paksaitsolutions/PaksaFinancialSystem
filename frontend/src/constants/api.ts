/**
 * API configuration and endpoint constants
 */

// Base API URL - can be overridden by environment variables
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000/api';

/**
 * API endpoints for different modules
 */
export const API_ENDPOINTS = {
  // Authentication
  AUTH: {
    LOGIN: `${API_BASE_URL}/auth/login`,
    LOGOUT: `${API_BASE_URL}/auth/logout`,
    REFRESH_TOKEN: `${API_BASE_URL}/auth/refresh-token`,
    PROFILE: `${API_BASE_URL}/auth/profile`,
  },
  
  // General Ledger
  GL_ACCOUNTS: `${API_BASE_URL}/gl/accounts`,
  GL_JOURNALS: `${API_BASE_URL}/gl/journals`,
  GL_TRIAL_BALANCE: `${API_BASE_URL}/gl/trial-balance`,
  GL_FINANCIAL_STATEMENTS: `${API_BASE_URL}/gl/financial-statements`,
  
  // Accounts Payable
  AP_VENDORS: `${API_BASE_URL}/ap/vendors`,
  AP_BILLS: `${API_BASE_URL}/ap/bills`,
  AP_PAYMENTS: `${API_BASE_URL}/ap/payments`,
  
  // Accounts Receivable
  AR_CUSTOMERS: `${API_BASE_URL}/ar/customers`,
  AR_INVOICES: `${API_BASE_URL}/ar/invoices`,
  AR_RECEIPTS: `${API_BASE_URL}/ar/receipts`,
  
  // Payroll
  PAYROLL_EMPLOYEES: `${API_BASE_URL}/payroll/employees`,
  PAYROLL_RUNS: `${API_BASE_URL}/payroll/runs`,
  PAYROLL_ITEMS: `${API_BASE_URL}/payroll/items`,
  
  // Reports
  REPORTS: `${API_BASE_URL}/reports`,
  
  // System
  SYSTEM_CONFIG: `${API_BASE_URL}/system/config`,
  SYSTEM_LOGS: `${API_BASE_URL}/system/logs`,
} as const;

/**
 * Default API request configuration
 */
export const API_CONFIG = {
  TIMEOUT: 30000, // 30 seconds
  MAX_RETRIES: 3,
  RETRY_DELAY: 1000, // 1 second
  CACHE_TTL: 5 * 60 * 1000, // 5 minutes
} as const;

/**
 * HTTP status codes
 */
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  ACCEPTED: 202,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  METHOD_NOT_ALLOWED: 405,
  CONFLICT: 409,
  UNPROCESSABLE_ENTITY: 422,
  TOO_MANY_REQUESTS: 429,
  INTERNAL_SERVER_ERROR: 500,
  SERVICE_UNAVAILABLE: 503,
} as const;

/**
 * Common HTTP headers
 */
export const HTTP_HEADERS = {
  CONTENT_TYPE: 'Content-Type',
  AUTHORIZATION: 'Authorization',
  ACCEPT: 'Accept',
  CACHE_CONTROL: 'Cache-Control',
  X_REQUESTED_WITH: 'X-Requested-With',
  X_CSRF_TOKEN: 'X-CSRF-TOKEN',
} as const;

export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE' | 'HEAD' | 'OPTIONS';
