import { format as dateFnsFormat, parseISO } from 'date-fns';

export function formatCurrency(value: number | null | undefined): string {
  if (value === null || value === undefined) return '0.00';
  return new Intl.NumberFormat('en-US', {
    style: 'decimal',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(Number(value));
}

export function formatDate(date: string | Date | null | undefined): string {
  if (!date) return '';
  const dateObj = typeof date === 'string' ? parseISO(date) : date;
  return dateFnsFormat(dateObj, 'MMM d, yyyy');
}

export function formatDateTime(date: string | Date | null | undefined): string {
  if (!date) return '';
  const dateObj = typeof date === 'string' ? parseISO(date) : date;
  return dateFnsFormat(dateObj, 'MMM d, yyyy h:mm a');
}

export function formatPercentage(value: number | null | undefined): string {
  if (value === null || value === undefined) return '0.00%';
  return new Intl.NumberFormat('en-US', {
    style: 'percent',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(Number(value) / 100);
}

export function formatNumber(
  value: number | string | null | undefined,
  options: Intl.NumberFormatOptions = {}
): string {
  if (value === null || value === undefined || value === '') return '0';
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
    ...options,
  }).format(Number(value));
}

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
}

export function formatPhoneNumber(phoneNumber: string): string {
  // Remove all non-digit characters
  const cleaned = ('' + phoneNumber).replace(/\D/g, '');
  
  // Check if the number has 10 digits (US/Canada format)
  const match = cleaned.match(/^(\d{3})(\d{3})(\d{4})$/);
  if (match) {
    return `(${match[1]}) ${match[2]}-${match[3]}`;
  }
  
  // Return original if format doesn't match
  return phoneNumber;
}

export function truncateText(text: string, maxLength: number = 100): string {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return `${text.substring(0, maxLength)}...`;
}

export function formatSSN(ssn: string): string {
  if (!ssn) return '';
  // Remove all non-digit characters
  const cleaned = ssn.replace(/\D/g, '');
  
  // Format as XXX-XX-XXXX
  if (cleaned.length === 9) {
    return `${cleaned.substring(0, 3)}-${cleaned.substring(3, 5)}-${cleaned.substring(5)}`;
  }
  
  // Return original if format doesn't match
  return ssn;
}

export function formatTaxId(taxId: string): string {
  if (!taxId) return '';
  // Remove all non-alphanumeric characters
  const cleaned = taxId.replace(/[^\dA-Za-z]/g, '');
  
  // Format as XX-XXXXXXX for EIN
  if (cleaned.length === 9) {
    return `${cleaned.substring(0, 2)}-${cleaned.substring(2)}`;
  }
  
  // Return original if format doesn't match
  return taxId;
}
