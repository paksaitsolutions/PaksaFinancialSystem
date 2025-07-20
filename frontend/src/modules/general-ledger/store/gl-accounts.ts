import { defineStore } from 'pinia';
import { ref } from 'vue';
import axios from 'axios';
import { useToast } from 'primevue/usetoast';
import type { AxiosError } from 'axios';
import { useI18n } from 'vue-i18n';

export interface GlAccount {
  id: string;
  accountNumber: string;
  name: string;
  description?: string;
  accountType: 'asset' | 'liability' | 'equity' | 'revenue' | 'expense' | 'gain' | 'loss';
  accountSubType?: string;
  parentAccountId?: string;
  isActive: boolean;
  isSystemAccount: boolean;
  currency: string;
  taxCode?: string;
  costCenter?: string;
  projectCode?: string;
  balance: number;
  budgetAmount?: number;
  budgetVariance?: number;
  createdAt: string;
  updatedAt: string;
  createdBy: string;
  updatedBy?: string;
  children?: GlAccount[];
  level?: number;
}

interface GlAccountState {
  accounts: GlAccount[];
  accountTree: GlAccount[];
  currentAccount: GlAccount | null;
  loading: boolean;
  error: string | null;
}

export const useGlAccountsStore = defineStore('glAccounts', () => {
  const toast = useToast();
  const { t } = useI18n();
  
  // State
  const state = ref<GlAccountState>({
    accounts: [],
    accountTree: [],
    currentAccount: null,
    loading: false,
    error: null
  });

  // Getters
  const isLoading = computed(() => state.value.loading);
  const hasError = computed(() => state.value.error !== null);
  const allAccounts = computed(() => state.value.accounts);
  const activeAccounts = computed(() => 
    state.value.accounts.filter(account => account.isActive)
  );
  const accountHierarchy = computed(() => state.value.accountTree);

  // Actions
  async function fetchAccounts() {
    state.value.loading = true;
    state.value.error = null;
    
    try {
      const response = await axios.get<GlAccount[]>('/api/gl/accounts');
      state.value.accounts = response.data;
      state.value.accountTree = buildAccountTree(response.data);
      return response.data;
    } catch (err) {
      const errorMessage = t('gl.errors.fetchAccounts');
      handleApiError(errorMessage, err);
      throw err;
    } finally {
      state.value.loading = false;
    }
  }

  async function fetchAccountById(id: string) {
    state.value.loading = true;
    state.value.error = null;
    
    try {
      const response = await axios.get<GlAccount>(`/api/gl/accounts/${id}`);
      state.value.currentAccount = response.data;
      return response.data;
    } catch (err) {
      const errorMessage = t('gl.errors.fetchAccount');
      handleApiError(errorMessage, err);
      throw err;
    } finally {
      state.value.loading = false;
    }
  }

  async function createAccount(accountData: Omit<GlAccount, 'id' | 'createdAt' | 'updatedAt' | 'createdBy' | 'balance'>) {
    state.value.loading = true;
    state.value.error = null;
    
    try {
      const response = await axios.post<GlAccount>('/api/gl/accounts', accountData);
      await fetchAccounts(); // Refresh the list
      toast.add({
        severity: 'success',
        summary: t('common.success'),
        detail: t('gl.messages.accountCreated'),
        life: 3000
      });
      return response.data;
    } catch (err) {
      const errorMessage = t('gl.errors.createAccount');
      handleApiError(errorMessage, err);
      throw err;
    } finally {
      state.value.loading = false;
    }
  }

  async function updateAccount({ id, data }: { id: string; data: Partial<GlAccount> }) {
    state.value.loading = true;
    state.value.error = null;
    
    try {
      const response = await axios.put<GlAccount>(`/api/gl/accounts/${id}`, data);
      await fetchAccounts(); // Refresh the list
      toast.add({
        severity: 'success',
        summary: t('common.success'),
        detail: t('gl.messages.accountUpdated'),
        life: 3000
      });
      return response.data;
    } catch (err) {
      const errorMessage = t('gl.errors.updateAccount');
      handleApiError(errorMessage, err);
      throw err;
    } finally {
      state.value.loading = false;
    }
  }

  async function deleteAccount(id: string) {
    state.value.loading = true;
    state.value.error = null;
    
    try {
      await axios.delete(`/api/gl/accounts/${id}`);
      await fetchAccounts(); // Refresh the list
      toast.add({
        severity: 'success',
        summary: t('common.success'),
        detail: t('gl.messages.accountDeleted'),
        life: 3000
      });
    } catch (err) {
      const errorMessage = t('gl.errors.deleteAccount');
      handleApiError(errorMessage, err);
      throw err;
    } finally {
      state.value.loading = false;
    }
  }

  // Helper functions
  function buildAccountTree(accounts: GlAccount[], parentId: string | null = null, level: number = 0): GlAccount[] {
    return accounts
      .filter(account => account.parentAccountId === parentId)
      .map(account => ({
        ...account,
        level,
        children: buildAccountTree(accounts, account.id, level + 1)
      }));
  }

  function getAccountByNumber(accountNumber: string): GlAccount | undefined {
    return state.value.accounts.find(account => account.accountNumber === accountNumber);
  }

  function getAccountPath(accountId: string): GlAccount[] {
    const path: GlAccount[] = [];
    let currentId: string | undefined = accountId;
    
    while (currentId) {
      const account = state.value.accounts.find(a => a.id === currentId);
      if (!account) break;
      
      path.unshift(account);
      currentId = account.parentAccountId;
    }
    
    return path;
  }

  function handleApiError(defaultMessage: string, error: unknown) {
    const axiosError = error as AxiosError<{ message?: string }>;
    const errorMessage = axiosError.response?.data?.message || defaultMessage;
    
    toast.add({
      severity: 'error',
      summary: t('common.error'),
      detail: errorMessage,
      life: 5000
    });
    
    console.error('API Error:', error);
    state.value.error = errorMessage;
  }

  // Initialize the store
  function $reset() {
    state.value = {
      accounts: [],
      accountTree: [],
      currentAccount: null,
      loading: false,
      error: null
    };
  }

  return {
    // State
    state,
    
    // Getters
    isLoading,
    hasError,
    allAccounts,
    activeAccounts,
    accountHierarchy,
    
    // Actions
    fetchAccounts,
    fetchAccountById,
    createAccount,
    updateAccount,
    deleteAccount,
    getAccountByNumber,
    getAccountPath,
    $reset
  };
});

export default useGlAccountsStore;
