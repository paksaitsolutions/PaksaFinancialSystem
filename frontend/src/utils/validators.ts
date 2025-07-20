/**
 * Form validation utilities
 * 
 * This file provides helper functions for form validation using the validation constants.
 */

import { VALIDATION_RULES, VALIDATION_MESSAGES } from '@/constants/validation';
import type { Ref } from 'vue';

type ValidationRule = (value: any) => true | string;

/**
 * Creates a validation function that applies multiple rules
 * @param rules Array of validation rules to apply
 * @returns A function that validates a value against all rules
 */
export function createValidator(rules: Array<(value: any) => true | string>): (value: any) => true | string {
  return (value: any) => {
    for (const rule of rules) {
      const result = rule(value);
      if (result !== true) {
        return result; // Return the first error message
      }
    }
    return true; // All rules passed
  };
}

/**
 * Common validation rules as composable functions
 */
export function useValidators() {
  /**
   * Required field validator
   */
  const required = (fieldName: string): ValidationRule => {
    return (value: any) => {
      if (value === null || value === undefined || value === '') {
        return VALIDATION_MESSAGES.REQUIRED(fieldName);
      }
      if (Array.isArray(value) && value.length === 0) {
        return VALIDATION_MESSAGES.REQUIRED(fieldName);
      }
      return true;
    };
  };

  /**
   * Email validator
   */
  const email = (value: string): true | string => {
    if (!value) return true; // Skip if empty (use with required() if needed)
    return VALIDATION_RULES.email(value);
  };

  /**
   * Password strength validator
   */
  const password = (value: string): true | string => {
    if (!value) return true; // Skip if empty (use with required() if needed)
    return VALIDATION_RULES.password(value);
  };

  /**
   * Minimum length validator
   */
  const minLength = (min: number): ValidationRule => {
    return (value: string) => {
      if (!value) return true; // Skip if empty (use with required() if needed)
      return value.length >= min || VALIDATION_MESSAGES.MIN_LENGTH('This field', min);
    };
  };

  /**
   * Maximum length validator
   */
  const maxLength = (max: number): ValidationRule => {
    return (value: string) => {
      if (!value) return true; // Skip if empty
      return value.length <= max || VALIDATION_MESSAGES.MAX_LENGTH('This field', max);
    };
  };

  /**
   * Minimum value validator (for numbers)
   */
  const minValue = (min: number): ValidationRule => {
    return (value: number) => {
      if (value === null || value === undefined) return true;
      const num = typeof value === 'string' ? parseFloat(value) : value;
      return num >= min || VALIDATION_MESSAGES.MIN_VALUE('This field', min);
    };
  };

  /**
   * Maximum value validator (for numbers)
   */
  const maxValue = (max: number): ValidationRule => {
    return (value: number) => {
      if (value === null || value === undefined) return true;
      const num = typeof value === 'string' ? parseFloat(value) : value;
      return num <= max || VALIDATION_MESSAGES.MAX_VALUE('This field', max);
    };
  };

  /**
   * Pattern matching validator
   */
  const pattern = (regex: RegExp, message: string): ValidationRule => {
    return (value: string) => {
      if (!value) return true; // Skip if empty
      return regex.test(value) || message;
    };
  };

  /**
   * Custom validator function
   */
  const custom = (validator: (value: any) => true | string): ValidationRule => {
    return (value: any) => validator(value);
  };

  /**
   * Creates a validator that checks if two fields match
   * Useful for password confirmation fields
   */
  const matchField = (otherValue: Ref<any>, message: string): ValidationRule => {
    return (value: any) => {
      return value === otherValue.value || message;
    };
  };

  /**
   * Creates a validator that checks if a date is in the future
   */
  const futureDate = (value: string | Date): true | string => {
    if (!value) return true; // Skip if empty
    const date = typeof value === 'string' ? new Date(value) : value;
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    return date > today || VALIDATION_MESSAGES.FUTURE_DATE;
  };

  /**
   * Creates a validator that checks if a date is in the past
   */
  const pastDate = (value: string | Date): true | string => {
    if (!value) return true; // Skip if empty
    const date = typeof value === 'string' ? new Date(value) : value;
    const today = new Date();
    today.setHours(23, 59, 59, 999);
    return date < today || VALIDATION_MESSAGES.PAST_DATE;
  };

  /**
   * Creates a validator that checks if a value is a valid number
   */
  const number = (value: any): true | string => {
    if (value === null || value === undefined || value === '') return true;
    return !isNaN(Number(value)) || VALIDATION_MESSAGES.INVALID_NUMBER;
  };

  /**
   * Creates a validator that checks if a value is a valid currency amount
   */
  const currency = (value: string): true | string => {
    if (!value) return true;
    return VALIDATION_RULES.currency(value);
  };

  /**
   * Creates a validator that checks if a value is a valid percentage (0-100)
   */
  const percentage = (value: string): true | string => {
    if (!value) return true;
    return VALIDATION_RULES.percentage(value);
  };

  return {
    createValidator,
    required,
    email,
    password,
    minLength,
    maxLength,
    minValue,
    maxValue,
    pattern,
    custom,
    matchField,
    futureDate,
    pastDate,
    number,
    currency,
    percentage,
  };
}

/**
 * Composable for form validation
 */
export function useFormValidation() {
  const errors = ref<Record<string, string>>({});
  const isValid = ref(false);
  const isDirty = ref(false);

  /**
   * Validates a form field
   */
  const validateField = (fieldName: string, value: any, validators: Array<(value: any) => true | string>) => {
    const validator = createValidator(validators);
    const result = validator(value);
    
    if (result === true) {
      // Remove error if it exists
      if (errors.value[fieldName]) {
        const newErrors = { ...errors.value };
        delete newErrors[fieldName];
        errors.value = newErrors;
      }
      return true;
    } else {
      // Set error
      errors.value = {
        ...errors.value,
        [fieldName]: result as string,
      };
      return false;
    }
  };

  /**
   * Validates the entire form
   */
  const validateForm = (fields: Record<string, { value: any; validators: Array<(value: any) => true | string> }>) => {
    let formIsValid = true;
    const newErrors: Record<string, string> = {};
    
    for (const [fieldName, field] of Object.entries(fields)) {
      const validator = createValidator(field.validators);
      const result = validator(field.value);
      
      if (result !== true) {
        newErrors[fieldName] = result;
        formIsValid = false;
      }
    }
    
    errors.value = newErrors;
    isValid.value = formIsValid;
    isDirty.value = true;
    
    return formIsValid;
  };

  /**
   * Resets the form validation state
   */
  const resetValidation = () => {
    errors.value = {};
    isValid.value = false;
    isDirty.value = false;
  };

  /**
   * Gets the error message for a field
   */
  const getError = (fieldName: string): string => {
    return errors.value[fieldName] || '';
  };

  /**
   * Checks if a field has an error
   */
  const hasError = (fieldName: string): boolean => {
    return !!errors.value[fieldName];
  };

  return {
    errors,
    isValid,
    isDirty,
    validateField,
    validateForm,
    resetValidation,
    getError,
    hasError,
  };
}

// Export types
export type { ValidationRule };
