/**
 * Standardized API response types for consistent handling across the frontend
 */

export interface ApiResponse<T = any> {
  status: 'success' | 'error'
  message?: string
  data?: T
  meta?: Record<string, any>
}

export interface PaginationMeta {
  total: number
  page: number
  page_size: number
  pages: number
  has_next: boolean
  has_prev: boolean
}

export interface PaginatedResponse<T = any> extends ApiResponse<T[]> {
  pagination: PaginationMeta
}

export interface ErrorResponse {
  status: 'error'
  message: string
  error_code?: string
  details?: any
}

export interface PaginationParams {
  page?: number
  page_size?: number
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}

// Helper type for extracting data from API responses
export type ApiData<T> = T extends ApiResponse<infer U> ? U : never
export type PaginatedData<T> = T extends PaginatedResponse<infer U> ? U : never