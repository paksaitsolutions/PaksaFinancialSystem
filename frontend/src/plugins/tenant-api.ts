import axios from 'axios'
import { useTenantStore } from '@/stores/tenant'

// Create tenant-aware axios instance
export const tenantApi = axios.create({
  baseURL: '/api/v1'
})

// Request interceptor to add tenant header
tenantApi.interceptors.request.use((config) => {
  const tenantStore = useTenantStore()
  
  if (tenantStore.tenantId) {
    config.headers['X-Tenant-ID'] = tenantStore.tenantId
  }
  
  return config
})

// Response interceptor for tenant-specific error handling
tenantApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 403 && error.response?.data?.detail?.includes('tenant')) {
      // Tenant access denied - redirect to company selection
      const tenantStore = useTenantStore()
      tenantStore.logout()
      window.location.href = '/company-select'
    }
    return Promise.reject(error)
  }
)

// Feature flag checker
export const hasFeature = (feature: string): boolean => {
  const tenantStore = useTenantStore()
  return tenantStore.hasFeature(feature)
}

// Tenant-aware API methods
export const tenantApiMethods = {
  get: (url: string, config?: any) => tenantApi.get(url, config),
  post: (url: string, data?: any, config?: any) => tenantApi.post(url, data, config),
  put: (url: string, data?: any, config?: any) => tenantApi.put(url, data, config),
  delete: (url: string, config?: any) => tenantApi.delete(url, config),
  
  // Tenant-specific endpoints
  getTenantInfo: () => tenantApi.get('/tenant/info'),
  getTenantUsage: () => tenantApi.get('/tenant/usage'),
  trackApiUsage: (endpoint: string) => tenantApi.post('/tenant/track-api', { endpoint })
}