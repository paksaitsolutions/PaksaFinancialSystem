import { api } from '@/utils/api';

export const dataIntegrityService = {
  async getConstraintsReview() {
    return api.get('/api/v1/data-integrity/constraints-review');
  },

  async runReconciliation() {
    return api.post('/api/v1/data-integrity/reconciliation', {}, { idempotencyKey: true });
  },

  async getDataQualityDashboard() {
    return api.get('/api/v1/data-quality/dashboard');
  }
};
