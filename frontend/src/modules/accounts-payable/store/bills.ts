import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useApi } from '@/composables/useApi'

export const useBillStore = defineStore('ap/bills', () => {
  const api = useApi()
  
  const bills = ref([])
  const loading = ref(false)
  const error = ref(null)
  
  const getBills = async (filters = {}) => {
    loading.value = true
    try {
      const response = await api.get('/ap/bills', { params: filters })
      bills.value = response.data
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  const createBill = async (billData) => {
    loading.value = true
    try {
      const response = await api.post('/ap/bills', billData)
      bills.value.push(response.data)
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  const updateBill = async (billId, billData) => {
    loading.value = true
    try {
      const response = await api.put(`/ap/bills/${billId}`, billData)
      const index = bills.value.findIndex(b => b.id === billId)
      if (index !== -1) {
        bills.value[index] = response.data
      }
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  const approveBill = async (billId, approvalData) => {
    loading.value = true
    try {
      const response = await api.post(`/ap/bills/${billId}/approve`, approvalData)
      const index = bills.value.findIndex(b => b.id === billId)
      if (index !== -1) {
        bills.value[index].status = 'approved'
      }
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  const rejectBill = async (billId, rejectionData) => {
    loading.value = true
    try {
      const response = await api.post(`/ap/bills/${billId}/reject`, rejectionData)
      const index = bills.value.findIndex(b => b.id === billId)
      if (index !== -1) {
        bills.value[index].status = 'rejected'
      }
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  const performThreeWayMatch = async (billId, matchData) => {
    loading.value = true
    try {
      const response = await api.post(`/ap/bills/${billId}/match`, matchData)
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  const schedulePayment = async (billId, scheduleData) => {
    loading.value = true
    try {
      const response = await api.post(`/ap/bills/${billId}/schedule-payment`, scheduleData)
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }
  
  return {
    bills,
    loading,
    error,
    getBills,
    createBill,
    updateBill,
    approveBill,
    rejectBill,
    performThreeWayMatch,
    schedulePayment
  }
})