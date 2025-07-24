/**
 * Utility functions for formatting data
 */

export const formatCurrency = (amount: number, currency: string = 'USD'): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency
  }).format(amount);
};

export const formatPercentage = (value: number, decimals: number = 2): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'percent',
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  }).format(value / 100);
};

export const formatDate = (date: Date | string, format: string = 'PPpp'): string => {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  
  // Simple date formatting - in production, use date-fns or similar
  if (format === 'PPpp') {
    return dateObj.toLocaleString();
  }
  
  return dateObj.toLocaleDateString();
};

export const formatNumber = (value: number, decimals: number = 2): string => {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  }).format(value);
};