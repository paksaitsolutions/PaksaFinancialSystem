import { defineStore } from 'pinia'
import axios from 'axios'

export const useIntegrationStore = defineStore('integration', {
  state: () => ({
    executiveDashboard: null,
    cashFlowStatement: null,
    financialSummary: null,
    loading: false,
    error: null
  }),

  actions: {
    async getExecutiveDashboard(companyId, periodStart = null, periodEnd = null) {
      this.loading = true
      try {
        const params = new URLSearchParams()
        if (periodStart) params.append('period_start', periodStart)
        if (periodEnd) params.append('period_end', periodEnd)
        
        const response = await axios.get(`/api/integration/reports/executive-dashboard/${companyId}?${params}`)
        this.executiveDashboard = response.data
        return response.data
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async getCashFlowStatement(companyId, periodStart, periodEnd) {
      this.loading = true
      try {
        const params = new URLSearchParams({
          period_start: periodStart,
          period_end: periodEnd
        })
        
        const response = await axios.get(`/api/integration/reports/cash-flow-statement/${companyId}?${params}`)
        this.cashFlowStatement = response.data
        return response.data
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async getFinancialSummary(companyId) {
      this.loading = true
      try {
        const response = await axios.get(`/api/integration/financial-summary/${companyId}`)
        this.financialSummary = response.data
        return response.data
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async processPurchaseToPayment(purchaseData) {
      this.loading = true
      try {
        const response = await axios.post('/api/integration/workflows/purchase-to-payment', purchaseData)
        return response.data
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    },

    async processInvoiceToCash(invoiceData) {
      this.loading = true
      try {
        const response = await axios.post('/api/integration/workflows/invoice-to-cash', invoiceData)
        return response.data
      } catch (error) {
        this.error = error.message
        throw error
      } finally {
        this.loading = false
      }
    }
  }
})