import axios, { AxiosRequestConfig, AxiosResponse } from 'axios'
import { cache } from './cache'

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

    // Response interceptor
    this.instance.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          window.location.href = '/auth/login'
        }
        return Promise.reject(error)
      }
    )
  }

  // GET with caching
  async get<T = any>(url: string, config?: AxiosRequestConfig & { cache?: boolean; ttl?: number }): Promise<AxiosResponse<T>> {
    const { cache: useCache = false, ttl = 5 * 60 * 1000, ...axiosConfig } = config || {}
    
    if (useCache) {
      const cacheKey = `GET_${url}_${JSON.stringify(axiosConfig)}`
      return cache.getOrFetch(cacheKey, () => this.instance.get<T>(url, axiosConfig), ttl)
    }
    
    return this.instance.get<T>(url, axiosConfig)
  }

  // POST with cache invalidation
  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    this.clearRelatedCache(url)
    return this.instance.post<T>(url, data, config)
  }

  // PUT with cache invalidation
  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    this.clearRelatedCache(url)
    return this.instance.put<T>(url, data, config)
  }

  // DELETE with cache invalidation
  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    this.clearRelatedCache(url)
    return this.instance.delete<T>(url, config)
  }

  // Request deduplication
  async getWithDeduplication<T = any>(url: string, config?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    const key = `${url}_${JSON.stringify(config)}`
    
    if (this.requestCache.has(key)) {
      return this.requestCache.get(key)!
    }
    
    const request = this.instance.get<T>(url, config)
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
}

export const apiClient = new ApiClient()

export default apiClient