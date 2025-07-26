import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useApi } from '@/composables/useApi'

export const useCollectionsStore = defineStore('ar/collections', () => {
  const api = useApi()
  
  const collections = ref([])
  const loading = ref(false)
  const error = ref(null)
  
  const getCollectionsWorkflow = async () => {
    loading.value = true
    try {
      const response = await api.get('/ar/collections/workflow')
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  const startCollectionsWorkflow = async (customerId, workflowData) => {
    loading.value = true
    try {
      const response = await api.post(`/ar/collections/workflow/${customerId}`, workflowData)
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  const sendDunningLetter = async (letterData) => {
    loading.value = true
    try {
      const response = await api.post('/ar/collections/dunning-letters/send', letterData)
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  const createPaymentReminder = async (reminderData) => {
    loading.value = true
    try {
      const response = await api.post('/ar/collections/reminders', reminderData)
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  const getAgingReport = async () => {
    loading.value = true
    try {
      const response = await api.get('/ar/collections/aging-report')
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  return {
    collections,
    loading,
    error,
    getCollectionsWorkflow,
    startCollectionsWorkflow,
    sendDunningLetter,
    createPaymentReminder,
    getAgingReport
  }
})