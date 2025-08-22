import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import axios from 'axios';
import { useToast } from 'primevue/usetoast';
import type { AxiosError } from 'axios';
import { useI18n } from 'vue-i18n';

export interface RecurringJournalEntry {
  id: string;
  accountNumber: string;
  description: string;
  debit: number;
  credit: number;
  costCenter?: string;
  projectCode?: string;
}

export interface RecurringJournal {
  id: string;
  name: string;
  description: string;
  frequency: 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'yearly';
  startDate: string;
  endDate?: string;
  entries: RecurringJournalEntry[];
  isActive: boolean;
  lastRunDate?: string;
  nextRunDate: string;
  createdBy: string;
  createdAt: string;
  updatedAt: string;
}

export const useRecurringJournalStore = defineStore('glRecurringJournal', () => {
  const toast = useToast();
  const { t } = useI18n();
  
  // State
  const loading = ref(false);
  const error = ref<string | null>(null);
  const recurringJournals = ref<RecurringJournal[]>([]);
  const currentJournal = ref<RecurringJournal | null>(null);

  // Getters
  const isLoading = computed(() => loading.value);
  const hasError = computed(() => error.value !== null);
  const activeJournals = computed(() => 
    recurringJournals.value.filter(journal => journal.isActive)
  );

  // Actions
  async function fetchRecurringJournals() {
    try {
      loading.value = true;
      error.value = null;
      const response = await axios.get('/api/gl/recurring-journals');
      recurringJournals.value = response.data;
      return response.data;
    } catch (err) {
      return handleApiError('Failed to fetch recurring journals', err);
    } finally {
      loading.value = false;
    }
  }

  async function fetchRecurringJournalById(id: string) {
    try {
      loading.value = true;
      error.value = null;
      const response = await axios.get(`/api/gl/recurring-journals/${id}`);
      currentJournal.value = response.data;
      return response.data;
    } catch (err) {
      return handleApiError('Failed to fetch recurring journal', err);
    } finally {
      loading.value = false;
    }
  }

  async function createRecurringJournal(
    journalData: Omit<RecurringJournal, 'id' | 'createdAt' | 'updatedAt' | 'lastRunDate'>
  ) {
    try {
      loading.value = true;
      error.value = null;
      const response = await axios.post('/api/gl/recurring-journals', journalData);
      await fetchRecurringJournals(); // Refresh the list
      toast.add({
        severity: 'success',
        summary: t('common.success'),
        detail: t('gl.recurringJournal.created'),
        life: 3000
      });
      return response.data;
    } catch (err) {
      return handleApiError('Failed to create recurring journal', err);
    } finally {
      loading.value = false;
    }
  }

  async function updateRecurringJournal(
    { id, data }: { id: string; data: Partial<RecurringJournal> }
  ) {
    try {
      loading.value = true;
      error.value = null;
      const response = await axios.patch(`/api/gl/recurring-journals/${id}`, data);
      await fetchRecurringJournals(); // Refresh the list
      toast.add({
        severity: 'success',
        summary: t('common.success'),
        detail: t('gl.recurringJournal.updated'),
        life: 3000
      });
      return response.data;
    } catch (err) {
      return handleApiError('Failed to update recurring journal', err);
    } finally {
      loading.value = false;
    }
  }

  async function deleteRecurringJournal(id: string) {
    try {
      loading.value = true;
      error.value = null;
      await axios.delete(`/api/gl/recurring-journals/${id}`);
      await fetchRecurringJournals(); // Refresh the list
      toast.add({
        severity: 'success',
        summary: t('common.success'),
        detail: t('gl.recurringJournal.deleted'),
        life: 3000
      });
      return true;
    } catch (err) {
      return handleApiError('Failed to delete recurring journal', err);
    } finally {
      loading.value = false;
    }
  }

  async function toggleJournalStatus(id: string, isActive: boolean) {
    try {
      return await updateRecurringJournal({
        id,
        data: { isActive }
      });
    } catch (err) {
      return handleApiError('Failed to update journal status', err);
    }
  }

  // Helper function to handle API errors
  function handleApiError(defaultMessage: string, error: unknown) {
    const axiosError = error as AxiosError;
    let message = defaultMessage;
    
    if (axiosError.response?.data?.message) {
      message = axiosError.response.data.message;
    } else if (axiosError.message) {
      message = axiosError.message;
    }
    
    error.value = message;
    toast.add({
      severity: 'error',
      summary: t('common.error'),
      detail: message,
      life: 5000
    });
    
    throw error;
  }

  // Initialize the store
  function $reset() {
    loading.value = false;
    error.value = null;
    recurringJournals.value = [];
    currentJournal.value = null;
  }

  return {
    // State
    loading,
    error,
    recurringJournals,
    currentJournal,
    
    // Getters
    isLoading,
    hasError,
    activeJournals,
    
    // Actions
    fetchRecurringJournals,
    fetchRecurringJournalById,
    createRecurringJournal,
    updateRecurringJournal,
    deleteRecurringJournal,
    toggleJournalStatus,
    $reset
  };
});

// Export the store type for use in components
export type RecurringJournalStore = ReturnType<typeof useRecurringJournalStore>;
