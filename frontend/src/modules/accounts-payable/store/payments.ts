import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useApi } from '@/composables/useApi';
import type { Payment } from '../types';

export const usePaymentsStore = defineStore('ap/payments', () => {
  const api = useApi();
  
  // State
  const payments = ref<Payment[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const selectedPayment = ref<Payment | null>(null);
  const totalPayments = ref(0);
  
  // Getters
  const pendingPayments = computed(() => 
    payments.value.filter(payment => payment.status === 'pending')
  );
  
  const processedPayments = computed(() => 
    payments.value.filter(payment => payment.status === 'processed')
  );
  
  const failedPayments = computed(() => 
    payments.value.filter(payment => payment.status === 'failed')
  );
  
  const upcomingPayments = computed(() => {
    const today = new Date();
    const nextWeek = new Date();
    nextWeek.setDate(today.getDate() + 7);
    
    return payments.value.filter(payment => {
      const paymentDate = new Date(payment.paymentDate);
      return payment.status === 'scheduled' && 
             paymentDate >= today && 
             paymentDate <= nextWeek;
    });
  });
  
  // Actions
  const fetchPayments = async (params = {}) => {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await api.get('/ap/payments', { params });
      payments.value = response.data.data;
      totalPayments.value = response.data.meta?.total || payments.value.length;
      return response.data;
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch payments';
      throw err;
    } finally {
      loading.value = false;
    }
  };
  
  const fetchPaymentById = async (id: string | number) => {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await api.get(`/ap/payments/${id}`);
      selectedPayment.value = response.data.data;
      return response.data;
    } catch (err: any) {
      error.value = err.message || `Failed to fetch payment with ID ${id}`;
      throw err;
    } finally {
      loading.value = false;
    }
  };
  
  const createPayment = async (paymentData: Partial<Payment>) => {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await api.post('/ap/payments', paymentData);
      payments.value.push(response.data.data);
      return response.data;
    } catch (err: any) {
      error.value = err.message || 'Failed to create payment';
      throw err;
    } finally {
      loading.value = false;
    }
  };
  
  const updatePayment = async (id: string | number, paymentData: Partial<Payment>) => {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await api.put(`/ap/payments/${id}`, paymentData);
      const index = payments.value.findIndex(p => p.id === id);
      if (index !== -1) {
        payments.value[index] = { ...payments.value[index], ...response.data.data };
      }
      if (selectedPayment.value?.id === id) {
        selectedPayment.value = { ...selectedPayment.value, ...response.data.data };
      }
      return response.data;
    } catch (err: any) {
      error.value = err.message || `Failed to update payment with ID ${id}`;
      throw err;
    } finally {
      loading.value = false;
    }
  };
  
  const deletePayment = async (id: string | number) => {
    loading.value = true;
    error.value = null;
    
    try {
      await api.delete(`/ap/payments/${id}`);
      payments.value = payments.value.filter(p => p.id !== id);
      if (selectedPayment.value?.id === id) {
        selectedPayment.value = null;
      }
    } catch (err: any) {
      error.value = err.message || `Failed to delete payment with ID ${id}`;
      throw err;
    } finally {
      loading.value = false;
    }
  };
  
  const processPayment = async (id: string | number) => {
    return updatePayment(id, { status: 'processed' });
  };
  
  const schedulePayment = async (id: string | number, paymentDate: string) => {
    return updatePayment(id, { status: 'scheduled', paymentDate });
  };
  
  // Initialize the store
  const initialize = async () => {
    await fetchPayments();
  };
  
  return {
    // State
    payments,
    loading,
    error,
    selectedPayment,
    totalPayments,
    
    // Getters
    pendingPayments,
    processedPayments,
    failedPayments,
    upcomingPayments,
    
    // Actions
    fetchPayments,
    fetchPaymentById,
    createPayment,
    updatePayment,
    deletePayment,
    processPayment,
    schedulePayment,
    initialize,
    
    // Reset function for Pinia
    $reset: () => {
      payments.value = [];
      loading.value = false;
      error.value = null;
      selectedPayment.value = null;
      totalPayments.value = 0;
    },
  };
});
