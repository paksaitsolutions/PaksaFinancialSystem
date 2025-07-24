import { api } from '@/utils/api';
import { format } from 'date-fns';

export interface Currency {
  id: string;
  code: string;
  name: string;
  symbol: string;
  decimal_places: number;
  status: 'active' | 'inactive';
  is_base_currency: boolean;
  created_at: string;
  updated_at: string;
}

export interface ExchangeRate {
  id: string;
  source_currency: Currency;
  target_currency: Currency;
  rate: string;
  effective_date: string;
  rate_type: 'spot' | 'forward' | 'historical';
  is_official: boolean;
  source: string;
  created_at: string;
  updated_at: string;
}

export interface ConversionRequest {
  amount: number;
  from_currency: string;
  to_currency: string;
  conversion_date?: string;
}

export interface ConversionResponse {
  original_amount: string;
  original_currency: string;
  converted_amount: string;
  target_currency: string;
  exchange_rate: string;
  conversion_date: string;
  rate_source: string;
}

/**
 * Currency Service
 * Provides methods to interact with the currency API endpoints
 */
export default {
  /**
   * Get all currencies
   * @param includeInactive - Whether to include inactive currencies
   * @returns Promise with the list of currencies
   */
  async getAllCurrencies(includeInactive = false) {
    return api.get(`/currency?include_inactive=${includeInactive}`);
  },

  /**
   * Get a currency by ID
   * @param id - Currency ID
   * @returns Promise with the currency details
   */
  async getCurrency(id: string) {
    return api.get(`/currency/${id}`);
  },

  /**
   * Get a currency by code
   * @param code - Currency code (e.g., USD, EUR)
   * @returns Promise with the currency details
   */
  async getCurrencyByCode(code: string) {
    return api.get(`/currency/code/${code}`);
  },

  /**
   * Get the base currency
   * @returns Promise with the base currency details
   */
  async getBaseCurrency() {
    return api.get('/currency/base');
  },

  /**
   * Create a new currency
   * @param currency - Currency data
   * @returns Promise with the created currency
   */
  async createCurrency(currency: {
    code: string;
    name: string;
    symbol?: string;
    decimal_places?: number;
    status?: 'active' | 'inactive';
    is_base_currency?: boolean;
  }) {
    return api.post('/currency', currency);
  },

  /**
   * Update a currency
   * @param id - Currency ID
   * @param currency - Currency data to update
   * @returns Promise with the updated currency
   */
  async updateCurrency(id: string, currency: {
    code?: string;
    name?: string;
    symbol?: string;
    decimal_places?: number;
    status?: 'active' | 'inactive';
    is_base_currency?: boolean;
  }) {
    return api.put(`/currency/${id}`, currency);
  },

  /**
   * Delete a currency
   * @param id - Currency ID
   * @returns Promise with the deletion result
   */
  async deleteCurrency(id: string) {
    return api.delete(`/currency/${id}`);
  },

  /**
   * Create a new exchange rate
   * @param rate - Exchange rate data
   * @returns Promise with the created exchange rate
   */
  async createExchangeRate(rate: {
    source_currency_code: string;
    target_currency_code: string;
    rate: number;
    effective_date: Date;
    rate_type?: 'spot' | 'forward' | 'historical';
    is_official?: boolean;
    source?: string;
  }) {
    const formattedRate = {
      ...rate,
      effective_date: format(rate.effective_date, 'yyyy-MM-dd')
    };
    return api.post('/currency/exchange-rates', formattedRate);
  },

  /**
   * Get an exchange rate between two currencies
   * @param sourceCode - Source currency code
   * @param targetCode - Target currency code
   * @param date - Date for the rate (optional)
   * @returns Promise with the exchange rate
   */
  async getExchangeRate(sourceCode: string, targetCode: string, date?: Date) {
    let url = `/currency/exchange-rates/${sourceCode}/${targetCode}`;
    if (date) {
      url += `?rate_date=${format(date, 'yyyy-MM-dd')}`;
    }
    return api.get(url);
  },

  /**
   * Convert an amount between currencies
   * @param conversionRequest - Conversion request data
   * @returns Promise with the conversion result
   */
  async convertCurrency(conversionRequest: ConversionRequest) {
    const formattedRequest = {
      ...conversionRequest,
      conversion_date: conversionRequest.conversion_date 
        ? format(new Date(conversionRequest.conversion_date), 'yyyy-MM-dd')
        : undefined
    };
    return api.post('/currency/convert', formattedRequest);
  },

  /**
   * Format a number according to currency rules
   * @param amount - Amount to format
   * @param currencyCode - Currency code
   * @returns Formatted amount string
   */
  formatCurrency(amount: number, currencyCode: string = 'USD'): string {
    const formatter = new Intl.NumberFormat(undefined, {
      style: 'currency',
      currency: currencyCode,
    });
    return formatter.format(amount);
  }
};