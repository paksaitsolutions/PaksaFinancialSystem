/**
 * Common types used across the application
 */

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ApiError {
  message: string;
  code?: string;
  details?: Record<string, any>;
}

export interface SortOption {
  field: string;
  direction: 'asc' | 'desc';
}

export interface FilterOption {
  field: string;
  operator: 'eq' | 'neq' | 'gt' | 'gte' | 'lt' | 'lte' | 'like' | 'in' | 'is_null';
  value: any;
}

export interface ListQueryParams {
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_direction?: 'asc' | 'desc';
  filters?: FilterOption[];
  search?: string;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
  errors?: Record<string, string[]>;
}

export interface SelectOption<T = string> {
  value: T;
  label: string;
  disabled?: boolean;
  [key: string]: any;
}

export interface KeyValuePair<T = any> {
  [key: string]: T;
}

export type UUID = string;

export type Nullable<T> = T | null | undefined;
