import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { glAccountService } from '../api/gl-account.service';
import type {
  GlAccount,
  GlAccountTree,
  GlAccountFilters,
  CreateGlAccountDto,
  UpdateGlAccountDto,
  GlAccountSummary,
  GlAccountMoveDto,
  GlAccountBulkUpdateDto,
  GlAccountReconcileDto,
  GlAccountExportDto,
  GlAccountBalanceHistory
} from '../types/gl-account';

interface GlAccountState {
  accounts: Record<string, GlAccount>;
  hierarchy: GlAccountTree[];
  selectedAccount: GlAccount | null;
  loading: boolean;
  error: string | null;
  summary: GlAccountSummary | null;
  filters: GlAccountFilters;
}

export const useGlAccountStore = defineStore('glAccount', () => {
  // State
  const state = ref<GlAccountState>({
    accounts: {},
    hierarchy: [],
    selectedAccount: null,
    loading: false,
    error: null,
    summary: null,
    filters: {
      searchTerm: '',
      accountType: undefined,
      isActive: true,
      page: 1,
      pageSize: 20,
      sortField: 'accountNumber',
      sortOrder: 'asc',
    } as GlAccountFilters,
  });

  // Getters
  const accountsList = computed<GlAccount[]>(() => Object.values(state.value.accounts));
  const activeAccounts = computed<GlAccount[]>(() => 
    Object.values(state.value.accounts).filter(account => account.status === 'active')
  );
  
  const accountHierarchy = computed<GlAccountTree[]>(() => state.value.hierarchy);
  const selectedAccount = computed<GlAccount | null>(() => state.value.selectedAccount);
  const isLoading = computed<boolean>(() => state.value.loading);
  const error = computed<string | null>(() => state.value.error);
  const accountSummary = computed<GlAccountSummary | null>(() => state.value.summary);
  const currentFilters = computed<GlAccountFilters>(() => state.value.filters);

  // Actions
  const setFilters = (filters: Partial<GlAccountFilters>) => {
    state.value.filters = { 
      ...state.value.filters, 
      ...filters,
      // Ensure we don't have undefined values that would override defaults
      ...Object.fromEntries(
        Object.entries(filters).filter(([_, v]) => v !== undefined)
      )
    } as GlAccountFilters;
  };

  const resetFilters = () => {
    state.value.filters = {
      searchTerm: '',
      accountType: undefined,
      isActive: true,
      page: 1,
      pageSize: 20,
      sortField: 'accountNumber',
      sortOrder: 'asc',
    } as GlAccountFilters;
  };

  const fetchAccounts = async (filters?: GlAccountFilters) => {
    state.value.loading = true;
    state.value.error = null;
    
    try {
      const response = await glAccountService.fetchAccounts(filters || state.value.filters);
      
      // Update accounts in state
      response.data.forEach(account => {
        state.value.accounts[account.id] = account;
      });
      
      return response;
    } catch (err: any) {
      state.value.error = err.message || 'Failed to fetch accounts';
      throw err;
    } finally {
      state.value.loading = false;
    }
  };

  const fetchAccountById = async (id: string) => {
    state.value.loading = true;
    state.value.error = null;
    
    try {
      const account = await glAccountService.fetchAccountById(id);
      state.value.accounts[account.id] = account;
      state.value.selectedAccount = account;
      return account;
    } catch (err: any) {
      state.value.error = err.message || `Failed to fetch account with ID: ${id}`;
      throw err;
    } finally {
      state.value.loading = false;
    }
  };

  const createAccount = async (accountData: CreateGlAccountDto) => {
    state.value.loading = true;
    state.value.error = null;
    
    try {
      const newAccount = await glAccountService.createAccount(accountData);
      state.value.accounts[newAccount.id] = newAccount;
      
      // If this is a top-level account, add it to the hierarchy
      if (!newAccount.parentAccountId) {
        state.value.hierarchy.push({
          ...newAccount,
          children: []
        });
      }
      
      return newAccount;
    } catch (err: any) {
      state.value.error = err.message || 'Failed to create account';
      throw err;
    } finally {
      state.value.loading = false;
    }
  };

  const updateAccount = async (id: string, accountData: UpdateGlAccountDto) => {
    state.value.loading = true;
    state.value.error = null;
    
    try {
      const updatedAccount = await glAccountService.updateAccount(id, accountData);
      state.value.accounts[updatedAccount.id] = updatedAccount;
      
      // Update selected account if it's the one being updated
      if (state.value.selectedAccount?.id === updatedAccount.id) {
        state.value.selectedAccount = updatedAccount;
      }
      
      return updatedAccount;
    } catch (err: any) {
      state.value.error = err.message || `Failed to update account with ID: ${id}`;
      throw err;
    } finally {
      state.value.loading = false;
    }
  };

  const deleteAccount = async (id: string) => {
    state.value.loading = true;
    state.value.error = null;
    
    try {
      await glAccountService.deleteAccount(id);
      delete state.value.accounts[id];
      
      // Remove from selected account if it's the one being deleted
      if (state.value.selectedAccount?.id === id) {
        state.value.selectedAccount = null;
      }
      
      // Remove from hierarchy
      removeFromHierarchy(id);
      
      return true;
    } catch (err: any) {
      state.value.error = err.message || `Failed to delete account with ID: ${id}`;
      throw err;
    } finally {
      state.value.loading = false;
    }
  };

  const fetchAccountHierarchy = async (parentId?: string | null) => {
    state.value.loading = true;
    state.value.error = null;
    
    try {
      const hierarchy = await glAccountService.getAccountHierarchy(parentId);
      
      if (!parentId) {
        // If loading root level, replace the entire hierarchy
        state.value.hierarchy = hierarchy;
      }
      
      // Update accounts in state
      const updateAccountsFromHierarchy = (items: GlAccountTree[]) => {
        items.forEach(item => {
          const { children, ...account } = item;
          state.value.accounts[account.id] = account;
          
          if (children && children.length > 0) {
            updateAccountsFromHierarchy(children);
          }
        });
      };
      
      updateAccountsFromHierarchy(hierarchy);
      
      return hierarchy;
    } catch (err: any) {
      state.value.error = err.message || 'Failed to fetch account hierarchy';
      throw err;
    } finally {
      state.value.loading = false;
    }
  };

  const fetchFullHierarchy = async () => {
    state.value.loading = true;
    state.value.error = null;
    
    try {
      const fullHierarchy = await glAccountService.getFullAccountHierarchy();
      
      // Helper function to update accounts from hierarchy
      const updateAccountsFromHierarchy = (items: GlAccountTree[]) => {
        items.forEach(item => {
          const { children, ...account } = item;
          state.value.accounts[account.id] = account;
          
          if (children && children.length > 0) {
            updateAccountsFromHierarchy(children);
          }
        });
      };
      
      updateAccountsFromHierarchy([fullHierarchy]);
      state.value.hierarchy = [fullHierarchy];
      
      return fullHierarchy;
    } catch (err: any) {
      state.value.error = err.message || 'Failed to fetch full account hierarchy';
      throw err;
    } finally {
      state.value.loading = false;
    }
  };

  const moveAccount = async (moveData: GlAccountMoveDto) => {
    state.value.loading = true;
    state.value.error = null;
    
    try {
      const updatedAccount = await glAccountService.moveAccount(moveData);
      state.value.accounts[updatedAccount.id] = updatedAccount;
      
      // Refresh the hierarchy to reflect the move
      await fetchAccountHierarchy();
      
      return updatedAccount;
    } catch (err: any) {
      state.value.error = err.message || 'Failed to move account';
      throw err;
    } finally {
      state.value.loading = false;
    }
  };

  const reconcileAccount = async (reconcileData: GlAccountReconcileDto) => {
    state.value.loading = true;
    state.value.error = null;
    
    try {
      const updatedAccount = await glAccountService.reconcileAccount(reconcileData);
      state.value.accounts[updatedAccount.id] = updatedAccount;
      
      if (state.value.selectedAccount?.id === updatedAccount.id) {
        state.value.selectedAccount = updatedAccount;
      }
      
      return updatedAccount;
    } catch (err: any) {
      state.value.error = err.message || 'Failed to reconcile account';
      throw err;
    } finally {
      state.value.loading = false;
    }
  };

  const fetchAccountSummary = async () => {
    state.value.loading = true;
    state.value.error = null;
    
    try {
      const summary = await glAccountService.getAccountSummary();
      state.value.summary = summary;
      return summary;
    } catch (err: any) {
      state.value.error = err.message || 'Failed to fetch account summary';
      throw err;
    } finally {
      state.value.loading = false;
    }
  };

  const searchAccounts = async (query: string): Promise<GlAccount[]> => {
    state.value.loading = true;
    state.value.error = null;
    
    try {
      // TODO: Implement actual API call when service is available
      // const response = await glAccountService.searchAccounts({
      //   searchTerm: query,
      //   pageSize: 10,
      //   isActive: true
      // });
      
      // Mock data for now
      const mockAccounts: GlAccount[] = [
        {
          id: 'mock-1',
          accountNumber: '1000',
          name: 'Cash and Cash Equivalents',
          accountType: 'asset',
          accountCategory: 'current_asset',
          status: 'active',
          isDetailAccount: true,
          isSystemAccount: false,
          isLocked: false,
          level: 0,
          sortOrder: 1,
          openingBalance: 0,
          currentBalance: 0,
          yearToDateBalance: 0,
          isDeleted: false,
          currency: 'USD',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          createdBy: 'system',
          customFields: {}
        } as GlAccount
      ];
      
      // Update accounts in state
      mockAccounts.forEach((account: GlAccount) => {
        state.value.accounts[account.id] = account;
      });
      
      return mockAccounts;
    } catch (err: any) {
      state.value.error = err.message || 'Failed to search accounts';
      throw err;
    } finally {
      state.value.loading = false;
    }
  };

  const fetchAccountBalanceHistory = async (accountId: string, startDate: string, endDate: string): Promise<GlAccountBalanceHistory[]> => {
    state.value.loading = true;
    state.value.error = null;
    
    try {
      // TODO: Implement actual API call when service is available
      // const response = await glAccountService.fetchAccountBalanceHistory(accountId, startDate, endDate);
      // return response.data;
      
      // Mock data for now
      return [
        {
          date: new Date().toISOString(),
          balance: 1000,
          change: 100,
          transactionCount: 1,
          openingBalance: 900,
          closingBalance: 1000
        }
      ];
    } catch (err: any) {
      state.value.error = err.message || 'Failed to fetch account balance history';
      throw err;
    } finally {
      state.value.loading = false;
    }
  };

  // Helper function to remove an account from the hierarchy
  const removeFromHierarchy = (accountId: string, items: GlAccountTree[] = state.value.hierarchy): boolean => {
    for (let i = 0; i < items.length; i++) {
      if (items[i].id === accountId) {
        items.splice(i, 1);
        return true;
      }
      
      if (items[i].children && items[i].children!.length > 0) {
        if (removeFromHierarchy(accountId, items[i].children)) {
          return true;
        }
      }
    }
    
    return false;
  };

  // Reset store state
  const reset = () => {
    state.value = {
      accounts: {},
      hierarchy: [],
      selectedAccount: null,
      loading: false,
      error: null,
      summary: null,
      filters: {
        search: '',
        accountType: undefined,
        isActive: true,
        page: 1,
        limit: 20,
        sortBy: 'accountNumber',
        sortOrder: 'asc',
      },
    };
  };

  return {
    state,
    accounts: computed(() => state.value.accounts),
    account: computed(() => state.value.account),
    hierarchy: computed(() => state.value.hierarchy),
    loading: computed(() => state.value.loading),
    error: computed(() => state.value.error),
    summary: computed(() => state.value.summary),
    filters: computed(() => state.value.filters),
    
    // Actions
    setFilters,
    resetFilters,
    fetchAccounts,
    fetchAccount,
    createAccount,
    updateAccount,
    deleteAccount,
    fetchHierarchy,
    moveAccount,
    bulkUpdateAccounts: async (updates: GlAccountBulkUpdateDto) => {
      // TODO: Implement bulk update when API is ready
      console.log('Bulk update accounts:', updates);
    },
    reconcileAccount: async (data: GlAccountReconcileDto) => {
      // TODO: Implement reconcile when API is ready
      console.log('Reconcile account:', data);
    },
    fetchSummary,
    fetchAccountBalanceHistory,
    exportAccounts: async (options: GlAccountExportDto) => {
      // TODO: Implement export when API is ready
      console.log('Export accounts:', options);
      return new Blob(['Mock export data'], { type: 'text/csv' });
    },
    searchAccounts,
    importAccounts: async (file: File, options: any) => {
      // TODO: Implement import when API is ready
      console.log('Import accounts:', file, options);
      return { success: true, imported: 0, errors: [] };
    },
    fetchAccountTransactions: async (accountId: string, filters: any) => {
      // TODO: Implement fetch transactions when API is ready
      console.log('Fetch transactions for account:', accountId, filters);
      return [];
    },
    fetchAccountReconciliationStatus: async (accountId: string) => {
      // TODO: Implement fetch reconciliation status when API is ready
      console.log('Fetch reconciliation status for account:', accountId);
      return { isReconciled: false, lastReconciledAt: null };
    },
    lockAccount: async (accountId: string, reason: string) => {
      // TODO: Implement lock account when API is ready
      console.log('Lock account:', accountId, reason);
      return true;
    },
    unlockAccount: async (accountId: string) => {
      // TODO: Implement unlock account when API is ready
      console.log('Unlock account:', accountId);
      return true;
    },
    fetchAccountActivity: async (accountId: string, period: string) => {
      // TODO: Implement fetch activity when API is ready
      console.log('Fetch activity for account:', accountId, period);
      return [];
    },
    fetchAccountBalanceTrend: async (accountId: string, period: string) => {
      // TODO: Implement fetch balance trend when API is ready
      console.log('Fetch balance trend for account:', accountId, period);
      return [];
    },
    fetchAccountBudget: async (accountId: string, period: string) => {
      // TODO: Implement fetch budget when API is ready
      console.log('Fetch budget for account:', accountId, period);
      return null;
    },
    updateAccountBudget: async (accountId: string, budget: any) => {
      // TODO: Implement update budget when API is ready
      console.log('Update budget for account:', accountId, budget);
      return true;
    },
    fetchAccountAllocations: async (accountId: string) => {
      // TODO: Implement fetch allocations when API is ready
      console.log('Fetch allocations for account:', accountId);
      return [];
    },
    createAccountAllocation: async (allocation: any) => {
      // TODO: Implement create allocation when API is ready
      console.log('Create allocation:', allocation);
      return { id: 'mock-allocation-id' };
    },
    deleteAccountAllocation: async (allocationId: string) => {
      // TODO: Implement delete allocation when API is ready
      console.log('Delete allocation:', allocationId);
      return true;
    }
  };
});

export default useGlAccountStore;
