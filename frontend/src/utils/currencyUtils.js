/**
 * Currency utility functions for formatting and conversion
 */
import currencyService from '@/services/currencyService';

/**
 * Format a number as a currency string
 * @param {number} amount - The amount to format
 * @param {string} currencyCode - The currency code (e.g., USD, EUR)
 * @param {object} options - Additional formatting options
 * @returns {string} Formatted currency string
 */
export function formatCurrency(amount, currencyCode = 'USD', options = {}) {
  const defaultOptions = {
    style: 'currency',
    currency: currencyCode,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  };
  
  // Override default options with provided options
  const formattingOptions = { ...defaultOptions, ...options };
  
  try {
    const formatter = new Intl.NumberFormat(undefined, formattingOptions);
    return formatter.format(amount);
  } catch (error) {
    console.error(`Error formatting currency ${currencyCode}:`, error);
    return `${currencyCode} ${amount.toFixed(2)}`;
  }
}

/**
 * Convert an amount from one currency to another
 * @param {number} amount - The amount to convert
 * @param {string} fromCurrency - Source currency code
 * @param {string} toCurrency - Target currency code
 * @param {Date} date - Date for the exchange rate (optional)
 * @returns {Promise<{amount: number, rate: number}>} Converted amount and rate used
 */
export async function convertCurrency(amount, fromCurrency, toCurrency, date = null) {
  if (fromCurrency === toCurrency) {
    return { amount, rate: 1 };
  }
  
  try {
    const response = await currencyService.convertCurrency({
      amount,
      from_currency: fromCurrency,
      to_currency: toCurrency,
      conversion_date: date ? date.toISOString().split('T')[0] : undefined
    });
    
    return {
      amount: parseFloat(response.data.converted_amount),
      rate: parseFloat(response.data.exchange_rate)
    };
  } catch (error) {
    console.error('Currency conversion error:', error);
    throw new Error(`Failed to convert from ${fromCurrency} to ${toCurrency}`);
  }
}

/**
 * Get the currency symbol for a currency code
 * @param {string} currencyCode - The currency code (e.g., USD, EUR)
 * @returns {string} The currency symbol
 */
export function getCurrencySymbol(currencyCode) {
  const symbols = {
    USD: '$',
    EUR: '€',
    GBP: '£',
    JPY: '¥',
    PKR: '₨',
    SAR: '﷼',
    AED: 'د.إ',
    INR: '₹',
    CNY: '¥',
    CAD: 'C$',
    AUD: 'A$',
    CHF: 'Fr',
    RUB: '₽',
    BRL: 'R$',
    MXN: 'Mex$',
    ZAR: 'R'
  };
  
  return symbols[currencyCode] || currencyCode;
}

/**
 * Get the number of decimal places for a currency
 * @param {string} currencyCode - The currency code (e.g., USD, EUR)
 * @returns {number} The number of decimal places
 */
export function getCurrencyDecimals(currencyCode) {
  const decimals = {
    USD: 2,
    EUR: 2,
    GBP: 2,
    JPY: 0,
    PKR: 0,
    SAR: 2,
    AED: 2,
    INR: 2,
    CNY: 2,
    CAD: 2,
    AUD: 2,
    CHF: 2,
    RUB: 2,
    BRL: 2,
    MXN: 2,
    ZAR: 2
  };
  
  return decimals[currencyCode] !== undefined ? decimals[currencyCode] : 2;
}

/**
 * Parse a currency string to a number
 * @param {string} value - The currency string to parse
 * @returns {number} The parsed number
 */
export function parseCurrency(value) {
  if (typeof value === 'number') return value;
  
  // Remove all non-numeric characters except decimal point
  const numStr = value.replace(/[^0-9.]/g, '');
  return parseFloat(numStr) || 0;
}