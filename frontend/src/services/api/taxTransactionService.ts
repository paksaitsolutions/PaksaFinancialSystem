import { apiClient } from '@/utils/apiClient';
import { 
  TaxTransaction, 
  TaxTransactionCreate, 
  TaxTransactionUpdate, 
  TaxTransactionFilter,
  TaxTransactionComponent
} from '@/types/tax';
import { 
  PaginatedResponse, 
  ApiResponse, 
  UUID 
} from '@/types/common';

export class TaxTransactionService {
  private baseUrl = '/api/v1/tax/transactions';

  /**
   * Create a new tax transaction
   */
  async createTransaction(data: TaxTransactionCreate): Promise<TaxTransaction> {
    try {
      const response = await apiClient.post<ApiResponse<{ transaction: TaxTransaction }>>(
        this.baseUrl, 
        data
      );
      return response.data.transaction;
    } catch (error) {
      this.handleError('Failed to create tax transaction', error);
    }
  }

  /**
   * Get a tax transaction by ID
   */
  async getTransaction(id: UUID): Promise<TaxTransaction> {
    try {
      const response = await apiClient.get<ApiResponse<{ transaction: TaxTransaction }>>(
        `${this.baseUrl}/${id}`
      );
      return response.data.transaction;
    } catch (error) {
      this.handleError(`Failed to fetch tax transaction ${id}`, error);
    }
  }

  /**
   * List tax transactions with filtering and pagination
   */
  async listTransactions(
    params: TaxTransactionFilter & { 
      page?: number;
      pageSize?: number;
    }
  ): Promise<PaginatedResponse<TaxTransaction>> {
    try {
      const { page = 1, pageSize = 10, ...filters } = params;
      
      // Convert dates to ISO strings for the API
      const queryParams: Record<string, any> = {
        page,
        page_size: pageSize,
        ...filters
      };

      // Format dates
      if (filters.start_date) {
        queryParams.start_date = new Date(filters.start_date).toISOString();
      }
      if (filters.end_date) {
        queryParams.end_date = new Date(filters.end_date).toISOString();
      }

      const response = await apiClient.get<ApiResponse<{
        items: TaxTransaction[];
        total: number;
        page: number;
        page_size: number;
        total_pages: number;
      }>>(this.baseUrl, { params: queryParams });
      
      return response.data;
    } catch (error) {
      this.handleError('Failed to fetch tax transactions', error);
    }
  }

  /**
   * Update a tax transaction
   */
  async updateTransaction(
    id: UUID, 
    data: TaxTransactionUpdate
  ): Promise<TaxTransaction> {
    try {
      const response = await apiClient.put<ApiResponse<{ transaction: TaxTransaction }>>(
        `${this.baseUrl}/${id}`, 
        data
      );
      return response.data.transaction;
    } catch (error) {
      this.handleError(`Failed to update tax transaction ${id}`, error);
    }
  }

  /**
   * Post a draft transaction
   */
  async postTransaction(id: UUID): Promise<TaxTransaction> {
    try {
      const response = await apiClient.post<ApiResponse<{ transaction: TaxTransaction }>>(
        `${this.baseUrl}/${id}/post`
      );
      return response.data.transaction;
    } catch (error) {
      this.handleError(`Failed to post tax transaction ${id}`, error);
    }
  }

  /**
   * Void a posted transaction
   */
  async voidTransaction(id: UUID, reason: string): Promise<TaxTransaction> {
    try {
      const response = await apiClient.post<ApiResponse<{ transaction: TaxTransaction }>>(
        `${this.baseUrl}/${id}/void`,
        { reason }
      );
      return response.data.transaction;
    } catch (error) {
      this.handleError(`Failed to void tax transaction ${id}`, error);
    }
  }

  /**
   * Get transaction components
   */
  async getTransactionComponents(transactionId: UUID): Promise<TaxTransactionComponent[]> {
    try {
      const response = await apiClient.get<ApiResponse<{ components: TaxTransactionComponent[] }>>(
        `${this.baseUrl}/${transactionId}/components`
      );
      return response.data.components || [];
    } catch (error) {
      this.handleError(
        `Failed to fetch components for transaction ${transactionId}`, 
        error
      );
    }
  }

  /**
   * Export transactions to a file
   */
  async exportTransactions(
    params: TaxTransactionFilter & {
      format: 'csv' | 'excel' | 'pdf';
    }
  ): Promise<Blob> {
    try {
      const { format, ...filters } = params;
      
      const queryParams: Record<string, any> = {
        ...filters
      };

      // Format dates
      if (filters.start_date) {
        queryParams.start_date = new Date(filters.start_date).toISOString();
      }
      if (filters.end_date) {
        queryParams.end_date = new Date(filters.end_date).toISOString();
      }

      const response = await apiClient.get<Blob>(
        `${this.baseUrl}/export/${format}`,
        {
          params: queryParams,
          responseType: 'blob'
        }
      );
      
      return response;
    } catch (error) {
      this.handleError('Failed to export tax transactions', error);
    }
  }

  /**
   * Handle API errors consistently
   */
  private handleError(message: string, error: unknown): never {
    console.error(message, error);
    
    let errorMessage = message;
    
    if (error && typeof error === 'object') {
      const err = error as Record<string, any>;
      
      // Handle API error response
      if (err.response?.data) {
        const { message: apiMsg, detail } = err.response.data;
        if (apiMsg) errorMessage = apiMsg;
        else if (detail) errorMessage += `: ${detail}`;
      } 
      // Handle Axios error
      else if (err.isAxiosError && err.message) {
        errorMessage += `: ${err.message}`;
      }
      // Handle generic error
      else if (err.message) {
        errorMessage += `: ${err.message}`;
      }
    } 
    // Handle string errors
    else if (typeof error === 'string') {
      errorMessage += `: ${error}`;
    }
    
    // Ensure we always throw an Error object
    if (error instanceof Error) {
      error.message = errorMessage;
      throw error;
    }
    
    throw new Error(errorMessage);
  }
}

export const taxTransactionService = new TaxTransactionService();
