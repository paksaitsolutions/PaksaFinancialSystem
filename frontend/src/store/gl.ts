import { defineStore } from 'pinia';
import { ref } from 'vue';
import axios from 'axios';
import { useToast } from 'vue-toastification';
import type { RecurringJournal } from '@/components/gl/recurring/RecurringJournalForm.vue';

export const useGlStore = defineStore('gl', () => {
  const toast = useToast();
  const loading = ref(false);
  const error = ref<string | null>(null);
  const recurringJournals = ref<RecurringJournal[]>([]);

  // Fetch all recurring journals
  async function fetchRecurringJournals() {
    loading.value = true;
    error.value = null;
    try {
      const response = await axios.get('/api/gl/recurring-journals');
      recurringJournals.value = response.data;
      return response.data;
    } catch (err) {
      error.value = 'Failed to fetch recurring journals';
      toast.error(error.value);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  // Fetch a single recurring journal by ID
  async function fetchRecurringJournalById(id: string) {
    loading.value = true;
    error.value = null;
    try {
      const response = await axios.get(`/api/gl/recurring-journals/${id}`);
      return response.data;
    } catch (err) {
      error.value = 'Failed to fetch recurring journal';
      toast.error(error.value);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  // Create a new recurring journal
  async function createRecurringJournal(journal: Omit<RecurringJournal, 'id'>) {
    loading.value = true;
    error.value = null;
    try {
      const response = await axios.post('/api/gl/recurring-journals', journal);
      toast.success('Recurring journal created successfully');
      return response.data;
    } catch (err) {
      error.value = 'Failed to create recurring journal';
      toast.error(error.value);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  // Update an existing recurring journal
  async function updateRecurringJournal({ id, data }: { id: string; data: Partial<RecurringJournal> }) {
    loading.value = true;
    error.value = null;
    try {
      const response = await axios.put(`/api/gl/recurring-journals/${id}`, data);
      toast.success('Recurring journal updated successfully');
      return response.data;
    } catch (err) {
      error.value = 'Failed to update recurring journal';
      toast.error(error.value);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  // Delete a recurring journal
  async function deleteRecurringJournal(id: string) {
    loading.value = true;
    error.value = null;
    try {
      await axios.delete(`/api/gl/recurring-journals/${id}`);
      toast.success('Recurring journal deleted successfully');
      return true;
    } catch (err) {
      error.value = 'Failed to delete recurring journal';
      toast.error(error.value);
      throw err;
    } finally {
      loading.value = false;
    }
  }

  return {
    loading,
    error,
    recurringJournals,
    fetchRecurringJournals,
    fetchRecurringJournalById,
    createRecurringJournal,
    updateRecurringJournal,
    deleteRecurringJournal,
  };
});
