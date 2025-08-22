import { ref, computed, onMounted } from 'vue';
import { useTaxReportingStore } from '@/modules/tax/store/reporting';
import type { TaxReportFilter, TaxFilingCreate, TaxFilingSubmit } from '@/types/tax/reporting';

export function useTaxReporting() {
  const store = useTaxReportingStore();
  const isInitialized = ref(false);

  // State from store
  const isLoading = computed(() => store.isLoading);
  const error = computed(() => store.error);
  const liabilityReport = computed(() => store.liabilityReport);
  const complianceStatus = computed(() => store.complianceStatus);
  const upcomingFilings = computed(() => store.upcomingFilings);
  const currentFiling = computed(() => store.currentFiling);
  const filings = computed(() => store.filings);
  const pagination = computed(() => store.pagination);
  const filter = computed(() => store.filter);

  // Computed properties
  const hasUpcomingFilings = computed(() => upcomingFilings.value.length > 0);
  const hasFilings = computed(() => filings.value.length > 0);
  const hasLiabilityData = computed(() => {
    return liabilityReport.value !== null && liabilityReport.value.periods.length > 0;
  });
  const hasComplianceData = computed(() => {
    return complianceStatus.value !== null;
  });
  const isCompliant = computed(() => {
    return complianceStatus.value?.overall_status === 'compliant';
  });

  // Initialize the composable
  const initialize = async () => {
    if (isInitialized.value) return;
    
    try {
      await Promise.all([
        store.fetchTaxComplianceStatus(),
        store.fetchUpcomingTaxFilings(90),
        store.fetchTaxFilings({ limit: 5 })
      ]);
      
      isInitialized.value = true;
    } catch (error) {
      console.error('Failed to initialize tax reporting:', error);
      throw error;
    }
  };

  // Fetch tax liability report
  const fetchTaxLiabilityReport = async (filter: TaxReportFilter) => {
    try {
      return await store.fetchTaxLiabilityReport(filter);
    } catch (error) {
      console.error('Failed to fetch tax liability report:', error);
      throw error;
    }
  };

  // Fetch tax compliance status
  const fetchTaxComplianceStatus = async (taxTypes?: string[], jurisdictionCodes?: string[]) => {
    try {
      return await store.fetchTaxComplianceStatus(taxTypes, jurisdictionCodes);
    } catch (error) {
      console.error('Failed to fetch tax compliance status:', error);
      throw error;
    }
  };

  // Fetch upcoming tax filings
  const fetchUpcomingTaxFilings = async (daysAhead = 90) => {
    try {
      return await store.fetchUpcomingTaxFilings(daysAhead);
    } catch (error) {
      console.error('Failed to fetch upcoming tax filings:', error);
      throw error;
    }
  };

  // Fetch tax filing by ID
  const fetchTaxFiling = async (filingId: string) => {
    try {
      return await store.fetchTaxFiling(filingId);
    } catch (error) {
      console.error('Failed to fetch tax filing:', error);
      throw error;
    }
  };

  // Fetch tax filings with filtering and pagination
  const fetchTaxFilings = async (filter: Partial<TaxReportFilter> = {}) => {
    try {
      return await store.fetchTaxFilings(filter);
    } catch (error) {
      console.error('Failed to fetch tax filings:', error);
      throw error;
    }
  };

  // Prepare a tax filing
  const prepareTaxFiling = async (filingData: TaxFilingCreate) => {
    try {
      return await store.prepareTaxFiling(filingData);
    } catch (error) {
      console.error('Failed to prepare tax filing:', error);
      throw error;
    }
  };

  // Submit a tax filing
  const submitTaxFiling = async (filingId: string, submissionData: TaxFilingSubmit) => {
    try {
      return await store.submitTaxFiling(filingId, submissionData);
    } catch (error) {
      console.error('Failed to submit tax filing:', error);
      throw error;
    }
  };

  // Download tax filing document
  const downloadFilingDocument = async (filingId: string, documentId: string) => {
    try {
      return await store.downloadFilingDocument(filingId, documentId);
    } catch (error) {
      console.error('Failed to download tax filing document:', error);
      throw error;
    }
  };

  // Upload document to tax filing
  const uploadFilingDocument = async (
    filingId: string,
    file: File,
    documentType: string,
    description?: string
  ) => {
    try {
      return await store.uploadFilingDocument(filingId, file, documentType, description);
    } catch (error) {
      console.error('Failed to upload tax filing document:', error);
      throw error;
    }
  };

  // Delete tax filing document
  const deleteFilingDocument = async (filingId: string, documentId: string) => {
    try {
      await store.deleteFilingDocument(filingId, documentId);
    } catch (error) {
      console.error('Failed to delete tax filing document:', error);
      throw error;
    }
  };

  // Export tax report
  const exportTaxReport = async (format: 'csv' | 'excel' | 'pdf', filter: TaxReportFilter) => {
    try {
      return await store.exportTaxReport(format, filter);
    } catch (error) {
      console.error(`Failed to export tax report as ${format}:`, error);
      throw error;
    }
  };

  // Set filter
  const setFilter = (newFilter: Partial<TaxReportFilter>) => {
    store.setFilter(newFilter);
  };

  // Reset filter
  const resetFilter = () => {
    store.resetFilter();
  };

  // Initialize on mount if in a component
  onMounted(() => {
    initialize();
  });

  return {
    // State
    isLoading,
    error,
    liabilityReport,
    complianceStatus,
    upcomingFilings,
    currentFiling,
    filings,
    pagination,
    filter,
    
    // Computed
    hasUpcomingFilings,
    hasFilings,
    hasLiabilityData,
    hasComplianceData,
    isCompliant,
    
    // Actions
    initialize,
    fetchTaxLiabilityReport,
    fetchTaxComplianceStatus,
    fetchUpcomingTaxFilings,
    fetchTaxFiling,
    fetchTaxFilings,
    prepareTaxFiling,
    submitTaxFiling,
    downloadFilingDocument,
    uploadFilingDocument,
    deleteFilingDocument,
    exportTaxReport,
    setFilter,
    resetFilter
  };
}

export default useTaxReporting;
