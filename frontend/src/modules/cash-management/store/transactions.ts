import { defineStore } from 'pinia';
import { ref } from 'vue';
import { useToast } from 'primevue/usetoast';
import BankAccountService from '../api/BankAccountService';

interface Transaction {
  id?: string;
  bankAccountId: string;
  date: string;
  amount: number;
  type: 'deposit' | 'withdrawal' | 'transfer' | 'fee' | 'interest' | 'other';
  category?: string;
  description: string;
  referenceNumber?: string;
  status: 'pending' | 'completed' | 'cancelled' | 'reconciled';
  notes?: string;
  createdBy?: string;
  createdAt?: string;
  updatedAt?: string;
}

export const useTransactionsStore = defineStore('transactions', () => {
  const toast = useToast();
  const transactions = ref<Transaction[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);
  
  // Transaction types for dropdowns
  const transactionTypes = ref([
    { name: 'Deposit', value: 'deposit' },
    { name: 'Withdrawal', value: 'withdrawal' },
    { name: 'Transfer', value: 'transfer' },
    { name: 'Fee', value: 'fee' },
    { name: 'Interest', value: 'interest' },
    { name: 'Other', value: 'other' },
  ]);
  
  // Transaction statuses
  const transactionStatuses = ref([
    { name: 'Pending', value: 'pending' },
    { name: 'Completed', value: 'completed' },
    { name: 'Cancelled', value: 'cancelled' },
    { name: 'Reconciled', value: 'reconciled' },
  ]);

  // Fetch all transactions for a bank account
  const fetchTransactions = async (bankAccountId: string) => {
    try {
      loading.value = true;
      error.value = null;
      const response = await BankAccountService.getTransactions(bankAccountId);
      transactions.value = response.data;
      return transactions.value;
    } catch (err) {
      console.error('Error fetching transactions:', err);
      error.value = 'Failed to load transactions. Please try again later.';
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to load transactions',
        life: 5000,
      });
      throw err;
    } finally {
      loading.value = false;
    }
  };

  // Create a new transaction
  const createTransaction = async (transactionData: Omit<Transaction, 'id'>) => {
    try {
      loading.value = true;
      error.value = null;
      const response = await BankAccountService.createTransaction(transactionData);
      transactions.value.push(response.data);
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Transaction created successfully',
        life: 3000,
      });
      return response.data;
    } catch (err) {
      console.error('Error creating transaction:', err);
      error.value = 'Failed to create transaction. Please try again.';
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to create transaction',
        life: 5000,
      });
      throw err;
    } finally {
      loading.value = false;
    }
  };

  // Update an existing transaction
  const updateTransaction = async (id: string, transactionData: Partial<Transaction>) => {
    try {
      loading.value = true;
      error.value = null;
      const response = await BankAccountService.updateTransaction(id, transactionData);
      const index = transactions.value.findIndex(t => t.id === id);
      if (index !== -1) {
        transactions.value[index] = { ...transactions.value[index], ...response.data };
      }
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Transaction updated successfully',
        life: 3000,
      });
      return response.data;
    } catch (err) {
      console.error('Error updating transaction:', err);
      error.value = 'Failed to update transaction. Please try again.';
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to update transaction',
        life: 5000,
      });
      throw err;
    } finally {
      loading.value = false;
    }
  };

  // Delete a transaction
  const deleteTransaction = async (id: string) => {
    try {
      loading.value = true;
      error.value = null;
      await BankAccountService.deleteTransaction(id);
      transactions.value = transactions.value.filter(t => t.id !== id);
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Transaction deleted successfully',
        life: 3000,
      });
      return true;
    } catch (err) {
      console.error('Error deleting transaction:', err);
      error.value = 'Failed to delete transaction. Please try again.';
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to delete transaction',
        life: 5000,
      });
      throw err;
    } finally {
      loading.value = false;
    }
  };

  // Get a single transaction by ID
  const getTransactionById = (id: string) => {
    return transactions.value.find(t => t.id === id);
  };

  // Get all transaction types for dropdown
  const getTransactionTypes = () => {
    return transactionTypes.value;
  };

  // Get all transaction statuses for dropdown
  const getTransactionStatuses = () => {
    return transactionStatuses.value;
  };

  return {
    transactions,
    loading,
    error,
    fetchTransactions,
    createTransaction,
    updateTransaction,
    deleteTransaction,
    getTransactionById,
    getTransactionTypes,
    getTransactionStatuses,
  };
});
