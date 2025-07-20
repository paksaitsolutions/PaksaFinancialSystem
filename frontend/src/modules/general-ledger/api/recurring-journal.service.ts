import axios, { type AxiosInstance, type AxiosResponse, type AxiosError } from 'axios';
import { useAuthStore } from '@/store/auth';
import type { 
  RecurringJournal, 
  RecurringJournalCreate, 
  RecurringJournalUpdate, 
  RecurringJournalListParams, 
  RecurringJournalListResponse,
  RecurringJournalPreview,
  RecurringJournalRunParams,
  RecurringJournalRunResponse,
  RecurringJournalStats,
  RecurringJournalOccurrence
} from '../types/recurringJournal';

const API_BASE_URL = '/api/gl/recurring-journals';

/**
 * Service for handling recurring journal API operations
 */
class RecurringJournalService {
  private readonly http: AxiosInstance;
  
  constructor() {
    this.http = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    });

    // Add request interceptor for auth
    this.http.interceptors.request.use(
      (config) => {
        const authStore = useAuthStore();
        if (authStore.token) {
          config.headers.Authorization = `Bearer ${authStore.token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );
  }
  
  /**
   * Get all recurring journals with optional filtering and pagination
   */
  async getRecurringJournals(
    params?: RecurringJournalListParams
  ): Promise<RecurringJournalListResponse> {
    try {
      const response = await this.http.get<RecurringJournalListResponse>('', { params });
      return response.data;
    } catch (error) {
      return this.handleError(error as AxiosError, 'Failed to fetch recurring journals');
    }
  }

  /**
   * Get a single recurring journal by ID
   */
  async getRecurringJournal(id: string): Promise<RecurringJournal> {
    try {
      const response = await this.http.get<{ data: RecurringJournal }>(`/${id}`);
      return response.data.data;
    } catch (error) {
      return this.handleError(error as AxiosError, `Failed to fetch recurring journal ${id}`);
    }
  }

  /**
   * Create a new recurring journal
   */
  async createRecurringJournal(data: RecurringJournalCreate): Promise<RecurringJournal> {
    try {
      const response = await this.http.post<{ data: RecurringJournal }>('', data);
      return response.data.data;
    } catch (error) {
      return this.handleError(error as AxiosError, 'Failed to create recurring journal');
    }
  }

  /**
   * Update an existing recurring journal
   */
  async updateRecurringJournal(
    id: string, 
    data: RecurringJournalUpdate
  ): Promise<RecurringJournal> {
    try {
      const response = await this.http.put<{ data: RecurringJournal }>(`/${id}`, data);
      return response.data.data;
    } catch (error) {
      return this.handleError(error as AxiosError, `Failed to update recurring journal ${id}`);
    }
  }

  /**
   * Delete a recurring journal
   */
  async deleteRecurringJournal(id: string): Promise<void> {
    try {
      await this.http.delete(`/${id}`);
    } catch (error) {
      return this.handleError(error as AxiosError, `Failed to delete recurring journal ${id}`);
    }
  }

  /**
   * Update the status of a recurring journal
   */
  async updateRecurringJournalStatus(
    id: string, 
    status: 'active' | 'paused' | 'cancelled'
  ): Promise<RecurringJournal> {
    try {
      const response = await this.http.patch<{ data: RecurringJournal }>(
        `/${id}/status`,
        { status }
      );
      return response.data.data;
    } catch (error) {
      return this.handleError(error as AxiosError, `Failed to update status for recurring journal ${id}`);
    }
  }

  /**
   * Preview the next occurrences of a recurring journal
   */
  async previewRecurringJournal(
    id: string,
    params?: { limit?: number; start_date?: string }
  ): Promise<RecurringJournalPreview> {
    try {
      const response = await this.http.get<{ data: RecurringJournalPreview }>(
        `/${id}/preview`,
        { params }
      );
      return response.data.data;
    } catch (error) {
      return this.handleError(error as AxiosError, `Failed to preview recurring journal ${id}`);
    }
  }

  /**
   * Run a recurring journal for a specific date
   */
  async runRecurringJournal(
    id: string,
    params: RecurringJournalRunParams = {}
  ): Promise<RecurringJournalRunResponse> {
    try {
      const response = await this.http.post<{ data: RecurringJournalRunResponse }>(
        `/${id}/run`,
        params
      );
      return response.data.data;
    } catch (error) {
      return this.handleError(error as AxiosError, `Failed to run recurring journal ${id}`);
    }
  }

  /**
   * Get statistics about recurring journals
   */
  async getRecurringJournalStats(): Promise<RecurringJournalStats> {
    try {
      const response = await this.http.get<{ data: RecurringJournalStats }>('/stats');
      return response.data.data;
    } catch (error) {
      return this.handleError(error as AxiosError, 'Failed to fetch recurring journal statistics');
    }
  }

  /**
   * Get past occurrences of a recurring journal
   */
  async getRecurringJournalOccurrences(
    id: string,
    params?: { page?: number; per_page?: number }
  ): Promise<{ data: RecurringJournalOccurrence[]; meta: any }> {
    try {
      const response = await this.http.get<{ data: RecurringJournalOccurrence[]; meta: any }>(
        `/${id}/occurrences`,
        { params }
      );
      return response.data;
    } catch (error) {
      return this.handleError(
        error as AxiosError, 
        `Failed to fetch occurrences for recurring journal ${id}`
      );
    }
  }

  /**
   * Handle API errors consistently
   */
  private async handleError<T>(error: AxiosError, defaultMessage: string): Promise<T> {
    console.error(defaultMessage, error);
    
    let errorMessage = defaultMessage;
    const authStore = useAuthStore();
    
    if (axios.isAxiosError(error)) {
      if (error.response) {
        // Server responded with a status code outside 2xx
        const status = error.response.status;
        
        if (status === 401) {
          // Handle unauthorized (e.g., token expired)
          authStore.logout();
          errorMessage = 'Your session has expired. Please log in again.';
        } else if (status === 403) {
          errorMessage = 'You do not have permission to perform this action.';
        } else if (status === 404) {
          errorMessage = 'The requested resource was not found.';
        } else if (status === 422) {
          // Handle validation errors
          const errors = (error.response.data as any)?.errors;
          if (errors) {
            errorMessage = Object.values(errors).flat().join(' ');
          } else {
            errorMessage = 'Validation failed. Please check your input.';
          }
        } else if (status >= 500) {
          errorMessage = 'A server error occurred. Please try again later.';
        }
      } else if (error.request) {
        // Request was made but no response received
        errorMessage = 'No response from server. Please check your connection.';
      } else {
        // Something happened in setting up the request
        errorMessage = `Request error: ${error.message}`;
      }
    }
    
    // Create and throw an error with the appropriate message
    const errorWithMessage = new Error(errorMessage) as Error & { response?: any };
    errorWithMessage.response = (error as AxiosError).response;
    
    // Re-throw the error to be handled by the calling component
    throw errorWithMessage;
  }
}

// Export a singleton instance
export const recurringJournalService = new RecurringJournalService();
