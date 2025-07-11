import { defineStore } from 'pinia';
import { ref } from 'vue';
import { useApi } from '@/composables/useApi';
import type { 
  TaxExemption, 
  TaxExemptionFormData,
  TaxExemptionFilter,
  TaxRule,
  TaxRuleFormData,
  TaxRuleFilter
} from '@/types/tax';

const api = useApi();

export const useTaxStore = defineStore('tax', () => {
  // State
  const taxExemptions = ref<TaxExemption[]>([]);
  const taxExemption = ref<TaxExemption | null>(null);
  const taxRules = ref<TaxRule[]>([]);
  const taxRule = ref<TaxRule | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Getters
  const getTaxExemptionById = (id: string) => 
    taxExemptions.value.find(e => e.id === id) || null;

  const getTaxRuleById = (id: string) => 
    taxRules.value.find(r => r.id === id) || null;

  // Actions
  // Tax Exemptions
  const fetchTaxExemptions = async (filter?: TaxExemptionFilter) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await api.get('/api/v1/tax/exemptions', { params: filter });
      taxExemptions.value = response.data.data;
      return response.data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch tax exemptions';
      throw error.value;
    } finally {
      loading.value = false;
    }
  };

  const fetchTaxExemption = async (id: string) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await api.get(`/api/v1/tax/exemptions/${id}`);
      taxExemption.value = response.data.data;
      return response.data.data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch tax exemption';
      throw error.value;
    } finally {
      loading.value = false;
    }
  };

  const createTaxExemption = async (data: TaxExemptionFormData) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await api.post('/api/v1/tax/exemptions', data);
      taxExemptions.value.push(response.data.data);
      return response.data.data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to create tax exemption';
      throw error.value;
    } finally {
      loading.value = false;
    }
  };

  const updateTaxExemption = async (id: string, data: Partial<TaxExemptionFormData>) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await api.put(`/api/v1/tax/exemptions/${id}`, data);
      const index = taxExemptions.value.findIndex(e => e.id === id);
      if (index !== -1) {
        taxExemptions.value[index] = response.data.data;
      }
      if (taxExemption.value?.id === id) {
        taxExemption.value = response.data.data;
      }
      return response.data.data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update tax exemption';
      throw error.value;
    } finally {
      loading.value = false;
    }
  };

  const deleteTaxExemption = async (id: string) => {
    loading.value = true;
    error.value = null;
    try {
      await api.delete(`/api/v1/tax/exemptions/${id}`);
      taxExemptions.value = taxExemptions.value.filter(e => e.id !== id);
      if (taxExemption.value?.id === id) {
        taxExemption.value = null;
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete tax exemption';
      throw error.value;
    } finally {
      loading.value = false;
    }
  };

  // Tax Rules
  const fetchTaxRules = async (filter?: TaxRuleFilter) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await api.get('/api/v1/tax/rules', { params: filter });
      taxRules.value = response.data.data;
      return response.data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch tax rules';
      throw error.value;
    } finally {
      loading.value = false;
    }
  };

  const fetchTaxRule = async (id: string) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await api.get(`/api/v1/tax/rules/${id}`);
      taxRule.value = response.data.data;
      return response.data.data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch tax rule';
      throw error.value;
    } finally {
      loading.value = false;
    }
  };

  const createTaxRule = async (data: TaxRuleFormData) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await api.post('/api/v1/tax/rules', data);
      taxRules.value.push(response.data.data);
      return response.data.data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to create tax rule';
      throw error.value;
    } finally {
      loading.value = false;
    }
  };

  const updateTaxRule = async (id: string, data: Partial<TaxRuleFormData>) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await api.put(`/api/v1/tax/rules/${id}`, data);
      const index = taxRules.value.findIndex(r => r.id === id);
      if (index !== -1) {
        taxRules.value[index] = response.data.data;
      }
      if (taxRule.value?.id === id) {
        taxRule.value = response.data.data;
      }
      return response.data.data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to update tax rule';
      throw error.value;
    } finally {
      loading.value = false;
    }
  };

  const deleteTaxRule = async (id: string) => {
    loading.value = true;
    error.value = null;
    try {
      await api.delete(`/api/v1/tax/rules/${id}`);
      taxRules.value = taxRules.value.filter(r => r.id !== id);
      if (taxRule.value?.id === id) {
        taxRule.value = null;
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete tax rule';
      throw error.value;
    } finally {
      loading.value = false;
    }
  };

  // Reset state
  const reset = () => {
    taxExemptions.value = [];
    taxExemption.value = null;
    taxRules.value = [];
    taxRule.value = null;
    loading.value = false;
    error.value = null;
  };

  return {
    // State
    taxExemptions,
    taxExemption,
    taxRules,
    taxRule,
    loading,
    error,
    
    // Getters
    getTaxExemptionById,
    getTaxRuleById,
    
    // Actions - Tax Exemptions
    fetchTaxExemptions,
    fetchTaxExemption,
    createTaxExemption,
    updateTaxExemption,
    deleteTaxExemption,
    
    // Actions - Tax Rules
    fetchTaxRules,
    fetchTaxRule,
    createTaxRule,
    updateTaxRule,
    deleteTaxRule,
    
    // Reset
    reset
  };
});

export default useTaxStore;
