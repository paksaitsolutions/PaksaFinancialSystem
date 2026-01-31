import axios, { AxiosRequestConfig, AxiosResponse } from 'axios'
import { cache } from './cache'
import { handleApiError } from './api-error-handler'
import type { ApiResponse, PaginatedResponse, PaginationParams } from '@/types/api'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

class ApiClient {
  private instance = axios.create({
    baseURL: API_BASE_URL,
    timeout: 30000,
    headers: {
      'Content-Type': 'application/json',
    },
  })
  
  private requestCache = new Map<string, Promise<any>>()

  constructor() {
    this.setupInterceptors()
  }

  private setupInterceptors() {
    // Request interceptor
    this.instance.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // Response interceptor with centralized error handling
    this.instance.interceptors.response.use(
      (response) => response,
      (error) => {
        // Use centralized error handler
        handleApiError(error)
        return Promise.reject(error)
      }
    )
  }

  // GET with caching and standardized response handling
  async get<T = any>(
    url: string, 
    config?: AxiosRequestConfig & { cache?: boolean; ttl?: number }
  ): Promise<AxiosResponse<ApiResponse<T>>> {
    const { cache: useCache = false, ttl = 5 * 60 * 1000, ...axiosConfig } = config || {}
    
    if (useCache) {
      const cacheKey = `GET_${url}_${JSON.stringify(axiosConfig)}`
      return cache.getOrFetch(cacheKey, () => this.instance.get<ApiResponse<T>>(url, axiosConfig), ttl)
    }
    
    return this.instance.get<ApiResponse<T>>(url, axiosConfig)
  }

  // GET with pagination support
  async getPaginated<T = any>(
    url: string,
    params?: PaginationParams,
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<PaginatedResponse<T>>> {
    const queryParams = new URLSearchParams()
    
    if (params?.page) queryParams.set('page', params.page.toString())
    if (params?.page_size) queryParams.set('page_size', params.page_size.toString())
    if (params?.sort_by) queryParams.set('sort_by', params.sort_by)
    if (params?.sort_order) queryParams.set('sort_order', params.sort_order)
    
    const fullUrl = queryParams.toString() ? `${url}?${queryParams}` : url
    return this.instance.get<PaginatedResponse<T>>(fullUrl, config)
  }

  // POST with cache invalidation and standardized response
  async post<T = any>(
    url: string, 
    data?: any, 
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<ApiResponse<T>>> {
    this.clearRelatedCache(url)
    return this.instance.post<ApiResponse<T>>(url, data, config)
  }

  // PUT with cache invalidation and standardized response
  async put<T = any>(
    url: string, 
    data?: any, 
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<ApiResponse<T>>> {
    this.clearRelatedCache(url)
    return this.instance.put<ApiResponse<T>>(url, data, config)
  }

  // DELETE with cache invalidation and standardized response
  async delete<T = any>(
    url: string, 
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<ApiResponse<T>>> {
    this.clearRelatedCache(url)
    return this.instance.delete<ApiResponse<T>>(url, config)
  }

  // Request deduplication with standardized response
  async getWithDeduplication<T = any>(
    url: string, 
    config?: AxiosRequestConfig
  ): Promise<AxiosResponse<ApiResponse<T>>> {
    const key = `${url}_${JSON.stringify(config)}`
    
    if (this.requestCache.has(key)) {
      return this.requestCache.get(key)!
    }
    
    const request = this.instance.get<ApiResponse<T>>(url, config)
    this.requestCache.set(key, request)
    
    try {
      return await request
    } finally {
      this.requestCache.delete(key)
    }
  }

  private clearRelatedCache(url: string): void {
    cache.clear() // Simple cache invalidation
  }

  // Prefetch data
  async prefetch(urls: string[]): Promise<void> {
    const promises = urls.map(url => 
      this.get(url, { cache: true }).catch(() => null)
    )
    await Promise.all(promises)
  }

  clearCache(): void {
    cache.clear()
  }

  // Helper methods for extracting data from standardized responses
  extractData<T>(response: AxiosResponse<ApiResponse<T>>): T | undefined {
    return response.data.data
  }

  extractPaginatedData<T>(response: AxiosResponse<PaginatedResponse<T>>): {
    data: T[]
    pagination: PaginatedResponse<T>['pagination']
    meta?: Record<string, any>
  } {
    return {
      data: response.data.data || [],
      pagination: response.data.pagination,
      meta: response.data.meta
    }
  }
}

export const apiClient = new ApiClient()

export default apiClient