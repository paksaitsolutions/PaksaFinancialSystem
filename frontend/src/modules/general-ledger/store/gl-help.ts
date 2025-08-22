import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useApi } from '@/composables/useApi'

export const useGLHelpStore = defineStore('gl-help', () => {
  const api = useApi()
  const loading = ref(false)
  const error = ref(null)

  const submitFeedback = async (feedbackData) => {
    loading.value = true
    try {
      const response = await api.post('/general-ledger/help/feedback', feedbackData)
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const getHelpContent = async (topicId) => {
    try {
      const response = await api.get(`/general-ledger/help/topics/${topicId}`)
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  const searchHelp = async (query) => {
    try {
      const response = await api.get('/general-ledger/help/search', { params: { q: query } })
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  return {
    loading,
    error,
    submitFeedback,
    getHelpContent,
    searchHelp
  }
})