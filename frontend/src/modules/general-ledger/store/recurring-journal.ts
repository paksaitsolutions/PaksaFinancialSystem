import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useI18n } from 'vue-i18n';
import type { 
  RecurringJournal, 
  RecurringJournalCreate, 
  RecurringJournalUpdate, 
  RecurringJournalListParams,
  RecurringJournalStatus,
  RecurringJournalRunParams,
  RecurringJournalRunResponse,
  RecurringJournalPreview,
  RecurringJournalOccurrence
} from '../types/recurringJournal';
import recurringJournalService from '../api/recurring-journal.service';

export const useRecurringJournalStore = defineStore('glRecurringJournal', () => {
  const toast = useToast();
  const { t } = useI18n();
  
  // State
  const loading = ref(false);
  const error = ref<string | null>(null);
  const recurringJournals = ref<RecurringJournal[]>([]);
  const currentJournal = ref<RecurringJournal | null>(null);
  const totalItems = ref(0);
  const loadingPreview = ref(false);
  const previewData = ref<RecurringJournalPreview | null>(null);
  const occurrences = ref<RecurringJournalOccurrence[]>([]);
  const totalOccurrences = ref(0);
  const runResults = ref<RecurringJournalRunResponse | null>(null);
  const running = ref(false);

  // Getters
  const isLoading = computed(() => loading.value);
  const hasError = computed(() => error.value !== null);
  const activeJournals = computed(() => 
    recurringJournals.value.filter(journal => journal.status === 'active')
  );
  const upcomingJournals = computed(() => {
    const now = new Date();
    return recurringJournals.value
      .filter(journal => 
        journal.status === 'active' && 
        new Date(journal.next_run_date || '') >= now
      )
      .sort((a, b) => 
        new Date(a.next_run_date || '').getTime() - 
        new Date(b.next_run_date || '').getTime()
      );
  });

  // Actions
  async function fetchRecurringJournals(params?: RecurringJournalListParams) {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await recurringJournalService.getRecurringJournals(params);
      recurringJournals.value = response.data;
      totalItems.value = response.pagination?.total || response.data.length;
      return response;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch recurring journals';
      toast.add({
        severity: 'error',
        summary: t('common.error'),
        detail: error.value,
        life: 5000
      });
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function fetchRecurringJournal(id: string) {
    loading.value = true;
    error.value = null;
    
    try {
      const journal = await recurringJournalService.getRecurringJournal(id);
      currentJournal.value = journal;
      return journal;
    } catch (err) {
      error.value = err instanceof Error ? err.message : `Failed to fetch recurring journal ${id}`;
      toast.add({
        severity: 'error',
        summary: t('common.error'),
        detail: error.value,
        life: 5000
      });
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function createRecurringJournal(data: RecurringJournalCreate) {
    loading.value = true;
    error.value = null;
    
    try {
      const journal = await recurringJournalService.createRecurringJournal(data);
      recurringJournals.value.unshift(journal);
      totalItems.value += 1;
      return journal;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to create recurring journal';
      toast.add({
        severity: 'error',
        summary: t('common.error'),
        detail: error.value,
        life: 5000
      });
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function updateRecurringJournal(id: string, data: RecurringJournalUpdate) {
    loading.value = true;
    error.value = null;
    
    try {
      const journal = await recurringJournalService.updateRecurringJournal(id, data);
      
      // Update in the list
      const index = recurringJournals.value.findIndex(j => j.id === id);
      if (index !== -1) {
        recurringJournals.value[index] = { ...recurringJournals.value[index], ...journal };
      }
      
      // Update current journal if it's the one being edited
      if (currentJournal.value?.id === id) {
        currentJournal.value = { ...currentJournal.value, ...journal };
      }
      
      return journal;
    } catch (err) {
      error.value = err instanceof Error ? err.message : `Failed to update recurring journal ${id}`;
      toast.add({
        severity: 'error',
        summary: t('common.error'),
        detail: error.value,
        life: 5000
      });
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function deleteRecurringJournal(id: string) {
    loading.value = true;
    error.value = null;
    
    try {
      await recurringJournalService.deleteRecurringJournal(id);
      
      // Remove from the list
      const index = recurringJournals.value.findIndex(j => j.id === id);
      if (index !== -1) {
        recurringJournals.value.splice(index, 1);
        totalItems.value -= 1;
      }
      
      // Clear current journal if it's the one being deleted
      if (currentJournal.value?.id === id) {
        currentJournal.value = null;
      }
      
      return true;
    } catch (err) {
      error.value = err instanceof Error ? err.message : `Failed to delete recurring journal ${id}`;
      toast.add({
        severity: 'error',
        summary: t('common.error'),
        detail: error.value,
        life: 5000
      });
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function updateStatus(id: string, status: RecurringJournalStatus) {
    try {
      const journal = await recurringJournalService.updateRecurringJournalStatus(id, status);
      
      // Update in the list
      const index = recurringJournals.value.findIndex(j => j.id === id);
      if (index !== -1) {
        recurringJournals.value[index] = { ...recurringJournals.value[index], status };
      }
      
      // Update current journal if it's the one being updated
      if (currentJournal.value?.id === id) {
        currentJournal.value = { ...currentJournal.value, status };
      }
      
      return journal;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : `Failed to update status for journal ${id}`;
      toast.add({
        severity: 'error',
        summary: t('common.error'),
        detail: errorMessage,
        life: 5000
      });
      throw err;
    }
  }

  async function previewRun(id: string, params?: { limit?: number; start_date?: string }) {
    loadingPreview.value = true;
    try {
      previewData.value = await recurringJournalService.previewRecurringJournal(id, params);
      return previewData.value;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : `Failed to preview run for journal ${id}`;
      toast.add({
        severity: 'error',
        summary: t('common.error'),
        detail: errorMessage,
        life: 5000
      });
      throw err;
    } finally {
      loadingPreview.value = false;
    }
  }

  async function runNow(id: string, params: RecurringJournalRunParams = {}) {
    running.value = true;
    try {
      const results = await recurringJournalService.runRecurringJournal(id, params);
      runResults.value = results;
      
      // Refresh the journal to get updated next_run_date
      if (currentJournal.value?.id === id) {
        await fetchRecurringJournal(id);
      }
      
      return results;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : `Failed to run journal ${id}`;
      toast.add({
        severity: 'error',
        summary: t('common.error'),
        detail: errorMessage,
        life: 5000
      });
      throw err;
    } finally {
      running.value = false;
    }
  }

  async function fetchOccurrences(id: string, params?: { page?: number; per_page?: number }) {
    loading.value = true;
    try {
      const response = await recurringJournalService.getRecurringJournalOccurrences(id, params);
      occurrences.value = response.data;
      totalOccurrences.value = response.meta?.total || response.data.length;
      return response;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : `Failed to fetch occurrences for journal ${id}`;
      toast.add({
        severity: 'error',
        summary: t('common.error'),
        detail: errorMessage,
        life: 5000
      });
      throw err;
    } finally {
      loading.value = false;
    }
  }

  function $reset() {
    loading.value = false;
    error.value = null;
    recurringJournals.value = [];
    currentJournal.value = null;
    totalItems.value = 0;
    loadingPreview.value = false;
    previewData.value = null;
    occurrences.value = [];
    totalOccurrences.value = 0;
    runResults.value = null;
    running.value = false;
  }

  return {
    // State
    loading,
    error,
    recurringJournals,
    currentJournal,
    totalItems,
    loadingPreview,
    previewData,
    occurrences,
    totalOccurrences,
    runResults,
    running,
    
    // Getters
    isLoading,
    hasError,
    activeJournals,
    upcomingJournals,
    
    // Actions
    fetchRecurringJournals,
    fetchRecurringJournal,
    createRecurringJournal,
    updateRecurringJournal,
    deleteRecurringJournal,
    updateStatus,
    previewRun,
    runNow,
    fetchOccurrences,
    $reset
  };
});

// Export the store type for use in components
export type RecurringJournalStore = ReturnType<typeof useRecurringJournalStore>;
