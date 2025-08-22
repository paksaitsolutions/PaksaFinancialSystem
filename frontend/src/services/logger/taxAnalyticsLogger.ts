import { useLogger } from '@/composables/useLogger';
import { useAnalytics } from '@/composables/useAnalytics';
import { TaxAnalyticsRequest, TaxAnalyticsResponse } from '@/types/tax';

export class TaxAnalyticsLogger {
  private logger = useLogger();
  private analytics = useAnalytics();

  constructor() {
    this.setupEventListeners();
  }

  private setupEventListeners(): void {
    // Listen for analytics-related events
    window.addEventListener('taxAnalyticsEvent', (event) => {
      this.handleAnalyticsEvent(event.detail);
    });
  }

  // Analytics Event Handlers
  logAnalyticsRequest(request: TaxAnalyticsRequest): void {
    this.logger.info('Tax Analytics Request', {
      period: request.period,
      startDate: request.start_date,
      endDate: request.end_date
    });

    this.analytics.trackEvent('TaxAnalytics', 'Request', {
      period: request.period,
      hasCustomDates: !!request.start_date || !!request.end_date
    });
  }

  logAnalyticsResponse(response: TaxAnalyticsResponse): void {
    this.logger.info('Tax Analytics Response', {
      metrics: response.metrics,
      insights: response.insights
    });

    this.analytics.trackEvent('TaxAnalytics', 'Response', {
      complianceRate: response.metrics.complianceRate,
      totalTax: response.metrics.totalTax
    });
  }

  logExportRequest(format: string): void {
    this.logger.info('Tax Analytics Export Request', { format });
    this.analytics.trackEvent('TaxAnalytics', 'Export', { format });
  }

  logPeriodChange(period: string): void {
    this.logger.info('Tax Analytics Period Change', { period });
    this.analytics.trackEvent('TaxAnalytics', 'PeriodChange', { period });
  }

  logRefresh(): void {
    this.logger.info('Tax Analytics Data Refresh');
    this.analytics.trackEvent('TaxAnalytics', 'Refresh');
  }

  // Error Logging
  logError(error: Error, context: string): void {
    this.logger.error(`Tax Analytics Error - ${context}:`, error);
    this.analytics.trackException(error, {
      context,
      severity: 'critical'
    });
  }

  // Performance Monitoring
  startPerformanceTimer(name: string): void {
    performance.mark(`tax-analytics-${name}-start`);
  }

  endPerformanceTimer(name: string): void {
    const start = `tax-analytics-${name}-start`;
    const end = `tax-analytics-${name}-end`;
    performance.mark(end);
    
    const measure = performance.measure(name, start, end);
    this.logger.info(`Tax Analytics Performance - ${name}`, {
      duration: measure.duration
    });

    this.analytics.trackTiming('TaxAnalytics', name, measure.duration);
  }

  // Usage Metrics
  logChartInteraction(chartType: string, action: string): void {
    this.logger.info('Tax Analytics Chart Interaction', { chartType, action });
    this.analytics.trackEvent('TaxAnalytics', 'ChartInteraction', {
      chartType,
      action
    });
  }

  logExportCompletion(format: string, duration: number): void {
    this.logger.info('Tax Analytics Export Completion', { format, duration });
    this.analytics.trackEvent('TaxAnalytics', 'ExportComplete', {
      format,
      duration
    });
  }

  // Session Metrics
  logSessionStart(): void {
    this.logger.info('Tax Analytics Session Start');
    this.analytics.trackEvent('TaxAnalytics', 'SessionStart');
  }

  logSessionEnd(): void {
    this.logger.info('Tax Analytics Session End');
    this.analytics.trackEvent('TaxAnalytics', 'SessionEnd');
  }
}

// Export singleton instance
export const taxAnalyticsLogger = new TaxAnalyticsLogger();
