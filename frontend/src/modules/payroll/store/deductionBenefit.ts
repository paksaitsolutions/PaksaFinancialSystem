import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { useToast } from 'primevue/usetoast';
import { api } from '@/api';

export interface DeductionBenefit {
  id?: string;
  code: string;
  name: string;
  description?: string;
  type: 'deduction' | 'benefit';
  amountType: 'fixed' | 'percentage';
  amount: number;
  isTaxable: boolean;
  isActive: boolean;
  effectiveDate: string;
  glAccountId?: string;
  glAccountCode?: string;
  glAccountName?: string;
  createdBy?: string;
  createdAt?: string;
  updatedBy?: string;
  updatedAt?: string;
}

export interface GLAccount {
  id: string;
  code: string;
  name: string;
  fullName: string;
  accountType: string;
  isActive: boolean;
}

interface DeductionBenefitState {
  deductionBenefits: DeductionBenefit[];
  totalRecords: number;
  loading: boolean;
  glAccounts: GLAccount[];
  glAccountsLoading: boolean;
}

export const useDeductionBenefitStore = defineStore('deductionBenefit', () => {
  const { t } = useI18n();
  const toast = useToast();
  
  // State
  const state = ref<DeductionBenefitState>({
    deductionBenefits: [],
    totalRecords: 0,
    loading: false,
    glAccounts: [],
    glAccountsLoading: false
  });

  // Getters
  const deductionBenefits = computed(() => state.value.deductionBenefits);
  const totalRecords = computed(() => state.value.totalRecords);
  const loading = computed(() => state.value.loading);
  const glAccounts = computed(() => state.value.glAccounts);
  const glAccountsLoading = computed(() => state.value.glAccountsLoading);

  // Actions
  const fetchDeductionBenefits = async (params: any = {}) => {
    try {
      state.value.loading = true;
      
      // Set default pagination if not provided
      const page = params.page || 1;
      const limit = params.limit || 10;
      
      // Prepare query parameters
      const queryParams: Record<string, any> = {
        page,
        limit,
        ...(params.sortField && { sort: `${params.sortField}:${params.sortOrder > 0 ? 'asc' : 'desc'}` }),
        ...(params.type && { type: params.type }),
        ...(params.search && { search: params.search }),
        ...(params.status !== undefined && { isActive: params.status })
      };
      
      // Remove undefined values
      Object.keys(queryParams).forEach(key => queryParams[key] === undefined && delete queryParams[key]);
      
      const response = await api.get('/payroll/deduction-benefits', { params: queryParams });
      
      state.value.deductionBenefits = response.data.data;
      state.value.totalRecords = response.data.meta.total;
      
      return response.data;
    } catch (error) {
      console.error('Error fetching deduction/benefit records:', error);
      toast.add({
        severity: 'error',
        summary: t('common.error'),
        detail: t('common.fetchError'),
        life: 5000
      });
      throw error;
    } finally {
      state.value.loading = false;
    }
  };

  const fetchDeductionBenefitById = async (id: string) => {
    try {
      state.value.loading = true;
      const response = await api.get(`/payroll/deduction-benefits/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching deduction/benefit with ID ${id}:`, error);
      toast.add({
        severity: 'error',
        summary: t('common.error'),
        detail: t('common.fetchError'),
        life: 5000
      });
      throw error;
    } finally {
      state.value.loading = false;
    }
  };

  const createDeductionBenefit = async (data: Partial<DeductionBenefit>) => {
    try {
      state.value.loading = true;
      const response = await api.post('/payroll/deduction-benefits', data);
      
      toast.add({
        severity: 'success',
        summary: t('common.success'),
        detail: t('payroll.deductionBenefit.createSuccess'),
        life: 5000
      });
      
      return response.data;
    } catch (error: any) {
      console.error('Error creating deduction/benefit:', error);
      
      let errorMessage = t('common.saveError');
      if (error.response?.data?.message) {
        errorMessage = error.response.data.message;
      }
      
      toast.add({
        severity: 'error',
        summary: t('common.error'),
        detail: errorMessage,
        life: 5000
      });
      
      throw error;
    } finally {
      state.value.loading = false;
    }
  };

  const updateDeductionBenefit = async (data: Partial<DeductionBenefit> & { id: string }) => {
    try {
      state.value.loading = true;
      const { id, ...updateData } = data;
      const response = await api.put(`/payroll/deduction-benefits/${id}`, updateData);
      
      // Update the local state
      const index = state.value.deductionBenefits.findIndex(item => item.id === id);
      if (index !== -1) {
        state.value.deductionBenefits[index] = { ...state.value.deductionBenefits[index], ...updateData };
      }
      
      toast.add({
        severity: 'success',
        summary: t('common.success'),
        detail: t('payroll.deductionBenefit.updateSuccess'),
        life: 5000
      });
      
      return response.data;
    } catch (error: any) {
      console.error(`Error updating deduction/benefit with ID ${data.id}:`, error);
      
      let errorMessage = t('common.saveError');
      if (error.response?.data?.message) {
        errorMessage = error.response.data.message;
      }
      
      toast.add({
        severity: 'error',
        summary: t('common.error'),
        detail: errorMessage,
        life: 5000
      });
      
      throw error;
    } finally {
      state.value.loading = false;
    }
  };

  const deleteDeductionBenefit = async (id: string) => {
    try {
      state.value.loading = true;
      await api.delete(`/payroll/deduction-benefits/${id}`);
      
      // Remove from local state
      state.value.deductionBenefits = state.value.deductionBenefits.filter(item => item.id !== id);
      state.value.totalRecords--;
      
      toast.add({
        severity: 'success',
        summary: t('common.success'),
        detail: t('payroll.deductionBenefit.deleteSuccess'),
        life: 5000
      });
      
      return true;
    } catch (error) {
      console.error(`Error deleting deduction/benefit with ID ${id}:`, error);
      
      toast.add({
        severity: 'error',
        summary: t('common.error'),
        detail: t('common.deleteError'),
        life: 5000
      });
      
      throw error;
    } finally {
      state.value.loading = false;
    }
  };

  const toggleDeductionBenefitStatus = async (id: string, isActive: boolean) => {
    try {
      state.value.loading = true;
      const response = await api.patch(`/payroll/deduction-benefits/${id}/status`, { isActive });
      
      // Update local state
      const index = state.value.deductionBenefits.findIndex(item => item.id === id);
      if (index !== -1) {
        state.value.deductionBenefits[index].isActive = isActive;
      }
      
      toast.add({
        severity: 'success',
        summary: t('common.success'),
        detail: isActive 
          ? t('payroll.deductionBenefit.activateSuccess')
          : t('payroll.deductionBenefit.deactivateSuccess'),
        life: 5000
      });
      
      return response.data;
    } catch (error) {
      console.error(`Error toggling status for deduction/benefit with ID ${id}:`, error);
      
      toast.add({
        severity: 'error',
        summary: t('common.error'),
        detail: t('common.updateError'),
        life: 5000
      });
      
      throw error;
    } finally {
      state.value.loading = false;
    }
  };

  const fetchGLAccounts = async () => {
    try {
      if (state.value.glAccounts.length > 0) return; // Already loaded
      
      state.value.glAccountsLoading = true;
      const response = await api.get('/gl/accounts', {
        params: {
          limit: 1000, // Adjust based on expected number of accounts
          isActive: true,
          fields: 'id,code,name,fullName,accountType,isActive'
        }
      });
      
      state.value.glAccounts = response.data.data;
    } catch (error) {
      console.error('Error fetching GL accounts:', error);
      toast.add({
        severity: 'error',
        summary: t('common.error'),
        detail: t('common.fetchError'),
        life: 5000
      });
      throw error;
    } finally {
      state.value.glAccountsLoading = false;
    }
  };

  const exportDeductionBenefits = async (params: any): Promise<Blob> => {
    try {
      state.value.loading = true;
      
      const response = await api.get('/payroll/deduction-benefits/export', {
        params: {
          format: params.format,
          ...(params.startPage && { startPage: params.startPage }),
          ...(params.endPage && { endPage: params.endPage }),
          ...(params.type && { type: params.type }),
          ...(params.search && { search: params.search }),
          ...(params.status !== undefined && { isActive: params.status })
        },
        responseType: 'blob'
      });
      
      return response.data;
    } catch (error) {
      console.error('Error exporting deduction/benefit data:', error);
      
      toast.add({
        severity: 'error',
        summary: t('common.error'),
        detail: t('common.exportError'),
        life: 5000
      });
      
      throw error;
    } finally {
      state.value.loading = false;
    }
  };

  // Reset store state
  const $reset = () => {
    state.value = {
      deductionBenefits: [],
      totalRecords: 0,
      loading: false,
      glAccounts: [],
      glAccountsLoading: false
    };
  };

  return {
    // State
    state,
    
    // Getters
    deductionBenefits,
    totalRecords,
    loading,
    glAccounts,
    glAccountsLoading,
    
    // Actions
    fetchDeductionBenefits,
    fetchDeductionBenefitById,
    createDeductionBenefit,
    updateDeductionBenefit,
    deleteDeductionBenefit,
    toggleDeductionBenefitStatus,
    fetchGLAccounts,
    exportDeductionBenefits,
    $reset
  };
});

export type DeductionBenefitStore = ReturnType<typeof useDeductionBenefitStore>;
