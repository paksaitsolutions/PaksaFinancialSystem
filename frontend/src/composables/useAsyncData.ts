import { ref, Ref } from 'vue'
import { apiClient } from '@/utils/apiClient'

interface UseAsyncDataOptions {
  cache?: boolean
  ttl?: number
  immediate?: boolean
}

export function useAsyncData<T>(
  url: string,
  options: UseAsyncDataOptions = {}
) {
  const { cache = true, ttl = 5 * 60 * 1000, immediate = true } = options
  
  const data: Ref<T | null> = ref(null)
  const loading = ref(false)
  const error = ref<Error | null>(null)

  const execute = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await apiClient.get<T>(url, { cache, ttl })
      data.value = response.data
    } catch (err) {
      error.value = err as Error
    } finally {
      loading.value = false
    }
  }

  const refresh = () => {
    apiClient.clearCache()
    return execute()
  }

  if (immediate) {
    execute()
  }

  return {
    data,
    loading,
    error,
    execute,
    refresh
  }
}