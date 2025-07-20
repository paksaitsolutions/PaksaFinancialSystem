import { defineStore } from 'pinia';
import { ref } from 'vue';
import { 
  DeductionBenefit, 
  DeductionBenefitFormData 
} from '../services/payrollApiService';
import { payrollApiService } from '../services/payrollApiService';

interface DeductionBenefitState {
  items: DeductionBenefit[];
  selectedItem: DeductionBenefit | null;
  loading: boolean;
  error: string | null;
  currentPage: number;
  totalItems: number;
  itemsPerPage: number;
  filter: {
    type: string;
    activeOnly: boolean;
    search: string;
  };
}

export const useDeductionBenefitStore = defineStore('deductionBenefit', () => {
  // State
  const state = ref<DeductionBenefitState>({
    items: [],
    selectedItem: null,
    loading: false,
    error: null,
    currentPage: 1,
    totalItems: 0,
    itemsPerPage: 10,
    filter: {
      type: '',
      activeOnly: true,
      search: ''
    }
  });

  // Getters
  const filteredItems = () => {
    return state.value.items.filter(item => {
      const matchesType = !state.value.filter.type || item.type === state.value.filter.type;
      const matchesActive = !state.value.filter.activeOnly || item.active === true;
      const matchesSearch = !state.value.filter.search || 
        item.name.toLowerCase().includes(state.value.filter.search.toLowerCase()) ||
        item.description?.toLowerCase().includes(state.value.filter.search.toLowerCase());
      
      return matchesType && matchesActive && matchesSearch;
    });
  };

  const paginatedItems = () => {
    const start = (state.value.currentPage - 1) * state.value.itemsPerPage;
    const end = start + state.value.itemsPerPage;
    return filteredItems().slice(start, end);
  };

  // Actions
  const fetchItems = async () => {
    state.value.loading = true;
    state.value.error = null;
    
    try {
      const params = {
        active_only: state.value.filter.activeOnly,
        type: state.value.filter.type || undefined,
        search: state.value.filter.search || undefined
      };
      
      const items = await payrollApiService.getDeductionsBenefits(params);
      state.value.items = items;
      state.value.totalItems = items.length;
    } catch (error) {
      console.error('Failed to fetch deductions/benefits:', error);
      state.value.error = 'Failed to load deductions/benefits. Please try again.';
      throw error;
    } finally {
      state.value.loading = false;
    }
  };

  const getItemById = async (id: number) => {
    const existing = state.value.items.find(item => item.id === id);
    if (existing) {
      state.value.selectedItem = existing;
      return existing;
    }

    try {
      state.value.loading = true;
      const item = await payrollApiService.getDeductionBenefit(id);
      state.value.selectedItem = item;
      return item;
    } catch (error) {
      console.error(`Failed to fetch deduction/benefit ${id}:`, error);
      state.value.error = 'Failed to load deduction/benefit details.';
      throw error;
    } finally {
      state.value.loading = false;
    }
  };

  const createItem = async (formData: DeductionBenefitFormData) => {
    try {
      state.value.loading = true;
      const newItem = await payrollApiService.createDeductionBenefit(formData);
      state.value.items.unshift(newItem);
      state.value.totalItems++;
      return newItem;
    } catch (error) {
      console.error('Failed to create deduction/benefit:', error);
      state.value.error = 'Failed to create deduction/benefit. Please check your input and try again.';
      throw error;
    } finally {
      state.value.loading = false;
    }
  };

  const updateItem = async (id: number, updates: Partial<DeductionBenefitFormData>) => {
    try {
      state.value.loading = true;
      const updatedItem = await payrollApiService.updateDeductionBenefit(id, updates);
      
      const index = state.value.items.findIndex(item => item.id === id);
      if (index !== -1) {
        state.value.items[index] = updatedItem;
      }
      
      if (state.value.selectedItem?.id === id) {
        state.value.selectedItem = updatedItem;
      }
      
      return updatedItem;
    } catch (error) {
      console.error(`Failed to update deduction/benefit ${id}:`, error);
      state.value.error = 'Failed to update deduction/benefit. Please try again.';
      throw error;
    } finally {
      state.value.loading = false;
    }
  };

  const deleteItem = async (id: number) => {
    try {
      state.value.loading = true;
      await payrollApiService.deleteDeductionBenefit(id);
      
      const index = state.value.items.findIndex(item => item.id === id);
      if (index !== -1) {
        state.value.items.splice(index, 1);
        state.value.totalItems--;
      }
      
      if (state.value.selectedItem?.id === id) {
        state.value.selectedItem = null;
      }
    } catch (error) {
      console.error(`Failed to delete deduction/benefit ${id}:`, error);
      state.value.error = 'Failed to delete deduction/benefit. Please try again.';
      throw error;
    } finally {
      state.value.loading = false;
    }
  };

  const exportItems = async (format: string, options: any = {}) => {
    try {
      state.value.loading = true;
      const result = await payrollApiService.exportDeductionsBenefits(format, {
        ...options,
        filter: state.value.filter
      });
      return result.url;
    } catch (error) {
      console.error('Failed to export deductions/benefits:', error);
      state.value.error = 'Failed to export data. Please try again.';
      throw error;
    } finally {
      state.value.loading = false;
    }
  };

  // Reset state
  const resetState = () => {
    state.value = {
      items: [],
      selectedItem: null,
      loading: false,
      error: null,
      currentPage: 1,
      totalItems: 0,
      itemsPerPage: 10,
      filter: {
        type: '',
        activeOnly: true,
        search: ''
      }
    };
  };

  return {
    // State
    state,
    
    // Getters
    filteredItems,
    paginatedItems,
    
    // Actions
    fetchItems,
    getItemById,
    createItem,
    updateItem,
    deleteItem,
    exportItems,
    resetState
  };
});

export default useDeductionBenefitStore;
