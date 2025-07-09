import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useI18n } from 'vue-i18n';
import reconciliationService from '@/services/gl/reconciliationService';
import type { 
  Reconciliation, 
  ReconciliationAccount, 
  ReconciliationStatus,
  ReconciliationFilter as FilterType,
  UpdateReconciliationData,
  AccountReconciliationStatus
} from '@/types/gl/reconciliation';

interface PaginatedResponse<T> {
  data: T[];
  meta: {
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  };
}

interface UnreconciledTransaction {
  id: string;
  date: string;
  description: string;
  amount: number;
  type: 'debit' | 'credit';
}

interface ReconciliationState {
  reconciliations: Reconciliation[];
  currentReconciliation: Reconciliation | null;
  loading: boolean;
  error: string | null;
  filters: Partial<FilterType>;
  pagination: {
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  };
  unreconciledTransactions: UnreconciledTransaction[];
}

export const useReconciliationStore = defineStore('reconciliation', () => {
  const toast = useToast();
  const { t } = useI18n();
  
  // State
  const state = ref<ReconciliationState>({
    reconciliations: [],
    currentReconciliation: null,
    loading: false,
    error: null,
    filters: {},
    pagination: {
      total: 0,
      page: 1,
      limit: 10,
      totalPages: 1
    },
    unreconciledTransactions: []
  });

  // Getters
  const getReconciliations = computed(() => state.value.reconciliations);
  const getCurrentReconciliation = computed(() => state.value.currentReconciliation);
  const isLoading = computed(() => state.value.loading);
  const getError = computed(() => state.value.error);
  const getFilters = computed(() => state.value.filters);
  const getPagination = computed(() => state.value.pagination);
  const getUnreconciledTransactions = computed(() => state.value.unreconciledTransactions);

  // Helper to handle paginated response
  const handlePaginatedResponse = (response: { data: Reconciliation[] | PaginatedResponse<Reconciliation> }) => {
    if (Array.isArray(response.data)) {
      // Handle non-paginated response (array of reconciliations)
      state.value.reconciliations = response.data;
      state.value.pagination = {
        total: response.data.length,
        page: 1,
        limit: response.data.length,
        totalPages: 1
      };
    } else if (response.data && 'data' in response.data && 'meta' in response.data) {
      // Handle paginated response with meta
      const paginatedResponse = response.data as PaginatedResponse<Reconciliation>;
      state.value.reconciliations = paginatedResponse.data;
      state.value.pagination = {
        total: paginatedResponse.meta.total,
        page: paginatedResponse.meta.page,
        limit: paginatedResponse.meta.limit,
        totalPages: paginatedResponse.meta.totalPages
      };
    } else {
      // Fallback for unexpected response format
      console.warn('Unexpected response format from reconciliation service:', response);
      state.value.reconciliations = [];
      state.value.pagination = {
        total: 0,
        page: 1,
        limit: 10,
        totalPages: 0
      };
    }
  };

  // Computed for paginated reconciliations
  const paginatedReconciliations = computed(() => {
    const start = (state.value.pagination.page - 1) * state.value.pagination.limit;
    const end = start + state.value.pagination.limit;
    return state.value.reconciliations.slice(start, end);
  });

  const totalPages = computed(() => state.value.pagination.totalPages);

  // Actions
  const fetchReconciliations = async (params: Partial<FilterType> = {}): Promise<void> => {
    state.value.loading = true;
    state.value.error = null;
    
    try {
      // Merge filters and pagination params
      const queryParams = {
        ...state.value.filters,
        ...params,
        page: params.page || state.value.pagination.page,
        limit: params.limit || state.value.pagination.limit,
      };
      
      // Remove undefined or empty string values
      const cleanParams = Object.fromEntries(
        Object.entries(queryParams).filter(([_, v]) => v !== undefined && v !== '')
      );
      
      const response = await reconciliationService.getReconciliations(cleanParams);
      handlePaginatedResponse(response);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error fetching reconciliations';
      state.value.error = errorMessage;
      toast.add({
        severity: 'error',
        summary: t('error'),
        detail: errorMessage,
        life: 3000
      });
      throw error;
    } finally {
      state.value.loading = false;
    }
  };
  
  const fetchReconciliationById = async (id: string): Promise<Reconciliation | undefined> => {
    state.value.loading = true;
    state.value.error = null;
    
    try {
      const response = await reconciliationService.getReconciliationById(id);
      state.value.currentReconciliation = response.data;
      return response.data;
    } catch (error) {
      console.error('Error fetching reconciliation:', error);
      const errorMessage = error instanceof Error ? error.message : 'Failed to fetch reconciliation';
      state.value.error = errorMessage;
      toast.add({
        severity: 'error',
        summary: t('error'),
        detail: errorMessage,
        life: 5000
      });
      return undefined;
    } finally {
      state.value.loading = false;
    }
  };

  const createReconciliation = async (
    reconciliation: Omit<Reconciliation, 'id' | 'status' | 'createdAt' | 'updatedAt' | 'accounts' | 'totalAccounts' | 'reconciledAccounts' | 'pendingAccounts' | 'totalDifference' | 'createdByName' | 'updatedByName' | 'completedAt' | 'completedBy' | 'approvedAt' | 'approvedBy' | 'rejectionReason' | 'rejectedBy' | 'rejectedAt' | 'referenceNumber' | 'reconciliationDate' | 'createdBy' | 'updatedBy' | 'notes'>
  ): Promise<Reconciliation> => {
    state.value.loading = true;
    state.value.error = null;
    
    try {
      const response = await reconciliationService.createReconciliation({
        ...reconciliation,
        status: 'draft' as ReconciliationStatus,
        referenceNumber: `REC-${Date.now()}`,
        reconciliationDate: new Date().toISOString(),
        createdBy: 'system', // TODO: Replace with actual user ID from auth store
        updatedBy: 'system', // TODO: Replace with actual user ID from auth store
        notes: ''
      });
      await fetchReconciliations(); // Refresh the list
      return response.data;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to create reconciliation';
      state.value.error = errorMessage;
      toast.add({
        severity: 'error',
        summary: t('error'),
        detail: errorMessage,
        life: 3000
      });
      throw error;
    } finally {
      state.value.loading = false;
    }
  };

  const updateReconciliation = async (
    id: string, 
    updateData: UpdateReconciliationData
  ): Promise<Reconciliation> => {
    state.value.loading = true;
    state.value.error = null;
    
    try {
      const response = await reconciliationService.updateReconciliation(id, updateData);
      const updatedReconciliation = response.data;
      
      // Update the reconciliation in the list if it exists
      const index = state.value.reconciliations.findIndex(r => r.id === id);
      if (index !== -1) {
        state.value.reconciliations[index] = { 
          ...state.value.reconciliations[index], 
          ...updatedReconciliation 
        };
      }
      
      // Update current reconciliation if it's the one being updated
      if (state.value.currentReconciliation?.id === id) {
        state.value.currentReconciliation = { 
          ...state.value.currentReconciliation, 
          ...updatedReconciliation
        };
      }
      
      toast.add({
        severity: 'success',
        summary: t('success'),
        detail: t('reconciliation.updated'),
        life: 3000
      });
      
      return updatedReconciliation;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error updating reconciliation';
      state.value.error = errorMessage;
      toast.add({
        severity: 'error',
        summary: t('error'),
        detail: errorMessage,
        life: 3000
      });
      throw error;
    } finally {
      state.value.loading = false;
    }
  };

  const deleteReconciliation = async (id: string): Promise<boolean> => {
    state.value.loading = true;
    state.value.error = null;
    
    try {
      await reconciliationService.deleteReconciliation(id);
      
      // Remove the deleted reconciliation from the list
      state.value.reconciliations = state.value.reconciliations.filter(
        rec => rec.id !== id
      );
      
      // Clear current reconciliation if it's the one being deleted
      if (state.value.currentReconciliation?.id === id) {
        state.value.currentReconciliation = null;
      }
      
      toast.add({
        severity: 'success',
        summary: t('success'),
        detail: t('reconciliation.deleted'),
        life: 3000
      });
      return true;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : `Failed to delete reconciliation ${id}`;
      state.value.error = errorMessage;
      toast.add({
        severity: 'error',
        summary: t('error'),
        detail: errorMessage,
        life: 3000
      });
      throw error;
    } finally {
      state.value.loading = false;
    }
  };

  const reconcileAccount = async (
    reconciliationId: string,
    accountId: string,
    reconciledBalance: number
  ): Promise<ReconciliationAccount> => {
    state.value.loading = true;
    state.value.error = null;
    
    try {
      const response = await reconciliationService.reconcileAccount(
        reconciliationId,
        accountId,
        reconciledBalance
      );
      
      // Update the account in the current reconciliation
      if (state.value.currentReconciliation) {
        const accountIndex = state.value.currentReconciliation.accounts.findIndex(
          acc => acc.accountId === accountId
        );
        
        if (accountIndex !== -1) {
          state.value.currentReconciliation.accounts[accountIndex] = {
            ...state.value.currentReconciliation.accounts[accountIndex],
            ...response.data,
            status: 'reconciled' as AccountReconciliationStatus,
            reconciledAt: new Date().toISOString(),
            reconciledBy: 'current-user-id' // TODO: Replace with actual user ID from auth store
          };
        }
      }
      
      return response.data;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error reconciling account';
      state.value.error = errorMessage;
      toast.add({
        severity: 'error',
        summary: t('error'),
        detail: errorMessage,
        life: 3000
      });
      throw error;
    } finally {
      state.value.loading = false;
    }
  };

  const finalizeReconciliation = async (id: string): Promise<Reconciliation> => {
    state.value.loading = true;
    state.value.error = null;
    
    try {
      const response = await reconciliationService.finalizeReconciliation(id);
      const updatedReconciliation = response;
      
      // Update the reconciliation in the list if it exists
      const index = state.value.reconciliations.findIndex(r => r.id === id);
      if (index !== -1) {
        state.value.reconciliations[index] = response;
      }
      
      // Update current reconciliation if it's the one being finalized
      if (state.value.currentReconciliation?.id === id) {
        state.value.currentReconciliation = response;
      }
      
      toast.add({
        severity: 'success',
        summary: t('success'),
        detail: t('reconciliation.finalized'),
        life: 3000
      });
      
      return response;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error finalizing reconciliation';
      state.value.error = errorMessage;
      toast.add({
        severity: 'error',
        summary: t('error'),
        detail: errorMessage,
        life: 3000
      });
      throw error;
    } finally {
      state.value.loading = false;
    }
  };

  const fetchUnreconciledTransactions = async (
    accountId: string,
    startDate: string,
    endDate: string
  ): Promise<UnreconciledTransaction[]> => {
    state.value.loading = true;
    state.value.error = null;
    
    try {
      const response = await reconciliationService.getUnreconciledTransactions(
        accountId,
        startDate,
        endDate
      );
      
      const transactions = response.data || [];
      state.value.unreconciledTransactions = transactions;
      return transactions;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error fetching unreconciled transactions';
      state.value.error = errorMessage;
      toast.add({
        severity: 'error',
        summary: t('error'),
        detail: errorMessage,
        life: 3000
      });
      throw error;
    } finally {
      state.value.loading = false;
    }
  };

  const setFilters = (newFilters: Partial<FilterType>): void => {
    state.value.filters = { ...state.value.filters, ...newFilters };
  };

  const resetFilters = (): void => {
    state.value.filters = {};
  };

  return {
    // State
    state,
    
    // Getters
    getReconciliations,
    getCurrentReconciliation,
    isLoading,
    getError,
    getFilters,
    getPagination,
    getUnreconciledTransactions,
    paginatedReconciliations,
    totalPages,
    
    // Actions
    fetchReconciliations,
    fetchReconciliationById,
    createReconciliation,
    updateReconciliation,
    deleteReconciliation,
    reconcileAccount,
    finalizeReconciliation,
    fetchUnreconciledTransactions,
    setFilters,
    resetFilters
  };
});

export default useReconciliationStore;
