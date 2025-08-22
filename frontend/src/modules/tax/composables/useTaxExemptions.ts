import { ref, computed } from 'vue';
import { useTaxPolicyStore } from '@/stores/taxPolicy';
import type { TaxExemption, TaxExemptionFormData } from '@/types/tax';

export function useTaxExemptions() {
  const taxPolicyStore = useTaxPolicyStore();
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Computed properties
  const taxExemptions = computed(() => taxPolicyStore.taxExemptions);
  const currentExemption = computed(() => taxPolicyStore.currentExemption);

  // Methods
  const fetchTaxExemptions = async (filter = {}) => {
    loading.value = true;
    error.value = null;
    try {
      await taxPolicyStore.fetchTaxExemptions(filter);
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
      return await taxPolicyStore.fetchTaxExemption(id);
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
      return await taxPolicyStore.createTaxExemption(data);
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
      return await taxPolicyStore.updateTaxExemption(id, data);
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
      await taxPolicyStore.deleteTaxExemption(id);
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete tax exemption';
      throw error.value;
    } finally {
      loading.value = false;
    }
  };

  const resetTaxExemption = () => {
    taxPolicyStore.reset();
  };

  return {
    // State
    loading: computed(() => loading.value),
    error: computed(() => error.value),
    
    // Computed
    taxExemptions,
    currentExemption,
    
    // Methods
    fetchTaxExemptions,
    fetchTaxExemption,
    createTaxExemption,
    updateTaxExemption,
    deleteTaxExemption,
    resetTaxExemption,
  };
}

export default useTaxExemptions;
