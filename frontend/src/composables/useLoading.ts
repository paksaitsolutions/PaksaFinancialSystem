import { ref, computed } from 'vue';

export function useLoading(initialState = false) {
  const loading = ref(initialState);
  const loadingStates = ref<Record<string, boolean>>({});

  const isLoading = computed(() => loading.value);
  const hasAnyLoading = computed(() => 
    loading.value || Object.values(loadingStates.value).some(state => state)
  );

  const setLoading = (state: boolean) => {
    loading.value = state;
  };

  const setLoadingState = (key: string, state: boolean) => {
    loadingStates.value[key] = state;
  };

  const getLoadingState = (key: string) => {
    return loadingStates.value[key] || false;
  };

  const withLoading = async <T>(
    operation: () => Promise<T>,
    key?: string
  ): Promise<T> => {
    try {
      if (key) {
        setLoadingState(key, true);
      } else {
        setLoading(true);
      }
      
      return await operation();
    } finally {
      if (key) {
        setLoadingState(key, false);
      } else {
        setLoading(false);
      }
    }
  };

  return {
    loading: isLoading,
    hasAnyLoading,
    setLoading,
    setLoadingState,
    getLoadingState,
    withLoading
  };
}