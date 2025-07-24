import { ref, onMounted, type Ref } from 'vue'

export interface AsyncDataOptions<T> {
  immediate?: boolean
  onError?: (error: Error) => void
  transform?: (data: any) => T
}

export function useAsyncData<T = any>(
  fetcher: () => Promise<T>,
  options: AsyncDataOptions<T> = {}
) {
  const data: Ref<T | null> = ref(null)
  const loading = ref(false)
  const error = ref<Error | null>(null)

  const execute = async () => {
    loading.value = true
    error.value = null
    
    try {
      const result = await fetcher()
      data.value = options.transform ? options.transform(result) : result
    } catch (err) {
      error.value = err as Error
      if (options.onError) {
        options.onError(err as Error)
      }
    } finally {
      loading.value = false
    }
  }

  const refresh = () => execute()

  if (options.immediate !== false) {
    onMounted(execute)
  }

  return {
    data,
    loading,
    error,
    execute,
    refresh
  }
}

export function useAsyncList<T = any>(
  fetcher: () => Promise<T[]>,
  options: AsyncDataOptions<T[]> = {}
) {
  const { data, loading, error, execute, refresh } = useAsyncData(fetcher, options)
  
  const items = ref<T[]>([])
  
  // Watch data changes and update items
  const updateItems = () => {
    items.value = data.value || []
  }
  
  return {
    items,
    loading,
    error,
    execute,
    refresh,
    updateItems
  }
}