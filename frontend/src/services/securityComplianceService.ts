import { api } from '@/utils/api';

export const securityComplianceService = {
  async getSecurityStatus() {
    return api.get('/api/v1/security/compliance/status');
  },

  async getApprovalMatrix() {
    return api.get('/api/v1/compliance/sox/approval-matrix');
  }
};
