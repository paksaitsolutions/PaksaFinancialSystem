import { defineStore } from 'pinia';
import { ref } from 'vue';
import { useToast } from 'primevue/usetoast';
import BankAccountService from '../api/BankAccountService';

interface Reconciliation {
  id?: string;
  bankAccountId: string;
  statementDate: string;
  endingBalance: number;
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled';
  notes?: string;
  reconciledBy?: string;
  reconciledAt?: string;
  createdAt?: string;
  updatedAt?: string;
  transactions?: any[]; // Array of reconciled transaction IDs or details
}

export const useReconciliationStore = defineStore('reconciliation', () => {
  const toast = useToast();
  const reconciliations = ref<Reconciliation[]>([]);
  const currentReconciliation = ref<Reconciliation | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);
  
  // Reconciliation statuses
  const reconciliationStatuses = ref([
    { name: 'Pending', value: 'pending' },
    { name: 'In Progress', value: 'in_progress' },
    { name: 'Completed', value: 'completed' },
    { name: 'Cancelled', value: 'cancelled' },
  ]);

  // Fetch all reconciliations for a bank account
  const fetchReconciliations = async (bankAccountId: string) => {
    try {
      loading.value = true;
      error.value = null;
      const response = await BankAccountService.getReconciliations(bankAccountId);
      reconciliations.value = response.data;
      return reconciliations.value;
    } catch (err) {
      console.error('Error fetching reconciliations:', err);
      error.value = 'Failed to load reconciliations. Please try again later.';
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to load reconciliations',
        life: 5000,
      });
      throw err;
    } finally {
      loading.value = false;
    }
  };

  // Start a new reconciliation
  const startReconciliation = async (bankAccountId: string, statementDate: string, endingBalance: number) => {
    try {
      loading.value = true;
      error.value = null;
      const response = await BankAccountService.startReconciliation({
        bankAccountId,
        statementDate,
        endingBalance,
        status: 'in_progress',
      });
      currentReconciliation.value = response.data;
      reconciliations.value.push(response.data);
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Reconciliation started successfully',
        life: 3000,
      });
      return response.data;
    } catch (err) {
      console.error('Error starting reconciliation:', err);
      error.value = 'Failed to start reconciliation. Please try again.';
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to start reconciliation',
        life: 5000,
      });
      throw err;
    } finally {
      loading.value = false;
    }
  };

  // Update a reconciliation
  const updateReconciliation = async (id: string, reconciliationData: Partial<Reconciliation>) => {
    try {
      loading.value = true;
      error.value = null;
      const response = await BankAccountService.updateReconciliation(id, reconciliationData);
      
      // Update in the reconciliations array
      const index = reconciliations.value.findIndex(r => r.id === id);
      if (index !== -1) {
        reconciliations.value[index] = { ...reconciliations.value[index], ...response.data };
      }
      
      // Update current reconciliation if it's the one being updated
      if (currentReconciliation.value?.id === id) {
        currentReconciliation.value = { ...currentReconciliation.value, ...response.data };
      }
      
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Reconciliation updated successfully',
        life: 3000,
      });
      return response.data;
    } catch (err) {
      console.error('Error updating reconciliation:', err);
      error.value = 'Failed to update reconciliation. Please try again.';
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to update reconciliation',
        life: 5000,
      });
      throw err;
    } finally {
      loading.value = false;
    }
  };

  // Complete a reconciliation
  const completeReconciliation = async (id: string, notes?: string) => {
    try {
      return await updateReconciliation(id, { 
        status: 'completed',
        notes,
        reconciledAt: new Date().toISOString(),
        // In a real app, you would also update the reconciled transactions here
      });
    } catch (err) {
      console.error('Error completing reconciliation:', err);
      throw err;
    }
  };

  // Cancel a reconciliation
  const cancelReconciliation = async (id: string, notes?: string) => {
    try {
      return await updateReconciliation(id, { 
        status: 'cancelled',
        notes: notes || 'Reconciliation was cancelled',
      });
    } catch (err) {
      console.error('Error cancelling reconciliation:', err);
      throw err;
    }
  };

  // Get a single reconciliation by ID
  const getReconciliationById = async (id: string) => {
    try {
      // First check if we have it in the store
      const existing = reconciliations.value.find(r => r.id === id);
      if (existing) {
        currentReconciliation.value = existing;
        return existing;
      }
      
      // If not, fetch it from the API
      loading.value = true;
      error.value = null;
      const response = await BankAccountService.getReconciliation(id);
      currentReconciliation.value = response.data;
      return response.data;
    } catch (err) {
      console.error('Error fetching reconciliation:', err);
      error.value = 'Failed to load reconciliation. Please try again later.';
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to load reconciliation',
        life: 5000,
      });
      throw err;
    } finally {
      loading.value = false;
    }
  };

  // Get all reconciliation statuses for dropdown
  const getReconciliationStatuses = () => {
    return reconciliationStatuses.value;
  };

  return {
    reconciliations,
    currentReconciliation,
    loading,
    error,
    fetchReconciliations,
    startReconciliation,
    updateReconciliation,
    completeReconciliation,
    cancelReconciliation,
    getReconciliationById,
    getReconciliationStatuses,
  };
});
