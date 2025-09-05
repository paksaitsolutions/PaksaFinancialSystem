import { api } from '@/utils/api';

export interface BankAccount {
  id: string;
  name: string;
  account_number: string;
  bank_name: string;
  account_type: string;
  current_balance: number;
  is_active: boolean;
  company_id: string;
  created_at: string;
  updated_at: string;
}

export interface BankAccountCreate {
  name: string;
  account_number: string;
  bank_name: string;
  account_type: string;
  current_balance?: number;
  is_active?: boolean;
}

export default {
  async getBankAccounts(companyId: string) {
    return api.get(`/bank-accounts/company/${companyId}`);
  },

  async getBankAccount(accountId: string) {
    return api.get(`/bank-accounts/${accountId}`);
  },

  async createBankAccount(companyId: string, accountData: BankAccountCreate) {
    return api.post(`/bank-accounts/company/${companyId}`, accountData);
  },

  async updateBankAccount(accountId: string, accountData: Partial<BankAccountCreate>) {
    return api.put(`/bank-accounts/${accountId}`, accountData);
  },

  async deleteBankAccount(accountId: string) {
    return api.delete(`/bank-accounts/${accountId}`);
  }
};