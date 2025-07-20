import { ref, reactive, computed, watch, type Ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useApiRequest, type UseApiRequestReturn } from './useApiRequest';
import type { ApiResponse } from '@/types/global';

type ValidationRule = (value: any) => string | boolean;
type ValidationRules = Record<string, ValidationRule[]>;
type FormFields = Record<string, any>;
type FormOptions<T> = {
  /**
   * Initial form values
   */
  initialValues?: T;
  
  /**
   * Validation rules for form fields
   */
  validationRules?: ValidationRules;
  
  /**
   * Whether to validate on input
   * @default true
   */
  validateOnInput?: boolean;
  
  /**
   * Whether to validate on blur
   * @default true
   */
  validateOnBlur?: boolean;
  
  /**
   * Whether to show all validation errors
   * @default false
   */
  showAllErrors?: boolean;
  
  /**
   * Custom error messages for validation rules
   */
  errorMessages?: Record<string, string>;
};

/**
 * Composable for handling forms with validation and submission
 */
export function useForm<T extends FormFields = FormFields>(options: FormOptions<T> = {}) {
  const { t } = useI18n();
  const {
    initialValues = {} as T,
    validationRules = {} as ValidationRules,
    validateOnInput = true,
    validateOnBlur = true,
    showAllErrors = false,
    errorMessages = {},
  } = options;
  
  // Form state
  const form = reactive<T>({ ...initialValues } as T);
  const touched = reactive<Record<keyof T, boolean>>({} as Record<keyof T, boolean>);
  const errors = reactive<Record<keyof T, string[]>>({} as Record<keyof T, string[]>);
  const isSubmitting = ref(false);
  const submitCount = ref(0);
  const isValid = ref(true);
  const isDirty = ref(false);
  const apiRequest = useApiRequest();
  
  // Initialize errors object
  Object.keys(initialValues).forEach((key) => {
    errors[key as keyof T] = [];
    touched[key as keyof T] = false;
  });
  
  /**
   * Default validation rules
   */
  const defaultRules: Record<string, ValidationRule> = {
    required: (value) => {
      if (value === undefined || value === null || value === '') {
        return errorMessages.required || t('validation.required');
      }
      return true;
    },
    email: (value) => {
      if (value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
        return errorMessages.email || t('validation.email');
      }
      return true;
    },
    minLength: (min) => (value) => {
      if (value && value.length < min) {
        return errorMessages.minLength || t('validation.minLength', { min });
      }
      return true;
    },
    maxLength: (max) => (value) => {
      if (value && value.length > max) {
        return errorMessages.maxLength || t('validation.maxLength', { max });
      }
      return true;
    },
    numeric: (value) => {
      if (value && isNaN(Number(value))) {
        return errorMessages.numeric || t('validation.numeric');
      }
      return true;
    },
  };
  
  /**
   * Validate a single field
   */
  const validateField = (field: keyof T): boolean => {
    const rules = validationRules[field as string] || [];
    const fieldErrors: string[] = [];
    
    for (const rule of rules) {
      const result = rule(form[field]);
      if (typeof result === 'string') {
        fieldErrors.push(result);
      } else if (result === false) {
        fieldErrors.push(t('validation.invalid'));
      }
      
      // Only show first error if not showing all errors
      if (fieldErrors.length > 0 && !showAllErrors) {
        break;
      }
    }
    
    errors[field] = fieldErrors;
    return fieldErrors.length === 0;
  };
  
  /**
   * Validate all fields
   */
  const validate = (): boolean => {
    let isValid = true;
    
    Object.keys(form).forEach((key) => {
      const fieldValid = validateField(key as keyof T);
      if (!fieldValid) {
        isValid = false;
      }
    });    
    return isValid;
  };
  
  /**
   * Reset form to initial values
   */
  const reset = () => {
    Object.assign(form, initialValues);
    Object.keys(errors).forEach((key) => {
      errors[key as keyof T] = [];
    });
    Object.keys(touched).forEach((key) => {
      touched[key as keyof T] = false;
    });
    isSubmitting.value = false;
    submitCount.value = 0;
    isValid.value = true;
    isDirty.value = false;
  };
  
  /**
   * Set form field value
   */
  const setFieldValue = <K extends keyof T>(field: K, value: T[K]) => {
    form[field] = value;
    isDirty.value = true;
    
    if (validateOnInput) {
      validateField(field);
    }
  };
  
  /**
   * Set form values
   */
  const setValues = (values: Partial<T>) => {
    Object.assign(form, values);
    isDirty.value = true;
  };
  
  /**
   * Set form errors
   */
  const setErrors = (newErrors: Record<string, string[]>) => {
    Object.keys(newErrors).forEach((key) => {
      if (key in errors) {
        errors[key as keyof T] = newErrors[key];
      }
    });
  };
  
  /**
   * Handle form submission
   */
  const handleSubmit = async (
    submitFn: (values: T) => Promise<ApiResponse<any> | void>,
    onSuccess?: (data: any) => void,
    onError?: (error: any) => void
  ) => {
    submitCount.value++;
    isSubmitting.value = true;
    
    // Validate form
    const isValid = validate();
    
    if (!isValid) {
      isSubmitting.value = false;
      return Promise.reject(new Error('Form validation failed'));
    }
    
    try {
      const result = await submitFn({ ...form });
      
      if (onSuccess) {
        onSuccess(result);
      }
      
      return result;
    } catch (error) {
      if (onError) {
        onError(error);
      }
      
      // Handle API validation errors
      if (error.response?.status === 422 && error.response?.data?.errors) {
        setErrors(error.response.data.errors);
      }
      
      throw error;
    } finally {
      isSubmitting.value = false;
    }
  };
  
  /**
   * Handle field blur
   */
  const handleBlur = (field: keyof T) => {
    touched[field] = true;
    
    if (validateOnBlur) {
      validateField(field);
    }
  };
  
  /**
   * Check if a field has an error
   */
  const hasError = (field: keyof T): boolean => {
    return errors[field] && errors[field].length > 0;
  };
  
  /**
   * Get error message for a field
   */
  const getError = (field: keyof T): string | null => {
    return errors[field]?.[0] || null;
  };
  
  /**
   * Check if a field has been touched
   */
  const isTouched = (field: keyof T): boolean => {
    return !!touched[field];
  };
  
  // Watch for changes to validate on input
  if (validateOnInput) {
    watch(form, () => {
      if (isDirty.value) {
        validate();
      }
    }, { deep: true });
  }
  
  // Watch for changes to update dirty state
  watch(() => ({ ...form }), (newValues, oldValues) => {
    if (JSON.stringify(newValues) !== JSON.stringify(initialValues)) {
      isDirty.value = true;
    } else {
      isDirty.value = false;
    }
  }, { deep: true });
  
  return {
    // Form state
    form,
    errors,
    touched,
    isSubmitting: computed(() => isSubmitting.value),
    isValid: computed(() => isValid.value),
    isDirty: computed(() => isDirty.value),
    submitCount: computed(() => submitCount.value),
    
    // Methods
    validate,
    validateField,
    reset,
    setFieldValue,
    setValues,
    setErrors,
    handleSubmit,
    handleBlur,
    hasError,
    getError,
    isTouched,
    
    // API request
    ...apiRequest,
  };
}

export type UseFormReturn<T> = ReturnType<typeof useForm<T>>;
