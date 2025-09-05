import { api } from '@/utils/api';

export interface Country {
  id: string;
  code: string;
  name: string;
  full_name: string;
  iso3_code: string;
  phone_code: string;
  is_active: boolean;
}

export interface Currency {
  id: string;
  code: string;
  name: string;
  symbol: string;
  decimal_places: number;
  is_active: boolean;
}

export interface Language {
  id: string;
  code: string;
  name: string;
  native_name: string;
  is_rtl: boolean;
  is_active: boolean;
}

export interface Timezone {
  id: string;
  code: string;
  name: string;
  utc_offset: string;
  is_active: boolean;
}

export interface AccountType {
  id: string;
  code: string;
  name: string;
  category: string;
  normal_balance: string;
  is_active: boolean;
}

export interface PaymentMethod {
  id: string;
  code: string;
  name: string;
  description: string;
  is_active: boolean;
}

export interface TaxType {
  id: string;
  code: string;
  name: string;
  description: string;
  is_active: boolean;
}

export interface BankAccountType {
  id: string;
  code: string;
  name: string;
  description: string;
  is_active: boolean;
}

export default {
  async getCountries(activeOnly: boolean = true) {
    return api.get(`/reference-data/countries?active_only=${activeOnly}`);
  },

  async getCurrencies(activeOnly: boolean = true) {
    return api.get(`/reference-data/currencies?active_only=${activeOnly}`);
  },

  async getLanguages(activeOnly: boolean = true) {
    return api.get(`/reference-data/languages?active_only=${activeOnly}`);
  },

  async getTimezones(activeOnly: boolean = true) {
    return api.get(`/reference-data/timezones?active_only=${activeOnly}`);
  },

  async getAccountTypes(activeOnly: boolean = true) {
    return api.get(`/reference-data/account-types?active_only=${activeOnly}`);
  },

  async getPaymentMethods(activeOnly: boolean = true) {
    return api.get(`/reference-data/payment-methods?active_only=${activeOnly}`);
  },

  async getTaxTypes(activeOnly: boolean = true) {
    return api.get(`/reference-data/tax-types?active_only=${activeOnly}`);
  },

  async getBankAccountTypes(activeOnly: boolean = true) {
    return api.get(`/reference-data/bank-account-types?active_only=${activeOnly}`);
  }
};