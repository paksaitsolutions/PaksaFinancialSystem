import { ref, computed } from 'vue';
import { useStore } from 'vuex';
import { useToast } from 'primevue/usetoast';
import enhancedReportsService from '@/services/enhancedReportsService';

export function useEnhancedReports() {
  const store = useStore();
  const toast = useToast();
  
  const loading = ref(false);
  const exportLoading = ref(false);
  const reports = ref([]);
  
  const currentCompany = computed(() => store.state.auth.currentCompany);
  
  const generateReport = async (reportType: string, params: any) => {
    if (!currentCompany.value?.id) {
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: 'No company selected',
        life: 5000
      });
      return null;
    }
    
    loading.value = true;
    try {
      let result;
      
      switch (reportType) {
        case 'income_statement':
          result = await enhancedReportsService.generateIncomeStatement(
            currentCompany.value.id,
            params.periodStart,
            params.periodEnd
          );
          break;
          
        case 'balance_sheet':
          result = await enhancedReportsService.generateBalanceSheet(
            currentCompany.value.id,
            params.asOfDate
          );
          break;
          
        case 'cash_flow':
          result = await enhancedReportsService.generateCashFlowStatement(
            currentCompany.value.id,
            params.periodStart,
            params.periodEnd
          );
          break;
          
        case 'aging_report':
          result = await enhancedReportsService.generateAgingReport(
            currentCompany.value.id,
            params.agingType,
            params.asOfDate
          );
          break;
          
        case 'tax_summary':
          result = await enhancedReportsService.generateTaxSummaryReport(
            currentCompany.value.id,
            params.periodStart,
            params.periodEnd,
            params.taxType
          );
          break;
          
        default:
          throw new Error(`Unsupported report type: ${reportType}`);
      }
      
      toast.add({
        severity: 'success',
        summary: 'Report Generated',
        detail: 'Report has been generated successfully',
        life: 3000
      });
      
      return result.data;
    } catch (error) {
      console.error('Error generating report:', error);
      toast.add({
        severity: 'error',
        summary: 'Generation Failed',
        detail: 'Failed to generate report',
        life: 5000
      });
      return null;
    } finally {
      loading.value = false;
    }
  };
  
  const exportReport = async (reportId: string, format: string) => {
    exportLoading.value = true;
    try {
      switch (format.toLowerCase()) {
        case 'pdf':
          await enhancedReportsService.exportReportToPDF(reportId);
          break;
        case 'excel':
          await enhancedReportsService.exportReportToExcel(reportId);
          break;
        case 'csv':
          await enhancedReportsService.exportReportToCSV(reportId);
          break;
        default:
          throw new Error(`Unsupported export format: ${format}`);
      }
      
      toast.add({
        severity: 'success',
        summary: 'Export Started',
        detail: `Report export to ${format.toUpperCase()} has been initiated`,
        life: 3000
      });
    } catch (error) {
      console.error('Export error:', error);
      toast.add({
        severity: 'error',
        summary: 'Export Failed',
        detail: 'Failed to export report',
        life: 5000
      });
    } finally {
      exportLoading.value = false;
    }
  };
  
  const loadCompanyReports = async (limit = 100) => {
    if (!currentCompany.value?.id) return;
    
    loading.value = true;
    try {
      const response = await enhancedReportsService.listCompanyReports(
        currentCompany.value.id,
        limit
      );
      reports.value = response.data;
    } catch (error) {
      console.error('Error loading reports:', error);
      toast.add({
        severity: 'error',
        summary: 'Load Failed',
        detail: 'Failed to load company reports',
        life: 5000
      });
    } finally {
      loading.value = false;
    }
  };
  
  const getReport = async (reportId: string) => {
    try {
      const response = await enhancedReportsService.getReport(reportId);
      return response.data;
    } catch (error) {
      console.error('Error getting report:', error);
      toast.add({
        severity: 'error',
        summary: 'Load Failed',
        detail: 'Failed to load report',
        life: 5000
      });
      return null;
    }
  };
  
  return {
    loading,
    exportLoading,
    reports,
    currentCompany,
    generateReport,
    exportReport,
    loadCompanyReports,
    getReport
  };
}