import api from '@/services/api';

class ReconciliationService {
  // Get reconciliation status for an account
  async getReconciliationStatus(accountId, startDate, endDate) {
    try {
      const response = await api.get(`/api/cash/reconciliations/status`, {
        params: { account_id: accountId, start_date: startDate, end_date: endDate }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching reconciliation status:', error);
      throw error;
    }
  }

  // Start a new reconciliation
  async startReconciliation(accountId, statementDate, openingBalance, closingBalance) {
    try {
      const response = await api.post('/api/cash/reconciliations', {
        account_id: accountId,
        statement_date: statementDate,
        opening_balance: openingBalance,
        closing_balance: closingBalance
      });
      return response.data;
    } catch (error) {
      console.error('Error starting reconciliation:', error);
      throw error;
    }
  }

  // Get unreconciled transactions
  async getUnreconciledTransactions(accountId, reconciliationId) {
    try {
      const response = await api.get(`/api/cash/transactions/unreconciled`, {
        params: { 
          account_id: accountId,
          reconciliation_id: reconciliationId 
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching unreconciled transactions:', error);
      throw error;
    }
  }

  // Match transactions
  async matchTransactions(matches) {
    try {
      const response = await api.post('/api/cash/reconciliations/match', { matches });
      return response.data;
    } catch (error) {
      console.error('Error matching transactions:', error);
      throw error;
    }
  }

  // Complete reconciliation
  async completeReconciliation(reconciliationId) {
    try {
      const response = await api.post(`/api/cash/reconciliations/${reconciliationId}/complete`);
      return response.data;
    } catch (error) {
      console.error('Error completing reconciliation:', error);
      throw error;
    }
  }

  // Get reconciliation report
  async getReconciliationReport(reconciliationId) {
    try {
      const response = await api.get(`/api/cash/reconciliations/${reconciliationId}/report`);
      return response.data;
    } catch (error) {
      console.error('Error fetching reconciliation report:', error);
      throw error;
    }
  }

  // Import bank statement
  async importBankStatement(accountId, file, format = 'csv') {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('account_id', accountId);
      formData.append('format', format);

      const response = await api.post('/api/cash/statements/import', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error importing bank statement:', error);
      throw error;
    }
  }
}

export default new ReconciliationService();
