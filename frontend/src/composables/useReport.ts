import { ref, computed } from 'vue';
import { useStore } from 'vuex';
import { useToast } from 'primevue/usetoast';
import { format, subMonths, startOfMonth, endOfMonth, parseISO } from 'date-fns';

export const useReport = () => {
  const store = useStore();
  const toast = useToast();
  
  // State
  const loading = ref(false);
  const exportLoading = ref(false);
  const dateRange = ref<[Date, Date]>([
    startOfMonth(subMonths(new Date(), 1)),
    endOfMonth(subMonths(new Date(), 1))
  ]);
  
  // Computed
  const formattedDateRange = computed(() => {
    if (!dateRange.value || dateRange.value.length !== 2) return '';
    return `${format(dateRange.value[0], 'MMM d, yyyy')} - ${format(dateRange.value[1], 'MMM d, yyyy')}`;
  });
  
  // Methods
  const handleDateRangeUpdate = (newRange: [Date, Date] | Date[] | null) => {
    if (!newRange || !Array.isArray(newRange) || newRange.length !== 2) return;
    
    // Ensure we have valid Date objects
    const startDate = newRange[0] instanceof Date ? newRange[0] : parseISO(newRange[0]);
    const endDate = newRange[1] instanceof Date ? newRange[1] : parseISO(newRange[1]);
    
    dateRange.value = [startDate, endDate];
  };
  
  const handleExport = async (format: string, exportFunction: () => Promise<void>) => {
    try {
      exportLoading.value = true;
      await exportFunction();
      
      toast.add({
        severity: 'success',
        summary: 'Export Successful',
        detail: `Report exported as ${format.toUpperCase()} successfully.`,
        life: 3000
      });
    } catch (error) {
      console.error(`Error exporting to ${format}:`, error);
      
      toast.add({
        severity: 'error',
        summary: 'Export Failed',
        detail: `Failed to export report as ${format.toUpperCase()}. Please try again.`,
        life: 5000
      });
    } finally {
      exportLoading.value = false;
    }
  };
  
  const exportToPDF = async (generatePdf: () => Promise<void>) => {
    return handleExport('PDF', generatePdf);
  };
  
  const exportToExcel = async (generateExcel: () => Promise<void>) => {
    return handleExport('Excel', generateExcel);
  };
  
  const exportToCSV = async (generateCsv: () => Promise<void>) => {
    return handleExport('CSV', generateCsv);
  };
  
  const formatCurrency = (value: number, currency: string = 'USD', decimals: number = 2): string => {
    if (isNaN(value)) return 'N/A';
    
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    }).format(value);
  };
  
  const formatPercentage = (value: number, decimals: number = 1): string => {
    if (value === null || value === undefined) return 'N/A';
    
    return new Intl.NumberFormat('en-US', {
      style: 'percent',
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    }).format(value / 100);
  };
  
  const formatNumber = (value: number, decimals: number = 0): string => {
    if (isNaN(value)) return 'N/A';
    
    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    }).format(value);
  };
  
  const getChangeClass = (value: number): string => {
    if (value > 0) return 'positive-change';
    if (value < 0) return 'negative-change';
    return 'no-change';
  };
  
  // Helper to generate a unique ID for report exports
  const generateReportId = (prefix: string = 'rpt'): string => {
    return `${prefix}-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
  };
  
  return {
    // State
    loading,
    exportLoading,
    dateRange,
    
    // Computed
    formattedDateRange,
    
    // Methods
    handleDateRangeUpdate,
    handleExport,
    exportToPDF,
    exportToExcel,
    exportToCSV,
    formatCurrency,
    formatPercentage,
    formatNumber,
    getChangeClass,
    generateReportId
  };
};

export default useReport;
