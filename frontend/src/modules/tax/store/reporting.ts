import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useErrorHandling } from '@/composables/useErrorHandling';
import { taxReportingService } from '@/services/api/taxReportingService';
import type {
  TaxLiabilityReportResponse,
  TaxComplianceStatus,
  TaxFiling,
  TaxFilingUpcoming,
  TaxReportFilter,
  TaxFilingCreate,
  TaxFilingSubmit,
  TaxLiabilityReportRequest,
  TaxFilingResponse
} from '@/services/api/taxReportingService';

// Define the TaxFilingDocument type since it's not exported from the service
type TaxFilingDocument = {
  id: string;
  name: string;
  type: string;
  url: string;
  description?: string;
  created_at: string;
  updated_at: string;
};

// Extend the TaxReportFilter interface to include pagination
export interface PaginatedTaxReportFilter extends Omit<TaxReportFilter, 'startDate' | 'endDate'> {
  page?: number;
  pageSize?: number;
  groupBy?: 'day' | 'week' | 'month' | 'quarter' | 'year';
  dateFrom?: string;
  dateTo?: string;
  taxType?: string;
  jurisdiction?: string;
  status?: string;
  search?: string;
  type?: string;
  startDate?: string;
  endDate?: string;
}

// Interface for pagination metadata
interface PaginationMeta {
  page: number;
  pageSize: number;
  total: number;
  totalPages: number;
}

// Interface for the tax liability report state
interface TaxLiabilityReportState {
  report: TaxLiabilityReportResponse | null;
  loading: boolean;
  error: string | null;
  pagination: PaginationMeta;
  filter: PaginatedTaxReportFilter;
}

// Interface for the tax filing state
interface TaxFilingState {
  filings: TaxFiling[];
  currentFiling: TaxFiling | null;
  upcomingFilings: TaxFilingUpcoming[];
  complianceStatus: TaxComplianceStatus | null;
  loading: boolean;
  error: string | null;
  pagination: PaginationMeta;
  filter: TaxReportFilter;
}

export interface TaxReportingState {
  liabilityReport: TaxLiabilityReportState;
  filings: TaxFilingState;
  loading: boolean;
  error: string | null;
}

export const useTaxReportingStore = defineStore('taxReporting', () => {
  const { handleError } = useErrorHandling();

  // Initial state
  const initialState: TaxReportingState = {
    liabilityReport: {
      report: null,
      loading: false,
      error: null,
      pagination: {
        page: 1,
        pageSize: 20,
        total: 0,
        totalPages: 1
      },
      filter: {
        page: 1,
        pageSize: 20,
        groupBy: 'month',
        dateFrom: new Date().toISOString().split('T')[0],
        dateTo: new Date().toISOString().split('T')[0],
        taxType: '',
        jurisdiction: '',
        status: '',
        search: '',
        type: '',
        startDate: new Date().toISOString().split('T')[0],
        endDate: new Date().toISOString().split('T')[0]
      }
    },
    filings: {
      filings: [],
      currentFiling: null,
      upcomingFilings: [],
      complianceStatus: null,
      loading: false,
      error: null,
      pagination: {
        page: 1,
        pageSize: 20,
        total: 0,
        totalPages: 1
      },
      filter: {
        type: '',
        jurisdiction: '',
        status: '',
        startDate: new Date().toISOString().split('T')[0],
        endDate: new Date().toISOString().split('T')[0],
        search: ''
      }
    },
    loading: false,
    error: null
  };

  // State
  const state = ref<TaxReportingState>({
    ...initialState
  });

  // Getters
  const loading = computed(() => state.value.loading);
  const error = computed(() => state.value.error);

  // Tax Liability Report Getters
  const liabilityReport = computed(() => state.value.liabilityReport.report);
  const liabilityReportLoading = computed(() => state.value.liabilityReport.loading);
  const liabilityReportError = computed(() => state.value.liabilityReport.error);
  const liabilityPagination = computed(() => state.value.liabilityReport.pagination);
  const liabilityFilter = computed(() => state.value.liabilityReport.filter);

  // Tax Filing Getters
  const complianceStatus = computed(() => state.value.filings.complianceStatus);
  const upcomingFilings = computed(() => state.value.filings.upcomingFilings);
  const currentFiling = computed(() => state.value.filings.currentFiling);
  const filings = computed(() => state.value.filings.filings);
  const filingsPagination = computed(() => state.value.filings.pagination);
  const filingsFilter = computed(() => state.value.filings.filter);
  const filingsLoading = computed(() => state.value.filings.loading);
  const filingsError = computed(() => state.value.filings.error);

  // Helper to handle errors
  const handleStoreError = (error: unknown): Error => {
    if (error instanceof Error) {
      return error;
    } else if (typeof error === 'string') {
      return new Error(error);
    } else if (error && typeof error === 'object' && 'message' in error) {
      return new Error(String((error as { message: unknown }).message));
    }
    return new Error('An unknown error occurred');
  };

  // Actions
  function setLoading(loading: boolean) {
    state.value.loading = loading;
    state.value.filings.loading = loading;
  }

  function setError(error: string | null) {
    if (error !== null && error !== undefined) {
      state.value.error = error;
    } else {
      state.value.error = 'An unknown error occurred';
    }
  }

  /**
   * Updates the pagination for the liability report
   */
  function setLiabilityPagination(pagination: Partial<PaginationMeta>) {
    state.value.liabilityReport.pagination = {
      ...state.value.liabilityReport.pagination,
      ...pagination
    };
  }

  /**
   * Updates the filter for the liability report
   */
  function setLiabilityFilter(filter: Partial<PaginatedTaxReportFilter>) {
    state.value.liabilityReport.filter = {
      ...state.value.liabilityReport.filter,
      ...filter
    };
  }

  function setFilter(newFilter: Partial<TaxReportFilter & { taxType?: string }>) {
    // Remove taxType if present as it's not part of TaxReportFilter
    const { taxType, ...validFilter } = newFilter;
    state.value.filings.filter = { 
      ...state.value.filings.filter, 
      ...validFilter 
    };
  }

  function resetFilter() {
    state.value.filings.filter = {
      type: '',
      jurisdiction: '',
      status: '',
      startDate: new Date().toISOString().split('T')[0],
      endDate: new Date().toISOString().split('T')[0],
      search: ''
    };
  }

  /**
   * Fetches a paginated tax liability report
   */
  async function fetchTaxLiabilityReport(filter: Partial<PaginatedTaxReportFilter> = {}) {
    try {
      // Update the filter in the state
      state.value.liabilityReport.filter = {
        ...state.value.liabilityReport.filter,
        ...filter,
        page: filter.page || 1,
        pageSize: filter.pageSize || 20
      };

      // Set loading state
      state.value.liabilityReport.loading = true;
      state.value.liabilityReport.error = null;

      // Prepare the request payload with only valid properties
      const requestPayload: TaxLiabilityReportRequest = {
        startDate: state.value.liabilityReport.filter.dateFrom || new Date().toISOString().split('T')[0],
        endDate: state.value.liabilityReport.filter.dateTo || new Date().toISOString().split('T')[0],
        page: state.value.liabilityReport.filter.page || 1,
        pageSize: state.value.liabilityReport.filter.pageSize || 20,
        groupBy: (state.value.liabilityReport.filter.groupBy as 'day' | 'week' | 'month' | 'quarter' | 'year') || 'month'
      };

      // Add optional filters if they exist
      if (state.value.liabilityReport.filter.taxType) {
        requestPayload.taxTypes = [state.value.liabilityReport.filter.taxType];
      }

      if (state.value.liabilityReport.filter.jurisdiction) {
        requestPayload.jurisdictionCodes = [state.value.liabilityReport.filter.jurisdiction];
      }

      // Call the API
      const response = await taxReportingService.generateTaxLiabilityReport(requestPayload);

      // Update the report and pagination in the state
      state.value.liabilityReport.report = response.data;

      if (response.data?.pagination) {
        state.value.liabilityReport.pagination = {
          page: response.data.pagination.page,
          pageSize: response.data.pagination.page_size,
          total: response.data.pagination.total_items,
          totalPages: response.data.pagination.total_pages
        };
      }

      return response.data;
    } catch (err) {
      const error = handleStoreError(err);
      state.value.liabilityReport.error = error.message;
      throw error;
    } finally {
      state.value.liabilityReport.loading = false;
    }
  }

  async function fetchTaxComplianceStatus(companyId: string) {
    try {
      state.value.filings.loading = true;
      state.value.filings.error = null;
      const response = await taxReportingService.getTaxComplianceStatus(companyId);
      state.value.filings.complianceStatus = response.data;
      return response.data;
    } catch (err) {
      const error = handleStoreError(err);
      state.value.filings.error = 'Failed to fetch tax compliance status';
      throw error;
    } finally {
      state.value.filings.loading = false;
    }
  }

  async function fetchUpcomingTaxFilings(companyId: string) {
    try {
      state.value.filings.loading = true;
      state.value.filings.error = null;
      const response = await taxReportingService.getUpcomingTaxFilings(companyId);
      state.value.filings.upcomingFilings = response.data || [];
      return response.data;
    } catch (err) {
      const error = handleStoreError(err);
      state.value.filings.error = 'Failed to fetch upcoming tax filings';
      throw error;
    } finally {
      state.value.filings.loading = false;
    }
  }

  async function fetchTaxFiling(filingId: string) {
    try {
      state.value.filings.loading = true;
      state.value.filings.error = null;
      const response = await taxReportingService.getTaxFiling(filingId);
      state.value.filings.currentFiling = response.data?.filing || null;
      return response.data;
    } catch (err) {
      const error = handleStoreError(err);
      state.value.filings.error = 'Failed to fetch tax filing';
      throw error;
    } finally {
      state.value.filings.loading = false;
    }
  }

  async function fetchTaxFilings(
    companyId: string,
    filter: Partial<TaxReportFilter & { taxType?: string }> = {},
    page: number = 1,
    pageSize: number = 20
  ) {
    try {
      state.value.filings.loading = true;
      state.value.filings.error = null;

      // Ensure required filter fields have default values and remove taxType
      const { taxType, ...validFilter } = filter;
      const effectiveFilter: TaxReportFilter = {
        startDate: validFilter.startDate || new Date().toISOString().split('T')[0],
        endDate: validFilter.endDate || new Date().toISOString().split('T')[0],
        type: validFilter.type || '',
        status: validFilter.status || '',
        jurisdiction: validFilter.jurisdiction || '',
        search: validFilter.search || ''
      };

      const response = await taxReportingService.getTaxFilings(
        companyId,
        effectiveFilter,
        page,
        pageSize
      );

      state.value.filings.filings = response.data || [];

      if (response.pagination) {
        state.value.filings.pagination = {
          total: response.pagination.total || 0,
          page: response.pagination.page || page,
          pageSize: response.pagination.page_size || pageSize,
          totalPages: response.pagination.total_pages || 1
        };
      }

      // Update the filter in state
      state.value.filings.filter = { ...effectiveFilter };

      return response;
    } catch (err) {
      const error = handleStoreError(err);
      state.value.filings.error = 'Failed to fetch tax filings';
      throw error;
    } finally {
      state.value.filings.loading = false;
    }
  }

  async function prepareTaxFiling(filing: TaxFilingCreate) {
    try {
      state.value.filings.loading = true;
      state.value.filings.error = null;
      const response = await taxReportingService.prepareTaxFiling(filing);
      return response.data;
    } catch (err) {
      const error = handleStoreError(err);
      state.value.filings.error = 'Failed to prepare tax filing';
      throw error;
    } finally {
      state.value.filings.loading = false;
    }
  }

  async function submitTaxFiling(filingId: string, data: TaxFilingSubmit): Promise<TaxFiling> {
    try {
      state.value.filings.loading = true;
      state.value.filings.error = null;
      
      // Submit the filing
      const response = await taxReportingService.submitTaxFiling(filingId, data);
      const updatedFiling = response as unknown as TaxFiling;
      
      // Update the current filing in state
      if (state.value.filings.currentFiling?.id === filingId) {
        state.value.filings.currentFiling = updatedFiling;
      }
      
      // Update in filings list if present
      const filingIndex = state.value.filings.filings.findIndex(f => f.id === filingId);
      if (filingIndex !== -1) {
        state.value.filings.filings[filingIndex] = updatedFiling;
      }
      
      return updatedFiling;
    } catch (err) {
      const error = handleStoreError(err);
      state.value.filings.error = 'Failed to submit tax filing';
      throw error;
    } finally {
      state.value.filings.loading = false;
    }
  }

  async function downloadFilingDocument(filingId: string, documentId: string): Promise<Blob> {
    try {
      state.value.loading = true;
      state.value.error = null;
      const response = await taxReportingService.downloadFilingDocument(filingId, documentId);
      return response as unknown as Blob; // Assuming the service returns a Blob directly
    } catch (err) {
      const error = handleStoreError(err);
      state.value.error = 'Failed to download document';
      throw error;
    } finally {
      state.value.loading = false;
    }
  }

  async function uploadFilingDocument(
    filingId: string, 
    file: File, 
    documentType: string,
    description?: string
  ): Promise<{ id: string; name: string; type: string; url: string; uploaded_at: string }> {
    try {
      state.value.loading = true;
      state.value.error = null;

      // Validate file type and size
      const validTypes = ['application/pdf', 'image/jpeg', 'image/png'];
      const maxSize = 10 * 1024 * 1024; // 10MB

      if (!validTypes.includes(file.type)) {
        throw new Error('Invalid file type. Please upload a PDF, JPEG, or PNG file.');
      }

      if (file.size > maxSize) {
        throw new Error('File size exceeds the maximum limit of 10MB.');
      }

      const formData = new FormData();
      formData.append('file', file);
      formData.append('documentType', documentType);
      
      if (description) {
        formData.append('description', description);
      }

      const response = await taxReportingService.uploadFilingDocument(filingId, formData);
      const document = response as unknown as TaxFilingDocument;
      
      // Update the current filing's documents if this is the current filing
      const currentFiling = state.value.filings.currentFiling;
      if (currentFiling?.id === filingId) {
        state.value.filings.currentFiling = {
          ...currentFiling,
          documents: [
            ...(currentFiling.documents || []),
            document
          ]
        };
      }
      
      // Return the document with the expected type
      return {
        id: document.id,
        name: document.name,
        type: document.type,
        url: document.url,
        uploaded_at: document.created_at
      };
    } catch (err) {
      const error = handleStoreError(err);
      state.value.error = 'Failed to upload document';
      throw error;
    } finally {
      state.value.loading = false;
    }
  }

  async function deleteFilingDocument(filingId: string, documentId: string): Promise<void> {
    try {
      state.value.loading = true;
      state.value.error = null;

      await taxReportingService.deleteFilingDocument(filingId, documentId);

      // Remove the document from the current filing if it's the current one
      const currentFiling = state.value.filings.currentFiling;
      if (currentFiling?.id === filingId) {
        state.value.filings.currentFiling = {
          ...currentFiling,
          documents: (currentFiling.documents || []).filter(
            (doc: TaxFilingDocument) => doc.id !== documentId
          )
        };
      }
      
      // Also remove from the filings list if it exists there
      const filingIndex = state.value.filings.filings.findIndex(f => f.id === filingId);
      if (filingIndex !== -1) {
        const updatedFiling = {
          ...state.value.filings.filings[filingIndex],
          documents: (state.value.filings.filings[filingIndex].documents || []).filter(
            (doc: TaxFilingDocument) => doc.id !== documentId
          )
        };
        state.value.filings.filings.splice(filingIndex, 1, updatedFiling);
      }
    } catch (err) {
      const error = handleStoreError(err);
      state.value.error = 'Failed to delete document';
      throw error;
    } finally {
      state.value.loading = false;
    }
  }

  async function exportTaxReport(
    format: 'pdf' | 'excel' | 'csv', 
    filter: TaxReportFilter & { startDate: string; endDate: string }
  ): Promise<Blob> {
    try {
      state.value.loading = true;
      state.value.error = null;
      
      // Ensure required fields are present
      const exportFilter: TaxLiabilityReportRequest = {
        startDate: filter.startDate || new Date().toISOString().split('T')[0],
        endDate: filter.endDate || new Date().toISOString().split('T')[0],
        page: 1,
        pageSize: 1000, // Export all records
        groupBy: 'month' as const
      };

      // Add optional filters if they exist
      if (filter.type) {
        exportFilter.taxTypes = [filter.type];
      }

      if (filter.jurisdiction) {
        exportFilter.jurisdictionCodes = [filter.jurisdiction];
      }

      const response = await taxReportingService.exportTaxReport(format, exportFilter);
      return response as unknown as Blob; // Assuming the service returns a Blob directly
    } catch (err) {
      const error = handleStoreError(err);
      state.value.error = `Failed to export ${format.toUpperCase()} report`;
      throw error;
    } finally {
      state.value.loading = false;
    }
  }

  function $reset() {
    state.value = JSON.parse(JSON.stringify(initialState));
  }

  return {
    // State
    state,

    // Getters
    isLoading: computed(() => state.value.loading),
    error: computed(() => state.value.error),
    liabilityReport: computed(() => state.value.liabilityReport),
    filings: computed(() => state.value.filings),
    liabilityPagination: computed(() => state.value.liabilityReport.pagination),
    liabilityFilter: computed(() => state.value.liabilityReport.filter),
    complianceStatus: computed(() => state.value.filings.complianceStatus),
    upcomingFilings: computed(() => state.value.filings.upcomingFilings),
    currentFiling: computed(() => state.value.filings.currentFiling),
    filingsList: computed(() => state.value.filings.filings),
    filingsPagination: computed(() => state.value.filings.pagination),
    filingsFilter: computed(() => state.value.filings.filter),
    filingsLoading: computed(() => state.value.filings.loading),
    filingsError: computed(() => state.value.filings.error),

    // Actions
    setLoading,
    setError,
    setLiabilityPagination,
    setLiabilityFilter,
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
    $reset
  } as const;
});
