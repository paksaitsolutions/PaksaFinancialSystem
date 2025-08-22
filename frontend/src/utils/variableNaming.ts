/**
 * Variable naming conventions for Vue components
 * Helps prevent duplicate variable declarations and improves TypeScript scoping
 */

// Common loading state patterns
export const LoadingStates = {
  // General loading
  LOADING: 'isLoading',
  SAVING: 'isSaving',
  DELETING: 'isDeleting',
  SUBMITTING: 'isSubmitting',
  
  // Specific operations
  FETCHING_DATA: 'isFetchingData',
  LOADING_ITEMS: 'isLoadingItems',
  PROCESSING: 'isProcessing',
  VALIDATING: 'isValidating',
  
  // Component specific
  MODAL_LOADING: 'isModalLoading',
  TABLE_LOADING: 'isTableLoading',
  FORM_LOADING: 'isFormLoading'
} as const

// Common error state patterns
export const ErrorStates = {
  ERROR: 'error',
  FORM_ERROR: 'formError',
  VALIDATION_ERROR: 'validationError',
  API_ERROR: 'apiError',
  NETWORK_ERROR: 'networkError'
} as const

// Common data state patterns
export const DataStates = {
  DATA: 'data',
  ITEMS: 'items',
  RECORDS: 'records',
  RESULTS: 'results',
  RESPONSE: 'response'
} as const

// TypeScript utility types for better scoping
export type LoadingState = typeof LoadingStates[keyof typeof LoadingStates]
export type ErrorState = typeof ErrorStates[keyof typeof ErrorStates]
export type DataState = typeof DataStates[keyof typeof DataStates]

// Helper function to create scoped variable names
export const createScopedName = (prefix: string, baseName: string): string => {
  return `${prefix}${baseName.charAt(0).toUpperCase()}${baseName.slice(1)}`
}

// Example usage:
// const userLoading = ref(false) // instead of loading
// const productError = ref('') // instead of error
// const orderData = ref([]) // instead of data