import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { glAnalyticsService } from '../services';
import type {
  TrendAnalysis,
  AnomalyDetection,
  PredictiveInsight,
  AccountPerformanceMetric
} from '../services/gl-analytics.service';
import type { AccountType } from '../types/gl-account';

export const useGlAnalyticsStore = defineStore('glAnalytics', () => {
  // State
  const trendAnalysis = ref<TrendAnalysis[]>([]);
  const anomalies = ref<AnomalyDetection[]>([]);
  const predictiveInsights = ref<PredictiveInsight[]>([]);
  const accountPerformance = ref<Record<string, AccountPerformanceMetric>>({});
  const loading = ref(false);
  const error = ref<string | null>(null);
  const lastUpdated = ref<Date | null>(null);

  // Getters
  const hasData = computed(() => {
    return trendAnalysis.value.length > 0 || 
           anomalies.value.length > 0 ||
           predictiveInsights.value.length > 0 ||
           Object.keys(accountPerformance.value).length > 0;
  });

  const highSeverityAnomalies = computed<AnomalyDetection[]>(() => {
    return anomalies.value.filter((a: AnomalyDetection) => a.severity === 'high');
  });

  const mediumSeverityAnomalies = computed<AnomalyDetection[]>(() => {
    return anomalies.value.filter((a: AnomalyDetection) => a.severity === 'medium');
  });

  const lowSeverityAnomalies = computed<AnomalyDetection[]>(() => {
    return anomalies.value.filter((a: AnomalyDetection) => a.severity === 'low');
  });

  const positiveTrends = computed<TrendAnalysis[]>(() => {
    return trendAnalysis.value.filter((t: TrendAnalysis) => t.trend === 'up');
  });

  const negativeTrends = computed<TrendAnalysis[]>(() => {
    return trendAnalysis.value.filter((t: TrendAnalysis) => t.trend === 'down');
  });

  // Actions
  async function fetchTrendAnalysis(params: {
    accountId?: string;
    accountType?: AccountType;
    period: 'monthly' | 'quarterly' | 'yearly';
    limit: number;
  }) {
    try {
      loading.value = true;
      error.value = null;
      const data = await glAnalyticsService.getTrendAnalysis(params);
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
  }) {
    try {
      loading.value = true;
      error.value = null;
      const data = await glAnalyticsService.detectAnomalies(params);
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
    accountIds?: string[];
    accountTypes?: AccountType[];
    forecastPeriods: number;
    confidenceThreshold?: number;
  }) {
    try {
      loading.value = true;
      error.value = null;
      const data = await glAnalyticsService.getPredictiveInsights({
        ...params,
        accountTypes: params.accountTypes
      });
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

  async function compareAccountPerformance(params: {
    accountIds: string[];
    compareWith: 'previous_period' | 'same_period_last_year' | 'budget';
    period: string;
  }) {
    try {
      loading.value = true;
      error.value = null;
      const data = await glAnalyticsService.compareAccountPerformance(params);
      
      // Convert array to object with accountId as key for easier lookups
      const performanceMap: Record<string, AccountPerformanceMetric> = {};
      data.forEach(item => {
        performanceMap[item.accountId] = item;
      });
      
      accountPerformance.value = performanceMap;
      lastUpdated.value = new Date();
      return data;
    } catch (err) {
      error.value = 'Failed to compare account performance';
      console.error('Error in compareAccountPerformance:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function getAccountInsights(accountId: string) {
    try {
      loading.value = true;
      error.value = null;
      const data = await glAnalyticsService.getAccountInsights(accountId);
      return data;
    } catch (err) {
      error.value = 'Failed to get account insights';
      console.error('Error in getAccountInsights:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function generateNarrativeReport(params: {
    period: string;
    accountTypes?: string[];
    includeCharts: boolean;
    language?: string;
  }) {
    try {
      loading.value = true;
      error.value = null;
      const data = await glAnalyticsService.generateNarrativeReport({
        ...params,
        accountTypes: params.accountTypes as any[] // Type assertion
      });
      return data;
    } catch (err) {
      error.value = 'Failed to generate narrative report';
      console.error('Error in generateNarrativeReport:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  function reset() {
    trendAnalysis.value = [];
    anomalies.value = [];
    predictiveInsights.value = [];
    accountPerformance.value = {};
    loading.value = false;
    error.value = null;
    lastUpdated.value = null;
  }

  return {
    // State
    trendAnalysis,
    anomalies,
    predictiveInsights,
    accountPerformance,
    loading,
    error,
    lastUpdated,
    
    // Getters
    hasData,
    highSeverityAnomalies,
    mediumSeverityAnomalies,
    lowSeverityAnomalies,
    positiveTrends,
    negativeTrends,
    
    // Actions
    fetchTrendAnalysis,
    detectAnomalies,
    fetchPredictiveInsights,
    compareAccountPerformance,
    getAccountInsights,
    generateNarrativeReport,
    reset
  };
});

// Export the store type for use in components
export type GlAnalyticsStore = ReturnType<typeof useGlAnalyticsStore>;
