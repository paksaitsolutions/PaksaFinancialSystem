import type { Router } from 'vue-router';
import { useUIStore } from '@/stores/ui';

export function setupNavigationGuards(router: Router) {
  router.beforeEach((to, from, next) => {
    const uiStore = useUIStore();
    
    // Set loading state
    uiStore.setGlobalLoading(true);
    
    // Update current module based on route
    const module = to.path.split('/')[1] || 'dashboard';
    uiStore.setCurrentModule(module);
    
    // Check authentication if required
    if (to.meta.requiresAuth) {
      // TODO: Check authentication status
      // For now, allow all routes
    }
    
    next();
  });

  router.afterEach(() => {
    const uiStore = useUIStore();
    uiStore.setGlobalLoading(false);
  });

  router.onError((error) => {
    const uiStore = useUIStore();
    uiStore.setGlobalLoading(false);
    
    uiStore.addNotification({
      type: 'error',
      title: 'Navigation Error',
      message: 'Failed to navigate to the requested page'
    });
    
    console.error('Router error:', error);
  });
}