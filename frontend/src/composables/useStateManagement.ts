import { ref } from 'vue'

const loading = ref(false)
const error = ref('')

export const useLoadingState = () => {
  const setLoading = (value: boolean) => {
    loading.value = value
  }

  const setError = (message: string) => {
    error.value = message
  }

  const clearError = () => {
    error.value = ''
  }

  return {
    loading,
    error,
    setLoading,
    setError,
    clearError
  }
}