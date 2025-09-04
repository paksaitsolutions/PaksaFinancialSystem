import axios from 'axios';
import { useAuthStore } from '@/stores/auth';

const API_BASE_URL = '/api/payroll/analytics';

interface PayrollTrendData {
  labels: string[];
  datasets: Array<{
    label: string;
    data: number[];
    backgroundColor: string;
    borderColor: string;
    tension: number;
  }>;
}

interface CostAnalysisData {
  labels: string[];
  datasets: Array<{
    label: string;
    data: number[];
    backgroundColor: string[];
  }>;
}

interface Anomaly {
  id: string;
  type: string;
  description: string;
  date: string;
  amount: number;
  expectedAmount: number;
  status: 'pending' | 'resolved' | 'ignored';
  employeeId: string;
  employeeName: string;
}

export const PayrollAnalyticsService = {
  /**
   * Get payroll trends data
   */
  async getPayrollTrends(period: 'daily' | 'weekly' | 'monthly' | 'yearly' = 'monthly', limit: number = 12): Promise<{ data: PayrollTrendData }> {
    try {
      const authStore = useAuthStore();
      const response = await axios.get(`${API_BASE_URL}/trends`, {
        params: { period, limit },
        headers: {
          'Authorization': `Bearer ${authStore.token}`,
          'Content-Type': 'application/json'
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching payroll trends:', error);
      throw error;
    }
  },

  /**
   * Get payroll cost analysis
   */
  async getCostAnalysis(period: 'current_month' | 'last_month' | 'year_to_date' | 'custom' = 'current_month', 
                       groupBy: 'department' | 'position' | 'location' = 'department',
                       startDate?: string,
                       endDate?: string): Promise<{ data: CostAnalysisData }> {
    try {
      const authStore = useAuthStore();
      const params: any = { period, groupBy };
      
      if (startDate) params.startDate = startDate;
      if (endDate) params.endDate = endDate;
      
      const response = await axios.get(`${API_BASE_URL}/cost-analysis`, {
        params,
        headers: {
          'Authorization': `Bearer ${authStore.token}`,
          'Content-Type': 'application/json'
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching cost analysis:', error);
      throw error;
    }
  },

  /**
   * Detect anomalies in payroll data
   */
  async detectAnomalies(startDate: string, endDate: string, threshold: number = 2.0): Promise<{ data: Anomaly[] }> {
    try {
      const authStore = useAuthStore();
      const response = await axios.get(`${API_BASE_URL}/anomalies`, {
        params: { startDate, endDate, threshold },
        headers: {
          'Authorization': `Bearer ${authStore.token}`,
          'Content-Type': 'application/json'
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error detecting anomalies:', error);
      throw error;
    }
  },

  /**
   * Get payroll summary statistics
   */
  async getPayrollSummary(period: 'current_month' | 'last_month' | 'year_to_date' | 'custom' = 'current_month',
                         startDate?: string,
                         endDate?: string): Promise<{ data: any }> {
    try {
      const authStore = useAuthStore();
      const params: any = { period };
      
      if (startDate) params.startDate = startDate;
      if (endDate) params.endDate = endDate;
      
      const response = await axios.get(`${API_BASE_URL}/summary`, {
        params,
        headers: {
          'Authorization': `Bearer ${authStore.token}`,
          'Content-Type': 'application/json'
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching payroll summary:', error);
      throw error;
    }
  },

  /**
   * Get employee payroll details
   */
  async getEmployeePayrollDetails(employeeId: string, 
                                period: 'current_month' | 'last_month' | 'year_to_date' | 'custom' = 'current_month',
                                startDate?: string,
                                endDate?: string): Promise<{ data: any }> {
    try {
      const authStore = useAuthStore();
      const params: any = { period };
      
      if (startDate) params.startDate = startDate;
      if (endDate) params.endDate = endDate;
      
      const response = await axios.get(`${API_BASE_URL}/employee/${employeeId}`, {
        params,
        headers: {
          'Authorization': `Bearer ${authStore.token}`,
          'Content-Type': 'application/json'
        }
      });
      return response.data;
    } catch (error) {
      console.error(`Error fetching payroll details for employee ${employeeId}:`, error);
      throw error;
    }
  },

  /**
   * Export payroll data
   */
  async exportPayrollData(format: 'pdf' | 'excel' | 'csv' = 'excel',
                         period: 'current_month' | 'last_month' | 'year_to_date' | 'custom' = 'current_month',
                         startDate?: string,
                         endDate?: string): Promise<Blob> {
    try {
      const authStore = useAuthStore();
      const params: any = { format, period };
      
      if (startDate) params.startDate = startDate;
      if (endDate) params.endDate = endDate;
      
      const response = await axios.get(`${API_BASE_URL}/export`, {
        params,
        responseType: 'blob',
        headers: {
          'Authorization': `Bearer ${authStore.token}`,
          'Accept': this.getMimeType(format)
        }
      });
      
      return response.data;
    } catch (error) {
      console.error('Error exporting payroll data:', error);
      throw error;
    }
  },

  /**
   * Get mime type for export format
   */
  getMimeType(format: string): string {
    switch (format) {
      case 'pdf':
        return 'application/pdf';
      case 'excel':
        return 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
      case 'csv':
        return 'text/csv';
      default:
        return 'application/octet-stream';
    }
  },

  /**
   * Get file extension for export format
   */
  getFileExtension(format: string): string {
    switch (format) {
      case 'pdf':
        return 'pdf';
      case 'excel':
        return 'xlsx';
      case 'csv':
        return 'csv';
      default:
        return 'bin';
    }
  }
};

export default PayrollAnalyticsService;
