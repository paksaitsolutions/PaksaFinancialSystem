/**
 * Common TypeScript types for the application
 */

// Base entity interface
export interface BaseEntity {
  id: string
  createdAt: string
  updatedAt: string
  tenantId?: string
}

// API response wrapper
export interface ApiResponse<T> {
  data: T
  message?: string
  success: boolean
}

// Pagination interface
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  limit: number
  hasNext: boolean
  hasPrev: boolean
}

// Form validation
export interface ValidationRule {
  required?: boolean
  minLength?: number
  maxLength?: number
  pattern?: RegExp
  custom?: (value: any) => boolean | string
}

// Component props with validation
export interface BaseProps {
  loading?: boolean
  disabled?: boolean
  error?: string
}

// State management types
export interface LoadingState {
  isLoading: boolean
  error: string | null
}

// User interface
export interface User extends BaseEntity {
  email: string
  firstName: string
  lastName: string
  role: string
  isActive: boolean
}

// Company/Tenant interface
export interface Company extends BaseEntity {
  name: string
  code: string
  address: string
  phone: string
  email: string
  isActive: boolean
}