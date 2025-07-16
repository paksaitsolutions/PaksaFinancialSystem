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

router.beforeEach(async (to, from, next) => {
  const appName = 'Paksa Financial System';
  // Set document title
  document.title = to.meta.title ? `${to.meta.title} | ${appName}` : appName;
  
  const authStore = useAuthStore();
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
  const isAuthenticated = authStore.isAuthenticated;

  // If route requires auth and user is not logged in, redirect to login
  if (requiresAuth && !isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } });
    return;
  }

  // If user is logged in and tries to access auth pages, redirect to home
  const authPages = ['login', 'register', 'forgot-password'];
  if (isAuthenticated && authPages.includes(String(to.name))) {
    next({ name: 'dashboard' });
    return;
  }

  // Check route permissions if any
  if (to.meta.permissions) {
    const hasPermission = (to.meta.permissions as string[]).some(permission => 
      authStore.hasPermission(permission)
    );
    
    if (!hasPermission) {
      next({ name: 'unauthorized' });
      return;
    }
  }

  // Continue with navigation
  next();
});

export default router;