import { useNotification } from '@/composables/useNotification';
import { useTaxAnalyticsStore } from '@/modules/tax/store/analytics';
import { useLogger } from '@/composables/useLogger';

export class TaxAnalyticsErrorHandler {
  private notification = useNotification();
  private logger = useLogger();
  private store = useTaxAnalyticsStore();

  constructor() {
    this.setupErrorHandlers();
  }

  private setupErrorHandlers(): void {
    // Global error handler
    window.addEventListener('error', (event) => {
      this.handleError(event.error, 'Global Error');
    });

    // Promise rejection handler
    window.addEventListener('unhandledrejection', (event) => {
      this.handleError(event.reason, 'Promise Rejection');
    });
  }

  handleError(error: any, context: string): void {
    try {
      // Log the error
      this.logger.error(`Tax Analytics Error - ${context}:`, error);

      // Get specific error details
      const errorDetails = this.getErrorMessage(error);

      // Show user-friendly notification
      this.notification.error(errorDetails.userMessage);

      // Update store with error state
      this.store.error = errorDetails.userMessage;

      // Track error metrics
      this.trackErrorMetrics(errorDetails);
    } catch (handlerError) {
      // Fallback if error handling itself fails
      console.error('Error in error handler:', handlerError);
      this.notification.error('An unexpected error occurred. Please try again later.');
    }
  }

  private getErrorMessage(error: any): { code: string; userMessage: string; details: string } {
    if (!error) {
      return {
        code: 'UNKNOWN_ERROR',
        userMessage: 'An unexpected error occurred. Please try again later.',
        details: 'Unknown error with no details available'
      };
    }

    // Handle API errors
    if (error.response?.data?.detail) {
      return {
        code: error.response.data.detail,
        userMessage: error.response.data.detail,
        details: JSON.stringify(error.response.data)
      };
    }

    // Handle validation errors
    if (error.errors) {
      return {
        code: 'VALIDATION_ERROR',
        userMessage: 'Validation failed. Please check your input.',
        details: JSON.stringify(error.errors)
      };
    }

    // Handle network errors
    if (error.message?.includes('Network Error')) {
      return {
        code: 'NETWORK_ERROR',
        userMessage: 'Network error occurred. Please check your connection.',
        details: error.message
      };
    }

    // Default error handling
    return {
      code: 'UNKNOWN_ERROR',
      userMessage: 'An unexpected error occurred. Please try again later.',
      details: error.message || error.toString()
    };
  }

  private trackErrorMetrics(errorDetails: { code: string; userMessage: string; details: string }): void {
    // Track error metrics using analytics service
    // This would typically be implemented using your analytics service
    // For example:
    // analyticsService.trackError({
    //   errorType: errorDetails.code,
    //   errorMessage: errorDetails.userMessage,
    //   errorDetails: errorDetails.details
    // });
  }

  // Specific error handlers for common scenarios
  handleAnalyticsFetchError(error: any): void {
    const errorDetails = this.getErrorMessage(error);
    this.handleError(error, 'Analytics Fetch Error');
  }

  handleExportError(error: any): void {
    const errorDetails = this.getErrorMessage(error);
    this.handleError(error, 'Export Error');
  }

  handleChartError(error: any): void {
    const errorDetails = this.getErrorMessage(error);
    this.handleError(error, 'Chart Error');
  }
}

// Export singleton instance
export const taxAnalyticsErrorHandler = new TaxAnalyticsErrorHandler();
