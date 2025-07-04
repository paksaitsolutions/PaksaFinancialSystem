import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useAppStore } from '@/stores/app';
import { nextTick } from 'vue';
import { filterDevRoutes } from '@/utils/routerUtils';

// Base routes configuration
const baseRoutes: RouteRecordRaw[] = [
  // Auth routes
  {
    path: '/auth',
    name: 'auth',
    component: () => import('@/layouts/AuthLayout.vue'),
    meta: { requiresAuth: false },
    children: [
      {
        path: 'login',
        name: 'login',
        component: () => import('@/views/auth/LoginView.vue'),
        meta: { title: 'Login' }
      },
      {
        path: 'forgot-password',
        name: 'forgot-password',
        component: () => import('@/views/auth/ForgotPasswordView.vue'),
        meta: { title: 'Forgot Password' }
      },
      {
        path: 'reset-password',
        name: 'reset-password',
        component: () => import('@/views/auth/ResetPasswordView.vue'),
        meta: { title: 'Reset Password' }
      }
    ]
  },
  
  // Main app routes
  {
    path: '/',
    component: () => import('@/layouts/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      // Dashboard
      {
        path: '',
        name: 'dashboard',
        component: () => import('@/views/dashboard/DashboardView.vue'),
        meta: { 
          title: 'Dashboard',
          icon: 'pi pi-fw pi-home'
        }
      },
      
      // Compliance & Security
      {
        path: 'compliance',
        name: 'compliance',
        meta: { 
          title: 'Compliance & Security',
          icon: 'pi pi-fw pi-shield',
          permission: 'view_compliance_dashboard'
        },
        children: [
          // Dashboard
          {
            path: '',
            name: 'compliance-dashboard',
            component: () => import('@/views/compliance/DashboardView.vue'),
            meta: { 
              title: 'Compliance Dashboard',
              breadcrumb: 'Dashboard'
            }
          },
          
          // Audit Logs
          {
            path: 'audit-logs',
            name: 'audit-logs',
            component: () => import('@/views/compliance/audit/LogsView.vue'),
            meta: { 
              title: 'Audit Logs',
              breadcrumb: 'Audit Logs',
              permission: 'view_audit_logs'
            }
          },
          
          // Data Subject Requests
          {
            path: 'data-subject-requests',
            name: 'data-subject-requests',
            component: () => import('@/views/compliance/data-subject/RequestsView.vue'),
            meta: { 
              title: 'Data Subject Requests',
              breadcrumb: 'Data Subject Requests',
              permission: 'manage_data_subject_requests'
            }
          },
          
          // Security Policies
          {
            path: 'security/policies',
            name: 'security-policies',
            component: () => import('@/views/compliance/security/PoliciesView.vue'),
            meta: { 
              title: 'Security Policies',
              breadcrumb: 'Security Policies',
              permission: 'manage_security_policies'
            }
          },
          
          // Security Events
          {
            path: 'security/events',
            name: 'security-events',
            component: () => import('@/views/compliance/security/EventsView.vue'),
            meta: { 
              title: 'Security Events',
              breadcrumb: 'Security Events',
              permission: 'view_security_events'
            }
          },
          
          // Encryption Keys
          {
            path: 'security/encryption-keys',
            name: 'encryption-keys',
            component: () => import('@/views/compliance/security/EncryptionKeysView.vue'),
            meta: { 
              title: 'Encryption Keys',
              breadcrumb: 'Encryption Keys',
              permission: 'manage_encryption_keys'
            }
          },
          
          // Settings
          {
            path: 'settings',
            name: 'compliance-settings',
            component: () => import('@/views/compliance/SettingsView.vue'),
            meta: { 
              title: 'Compliance Settings',
              breadcrumb: 'Settings',
              permission: 'manage_compliance_settings'
            }
          }
        ]
      },
      
      // Error routes
      {
        path: '/error',
        name: 'error',
        component: () => import('@/layouts/ErrorLayout.vue'),
        meta: { requiresAuth: false },
        children: [
          {
            path: 'not-found',
            name: 'not-found',
            component: () => import('@/views/errors/PageNotFoundView.vue'),
            meta: { title: 'Page Not Found' }
          },
          {
            path: 'access-denied',
            name: 'access-denied',
            component: () => import('@/views/errors/AccessDeniedView.vue'),
            meta: { title: 'Access Denied' }
          }
        ]
      },
      
      // Catch-all route for 404
      {
        path: '/:pathMatch(.*)*',
        redirect: '/error/not-found'
      }
    ]
  }
];

// Development-only routes
const devRoutes: RouteRecordRaw[] = [
  // Test Routes (Development Only)
  {
    path: '/test',
    name: 'test',
    component: () => import('@/layouts/AppLayout.vue'),
    meta: { 
      requiresAuth: true,
      permission: 'manage_encryption_keys',
      devOnly: true
    },
    children: [
      // Encryption Test
      {
        path: 'encryption',
        name: 'test-encryption',
        component: () => import('@/views/compliance/security/test/EncryptionTestView.vue'),
        meta: { 
          title: 'Encryption Test',
          breadcrumb: 'Encryption Test',
          permission: 'manage_encryption_keys',
          devOnly: true
        }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: { name: 'not-found' }
  }
];

// Combine all routes and filter out dev routes in production
const routes = filterDevRoutes([...baseRoutes, ...devRoutes]);

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition;
    } else {
      return { top: 0 };
    }
  }
});

// Navigation guard
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();
  const appStore = useAppStore();
  
  // Set loading
  appStore.setLoading(true);
  
  // Set page title if available
  const title = to.meta.title as string | undefined;
  if (title) {
    document.title = `${title} | ${import.meta.env.VITE_APP_NAME || 'Paksa Financial System'}`;
  }
  
  // Check if the route requires authentication
  if (to.matched.some(record => record.meta.requiresAuth)) {
    // Check if user is authenticated
    if (!authStore.isAuthenticated) {
      // Redirect to login if not authenticated
      next({ 
        name: 'login',
        query: { redirect: to.fullPath }
      });
      return;
    }
    
    // Check permissions if required
    const requiredPermission = to.meta.permission as string | undefined;
    if (requiredPermission && !authStore.hasPermission(requiredPermission)) {
      next({ name: 'access-denied' });
      return;
    }
  }
  
  // If user is authenticated and trying to access auth pages, redirect to dashboard
  if (authStore.isAuthenticated && to.matched.some(record => record.path.includes('/auth'))) {
    next({ name: 'dashboard' });
    return;
  }
  
  next();
});

// After each route change
router.afterEach((to) => {
  const appStore = useAppStore();
  
  // Set page title
  const title = to.meta.title as string || 'Paksa Financial System';
  document.title = `${title} | Paksa Financial System`;
  
  // Reset loading state
  nextTick(() => {
    appStore.setLoading(false);
  });
});

export default router;
