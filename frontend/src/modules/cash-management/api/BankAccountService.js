import api from '@/api';

class BankAccountService {
  /**
   * Get all bank accounts
   * @param {Object} params - Query parameters
   * @returns {Promise<Array>} List of bank accounts
   */
  async getBankAccounts(params = {}) {
    try {
      const response = await api.get('/cash-management/bank-accounts/', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching bank accounts:', error);
      throw error;
    }
  }

  /**
   * Get a single bank account by ID
   * @param {string} id - Bank account ID
   * @returns {Promise<Object>} Bank account details
   */
  async getBankAccount(id) {
    try {
      const response = await api.get(`/cash-management/bank-accounts/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching bank account ${id}:`, error);
      throw error;
    }
  }

  /**
   * Create a new bank account
   * @param {Object} accountData - Bank account data
   * @returns {Promise<Object>} Created bank account
   */
  async createBankAccount(accountData) {
    try {
      const response = await api.post('/cash-management/bank-accounts/', accountData);
      return response.data;
    } catch (error) {
      console.error('Error creating bank account:', error);
      throw error;
    }
  }

  /**
   * Update an existing bank account
   * @param {string} id - Bank account ID
   * @param {Object} accountData - Updated bank account data
   * @returns {Promise<Object>} Updated bank account
   */
  async updateBankAccount(id, accountData) {
    try {
      const response = await api.put(`/cash-management/bank-accounts/${id}`, accountData);
      return response.data;
    } catch (error) {
      console.error(`Error updating bank account ${id}:`, error);
      throw error;
    }
  }

  /**
   * Delete a bank account
   * @param {string} id - Bank account ID
   * @returns {Promise<void>}
   */
  async deleteBankAccount(id) {
    try {
      await api.delete(`/cash-management/bank-accounts/${id}`);
    } catch (error) {
      console.error(`Error deleting bank account ${id}:`, error);
      throw error;
    }
  }

  /**
   * Get transactions for a bank account
   * @param {string} accountId - Bank account ID
   * @param {Object} params - Query parameters
   * @returns {Promise<Array>} List of transactions
   */
  async getAccountTransactions(accountId, params = {}) {
    try {
      const response = await api.get(`/cash-management/bank-accounts/${accountId}/transactions`, { params });
      return response.data;
    } catch (error) {
      console.error(`Error fetching transactions for account ${accountId}:`, error);
      throw error;
    }
  }

  /**
   * Get reconciliation history for a bank account
   * @param {string} accountId - Bank account ID
   * @returns {Promise<Array>} List of reconciliations
   */
  async getAccountReconciliations(accountId) {
    try {
      const response = await api.get(`/cash-management/bank-accounts/${accountId}/reconciliations`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching reconciliations for account ${accountId}:`, error);
      throw error;
    }
  }

  /**
   * Get cash position summary
   * @returns {Promise<Object>} Cash position data
   */
  async getCashPosition() {
    try {
      const response = await api.get('/cash-management/cash-position');
      return response.data;
    } catch (error) {
      console.error('Error fetching cash position:', error);
      throw error;
    }
  }

  /**
   * Get cash flow forecast
   * @param {Object} params - Query parameters
   * @returns {Promise<Object>} Cash flow forecast data
   */
  async getCashFlowForecast(params = {}) {
    try {
      const response = await api.get('/cash-management/forecasts', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching cash flow forecast:', error);
      throw error;
    }
  }

  /**
   * Import bank statements
   * @param {string} accountId - Bank account ID
   * @param {File} file - Statement file
   * @param {Object} options - Import options
   * @returns {Promise<Object>} Import result
   */
  async importBankStatement(accountId, file, options = {}) {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      if (options.format) {
        formData.append('format', options.format);
      }
      if (options.startDate) {
        formData.append('start_date', options.startDate);
      }
      if (options.endDate) {
        formData.append('end_date', options.endDate);
      }

      const response = await api.post(
        `/cash-management/bank-accounts/${accountId}/import`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      
      return response.data;
    } catch (error) {
      console.error('Error importing bank statement:', error);
      throw error;
    }
  }

  /**
   * Export bank account data
   * @param {string} accountId - Bank account ID
   * @param {string} format - Export format (csv, xlsx, pdf)
   * @param {Object} params - Query parameters
   * @returns {Promise<Blob>} Exported file
   */
  async exportBankAccountData(accountId, format = 'csv', params = {}) {
    try {
      const response = await api.get(
        `/cash-management/bank-accounts/${accountId}/export`,
        {
          params: { ...params, format },
          responseType: 'blob',
        }
      );
      
      return response.data;
    } catch (error) {
      console.error('Error exporting bank account data:', error);
      throw error;
    }
  }
}

export default new BankAccountService();
