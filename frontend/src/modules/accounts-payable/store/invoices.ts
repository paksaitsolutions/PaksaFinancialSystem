import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useApi } from '@/composables/useApi';
import type { Invoice } from '../types';

export const useInvoicesStore = defineStore('ap/invoices', () => {
  const api = useApi();
  
  // State
  const invoices = ref<Invoice[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const selectedInvoice = ref<Invoice | null>(null);
  const totalInvoices = ref(0);
  
  // Getters
  const pendingInvoices = computed(() => 
    invoices.value.filter(invoice => invoice.status === 'pending')
  );
  
  const approvedInvoices = computed(() => 
    invoices.value.filter(invoice => invoice.status === 'approved')
  );
  
  const paidInvoices = computed(() => 
    invoices.value.filter(invoice => invoice.status === 'paid')
  );
  
  const overdueInvoices = computed(() => {
    const today = new Date();
    return invoices.value.filter(invoice => {
      const dueDate = new Date(invoice.dueDate);
      return invoice.status !== 'paid' && dueDate < today;
    });
  });
  
  // Actions
  const fetchInvoices = async (params = {}) => {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await api.get('/ap/invoices', { params });
      invoices.value = response.data.data;
      totalInvoices.value = response.data.meta?.total || invoices.value.length;
      return response.data;
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch invoices';
      throw err;
    } finally {
      loading.value = false;
    }
  };
  
  const fetchInvoiceById = async (id: string | number) => {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await api.get(`/ap/invoices/${id}`);
      selectedInvoice.value = response.data.data;
      return response.data;
    } catch (err: any) {
      error.value = err.message || `Failed to fetch invoice with ID ${id}`;
      throw err;
    } finally {
      loading.value = false;
    }
  };
  
  const createInvoice = async (invoiceData: Partial<Invoice>) => {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await api.post('/ap/invoices', invoiceData);
      invoices.value.push(response.data.data);
      return response.data;
    } catch (err: any) {
      error.value = err.message || 'Failed to create invoice';
      throw err;
    } finally {
      loading.value = false;
    }
  };
  
  const updateInvoice = async (id: string | number, invoiceData: Partial<Invoice>) => {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await api.put(`/ap/invoices/${id}`, invoiceData);
      const index = invoices.value.findIndex(i => i.id === id);
      if (index !== -1) {
        invoices.value[index] = { ...invoices.value[index], ...response.data.data };
      }
      if (selectedInvoice.value?.id === id) {
        selectedInvoice.value = { ...selectedInvoice.value, ...response.data.data };
      }
      return response.data;
    } catch (err: any) {
      error.value = err.message || `Failed to update invoice with ID ${id}`;
      throw err;
    } finally {
      loading.value = false;
    }
  };
  
  const deleteInvoice = async (id: string | number) => {
    loading.value = true;
    error.value = null;
    
    try {
      await api.delete(`/ap/invoices/${id}`);
      invoices.value = invoices.value.filter(i => i.id !== id);
      if (selectedInvoice.value?.id === id) {
        selectedInvoice.value = null;
      }
    } catch (err: any) {
      error.value = err.message || `Failed to delete invoice with ID ${id}`;
      throw err;
    } finally {
      loading.value = false;
    }
  };
  
  const approveInvoice = async (id: string | number) => {
    return updateInvoice(id, { status: 'approved' });
  };
  
  const rejectInvoice = async (id: string | number, reason: string) => {
    return updateInvoice(id, { status: 'rejected', rejectionReason: reason });
  };
  
  // Initialize the store
  const initialize = async () => {
    await fetchInvoices();
  };
  
  return {
    // State
    invoices,
    loading,
    error,
    selectedInvoice,
    totalInvoices,
    
    // Getters
    pendingInvoices,
    approvedInvoices,
    paidInvoices,
    overdueInvoices,
    
    // Actions
    fetchInvoices,
    fetchInvoiceById,
    createInvoice,
    updateInvoice,
    deleteInvoice,
    approveInvoice,
    rejectInvoice,
    initialize,
    
    // Reset function for Pinia
    $reset: () => {
      invoices.value = [];
      loading.value = false;
      error.value = null;
      selectedInvoice.value = null;
      totalInvoices.value = 0;
    },
  };
});
