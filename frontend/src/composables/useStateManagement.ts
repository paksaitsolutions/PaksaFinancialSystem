/**
 * Consistent state management patterns
 */
import { ref, reactive, computed, type Ref } from 'vue'
import type { LoadingState } from '@/types/common'

// Use ref for primitive values
export function useRefState<T>(initialValue: T): Ref<T> {
  return ref(initialValue)
}

// Use reactive for objects
export function useReactiveState<T extends object>(initialValue: T) {
  return reactive(initialValue)
}

// Standard loading state pattern
export function useLoadingState() {
  const state = reactive<LoadingState>({
    isLoading: false,
    error: null
  })
  
  const setLoading = (loading: boolean) => {
    state.isLoading = loading
    if (loading) {
      state.error = null
    }
  }
  
  const setError = (error: string | null) => {
    state.error = error
    state.isLoading = false
  }
  
  const clearError = () => {
    state.error = null
  }
  
  return {
    state,
    setLoading,
    setError,
    clearError,
    isLoading: computed(() => state.isLoading),
    error: computed(() => state.error),
    hasError: computed(() => !!state.error)
  }
}

// List management pattern
export function useListState<T>() {
  const items = ref<T[]>([])
  const selectedItems = ref<T[]>([])
  const { state: loadingState, setLoading, setError } = useLoadingState()
  
  const addItem = (item: T) => {
    items.value.push(item)
  }
  
  const removeItem = (index: number) => {
    items.value.splice(index, 1)
  }
  
  const updateItem = (index: number, item: T) => {
    items.value[index] = item
  }
  
  const selectItem = (item: T) => {
    if (!selectedItems.value.includes(item)) {
      selectedItems.value.push(item)
    }
  }
  
  const deselectItem = (item: T) => {
    const index = selectedItems.value.indexOf(item)
    if (index > -1) {
      selectedItems.value.splice(index, 1)
    }
  }
  
  const clearSelection = () => {
    selectedItems.value = []
  }
  
  return {
    items,
    selectedItems,
    loadingState,
    setLoading,
    setError,
    addItem,
    removeItem,
    updateItem,
    selectItem,
    deselectItem,
    clearSelection,
    hasItems: computed(() => items.value.length > 0),
    hasSelection: computed(() => selectedItems.value.length > 0)
  }
}