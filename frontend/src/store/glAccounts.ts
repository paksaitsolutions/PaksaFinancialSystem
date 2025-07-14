import { defineStore } from 'pinia'
import { ref } from 'vue'
import { apiClient } from '@/utils/apiClient'

export const useGLStore = defineStore('glAccounts', () => {
  const accounts = ref([])
  const journalEntries = ref([])
  const loading = ref(false)

  const fetchAccounts = async () => {
    loading.value = true
    try {
      const response = await apiClient.get('/api/v1/gl/accounts/')
      accounts.value = response.data
    } catch (error) {
      console.error('Error fetching accounts:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const createAccount = async (accountData: any) => {
    try {
      const response = await apiClient.post('/api/v1/gl/accounts/', accountData)
      accounts.value.push(response.data)
      return response.data
    } catch (error) {
      console.error('Error creating account:', error)
      throw error
    }
  }

  const updateAccount = async (id: number, accountData: any) => {
    try {
      const response = await apiClient.put(`/api/v1/gl/accounts/${id}`, accountData)
      const index = accounts.value.findIndex(acc => acc.id === id)
      if (index !== -1) {
        accounts.value[index] = response.data
      }
      return response.data
    } catch (error) {
      console.error('Error updating account:', error)
      throw error
    }
  }

  const deleteAccount = async (id: number) => {
    try {
      await apiClient.delete(`/api/v1/gl/accounts/${id}`)
      accounts.value = accounts.value.filter(acc => acc.id !== id)
    } catch (error) {
      console.error('Error deleting account:', error)
      throw error
    }
  }

  const fetchJournalEntries = async () => {
    loading.value = true
    try {
      const response = await apiClient.get('/api/v1/gl/journal-entries/')
      journalEntries.value = response.data
    } catch (error) {
      console.error('Error fetching journal entries:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const createJournalEntry = async (entryData: any) => {
    try {
      const response = await apiClient.post('/api/v1/gl/journal-entries/', entryData)
      journalEntries.value.push(response.data)
      return response.data
    } catch (error) {
      console.error('Error creating journal entry:', error)
      throw error
    }
  }

  return {
    accounts,
    journalEntries,
    loading,
    fetchAccounts,
    createAccount,
    updateAccount,
    deleteAccount,
    fetchJournalEntries,
    createJournalEntry
  }
})