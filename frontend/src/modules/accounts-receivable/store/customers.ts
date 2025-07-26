import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useApi } from '@/composables/useApi'

export const useCustomerStore = defineStore('ar/customers', () => {
  const api = useApi()
  
  const customers = ref([])
  const loading = ref(false)
  const error = ref(null)
  
  const getCustomers = async (filters = {}) => {
    loading.value = true
    try {
      const response = await api.get('/ar/customers', { params: filters })
      customers.value = response.data
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  const createCustomer = async (customerData) => {
    loading.value = true
    try {
      const response = await api.post('/ar/customers', customerData)
      customers.value.push(response.data)
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  const updateCustomer = async (customerId, customerData) => {
    loading.value = true
    try {
      const response = await api.put(`/ar/customers/${customerId}`, customerData)
      const index = customers.value.findIndex(c => c.id === customerId)
      if (index !== -1) {
        customers.value[index] = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  const updateCustomerCredit = async (customerId, creditData) => {
    loading.value = true
    try {
      const response = await api.put(`/ar/customers/${customerId}/credit`, creditData)
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  return {
    customers,
    loading,
    error,
    getCustomers,
    createCustomer,
    updateCustomer,
    updateCustomerCredit
  }
})