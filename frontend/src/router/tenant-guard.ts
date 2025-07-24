import { NavigationGuardNext, RouteLocationNormalized } from 'vue-router'
import { useTenantStore } from '@/stores/tenant'

export const tenantGuard = (
  to: RouteLocationNormalized,
  from: RouteLocationNormalized,
  next: NavigationGuardNext
) => {
  const tenantStore = useTenantStore()
  
  // Skip tenant check for auth routes
  if (to.path.startsWith('/auth') || to.path === '/company-select') {
    next()
    return
  }
  
  // Check if user has selected a company
  if (!tenantStore.currentCompany) {
    next('/company-select')
    return
  }
  
  // Check if route requires specific features
  if (to.meta?.requiredFeature) {
    const hasFeature = tenantStore.hasFeature(to.meta.requiredFeature as string)
    if (!hasFeature) {
      next('/unauthorized')
      return
    }
  }
  
  next()
}

export const setupTenantRouting = (router: any) => {
  router.beforeEach(tenantGuard)
  
  // Add tenant-specific routes
  router.addRoute({
    path: '/company-select',
    name: 'CompanySelect',
    component: () => import('@/views/tenant/CompanySelectView.vue')
  })
  
  router.addRoute({
    path: '/unauthorized',
    name: 'Unauthorized',
    component: () => import('@/views/tenant/UnauthorizedView.vue')
  })
}