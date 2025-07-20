import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router';
import { authRoutes, glRoutes, apRoutes, arRoutes, payrollRoutes, cashRoutes, assetsRoutes, taxRoutes, rootRoute, dashboardRoutes } from './modules/allRoutes';
import { useAuthStore } from '@/modules/auth/store';

// Function to load route component with error handling
const loadView = (view: string) => {
  return () => {
    return import(/* webpackChunkName: "view-[request]" */ `@/views/${view}.vue`)
      .catch(() => import('@/views/UnderConstruction.vue'));
  };
};

// Base routes that don't require authentication
const publicRoutes: RouteRecordRaw[] = [
  // Root route
  rootRoute,
  
  // Dashboard route
  dashboardRoutes,
  
  // Module routes
  glRoutes,
  apRoutes,
  arRoutes,
  payrollRoutes,
  cashRoutes,
  assetsRoutes,
  taxRoutes,
  
  // Auth routes
  authRoutes,
  
  // 404 page for routes that don't match
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFound.vue'),
    meta: { title: 'Page Not Found' }
  }
];

// Create router instance
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: publicRoutes,
  scrollBehavior(to, from, savedPosition) {
    // Scroll to top on route change
    if (savedPosition) {
      return savedPosition;
    } else {
      return { top: 0 };
    }
  }
});

// Global navigation guards
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();
  const isAuthenticated = authStore.isAuthenticated;
  
  // Set page title
  const title = to.meta.title as string || 'Paksa Financial System';
  document.title = `${title} | PFS`;

  // Handle root path redirect (handled by the root route)
  if (to.path === '/') {
    next();
    return;
  }

  // Check if route requires authentication
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!isAuthenticated) {
      // Store the attempted URL for redirecting after login
      const redirectPath = to.fullPath === '/' ? undefined : to.fullPath;
      next({ 
        name: 'Login',
        query: { redirect: redirectPath }
      });
      return;
    }
    
    // Check for required permissions
    if (to.meta.permissions) {
      const requiredPermissions = Array.isArray(to.meta.permissions) 
        ? to.meta.permissions 
        : [to.meta.permissions];
      
      const hasPermission = authStore.hasAnyPermission?.(requiredPermissions) || false;
      
      if (!hasPermission) {
        // Redirect to dashboard if unauthorized for the requested route
        next({ name: 'Dashboard' });
        return;
      }
    }
  }

  // Redirect to dashboard if already authenticated and trying to access auth pages
  if (to.matched.some(record => record.meta.requiresGuest) && isAuthenticated) {
    next({ name: 'Dashboard' });
    return;
  }

  // Continue with navigation
  next();
});

// Handle navigation errors
router.onError((error) => {
  console.error('Router error:', error);
  // You can add error tracking here (e.g., Sentry, LogRocket)
});

export default router;