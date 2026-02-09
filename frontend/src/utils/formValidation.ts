export type ValidationRule<T = any> = {
  label?: string;
  required?: boolean;
  min?: number;
  max?: number;
  pattern?: RegExp;
  custom?: (value: T, data: Record<string, any>) => string | null;
};

export type ValidationSchema<T extends Record<string, any>> = {
  [K in keyof T]?: ValidationRule<T[K]>;
};

export type ValidationResult = {
  isValid: boolean;
  errors: Record<string, string>;
};

const isEmptyValue = (value: unknown): boolean => {
  if (value === null || value === undefined) return true;
  if (typeof value === 'string') return value.trim().length === 0;
  if (Array.isArray(value)) return value.length === 0;
  return false;
};

const normalizeLabel = (key: string, rule?: ValidationRule): string => {
  if (rule?.label) return rule.label;
  return key
    .replace(/_/g, ' ')
    .replace(/([a-z])([A-Z])/g, '$1 $2')
    .replace(/\b\w/g, (char) => char.toUpperCase());
};

export const validateSchema = <T extends Record<string, any>>(
  data: T,
  schema: ValidationSchema<T>
): ValidationResult => {
  const errors: Record<string, string> = {};

  Object.entries(schema).forEach(([key, rule]) => {
    if (!rule) return;
    const value = data[key as keyof T];
    const label = normalizeLabel(key, rule);

    if (rule.required && isEmptyValue(value)) {
      errors[key] = `${label} is required`;
      return;
    }

    if (typeof value === 'string') {
      if (rule.min !== undefined && value.trim().length < rule.min) {
        errors[key] = `${label} must be at least ${rule.min} characters`;
        return;
      }
      if (rule.max !== undefined && value.trim().length > rule.max) {
        errors[key] = `${label} must be ${rule.max} characters or less`;
        return;
      }
      if (rule.pattern && !rule.pattern.test(value)) {
        errors[key] = `${label} is invalid`;
        return;
      }
    }

    if (typeof value === 'number') {
      if (rule.min !== undefined && value < rule.min) {
        errors[key] = `${label} must be at least ${rule.min}`;
        return;
      }
      if (rule.max !== undefined && value > rule.max) {
        errors[key] = `${label} must be ${rule.max} or less`;
        return;
      }
    }

    if (rule.custom) {
      const customMessage = rule.custom(value, data);
      if (customMessage) {
        errors[key] = customMessage;
      }
    }
  });

  return { isValid: Object.keys(errors).length === 0, errors };
};
