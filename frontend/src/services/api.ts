/**
 * API service layer for backend integration
 */
import axios, { AxiosInstance, AxiosResponse } from 'axios'
import type { ApiResponse, PaginatedResponse } from '@/types/common'

class ApiService {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json'
      }
    })

    // Request interceptor for auth
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    })

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('access_token')
          window.location.href = '/auth/login'
        }
        return Promise.reject(error)
      }
    )
  }

  async get<T>(url: string, params?: any): Promise<T> {
    const response: AxiosResponse<T> = await this.client.get(url, { params })
    return response.data
  }

  async post<T>(url: string, data?: any): Promise<T> {
    const response: AxiosResponse<T> = await this.client.post(url, data)
    return response.data
  }

  async put<T>(url: string, data?: any): Promise<T> {
    const response: AxiosResponse<T> = await this.client.put(url, data)
    return response.data
  }

  async delete<T>(url: string): Promise<T> {
    const response: AxiosResponse<T> = await this.client.delete(url)
    return response.data
  }
}

export const apiService = new ApiService()

// Specific API endpoints
export const accountsApi = {
  getAll: (params?: any) => apiService.get<PaginatedResponse<any>>('/gl/accounts', params),
  getById: (id: string) => apiService.get<ApiResponse<any>>(`/gl/accounts/${id}`),
  create: (data: any) => apiService.post<ApiResponse<any>>('/gl/accounts', data),
  update: (id: string, data: any) => apiService.put<ApiResponse<any>>(`/gl/accounts/${id}`, data),
  delete: (id: string) => apiService.delete<ApiResponse<any>>(`/gl/accounts/${id}`)
}

export const journalEntriesApi = {
  getAll: (params?: any) => apiService.get<PaginatedResponse<any>>('/gl/journal-entries', params),
  getById: (id: string) => apiService.get<ApiResponse<any>>(`/gl/journal-entries/${id}`),
  create: (data: any) => apiService.post<ApiResponse<any>>('/gl/journal-entries', data),
  update: (id: string, data: any) => apiService.put<ApiResponse<any>>(`/gl/journal-entries/${id}`, data),
  delete: (id: string) => apiService.delete<ApiResponse<any>>(`/gl/journal-entries/${id}`)
}

export const vendorsApi = {
  getAll: (params?: any) => apiService.get<PaginatedResponse<any>>('/ap/vendors', params),
  getById: (id: string) => apiService.get<ApiResponse<any>>(`/ap/vendors/${id}`),
  create: (data: any) => apiService.post<ApiResponse<any>>('/ap/vendors', data),
  update: (id: string, data: any) => apiService.put<ApiResponse<any>>(`/ap/vendors/${id}`, data),
  delete: (id: string) => apiService.delete<ApiResponse<any>>(`/ap/vendors/${id}`)
}

export const budgetApi = {
  getAll: (params?: any) => apiService.get<PaginatedResponse<any>>('/budget/budgets', params),
  getById: (id: string) => apiService.get<ApiResponse<any>>(`/budget/budgets/${id}`),
  create: (data: any) => apiService.post<ApiResponse<any>>('/budget/budgets', data),
  update: (id: string, data: any) => apiService.put<ApiResponse<any>>(`/budget/budgets/${id}`, data),
  delete: (id: string) => apiService.delete<ApiResponse<any>>(`/budget/budgets/${id}`)
}