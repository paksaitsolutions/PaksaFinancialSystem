/**
 * GL module error handling utilities
 */

export interface GLError {
  code: string
  message: string
  field?: string
  details?: any
}

export class GLErrorHandler {
  private static errorMessages: Record<string, string> = {
    'ACCOUNT_CODE_EXISTS': 'An account with this code already exists. Please choose a different code.',
    'ACCOUNT_NOT_FOUND': 'The requested account could not be found.',
    'ENTRY_NOT_BALANCED': 'The journal entry is not balanced. Total debits must equal total credits.',
    'ENTRY_ALREADY_POSTED': 'This journal entry has already been posted and cannot be modified.',
    'VALIDATION_ERROR': 'Please correct the highlighted errors and try again.',
    'PERMISSION_DENIED': 'You do not have permission to perform this action.',
    'OPERATION_FAILED': 'The operation could not be completed. Please try again.',
    'NETWORK_ERROR': 'Network error. Please check your connection and try again.'
  }

  static handleApiError(error: any): GLError {
    if (error.response) {
      const { status, data } = error.response
      
      if (status === 400 && data.error) {
        return {
          code: data.error.code || 'VALIDATION_ERROR',
          message: this.getUserFriendlyMessage(data.error.code, data.error.message),
          field: data.error.details?.field,
          details: data.error.details
        }
      }
      
      if (status === 403) {
        return {
          code: 'PERMISSION_DENIED',
          message: this.errorMessages.PERMISSION_DENIED
        }
      }
    }
    
    return {
      code: 'UNKNOWN_ERROR',
      message: 'An unexpected error occurred. Please try again.'
    }
  }

  static getUserFriendlyMessage(code: string, fallback?: string): string {
    return this.errorMessages[code] || fallback || 'An unexpected error occurred.'
  }

  static showError(error: GLError, showSnackbar: (message: string, color: string) => void) {
    showSnackbar(error.message, 'error')
  }
}