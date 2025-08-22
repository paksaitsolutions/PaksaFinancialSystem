export default [
  {
    path: '/integration',
    name: 'Integration',
    component: () => import('@/layouts/DefaultLayout.vue'),
    children: [
      {
        path: 'dashboard',
        name: 'ExecutiveDashboard',
        component: () => import('@/components/integration/ExecutiveDashboard.vue'),
        meta: {
          title: 'Executive Dashboard',
          requiresAuth: true
        }
      },
      {
        path: 'workflows',
        name: 'WorkflowManager',
        component: () => import('@/components/integration/WorkflowManager.vue'),
        meta: {
          title: 'Integrated Workflows',
          requiresAuth: true
        }
      },
      {
        path: 'reports',
        name: 'IntegratedReports',
        component: () => import('@/components/integration/IntegratedReports.vue'),
        meta: {
          title: 'Integrated Reports',
          requiresAuth: true
        }
      }
    ]
  }
]