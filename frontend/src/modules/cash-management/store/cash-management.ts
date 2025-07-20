import { defineStore } from 'pinia';

export const useCashManagementStore = defineStore('cashManagement', {
  state: () => ({
    // Shared state for the Cash Management module
    loading: false,
    error: null as string | null,
  }),
  
  actions: {
    setLoading(loading: boolean) {
      this.loading = loading;
    },
    
    setError(error: string | null) {
      this.error = error;
    },
    
    clearError() {
      this.error = null;
    },
  },
});
