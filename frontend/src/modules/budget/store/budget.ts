import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useToast } from 'primevue/usetoast';
import { 
  BudgetResponse as Budget, 
  BudgetStatus, 
  BudgetType, 
  type BudgetLine, 
  type BudgetAllocation, 
  type BudgetRule, 
  type BudgetApproval,
  type BudgetCreate,
  type BudgetUpdate,
  type BudgetApprovalCreate,
  type BudgetFilters,
  type BudgetListResponse
} from '../types/budget';

interface BudgetState {
  budgets: Budget[];
  loading: boolean;
  error: string | null;
  currentBudget: Budget | null;
  budgetStatuses: { name: string; value: BudgetStatus }[];
  budgetTypes: { name: string; value: BudgetType }[];
}

export const useBudgetStore = defineStore('budget', () => {
  const toast = useToast();
  const state = ref<BudgetState>({
    budgets: [],
    loading: false,
    error: null,
    currentBudget: null,
    budgetStatuses: [
      { name: 'Draft', value: BudgetStatus.DRAFT },
      { name: 'Approved', value: BudgetStatus.APPROVED },
      { name: 'Rejected', value: BudgetStatus.REJECTED },
      { name: 'Archived', value: BudgetStatus.ARCHIVED }
    ],
    budgetTypes: [
      { name: 'Operational', value: BudgetType.OPERATIONAL },
      { name: 'Capital', value: BudgetType.CAPITAL },
      { name: 'Project', value: BudgetType.PROJECT },
      { name: 'Department', value: BudgetType.DEPARTMENT }
    ]
  });

  // Getters
  const budgets = computed(() => state.value.budgets);
  const loading = computed(() => state.value.loading);
  const error = computed(() => state.value.error);
  const currentBudget = computed(() => state.value.currentBudget);
  const budgetStatuses = computed(() => state.value.budgetStatuses);
  const budgetTypes = computed(() => state.value.budgetTypes);

  // Actions
  const setLoading = (loading: boolean) => {
    state.value.loading = loading;
  };

  const setError = (error: string | null) => {
    state.value.error = error;
    if (error) {
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: error,
        life: 5000,
      });
    }
  };

  const setBudgets = (budgets: Budget[]) => {
    state.value.budgets = budgets;
  };

  const setCurrentBudget = (budget: Budget | null) => {
    state.value.currentBudget = budget;
  };

  // Fetch all budgets with optional filters
  const fetchBudgets = async (_filters?: BudgetFilters): Promise<BudgetListResponse> => {
    try {
      setLoading(true);
      setError(null);
      // TODO: Replace with actual API call
      // const response = await BudgetService.getBudgets(filters);
      // setBudgets(response.data.budgets);
      // return response.data;
      
      // Mock response for now
      const mockResponse: BudgetListResponse = {
        budgets: [],
        total: 0,
        page: 1,
        limit: 10
      };
      return mockResponse;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to fetch budgets';
      setError(errorMessage);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // Fetch a single budget by ID
  const fetchBudgetById = async (id: number): Promise<Budget | null> => {
    try {
      setLoading(true);
      setError(null);
      // TODO: Replace with actual API call
      // const response = await BudgetService.getBudgetById(id);
      // setCurrentBudget(response.data);
      // return response.data;
      return null;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to fetch budget';
      setError(errorMessage);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // Create a new budget
  const createBudget = async (budgetData: BudgetCreate): Promise<Budget> => {
    try {
      setLoading(true);
      setError(null);
      // TODO: Replace with actual API call
      // const response = await BudgetService.createBudget(budgetData);
      // return response.data;
      throw new Error('Not implemented');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to create budget';
      setError(errorMessage);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // Update an existing budget
  const updateBudget = async (id: number, budgetData: BudgetUpdate): Promise<Budget> => {
    try {
      setLoading(true);
      setError(null);
      // TODO: Replace with actual API call
      // const response = await BudgetService.updateBudget(id, budgetData);
      // return response.data;
      throw new Error('Not implemented');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to update budget';
      setError(errorMessage);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // Delete a budget
  const deleteBudget = async (id: number): Promise<void> => {
    try {
      setLoading(true);
      setError(null);
      // TODO: Replace with actual API call
      // await BudgetService.deleteBudget(id);
      throw new Error('Not implemented');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to delete budget';
      setError(errorMessage);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // Submit a budget for approval
  const submitForApproval = async (id: number, _notes?: string): Promise<Budget> => {
    try {
      setLoading(true);
      setError(null);
      // TODO: Replace with actual API call
      // const response = await BudgetService.submitForApproval(id, { notes });
      // return response.data;
      throw new Error('Not implemented');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to submit budget for approval';
      setError(errorMessage);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // Approve a budget
  const approveBudget = async (_id: number, _approvalData: BudgetApprovalCreate): Promise<Budget> => {
    try {
      setLoading(true);
      setError(null);
      // TODO: Replace with actual API call
      // const response = await BudgetService.approveBudget(id, approvalData);
      // return response.data;
      throw new Error('Not implemented');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to approve budget';
      setError(errorMessage);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // Reject a budget
  const rejectBudget = async (id: number, reason: string): Promise<Budget> => {
    try {
      setLoading(true);
      setError(null);
      // TODO: Replace with actual API call
      // const response = await BudgetService.rejectBudget(id, { reason });
      // return response.data;
      throw new Error('Not implemented');
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to reject budget';
      setError(errorMessage);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // Get budget status display name
  const getStatusDisplayName = (status: BudgetStatus): string => {
    const statusObj = state.value.budgetStatuses.find(s => s.value === status);
    return statusObj ? statusObj.name : status;
  };

  // Get budget type display name
  const getTypeDisplayName = (type: BudgetType): string => {
    const typeObj = state.value.budgetTypes.find(t => t.value === type);
    return typeObj ? typeObj.name : type;
  };

  return {
    // State
    budgets,
    loading,
    error,
    currentBudget,
    budgetStatuses,
    budgetTypes,
    
    // Getters
    getStatusDisplayName,
    getTypeDisplayName,
    
    // Actions
    fetchBudgets,
    fetchBudgetById,
    createBudget,
    updateBudget,
    deleteBudget,
    submitForApproval,
    approveBudget,
    rejectBudget,
    setCurrentBudget,
  };
});
