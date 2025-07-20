import { apiClient } from '@/utils/apiClient';
import type { 
  Reconciliation, 
  ReconciliationAccount, 
  ReconciliationStatus, 
  ReconciliationFilter as FilterType 
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

const RECONCILIATION_BASE_URL = '/api/gl/reconciliations';

interface FetchReconciliationsParams extends Partial<FilterType> {
  status?: ReconciliationStatus | '';
  startDate?: string;
  endDate?: string;
  accountId?: string;
  page?: number;
  limit?: number;
  sortBy?: string;
  sortDirection?: 'asc' | 'desc';
}

interface UpdateReconciliationData extends Partial<Reconciliation> {
  // Add properties that can be updated
}

export default {
  /**
   * Fetches all reconciliations with optional filtering
   */
  async getReconciliations(
    params: FetchReconciliationsParams = {}
  ): Promise<{ data: Reconciliation[] | PaginatedResponse<Reconciliation> }> {
    const cleanParams = Object.fromEntries(
      Object.entries(params).filter(([_, v]) => v !== undefined && v !== '')
    );
    return apiClient.get<{ data: Reconciliation[] | PaginatedResponse<Reconciliation> }>(
      RECONCILIATION_BASE_URL,
      { params: cleanParams }
    ).catch((error: unknown) => {
      console.error('Error fetching reconciliations:', error);
      const axiosError = error as { response?: { data?: unknown } };
      throw axiosError.response?.data || error;
    });
  },

  /**
   * Fetches a single reconciliation by ID
   */
  async getReconciliationById(id: string): Promise<{ data: Reconciliation }> {
    return apiClient.get<{ data: Reconciliation }>(
      `${RECONCILIATION_BASE_URL}/${id}`
    ).catch((error: unknown) => {
      console.error(`Error fetching reconciliation ${id}:`, error);
      const axiosError = error as { response?: { data?: unknown } };
      throw axiosError.response?.data || error;
    });
  },

  /**
   * Creates a new reconciliation
   */
  async createReconciliation(
    reconciliationData: Omit<Reconciliation, 'id' | 'createdAt' | 'updatedAt' | 'status'>
  ): Promise<{ data: Reconciliation }> {
    return apiClient.post<{ data: Reconciliation }>(
      RECONCILIATION_BASE_URL,
      reconciliationData
    ).catch((error: unknown) => {
      console.error('Error creating reconciliation:', error);
      const axiosError = error as { response?: { data?: unknown } };
      throw axiosError.response?.data || error;
    });
  },

  /**
   * Updates an existing reconciliation
   */
  async updateReconciliation(
    id: string,
    data: UpdateReconciliationData
  ): Promise<{ data: Reconciliation }> {
    return apiClient.put<{ data: Reconciliation }>(
      `${RECONCILIATION_BASE_URL}/${id}`,
      data
    ).catch((error: unknown) => {
      console.error(`Error updating reconciliation ${id}:`, error);
      const axiosError = error as { response?: { data?: unknown } };
      throw axiosError.response?.data || error;
    });
  },

  /**
   * Deletes a reconciliation
   */
  async deleteReconciliation(id: string): Promise<{ success: boolean }> {
    return apiClient
      .delete<{ success: boolean }>(`${RECONCILIATION_BASE_URL}/${id}`)
      .then(response => ({
        success: response.data?.success ?? false
      }));
  },

  /**
   * Reconciles a specific account within a reconciliation
   */
  async reconcileAccount(
    reconciliationId: string,
    accountId: string,
    reconciledBalance: number
  ): Promise<{ data: ReconciliationAccount }> {
    return apiClient.post<{ data: ReconciliationAccount }>(
      `${RECONCILIATION_BASE_URL}/${reconciliationId}/accounts/${accountId}/reconcile`,
      { reconciledBalance }
    ).catch((error: unknown) => {
      console.error(
        `Error reconciling account ${accountId} for reconciliation ${reconciliationId}:`,
        error
      );
      const axiosError = error as { response?: { data?: unknown } };
      throw axiosError.response?.data || error;
    });
  },

  /**
   * Finalizes a reconciliation, marking it as completed
   */
  async finalizeReconciliation(id: string): Promise<Reconciliation> {
    return apiClient.post<{ data: Reconciliation }>(
      `${RECONCILIATION_BASE_URL}/${id}/finalize`
    ).catch((error: unknown) => {
      console.error(`Error finalizing reconciliation ${id}:`, error);
      const axiosError = error as { response?: { data?: unknown } };
      throw axiosError.response?.data || error;
    });
  },

  /**
   * Gets unreconciled transactions for an account within a date range
   */
  async getUnreconciledTransactions(
    accountId: string,
    startDate: string,
    endDate: string
  ): Promise<{ data: Array<{ id: string; date: string; description: string; amount: number; type: 'debit' | 'credit' }> }> {
    return apiClient
      .get<{ data: Array<{ id: string; date: string; description: string; amount: number; type: 'debit' | 'credit' }> }>(
        `${RECONCILIATION_BASE_URL}/unreconciled-transactions`,
        { params: { accountId, startDate, endDate } }
      )
      .catch((error: unknown) => {
        console.error('Error fetching unreconciled transactions:', error);
        const axiosError = error as { response?: { data?: unknown } };
        throw axiosError.response?.data || error;
      });
  },

  /**
   * Gets reconciliation report data
   */
  async getReconciliationReport(id: string): Promise<Blob> {
    return apiClient
      .get<Blob>(`${RECONCILIATION_BASE_URL}/${id}/report`, {
        responseType: 'blob'
      })
      .catch((error: unknown) => {
        console.error('Error fetching reconciliation report:', error);
        const axiosError = error as { response?: { data?: unknown } };
        throw axiosError.response?.data || error;
      });
  },

  /**
   * Exports reconciliation data
   */
  async exportReconciliation(id: string, format: 'pdf' | 'excel' = 'pdf'): Promise<Blob> {
    return apiClient
      .get<Blob>(`${RECONCILIATION_BASE_URL}/${id}/export`, {
        params: { format },
        responseType: 'blob'
      })
      .catch((error: unknown) => {
        console.error('Error exporting reconciliation:', error);
        const axiosError = error as { response?: { data?: unknown } };
        throw axiosError.response?.data || error;
      });
  }
};
