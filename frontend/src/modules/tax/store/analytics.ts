import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useApi } from '@/composables/useApi';
import { useAuthStore } from '@/modules/auth/store';
import { formatCurrency } from '@/utils/formatters';

// Define local types since we can't import from @/types/tax
interface TaxMetrics {
  totalTax: number;
  avgTaxPerEmployee: number;
  complianceRate: number;
  exemptionUsage: Record<string, number>;
  jurisdictionalBreakdown: Record<string, number>;
  // Add other metric properties as needed
}

export const useTaxAnalyticsStore = defineStore('taxAnalytics', () => {
  const api = useApi();
  const authStore = useAuthStore();

  const selectedPeriod = ref<string>('current_month');
  const periodOptions = [
    { text: 'Current Month', value: 'current_month' },
    { text: 'Current Quarter', value: 'current_quarter' },
    { text: 'Current Year', value: 'current_year' },
    { text: 'Custom Range', value: 'custom' }
  ];

  const analyticsData = ref<TaxMetrics>({
    totalTax: 0,
    avgTaxPerEmployee: 0,
    complianceRate: 0,
    exemptionUsage: {},
    jurisdictionalBreakdown: {}
  });

  const insights = ref({
    compliance: '',
    optimization: '',
    risk: ''
  });

  const loading = ref<boolean>(false);
  const error = ref<string | null>(null);

  async function fetchAnalytics() {
    try {
      loading.value = true;
      error.value = null;
      // Implementation here
    } catch (err) {
      error.value = 'Failed to fetch tax analytics';
      console.error('Error fetching tax analytics:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function exportAnalytics(format: 'csv' | 'excel' | 'pdf') {
    try {
      loading.value = true;
      error.value = null;
      
      // Prepare request parameters
      const params = {
        period: selectedPeriod.value,
        format,
        companyId: authStore.currentCompany?.id
      };

      // Set appropriate headers based on format
      const headers: Record<string, string> = {
        'Accept': 'application/json',
        'Authorization': `Bearer ${authStore.accessToken}`
      };

      if (format === 'pdf') {
        headers['Accept'] = 'application/pdf';
        headers['Response-Type'] = 'blob';
      } else if (format === 'excel') {
        headers['Accept'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
        headers['Response-Type'] = 'blob';
      } else {
        headers['Accept'] = 'text/csv';
        headers['Response-Type'] = 'blob';
      }

      const response = await api.get('/api/tax/analytics/export', {
        params,
        headers,
        responseType: format === 'pdf' || format === 'excel' || format === 'csv' ? 'blob' : 'json'
      });

      // For file downloads, we return the raw response
      if (format === 'pdf' || format === 'excel' || format === 'csv') {
        return response;
      }

      // For JSON responses (if needed in the future)
      return response.data;
    } catch (err: any) {
      error.value = `Failed to export ${format} report`;
      console.error(`Error exporting ${format} report:`, err);
      
      // Handle specific error cases
      if (err.response?.status === 401) {
        authStore.logout();
        throw new Error('Session expired. Please log in again.');
      } else if (err.response?.status === 403) {
        throw new Error('You do not have permission to export tax data.');
      } else if (err.response?.status === 404) {
        throw new Error('No data available for the selected period.');
      }
      
      throw err;
    } finally {
      loading.value = false;
    }
  }

  function calculateComplianceRate(payRuns: any[]): number {
    if (!payRuns.length) return 0;
    const compliant = payRuns.filter(run => run.status === 'compliant').length;
    return (compliant / payRuns.length) * 100;
  }

  function generateInsightsPrompt(metrics: any, taxPolicy: any): string {
    // Implementation here
    return '';
  }

  async function refreshData() {
    await fetchAnalytics();
  }

  return {
    // State
    selectedPeriod,
    periodOptions,
    analyticsData,
    insights,
    loading: computed(() => loading.value),
    error: computed(() => error.value),
    
    // Getters
    formattedTotalTax: computed(() => formatCurrency(analyticsData.value.totalTax)),
    formattedAvgTax: computed(() => formatCurrency(analyticsData.value.avgTaxPerEmployee)),
    formattedComplianceRate: computed(() => `${analyticsData.value.complianceRate.toFixed(1)}%`),
    
    // Actions
    fetchAnalytics,
    exportAnalytics,
    refreshData,
    calculateComplianceRate,
    generateInsightsPrompt
  };
});
