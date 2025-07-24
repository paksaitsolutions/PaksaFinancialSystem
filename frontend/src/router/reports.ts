export default [
  {
    path: '/reports',
    name: 'Reports',
    component: () => import('@/views/reports/ReportsView.vue'),
    meta: {
      requiresAuth: true,
      title: 'Reports'
    }
  },
  {
    path: '/reports/enhanced',
    name: 'EnhancedReports',
    component: () => import('@/views/reports/EnhancedReportsView.vue'),
    meta: {
      requiresAuth: true,
      title: 'Enhanced Reports'
    }
  },
  {
    path: '/reports/financial',
    name: 'FinancialReports',
    component: () => import('@/views/reports/FinancialReportsView.vue'),
    meta: {
      requiresAuth: true,
      title: 'Financial Reports'
    }
  },
  {
    path: '/reports/income-statement',
    name: 'IncomeStatement',
    component: () => import('@/views/reports/IncomeStatementReport.vue'),
    meta: {
      requiresAuth: true,
      title: 'Income Statement'
    }
  },
  {
    path: '/reports/balance-sheet',
    name: 'BalanceSheet',
    component: () => import('@/views/reports/BalanceSheetReport.vue'),
    meta: {
      requiresAuth: true,
      title: 'Balance Sheet'
    }
  },
  {
    path: '/reports/cash-flow',
    name: 'CashFlow',
    component: () => import('@/views/reports/CashFlowReport.vue'),
    meta: {
      requiresAuth: true,
      title: 'Cash Flow Statement'
    }
  },
  {
    path: '/reports/ar-aging',
    name: 'ARAging',
    component: () => import('@/views/reports/ARAgingReport.vue'),
    meta: {
      requiresAuth: true,
      title: 'AR Aging Report'
    }
  },
  {
    path: '/reports/ap-aging',
    name: 'APAging',
    component: () => import('@/views/reports/APAgingReport.vue'),
    meta: {
      requiresAuth: true,
      title: 'AP Aging Report'
    }
  },
  {
    path: '/reports/templates',
    name: 'ReportTemplates',
    component: () => import('@/views/reports/ReportTemplatesView.vue'),
    meta: {
      requiresAuth: true,
      title: 'Report Templates'
    }
  },
  {
    path: '/reports/schedules',
    name: 'ReportSchedules',
    component: () => import('@/views/reports/ReportSchedulesView.vue'),
    meta: {
      requiresAuth: true,
      title: 'Report Schedules'
    }
  }
];