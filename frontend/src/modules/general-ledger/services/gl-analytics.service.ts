import { ref } from 'vue';
import axios from 'axios';
import type { AccountType } from '../types/gl-account';

export const API_BASE_URL = '/api/gl/analytics';

// Types for AI/BI analytics
export interface TrendAnalysis {
  period: string;
  amount: number;
  trend: 'up' | 'down' | 'stable';
  percentageChange: number;
  accountId?: string;
  accountType?: AccountType;
}

export interface AnomalyDetection {
  accountId: string;
  accountNumber: string;
  accountName: string;
  expectedAmount: number;
  actualAmount: number;
  deviation: number;
  severity: 'low' | 'medium' | 'high';
  dateDetected: string;
  transactionId?: string;
  notes?: string;
}

export interface PredictiveInsight {
  accountId: string;
  accountNumber: string;
  accountName: string;
  prediction: {
    nextPeriodAmount: number;
    confidence: number;
    trend: 'increasing' | 'decreasing' | 'stable';
    lowerBound?: number;
    upperBound?: number;
  };
  recommendations: string[];
  lastUpdated: string;
}

export interface AccountPerformanceMetric {
  accountId: string;
  accountNumber: string;
  accountName: string;
  currentPeriod: number;
  previousPeriod: number;
  yoyGrowth: number;
  qoqGrowth: number;
  variance: number;
  accountType: AccountType;
  currency: string;
}

class GlAnalyticsService {
  private loading = ref(false);
  private error = ref<string | null>(null);

  /**
   * Get trend analysis for a specific account or account type
   */
  async getTrendAnalysis(params: {
    accountId?: string;
    accountType?: AccountType;
    period: 'monthly' | 'quarterly' | 'yearly';
    limit: number;
  }): Promise<TrendAnalysis[]> {
    try {
      this.loading.value = true;
      const response = await axios.get<TrendAnalysis[]>(`${API_BASE_URL}/trends`, { params });
      return response.data;
    } catch (err) {
      this.handleError('Failed to fetch trend analysis', err);
      throw err;
    } finally {
      this.loading.value = false;
    }
  }

  /**
   * Detect anomalies in account balances or transactions
   */
  async detectAnomalies(params: {
    startDate: string;
    endDate: string;
    minSeverity?: 'low' | 'medium' | 'high';
  }): Promise<AnomalyDetection[]> {
    try {
      this.loading.value = true;
      const response = await axios.get<AnomalyDetection[]>(`${API_BASE_URL}/anomalies`, { params });
      return response.data;
    } catch (err) {
      this.handleError('Failed to detect anomalies', err);
      throw err;
    } finally {
      this.loading.value = false;
    }
  }

  /**
   * Get predictive insights for future periods
   */
  async getPredictiveInsights(params: {
    accountIds?: string[];
    accountTypes?: AccountType[];
    forecastPeriods: number;
    confidenceThreshold?: number;
  }): Promise<PredictiveInsight[]> {
    try {
      this.loading.value = true;
      const response = await axios.post<PredictiveInsight[]>(
        `${API_BASE_URL}/predictions`,
        params
      );
      return response.data;
    } catch (err) {
      this.handleError('Failed to get predictive insights', err);
      throw err;
    } finally {
      this.loading.value = false;
    }
  }

  /**
   * Compare account performance across different periods
   */
  async compareAccountPerformance(params: {
    accountIds: string[];
    compareWith: 'previous_period' | 'same_period_last_year' | 'budget';
    period: string;
  }): Promise<AccountPerformanceMetric[]> {
    try {
      this.loading.value = true;
      const response = await axios.get<AccountPerformanceMetric[]>(
        `${API_BASE_URL}/performance`, 
        { params }
      );
      return response.data;
    } catch (err) {
      this.handleError('Failed to compare account performance', err);
      throw err;
    } finally {
      this.loading.value = false;
    }
  }

  /**
   * Get AI-generated insights for a specific account
   */
  async getAccountInsights(accountId: string): Promise<{
    keyMetrics: any[];
    trends: any[];
    recommendations: string[];
    riskFactors: string[];
  }> {
    try {
      this.loading.value = true;
      const response = await axios.get(`${API_BASE_URL}/accounts/${accountId}/insights`);
      return response.data;
    } catch (err) {
      this.handleError('Failed to get account insights', err);
      throw err;
    } finally {
      this.loading.value = false;
    }
  }

  /**
   * Generate a narrative report for a specific period
   */
  async generateNarrativeReport(params: {
    period: string;
    accountTypes?: AccountType[];
    includeCharts: boolean;
    language?: string;
  }): Promise<{
    summary: string;
    keyFindings: string[];
    charts?: any[];
    generatedAt: string;
  }> {
    try {
      this.loading.value = true;
      const response = await axios.post(`${API_BASE_URL}/reports/narrative`, params);
      return response.data;
    } catch (err) {
      this.handleError('Failed to generate narrative report', err);
      throw err;
    } finally {
      this.loading.value = false;
    }
  }

  // Helper method to handle errors consistently
  private handleError(message: string, error: unknown): void {
    const errorMessage = error instanceof Error ? error.message : String(error);
    console.error(`${message}:`, error);
    this.error.value = errorMessage;
    // Could integrate with a global error handling service here
  }

  // Getters for reactive state
  get isLoading() {
    return this.loading.value;
  }

  get hasError() {
    return this.error.value !== null;
  }

  get errorMessage() {
    return this.error.value;
  }
}

export const glAnalyticsService = new GlAnalyticsService();
