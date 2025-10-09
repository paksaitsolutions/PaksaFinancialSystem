import { createRouter, createWebHistory } from 'vue-router';
// Import Vue Router types
import type { 
  RouteRecordRaw, 
  RouteMeta,
  RouteRecordRedirectOption
} from 'vue-router';

// Import module routes
import hrmRoutes from './modules/hrm';

// Type for route query parameters (unused but kept for future reference)
type RouteQuery = {
  [key: string]: string | string[] | undefined;
  redirect?: string;
};

// Define our custom route meta properties
type CustomRouteMeta = {
  title?: string;
  icon?: string;
  requiresAuth?: boolean;
  requiresGuest?: boolean;
  requiresAdmin?: boolean;
  roles?: string[];
  layout?: string | null;
  module?: string;
};

// Extend Vue Router types
declare module 'vue-router' {
  // Extend Vue Router's RouteMeta with our custom properties
  interface RouteMeta extends CustomRouteMeta {}

  // Extend RouteLocationNormalized to include our custom query type
}

// Import for functional components (commented out since not currently used)
// import { h } from 'vue';

// Base route type that matches Vue Router's expectations
type AppRouteRecordRaw = Omit<RouteRecordRaw, 'children' | 'redirect' | 'meta'> & {
  children?: AppRouteRecordRaw[];
  redirect?: RouteRecordRedirectOption;
  meta?: RouteMeta;
};

// Public routes (no authentication required)
const publicRoutes: AppRouteRecordRaw[] = [
  {
    path: '/auth',
    component: () => import('@/layouts/AuthLayout.vue'),
    meta: { requiresGuest: true, layout: null },
    redirect: { name: 'Login' },
    children: [
      {
        path: 'login',
        name: 'Login',
        component: () => import('@/modules/auth/views/Login.vue'),
        meta: { title: 'Login' }
      },
      {
        path: 'register',
        name: 'Register',
        component: () => import('@/modules/auth/views/Register.vue'),
        meta: { title: 'Create Account' }
      },
      {
        path: 'forgot-password',
        name: 'ForgotPassword',
        component: () => import('@/modules/auth/views/ForgotPassword.vue'),
        meta: { title: 'Reset Password' }
      },
      {
        path: 'reset-password/:token',
        name: 'ResetPassword',
        component: () => import('@/modules/auth/views/ResetPassword.vue'),
        meta: { title: 'Set New Password' },
        props: true
      },
      {
        path: 'verify-email/:token',
        name: 'VerifyEmail',
        component: () => import('@/modules/auth/views/VerifyEmail.vue'),
        meta: { title: 'Verify Email' },
        props: true
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/error/NotFound.vue'),
    meta: { 
      title: 'Page Not Found',
      requiresAuth: false
    }
  },
  {
    path: '/500',
    name: 'Error500',
    component: () => import('@/components/common/PlaceholderView.vue'),
    meta: { 
      title: 'Server Error',
      requiresAuth: false
    }
  }
];

// Helper function to create module routes (unused but kept for future reference)
const createModuleRoute = (
  name: string,
  path: string,
  routes: AppRouteRecordRaw[],
  meta: RouteMeta = {}
): AppRouteRecordRaw => {
  return {
    path,
    name,
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { 
      requiresAuth: true,
      ...meta 
    },
    children: routes
  };
};

// Note: Module routes are now defined directly in mainAppRoute for simplicity

// Define the main application routes

// Convert our route type to Vue Router's expected type
const toRouteRecord = (route: AppRouteRecordRaw): RouteRecordRaw => {
  const { children, meta, redirect, ...rest } = route;
  
  // Create base route record with required properties
  const result: Omit<RouteRecordRaw, 'redirect'> & { redirect?: RouteRecordRedirectOption } = {
    ...rest,
    meta: meta || {}
  };

  // Handle redirect if it exists
  if (redirect !== undefined) {
    result.redirect = redirect;
  }
  
  // Handle children recursively if they exist
  if (children) {
    result.children = children.map(toRouteRecord);
  }
  
  // Ensure path is always defined (required by RouteRecordRaw)
  if (!result.path) {
    result.path = '';
  }
  
  return result as RouteRecordRaw;
};

// Main application route with all the module routes as children
const mainAppRoute: AppRouteRecordRaw = {
  path: '/',
  component: () => import('@/layouts/AppLayout.vue'),
  meta: { 
    requiresAuth: true,
    layout: null
  },
  children: [
    // Dashboard
    {
      path: '',
      name: 'Dashboard',
      component: () => import('@/views/home/Home.vue'),
      meta: { title: 'Dashboard', requiresAuth: true }
    },
    // General Ledger - Lazy loaded with chunk names
    {
      path: 'gl',
      name: 'GeneralLedger',
      component: () => import(/* webpackChunkName: "gl-dashboard" */ '@/modules/general-ledger/views/Dashboard.vue'),
      meta: { title: 'General Ledger' }
    },
    {
      path: 'gl/dashboard',
      name: 'GLDashboard',
      component: () => import('@/modules/general-ledger/views/Dashboard.vue'),
      meta: { title: 'GL Dashboard' }
    },
    {
      path: 'gl/chart-of-accounts',
      name: 'ChartOfAccounts',
      component: () => import('@/modules/general-ledger/views/ChartOfAccounts.vue'),
      meta: { title: 'Chart of Accounts' }
    },
    {
      path: 'gl/trial-balance',
      name: 'TrialBalance',
      component: () => import('@/modules/general-ledger/views/TrialBalance.vue'),
      meta: { title: 'Trial Balance' }
    },
    {
      path: 'gl/general-ledger-report',
      name: 'GeneralLedgerReport',
      component: () => import('@/modules/general-ledger/views/GeneralLedgerReport.vue'),
      meta: { title: 'General Ledger Report' }
    },
    {
      path: 'gl/reconciliation',
      name: 'AccountReconciliation',
      component: () => import('@/modules/general-ledger/views/AccountReconciliation.vue'),
      meta: { title: 'Account Reconciliation' }
    },
    {
      path: 'gl/financial-statements',
      name: 'FinancialStatements',
      component: () => import('@/modules/general-ledger/views/FinancialStatements.vue'),
      meta: { title: 'Financial Statements' }
    },
    {
      path: 'gl/period-close',
      name: 'PeriodClose',
      component: () => import('@/modules/general-ledger/views/PeriodClose.vue'),
      meta: { title: 'Period Close' }
    },
    {
      path: 'gl/budget-actual',
      name: 'BudgetActual',
      component: () => import('@/modules/general-ledger/views/BudgetActual.vue'),
      meta: { title: 'Budget vs Actual' }
    },
    {
      path: 'gl/recurring',
      name: 'RecurringJournals',
      component: () => import('@/modules/general-ledger/views/RecurringJournals.vue'),
      meta: { title: 'Recurring Journal Entries' }
    },
    {
      path: 'gl/journal-entries',
      name: 'JournalEntries',
      component: () => import('@/modules/accounting/views/JournalEntryView.vue'),
      meta: { title: 'Journal Entries' }
    },
    {
      path: 'gl/accounts',
      name: 'GLAccounts',
      component: () => import('@/modules/general-ledger/views/ChartOfAccounts.vue'),
      meta: { title: 'Chart of Accounts' }
    },
    // Accounting
    {
      path: 'accounting/journal-entry',
      name: 'JournalEntry',
      component: () => import('@/modules/accounting/views/JournalEntryView.vue'),
      meta: { title: 'Journal Entry' }
    },
    // Accounts Payable - Lazy loaded
    {
      path: 'ap',
      name: 'AccountsPayable',
      component: () => import(/* webpackChunkName: "ap-module" */ '@/modules/accounts-payable/views/APDashboard.vue'),
      meta: { title: 'Accounts Payable' }
    },
    {
      path: 'ap/create-bill',
      name: 'CreateBill',
      component: () => import('@/modules/accounts-payable/views/CreateBill.vue'),
      meta: { title: 'Create New Bill' }
    },
    {
      path: 'ap/add-vendor',
      name: 'AddVendor',
      component: () => import('@/modules/accounts-payable/views/AddVendor.vue'),
      meta: { title: 'Add Vendor' }
    },
    {
      path: 'ap/record-payment',
      name: 'RecordPayment',
      component: () => import('@/modules/accounts-payable/views/RecordPayment.vue'),
      meta: { title: 'Record Payment' }
    },
    {
      path: 'ap/import-bills',
      name: 'ImportBills',
      component: () => import('@/modules/accounts-payable/views/ImportBills.vue'),
      meta: { title: 'Import Bills' }
    },
    {
      path: 'ap/reports',
      name: 'APReports',
      component: () => import('@/modules/accounts-payable/views/APReports.vue'),
      meta: { title: 'AP Reports' }
    },
    {
      path: 'ap/bills',
      name: 'APBills',
      component: () => import('@/modules/accounts-payable/views/BillsView.vue'),
      meta: { title: 'AP Bills' }
    },
    {
      path: 'ap/vendors',
      name: 'APVendors',
      component: () => import('@/modules/accounts-payable/views/VendorsView.vue'),
      meta: { title: 'Vendors' }
    },
    {
      path: 'ap/vendor-management',
      name: 'VendorManagement',
      component: () => import('@/modules/accounts-payable/views/VendorManagementView.vue'),
      meta: { title: 'Vendor Management' }
    },
    {
      path: 'ap/invoices',
      name: 'APInvoices',
      component: () => import('@/modules/accounts-payable/views/invoices/InvoicesView.vue'),
      meta: { title: 'AP Invoices' }
    },
    {
      path: 'ap/invoice-management',
      name: 'InvoiceManagement',
      component: () => import('@/modules/accounts-payable/views/InvoiceManagementView.vue'),
      meta: { title: 'Invoice Management' }
    },
    {
      path: 'ap/payments',
      name: 'APPayments',
      component: () => import('@/modules/accounts-payable/views/payments/PaymentsView.vue'),
      meta: { title: 'AP Payments' }
    },
    {
      path: 'ap/payment-management',
      name: 'PaymentManagement',
      component: () => import('@/modules/accounts-payable/views/PaymentManagementView.vue'),
      meta: { title: 'Payment Management' }
    },
    {
      path: 'ap/credit-memos',
      name: 'CreditMemos',
      component: () => import('@/modules/accounts-payable/views/CreditMemoManagementView.vue'),
      meta: { title: 'Credit Memos' }
    },
    {
      path: 'ap/1099-forms',
      name: 'Form1099Management',
      component: () => import('@/modules/accounts-payable/views/Form1099ManagementView.vue'),
      meta: { title: '1099 Forms' }
    },
    // Accounts Receivable - Lazy loaded
    {
      path: 'ar',
      name: 'AccountsReceivable',
      component: () => import(/* webpackChunkName: "ar-module" */ '@/modules/accounts-receivable/views/AccountsReceivableView.vue'),
      meta: { title: 'Accounts Receivable' }
    },
    {
      path: 'accounts-receivable/invoices',
      name: 'ARInvoicesList',
      component: () => import('@/modules/accounts-receivable/views/AccountsReceivableView.vue'),
      meta: { title: 'AR Invoices' }
    },
    {
      path: 'ar/invoices',
      name: 'ARInvoices',
      component: () => import('@/modules/accounts-receivable/views/AccountsReceivableView.vue'),
      meta: { title: 'AR Invoices' }
    },
    {
      path: 'ar/payments',
      name: 'ARPayments',
      component: () => import('@/modules/accounts-receivable/views/AccountsReceivableView.vue'),
      meta: { title: 'AR Payments' }
    },
    {
      path: 'ar/collections',
      name: 'ARCollections',
      component: () => import('@/modules/accounts-receivable/views/CollectionsManagementView.vue'),
      meta: { title: 'AR Collections' }
    },
    {
      path: 'ar/customers',
      name: 'ARCustomers',
      component: () => import('@/modules/accounts-receivable/views/CustomersView.vue'),
      meta: { title: 'Customers' }
    },
    {
      path: 'ar/analytics',
      name: 'ARAnalytics',
      component: () => import('@/modules/accounts-receivable/ARAnalyticsView.vue'),
      meta: { title: 'AR Analytics' }
    },
    {
      path: 'ar/reports',
      name: 'ARReports',
      component: () => import('@/modules/reports/views/ARReports.vue'),
      meta: { title: 'AR Reports' }
    },
    // Cash Management
    {
      path: 'cash',
      name: 'CashManagement',
      component: () => import('@/modules/cash-management/views/CashManagementView.vue'),
      meta: { title: 'Cash Management' }
    },
    {
      path: 'cash/accounts',
      name: 'CashAccounts',
      component: () => import('@/modules/cash-management/views/BankAccounts.vue'),
      meta: { title: 'Bank Accounts' }
    },
    {
      path: 'cash/transactions',
      name: 'CashTransactions',
      component: () => import('@/modules/cash-management/views/Transactions.vue'),
      meta: { title: 'Cash Transactions' }
    },
    {
      path: 'cash/reconciliation',
      name: 'CashReconciliation',
      component: () => import('@/modules/cash-management/views/Reconciliation.vue'),
      meta: { title: 'Bank Reconciliation' }
    },
    {
      path: 'cash/forecasting',
      name: 'CashForecasting',
      component: () => import('@/modules/cash-management/views/CashFlowForecastingView.vue'),
      meta: { title: 'Cash Flow Forecasting' }
    },
    {
      path: 'cash/banking-integration',
      name: 'BankingIntegration',
      component: () => import('@/modules/cash-management/views/BankingIntegrationView.vue'),
      meta: { title: 'Banking Integration' }
    },
    // Inventory
    {
      path: 'inventory',
      name: 'Inventory',
      component: () => import('@/modules/inventory/views/InventoryManagementView.vue'),
      meta: { title: 'Inventory' }
    },
    {
      path: 'inventory/items',
      name: 'InventoryItems',
      component: () => import('@/modules/inventory/views/ItemsView.vue'),
      meta: { title: 'Inventory Items' }
    },
    {
      path: 'inventory/locations',
      name: 'InventoryLocations',
      component: () => import('@/modules/inventory/views/LocationsView.vue'),
      meta: { title: 'Inventory Locations' }
    },
    {
      path: 'inventory/adjustments',
      name: 'InventoryAdjustments',
      component: () => import('@/modules/inventory/views/AdjustmentsView.vue'),
      meta: { title: 'Inventory Adjustments' }
    },
    {
      path: 'inventory/reports',
      name: 'InventoryReports',
      component: () => import('@/modules/inventory/views/ReportsView.vue'),
      meta: { title: 'Inventory Reports' }
    },
    // Fixed Assets
    {
      path: 'fixed-assets',
      name: 'FixedAssets',
      component: () => import('@/modules/fixed-assets/views/FixedAssetsView.vue'),
      meta: { title: 'Fixed Assets' }
    },
    {
      path: 'assets',
      redirect: '/assets/management'
    },
    {
      path: 'assets/management',
      name: 'AssetsManagement',
      component: () => import('@/modules/fixed-assets/views/FixedAssetsView.vue'),
      meta: { title: 'Assets Management' }
    },
    {
      path: 'assets/depreciation',
      name: 'AssetsDepreciation',
      component: () => import('@/modules/fixed-assets/views/DepreciationView.vue'),
      meta: { title: 'Assets Depreciation' }
    },
    {
      path: 'assets/maintenance',
      name: 'AssetsMaintenance',
      component: () => import('@/modules/fixed-assets/views/MaintenanceView.vue'),
      meta: { title: 'Assets Maintenance' }
    },
    // Budget
    {
      path: 'budget',
      name: 'Budget',
      component: () => import('@/modules/budget/views/BudgetDashboard.vue'),
      meta: { title: 'Budget Management' }
    },
    {
      path: 'budget/manage',
      name: 'BudgetManage',
      component: () => import('@/modules/budget/views/BudgetingView.vue'),
      meta: { title: 'Budget Management' }
    },
    {
      path: 'budget/planning',
      name: 'BudgetPlanning',
      component: () => import('@/modules/budget/views/BudgetPlanningView.vue'),
      meta: { title: 'Budget Planning' }
    },
    {
      path: 'budget/monitoring',
      name: 'BudgetMonitoring',
      component: () => import('@/modules/budget/views/BudgetMonitoringView.vue'),
      meta: { title: 'Budget Monitoring' }
    },
    {
      path: 'budget/approval',
      name: 'BudgetApproval',
      component: () => import('@/modules/budget/views/BudgetApprovalView.vue'),
      meta: { title: 'Budget Approval' }
    },
    {
      path: 'budget/reports',
      name: 'BudgetReports',
      component: () => import('@/modules/budget/views/BudgetReportView.vue'),
      meta: { title: 'Budget Reports' }
    },
    {
      path: 'budget/forecasting',
      name: 'BudgetForecasting',
      component: () => import('@/modules/budget/views/Forecasts.vue'),
      meta: { title: 'Budget Forecasting' }
    },
    {
      path: 'budget/plans',
      name: 'BudgetPlans',
      component: () => import('@/modules/budget/views/BudgetPlanningView.vue'),
      meta: { title: 'Budget Plans' }
    },
    {
      path: 'budget/forecasts',
      name: 'BudgetForecasts',
      component: () => import('@/modules/budget/views/Forecasts.vue'),
      meta: { title: 'Budget Forecasts' }
    },
    {
      path: 'budget/scenarios',
      name: 'BudgetScenarios',
      component: () => import('@/modules/budget/views/Scenarios.vue'),
      meta: { title: 'Budget Scenarios' }
    },
    // HRM Module - Lazy loaded
    ...hrmRoutes,
    // Payroll - Lazy loaded
    {
      path: 'payroll',
      name: 'Payroll',
      component: () => import(/* webpackChunkName: "payroll-module" */ '@/modules/payroll/views/AnalyticsDashboard.vue'),
      meta: { title: 'Payroll' }
    },
    {
      path: 'payroll/employees',
      name: 'PayrollEmployees',
      component: () => import('@/modules/payroll/views/EmployeeManagementView.vue'),
      meta: { title: 'Payroll Employees' }
    },
    {
      path: 'payroll/payruns',
      name: 'PayrollPayruns',
      component: () => import('@/modules/payroll/views/PayRunListView.vue'),
      meta: { title: 'Payroll Runs' }
    },
    {
      path: 'payroll/payslips',
      name: 'PayrollPayslips',
      component: () => import('@/modules/payroll/views/PayslipsView.vue'),
      meta: { title: 'Payslips' }
    },
    {
      path: 'payroll/deductions',
      name: 'PayrollDeductions',
      component: () => import('@/modules/payroll/views/DeductionsView.vue'),
      meta: { title: 'Payroll Deductions' }
    },
    {
      path: 'payroll/taxes',
      name: 'PayrollTaxes',
      component: () => import('@/modules/payroll/views/TaxesView.vue'),
      meta: { title: 'Payroll Taxes' }
    },
    {
      path: 'payroll/reports',
      name: 'PayrollReports',
      component: () => import('@/modules/payroll/views/ReportsView.vue'),
      meta: { title: 'Payroll Reports' }
    },
    // Tax Management - Lazy loaded
    {
      path: 'tax',
      name: 'TaxManagement',
      component: () => import(/* webpackChunkName: "tax-module" */ '@/modules/tax/views/TaxDashboard.vue'),
      meta: { title: 'Tax Management' }
    },
    {
      path: 'tax/codes',
      name: 'TaxCodes',
      component: () => import('@/modules/tax/views/TaxCodes.vue'),
      meta: { title: 'Tax Codes' }
    },
    {
      path: 'tax/rates',
      name: 'TaxRates',
      component: () => import('@/modules/tax/views/TaxRates.vue'),
      meta: { title: 'Tax Rates' }
    },
    {
      path: 'tax/jurisdictions',
      name: 'TaxJurisdictions',
      component: () => import('@/modules/tax/views/TaxJurisdictions.vue'),
      meta: { title: 'Tax Jurisdictions' }
    },
    {
      path: 'tax/exemptions',
      name: 'TaxExemptions',
      component: () => import('@/modules/tax/views/TaxExemptionsView.vue'),
      meta: { title: 'Tax Exemptions' }
    },
    {
      path: 'tax/returns',
      name: 'TaxReturns',
      component: () => import('@/modules/tax/views/TaxReturns.vue'),
      meta: { title: 'Tax Returns' }
    },
    {
      path: 'tax/compliance',
      name: 'TaxCompliance',
      component: () => import('@/modules/tax/views/TaxCompliance.vue'),
      meta: { title: 'Tax Compliance' }
    },
    {
      path: 'tax/reports',
      name: 'TaxReports',
      component: () => import('@/modules/tax/views/TaxReports.vue'),
      meta: { title: 'Tax Reports' }
    },
    // Reports
    {
      path: 'reports',
      name: 'Reports',
      component: () => import('@/modules/reports/views/ReportsView.vue'),
      meta: { title: 'All Reports' }
    },
    {
      path: 'reports/financial',
      name: 'FinancialReports',
      component: () => import('@/modules/reports/views/FinancialReportsView.vue'),
      meta: { title: 'Financial Reports' }
    },
    {
      path: 'reports/operational',
      name: 'OperationalReports',
      component: () => import('@/modules/reports/views/OperationalReportsView.vue'),
      meta: { title: 'Operational Reports' }
    },
    {
      path: 'reports/compliance',
      name: 'ComplianceReports',
      component: () => import('@/modules/reports/views/ComplianceReportsView.vue'),
      meta: { title: 'Compliance Reports' }
    },
    {
      path: 'reports/custom',
      name: 'CustomReports',
      component: () => import('@/modules/reports/views/CustomReportsView.vue'),
      meta: { title: 'Custom Reports' }
    },
    {
      path: 'reports/aged',
      name: 'AgedReports',
      component: () => import('@/modules/reports/views/AgedReportsView.vue'),
      meta: { title: 'Aged Receivables/Payables' }
    },
    {
      path: 'reports/tax',
      name: 'TaxReports',
      component: () => import('@/modules/reports/views/TaxReportsView.vue'),
      meta: { title: 'Tax Reports' }
    },
    {
      path: 'reports/audit',
      name: 'AuditReports',
      component: () => import('@/modules/reports/views/AuditReportsView.vue'),
      meta: { title: 'Audit Reports' }
    },
    {
      path: 'reports/income-statement',
      name: 'IncomeStatement',
      component: () => import('@/modules/reports/views/IncomeStatementView.vue'),
      meta: { title: 'Income Statement' }
    },
    {
      path: 'reports/cash-flow',
      name: 'CashFlowStatement',
      component: () => import('@/modules/reports/views/CashFlowView.vue'),
      meta: { title: 'Cash Flow Statement' }
    },
    {
      path: 'reports/ap-aging',
      name: 'APAging',
      component: () => import('@/modules/reports/views/AgedReportsView.vue'),
      meta: { title: 'AP Aging Report' }
    },
    {
      path: 'reports/ar-aging',
      name: 'ARAging',
      component: () => import('@/modules/reports/views/AgedReportsView.vue'),
      meta: { title: 'AR Aging Report' }
    },
    // Approvals
    {
      path: 'approvals',
      name: 'Approvals',
      component: () => import('@/views/approvals/ApprovalsView.vue'),
      meta: { title: 'Approval Workflows' }
    },
    // AI & Business Intelligence
    {
      path: 'ai',
      name: 'AIInsights',
      component: () => import('@/modules/ai-bi/views/AIDashboard.vue'),
      meta: { title: 'AI Insights' }
    },
    {
      path: 'ai/assistant',
      name: 'AIAssistant',
      component: () => import('@/modules/ai-bi/views/AIAssistant.vue'),
      meta: { title: 'AI Assistant' }
    },
    {
      path: 'bi',
      name: 'BIDashboard',
      component: () => import('@/modules/ai-bi/views/BusinessIntelligence.vue'),
      meta: { title: 'BI Dashboard' }
    },
    {
      path: 'bi/analytics',
      name: 'BIAnalytics',
      component: () => import('@/modules/ai-bi/views/Reports.vue'),
      meta: { title: 'BI Analytics' }
    },
    // Super Admin
    {
      path: 'super-admin',
      name: 'SuperAdmin',
      component: () => import('@/modules/super-admin/views/SuperAdminView.vue'),
      meta: { title: 'Super Admin', requiresAdmin: true }
    },
    {
      path: 'super-admin/system-monitoring',
      name: 'SystemMonitoring',
      component: () => import('@/modules/super-admin/views/SystemMonitoring.vue'),
      meta: { title: 'System Monitoring', requiresAdmin: true }
    },
    {
      path: 'super-admin/global-config',
      name: 'GlobalConfiguration',
      component: () => import('@/modules/super-admin/views/GlobalConfiguration.vue'),
      meta: { title: 'Global Configuration', requiresAdmin: true }
    },
    {
      path: 'super-admin/platform-analytics',
      name: 'PlatformAnalytics',
      component: () => import('@/modules/super-admin/views/PlatformAnalytics.vue'),
      meta: { title: 'Platform Analytics', requiresAdmin: true }
    },
    {
      path: 'super-admin/license-management',
      name: 'LicenseManagement',
      component: () => import('@/modules/super-admin/views/LicenseManagement.vue'),
      meta: { title: 'License Management', requiresAdmin: true }
    },
    {
      path: 'super-admin/system-health',
      name: 'SystemHealthDashboard',
      component: () => import('@/modules/super-admin/views/SystemHealthDashboard.vue'),
      meta: { title: 'System Health Dashboard', requiresAdmin: true }
    },
    // Settings
    {
      path: 'settings',
      name: 'Settings',
      component: () => import('@/modules/settings/views/SettingsView.vue'),
      meta: { title: 'Settings' },
      redirect: { name: 'GeneralSettings' },
      children: [
        {
          path: 'general',
          name: 'GeneralSettings',
          component: () => import('@/modules/settings/views/GeneralSettings.vue'),
          meta: { title: 'General Settings' }
        },
        {
          path: 'company',
          name: 'CompanyProfile',
          component: () => import('@/modules/settings/views/CompanyProfileSettings.vue'),
          meta: { title: 'Company Profile' }
        },
        {
          path: 'chart-of-accounts',
          name: 'SettingsChartOfAccounts',
          component: () => import('@/modules/settings/views/ChartOfAccountsSettings.vue'),
          meta: { title: 'Chart of Accounts' }
        },
        {
          path: 'tax-rates',
          name: 'SettingsTaxRates',
          component: () => import('@/modules/settings/views/TaxRateSettings.vue'),
          meta: { title: 'Tax Rate Management' }
        },
        {
          path: 'users',
          name: 'UserManagement',
          component: () => import('@/modules/settings/views/UserManagement.vue'),
          meta: { title: 'User Management' }
        },
        {
          path: 'system',
          name: 'SystemPreferences',
          component: () => import('@/modules/settings/views/SystemPreferences.vue'),
          meta: { title: 'System Preferences' }
        },
        {
          path: 'integrations',
          name: 'IntegrationSettings',
          component: () => import('@/modules/settings/views/IntegrationSettings.vue'),
          meta: { title: 'Integration Settings' }
        },
        {
          path: 'backup',
          name: 'BackupRestore',
          component: () => import('@/modules/settings/views/BackupRestoreSettings.vue'),
          meta: { title: 'Backup & Restore' }
        },
        {
          path: 'currency',
          name: 'CurrencySettings',
          component: () => import('@/modules/settings/views/CurrencySettings.vue'),
          meta: { title: 'Currency Settings' }
        },
        {
          path: 'tenant',
          name: 'TenantManagement',
          component: () => import('@/modules/super-admin/views/TenantManagement.vue'),
          meta: { title: 'Tenant Management', requiresAdmin: true }
        },
        {
          path: 'security',
          name: 'SecuritySettings',
          component: () => import('@/modules/settings/views/SecuritySettings.vue'),
          meta: { title: 'Security Settings' }
        }
      ]
    }
  ]
};

// Create router instance
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    ...publicRoutes.map(route => toRouteRecord(route)),
    toRouteRecord(mainAppRoute)
  ],
  scrollBehavior(_to, _from, savedPosition) {
    return savedPosition || { top: 0 };
  }
});

// Router guard for authentication
router.beforeEach((to, _from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
  const requiresGuest = to.matched.some(record => record.meta.requiresGuest);
  const token = localStorage.getItem('token') || sessionStorage.getItem('token');

  console.log('Router guard:', { path: to.path, requiresAuth, requiresGuest, hasToken: !!token });

  if (requiresAuth && !token) {
    console.log('Redirecting to login - auth required but no token');
    next('/auth/login');
  } else if (requiresGuest && token) {
    console.log('Redirecting to dashboard - guest page but has token');
    next('/');
  } else {
    next();
  }
});

// Handle navigation errors
router.onError((error) => {
  console.error('Router error:', error);
  // You can add error reporting here
});

export default router;
