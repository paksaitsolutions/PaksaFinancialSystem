import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useApi } from '@/composables/useApi'

export const useInvoiceStore = defineStore('ar/invoices', () => {
  const api = useApi()
  
  const invoices = ref([])
  const loading = ref(false)
  const error = ref(null)
  
  const getInvoices = async (filters = {}) => {
    loading.value = true
    try {
      const response = await api.get('/ar/invoices', { params: filters })
      invoices.value = response.data
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  const createInvoice = async (invoiceData) => {
    loading.value = true
    try {
      const response = await api.post('/ar/invoices', invoiceData)
      invoices.value.push(response.data)
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  const approveInvoice = async (invoiceId, approvalData) => {
    loading.value = true
    try {
      const response = await api.post(`/ar/invoices/${invoiceId}/approve`, approvalData)
      const index = invoices.value.findIndex(i => i.id === invoiceId)
      if (index !== -1) {
        invoices.value[index].status = 'approved'
      }
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  const createRecurringInvoice = async (recurringData) => {
    loading.value = true
    try {
      const response = await api.post('/ar/invoices/recurring', recurringData)
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  const recordPayment = async (invoiceId, paymentData) => {
    loading.value = true
    try {
      const response = await api.post(`/ar/invoices/${invoiceId}/payment`, paymentData)
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  return {
    invoices,
    loading,
    error,
    getInvoices,
    createInvoice,
    approveInvoice,
    createRecurringInvoice,
    recordPayment
  }
})