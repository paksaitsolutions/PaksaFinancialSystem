import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router';
import { defineComponent } from 'vue';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        component: () => import('@/views/Home.vue')
      }
    ]
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        component: () => import('@/views/AdvancedDashboard.vue')
      }
    ]
  },
  {
    path: '/auth/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue')
  },
  {
    path: '/auth/register',
    name: 'Register',
    component: () => import('@/views/auth/Register.vue')
  },
  {
    path: '/auth/forgot-password',
    name: 'ForgotPassword',
    component: () => import('@/views/auth/ForgotPassword.vue')
  },
  {
    path: '/gl',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'GeneralLedger',
        component: () => import('@/views/accounting/GeneralLedgerView.vue')
      },
      {
        path: 'chart-of-accounts',
        name: 'ChartOfAccounts',
        component: () => import('@/views/accounting/ChartOfAccountsView.vue')
      },
      {
        path: 'journal-entries',
        name: 'JournalEntries',
        component: () => import('@/views/accounting/JournalEntryView.vue')
      },
      {
        path: 'trial-balance',
        name: 'TrialBalance',
        component: () => import('@/views/accounting/TrialBalanceView.vue')
      },
      {
        path: 'financial-statements',
        name: 'FinancialStatements',
        component: () => import('@/views/accounting/FinancialStatementsView.vue')
      }
    ]
  },
  {
    path: '/ap',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'AccountsPayable',
        component: () => import('@/views/accounts-payable/APDashboard.vue')
      }
    ]
  },
  {
    path: '/ar',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'AccountsReceivable',
        component: () => import('@/views/accounts-receivable/CustomersView.vue')
      }
    ]
  },
  {
    path: '/reports',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Reports',
        component: () => import('@/views/reports/SimpleReportsView.vue')
      }
    ]
  },
  {
    path: '/admin',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'SuperAdmin',
        component: () => import('@/views/admin/SuperAdminView.vue')
      }
    ]
  },
  {
    path: '/settings',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Settings',
        component: () => import('@/views/settings/CompanySettingsView.vue')
      }
    ]
  },
  {
    path: '/settings/currency',
    name: 'CurrencySettings',
    component: () => import('@/views/settings/CurrencyManagementView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/rbac',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'RoleManagement',
        component: () => import('@/views/rbac/RoleManagementView.vue')
      }
    ]
  },
  {
    path: '/cash',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'CashManagement',
        component: () => import('@/views/cash/CashManagementView.vue')
      }
    ]
  },
  {
    path: '/assets',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'FixedAssets',
        component: () => import('@/views/assets/FixedAssetsView.vue')
      }
    ]
  },
  {
    path: '/inventory',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Inventory',
        component: () => import('@/views/inventory/InventoryView.vue')
      }
    ]
  },
  {
    path: '/budget',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Budgeting',
        component: () => import('@/views/budget/BudgetingView.vue')
      }
    ]
  },
  {
    path: '/payroll',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Payroll',
        component: () => import('@/views/payroll/PayrollView.vue')
      }
    ]
  },
  {
    path: '/hrm',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'HRM',
        component: () => import('@/views/hrm/HRMView.vue')
      }
    ]
  },
  {
    path: '/tax',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'TaxManagement',
        component: () => import('@/views/ModuleView.vue')
      }
    ]
  },
  {
    path: '/main-dashboard',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'MainDashboard',
        component: () => import('@/views/Dashboard.vue')
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue')
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach((to, from, next) => {
  // Temporarily disable auth for testing
  next()
})

export default router;