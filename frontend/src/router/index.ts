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
    component: () => import('@/views/gl/JournalEntries.vue'),
    meta: { title: 'Journal Entries' },
  },
  {
    path: '/gl/trial-balance',
    name: 'TrialBalance',
    component: () => import('@/views/gl/TrialBalance.vue'),
    meta: { title: 'Trial Balance' },
  },
  // Accounts Payable
  {
    path: '/ap/vendors',
    name: 'Vendors',
    component: () => import('@/views/ap/VendorsAdvanced.vue'),
    meta: { title: 'Vendors' },
  },
  {
    path: '/ap/invoices',
    name: 'APInvoices',
    component: () => import('@/views/ap/Invoices.vue'),
    meta: { title: 'AP Invoices' },
  },
  {
    path: '/ap/payments',
    name: 'APPayments',
    component: () => import('@/views/ap/Payments.vue'),
    meta: { title: 'AP Payments' },
  },
  {
    path: '/ap/analytics',
    name: 'APAnalytics',
    component: () => import('@/views/ap/APAnalyticsDashboard.vue'),
    meta: { title: 'AP Analytics' },
  },
  // Accounts Receivable
  {
    path: '/ar/customers',
    name: 'Customers',
    component: () => import('@/views/ar/CustomersAdvanced.vue'),
    meta: { title: 'Customers' },
  },
  {
    path: '/ar/invoices',
    name: 'ARInvoices',
    component: () => import('@/views/ar/ARInvoicesAdvanced.vue'),
    meta: { title: 'AR Invoices' },
  },
  {
    path: '/ar/payments',
    name: 'ARPayments',
    component: () => import('@/views/ar/ARPaymentsAdvanced.vue'),
    meta: { title: 'AR Payments' },
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
  {
    path: '/payroll/reports',
    name: 'PayrollReports',
    component: () => import('@/views/TestHome.vue'),
    meta: { title: 'Payroll Reports' },
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
  {
    path: '/cash/forecast',
    name: 'CashForecast',
    component: () => import('@/views/TestHome.vue'),
    meta: { title: 'Cash Forecast' },
  },
  // Fixed Assets
  {
    path: '/assets/list',
    name: 'AssetList',
    component: () => import('@/views/TestHome.vue'),
    meta: { title: 'Fixed Assets' },
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
  // Tax Routes
  {
    path: '/tax/exemption-certificate',
    name: 'TaxExemptionCertificate',
    component: () => import('@/views/tax/TaxExemptionCertificate.vue'),
    meta: { title: 'Tax Exemption Certificate' },
  },
  {
    path: '/tax/policy',
    name: 'TaxPolicy',
    component: () => import('@/views/TestHome.vue'),
    meta: { title: 'Tax Policy' },
  },
  // Reports
  {
    path: '/reports',
    name: 'Reports',
    component: () => import('@/views/TestHome.vue'),
    meta: { title: 'Reports' },
  },
  {
    path: '/reports/ar',
    name: 'ARReports',
    component: () => import('@/views/reports/ARReports.vue'),
    meta: { title: 'AR Reports' },
  },
  {
    path: '/gl/advanced',
    name: 'GLDashboard',
    component: () => import('@/views/gl/AdvancedGL.vue'),
    meta: { title: 'General Ledger' },
  },
  {
    path: '/ar/analytics',
    name: 'ARAnalytics',
    component: () => import('@/views/ar/ARAnalyticsDashboard.vue'),
    meta: { title: 'AR Analytics' },
  },
  {
    path: '/gl/advanced',
    name: 'AdvancedGL',
    component: () => import('@/views/gl/AdvancedGL.vue'),
    meta: { title: 'Advanced General Ledger' },
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    return { top: 0, behavior: 'smooth' };
  },
});

router.beforeEach((to, from, next) => {
  const appName = 'Paksa Financial System';
  document.title = to.meta.title ? `${to.meta.title} | ${appName}` : appName;
  next();
});

export default router;