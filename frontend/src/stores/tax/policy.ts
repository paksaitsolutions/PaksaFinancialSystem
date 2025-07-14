import { defineStore } from 'pinia';
import { ref } from 'vue';
import { TaxPolicy, TaxRate, TaxExemption } from '@/types/tax';
import { taxReportingService } from '@/services/api/taxReportingService';

interface TaxPolicyState {
  currentPolicy: TaxPolicy | null;
  taxRates: TaxRate[];
  taxExemptions: TaxExemption[];
  loading: boolean;
  error: string | null;
}

export const useTaxPolicyStore = defineStore('taxPolicy', () => {
  const state = ref<TaxPolicyState>({
    currentPolicy: null,
    taxRates: [],
    taxExemptions: [],
    loading: false,
    error: null
  });

  const getCurrentPolicy = () => state.value.currentPolicy;
  const getTaxRates = () => state.value.taxRates;
  const getTaxExemptions = () => state.value.taxExemptions;
  const isLoading = () => state.value.loading;
  const getError = () => state.value.error;

  async function fetchPolicy() {
    try {
      state.value.loading = true;
      state.value.error = null;
      
      const response = await taxReportingService.getCurrentPolicy();
      state.value.currentPolicy = response;
      state.value.taxRates = response.tax_rates || [];
      state.value.taxExemptions = response.tax_exemptions || [];
    } catch (error) {
      console.error('Error fetching tax policy:', error);
      state.value.error = error instanceof Error ? error.message : 'Failed to fetch tax policy';
    } finally {
      state.value.loading = false;
    }
  }

  async function updatePolicy(policy: Partial<TaxPolicy>) {
    try {
      state.value.loading = true;
      state.value.error = null;
      
      const response = await taxReportingService.updatePolicy(policy);
      state.value.currentPolicy = { ...state.value.currentPolicy, ...response };
    } catch (error) {
      console.error('Error updating tax policy:', error);
      state.value.error = error instanceof Error ? error.message : 'Failed to update tax policy';
    } finally {
      state.value.loading = false;
    }
  }

  async function addTaxRate(rate: TaxRate) {
    try {
      state.value.loading = true;
      state.value.error = null;
      
      const response = await taxReportingService.addTaxRate(rate);
      state.value.taxRates = [...state.value.taxRates, response];
    } catch (error) {
      console.error('Error adding tax rate:', error);
      state.value.error = error instanceof Error ? error.message : 'Failed to add tax rate';
    } finally {
      state.value.loading = false;
    }
  }

  async function updateTaxRate(rateId: string, updates: Partial<TaxRate>) {
    try {
      state.value.loading = true;
      state.value.error = null;
      
      const response = await taxReportingService.updateTaxRate(rateId, updates);
      state.value.taxRates = state.value.taxRates.map(
        rate => (rate.id === rateId ? { ...rate, ...response } : rate)
      );
    } catch (error) {
      console.error('Error updating tax rate:', error);
      state.value.error = error instanceof Error ? error.message : 'Failed to update tax rate';
    } finally {
      state.value.loading = false;
    }
  }

  async function removeTaxRate(rateId: string) {
    try {
      state.value.loading = true;
      state.value.error = null;
      
      await taxReportingService.removeTaxRate(rateId);
      state.value.taxRates = state.value.taxRates.filter(rate => rate.id !== rateId);
    } catch (error) {
      console.error('Error removing tax rate:', error);
      state.value.error = error instanceof Error ? error.message : 'Failed to remove tax rate';
    } finally {
      state.value.loading = false;
    }
  }

  async function addTaxExemption(exemption: TaxExemption) {
    try {
      state.value.loading = true;
      state.value.error = null;
      
      const response = await taxReportingService.addTaxExemption(exemption);
      state.value.taxExemptions = [...state.value.taxExemptions, response];
    } catch (error) {
      console.error('Error adding tax exemption:', error);
      state.value.error = error instanceof Error ? error.message : 'Failed to add tax exemption';
    } finally {
      state.value.loading = false;
    }
  }

  async function updateTaxExemption(exemptionId: string, updates: Partial<TaxExemption>) {
    try {
      state.value.loading = true;
      state.value.error = null;
      
      const response = await taxReportingService.updateTaxExemption(exemptionId, updates);
      state.value.taxExemptions = state.value.taxExemptions.map(
        exemption => (exemption.id === exemptionId ? { ...exemption, ...response } : exemption)
      );
    } catch (error) {
      console.error('Error updating tax exemption:', error);
      state.value.error = error instanceof Error ? error.message : 'Failed to update tax exemption';
    } finally {
      state.value.loading = false;
    }
  }

  async function removeTaxExemption(exemptionId: string) {
    try {
      state.value.loading = true;
      state.value.error = null;
      
      await taxReportingService.removeTaxExemption(exemptionId);
      state.value.taxExemptions = state.value.taxExemptions.filter(
        exemption => exemption.id !== exemptionId
      );
    } catch (error) {
      console.error('Error removing tax exemption:', error);
      state.value.error = error instanceof Error ? error.message : 'Failed to remove tax exemption';
    } finally {
      state.value.loading = false;
    }
  }

  return {
    // Getters
    getCurrentPolicy,
    getTaxRates,
    getTaxExemptions,
    isLoading,
    getError,

    // Actions
    fetchPolicy,
    updatePolicy,
    addTaxRate,
    updateTaxRate,
    removeTaxRate,
    addTaxExemption,
    updateTaxExemption,
    removeTaxExemption
  };
});
