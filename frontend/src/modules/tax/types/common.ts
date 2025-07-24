export type UUID = string;
export type Nullable<T> = T | null;

export interface BaseEntity {
  id: UUID;
  created_at: string;
  updated_at: string;
  is_active: boolean;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: 'success' | 'error';
}

export interface FilterOptions {
  search?: string;
  sort_by?: string;
  sort_direction?: 'asc' | 'desc';
  page?: number;
  page_size?: number;
}