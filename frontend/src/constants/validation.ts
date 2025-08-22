/**
 * Validation rules and messages for form fields
 * 
 * This file centralizes all validation rules and messages to ensure consistency
 * across the application and make updates easier.
 */

/**
 * Common validation patterns
 */
export const VALIDATION_PATTERNS = {
  EMAIL: /^[^\s@]+@[^\s@]+\.[^\s@]+$/, // Simple email pattern
  PHONE: /^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$/,
  PASSWORD: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/,
  URL: /^(https?:\/\/)?([\w.-]+)\.([a-z]{2,})(\/\S*)?$/i,
  ZIP_CODE: /^[0-9]{5}(-[0-9]{4})?$/,
  CURRENCY: /^\d+(\.\d{1,2})?$/,
  PERCENTAGE: /^100(\.0{0,2})?$|^\d{1,2}(\.\d{1,2})?$/,
  TAX_ID: /^[0-9]{5}-[0-9]{4}-[0-9]{2}-[0-9]{3}$/,
  BANK_ACCOUNT: /^\d{9,18}$/,
  ROUTING_NUMBER: /^\d{9}$/,
  CREDIT_CARD: /^\d{4} \d{4} \d{4} \d{4}$/,
  EXPIRY_DATE: /^(0[1-9]|1[0-2])\/([0-9]{2})$/,
  CVV: /^\d{3,4}$/,
} as const;

/**
 * Common validation messages
 */
export const VALIDATION_MESSAGES = {
  REQUIRED: (field: string) => `${field} is required`,
  INVALID_EMAIL: 'Please enter a valid email address',
  INVALID_PHONE: 'Please enter a valid phone number',
  INVALID_PASSWORD: 'Password must be at least 8 characters long and include at least one uppercase letter, one lowercase letter, one number, and one special character',
  PASSWORDS_DO_NOT_MATCH: 'Passwords do not match',
  MIN_LENGTH: (field: string, length: number) => `${field} must be at least ${length} characters`,
  MAX_LENGTH: (field: string, length: number) => `${field} must be less than ${length} characters`,
  MIN_VALUE: (field: string, value: number) => `${field} must be at least ${value}`,
  MAX_VALUE: (field: string, value: number) => `${field} must be less than ${value}`,
  INVALID_FORMAT: (field: string) => `Invalid ${field} format`,
  INVALID_DATE: 'Please enter a valid date',
  FUTURE_DATE: 'Date must be in the future',
  PAST_DATE: 'Date must be in the past',
  INVALID_NUMBER: 'Please enter a valid number',
  INVALID_CURRENCY: 'Please enter a valid currency amount',
  INVALID_PERCENTAGE: 'Please enter a valid percentage (0-100)',
  INVALID_TAX_ID: 'Please enter a valid tax ID (format: 12345-6789-01-234)',
  INVALID_BANK_ACCOUNT: 'Please enter a valid bank account number (9-18 digits)',
  INVALID_ROUTING_NUMBER: 'Please enter a valid routing number (9 digits)',
  INVALID_CREDIT_CARD: 'Please enter a valid credit card number',
  INVALID_EXPIRY_DATE: 'Please enter a valid expiry date (MM/YY)',
  INVALID_CVV: 'Please enter a valid CVV (3-4 digits)',
} as const;

/**
 * Common validation rules for form fields
 */
export const VALIDATION_RULES = {
  // Required field
  required: (value: any) => !!value || VALIDATION_MESSAGES.REQUIRED('This field'),
  
  // Email validation
  email: (value: string) => {
    if (!value) return true;
    return VALIDATION_PATTERNS.EMAIL.test(value) || VALIDATION_MESSAGES.INVALID_EMAIL;
  },
  
  // Password validation
  password: (value: string) => {
    if (!value) return true;
    return VALIDATION_PATTERNS.PASSWORD.test(value) || VALIDATION_MESSAGES.INVALID_PASSWORD;
  },
  
  // Phone number validation
  phone: (value: string) => {
    if (!value) return true;
    return VALIDATION_PATTERNS.PHONE.test(value) || VALIDATION_MESSAGES.INVALID_PHONE;
  },
  
  // Minimum length validation
  minLength: (value: string, length: number) => {
    if (!value) return true;
    return value.length >= length || VALIDATION_MESSAGES.MIN_LENGTH('This field', length);
  },
  
  // Maximum length validation
  maxLength: (value: string, length: number) => {
    if (!value) return true;
    return value.length <= length || VALIDATION_MESSAGES.MAX_LENGTH('This field', length);
  },
  
  // Minimum value validation (for numbers)
  minValue: (value: number, min: number) => {
    if (value === null || value === undefined) return true;
    return value >= min || VALIDATION_MESSAGES.MIN_VALUE('This field', min);
  },
  
  // Maximum value validation (for numbers)
  maxValue: (value: number, max: number) => {
    if (value === null || value === undefined) return true;
    return value <= max || VALIDATION_MESSAGES.MAX_VALUE('This field', max);
  },
  
  // Currency validation
  currency: (value: string) => {
    if (!value) return true;
    return VALIDATION_PATTERNS.CURRENCY.test(value) || VALIDATION_MESSAGES.INVALID_CURRENCY;
  },
  
  // Percentage validation (0-100)
  percentage: (value: string) => {
    if (!value) return true;
    const num = parseFloat(value);
    return (num >= 0 && num <= 100) || VALIDATION_MESSAGES.INVALID_PERCENTAGE;
  },
  
  // Date validation
  futureDate: (value: string) => {
    if (!value) return true;
    const date = new Date(value);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    return date > today || VALIDATION_MESSAGES.FUTURE_DATE;
  },
  
  // Past date validation
  pastDate: (value: string) => {
    if (!value) return true;
    const date = new Date(value);
    const today = new Date();
    today.setHours(23, 59, 59, 999);
    return date < today || VALIDATION_MESSAGES.PAST_DATE;
  },
} as const;

/**
 * Common form field configurations
 */
export const FORM_FIELDS = {
  // Common field configurations
  TEXT: {
    variant: 'outlined',
    density: 'comfortable',
  },
  
  // Common select field configurations
  SELECT: {
    variant: 'outlined',
    density: 'comfortable',
    itemTitle: 'name',
    itemValue: 'id',
  },
  
  // Common date picker configurations
  DATE_PICKER: {
    variant: 'outlined',
    density: 'comfortable',
    format: 'yyyy-MM-dd',
  },
  
  // Common textarea configurations
  TEXTAREA: {
    variant: 'outlined',
    density: 'comfortable',
    rows: 3,
    autoGrow: true,
  },
} as const;
