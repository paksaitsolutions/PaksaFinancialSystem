import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useApi } from '@/composables/useApi'

export const usePeriodClosingStore = defineStore('period-closing', () => {
  const api = useApi()
  const loading = ref(false)
  const error = ref(null)

  const runPreClosingValidation = async () => {
    loading.value = true
    try {
      const response = await api.post('/general-ledger/period-closing/validate')
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const getTrialBalance = async () => {
    try {
      const response = await api.get('/general-ledger/trial-balance')
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  const getAdjustingEntries = async () => {
    try {
      const response = await api.get('/general-ledger/adjusting-entries')
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  const saveAdjustingEntry = async (entry) => {
    try {
      const response = await api.post('/general-ledger/adjusting-entries', entry)
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  const deleteAdjustingEntry = async (entryId) => {
    try {
      await api.delete(`/general-ledger/adjusting-entries/${entryId}`)
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  const closePeriod = async (closingData) => {
    loading.value = true
    try {
      const response = await api.post('/general-ledger/period-closing/close', closingData)
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    error,
    runPreClosingValidation,
    getTrialBalance,
    getAdjustingEntries,
    saveAdjustingEntry,
    deleteAdjustingEntry,
    closePeriod
  }
})