import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { JournalEntry, JournalEntryLine } from '@/types/accounting';
import { useToast } from 'primevue/usetoast';

// Mock data for development
const mockJournalEntries: JournalEntry[] = [
  {
    id: '1',
    reference: 'JE-2023-001',
    date: '2023-01-15',
    memo: 'Initial capital investment',
    status: 'posted',
    total_amount: 100000,
    lines: [
      {
        id: '1-1',
        account_id: '3001',
        account_name: 'Owner\'s Equity',
        debit: 0,
        credit: 100000,
        memo: 'Initial investment'
      },
      {
        id: '1-2',
        account_id: '1001',
        account_name: 'Cash',
        debit: 100000,
        credit: 0,
        memo: 'Initial investment'
      }
    ],
    created_at: '2023-01-15T10:00:00Z',
    updated_at: '2023-01-15T10:00:00Z'
  }
];

export const useJournalEntryStore = defineStore('journalEntry', () => {
  const toast = useToast();
  const journalEntries = ref<JournalEntry[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const isDraft = (entry: JournalEntry) => entry.status === 'draft';
  const isPosted = (entry: JournalEntry) => entry.status === 'posted';
  const isVoid = (entry: JournalEntry) => entry.status === 'void';

  // Computed properties
  const draftEntries = computed(() => journalEntries.value.filter(isDraft));
  const postedEntries = computed(() => journalEntries.value.filter(isPosted));
  const voidEntries = computed(() => journalEntries.value.filter(isVoid));
  const totalEntries = computed(() => journalEntries.value.length);

  // Fetch all journal entries
  const fetchJournalEntries = async (params: {
    startDate?: string;
    endDate?: string;
    status?: 'draft' | 'posted' | 'void';
  } = {}) => {
    loading.value = true;
    error.value = null;
    try {
      // TODO: Replace with actual API call
      // const { data } = await api.get('/api/accounting/journal-entries', { params });
      // journalEntries.value = data;
      
      // Using mock data for development
      journalEntries.value = mockJournalEntries;
      return journalEntries.value;
    } catch (err) {
      const message = 'Failed to fetch journal entries';
      error.value = message;
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: message,
        life: 3000
      });
      throw new Error(message);
    } finally {
      loading.value = false;
    }
  };

  // Create a new journal entry
  const createJournalEntry = async (entryData: Omit<JournalEntry, 'id'>) => {
    loading.value = true;
    error.value = null;
    
    // Validate entry data
    if (!entryData.reference) {
      throw new Error('Reference is required');
    }
    
    if (!entryData.date) {
      throw new Error('Date is required');
    }
    
    // Validate journal entry lines
    if (!entryData.lines || entryData.lines.length < 2) {
      throw new Error('At least two journal entry lines are required');
    }
    
    // Calculate total debits and credits
    const totalDebits = entryData.lines.reduce((sum, line) => sum + (line.debit || 0), 0);
    const totalCredits = entryData.lines.reduce((sum, line) => sum + (line.credit || 0), 0);
    
    if (Math.abs(totalDebits - totalCredits) > 0.01) { // Allow for floating point precision
      throw new Error('Total debits must equal total credits');
    }
    
    try {
      // TODO: Replace with actual API call
      // const response = await api.post('/api/accounting/journal-entries', {
      //   ...entryData,
      //   total_amount: totalDebits,
      //   status: 'draft' // Default status for new entries
      // });
      
      const newEntry: JournalEntry = {
        ...entryData,
        id: Date.now().toString(),
        total_amount: totalDebits,
        status: 'draft',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };
      
      journalEntries.value.push(newEntry);
      
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Journal entry created successfully',
        life: 3000
      });
      
      return newEntry;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to create journal entry';
      error.value = message;
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: message,
        life: 5000
      });
      throw err;
    } finally {
      loading.value = false;
    }
  };

  // Update an existing journal entry
  const updateJournalEntry = async (entryData: JournalEntry) => {
    if (!entryData.id) throw new Error('Journal entry ID is required');
    
    // Don't allow updating posted or void entries
      const existingEntry = journalEntries.value.find(e => e.id === entryData.id);
      if (existingEntry?.status !== 'draft') {
        throw new Error('Only draft entries can be updated');
      }
    
    // Validate entry data
    if (!entryData.reference) {
      throw new Error('Reference is required');
    }
    
    if (!entryData.date) {
      throw new Error('Date is required');
    }
    
    // Validate journal entry lines
    if (!entryData.lines || entryData.lines.length < 2) {
      throw new Error('At least two journal entry lines are required');
    }
    
    // Calculate total debits and credits
    const totalDebits = entryData.lines.reduce((sum, line) => sum + (line.debit || 0), 0);
    const totalCredits = entryData.lines.reduce((sum, line) => sum + (line.credit || 0), 0);
    
    if (Math.abs(totalDebits - totalCredits) > 0.01) { // Allow for floating point precision
      throw new Error('Total debits must equal total credits');
    }
    
    loading.value = true;
    error.value = null;
    
    try {
      // TODO: Replace with actual API call
      // const response = await api.put(`/api/accounting/journal-entries/${entryData.id}`, {
      //   ...entryData,
      //   total_amount: totalDebits,
      //   updated_at: new Date().toISOString()
      // });
      
      const updatedEntry: JournalEntry = {
        ...entryData,
        total_amount: totalDebits,
        updated_at: new Date().toISOString()
      };
      
      const index = journalEntries.value.findIndex(e => e.id === entryData.id);
      if (index !== -1) {
        journalEntries.value[index] = updatedEntry;
        
        toast.add({
          severity: 'success',
          summary: 'Success',
          detail: 'Journal entry updated successfully',
          life: 3000
        });
        
        return updatedEntry;
      }
      
      throw new Error('Journal entry not found');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to update journal entry';
      error.value = message;
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: message,
        life: 5000
      });
      throw err;
    } finally {
      loading.value = false;
    }
  };

  // Delete a journal entry
  const deleteJournalEntry = async (id: string) => {
    if (!id) throw new Error('Journal entry ID is required');
    
    // Don't allow deleting posted or void entries
    const entry = journalEntries.value.find(e => e.id === id);
    if (!entry) {
      throw new Error('Journal entry not found');
    }
    
    if (entry.status !== 'draft') {
      throw new Error('Only draft entries can be deleted');
    }
    
    loading.value = true;
    error.value = null;
    
    try {
      // TODO: Replace with actual API call
      // await api.delete(`/api/accounting/journal-entries/${id}`);
      
      journalEntries.value = journalEntries.value.filter(e => e.id !== id);
      
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Journal entry deleted successfully',
        life: 3000
      });
      
      return true;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to delete journal entry';
      error.value = message;
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: message,
        life: 5000
      });
      throw err;
    } finally {
      loading.value = false;
    }
  };
  
  // Post a draft journal entry
  const postJournalEntry = async (id: string) => {
    const entry = journalEntries.value.find(e => e.id === id);
    if (!entry) {
      throw new Error('Journal entry not found');
    }
    
    if (entry.status !== 'draft') {
      throw new Error('Only draft entries can be posted');
    }
    
    loading.value = true;
    error.value = null;
    
    try {
      // TODO: Replace with actual API call
      // const response = await api.post(`/api/accounting/journal-entries/${id}/post`);
      // const index = journalEntries.value.findIndex(e => e.id === id);
      // if (index !== -1) {
      //   journalEntries.value[index] = { ...entry, status: 'posted' };
      // }
      // return response.data;
      
      const index = journalEntries.value.findIndex(e => e.id === id);
      if (index !== -1) {
        journalEntries.value[index] = { 
          ...entry, 
          status: 'posted',
          updated_at: new Date().toISOString()
        };
        
        toast.add({
          severity: 'success',
          summary: 'Success',
          detail: 'Journal entry posted successfully',
          life: 3000
        });
        
        return journalEntries.value[index];
      }
      
      throw new Error('Journal entry not found');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to post journal entry';
      error.value = message;
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: message,
        life: 5000
      });
      throw err;
    } finally {
      loading.value = false;
    }
  };
  
  // Void a posted journal entry
  const voidJournalEntry = async (id: string, reason: string) => {
    const entry = journalEntries.value.find(e => e.id === id);
    if (!entry) {
      throw new Error('Journal entry not found');
    }
    
    if (entry.status !== 'posted') {
      throw new Error('Only posted entries can be voided');
    }
    
    if (!reason) {
      throw new Error('Reason is required to void a journal entry');
    }
    
    loading.value = true;
    error.value = null;
    
    try {
      // TODO: Replace with actual API call
      // const response = await api.post(`/api/accounting/journal-entries/${id}/void`, { reason });
      // const index = journalEntries.value.findIndex(e => e.id === id);
      // if (index !== -1) {
      //   journalEntries.value[index] = { 
      //     ...entry, 
      //     status: 'void',
      //     memo: `${entry.memo || ''}\nVOIDED: ${reason}`.trim()
      //   };
      // }
      // return response.data;
      
      const index = journalEntries.value.findIndex(e => e.id === id);
      if (index !== -1) {
        journalEntries.value[index] = { 
          ...entry, 
          status: 'void',
          memo: `${entry.memo || ''}\nVOIDED: ${reason}`.trim(),
          updated_at: new Date().toISOString()
        };
        
        toast.add({
          severity: 'success',
          summary: 'Success',
          detail: 'Journal entry voided successfully',
          life: 3000
        });
        
        return journalEntries.value[index];
      }
      
      throw new Error('Journal entry not found');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to void journal entry';
      error.value = message;
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: message,
        life: 5000
      });
      throw err;
    } finally {
      loading.value = false;
    }
  };

  // Get a single journal entry by ID
  const getJournalEntryById = (id: string): JournalEntry | null => {
    if (!id) return null;
    
    const entry = journalEntries.value.find(entry => entry.id === id);
    if (!entry) return null;
    
    // Ensure lines is always an array and has required fields
    const formattedEntry: JournalEntry = {
      ...entry,
      lines: (Array.isArray(entry.lines) ? entry.lines : []).map(line => ({
        id: line.id || `line-${Math.random().toString(36).substr(2, 9)}`,
        account_id: line.account_id || null,
        account_name: line.account_name || '',
        debit: line.debit || 0,
        credit: line.credit || 0,
        memo: line.memo || ''
      }))
    };
    
    return formattedEntry;
  };
  
  // Get entries by account ID
  const getEntriesByAccountId = (accountId: string): JournalEntry[] => {
    if (!accountId) return [];
    
    return journalEntries.value.filter(entry => 
      entry.lines.some(line => line.account_id === accountId)
    );
  };
  
  // Get entries by date range
  const getEntriesByDateRange = (startDate: string, endDate: string): JournalEntry[] => {
    if (!startDate || !endDate) return [];
    
    const start = new Date(startDate);
    const end = new Date(endDate);
    
    return journalEntries.value.filter(entry => {
      const entryDate = new Date(entry.date);
      return entryDate >= start && entryDate <= end;
    });
  };
  
  // Calculate account balance
  const getAccountBalance = (accountId: string, asOfDate?: string): number => {
    if (!accountId) return 0;
    
    const relevantEntries = asOfDate 
      ? journalEntries.value.filter(entry => new Date(entry.date) <= new Date(asOfDate))
      : journalEntries.value;
    
    return relevantEntries.reduce((balance, entry) => {
      const accountLines = entry.lines.filter(line => line.account_id === accountId);
      return accountLines.reduce((sum, line) => sum + (line.debit - line.credit), balance);
    }, 0);
  };

  return {
    // State
    journalEntries,
    loading,
    error,
    
    // Computed
    draftEntries,
    postedEntries,
    voidEntries,
    totalEntries,
    
    // Actions
    fetchJournalEntries,
    createJournalEntry,
    updateJournalEntry,
    deleteJournalEntry,
    getJournalEntryById,
    postJournalEntry,
    voidJournalEntry,
    getEntriesByAccountId,
    getEntriesByDateRange,
    getAccountBalance
  };
});
