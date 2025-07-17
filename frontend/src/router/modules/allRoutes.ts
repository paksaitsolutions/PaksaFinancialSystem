import { defineComponent } from 'vue';
import type { RouteRecordRaw } from 'vue-router';

// Import all view components
import UnderConstruction from '@/views/UnderConstruction.vue';

// Helper function to lazy load components with fallback
const lazyLoad = (path: string) => {
  return () => import(`@/views/${path}.vue`).catch(() => ({
    template: '<UnderConstruction />',
    components: { UnderConstruction },
  }));
};

// Auth layout component
const AuthLayout = defineComponent({
  template: '<router-view />'
});

// Auth routes
export const authRoutes: RouteRecordRaw = {
  path: '/auth',
  name: 'Auth',
  component: AuthLayout,
  meta: { requiresGuest: true },
  children: [
    {
      path: 'login',
      name: 'Login',
      component: () => import('@/views/auth/Login.vue'),
      meta: { title: 'Login' }
    },
    // Add register, forgot-password, etc. here
  ]
};

// Root route
export const rootRoute: RouteRecordRaw = {
  path: '/',
  name: 'Home',
  component: () => import('@/views/Home.vue'),
  meta: { 
    title: 'Home',
    requiresAuth: true
  },
};

// Dashboard route
export const dashboardRoutes: RouteRecordRaw = {
  path: '/dashboard',
  name: 'Dashboard',
  component: () => import('@/views/Dashboard.vue'),
  meta: { title: 'Dashboard' },
};

// GL layout component
const GLLayout = defineComponent({
  template: '<router-view />'
});

export const glRoutes: RouteRecordRaw = {
  path: '/gl',
  name: 'GL',
  component: GLLayout,
  redirect: '/gl/dashboard',
  children: [
    {
      path: 'dashboard',
      name: 'GLDashboard',
      component: lazyLoad('gl/Dashboard'),
      meta: { title: 'GL Dashboard' },
    },
    {
      path: 'accounts',
      name: 'ChartOfAccounts',
      component: lazyLoad('gl/ChartOfAccounts'),
      meta: { title: 'Chart of Accounts' },
    },
    {
      path: 'journal-entries',
      name: 'JournalEntries',
      component: lazyLoad('gl/JournalEntries'),
      meta: { title: 'Journal Entries' },
    },
    {
      path: 'trial-balance',
      name: 'TrialBalance',
      component: lazyLoad('gl/TrialBalance'),
      meta: { title: 'Trial Balance' },
    },
    {
      path: 'financial-statements',
      name: 'FinancialStatements',
      component: UnderConstruction,
      meta: { title: 'Financial Statements' },
    },
    {
      path: 'recurring-journals',
      name: 'RecurringJournals',
      component: UnderConstruction,
      meta: { title: 'Recurring Journals' },
    },
    {
      path: 'allocation-rules',
      name: 'AllocationRules',
      component: UnderConstruction,
      meta: { title: 'Allocation Rules' },
    },
    {
      path: 'period-close',
      name: 'PeriodClose',
      component: UnderConstruction,
      meta: { title: 'Period Close' },
    },
    {
      path: 'advanced',
      name: 'AdvancedGL',
      component: lazyLoad('gl/AdvancedGL'),
      meta: { title: 'Advanced GL' },
    },
  ],
};

// Route modules for different sections
const apRoutes: RouteRecordRaw = {
  path: '/ap',
  name: 'AP',
  component: defineComponent({ template: '<router-view />' }),
  redirect: '/ap/vendors',
  children: [
    { path: 'vendors', component: () => import('@/views/PlaceholderView.vue'), meta: { title: 'Vendors' } },
    { path: 'invoices', component: () => import('@/views/PlaceholderView.vue'), meta: { title: 'AP Invoices' } },
    { path: 'payments', component: () => import('@/views/PlaceholderView.vue'), meta: { title: 'Payments' } },
    { path: 'analytics', component: () => import('@/views/PlaceholderView.vue'), meta: { title: 'AP Analytics' } }
  ]
};

const arRoutes: RouteRecordRaw = {
  path: '/ar',
  name: 'AR',
  component: defineComponent({ template: '<router-view />' }),
  redirect: '/ar/customers',
  children: [
    { path: 'customers', component: () => import('@/views/PlaceholderView.vue'), meta: { title: 'Customers' } },
    { path: 'invoices', component: () => import('@/views/PlaceholderView.vue'), meta: { title: 'AR Invoices' } },
    { path: 'payments', component: () => import('@/views/PlaceholderView.vue'), meta: { title: 'Payments' } },
    { path: 'analytics', component: () => import('@/views/PlaceholderView.vue'), meta: { title: 'AR Analytics' } }
  ]
};

const payrollRoutes: RouteRecordRaw = {
  path: '/payroll',
  name: 'Payroll',
  component: defineComponent({ template: '<router-view />' }),
  redirect: '/payroll/employees',
  children: [
    { path: 'employees', component: () => import('@/views/PlaceholderView.vue'), meta: { title: 'Employees' } },
    { path: 'process', component: () => import('@/views/PlaceholderView.vue'), meta: { title: 'Process Payroll' } },
    { path: 'reports', component: () => import('@/views/PlaceholderView.vue'), meta: { title: 'Payroll Reports' } }
  ]
};

const cashRoutes: RouteRecordRaw = {
  path: '/cash',
  name: 'CashManagement',
  component: defineComponent({ template: '<router-view />' }),
  redirect: '/cash/accounts',
  children: [
    { path: 'accounts', component: () => import('@/views/PlaceholderView.vue'), meta: { title: 'Bank Accounts' } },
    { path: 'reconciliation', component: () => import('@/views/PlaceholderView.vue'), meta: { title: 'Reconciliation' } },
    { path: 'forecast', component: () => import('@/views/PlaceholderView.vue'), meta: { title: 'Cash Forecast' } }
  ]
};

const assetsRoutes: RouteRecordRaw = {
  path: '/assets',
  name: 'Assets',
  component: defineComponent({ template: '<router-view />' }),
  redirect: '/assets/list',
  children: [
    { path: 'list', component: () => import('@/views/PlaceholderView.vue'), meta: { title: 'Assets List' } },
    { path: 'depreciation', component: () => import('@/views/PlaceholderView.vue'), meta: { title: 'Depreciation' } },
    { path: 'maintenance', component: () => import('@/views/PlaceholderView.vue'), meta: { title: 'Maintenance' } }
  ]
};

const taxRoutes: RouteRecordRaw = {
  path: '/tax',
  name: 'Tax',
  component: defineComponent({ template: '<router-view />' }),
  redirect: '/tax/exemption-certificate',
  children: [
    { path: 'exemption-certificate', component: () => import('@/views/PlaceholderView.vue'), meta: { title: 'Exemption Certificates' } },
    { path: 'policy', component: () => import('@/views/PlaceholderView.vue'), meta: { title: 'Tax Policy' } }
  ]
};

// Export all routes as an array
export const allRoutes: RouteRecordRaw[] = [
  rootRoute,
  authRoutes,
  dashboardRoutes,
  glRoutes,
  apRoutes,
  arRoutes,
  payrollRoutes,
  cashRoutes,
  assetsRoutes,
  taxRoutes,
  // Catch-all route for 404s - must be last
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: { title: 'Page Not Found' }
  }
];

export default allRoutes;
