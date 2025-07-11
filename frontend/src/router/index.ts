import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router';

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/TestHome.vue'),
    meta: { title: 'Home' },
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { title: 'Dashboard' },
  },
  // General Ledger
  {
    path: '/gl/accounts',
    name: 'ChartOfAccounts',
    component: () => import('@/views/gl/ChartOfAccounts.vue'),
    meta: { title: 'Chart of Accounts' },
  },
  {
    path: '/gl/journal-entries',
    name: 'JournalEntries',
    component: () => import('@/views/TestHome.vue'),
    meta: { title: 'Journal Entries' },
  },
  // Accounts Payable
  {
    path: '/ap/vendors',
    name: 'Vendors',
    component: () => import('@/views/TestHome.vue'),
    meta: { title: 'Vendors' },
  },
  {
    path: '/ap/invoices',
    name: 'APInvoices',
    component: () => import('@/views/TestHome.vue'),
    meta: { title: 'AP Invoices' },
  },
  // Accounts Receivable
  {
    path: '/ar/customers',
    name: 'Customers',
    component: () => import('@/views/TestHome.vue'),
    meta: { title: 'Customers' },
  },
  {
    path: '/ar/invoices',
    name: 'ARInvoices',
    component: () => import('@/views/TestHome.vue'),
    meta: { title: 'AR Invoices' },
  },
  // Payroll
  {
    path: '/payroll/employees',
    name: 'Employees',
    component: () => import('@/views/TestHome.vue'),
    meta: { title: 'Employees' },
  },
  {
    path: '/payroll/process',
    name: 'PayrollProcess',
    component: () => import('@/views/TestHome.vue'),
    meta: { title: 'Process Payroll' },
  },
  // Cash Management
  {
    path: '/cash/accounts',
    name: 'BankAccounts',
    component: () => import('@/views/TestHome.vue'),
    meta: { title: 'Bank Accounts' },
  },
  {
    path: '/cash/reconciliation',
    name: 'BankReconciliation',
    component: () => import('@/views/TestHome.vue'),
    meta: { title: 'Bank Reconciliation' },
  },
  // Fixed Assets
  {
    path: '/assets/list',
    name: 'AssetList',
    component: () => import('@/views/TestHome.vue'),
    meta: { title: 'Fixed Assets' },
  },
  // Reports
  {
    path: '/reports',
    name: 'Reports',
    component: () => import('@/views/TestHome.vue'),
    meta: { title: 'Reports' },
  },
  // Additional routes
  {
    path: '/gl/trial-balance',
    name: 'TrialBalance',
    component: () => import('@/views/TestHome.vue'),
    meta: { title: 'Trial Balance' },
  },
  {
    path: '/ap/payments',
    name: 'APPayments',
    component: () => import('@/views/TestHome.vue'),
    meta: { title: 'AP Payments' },
  },
  {
    path: '/ar/payments',
    name: 'ARPayments',
    component: () => import('@/views/TestHome.vue'),
    meta: { title: 'AR Payments' },
  },
  {
    path: '/payroll/reports',
    name: 'PayrollReports',
    component: () => import('@/views/TestHome.vue'),
    meta: { title: 'Payroll Reports' },
  },
  {
    path: '/cash/forecast',
    name: 'CashForecast',
    component: () => import('@/views/TestHome.vue'),
    meta: { title: 'Cash Forecast' },
  },
  {
    path: '/assets/depreciation',
    name: 'AssetDepreciation',
    component: () => import('@/views/TestHome.vue'),
    meta: { title: 'Asset Depreciation' },
  },
  {
    path: '/assets/maintenance',
    name: 'AssetMaintenance',
    component: () => import('@/views/TestHome.vue'),
    meta: { title: 'Asset Maintenance' },
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    // Always scroll to top when navigating to a new route
    return { top: 0, behavior: 'smooth' };
  },
});

// Update page title based on route meta
router.beforeEach((to, from, next) => {
  const appName = 'Paksa Financial System';
  document.title = to.meta.title ? `${to.meta.title} | ${appName}` : appName;
  next();
});

export default router;
