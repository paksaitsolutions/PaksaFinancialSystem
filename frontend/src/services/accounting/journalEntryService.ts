import axios from 'axios';
import { useAuthStore } from '@/stores/auth';
import type { JournalEntry, JournalEntryLine, JournalEntryStatus } from '@/types/accounting';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

// Create axios instance with base URL and common headers
const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/accounting/journal-entries`,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Add request interceptor to include auth token
apiClient.interceptors.request.use((config) => {
  const authStore = useAuthStore();
  if (authStore.token) {
    config.headers.Authorization = `Bearer ${authStore.token}`;
  }
  return config;
});

// Helper function to handle API errors
const handleApiError = (error: any) => {
  let message = 'An error occurred';
  
  if (error.response) {
    // The request was made and the server responded with a status code
    // that falls out of the range of 2xx
    message = error.response.data?.detail || error.response.statusText || 'Request failed';
  } else if (error.request) {
    // The request was made but no response was received
    message = 'No response from server. Please check your connection.';
  } else {
    // Something happened in setting up the request that triggered an Error
    message = error.message;
  }
  
  console.error('API Error:', error);
  throw new Error(message);
};

/**
 * Fetch a list of journal entries with optional filters
 */
export const fetchJournalEntries = async (params: {
  page?: number;
  pageSize?: number;
  status?: JournalEntryStatus;
  startDate?: string;
  endDate?: string;
  reference?: string;
}) => {
  try {
    const {
      page = 1,
      pageSize = 10,
      status,
      startDate,
      endDate,
      reference,
    } = params;
    
    const skip = (page - 1) * pageSize;
    
    const response = await apiClient.get('/', {
      params: {
        skip,
        limit: pageSize,
        status,
        start_date: startDate,
        end_date: endDate,
        reference,
      },
    });
    
    return {
      data: response.data,
      pagination: {
        page,
        pageSize,
        total: response.headers['x-total-count'] ? parseInt(response.headers['x-total-count'], 10) : 0,
      },
    };
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Fetch a single journal entry by ID
 */
export const fetchJournalEntry = async (id: string) => {
  try {
    const response = await apiClient.get(`/${id}`, {
      params: {
        include_lines: true,
      },
    });
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Create a new journal entry
 */
export const createJournalEntry = async (entryData: {
  entry_date: string;
  reference: string;
  description: string;
  currency?: string;
  notes?: string;
  line_items: Array<{
    account_id: string;
    description: string;
    debit: number;
    credit: number;
    tax_code?: string;
    tax_amount?: number;
    entity_type?: string;
    entity_id?: string;
  }>;
}) => {
  try {
    const response = await apiClient.post('/', entryData);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Update an existing journal entry
 */
export const updateJournalEntry = async (
  id: string,
  entryData: {
    entry_date?: string;
    reference?: string;
    description?: string;
    currency?: string;
    notes?: string;
    status?: JournalEntryStatus;
    line_items?: Array<{
      id?: string;
      account_id: string;
      description: string;
      debit: number;
      credit: number;
      tax_code?: string;
      tax_amount?: number;
      entity_type?: string;
      entity_id?: string;
    }>;
  },
) => {
  try {
    const response = await apiClient.put(`/${id}`, entryData);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Delete a journal entry
 */
export const deleteJournalEntry = async (id: string, force: boolean = false) => {
  try {
    const response = await apiClient.delete(`/${id}`, {
      params: { force },
    });
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Post a journal entry to update account balances
 */
export const postJournalEntry = async (id: string) => {
  try {
    const response = await apiClient.post(`/${id}/post`);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Approve a journal entry
 */
export const approveJournalEntry = async (id: string) => {
  try {
    const response = await apiClient.post(`/${id}/approve`);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Reverse a posted journal entry
 */
export const reverseJournalEntry = async (
  id: string,
  reversalDate?: string,
  description?: string
) => {
  try {
    const response = await apiClient.post(`/${id}/reverse`, {
      reversal_date: reversalDate,
      description,
    });
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Batch create multiple journal entries
 */
export const batchCreateJournalEntries = async (entries: Array<{
  entry_date: string;
  reference: string;
  description: string;
  currency?: string;
  notes?: string;
  line_items: Array<{
    account_id: string;
    description: string;
    debit: number;
    credit: number;
    tax_code?: string;
    tax_amount?: number;
    entity_type?: string;
    entity_id?: string;
  }>;
}>) => {
  try {
    const response = await apiClient.post('/batch', { entries });
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Create a recurring journal entry template
 */
export const createRecurringJournalEntry = async (entryData: {
  entry_date: string;
  reference: string;
  description: string;
  currency?: string;
  notes?: string;
  frequency: 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'yearly';
  end_date?: string;
  occurrences?: number;
  line_items: Array<{
    account_id: string;
    description: string;
    debit: number;
    credit: number;
    tax_code?: string;
    tax_amount?: number;
    entity_type?: string;
    entity_id?: string;
  }>;
}) => {
  try {
    const response = await apiClient.post('/recurring', entryData);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Upload an attachment for a journal entry
 */
export const uploadAttachment = async (
  entryId: string,
  file: File,
  description?: string
) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    if (description) {
      formData.append('description', description);
    }
    
    const response = await apiClient.post(
      `/${entryId}/attachments`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Delete an attachment
 */
export const deleteAttachment = async (entryId: string, attachmentId: string) => {
  try {
    const response = await apiClient.delete(`/${entryId}/attachments/${attachmentId}`);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Get attachments for a journal entry
 */
export const getAttachments = async (entryId: string) => {
  try {
    const response = await apiClient.get(`/${entryId}/attachments`);
    return response.data;
  } catch (error) {
    return handleApiError(error);
  }
};

/**
 * Get the next journal entry number
 */
export const getNextJournalEntryNumber = async (): Promise<string> => {
  try {
    // This is a mock implementation - adjust based on your API
    const response = await fetchJournalEntries({ page: 1, pageSize: 1 });
    const count = response.pagination.total;
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    return `JE-${year}${month}-${String(count + 1).padStart(4, '0')}`;
  } catch (error) {
    console.error('Error generating next journal entry number:', error);
    // Fallback to a simple timestamp-based number
    return `JE-${Date.now()}`;
  }
};

export default {
  fetchJournalEntries,
  fetchJournalEntry,
  createJournalEntry,
  updateJournalEntry,
  deleteJournalEntry,
  postJournalEntry,
  approveJournalEntry,
  getNextJournalEntryNumber,
  reverseJournalEntry,
  batchCreateJournalEntries,
  createRecurringJournalEntry,
  uploadAttachment,
  deleteAttachment,
  getAttachments,
};
