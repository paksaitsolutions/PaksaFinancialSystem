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
    return api.get(`/chart-of-accounts/company/${companyId}`);
  },

  async getAccount(accountId: string) {
    return api.get(`/chart-of-accounts/${accountId}`);
  },

  async createAccount(companyId: string, accountData: ChartOfAccountCreate) {
    return api.post(`/chart-of-accounts/company/${companyId}`, accountData);
  },

  async updateAccount(accountId: string, accountData: Partial<ChartOfAccountCreate>) {
    return api.put(`/chart-of-accounts/${accountId}`, accountData);
  },

  async deleteAccount(accountId: string) {
    return api.delete(`/chart-of-accounts/${accountId}`);
  },

  async getAccountTypes() {
    return api.get('/chart-of-accounts/account-types');
  },

  async getAccountBalance(accountId: string, asOfDate?: string) {
    const params = asOfDate ? `?as_of_date=${asOfDate}` : '';
    return api.get(`/chart-of-accounts/${accountId}/balance${params}`);
  }
};