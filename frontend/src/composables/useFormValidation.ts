import { ref, computed } from 'vue';

export interface ValidationRule {
  (value: any, ...args: any[]): boolean | string;
}

export interface ValidationRules {
  [key: string]: ValidationRule;
}

export default function useFormValidation() {
  const validationRules = {
    required: (v: any) => !!v || 'This field is required',
    email: (v: string) => !v || /.+@.+\..+/.test(v) || 'Email must be valid',
    minLength: (v: string, length: number) => !v || v.length >= length || `Must be at least ${length} characters`,
    passwordMatch: (v: string, match: string) => !v || v === match || 'Passwords do not match',
    phone: (v: string) => !v || /^\+?[0-9]{10,15}$/.test(v) || 'Phone number must be valid',
    numeric: (v: string) => !v || /^[0-9]+$/.test(v) || 'Must contain only numbers',
    alphanumeric: (v: string) => !v || /^[a-zA-Z0-9]+$/.test(v) || 'Must contain only letters and numbers'
  } as const;

  const validate = (rules: Array<ValidationRule | string>, value: any, ...args: any[]): true | string => {
    for (const rule of rules) {
      const result = typeof rule === 'function' 
        ? rule(value, ...args)
        : validationRules[rule as keyof typeof validationRules](value, ...args);
        
      if (result !== true) return result as string;
    }
    return true;
  };

  return {
    validationRules,
    validate
  };
}

export type FormValidation = ReturnType<typeof useFormValidation>;
