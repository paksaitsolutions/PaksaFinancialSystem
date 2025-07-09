/**
 * Common validation utilities
 */

/**
 * Check if a value is empty (null, undefined, empty string, or whitespace)
 * @param value Value to check
 * @returns boolean indicating if the value is empty
 */
export const isEmpty = (value: any): boolean => {
  if (value === null || value === undefined) {
    return true;
  }
  if (typeof value === 'string') {
    return value.trim().length === 0;
  }
  if (Array.isArray(value)) {
    return value.length === 0;
  }
  if (typeof value === 'object') {
    return Object.keys(value).length === 0;
  }
  return false;
};

/**
 * Validate an email address
 * @param email Email to validate
 * @returns boolean indicating if the email is valid
 */
export const isValidEmail = (email: string): boolean => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(String(email).toLowerCase());
};

/**
 * Validate a URL
 * @param url URL to validate
 * @returns boolean indicating if the URL is valid
 */
export const isValidUrl = (url: string): boolean => {
  try {
    new URL(url);
    return true;
  } catch (_) {
    return false;
  }
};

/**
 * Validate a phone number (basic validation)
 * @param phone Phone number to validate
 * @returns boolean indicating if the phone number is valid
 */
export const isValidPhone = (phone: string): boolean => {
  const re = /^[+]?[(]?[0-9]{1,4}[)]?[-\s./0-9]*$/;
  return re.test(phone);
};

/**
 * Check if a value is a number
 * @param value Value to check
 * @returns boolean indicating if the value is a number
 */
export const isNumber = (value: any): boolean => {
  return typeof value === 'number' && !isNaN(value);
};

/**
 * Check if a value is a string
 * @param value Value to check
 * @returns boolean indicating if the value is a string
 */
export const isString = (value: any): value is string => {
  return typeof value === 'string' || value instanceof String;
};

/**
 * Check if a value is an object
 * @param value Value to check
 * @returns boolean indicating if the value is an object
 */
export const isObject = (value: any): value is object => {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
};
