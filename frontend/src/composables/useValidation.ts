/**
 * Component prop validation composable
 */
import { computed, ref } from 'vue'
import type { ValidationRule } from '@/types/common'

export function useValidation() {
  const errors = ref<Record<string, string>>({})
  
  const validateField = (value: any, rules: ValidationRule[], fieldName: string): boolean => {
    errors.value[fieldName] = ''
    
    for (const rule of rules) {
      if (rule.required && (!value || value === '')) {
        errors.value[fieldName] = `${fieldName} is required`
        return false
      }
      
      if (rule.minLength && value && value.length < rule.minLength) {
        errors.value[fieldName] = `${fieldName} must be at least ${rule.minLength} characters`
        return false
      }
      
      if (rule.maxLength && value && value.length > rule.maxLength) {
        errors.value[fieldName] = `${fieldName} must be no more than ${rule.maxLength} characters`
        return false
      }
      
      if (rule.pattern && value && !rule.pattern.test(value)) {
        errors.value[fieldName] = `${fieldName} format is invalid`
        return false
      }
      
      if (rule.custom && value) {
        const result = rule.custom(value)
        if (result !== true) {
          errors.value[fieldName] = typeof result === 'string' ? result : `${fieldName} is invalid`
          return false
        }
      }
    }
    
    return true
  }
  
  const validateForm = (formData: Record<string, any>, validationRules: Record<string, ValidationRule[]>): boolean => {
    let isValid = true
    
    for (const [fieldName, rules] of Object.entries(validationRules)) {
      const fieldValid = validateField(formData[fieldName], rules, fieldName)
      if (!fieldValid) {
        isValid = false
      }
    }
    
    return isValid
  }
  
  const clearErrors = () => {
    errors.value = {}
  }
  
  const hasErrors = computed(() => Object.keys(errors.value).some(key => errors.value[key]))
  
  return {
    errors,
    validateField,
    validateForm,
    clearErrors,
    hasErrors
  }
}