import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useApi } from '@/composables/useApi';
import type { Vendor } from '../types';

export const useVendorsStore = defineStore('ap/vendors', () => {
  const api = useApi();
  
  // State
  const vendors = ref<Vendor[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const selectedVendor = ref<Vendor | null>(null);
  const totalVendors = ref(0);
  
  // Getters
  const activeVendors = computed(() => 
    vendors.value.filter(vendor => vendor.status === 'active')
  );
  
  const inactiveVendors = computed(() => 
    vendors.value.filter(vendor => vendor.status === 'inactive')
  );
  
  // Actions
  const fetchVendors = async (params = {}) => {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await api.get('/ap/vendors', { params });
      vendors.value = response.data.data;
      totalVendors.value = response.data.meta?.total || vendors.value.length;
      return response.data;
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch vendors';
      throw err;
    } finally {
      loading.value = false;
    }
  };
  
  const fetchVendorById = async (id: string | number) => {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await api.get(`/ap/vendors/${id}`);
      selectedVendor.value = response.data.data;
      return response.data;
    } catch (err: any) {
      error.value = err.message || `Failed to fetch vendor with ID ${id}`;
      throw err;
    } finally {
      loading.value = false;
    }
  };
  
  const createVendor = async (vendorData: Partial<Vendor>) => {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await api.post('/ap/vendors', vendorData);
      vendors.value.push(response.data.data);
      return response.data;
    } catch (err: any) {
      error.value = err.message || 'Failed to create vendor';
      throw err;
    } finally {
      loading.value = false;
    }
  };
  
  const updateVendor = async (id: string | number, vendorData: Partial<Vendor>) => {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await api.put(`/ap/vendors/${id}`, vendorData);
      const index = vendors.value.findIndex(v => v.id === id);
      if (index !== -1) {
        vendors.value[index] = { ...vendors.value[index], ...response.data.data };
      }
      if (selectedVendor.value?.id === id) {
        selectedVendor.value = { ...selectedVendor.value, ...response.data.data };
      }
      return response.data;
    } catch (err: any) {
      error.value = err.message || `Failed to update vendor with ID ${id}`;
      throw err;
    } finally {
      loading.value = false;
    }
  };
  
  const deleteVendor = async (id: string | number) => {
    loading.value = true;
    error.value = null;
    
    try {
      await api.delete(`/ap/vendors/${id}`);
      vendors.value = vendors.value.filter(v => v.id !== id);
      if (selectedVendor.value?.id === id) {
        selectedVendor.value = null;
      }
    } catch (err: any) {
      error.value = err.message || `Failed to delete vendor with ID ${id}`;
      throw err;
    } finally {
      loading.value = false;
    }
  };
  
  // Initialize the store
  const initialize = async () => {
    await fetchVendors();
  };
  
  return {
    // State
    vendors,
    loading,
    error,
    selectedVendor,
    totalVendors,
    
    // Getters
    activeVendors,
    inactiveVendors,
    
    // Actions
    fetchVendors,
    fetchVendorById,
    createVendor,
    updateVendor,
    deleteVendor,
    initialize,
    
    // Reset function for Pinia
    $reset: () => {
      vendors.value = [];
      loading.value = false;
      error.value = null;
      selectedVendor.value = null;
      totalVendors.value = 0;
    },
  };
});
