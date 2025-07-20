import { ref, computed } from 'vue';
import { useApi } from '@/shared/composables/useApi';
import { glAccountService } from '../api/gl-account.service';
import type { 
  GlAccount, 
  CreateGlAccountDto, 
  UpdateGlAccountDto,
  GlAccountFilters,
  GlAccountSummary,
  GlAccountType
} from '../types/gl-account';

export function useGlAccounts() {
  // State
  const accounts = ref<GlAccount[]>([]);
  const currentAccount = ref<GlAccount | null>(null);
  const accountHierarchy = ref<GlAccount[]>([]);
  const accountSummary = ref<GlAccountSummary | null>(null);
  const totalAccounts = ref(0);
  const currentFilters = ref<GlAccountFilters>({});

  // API Composables
  const fetchApi = useApi<{ data: GlAccount[]; total: number }>();
  const singleApi = useApi<GlAccount>();
  const summaryApi = useApi<GlAccountSummary>();
  const hierarchyApi = useApi<GlAccount[]>();

  // Computed
  const isLoading = computed(() => 
    fetchApi.loading.value || 
    singleApi.loading.value || 
    summaryApi.loading.value ||
    hierarchyApi.loading.value
  );

  const error = computed(() => 
    fetchApi.error.value || 
    singleApi.error.value || 
    summaryApi.error.value ||
    hierarchyApi.error.value
  );

  // Methods
  const fetchAccounts = async (filters: GlAccountFilters = {}) => {
    currentFilters.value = { ...filters };
    const result = await fetchApi.execute(() => 
      glAccountService.fetchAccounts(filters)
    );
    
    if (result) {
      accounts.value = result.data;
      totalAccounts.value = result.total;
    }
    
    return result;
  };

  const fetchAccountById = async (id: string | number) => {
    const result = await singleApi.execute(() => 
      glAccountService.fetchAccountById(id)
    );
    
    if (result) {
      currentAccount.value = result;
    }
    
    return result;
  };

  const createAccount = async (data: CreateGlAccountDto) => {
    const result = await singleApi.execute(() => 
      glAccountService.createAccount(data)
    );
    
    if (result) {
      // Refresh the accounts list
      await fetchAccounts(currentFilters.value);
    }
    
    return result;
  };

  const updateAccount = async (id: string | number, data: UpdateGlAccountDto) => {
    const result = await singleApi.execute(() => 
      glAccountService.updateAccount(id, data)
    );
    
    if (result) {
      // Refresh the accounts list and current account
      await Promise.all([
        fetchAccounts(currentFilters.value),
        fetchAccountById(id)
      ]);
    }
    
    return result;
  };

  const deleteAccount = async (id: string | number) => {
    await singleApi.execute(() => glAccountService.deleteAccount(id));
    // Refresh the accounts list
    await fetchAccounts(currentFilters.value);
  };

  const fetchAccountSummary = async () => {
    const result = await summaryApi.execute(() => 
      glAccountService.getAccountSummary()
    );
    
    if (result) {
      accountSummary.value = result;
    }
    
    return result;
  };

  const fetchAccountHierarchy = async (parentId?: string | number) => {
    const result = await hierarchyApi.execute(() => 
      glAccountService.getAccountHierarchy(parentId)
    );
    
    if (result) {
      accountHierarchy.value = result;
    }
    
    return result;
  };

  const resetCurrentAccount = () => {
    currentAccount.value = null;
  };

  return {
    // State
    accounts,
    currentAccount,
    accountHierarchy,
    accountSummary,
    totalAccounts,
    currentFilters,
    
    // Computed
    isLoading,
    error,
    
    // Methods
    fetchAccounts,
    fetchAccountById,
    createAccount,
    updateAccount,
    deleteAccount,
    fetchAccountSummary,
    fetchAccountHierarchy,
    resetCurrentAccount,
  };
}
