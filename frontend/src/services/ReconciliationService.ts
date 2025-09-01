import api from './api'

const ReconciliationService = {
  async getReconciliationStatus(accountId: string, startDate?: Date, endDate?: Date) {
    const params: any = { account_id: accountId }
    if (startDate) params.start_date = startDate.toISOString().slice(0, 10)
    if (endDate) params.end_date = endDate.toISOString().slice(0, 10)
    const res = await api.get('/api/v1/reconciliation/status', { params })
    return res.data
  },

  async startReconciliation(accountId: string, statementDate: Date, openingBalance: number, closingBalance: number) {
    const payload = {
      account_id: accountId,
      statement_date: statementDate.toISOString().slice(0, 10),
      opening_balance: openingBalance,
      closing_balance: closingBalance,
      currency: 'USD'
    }
    const res = await api.post('/api/v1/reconciliation/start', payload)
    return res.data
  },

  async getUnreconciledTransactions(accountId: string, reconciliationId: string) {
    const res = await api.get(`/api/v1/reconciliation/${reconciliationId}/unreconciled`, {
      params: { account_id: accountId }
    })
    return res.data
  },

  async importBankStatement(accountId: string, file: File) {
    const form = new FormData()
    form.append('file', file)
    const res = await api.post(`/api/v1/reconciliation/import`, form, {
      params: { account_id: accountId },
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return res.data
  },

  async matchTransactions(matches: Array<{ transaction_id: string, statement_item_ids?: string[] }>) {
    const res = await api.post('/api/v1/reconciliation/match', { matches })
    return res.data
  },

  async completeReconciliation(reconciliationId: string) {
    const res = await api.post(`/api/v1/reconciliation/${reconciliationId}/complete`)
    return res.data
  }
}

export default ReconciliationService

