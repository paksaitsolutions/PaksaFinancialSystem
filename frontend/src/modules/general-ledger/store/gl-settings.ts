import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useApi } from '@/composables/useApi'

export const useGLSettingsStore = defineStore('gl-settings', () => {
  const api = useApi()
  const loading = ref(false)
  const error = ref(null)

  const getSettings = async () => {
    loading.value = true
    try {
      const response = await api.get('/general-ledger/settings')
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateSettings = async (settings) => {
    loading.value = true
    try {
      const response = await api.put('/general-ledger/settings', settings)
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const getAccountingPeriods = async () => {
    try {
      const response = await api.get('/general-ledger/periods')
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  const openPeriod = async (periodId) => {
    try {
      const response = await api.post(`/general-ledger/periods/${periodId}/open`)
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  const closePeriod = async (periodId) => {
    try {
      const response = await api.post(`/general-ledger/periods/${periodId}/close`)
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  const updatePeriodClosingSettings = async (settings) => {
    try {
      const response = await api.put('/general-ledger/period-closing-settings', settings)
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  const updateAuditSettings = async (settings) => {
    try {
      const response = await api.put('/general-ledger/audit-settings', settings)
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  return {
    loading,
    error,
    getSettings,
    updateSettings,
    getAccountingPeriods,
    openPeriod,
    closePeriod,
    updatePeriodClosingSettings,
    updateAuditSettings
  }
})