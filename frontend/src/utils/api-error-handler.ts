/**
 * Centralized API Error Handler
 * Maps backend error codes to user-friendly messages
 * Integrates with backend error_handler.py error codes
 */

import type { AxiosError } from 'axios'

// Backend error code types (from app/core/error_handler.py)
export type ErrorCode =
  // Authentication & Authorization (1xxx)
  | 'AUTH_001' | 'AUTH_002' | 'AUTH_003' | 'AUTH_004' | 'AUTH_005' | 'AUTH_006'
  // Validation Errors (2xxx)
  | 'VAL_001' | 'VAL_002' | 'VAL_003' | 'VAL_004'
  // Database Errors (3xxx)
  | 'DB_001' | 'DB_002' | 'DB_003' | 'DB_004' | 'DB_005'
  // Business Logic Errors (4xxx)
  | 'BIZ_001' | 'BIZ_002' | 'BIZ_003' | 'BIZ_004' | 'BIZ_005'
  // Resource Errors (5xxx)
  | 'RES_001' | 'RES_002' | 'RES_003'
  // System Errors (9xxx)
  | 'SYS_001' | 'SYS_002' | 'SYS_003'

export interface ApiErrorResponse {
  success: false
  error: {
    code: ErrorCode
    message: string
    details?: any
  }
}

export interface ParsedError {
  code: ErrorCode | 'UNKNOWN'
  message: string
  userMessage: string
  details?: any
  statusCode?: number
}

// User-friendly error messages mapped to backend error codes
const ERROR_MESSAGES: Record<ErrorCode | 'UNKNOWN', string> = {
  // Authentication & Authorization
  'AUTH_001': 'Invalid email or password. Please try again.',
  'AUTH_002': 'Your session has expired. Please log in again.',
  'AUTH_003': 'Invalid authentication token. Please log in again.',
  'AUTH_004': 'You do not have permission to perform this action.',
  'AUTH_005': 'Your account has been disabled. Please contact support.',
  'AUTH_006': 'Multi-factor authentication is required.',
  
  // Validation Errors
  'VAL_001': 'Please check the form and correct any errors.',
  'VAL_002': 'Required field is missing.',
  'VAL_003': 'Invalid format. Please check your input.',
  'VAL_004': 'Value is out of acceptable range.',
  
  // Database Errors
  'DB_001': 'Unable to connect to database. Please try again later.',
  'DB_002': 'The requested record was not found.',
  'DB_003': 'This record already exists.',
  'DB_004': 'Cannot delete this record as it is referenced by other data.',
  'DB_005': 'Database integrity error. Please contact support.',
  
  // Business Logic Errors
  'BIZ_001': 'This operation is not allowed.',
  'BIZ_002': 'Operation not permitted at this time.',
  'BIZ_003': 'Insufficient balance to complete this transaction.',
  'BIZ_004': 'This period is closed and cannot be modified.',
  'BIZ_005': 'This transaction has already been processed.',
  
  // Resource Errors
  'RES_001': 'The requested resource was not found.',
  'RES_002': 'This resource already exists.',
  'RES_003': 'This resource is currently locked by another user.',
  
  // System Errors
  'SYS_001': 'An unexpected error occurred. Please try again.',
  'SYS_002': 'Service is temporarily unavailable. Please try again later.',
  'SYS_003': 'External service error. Please try again later.',
  
  // Unknown
  'UNKNOWN': 'An unexpected error occurred. Please try again.'
}

/**
 * Parse API error response
 */
export function parseApiError(error: any): ParsedError {
  // Handle Axios errors
  if (error.response) {
    const { status, data } = error.response as { status: number; data: any }
    
    // Check if response matches our standardized error format
    if (data && !data.success && data.error) {
      const apiError = data as ApiErrorResponse
      return {
        code: apiError.error.code,
        message: apiError.error.message,
        userMessage: ERROR_MESSAGES[apiError.error.code] || ERROR_MESSAGES.UNKNOWN,
        details: apiError.error.details,
        statusCode: status
      }
    }
    
    // Handle legacy error formats
    if (data?.message) {
      return {
        code: 'UNKNOWN',
        message: data.message,
        userMessage: data.message,
        details: data.details,
        statusCode: status
      }
    }
    
    // Map HTTP status codes to error codes
    const statusCodeMap: Record<number, ErrorCode> = {
      401: 'AUTH_003',
      403: 'AUTH_004',
      404: 'RES_001',
      409: 'RES_002',
      422: 'VAL_001',
      500: 'SYS_001',
      503: 'SYS_002'
    }
    
    const code = statusCodeMap[status] || 'UNKNOWN'
    return {
      code,
      message: data?.detail || data?.message || 'Error occurred',
      userMessage: ERROR_MESSAGES[code],
      statusCode: status
    }
  }
  
  // Handle network errors
  if (error.message === 'Network Error') {
    return {
      code: 'SYS_002',
      message: 'Network Error',
      userMessage: 'Unable to connect to server. Please check your internet connection.'
    }
  }
  
  // Handle timeout errors
  if (error.code === 'ECONNABORTED') {
    return {
      code: 'SYS_002',
      message: 'Request Timeout',
      userMessage: 'Request timed out. Please try again.'
    }
  }
  
  // Fallback
  return {
    code: 'UNKNOWN',
    message: error.message || 'Unknown error',
    userMessage: ERROR_MESSAGES.UNKNOWN
  }
}

/**
 * Get user-friendly error message
 */
export function getUserMessage(error: any): string {
  const parsed = parseApiError(error)
  return parsed.userMessage
}

/**
 * Check if error is authentication related
 */
export function isAuthError(error: any): boolean {
  const parsed = parseApiError(error)
  return parsed.code.startsWith('AUTH_')
}

/**
 * Check if error is validation related
 */
export function isValidationError(error: any): boolean {
  const parsed = parseApiError(error)
  return parsed.code.startsWith('VAL_')
}

/**
 * Check if error is business logic related
 */
export function isBusinessError(error: any): boolean {
  const parsed = parseApiError(error)
  return parsed.code.startsWith('BIZ_')
}

/**
 * Handle API error globally (for use in interceptors)
 */
export function handleApiError(error: any): ParsedError {
  const parsed = parseApiError(error)
  
  // Log error for debugging (only in development)
  if (import.meta.env.DEV) {
    console.error('[API Error]', {
      code: parsed.code,
      message: parsed.message,
      details: parsed.details,
      statusCode: parsed.statusCode
    })
  }
  
  // Handle authentication errors globally
  if (isAuthError(error) && ['AUTH_002', 'AUTH_003'].includes(parsed.code)) {
    // Clear auth data
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    
    // Redirect to login (only if not already on login page)
    if (!window.location.pathname.includes('/auth/login')) {
      window.location.href = '/auth/login'
    }
  }
  
  return parsed
}

/**
 * Format validation errors for form display
 */
export function formatValidationErrors(error: any): Record<string, string> {
  const parsed = parseApiError(error)
  
  if (parsed.details?.validation_errors) {
    const errors: Record<string, string> = {}
    for (const err of parsed.details.validation_errors) {
      errors[err.field] = err.message
    }
    return errors
  }
  
  return {}
}

/**
 * Create error notification object
 */
export interface ErrorNotification {
  title: string
  message: string
  type: 'error' | 'warning' | 'info'
  duration?: number
}

export function createErrorNotification(error: any): ErrorNotification {
  const parsed = parseApiError(error)
  
  // Determine notification type based on error code
  let type: 'error' | 'warning' | 'info' = 'error'
  if (parsed.code.startsWith('VAL_')) {
    type = 'warning'
  } else if (parsed.code.startsWith('BIZ_')) {
    type = 'warning'
  }
  
  return {
    title: getErrorTitle(parsed.code),
    message: parsed.userMessage,
    type,
    duration: type === 'error' ? 5000 : 3000
  }
}

function getErrorTitle(code: ErrorCode | 'UNKNOWN'): string {
  if (code.startsWith('AUTH_')) return 'Authentication Error'
  if (code.startsWith('VAL_')) return 'Validation Error'
  if (code.startsWith('DB_')) return 'Database Error'
  if (code.startsWith('BIZ_')) return 'Operation Failed'
  if (code.startsWith('RES_')) return 'Resource Error'
  if (code.startsWith('SYS_')) return 'System Error'
  return 'Error'
}

export default {
  parseApiError,
  getUserMessage,
  isAuthError,
  isValidationError,
  isBusinessError,
  handleApiError,
  formatValidationErrors,
  createErrorNotification
}
