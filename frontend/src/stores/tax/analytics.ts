import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useApi } from '@/composables/useApi';
import { useAuthStore } from '@/stores/auth';
import { formatCurrency, formatDate } from '@/utils/formatters';
import { TaxPeriod, TaxMetrics, TaxAnalyticsRequest, TaxAnalyticsResponse } from '@/types/tax';

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

  const isLoading = ref(false);
  const error = ref<string | null>(null);

  const totalTax = computed(() => analyticsData.value.totalTax);
  const avgTaxPerEmployee = computed(() => analyticsData.value.avgTaxPerEmployee);
  const complianceRate = computed(() => analyticsData.value.complianceRate.toFixed(2));
  const totalExemptions = computed(() => analyticsData.value.totalExemptions);

  async function fetchAnalytics() {
    try {
      isLoading.value = true;
      error.value = null;

      // Fetch analytics from backend
      const response = await api.post<TaxAnalyticsResponse>('/api/tax/analytics', {
        period: selectedPeriod.value
      });

      // Update store with response data
      analyticsData.value = response.metrics;
      insights.value = response.insights;

    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch analytics';
      console.error('Error fetching tax analytics:', err);
    } finally {
      isLoading.value = false;
    }
  }

  // Export analytics data
  async function exportAnalytics(format: 'csv' | 'excel' | 'pdf') {
    try {
      isLoading.value = true;
      error.value = null;

      const response = await api.get(`api/tax/analytics/export?period=${selectedPeriod.value}&format=${format}`);
      return response;

    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to export analytics';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  function calculateComplianceRate(payRuns: any[]): number {
    let compliantRuns = 0;
    let totalRuns = payRuns.length;

    payRuns.forEach(run => {
      if (run.complianceStatus === 'compliant') {
        compliantRuns++;
      }
    });

    return (compliantRuns / totalRuns) * 100;
  }

  function generateInsightsPrompt(metrics: any, taxPolicy: any): string {
    return `Analyze the following tax metrics and provide insights based on the current tax policy:

    Metrics:
    - Total Tax Amount: ${formatCurrency(metrics.totalTax)}
    - Average Tax per Employee: ${formatCurrency(metrics.avgTaxPerEmployee)}
    - Compliance Rate: ${metrics.complianceRate}%
    - Exemption Usage: ${JSON.stringify(metrics.exemptionUsage)}
    - Jurisdictional Breakdown: ${JSON.stringify(metrics.jurisdictionalBreakdown)}

    Current Tax Policy:
    ${JSON.stringify(taxPolicy)}

    Provide insights in three categories:
    1. Compliance Analysis
    2. Optimization Recommendations
    3. Risk Assessment`;
  }

  function refreshData() {
    fetchAnalytics();
  }

  return {
    selectedPeriod,
    periodOptions,
    analyticsData,
    insights,
    isLoading,
    error,
    totalTax,
    avgTaxPerEmployee,
    complianceRate,
    totalExemptions,
    fetchAnalytics,
    refreshData,
    exportAnalytics
  };
});
