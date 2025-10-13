import { api } from '@/utils/api';

export interface ChartOfAccount {
  id: string;
  code: string;
  name: string;
  account_type: string;
  parent_id?: string;
  description?: string;
  is_active: boolean;
  balance: number;
  company_id: string;
  created_at: string;
  updated_at: string;
}

export interface ChartOfAccountCreate {
  code: string;
  name: string;
  account_type: string;
  parent_id?: string;
  description?: string;
  is_active?: boolean;
}

export default {
  async getAccounts(companyId: string) {
    return api.get('/api/v1/gl/accounts');
  },

  async getAccount(accountId: string) {
    return api.get(`/api/v1/gl/accounts/${accountId}`);
  },

  async createAccount(companyId: string, accountData: ChartOfAccountCreate) {
    return api.post('/api/v1/gl/accounts', accountData);
  },

  async updateAccount(accountId: string, accountData: Partial<ChartOfAccountCreate>) {
    return api.put(`/api/v1/gl/accounts/${accountId}`, accountData);
  },

  async deleteAccount(accountId: string) {
    return api.delete(`/api/v1/gl/accounts/${accountId}`);
  },

  async getAccountTypes() {
    return api.get('/reference-data/account-types');
  },

  async getAccountBalance(accountId: string, asOfDate?: string) {
    const params = asOfDate ? `?as_of_date=${asOfDate}` : '';
    return api.get(`/api/v1/gl/accounts/${accountId}/balance${params}`);
  }
};