import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { glReportingService } from '../services';
import type {
  ReportMetadata,
  ReportParameters,
  ReportGenerationOptions,
  ReportFormat
} from '../services/gl-reporting.service';

interface ScheduledReport {
  id: string;
  name: string;
  frequency: string;
  nextRun: string;
  recipients: string[];
  format: ReportFormat;
  lastRun?: string;
  status?: 'active' | 'paused' | 'error';
}

export const useGlReportingStore = defineStore('glReporting', () => {
  // State
  const availableReports = ref<ReportMetadata[]>([]);
  const scheduledReports = ref<ScheduledReport[]>([]);
  const reportHistory = ref<Array<{
    id: string;
    name: string;
    generatedAt: string;
    format: ReportFormat;
    status: 'completed' | 'failed' | 'processing';
    downloadUrl?: string;
    error?: string;
  }>>([]);
  
  const loading = ref(false);
  const generatingReport = ref(false);
  const error = ref<string | null>(null);
  const selectedReport = ref<ReportMetadata | null>(null);
  const reportParameters = ref<ReportParameters>({
    period: 'monthly',
    includeDetails: true,
    includeSummary: true,
    includeCharts: true,
    compareWithPrevious: true
  });
  const generationOptions = ref<ReportGenerationOptions>({
    format: 'pdf',
    includeCharts: true,
    includeAppendices: true,
    passwordProtect: false,
    watermark: true,
    language: 'en'
  });

  // Getters
  const financialStatements = computed(() => {
    return availableReports.value.filter(
      report => report.category === 'financial-statement'
    );
  });

  const ledgerReports = computed(() => {
    return availableReports.value.filter(
      report => report.category === 'ledger'
    );
  });

  const analyticalReports = computed(() => {
    return availableReports.value.filter(
      report => report.category === 'analytical'
    );
  });

  const regulatoryReports = computed(() => {
    return availableReports.value.filter(
      report => report.category === 'regulatory'
    );
  });

  const activeScheduledReports = computed(() => {
    return scheduledReports.value.filter(report => report.status === 'active');
  });

  const completedReports = computed(() => {
    return reportHistory.value.filter(report => report.status === 'completed');
  });

  const failedReports = computed(() => {
    return reportHistory.value.filter(report => report.status === 'failed');
  });

  // Actions
  async function fetchAvailableReports() {
    try {
      loading.value = true;
      error.value = null;
      const reports = await glReportingService.getAvailableReports();
      availableReports.value = reports;
      return reports;
    } catch (err) {
      error.value = 'Failed to fetch available reports';
      console.error('Error in fetchAvailableReports:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function generateReport(
    reportId: string,
    params: ReportParameters,
    options: ReportGenerationOptions
  ) {
    try {
      generatingReport.value = true;
      error.value = null;
      
      // Map reportId to the appropriate service method
      let result;
      switch (reportId) {
        case 'balance-sheet':
        case 'income-statement':
        case 'cash-flow':
        case 'retained-earnings':
          result = await glReportingService.generateFinancialStatement(
            reportId as any,
            params,
            options
          );
          break;
        case 'general-ledger':
          result = await glReportingService.generateGeneralLedgerReport(
            params as any, // Cast to expected type
            options
          );
          break;
        case 'trial-balance':
          if (!params.endDate) {
            throw new Error('End date is required for trial balance');
          }
          result = await glReportingService.generateTrialBalance(
            params.endDate,
            options
          );
          break;
        default:
          throw new Error(`Unsupported report type: ${reportId}`);
      }

      // Add to history if successful
      if (result) {
        reportHistory.value.unshift({
          id: Date.now().toString(),
          name: availableReports.value.find(r => r.id === reportId)?.name || reportId,
          generatedAt: new Date().toISOString(),
          format: options.format,
          status: 'completed',
          downloadUrl: result instanceof Blob ? 
            URL.createObjectURL(result) : 
            undefined
        });
      }

      return result;
    } catch (err) {
      error.value = `Failed to generate report: ${err instanceof Error ? err.message : 'Unknown error'}`;
      console.error('Error in generateReport:', err);
      
      // Add to history as failed
      reportHistory.value.unshift({
        id: Date.now().toString(),
        name: availableReports.value.find(r => r.id === reportId)?.name || reportId,
        generatedAt: new Date().toISOString(),
        format: options.format,
        status: 'failed',
        error: error.value
      });
      
      throw err;
    } finally {
      generatingReport.value = false;
    }
  }

  async function scheduleReport(
    reportId: string,
    schedule: {
      frequency: 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'yearly';
      time: string;
      recipients: string[];
      format: ReportFormat;
      startDate?: string;
      endDate?: string;
    }
  ) {
    try {
      loading.value = true;
      error.value = null;
      
      const result = await glReportingService.scheduleReport(reportId, schedule);
      
      // Add to scheduled reports
      scheduledReports.value.push({
        id: result.id,
        name: availableReports.value.find(r => r.id === reportId)?.name || reportId,
        frequency: schedule.frequency,
        nextRun: schedule.startDate || new Date().toISOString(),
        recipients: schedule.recipients,
        format: schedule.format,
        status: 'active'
      });
      
      return result;
    } catch (err) {
      error.value = 'Failed to schedule report';
      console.error('Error in scheduleReport:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function fetchScheduledReports() {
    try {
      loading.value = true;
      error.value = null;
      // In a real app, this would fetch from the API
      // For now, we'll just return the local state
      return scheduledReports.value;
    } catch (err) {
      error.value = 'Failed to fetch scheduled reports';
      console.error('Error in fetchScheduledReports:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function deleteScheduledReport(reportId: string) {
    try {
      loading.value = true;
      error.value = null;
      
      // In a real app, this would call the API to delete
      scheduledReports.value = scheduledReports.value.filter(
        report => report.id !== reportId
      );
      
      return true;
    } catch (err) {
      error.value = 'Failed to delete scheduled report';
      console.error('Error in deleteScheduledReport:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  function setReportParameters(params: Partial<ReportParameters>) {
    reportParameters.value = {
      ...reportParameters.value,
      ...params
    };
  }

  function setGenerationOptions(options: Partial<ReportGenerationOptions>) {
    generationOptions.value = {
      ...generationOptions.value,
      ...options
    };
  }

  function selectReport(reportId: string) {
    const report = availableReports.value.find(r => r.id === reportId);
    if (report) {
      selectedReport.value = report;
    }
  }

  function reset() {
    availableReports.value = [];
    scheduledReports.value = [];
    reportHistory.value = [];
    loading.value = false;
    generatingReport.value = false;
    error.value = null;
    selectedReport.value = null;
    reportParameters.value = {
      period: 'monthly',
      includeDetails: true,
      includeSummary: true,
      includeCharts: true,
      compareWithPrevious: true
    };
    generationOptions.value = {
      format: 'pdf',
      includeCharts: true,
      includeAppendices: true,
      passwordProtect: false,
      watermark: true,
      language: 'en'
    };
  }

  // Initialize the store
  function initialize() {
    fetchAvailableReports();
    fetchScheduledReports();
  }

  return {
    // State
    availableReports,
    scheduledReports,
    reportHistory,
    loading,
    generatingReport,
    error,
    selectedReport,
    reportParameters,
    generationOptions,
    
    // Getters
    financialStatements,
    ledgerReports,
    analyticalReports,
    regulatoryReports,
    activeScheduledReports,
    completedReports,
    failedReports,
    
    // Actions
    fetchAvailableReports,
    generateReport,
    scheduleReport,
    fetchScheduledReports,
    deleteScheduledReport,
    setReportParameters,
    setGenerationOptions,
    selectReport,
    initialize,
    reset
  };
});

// Export the store type for use in components
export type GlReportingStore = ReturnType<typeof useGlReportingStore>;
