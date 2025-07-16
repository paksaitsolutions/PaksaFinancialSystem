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
  // Tax Management Routes
  {
    path: '/tax',
    redirect: '/tax/dashboard',
    meta: { requiresAuth: true, permission: 'view_tax_module' },
    children: [
      {
        path: 'dashboard',
        name: 'TaxDashboard',
        component: () => import('@/views/tax/TaxDashboard.vue'),
        meta: { title: 'Tax Dashboard', permission: 'view_tax_dashboard' },
      },
      {
        path: 'compliance',
        name: 'TaxCompliance',
        component: () => import('@/views/tax/TaxCompliance.vue'),
        meta: { title: 'Tax Compliance', permission: 'view_tax_compliance' },
      },
      {
        path: 'codes',
        name: 'TaxCodes',
        component: () => import('@/views/tax/TaxCodes.vue'),
        meta: { title: 'Tax Codes', permission: 'view_tax_codes' },
      },
      {
        path: 'rates',
        name: 'TaxRates',
        component: () => import('@/views/tax/TaxRates.vue'),
        meta: { title: 'Tax Rates', permission: 'view_tax_rates' },
      },
      {
        path: 'jurisdictions',
        name: 'TaxJurisdictions',
        component: () => import('@/views/tax/TaxJurisdictions.vue'),
        meta: { title: 'Tax Jurisdictions', permission: 'view_tax_jurisdictions' },
      },
      {
        path: 'exemptions',
        name: 'TaxExemptions',
        component: () => import('@/views/tax/TaxExemptions.vue'),
        meta: { title: 'Tax Exemptions', permission: 'view_tax_exemptions' },
      },
      {
        path: 'exemption-certificates',
        name: 'TaxExemptionCertificates',
        component: () => import('@/views/tax/TaxExemptionCertificatesView.vue'),
        meta: { title: 'Exemption Certificates', permission: 'view_tax_exemption_certificates' },
      },
      {
        path: 'exemption-certificate/:id?',
        name: 'TaxExemptionCertificate',
        component: () => import('@/views/tax/TaxExemptionCertificate.vue'),
        meta: { title: 'Tax Exemption Certificate', permission: 'manage_tax_exemption_certificates' },
        props: true
      },
      {
        path: 'liability',
        name: 'TaxLiability',
        component: () => import('@/views/tax/TaxLiabilityReport.vue'),
        meta: { title: 'Tax Liability', permission: 'view_tax_liability' },
      },
      {
        path: 'filing',
        name: 'TaxFiling',
        component: () => import('@/views/tax/TaxCompliance.vue'),
        meta: { title: 'Tax Compliance', permission: 'view_tax_compliance' },
      },
      {
        path: 'reports',
        name: 'TaxReports',
        component: () => import('@/views/tax/TaxReports.vue'),
        meta: { title: 'Tax Reports', permission: 'view_tax_reports' },
      },
      {
        path: 'policy',
        name: 'TaxPolicy',
        component: () => import('@/views/tax/TaxPolicyView.vue'),
        meta: { title: 'Tax Policy', permission: 'view_tax_policy' },
      },
      {
        path: 'settings',
        name: 'TaxSettings',
        component: () => import('@/views/TestHome.vue'),
        meta: { title: 'Tax Settings', permission: 'manage_tax_settings' },
      },
    ],
  },
  // Reports
  {
    path: '/reports',
    name: 'FinancialReports',
    component: () => import('@/views/reports/FinancialReportsView.vue'),
    meta: { title: 'Financial Reports' },
  },
  {
    path: '/reports/balance-sheet',
    name: 'BalanceSheetReport',
    component: () => import('@/views/reports/BalanceSheetReport.vue'),
    meta: { title: 'Balance Sheet Report' },
  },
  {
    path: '/reports/income-statement',
    name: 'IncomeStatementReport',
    component: () => import('@/views/reports/IncomeStatementReport.vue'),
    meta: { title: 'Income Statement Report' },
  },
  {
    path: '/reports/cash-flow',
    name: 'CashFlowReport',
    component: () => import('@/views/reports/CashFlowReport.vue'),
    meta: { title: 'Cash Flow Report' },
  },
  {
    path: '/reports/ar-aging',
    name: 'ARAgingReport',
    component: () => import('@/views/reports/ARAgingReport.vue'),
    meta: { title: 'AR Aging Report' },
  },
  {
    path: '/reports/ap-aging',
    name: 'APAgingReport',
    component: () => import('@/views/reports/APAgingReport.vue'),
    meta: { title: 'AP Aging Report' },
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