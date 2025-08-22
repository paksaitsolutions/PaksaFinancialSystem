import { defineStore } from 'pinia';
import { ref } from 'vue';
import type {
  PayrollTrendAnalysis,
  PayrollAnomaly,
  PayrollPredictiveInsight,
  PayrollCostAnalysis
} from '../services/payroll-analytics.service';
import { payrollAnalyticsService } from '../services/payroll-analytics.service';

export const usePayrollAnalyticsStore = defineStore('payrollAnalytics', () => {
  // State
  const trendAnalysis = ref<PayrollTrendAnalysis[]>([]);
  const anomalies = ref<PayrollAnomaly[]>([]);
  const predictiveInsights = ref<PayrollPredictiveInsight[]>([]);
  const costAnalysis = ref<PayrollCostAnalysis[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const lastUpdated = ref<Date | null>(null);

  // Getters
  const hasData = () => 
    trendAnalysis.value.length > 0 || 
    anomalies.value.length > 0 || 
    predictiveInsights.value.length > 0 ||
    costAnalysis.value.length > 0;

  const highSeverityAnomalies = () => 
    anomalies.value.filter(a => a.severity === 'high');

  const mediumSeverityAnomalies = () => 
    anomalies.value.filter(a => a.severity === 'medium');

  const lowSeverityAnomalies = () => 
    anomalies.value.filter(a => a.severity === 'low');

  // Actions
  async function fetchTrendAnalysis(params: {
    period: 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'yearly';
    limit: number;
    departmentId?: string;
    locationId?: string;
  }) {
    try {
      loading.value = true;
      error.value = null;
      const data = await payrollAnalyticsService.getTrendAnalysis(params);
      trendAnalysis.value = data;
      lastUpdated.value = new Date();
      return data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch trend analysis';
      console.error('Error in fetchTrendAnalysis:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function detectAnomalies(params: {
    startDate: string;
    endDate: string;
    minSeverity?: 'low' | 'medium' | 'high';
    departmentId?: string;
    locationId?: string;
  }) {
    try {
      loading.value = true;
      error.value = null;
      const data = await payrollAnalyticsService.detectAnomalies(params);
      anomalies.value = data;
      lastUpdated.value = new Date();
      return data;
    } catch (err) {
      error.value = 'Failed to detect anomalies';
      console.error('Error in detectAnomalies:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function fetchPredictiveInsights(params: {
    forecastPeriods: number;
    confidenceThreshold?: number;
    departmentId?: string;
    locationId?: string;
  }) {
    try {
      loading.value = true;
      error.value = null;
      const data = await payrollAnalyticsService.getPredictiveInsights(params);
      predictiveInsights.value = data;
      lastUpdated.value = new Date();
      return data;
    } catch (err) {
      error.value = 'Failed to fetch predictive insights';
      console.error('Error in fetchPredictiveInsights:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function fetchCostAnalysis(params: {
    period: 'current_month' | 'last_month' | 'ytd' | 'last_year' | 'custom';
    startDate?: string;
    endDate?: string;
    groupBy: 'department' | 'location' | 'job_title' | 'employee_type';
  }) {
    try {
      loading.value = true;
      error.value = null;
      const data = await payrollAnalyticsService.getCostAnalysis(params);
      costAnalysis.value = data;
      lastUpdated.value = new Date();
      return data;
    } catch (err) {
      error.value = 'Failed to fetch cost analysis';
      console.error('Error in fetchCostAnalysis:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  function reset() {
    trendAnalysis.value = [];
    anomalies.value = [];
    predictiveInsights.value = [];
    costAnalysis.value = [];
    error.value = null;
    lastUpdated.value = null;
  }

  return {
    // State
    trendAnalysis,
    anomalies,
    predictiveInsights,
    costAnalysis,
    loading,
    error,
    lastUpdated,
    
    // Getters
    hasData,
    highSeverityAnomalies,
    mediumSeverityAnomalies,
    lowSeverityAnomalies,
    
    // Actions
    fetchTrendAnalysis,
    detectAnomalies,
    fetchPredictiveInsights,
    fetchCostAnalysis,
    reset
  };
});

// Export the store type for use in components
export type PayrollAnalyticsStore = ReturnType<typeof usePayrollAnalyticsStore>;
