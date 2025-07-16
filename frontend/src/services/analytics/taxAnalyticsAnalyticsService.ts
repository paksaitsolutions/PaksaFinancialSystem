import { TaxAnalyticsRequest, TaxAnalyticsResponse } from '@/types/tax';
import { useTaxAnalyticsStore } from '@/stores/tax/analytics';
import { useAnalytics } from '@/composables/useAnalytics';
import { taxAnalyticsLogger } from '@/services/logger/taxAnalyticsLogger';
import { taxAnalyticsErrorHandler } from '@/services/error/taxAnalyticsErrorHandler';

export class TaxAnalyticsAnalyticsService {
  private store = useTaxAnalyticsStore();
  private analytics = useAnalytics();
  private logger = taxAnalyticsLogger;
  private errorHandler = taxAnalyticsErrorHandler;

  constructor() {
    this.setupAnalyticsTracking();
  }

  private setupAnalyticsTracking(): void {
    // Track dashboard load
    this.analytics.trackPageView('TaxAnalyticsDashboard');

    // Track user interactions
    window.addEventListener('taxAnalyticsInteraction', (event) => {
      this.handleInteractionEvent(event.detail);
    });
  }

  async fetchAnalytics(request: TaxAnalyticsRequest): Promise<TaxAnalyticsResponse> {
    try {
      this.logger.startPerformanceTimer('fetchAnalytics');
      
      // Log request
      this.logger.logAnalyticsRequest(request);
      
      // Track request
      this.analytics.trackEvent('TaxAnalytics', 'Request', {
        period: request.period,
        hasCustomDates: !!request.start_date || !!request.end_date
      });

      // Fetch data
      const response = await this.store.fetchAnalytics(request);

      // Log response
      this.logger.logAnalyticsResponse(response);
      
      // Track response
      this.analytics.trackEvent('TaxAnalytics', 'Response', {
        complianceRate: response.metrics.complianceRate,
        totalTax: response.metrics.totalTax
      });

      // End performance timer
      this.logger.endPerformanceTimer('fetchAnalytics');

      return response;
    } catch (error) {
      // Log error
      this.logger.logError(error, 'Fetch Analytics');
      
      // Handle error
      this.errorHandler.handleAnalyticsFetchError(error);
      
      throw error;
    }
  }

  async exportAnalytics(format: string): Promise<void> {
    try {
      this.logger.startPerformanceTimer('exportAnalytics');
      
      // Log export request
      this.logger.logExportRequest(format);
      
      // Track export
      this.analytics.trackEvent('TaxAnalytics', 'Export', { format });

      // Export data
      await this.store.exportAnalytics(format);

      // Log export completion
      this.logger.logExportCompletion(format, performance.now() - this.logger.getPerformanceStartTime());
      
      // Track export completion
      this.analytics.trackEvent('TaxAnalytics', 'ExportComplete', { format });
    } catch (error) {
      // Log error
      this.logger.logError(error, 'Export Analytics');
      
      // Handle error
      this.errorHandler.handleExportError(error);
      
      throw error;
    } finally {
      // End performance timer
      this.logger.endPerformanceTimer('exportAnalytics');
    }
  }

  handleChartInteraction(chartType: string, action: string): void {
    try {
      // Log chart interaction
      this.logger.logChartInteraction(chartType, action);
      
      // Track chart interaction
      this.analytics.trackEvent('TaxAnalytics', 'ChartInteraction', {
        chartType,
        action
      });
    } catch (error) {
      // Log error
      this.logger.logError(error, 'Chart Interaction');
      
      // Handle error
      this.errorHandler.handleChartError(error);
    }
  }

  private handleInteractionEvent(event: { type: string; data: any }): void {
    try {
      switch (event.type) {
        case 'periodChange':
          this.logger.logPeriodChange(event.data.period);
          this.analytics.trackEvent('TaxAnalytics', 'PeriodChange', {
            period: event.data.period
          });
          break;
        case 'refresh':
          this.logger.logRefresh();
          this.analytics.trackEvent('TaxAnalytics', 'Refresh');
          break;
        case 'chartInteraction':
          this.handleChartInteraction(event.data.chartType, event.data.action);
          break;
      }
    } catch (error) {
      // Log error
      this.logger.logError(error, 'Interaction Event');
      
      // Handle error
      this.errorHandler.handleError(error, 'Interaction Event');
    }
  }

  // Performance Monitoring
  startPerformanceTimer(name: string): void {
    this.logger.startPerformanceTimer(name);
  }

  endPerformanceTimer(name: string): void {
    this.logger.endPerformanceTimer(name);
  }

  // Session Tracking
  trackSessionStart(): void {
    this.logger.logSessionStart();
    this.analytics.trackEvent('TaxAnalytics', 'SessionStart');
  }

  trackSessionEnd(): void {
    this.logger.logSessionEnd();
    this.analytics.trackEvent('TaxAnalytics', 'SessionEnd');
  }
}

// Export singleton instance
export const taxAnalyticsAnalyticsService = new TaxAnalyticsAnalyticsService();
