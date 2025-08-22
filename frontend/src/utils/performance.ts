/**
 * Frontend performance optimization utilities
 */

type CacheEntry<T = any> = {
  data: T
  timestamp: number
}

type PerformanceMetrics = {
  componentName: string
  loadTime: number
  renderTime?: number
  memoryUsage?: number
}

/**
 * Performance Optimizer class for frontend performance improvements
 */
export class PerformanceOptimizer<T = any> {
  private cache: Map<string, CacheEntry<T>>
  private cacheTimeout: number
  private performanceMetrics: PerformanceMetrics[]

  constructor(cacheTimeout = 5 * 60 * 1000) {
    this.cache = new Map()
    this.cacheTimeout = cacheTimeout
    this.performanceMetrics = []
  }

  // Lazy loading utility for Vue components
  static lazyLoad(componentPath: string) {
    return () => import(/* webpackChunkName: "[request]" */ `@/views/${componentPath}.vue`)
  }

  // Bundle splitting configuration
  static routeChunks = {
    // Core modules
    'general-ledger': () => import('@/modules/general-ledger/views/Dashboard.vue'),
    'accounts-payable': () => import('@/modules/accounts-payable/views/VendorsAdvancedView.vue'),
    'accounts-receivable': () => import('@/views/accounts-receivable/CustomersView.vue'),
    'budget': () => import('@/modules/budget/views/Dashboard.vue'),
    'reports': () => import('@/views/reports/ReportsView.vue'),
    
    // Admin modules
    'admin': () => import('@/views/admin/SuperAdminView.vue'),
    'settings': () => import('@/views/settings/CompanySettingsView.vue'),
    'rbac': () => import('@/views/rbac/RoleManagementView.vue'),
    
    // Secondary modules
    'cash': () => import('@/views/cash/CashManagementView.vue'),
    'assets': () => import('@/views/assets/FixedAssetsView.vue'),
    'payroll': () => import('@/views/payroll/PayrollView.vue'),
    'hrm': () => import('@/views/hrm/HRMView.vue'),
    'inventory': () => import('@/views/inventory/InventoryView.vue')
  }

  // Virtual scrolling configuration
  static virtualScrollConfig = {
    itemHeight: 50,
    bufferSize: 10,
    threshold: 100
  }

  /**
   * Debounce function for search inputs and other frequent events
   */
  static debounce<F extends (...args: any[]) => any>(
    func: F,
    delay: number
  ): (...args: Parameters<F>) => void {
    let timeoutId: NodeJS.Timeout | null = null
    
    return function(this: ThisParameterType<F>, ...args: Parameters<F>) {
      const context = this
      
      if (timeoutId) {
        clearTimeout(timeoutId)
      }
      
      timeoutId = setTimeout(() => {
        func.apply(context, args)
        timeoutId = null
      }, delay)
    }
  }

  /**
   * Throttle function for scroll and resize events
   */
  static throttle<F extends (...args: any[]) => any>(
    func: F,
    limit: number
  ): (...args: Parameters<F>) => void {
    let inThrottle = false
    
    return function(this: ThisParameterType<F>, ...args: Parameters<F>) {
      const context = this
      
      if (!inThrottle) {
        func.apply(context, args)
        inThrottle = true
        
        setTimeout(() => {
          inThrottle = false
        }, limit)
      }
    }
  }

  /**
   * Cache API responses or computed values
   */
  cacheResponse(key: string, data: T): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now()
    })
  }

  /**
   * Get cached response if available and not expired
   */
  getCachedResponse(key: string): T | null {
    const cached = this.cache.get(key)
    if (!cached) return null
    
    const isExpired = (Date.now() - cached.timestamp) > this.cacheTimeout
    if (isExpired) {
      this.cache.delete(key)
      return null
    }
    
    return cached.data
  }

  /**
   * Clear expired cache entries
   */
  cleanupExpiredCache(): void {
    const now = Date.now()
    
    for (const [key, entry] of this.cache.entries()) {
      if ((now - entry.timestamp) > this.cacheTimeout) {
        this.cache.delete(key)
      }
    }
  }

  /**
   * Track component performance metrics
   */
  trackComponentMetrics(metrics: Omit<PerformanceMetrics, 'timestamp'>): void {
    this.performanceMetrics.push({
      ...metrics,
      timestamp: Date.now()
    })
  }

  /**
   * Get performance metrics for analysis
   */
  getPerformanceMetrics(): PerformanceMetrics[] {
    return [...this.performanceMetrics]
  }
}

export const virtualScrollConfig = {
  itemHeight: 50,
  bufferSize: 10,
  threshold: 100
}

// Bundle splitting configuration
export const routeChunks = {
  // Core modules
  'general-ledger': () => import('@/modules/general-ledger/views/Dashboard.vue'),
  'accounts-payable': () => import('@/modules/accounts-payable/views/VendorsAdvancedView.vue'),
  'accounts-receivable': () => import('@/views/accounts-receivable/CustomersView.vue'),
  'budget': () => import('@/modules/budget/views/Dashboard.vue'),
  'reports': () => import('@/views/reports/ReportsView.vue'),
  
  // Admin modules
  'admin': () => import('@/views/admin/SuperAdminView.vue'),
  'settings': () => import('@/views/settings/CompanySettingsView.vue'),
  'rbac': () => import('@/views/rbac/RoleManagementView.vue'),
  
  // Secondary modules
  'cash': () => import('@/views/cash/CashManagementView.vue'),
  'assets': () => import('@/views/assets/FixedAssetsView.vue'),
  'payroll': () => import('@/views/payroll/PayrollView.vue'),
  'hrm': () => import('@/views/hrm/HRMView.vue'),
  'inventory': () => import('@/views/inventory/InventoryView.vue')
}

// Debounce utility for search inputs
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  delay: number
): ((...args: Parameters<T>) => void) => {
  let timeoutId: NodeJS.Timeout
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => func(...args), delay)
  }
}

// Memoization for expensive computations
export const memoize = <T extends (...args: any[]) => any>(fn: T): T => {
  const cache = new Map()
  return ((...args: any[]) => {
    const key = JSON.stringify(args)
    if (cache.has(key)) {
      return cache.get(key)
    }
    const result = fn(...args)
    cache.set(key, result)
    return result
  }) as T
}

// Image lazy loading
export const lazyImage = {
  mounted(el: HTMLImageElement) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target as HTMLImageElement
          img.src = img.dataset.src || ''
          observer.unobserve(img)
        }
      })
    })
    observer.observe(el)
  }
}