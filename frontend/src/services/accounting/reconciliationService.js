import api from '@/api/axios';

const RECONCILIATION_BASE_URL = '/api/v1/reconciliations';

export default {
  /**
   * Get a list of reconciliations with optional filters and pagination
   * @param {Object} params - Query parameters (page, limit, status, accountId, search, etc.)
   * @returns {Promise<Array>} - List of reconciliations
   */
  async getReconciliations(params = {}) {
    try {
      const response = await api.get(RECONCILIATION_BASE_URL, { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching reconciliations:', error);
      throw error;
    }
  },

  /**
   * Get a single reconciliation by ID
   * @param {string|number} id - Reconciliation ID
   * @returns {Promise<Object>} - Reconciliation details
   */
  async getReconciliation(id) {
    try {
      const response = await api.get(`${RECONCILIATION_BASE_URL}/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching reconciliation ${id}:`, error);
      throw error;
    }
  },

  /**
   * Create a new reconciliation
   * @param {Object} data - Reconciliation data
   * @returns {Promise<Object>} - Created reconciliation
   */
  async createReconciliation(data) {
    try {
      const response = await api.post(RECONCILIATION_BASE_URL, data);
      return response.data;
    } catch (error) {
      console.error('Error creating reconciliation:', error);
      throw error;
    }
  },

  /**
   * Update an existing reconciliation
   * @param {string|number} id - Reconciliation ID
   * @param {Object} data - Updated reconciliation data
   * @returns {Promise<Object>} - Updated reconciliation
   */
  async updateReconciliation(id, data) {
    try {
      const response = await api.put(`${RECONCILIATION_BASE_URL}/${id}`, data);
      return response.data;
    } catch (error) {
      console.error(`Error updating reconciliation ${id}:`, error);
      throw error;
    }
  },

  /**
   * Delete a reconciliation
   * @param {string|number} id - Reconciliation ID
   * @returns {Promise<void>}
   */
  async deleteReconciliation(id) {
    try {
      await api.delete(`${RECONCILIATION_BASE_URL}/${id}`);
    } catch (error) {
      console.error(`Error deleting reconciliation ${id}:`, error);
      throw error;
    }
  },

  /**
   * Get reconciliation items for a specific reconciliation
   * @param {string|number} reconciliationId - Reconciliation ID
   * @param {Object} params - Query parameters (page, limit, status, etc.)
   * @returns {Promise<Array>} - List of reconciliation items
   */
  async getReconciliationItems(reconciliationId, params = {}) {
    try {
      const response = await api.get(
        `${RECONCILIATION_BASE_URL}/${reconciliationId}/items`,
        { params }
      );
      return response.data;
    } catch (error) {
      console.error(`Error fetching reconciliation ${reconciliationId} items:`, error);
      throw error;
    }
  },

  /**
   * Add an item to a reconciliation
   * @param {string|number} reconciliationId - Reconciliation ID
   * @param {Object} item - Item data
   * @returns {Promise<Object>} - Created item
   */
  async addReconciliationItem(reconciliationId, item) {
    try {
      const response = await api.post(
        `${RECONCILIATION_BASE_URL}/${reconciliationId}/items`,
        item
      );
      return response.data;
    } catch (error) {
      console.error(`Error adding item to reconciliation ${reconciliationId}:`, error);
      throw error;
    }
  },

  /**
   * Update a reconciliation item
   * @param {string|number} reconciliationId - Reconciliation ID
   * @param {string|number} itemId - Item ID
   * @param {Object} data - Updated item data
   * @returns {Promise<Object>} - Updated item
   */
  async updateReconciliationItem(reconciliationId, itemId, data) {
    try {
      const response = await api.put(
        `${RECONCILIATION_BASE_URL}/${reconciliationId}/items/${itemId}`,
        data
      );
      return response.data;
    } catch (error) {
      console.error(
        `Error updating item ${itemId} in reconciliation ${reconciliationId}:`,
        error
      );
      throw error;
    }
  },

  /**
   * Delete a reconciliation item
   * @param {string|number} reconciliationId - Reconciliation ID
   * @param {string|number} itemId - Item ID
   * @returns {Promise<void>}
   */
  async deleteReconciliationItem(reconciliationId, itemId) {
    try {
      await api.delete(
        `${RECONCILIATION_BASE_URL}/${reconciliationId}/items/${itemId}`
      );
    } catch (error) {
      console.error(
        `Error deleting item ${itemId} from reconciliation ${reconciliationId}:`,
        error
      );
      throw error;
    }
  },

  /**
   * Get reconciliation rules
   * @param {Object} params - Query parameters (accountId, isActive, etc.)
   * @returns {Promise<Array>} - List of reconciliation rules
   */
  async getReconciliationRules(params = {}) {
    try {
      const response = await api.get(`${RECONCILIATION_BASE_URL}/rules`, { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching reconciliation rules:', error);
      throw error;
    }
  },

  /**
   * Create a reconciliation rule
   * @param {Object} data - Rule data
   * @returns {Promise<Object>} - Created rule
   */
  async createReconciliationRule(data) {
    try {
      const response = await api.post(`${RECONCILIATION_BASE_URL}/rules`, data);
      return response.data;
    } catch (error) {
      console.error('Error creating reconciliation rule:', error);
      throw error;
    }
  },

  /**
   * Update a reconciliation rule
   * @param {string|number} ruleId - Rule ID
   * @param {Object} data - Updated rule data
   * @returns {Promise<Object>} - Updated rule
   */
  async updateReconciliationRule(ruleId, data) {
    try {
      const response = await api.put(
        `${RECONCILIATION_BASE_URL}/rules/${ruleId}`,
        data
      );
      return response.data;
    } catch (error) {
      console.error(`Error updating reconciliation rule ${ruleId}:`, error);
      throw error;
    }
  },

  /**
   * Delete a reconciliation rule
   * @param {string|number} ruleId - Rule ID
   * @returns {Promise<void>}
   */
  async deleteReconciliationRule(ruleId) {
    try {
      await api.delete(`${RECONCILIATION_BASE_URL}/rules/${ruleId}`);
    } catch (error) {
      console.error(`Error deleting reconciliation rule ${ruleId}:`, error);
      throw error;
    }
  },

  /**
   * Get audit logs for a reconciliation
   * @param {string|number} reconciliationId - Reconciliation ID
   * @param {Object} params - Query parameters (action, startDate, endDate, etc.)
   * @returns {Promise<Array>} - List of audit logs
   */
  async getReconciliationAuditLogs(reconciliationId, params = {}) {
    try {
      const response = await api.get(
        `${RECONCILIATION_BASE_URL}/${reconciliationId}/audit-logs`,
        { params }
      );
      return response.data;
    } catch (error) {
      console.error(
        `Error fetching audit logs for reconciliation ${reconciliationId}:`,
        error
      );
      throw error;
    }
  },

  /**
   * Export reconciliation data
   * @param {string|number} reconciliationId - Reconciliation ID
   * @param {string} format - Export format (pdf, csv, xlsx)
   * @returns {Promise<Blob>} - Exported file data
   */
  async exportReconciliation(reconciliationId, format = 'pdf') {
    try {
      const response = await api.get(
        `${RECONCILIATION_BASE_URL}/${reconciliationId}/export`,
        {
          params: { format },
          responseType: 'blob'
        }
      );
      return response.data;
    } catch (error) {
      console.error(`Error exporting reconciliation ${reconciliationId}:`, error);
      throw error;
    }
  },

  /**
   * Auto-match reconciliation items
   * @param {string|number} reconciliationId - Reconciliation ID
   * @returns {Promise<Array>} - List of matched items
   */
  async autoMatchItems(reconciliationId) {
    try {
      const response = await api.post(
        `${RECONCILIATION_BASE_URL}/${reconciliationId}/auto-match`
      );
      return response.data;
    } catch (error) {
      console.error(
        `Error auto-matching items for reconciliation ${reconciliationId}:`,
        error
      );
      throw error;
    }
  },

  /**
   * Complete a reconciliation
   * @param {string|number} reconciliationId - Reconciliation ID
   * @returns {Promise<Object>} - Updated reconciliation
   */
  async completeReconciliation(reconciliationId) {
    try {
      const response = await api.post(
        `${RECONCILIATION_BASE_URL}/${reconciliationId}/complete`
      );
      return response.data;
    } catch (error) {
      console.error(`Error completing reconciliation ${reconciliationId}:`, error);
      throw error;
    }
  },

  /**
   * Reopen a completed reconciliation
   * @param {string|number} reconciliationId - Reconciliation ID
   * @returns {Promise<Object>} - Updated reconciliation
   */
  async reopenReconciliation(reconciliationId) {
    try {
      const response = await api.post(
        `${RECONCILIATION_BASE_URL}/${reconciliationId}/reopen`
      );
      return response.data;
    } catch (error) {
      console.error(`Error reopening reconciliation ${reconciliationId}:`, error);
      throw error;
    }
  },

  /**
   * Get reconciliation statistics
   * @param {Object} params - Query parameters (accountId, startDate, endDate, etc.)
   * @returns {Promise<Object>} - Statistics data
   */
  async getReconciliationStats(params = {}) {
    try {
      const response = await api.get(
        `${RECONCILIATION_BASE_URL}/stats`,
        { params }
      );
      return response.data;
    } catch (error) {
      console.error('Error fetching reconciliation statistics:', error);
      throw error;
    }
  },

  /**
   * Import reconciliation data from a file
   * @param {string|number} reconciliationId - Reconciliation ID
   * @param {File} file - File to import
   * @param {string} format - Import format (csv, xlsx)
   * @returns {Promise<Object>} - Import result
   */
  async importReconciliationData(reconciliationId, file, format = 'csv') {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('format', format);

      const response = await api.post(
        `${RECONCILIATION_BASE_URL}/${reconciliationId}/import`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      );
      return response.data;
    } catch (error) {
      console.error(
        `Error importing data for reconciliation ${reconciliationId}:`,
        error
      );
      throw error;
    }
  }
};
