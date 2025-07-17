import { createRouter, createWebHistory } from 'vue-router';
import { allRoutes } from './modules/allRoutes';
import { useAuthStore, setRouter } from '@/stores/auth';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: allRoutes,
  scrollBehavior(to, from, savedPosition) {
    return savedPosition || { top: 0 };
  },
});

// Initialize router in auth store
setRouter(router);

// Type guard to check if meta has permissions
const hasPermissions = (meta: any): meta is { permissions: string[] } => {
  return Array.isArray(meta?.permissions);
};

router.beforeEach(async (to, _, next) => {
  const appName = 'Paksa Financial System';
  // Set document title
  document.title = to.meta.title ? `${to.meta.title} | ${appName}` : appName;
  
  const authStore = useAuthStore();
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
  const requiresGuest = to.matched.some(record => record.meta.requiresGuest);
  const isAuthenticated = authStore.isAuthenticated;

  // If route requires guest but user is authenticated, redirect to home
  if (requiresGuest && isAuthenticated) {
    next({ name: 'Home' });
    return;
  }

  // If route requires auth and user is not logged in, redirect to login
  if (requiresAuth && !isAuthenticated) {
    next({ 
      name: 'Login',
      query: to.fullPath !== '/' ? { redirect: to.fullPath } : undefined
    });
    return;
  }

  // Check route permissions if any
  if (hasPermissions(to.meta)) {
    const hasPermission = to.meta.permissions.some(permission => 
      authStore.hasPermission(permission)
    );
    
    if (!hasPermission) {
      next({ name: 'NotFound' });
      return;
    }
  }

  // Continue with navigation
  next();
});

export default router;