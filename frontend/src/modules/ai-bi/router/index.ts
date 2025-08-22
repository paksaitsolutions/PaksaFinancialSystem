import { RouteRecordRaw } from 'vue-router';

const routes: Array<RouteRecordRaw> = [
  {
    path: '/ai-assistant',
    name: 'AIAssistant',
    component: () => import('../views/AIAssistant.vue'),
    meta: {
      title: 'AI Assistant',
      icon: 'mdi-robot-happy-outline',
      requiresAuth: true,
      permissions: ['view_ai_assistant']
    }
  },
  {
    path: '/business-intelligence',
    name: 'BusinessIntelligence',
    component: () => import('../views/BusinessIntelligence.vue'),
    meta: {
      title: 'Business Intelligence',
      icon: 'mdi-chart-box-outline',
      requiresAuth: true,
      permissions: ['view_business_intelligence']
    }
  },
  {
    path: '/reports',
    name: 'Reports',
    component: () => import('../views/Reports.vue'),
    meta: {
      title: 'Reports',
      icon: 'mdi-file-document-outline',
      requiresAuth: true,
      permissions: ['view_reports']
    },
    children: [
      {
        path: 'financial',
        name: 'FinancialReports',
        component: () => import('../views/reports/FinancialReports.vue'),
        meta: { title: 'Financial Reports' }
      },
      {
        path: 'operational',
        name: 'OperationalReports',
        component: () => import('../views/reports/OperationalReports.vue'),
        meta: { title: 'Operational Reports' }
      },
      {
        path: 'analytics',
        name: 'AnalyticsReports',
        component: () => import('../views/reports/AnalyticsReports.vue'),
        meta: { title: 'Analytics & Insights' }
      }
    ]
  }
];

export default routes;
