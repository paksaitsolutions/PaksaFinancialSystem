import { defineStore } from 'pinia';
import { ref } from 'vue';
import { useToast } from 'primevue/usetoast';
import BankAccountService from '../api/BankAccountService';

interface BankAccount {
  id?: string;
  name: string;
  accountNumber: string;
  bankName: string;
  accountType: string;
  currency: string;
  balance: number;
  isActive: boolean;
  description?: string;
  routingNumber?: string;
  iban?: string;
  swiftCode?: string;
  openingBalance?: number;
  openingDate?: string;
}

export const useBankAccountsStore = defineStore('bankAccounts', () => {
  const toast = useToast();
  const accounts = ref<BankAccount[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const accountTypes = ref([
    { name: 'Checking', code: 'checking' },
    { name: 'Savings', code: 'savings' },
    { name: 'Credit Card', code: 'credit_card' },
    { name: 'Loan', code: 'loan' },
    { name: 'Investment', code: 'investment' },
    { name: 'Other', code: 'other' },
  ]);

  // Fetch all bank accounts
  const fetchAccounts = async () => {
    try {
      loading.value = true;
      error.value = null;
      const response = await BankAccountService.getBankAccounts();
      accounts.value = response.data;
    } catch (err) {
      console.error('Error fetching bank accounts:', err);
      error.value = 'Failed to load bank accounts. Please try again later.';
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to load bank accounts',
        life: 5000,
      });
    } finally {
      loading.value = false;
    }
  };

  // Create a new bank account
  const createAccount = async (accountData: Omit<BankAccount, 'id'>) => {
    try {
      loading.value = true;
      error.value = null;
      const response = await BankAccountService.createBankAccount(accountData);
      accounts.value.push(response.data);
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Bank account created successfully',
        life: 3000,
      });
      return response.data;
    } catch (err) {
      console.error('Error creating bank account:', err);
      error.value = 'Failed to create bank account. Please try again.';
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to create bank account',
        life: 5000,
      });
      throw err;
    } finally {
      loading.value = false;
    }
  };

  // Update an existing bank account
  const updateAccount = async (id: string, accountData: Partial<BankAccount>) => {
    try {
      loading.value = true;
      error.value = null;
      const response = await BankAccountService.updateBankAccount(id, accountData);
      const index = accounts.value.findIndex(acc => acc.id === id);
      if (index !== -1) {
        accounts.value[index] = { ...accounts.value[index], ...response.data };
      }
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Bank account updated successfully',
        life: 3000,
      });
      return response.data;
    } catch (err) {
      console.error('Error updating bank account:', err);
      error.value = 'Failed to update bank account. Please try again.';
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to update bank account',
        life: 5000,
      });
      throw err;
    } finally {
      loading.value = false;
    }
  };

  // Delete a bank account
  const deleteAccount = async (id: string) => {
    try {
      loading.value = true;
      error.value = null;
      await BankAccountService.deleteBankAccount(id);
      accounts.value = accounts.value.filter(acc => acc.id !== id);
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Bank account deleted successfully',
        life: 3000,
      });
      return true;
    } catch (err) {
      console.error('Error deleting bank account:', err);
      error.value = 'Failed to delete bank account. Please try again.';
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to delete bank account',
        life: 5000,
      });
      throw err;
    } finally {
      loading.value = false;
    }
  };

  // Get a single bank account by ID
  const getAccountById = (id: string) => {
    return accounts.value.find(acc => acc.id === id);
  };

  // Get all account types
  const getAccountTypes = () => {
    return accountTypes.value;
  };

  return {
    accounts,
    loading,
    error,
    fetchAccounts,
    createAccount,
    updateAccount,
    deleteAccount,
    getAccountById,
    getAccountTypes,
  };
});
