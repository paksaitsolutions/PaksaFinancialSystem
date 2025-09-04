import type { RouteRecordRaw } from 'vue-router'

const superAdminRoutes: RouteRecordRaw[] = [
  {
    path: '/super-admin',
    name: 'SuperAdmin',
    component: () => import('../views/SuperAdminView.vue'),
    meta: { 
      title: 'Super Admin Dashboard',
      requiresAuth: true,
      requiresAdmin: true
    },
    children: [
      {
        path: 'companies',
        name: 'CompanyManagement',
        component: () => import('../components/CompanyManagement.vue'),
        meta: { title: 'Company Management' }
      },
      {
        path: 'system',
        name: 'SystemMonitoring',
        component: () => import('../components/SystemMonitoring.vue'),
        meta: { title: 'System Monitoring' }
      },
      {
        path: 'analytics',
        name: 'PlatformAnalytics',
        component: () => import('../components/PlatformAnalytics.vue'),
        meta: { title: 'Platform Analytics' }
      },
      {
        path: 'config',
        name: 'GlobalConfiguration',
        component: () => import('../components/GlobalConfiguration.vue'),
        meta: { title: 'Global Configuration' }
      }
    ]
  }
]

export default superAdminRoutes