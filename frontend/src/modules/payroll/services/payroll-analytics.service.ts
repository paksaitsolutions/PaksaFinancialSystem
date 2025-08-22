import { ref } from 'vue';
import axios from 'axios';

export interface PayrollTrendAnalysis {
  period: string;
  totalPayroll: number;
  employeeCount: number;
  averageSalary: number;
  overtimeCost: number;
  benefitsCost: number;
  taxWithheld: number;
  netPay: number;
  trend: 'up' | 'down' | 'stable';
  changePercentage: number;
}

export interface PayrollAnomaly {
  id: string;
  type: 'overtime' | 'tax' | 'benefits' | 'salary' | 'other';
  severity: 'low' | 'medium' | 'high';
  description: string;
  amount: number;
  expectedAmount?: number;
  variance: number;
  date: string;
  employeeId?: string;
  employeeName?: string;
  department?: string;
}

export interface PayrollPredictiveInsight {
  metric: string;
  currentValue: number;
  predictedValue: number;
  confidence: number;
  trend: 'increasing' | 'decreasing' | 'stable';
  lowerBound?: number;
  upperBound?: number;
  recommendations: string[];
  lastUpdated: string;
}

export interface PayrollCostAnalysis {
  department: string;
  totalPayroll: number;
  employeeCount: number;
  averageSalary: number;
  benefitsCost: number;
  taxCost: number;
  overtimeCost: number;
  otherCosts: number;
  costPerEmployee: number;
  percentageOfTotal: number;
}

const API_BASE_URL = '/api/payroll/analytics';

class PayrollAnalyticsService {
  private loading = ref(false);
  private error = ref<string | null>(null);

  /**
   * Get trend analysis for payroll data
   */
  async getTrendAnalysis(params: {
    period: 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'yearly';
    limit: number;
    departmentId?: string;
    locationId?: string;
  }): Promise<PayrollTrendAnalysis[]> {
    try {
      this.loading.value = true;
      const response = await axios.get<PayrollTrendAnalysis[]>(`${API_BASE_URL}/trends`, { params });
      return response.data;
    } catch (err) {
      this.handleError('Failed to fetch payroll trend analysis', err);
      throw err;
    } finally {
      this.loading.value = false;
    }
  }

  /**
   * Detect anomalies in payroll data
   */
  async detectAnomalies(params: {
    startDate: string;
    endDate: string;
    minSeverity?: 'low' | 'medium' | 'high';
    departmentId?: string;
    locationId?: string;
  }): Promise<PayrollAnomaly[]> {
    try {
      this.loading.value = true;
      const response = await axios.get<PayrollAnomaly[]>(`${API_BASE_URL}/anomalies`, { params });
      return response.data;
    } catch (err) {
      this.handleError('Failed to detect payroll anomalies', err);
      throw err;
    } finally {
      this.loading.value = false;
    }
  }

  /**
   * Get predictive insights for payroll
   */
  async getPredictiveInsights(params: {
    forecastPeriods: number;
    confidenceThreshold?: number;
    departmentId?: string;
    locationId?: string;
  }): Promise<PayrollPredictiveInsight[]> {
    try {
      this.loading.value = true;
      const response = await axios.post<PayrollPredictiveInsight[]>(
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
   * Get cost analysis by department
   */
  async getCostAnalysis(params: {
    period: 'current_month' | 'last_month' | 'ytd' | 'last_year' | 'custom';
    startDate?: string;
    endDate?: string;
    groupBy: 'department' | 'location' | 'job_title' | 'employee_type';
  }): Promise<PayrollCostAnalysis[]> {
    try {
      this.loading.value = true;
      const response = await axios.get<PayrollCostAnalysis[]>(`${API_BASE_URL}/cost-analysis`, { params });
      return response.data;
    } catch (err) {
      this.handleError('Failed to fetch cost analysis', err);
      throw err;
    } finally {
      this.loading.value = false;
    }
  }

  /**
   * Get employee compensation analysis
   */
  async getEmployeeCompensationAnalysis(params: {
    departmentId?: string;
    locationId?: string;
    jobTitle?: string;
    employeeType?: string;
    sortBy?: 'salary' | 'tenure' | 'performance_rating';
    sortOrder?: 'asc' | 'desc';
    limit?: number;
  }) {
    try {
      this.loading.value = true;
      const response = await axios.get(`${API_BASE_URL}/employee-compensation`, { params });
      return response.data;
    } catch (err) {
      this.handleError('Failed to fetch employee compensation analysis', err);
      throw err;
    } finally {
      this.loading.value = false;
    }
  }

  /**
   * Generate narrative report for payroll
   */
  async generateNarrativeReport(params: {
    period: string;
    includeCharts: boolean;
    language?: string;
  }) {
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

export const payrollAnalyticsService = new PayrollAnalyticsService();
