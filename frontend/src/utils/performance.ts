/**
 * Frontend performance optimization utilities
 */

// Lazy loading utility for Vue components
export const lazyLoad = (componentPath: string) => {
  return () => import(componentPath)
}

// Virtual scrolling configuration
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