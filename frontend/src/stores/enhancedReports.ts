import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import enhancedReportsService from '@/services/enhancedReportsService';

export const useEnhancedReportsStore = defineStore('enhancedReports', () => {
  const reports = ref([]);
  const templates = ref([]);
  const schedules = ref([]);
  const loading = ref(false);
  const currentCompanyId = ref(null);

  const recentReports = computed(() => 
    reports.value
      .filter(r => r.status === 'completed')
      .sort((a, b) => new Date(b.generated_at) - new Date(a.generated_at))
      .slice(0, 10)
  );

  const favoriteReports = computed(() => 
    reports.value.filter(r => r.is_favorite)
  );

  const reportsByType = computed(() => {
    const grouped = {};
    reports.value.forEach(report => {
      if (!grouped[report.report_type]) {
        grouped[report.report_type] = [];
      }
      grouped[report.report_type].push(report);
    });
    return grouped;
  });

  const setCurrentCompany = (companyId: string) => {
    currentCompanyId.value = companyId;
  };

  const loadReports = async (companyId?: string) => {
    const targetCompanyId = companyId || currentCompanyId.value;
    if (!targetCompanyId) return;

    loading.value = true;
    try {
      const response = await enhancedReportsService.listCompanyReports(targetCompanyId);
      reports.value = response.data || [];
    } catch (error) {
      console.error('Failed to load reports:', error);
      reports.value = [];
    } finally {
      loading.value = false;
    }
  };

  const generateReport = async (reportType: string, params: any) => {
    if (!currentCompanyId.value) {
      throw new Error('No company selected');
    }

    loading.value = true;
    try {
      let result;
      
      switch (reportType) {
        case 'income_statement':
          result = await enhancedReportsService.generateIncomeStatement(
            currentCompanyId.value,
            params.periodStart,
            params.periodEnd
          );
          break;
          
        case 'balance_sheet':
          result = await enhancedReportsService.generateBalanceSheet(
            currentCompanyId.value,
            params.asOfDate
          );
          break;
          
        case 'cash_flow':
          result = await enhancedReportsService.generateCashFlowStatement(
            currentCompanyId.value,
            params.periodStart,
            params.periodEnd
          );
          break;
          
        case 'aging_report':
          result = await enhancedReportsService.generateAgingReport(
            currentCompanyId.value,
            params.agingType,
            params.asOfDate
          );
          break;
          
        default:
          throw new Error(`Unsupported report type: ${reportType}`);
      }

      if (result.data) {
        reports.value.unshift(result.data);
      }
      
      return result.data;
    } finally {
      loading.value = false;
    }
  };

  const getReport = async (reportId: string) => {
    try {
      const response = await enhancedReportsService.getReport(reportId);
      return response.data;
    } catch (error) {
      console.error('Failed to get report:', error);
      return null;
    }
  };

  const exportReport = async (reportId: string, format: string) => {
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
          throw new Error(`Unsupported format: ${format}`);
      }
    } catch (error) {
      console.error('Export failed:', error);
      throw error;
    }
  };

  const createTemplate = async (templateData: any) => {
    if (!currentCompanyId.value) {
      throw new Error('No company selected');
    }

    try {
      const response = await enhancedReportsService.createReportTemplate(
        currentCompanyId.value,
        templateData
      );
      
      if (response.data) {
        templates.value.push(response.data);
      }
      
      return response.data;
    } catch (error) {
      console.error('Failed to create template:', error);
      throw error;
    }
  };

  const createSchedule = async (scheduleData: any) => {
    if (!currentCompanyId.value) {
      throw new Error('No company selected');
    }

    try {
      const response = await enhancedReportsService.createReportSchedule(
        currentCompanyId.value,
        scheduleData
      );
      
      if (response.data) {
        schedules.value.push(response.data);
      }
      
      return response.data;
    } catch (error) {
      console.error('Failed to create schedule:', error);
      throw error;
    }
  };

  return {
    reports,
    templates,
    schedules,
    loading,
    currentCompanyId,
    recentReports,
    favoriteReports,
    reportsByType,
    setCurrentCompany,
    loadReports,
    generateReport,
    getReport,
    exportReport,
    createTemplate,
    createSchedule
  };
});