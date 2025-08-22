import { api } from '@/utils/api';
import { format } from 'date-fns';

export interface IntercompanyTransaction {
  id: string;
  transaction_number: string;
  transaction_type: 'sale' | 'purchase' | 'loan' | 'expense_allocation' | 'revenue_sharing' | 'transfer';
  status: 'draft' | 'pending' | 'approved' | 'posted' | 'reconciled' | 'cancelled';
  source_company_id: string;
  target_company_id: string;
  amount: string;
  currency_id: string;
  transaction_date: string;
  due_date?: string;
  source_account_id: string;
  target_account_id: string;
  description?: string;
  reference_number?: string;
  source_journal_entry_id?: string;
  target_journal_entry_id?: string;
  approved_by?: string;
  approved_at?: string;
  created_at: string;
  updated_at: string;
}

export interface IntercompanyTransactionCreate {
  transaction_type: string;
  source_company_id: string;
  target_company_id: string;
  amount: number;
  currency_id: string;
  transaction_date: Date;
  due_date?: Date;
  source_account_id: string;
  target_account_id: string;
  description?: string;
  reference_number?: string;
}

/**
 * Intercompany Service
 * Provides methods to interact with the intercompany API endpoints
 */
export default {
  /**
   * Create a new intercompany transaction
   * @param transaction - Transaction data
   * @returns Promise with the created transaction
   */
  async createTransaction(transaction: IntercompanyTransactionCreate) {
    const formattedTransaction = {
      ...transaction,
      transaction_date: format(transaction.transaction_date, 'yyyy-MM-dd'),
      due_date: transaction.due_date ? format(transaction.due_date, 'yyyy-MM-dd') : undefined
    };
    return api.post('/intercompany/transactions', formattedTransaction);
  },

  /**
   * Get an intercompany transaction by ID
   * @param id - Transaction ID
   * @returns Promise with the transaction details
   */
  async getTransaction(id: string) {
    return api.get(`/intercompany/transactions/${id}`);
  },

  /**
   * List intercompany transactions
   * @param options - Filter options
   * @returns Promise with the list of transactions
   */
  async listTransactions(options = {
    company_id: null,
    status: null,
    skip: 0,
    limit: 100
  }) {
    const params = new URLSearchParams({
      skip: options.skip.toString(),
      limit: options.limit.toString()
    });

    if (options.company_id) {
      params.append('company_id', options.company_id);
    }

    if (options.status) {
      params.append('status_filter', options.status);
    }

    return api.get(`/intercompany/transactions?${params.toString()}`);
  },

  /**
   * Approve an intercompany transaction
   * @param id - Transaction ID
   * @returns Promise with the approved transaction
   */
  async approveTransaction(id: string) {
    return api.post(`/intercompany/transactions/${id}/approve`);
  },

  /**
   * Post an intercompany transaction
   * @param id - Transaction ID
   * @returns Promise with the posted transaction
   */
  async postTransaction(id: string) {
    return api.post(`/intercompany/transactions/${id}/post`);
  }
};