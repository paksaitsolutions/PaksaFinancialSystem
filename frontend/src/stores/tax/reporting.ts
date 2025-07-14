import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useErrorHandling } from '@/composables/useErrorHandling';
import taxReportingService, {
  TaxLiabilityReport,
  TaxFiling,
  TaxFilingCreate,
  TaxFilingSubmit,
  TaxComplianceStatus,
  TaxFilingUpcoming,
  TaxReportFilter,
  TaxReportResponse,
  TaxFilingResponse
} from '@/services/api/taxReportingService';

interface TaxReportingState {
  isLoading: boolean;
  error: string | null;
  liabilityReport: TaxLiabilityReport | null;
  complianceStatus: TaxComplianceStatus | null;
  upcomingFilings: TaxFilingUpcoming[];
  currentFiling: TaxFiling | null;
  filings: TaxFiling[];
  pagination: {
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  };
  filter: TaxReportFilter;
}

export const useTaxReportingStore = defineStore('taxReporting', () => {
  // State
  const state = ref<TaxReportingState>({
    isLoading: false,
    error: null,
    liabilityReport: null,
    complianceStatus: null,
    upcomingFilings: [],
    currentFiling: null,
    filings: [],
    pagination: {
      total: 0,
      page: 1,
      limit: 10,
      totalPages: 1
    },
    filter: {
      start_date: '',
      end_date: '',
      tax_types: [],
      jurisdiction_codes: [],
      group_by: 'month',
      statuses: [],
      sort_by: 'due_date',
      sort_order: 'asc',
      page: 1,
      limit: 10
    }
  });

  const { handleError } = useErrorHandling();

  // Getters
  const isLoading = computed(() => state.value.isLoading);
  const error = computed(() => state.value.error);
  const liabilityReport = computed(() => state.value.liabilityReport);
  const complianceStatus = computed(() => state.value.complianceStatus);
  const upcomingFilings = computed(() => state.value.upcomingFilings);
  const currentFiling = computed(() => state.value.currentFiling);
  const filings = computed(() => state.value.filings);
  const pagination = computed(() => state.value.pagination);
  const filter = computed(() => state.value.filter);

  // Actions
  const setLoading = (loading: boolean) => {
    state.value.isLoading = loading;
  };

  const setError = (error: string | null) => {
    state.value.error = error;
  };

  const setFilter = (newFilter: Partial<TaxReportFilter>) => {
    state.value.filter = { ...state.value.filter, ...newFilter };
  };

  const resetFilter = () => {
    state.value.filter = {
      start_date: '',
      end_date: '',
      tax_types: [],
      jurisdiction_codes: [],
      group_by: 'month',
      statuses: [],
      sort_by: 'due_date',
      sort_order: 'asc',
      page: 1,
      limit: 10
    };
  };

  // Fetch tax liability report
  const fetchTaxLiabilityReport = async (filter: TaxReportFilter) => {
    try {
      setLoading(true);
      setError(null);
      
      // Update the filter in the state
      setFilter(filter);
      
      const report = await taxReportingService.getTaxLiabilityReport(filter);
      state.value.liabilityReport = report;
      return report;
    } catch (error) {
      const errorMessage = handleError(error, 'Failed to fetch tax liability report');
      setError(errorMessage);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // Fetch tax compliance status
  const fetchTaxComplianceStatus = async (taxTypes?: string[], jurisdictionCodes?: string[]) => {
    try {
      setLoading(true);
      setError(null);
      
      const status = await taxReportingService.getTaxComplianceStatus(taxTypes, jurisdictionCodes);
      state.value.complianceStatus = status;
      return status;
    } catch (error) {
      const errorMessage = handleError(error, 'Failed to fetch tax compliance status');
      setError(errorMessage);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // Fetch upcoming tax filings
  const fetchUpcomingTaxFilings = async (daysAhead = 90) => {
    try {
      setLoading(true);
      setError(null);
      
      const filings = await taxReportingService.getUpcomingTaxFilings(daysAhead);
      state.value.upcomingFilings = filings;
      return filings;
    } catch (error) {
      const errorMessage = handleError(error, 'Failed to fetch upcoming tax filings');
      setError(errorMessage);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // Fetch tax filing by ID
  const fetchTaxFiling = async (filingId: string) => {
    try {
      setLoading(true);
      setError(null);
      
      const filing = await taxReportingService.getTaxFiling(filingId);
      state.value.currentFiling = filing;
      return filing;
    } catch (error) {
      const errorMessage = handleError(error, 'Failed to fetch tax filing');
      setError(errorMessage);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // Fetch tax filings with filtering and pagination
  const fetchTaxFilings = async (filter: Partial<TaxReportFilter> = {}) => {
    try {
      setLoading(true);
      setError(null);
      
      // Merge with current filter
      const mergedFilter = { ...state.value.filter, ...filter };
      setFilter(mergedFilter);
      
      const response = await taxReportingService.getTaxFilings(mergedFilter);
      
      state.value.filings = response.data;
      state.value.pagination = {
        total: response.pagination.total,
        page: response.pagination.page || 1,
        limit: response.pagination.limit || 10,
        totalPages: response.pagination.total_pages || 1
      };
      
      return response;
    } catch (error) {
      const errorMessage = handleError(error, 'Failed to fetch tax filings');
      setError(errorMessage);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // Prepare a tax filing
  const prepareTaxFiling = async (filingData: TaxFilingCreate): Promise<TaxFiling> => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await taxReportingService.prepareTaxFiling(filingData);
      
      // Add to the filings list if not already there
      const existingIndex = state.value.filings.findIndex(f => f.id === response.id);
      if (existingIndex === -1) {
        state.value.filings.unshift(response);
      }
      
      return response;
    } catch (error) {
      const errorMessage = handleError(error, 'Failed to prepare tax filing');
      setError(errorMessage);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // Submit a tax filing
  const submitTaxFiling = async (filingId: string, submissionData: TaxFilingSubmit): Promise<TaxFiling> => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await taxReportingService.submitTaxFiling(filingId, submissionData);
      
      // Update in the filings list
      const index = state.value.filings.findIndex(f => f.id === filingId);
      if (index !== -1) {
        state.value.filings[index] = response;
      }
      
      // Update current filing if it's the one being submitted
      if (state.value.currentFiling?.id === filingId) {
        state.value.currentFiling = response;
      }
      
      return response;
    } catch (error) {
      const errorMessage = handleError(error, 'Failed to submit tax filing');
      setError(errorMessage);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // Download tax filing document
  const downloadFilingDocument = async (filingId: string, documentId: string): Promise<Blob> => {
    try {
      setLoading(true);
      setError(null);
      
      return await taxReportingService.downloadFilingDocument(filingId, documentId);
    } catch (error) {
      const errorMessage = handleError(error, 'Failed to download tax filing document');
      setError(errorMessage);
      throw error;
    } finally {
      setLoading(false);
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
      setLoading(true);
      setError(null);
      
      const response = await taxReportingService.uploadFilingDocument(
        filingId,
        file,
        documentType,
        description
      );
      
      // Update current filing if it's the one being modified
      if (state.value.currentFiling?.id === filingId) {
        state.value.currentFiling.documents = state.value.currentFiling.documents || [];
        state.value.currentFiling.documents.push(response);
      }
      
      return response;
    } catch (error) {
      const errorMessage = handleError(error, 'Failed to upload tax filing document');
      setError(errorMessage);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // Delete tax filing document
  const deleteFilingDocument = async (filingId: string, documentId: string): Promise<void> => {
    try {
      setLoading(true);
      setError(null);
      
      await taxReportingService.deleteFilingDocument(filingId, documentId);
      
      // Remove from current filing if it's the one being modified
      if (state.value.currentFiling?.id === filingId) {
        state.value.currentFiling.documents = state.value.currentFiling.documents?.filter(
          doc => doc.id !== documentId
        ) || [];
      }
    } catch (error) {
      const errorMessage = handleError(error, 'Failed to delete tax filing document');
      setError(errorMessage);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // Export tax report
  const exportTaxReport = async (
    format: 'csv' | 'excel' | 'pdf',
    filter: TaxReportFilter
  ): Promise<Blob> => {
    try {
      setLoading(true);
      setError(null);
      
      return await taxReportingService.exportTaxReport(format, filter);
    } catch (error) {
      const errorMessage = handleError(error, `Failed to export tax report as ${format}`);
      setError(errorMessage);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // Reset store state
  const reset = () => {
    state.value = {
      isLoading: false,
      error: null,
      liabilityReport: null,
      complianceStatus: null,
      upcomingFilings: [],
      currentFiling: null,
      filings: [],
      pagination: {
        total: 0,
        page: 1,
        limit: 10,
        totalPages: 1
      },
      filter: {
        start_date: '',
        end_date: '',
        tax_types: [],
        jurisdiction_codes: [],
        group_by: 'month',
        statuses: [],
        sort_by: 'due_date',
        sort_order: 'asc',
        page: 1,
        limit: 10
      }
    };
  };

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
    
    // Actions
    setLoading,
    setError,
    setFilter,
    resetFilter,
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
    reset
  };
});

export default useTaxReportingStore;
