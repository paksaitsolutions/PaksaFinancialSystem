/**
 * Paksa Financial System - Form Validation Composable
 * Copyright (c) 2025 Paksa IT Solutions. All rights reserved.
 */
import { ref, computed } from 'vue';
import type { Ref } from 'vue';

export interface ValidationRule {
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  min?: number;
  max?: number;
  email?: boolean;
  pattern?: RegExp;
  custom?: (value: any) => boolean | string;
}

export interface FieldValidation {
  [key: string]: ValidationRule;
}

export interface ValidationErrors {
  [key: string]: string;
}

export function useFormValidation<T extends Record<string, any>>(
  formData: Ref<T>,
  rules: FieldValidation
) {
  const errors = ref<ValidationErrors>({});
  const touched = ref<Set<string>>(new Set());

  const validateField = (field: string, value: any): string => {
    const rule = rules[field];
    if (!rule) return '';

    if (rule.required && (!value || value === '' || (Array.isArray(value) && value.length === 0))) {
      return 'This field is required';
    }

    if (rule.minLength && value && value.length < rule.minLength) {
      return `Minimum length is ${rule.minLength}`;
    }

    if (rule.maxLength && value && value.length > rule.maxLength) {
      return `Maximum length is ${rule.maxLength}`;
    }

    if (rule.min !== undefined && value < rule.min) {
      return `Minimum value is ${rule.min}`;
    }

    if (rule.max !== undefined && value > rule.max) {
      return `Maximum value is ${rule.max}`;
    }

    if (rule.email && value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
      return 'Invalid email format';
    }

    if (rule.pattern && value && !rule.pattern.test(value)) {
      return 'Invalid format';
    }

    if (rule.custom) {
      const result = rule.custom(value);
      if (typeof result === 'string') return result;
      if (!result) return 'Validation failed';
    }

    return '';
  };

  const validate = (): boolean => {
    const newErrors: ValidationErrors = {};
    let isValid = true;

    Object.keys(rules).forEach(field => {
      const error = validateField(field, formData.value[field]);
      if (error) {
        newErrors[field] = error;
        isValid = false;
      }
    });

    errors.value = newErrors;
    return isValid;
  };

  const validateSingleField = (field: string) => {
    const error = validateField(field, formData.value[field]);
    if (error) {
      errors.value[field] = error;
    } else {
      delete errors.value[field];
    }
    touched.value.add(field);
  };

  const clearErrors = () => {
    errors.value = {};
    touched.value.clear();
  };

  const hasError = (field: string) => computed(() => !!errors.value[field]);
  const getError = (field: string) => computed(() => errors.value[field] || '');
  const isValid = computed(() => Object.keys(errors.value).length === 0);

  return {
    errors,
    touched,
    validate,
    validateSingleField,
    clearErrors,
    hasError,
    getError,
    isValid
  };
}

// Common validation rules
export const commonRules = {
  required: { required: true },
  email: { required: true, email: true },
  phone: { 
    required: true, 
    pattern: /^[\d\s\-\+\(\)]+$/,
    minLength: 10 
  },
  amount: { 
    required: true, 
    min: 0,
    custom: (val: any) => !isNaN(parseFloat(val)) || 'Must be a valid number'
  },
  percentage: { 
    required: true, 
    min: 0, 
    max: 100 
  },
  date: {
    required: true,
    custom: (val: any) => val instanceof Date || 'Must be a valid date'
  },
  positiveNumber: {
    required: true,
    min: 0.01,
    custom: (val: any) => parseFloat(val) > 0 || 'Must be greater than 0'
  }
};
