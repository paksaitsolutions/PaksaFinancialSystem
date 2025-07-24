/**
 * Analytics Service
 * 
 * This service provides comprehensive analytics functionality for the frontend,
 * replacing mock data with real API calls to the analytics backend.
 */
import { ref, computed } from 'vue';
import axios from 'axios';
import { useApi } from '@/composables/useApi';
import { useAuthStore } from '@/stores/auth';

export interface DateRange {
  start_date: string;
  end_date: string;
}

export interface FinancialSummary {
  revenue: number;
  expenses: number;
  profit: number;
  profit_margin: number;
  cash_flow: {
    inflows: number;
    outflows: number;
    net_cash_flow: number;
  };
  accounts_receivable: {
    total_outstanding: number;
    overdue_amount: number;
    current_ratio: number;
  };
  accounts_payable: {
    total_outstanding: number;
    due_soon: number;
  };
  period: {
    start: string;
    end: string;
  };
}

export interface TrendData {
  period: string;
  value: number;
  metric: string;
}

export interface KPIDashboard {
  financial_summary: FinancialSummary;
  growth_metrics: {
    revenue_growth: number;
    profit_growth: number;
  };
  operational_metrics: {
    active_customers: number;
    active_vendors: number;
    inventory_value: number;
  };
  trends: {
    revenue: TrendData[];
    profit: TrendData[];
  };
}

export interface ReportRequest {
  report_type: string;
  parameters: Record<string, any>;
  format?: string;
}

export interface ScheduledReportRequest {
  report_type: string;
  report_name: string;
  parameters: Record<string, any>;
  format: string;
  frequency: string;
  recipients: string[];
  cron_expression?: string;
}

export interface DashboardWidget {
  id: string;
  type: string;
  title: string;
  data?: any;
  chart_type?: string;
  x_axis?: string;
  y_axis?: string;
  value?: number;
  change?: number;
  format?: string;
  trend?: string;
}

export interface Dashboard {
  dashboard_id: string;
  title: string;
  widgets: DashboardWidget[];
  last_updated: string;
  refresh_interval: number;
}

export const useAnalytics = () => {
  const api = useApi();
  const authStore = useAuthStore();
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Data Aggregation Methods
  const getFinancialSummary = async (dateRange?: DateRange): Promise<FinancialSummary> => {
    try {
      loading.value = true;
      error.value = null;

      const params = new URLSearchParams();
      if (dateRange) {
        params.append('start_date', dateRange.start_date);
        params.append('end_date', dateRange.end_date);
      }

      const response = await api.get(`/api/analytics/financial-summary?${params.toString()}`);
      return response.data.data;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch financial summary';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const getTrendAnalysis = async (
    metric: string,
    period: string = 'monthly',
    months: number = 12
  ): Promise<TrendData[]> => {
    try {
      loading.value = true;
      error.value = null;

      const response = await api.get(`/api/analytics/trend-analysis/${metric}`, {
        params: { period, months }
      });
      return response.data.data;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch trend analysis';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const getKPIDashboard = async (): Promise<KPIDashboard> => {
    try {
      loading.value = true;
      error.value = null;

      const response = await api.get('/api/analytics/kpi-dashboard');
      return response.data.data;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch KPI dashboard';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  // Reporting Methods
  const generateReport = async (request: ReportRequest): Promise<any> => {
    try {
      loading.value = true;
      error.value = null;

      const response = await api.post('/api/analytics/reports/generate', request);
      return response.data.data;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to generate report';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const getReportTypes = async (): Promise<any[]> => {
    try {
      const response = await api.get('/api/analytics/reports/types');
      return response.data.data;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch report types';
      throw err;
    }
  };

  // Dashboard Methods
  const getExecutiveDashboard = async (): Promise<Dashboard> => {
    try {
      loading.value = true;
      error.value = null;

      const response = await api.get('/api/analytics/dashboards/executive');
      return response.data.data;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch executive dashboard';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const getFinancialDashboard = async (): Promise<Dashboard> => {
    try {
      loading.value = true;
      error.value = null;

      const response = await api.get('/api/analytics/dashboards/financial');
      return response.data.data;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch financial dashboard';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const getOperationalDashboard = async (): Promise<Dashboard> => {
    try {
      loading.value = true;
      error.value = null;

      const response = await api.get('/api/analytics/dashboards/operational');
      return response.data.data;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch operational dashboard';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const createCustomDashboard = async (config: {
    dashboard_type: string;
    widgets: any[];
  }): Promise<Dashboard> => {
    try {
      loading.value = true;
      error.value = null;

      const response = await api.post('/api/analytics/dashboards/custom', config);
      return response.data.data;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to create custom dashboard';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  // Scheduled Reports Methods
  const createScheduledReport = async (request: ScheduledReportRequest): Promise<any> => {
    try {
      loading.value = true;
      error.value = null;

      const response = await api.post('/api/analytics/scheduled-reports', request);
      return response.data.data;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to create scheduled report';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const getScheduledReports = async (): Promise<any[]> => {
    try {
      loading.value = true;
      error.value = null;

      const response = await api.get('/api/analytics/scheduled-reports');
      return response.data.data;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch scheduled reports';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const executeScheduledReport = async (reportId: string): Promise<void> => {
    try {
      loading.value = true;
      error.value = null;

      await api.post(`/api/analytics/scheduled-reports/${reportId}/execute`);
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to execute scheduled report';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const getExecutionHistory = async (reportId: string, limit: number = 50): Promise<any[]> => {
    try {
      const response = await api.get(`/api/analytics/scheduled-reports/${reportId}/history`, {
        params: { limit }
      });
      return response.data.data;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch execution history';
      throw err;
    }
  };

  // Performance Methods
  const getQueryPerformanceMetrics = async (): Promise<any> => {
    try {
      const response = await api.get('/api/analytics/performance/query-metrics');
      return response.data.data;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch performance metrics';
      throw err;
    }
  };

  const warmCache = async (): Promise<void> => {
    try {
      await api.post('/api/analytics/performance/warm-cache');
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to warm cache';
      throw err;
    }
  };

  const invalidateCache = async (): Promise<void> => {
    try {
      await api.post('/api/analytics/performance/invalidate-cache');
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to invalidate cache';
      throw err;
    }
  };

  // Data Warehouse Methods
  const runETLProcess = async (fullRefresh: boolean = false): Promise<void> => {
    try {
      loading.value = true;
      error.value = null;

      await api.post('/api/analytics/data-warehouse/etl', null, {
        params: { full_refresh: fullRefresh }
      });
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to run ETL process';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const getWarehouseStatistics = async (): Promise<any> => {
    try {
      const response = await api.get('/api/analytics/data-warehouse/statistics');
      return response.data.data;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch warehouse statistics';
      throw err;
    }
  };

  const initializeDataWarehouse = async (): Promise<void> => {
    try {
      loading.value = true;
      error.value = null;

      await api.post('/api/analytics/data-warehouse/initialize');
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to initialize data warehouse';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  // Utility Methods
  const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(value);
  };

  const formatPercentage = (value: number): string => {
    return `${value.toFixed(1)}%`;
  };

  const formatNumber = (value: number): string => {
    return new Intl.NumberFormat('en-US').format(value);
  };

  const getTrendDirection = (value: number): 'up' | 'down' | 'neutral' => {
    if (value > 0) return 'up';
    if (value < 0) return 'down';
    return 'neutral';
  };

  const getTrendColor = (direction: string): string => {
    switch (direction) {
      case 'up': return 'success';
      case 'down': return 'error';
      default: return 'info';
    }
  };

  return {
    // State
    loading: computed(() => loading.value),
    error: computed(() => error.value),

    // Data Aggregation
    getFinancialSummary,
    getTrendAnalysis,
    getKPIDashboard,

    // Reporting
    generateReport,
    getReportTypes,

    // Dashboards
    getExecutiveDashboard,
    getFinancialDashboard,
    getOperationalDashboard,
    createCustomDashboard,

    // Scheduled Reports
    createScheduledReport,
    getScheduledReports,
    executeScheduledReport,
    getExecutionHistory,

    // Performance
    getQueryPerformanceMetrics,
    warmCache,
    invalidateCache,

    // Data Warehouse
    runETLProcess,
    getWarehouseStatistics,
    initializeDataWarehouse,

    // Utilities
    formatCurrency,
    formatPercentage,
    formatNumber,
    getTrendDirection,
    getTrendColor
  };
};