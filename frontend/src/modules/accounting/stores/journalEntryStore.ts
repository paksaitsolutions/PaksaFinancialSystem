import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { JournalEntry, JournalEntryState, NewJournalEntry } from '../types/accounting';

export const useJournalEntryStore = defineStore('journalEntry', () => {
  const state = ref<JournalEntryState>({
    entries: [],
    loading: false,
    error: null
  });

  const fetchJournalEntries = async () => {
    state.value.loading = true;
    state.value.error = null;
    try {
      // TODO: Replace with actual API call
      // const response = await api.get('/api/accounting/journal-entries');
      // state.value.entries = response.data;
    } catch (error) {
      state.value.error = 'Failed to fetch journal entries';
      throw error;
    } finally {
      state.value.loading = false;
    }
  };

  const createJournalEntry = async (entry: NewJournalEntry): Promise<JournalEntry> => {
    try {
      // TODO: Replace with actual API call
      // const response = await api.post('/api/accounting/journal-entries', entry);
      // state.value.entries.push(response.data);
      // return response.data;
      return {
        ...entry,
        id: Date.now().toString(),
        total_amount: entry.lines.reduce((sum, line) => sum + line.debit, 0)
      };
    } catch (error) {
      state.value.error = 'Failed to create journal entry';
      throw error;
    }
  };

  const updateJournalEntry = async (id: string, updates: Partial<NewJournalEntry>): Promise<JournalEntry> => {
    try {
      // TODO: Replace with actual API call
      // const response = await api.put(`/api/accounting/journal-entries/${id}`, updates);
      // const index = state.value.entries.findIndex(e => e.id === id);
      // if (index !== -1) {
      //   state.value.entries[index] = response.data;
      // }
      // return response.data;
      const entry = state.value.entries.find(e => e.id === id);
      if (!entry) throw new Error('Journal entry not found');
      
      const updatedEntry = { ...entry, ...updates };
      return updatedEntry;
    } catch (error) {
      state.value.error = 'Failed to update journal entry';
      throw error;
    }
  };

  const deleteJournalEntry = async (id: string): Promise<void> => {
    try {
      // TODO: Replace with actual API call
      // await api.delete(`/api/accounting/journal-entries/${id}`);
      state.value.entries = state.value.entries.filter(entry => entry.id !== id);
    } catch (error) {
      state.value.error = 'Failed to delete journal entry';
      throw error;
    }
  };

  return {
    state,
    fetchJournalEntries,
    createJournalEntry,
    updateJournalEntry,
    deleteJournalEntry
  };
});
