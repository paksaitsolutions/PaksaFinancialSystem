import { defineStore } from 'pinia';
import { ref } from 'vue';
import { useApi } from '@/composables/useApi';
import type { 
  TaxExemption, 
  TaxExemptionFormData,
  TaxExemptionFilter
} from '@/types/tax';

const api = useApi();

export const useTaxPolicyStore = defineStore('taxPolicy', () => {
  // State
  const taxExemptions = ref<TaxExemption[]>([]);
  const currentExemption = ref<TaxExemption | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Getters
  const getExemptionById = (id: string) => 
    taxExemptions.value.find(e => e.id === id) || null;

  // Actions
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
      currentExemption.value = response.data.data;
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
      if (currentExemption.value?.id === id) {
        currentExemption.value = response.data.data;
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
      if (currentExemption.value?.id === id) {
        currentExemption.value = null;
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to delete tax exemption';
      throw error.value;
    } finally {
      loading.value = false;
    }
  };

  const downloadTaxExemptionCertificate = async (id: string, filename: string) => {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await api.get(`/api/v1/tax/exemptions/${id}/download`, {
        responseType: 'blob',
      });
      
      // Get the filename from the Content-Disposition header if available
      const contentDisposition = response.headers['content-disposition'];
      let downloadFilename = filename;
      
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
        if (filenameMatch && filenameMatch[1]) {
          downloadFilename = filenameMatch[1].replace(/['"]/g, '');
        }
      }
      
      // Create a blob URL for the file
      const url = window.URL.createObjectURL(new Blob([response.data]));
      
      // Create a temporary anchor element to trigger the download
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', downloadFilename);
      document.body.appendChild(link);
      
      // Trigger the download
      link.click();
      
      // Clean up
      link.remove();
      window.URL.revokeObjectURL(url);
      
      return true;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to download certificate';
      error.value = errorMessage;
      throw new Error(errorMessage);
    } finally {
      loading.value = false;
    }
  };

  // Reset state
  const reset = () => {
    taxExemptions.value = [];
    currentExemption.value = null;
    loading.value = false;
    error.value = null;
  };

  return {
    // State
    taxExemptions,
    currentExemption,
    loading,
    error,
    
    // Getters
    getExemptionById,
    
    // Actions
    fetchTaxExemptions,
    fetchTaxExemption,
    createTaxExemption,
    updateTaxExemption,
    deleteTaxExemption,
    downloadTaxExemptionCertificate,
    reset
  };
});

export default useTaxPolicyStore;
