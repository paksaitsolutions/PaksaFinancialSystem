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
    
    async refreshAllData() {
      this.setLoading(true)
      try {
        // Refresh all cash management data
        console.log('Refreshing cash management data')
      } catch (error) {
        this.setError('Failed to refresh data')
      } finally {
        this.setLoading(false)
      }
    },
    
    async generateCashFlowForecast(forecastParams: any) {
      this.setLoading(true)
      try {
        // Generate cash flow forecast
        const response = await fetch('/api/v1/cash-management/cash-flow/forecast', {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' }
        })
        return await response.json()
      } catch (error) {
        this.setError('Failed to generate forecast')
        throw error
      } finally {
        this.setLoading(false)
      }
    },
    
    async performBankReconciliation(reconciliationData: any) {
      this.setLoading(true)
      try {
        const response = await fetch('/api/v1/cash-management/reconciliations', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(reconciliationData)
        })
        return await response.json()
      } catch (error) {
        this.setError('Failed to perform reconciliation')
        throw error
      } finally {
        this.setLoading(false)
      }
    },
    
    async importBankStatement(statementData: any) {
      this.setLoading(true)
      try {
        const response = await fetch('/api/v1/cash-management/bank-statements/import', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(statementData)
        })
        return await response.json()
      } catch (error) {
        this.setError('Failed to import statement')
        throw error
      } finally {
        this.setLoading(false)
      }
    },
    
    async processPayment(paymentData: any) {
      this.setLoading(true)
      try {
        const response = await fetch('/api/v1/cash-management/payments/process', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(paymentData)
        })
        return await response.json()
      } catch (error) {
        this.setError('Failed to process payment')
        throw error
      } finally {
        this.setLoading(false)
      }
    },
    
    async createBankingFee(feeData: any) {
      this.setLoading(true)
      try {
        const response = await fetch('/api/v1/cash-management/banking-fees', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(feeData)
        })
        return await response.json()
      } catch (error) {
        this.setError('Failed to create banking fee')
        throw error
      } finally {
        this.setLoading(false)
      }
    },
    
    async getCashPosition() {
      this.setLoading(true)
      try {
        const response = await fetch('/api/v1/cash-management/cash-flow/position')
        return await response.json()
      } catch (error) {
        this.setError('Failed to get cash position')
        throw error
      } finally {
        this.setLoading(false)
      }
    }
  },
});
