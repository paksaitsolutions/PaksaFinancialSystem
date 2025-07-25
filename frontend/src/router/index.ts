import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router';
import { defineComponent } from 'vue';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboard',
    name: 'Dashboard', 
    component: () => import('@/views/Dashboard.vue'),
    meta: { requiresAuth: true }
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
    name: 'GeneralLedger',
    component: () => import('@/views/accounting/GeneralLedgerView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/gl/chart-of-accounts',
    name: 'ChartOfAccounts',
    component: () => import('@/views/accounting/ChartOfAccountsView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/gl/journal-entries',
    name: 'JournalEntries',
    component: () => import('@/views/accounting/JournalEntryView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/gl/trial-balance',
    name: 'TrialBalance',
    component: () => import('@/views/accounting/TrialBalanceView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/gl/financial-statements',
    name: 'FinancialStatements',
    component: () => import('@/views/accounting/FinancialStatementsView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/ap',
    name: 'AccountsPayable',
    component: () => import('@/views/accounts-payable/VendorsView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/ar',
    name: 'AccountsReceivable',
    component: () => import('@/views/accounts-receivable/CustomersView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/reports',
    name: 'Reports',
    component: () => import('@/views/reports/SimpleReportsView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/admin',
    name: 'SuperAdmin',
    component: () => import('@/views/admin/SuperAdminView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/settings/CompanySettingsView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/settings/currency',
    name: 'CurrencySettings',
    component: () => import('@/views/settings/CurrencyManagementView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/rbac',
    name: 'RoleManagement',
    component: () => import('@/views/rbac/RoleManagementView.vue'),
    meta: { requiresAuth: true }
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
  const token = localStorage.getItem('token')
  
  if (to.meta.requiresAuth && !token) {
    next('/auth/login')
  } else if (to.path === '/auth/login' && token) {
    next('/')
  } else {
    next()
  }
})

export default router;