import currencyService from '@/services/currencyService';

interface FormatCurrencyOptions extends Intl.NumberFormatOptions {
  style?: 'currency' | 'decimal' | 'percent';
  currency?: string;
  minimumFractionDigits?: number;
  maximumFractionDigits?: number;
}

interface CurrencyConversionResult {
  amount: number;
  rate: number;
}

/**
 * Format a number as a currency string
 * @param amount - The amount to format
 * @param currencyCode - The currency code (e.g., 'USD', 'EUR')
 * @param options - Additional formatting options
 * @returns Formatted currency string
 */
export function formatCurrency(
  amount: number,
  currencyCode: string = 'USD',
  options: FormatCurrencyOptions = {}
): string {
  const defaultOptions: FormatCurrencyOptions = {
    style: 'currency',
    currency: currencyCode,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
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
 * @param amount - The amount to convert
 * @param fromCurrency - Source currency code
 * @param toCurrency - Target currency code
 * @param date - Optional date for the exchange rate
 * @returns Promise with converted amount and rate used
 */
export async function convertCurrency(
  amount: number,
  fromCurrency: string,
  toCurrency: string,
  date: Date | null = null
): Promise<CurrencyConversionResult> {
  if (fromCurrency === toCurrency) {
    return { amount, rate: 1 };
  }
  
  try {
    const response = await currencyService.convertCurrency({
      amount,
      from_currency: fromCurrency,
      to_currency: toCurrency,
      date: date?.toISOString().split('T')[0],
    });
    
    return {
      amount: response.converted_amount,
      rate: response.exchange_rate,
    };
  } catch (error) {
    console.error('Error converting currency:', error);
    throw new Error(`Failed to convert ${fromCurrency} to ${toCurrency}`);
  }
}

// Currency symbol map for common currencies
const CURRENCY_SYMBOLS: Record<string, string> = {
  USD: '$',
  EUR: '€',
  GBP: '£',
  JPY: '¥',
  CNY: '¥',
  INR: '₹',
  KRW: '₩',
  RUB: '₽',
  TRY: '₺',
  VND: '₫',
  THB: '฿',
  ILS: '₪',
  PHP: '₱',
  NGN: '₦',
};

/**
 * Get the currency symbol for a currency code
 * @param currencyCode - The currency code (e.g., 'USD', 'EUR')
 * @returns The currency symbol
 */
export function getCurrencySymbol(currencyCode: string): string {
  // Return from our map if available
  if (CURRENCY_SYMBOLS[currencyCode]) {
    return CURRENCY_SYMBOLS[currencyCode];
  }
  
  // Fallback to Intl if available
  try {
    const formatter = new Intl.NumberFormat(undefined, {
      style: 'currency',
      currency: currencyCode,
      currencyDisplay: 'symbol',
    });
    
    // Extract the symbol from the formatted string
    const parts = formatter.formatToParts(123);
    const symbolPart = parts.find(part => part.type === 'currency');
    
    return symbolPart?.value || currencyCode;
  } catch (error) {
    console.error(`Error getting symbol for ${currencyCode}:`, error);
    return currencyCode;
  }
}

// Common currency decimal places
const CURRENCY_DECIMALS: Record<string, number> = {
  BIF: 0, CLP: 0, DJF: 0, GNF: 0, JPY: 0, KMF: 0, KRW: 0,
  MGA: 0, PYG: 0, RWF: 0, VND: 0, VUV: 0, XAF: 0, XPF: 0,
  BHD: 3, JOD: 3, KWD: 3, OMR: 3, TND: 3,
};

/**
 * Get the number of decimal places for a currency
 * @param currencyCode - The currency code (e.g., 'USD', 'JPY')
 * @returns The number of decimal places (default: 2)
 */
export function getCurrencyDecimals(currencyCode: string): number {
  // Return from our map if available
  if (currencyCode in CURRENCY_DECIMALS) {
    return CURRENCY_DECIMALS[currencyCode];
  }
  
  // Default to 2 decimal places
  return 2;
}

/**
 * Parse a currency string to a number
 * @param value - The currency string to parse
 * @returns The parsed number
 */
export function parseCurrency(value: string): number {
  if (!value) return 0;
  
  // Remove all non-numeric characters except decimal point and minus sign
  const numericValue = value.replace(/[^0-9.-]+/g, '');
  
  // Parse as float and handle invalid numbers
  const parsed = parseFloat(numericValue);
  return isNaN(parsed) ? 0 : parsed;
}

export default {
  formatCurrency,
  convertCurrency,
  getCurrencySymbol,
  getCurrencyDecimals,
  parseCurrency,
};
