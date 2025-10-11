import { ref } from 'vue'
import { useUnifiedNotifications } from './useUnifiedNotifications'

export interface ErrorContext {
  component?: string
  action?: string
  userId?: string
  timestamp?: Date
  metadata?: Record<string, any>
}

export interface ErrorLog {
  id: string
  error: Error
  context: ErrorContext
  timestamp: Date
  handled: boolean
}

const errorLogs = ref<ErrorLog[]>([])
const { error: showErrorNotification } = useUnifiedNotifications()

export function useUnifiedErrorHandler() {
  const logError = (error: Error, context: ErrorContext = {}) => {
    const errorLog: ErrorLog = {
      id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
      error,
      context: {
        timestamp: new Date(),
        ...context
      },
      timestamp: new Date(),
      handled: false
    }
    
    errorLogs.value.push(errorLog)
    
    // Keep only last 100 errors
    if (errorLogs.value.length > 100) {
      errorLogs.value = errorLogs.value.slice(-100)
    }
    
    // Log to console in development
    if (import.meta.env.DEV) {
      console.error('Error logged:', errorLog)
    }
    
    return errorLog.id
  }

  const handleError = (error: Error, context: ErrorContext = {}, showNotification = true) => {
    const errorId = logError(error, context)
    
    if (showNotification) {
      const message = getErrorMessage(error)
      showErrorNotification(
        message,
        'An error occurred',
        {
          actions: [
            {
              label: 'Retry',
              action: () => {
                // Emit retry event or callback
                if (context.metadata?.retryCallback) {
                  context.metadata.retryCallback()
                }
              }
            }
          ]
        }
      )
    }
    
    // Mark as handled
    const errorLog = errorLogs.value.find(log => log.id === errorId)
    if (errorLog) {
      errorLog.handled = true
    }
    
    return errorId
  }

  const getErrorMessage = (error: Error): string => {
    // API errors
    if (error.message.includes('Network Error')) {
      return 'Unable to connect to the server. Please check your internet connection.'
    }
    
    if (error.message.includes('401')) {
      return 'Your session has expired. Please log in again.'
    }
    
    if (error.message.includes('403')) {
      return 'You do not have permission to perform this action.'
    }
    
    if (error.message.includes('404')) {
      return 'The requested resource was not found.'
    }
    
    if (error.message.includes('500')) {
      return 'A server error occurred. Please try again later.'
    }
    
    // Validation errors
    if (error.message.includes('validation')) {
      return 'Please check your input and try again.'
    }
    
    // Generic fallback
    return error.message || 'An unexpected error occurred.'
  }

  const clearErrorLogs = () => {
    errorLogs.value = []
  }

  const getUnhandledErrors = () => {
    return errorLogs.value.filter(log => !log.handled)
  }

  const markErrorAsHandled = (errorId: string) => {
    const errorLog = errorLogs.value.find(log => log.id === errorId)
    if (errorLog) {
      errorLog.handled = true
    }
  }

  // Global error handler setup
  const setupGlobalErrorHandler = () => {
    window.addEventListener('error', (event) => {
      handleError(new Error(event.message), {
        component: 'Global',
        action: 'Runtime Error',
        metadata: {
          filename: event.filename,
          lineno: event.lineno,
          colno: event.colno
        }
      })
    })

    window.addEventListener('unhandledrejection', (event) => {
      handleError(new Error(event.reason), {
        component: 'Global',
        action: 'Unhandled Promise Rejection'
      })
    })
  }

  return {
    errorLogs,
    logError,
    handleError,
    getErrorMessage,
    clearErrorLogs,
    getUnhandledErrors,
    markErrorAsHandled,
    setupGlobalErrorHandler
  }
}