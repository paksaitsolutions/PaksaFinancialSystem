import { createRouter, createWebHistory, type RouteRecordRaw, type RouteMeta } from 'vue-router';
import { useAuthStore } from '@/modules/auth/store/auth.store';

// Extend the RouteMeta interface to include our custom properties
declare module 'vue-router' {
  interface RouteMeta {
    title?: string;
    requiresAuth?: boolean;
    requiresGuest?: boolean;
    requiresAdmin?: boolean;
    permission?: string | string[];
    module?: string;
    icon?: string;
    breadcrumb?: boolean | string | string[];
    hidden?: boolean;
    roles?: string[];
    layout?: string;
  }
}

// Use Vue Router's built-in types
type AppRouteRecordRaw = RouteRecordRaw;

// Public routes (no authentication required)
const publicRoutes: AppRouteRecordRaw[] = [
  {
    path: '/auth',
    component: () => import('@/layouts/AuthLayout.vue'),
    meta: { requiresGuest: true, layout: null },
    redirect: '/auth/login',
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
        meta: { title: 'Set New Password', layout: 'AuthLayout' }
      }
    ]
  },
  {
    path: '/error/404',
    name: 'Error404',
    component: () => import('@/views/common/NotFound.vue'),
    meta: { 
      title: 'Page Not Found',
      requiresAuth: false,
      layout: 'ErrorLayout'  // Use a simple layout for error pages
    }
  },
  {
    path: '/error/403',
    name: 'Error403',
    component: () => import('@/views/common/Forbidden.vue'),
    meta: { 
      title: 'Access Denied',
      requiresAuth: false,
      layout: 'ErrorLayout'  // Use a simple layout for error pages
    }
  },
  {
    path: '/error/500',
    name: 'Error500',
    component: () => import('@/views/common/ServerError.vue'),
    meta: { 
      title: 'Server Error',
      requiresAuth: false,
      layout: 'ErrorLayout'  // Use a simple layout for error pages
    }
  }
];

// Helper function to create module routes
function createModuleRoute(
  name: string,
  path: string,
  routes: RouteRecordRaw[],
  meta?: RouteMeta
): RouteRecordRaw {
  return {
    path: `/${path}`,
    name,
    component: () => import(`@/layouts/MainLayout.vue`),
    meta: {
      ...meta,
      module: path,
      requiresAuth: true,
      layout: null  // Set to null since MainLayout is used as component
    },
    children: routes
  };
}

// Module routes
const moduleRoutes = {
  dashboard: createModuleRoute('Dashboard', 'dashboard', [
    {
      path: '',
      name: 'DashboardHome',
      component: () => import('@/views/home/Home.vue'),
      meta: { title: 'Overview' }
    },
    {
      path: 'analytics',
      name: 'DashboardAnalytics',
      component: () => import('@/views/home/Home.vue'), // Using Home as a placeholder
      meta: { title: 'Analytics', icon: 'chart-line' }
    }
  ]),
  
  generalLedger: createModuleRoute('General Ledger', 'gl', [
    {
      path: 'dashboard',
      name: 'GLDashboard',
      component: () => import('@/modules/general-ledger/views/Dashboard.vue'),
      meta: { title: 'Dashboard' }
    },
    {
      path: 'chart-of-accounts',
      name: 'ChartOfAccounts',
      component: () => import('@/modules/general-ledger/views/ChartOfAccounts.vue'),
      meta: { title: 'Chart of Accounts' }
    },
    {
      path: 'journal-entries',
      name: 'JournalEntries',
      component: () => import('@/modules/general-ledger/views/journal-entries/JournalEntriesView.vue'),
      meta: { title: 'Journal Entries' }
    },
    {
      path: 'trial-balance',
      name: 'TrialBalance',
      component: () => import('@/modules/general-ledger/views/TrialBalanceView.vue'),
      meta: { title: 'Trial Balance' }
    },
    {
      path: 'financial-statements',
      name: 'FinancialStatements',
      component: () => import('@/modules/general-ledger/views/financial-statements/FinancialStatementsView.vue'),
      meta: { title: 'Financial Statements' }
    },
    {
      path: 'reports',
      name: 'GLReports',
      component: () => import('@/modules/general-ledger/views/GLReportingDashboard.vue'),
      meta: { title: 'Reports' }
    }
  ]),
  
  accountsPayable: createModuleRoute('Accounts Payable', 'ap', [
    {
      path: '',
      name: 'APDashboard',
      component: () => import('@/modules/accounts-payable/views/APDashboard.vue'),
      meta: { title: 'Dashboard' }
    },
    {
      path: 'vendors',
      name: 'Vendors',
      component: () => import('@/modules/accounts-payable/views/VendorsView.vue'),
      meta: { title: 'Vendors' }
    },
    {
      path: 'invoices',
      name: 'Invoices',
      component: () => import('@/modules/accounts-payable/views/InvoiceManagementView.vue'),
      meta: { title: 'Invoices' }
    },
    {
      path: 'payments',
      name: 'Payments',
      component: () => import('@/modules/accounts-payable/views/PaymentManagementView.vue'),
      meta: { title: 'Payments' }
    },
    {
      path: 'credit-memos',
      name: 'CreditMemos',
      component: () => import('@/modules/accounts-payable/views/CreditMemoManagementView.vue'),
      meta: { title: 'Credit Memos' }
    },
    {
      path: 'reports',
      name: 'APReports',
      component: () => import('@/modules/accounts-payable/views/APDashboard.vue'),
      meta: { title: 'Reports' }
    }
  ]),
  
  accountsReceivable: createModuleRoute('Accounts Receivable', 'ar', [
    {
      path: '',
      name: 'ARDashboard',
      component: () => import('@/modules/accounts-receivable/views/AccountsReceivableView.vue'),
      meta: { title: 'Dashboard' }
    },
    {
      path: 'customers',
      name: 'Customers',
      component: () => import('@/modules/accounts-receivable/views/CustomersView.vue'),
      meta: { title: 'Customers' }
    },
    {
      path: 'invoices',
      name: 'ARInvoices',
      component: () => import('@/modules/accounts-receivable/views/InvoiceProcessingView.vue'),
      meta: { title: 'Invoices' }
    },
    {
      path: 'payments',
      name: 'ARPayments',
      component: () => import('@/modules/accounts-receivable/views/ARPaymentsAdvanced.vue'),
      meta: { title: 'Payments' }
    },
    {
      path: 'collections',
      name: 'Collections',
      component: () => import('@/modules/accounts-receivable/views/CollectionsManagementView.vue'),
      meta: { title: 'Collections' }
    },
    {
      path: 'analytics',
      name: 'ARAnalytics',
      component: () => import('@/modules/accounts-receivable/ARAnalyticsView.vue'),
      meta: { title: 'Analytics' }
    }
  ]),
  
  cashManagement: createModuleRoute('Cash Management', 'cash', [
    {
      path: '',
      name: 'CashDashboard',
      component: () => import('@/modules/cash-management/views/CashManagementView.vue'),
      meta: { title: 'Dashboard' }
    },
    {
      path: 'bank-accounts',
      name: 'BankAccounts',
      component: () => import('@/modules/cash-management/views/BankAccounts.vue'),
      meta: { title: 'Bank Accounts' }
    },
    {
      path: 'transactions',
      name: 'CashTransactions',
      component: () => import('@/modules/cash-management/views/Transactions.vue'),
      meta: { title: 'Transactions' }
    },
    {
      path: 'reconciliation',
      name: 'Reconciliation',
      component: () => import('@/modules/cash-management/views/Reconciliation.vue'),
      meta: { title: 'Reconciliation' }
    },
    {
      path: 'forecast',
      name: 'CashForecast',
      component: () => import('@/modules/cash-management/views/CashFlowForecastingView.vue'),
      meta: { title: 'Cash Flow Forecast' }
    },
    {
      path: 'banking-integration',
      name: 'BankingIntegration',
      component: () => import('@/modules/cash-management/views/BankingIntegrationView.vue'),
      meta: { title: 'Banking Integration' }
    }
  ]),
  
  fixedAssets: createModuleRoute('Fixed Assets', 'fixed-assets', [
    {
      path: '',
      name: 'FixedAssetsDashboard',
      component: () => import('@/modules/fixed-assets/views/FixedAssetsView.vue'),
      meta: { title: 'Dashboard' }
    },
    {
      path: 'depreciation',
      name: 'Depreciation',
      component: () => import('@/modules/fixed-assets/views/DepreciationView.vue'),
      meta: { title: 'Depreciation' }
    },
    {
      path: 'maintenance',
      name: 'Maintenance',
      component: () => import('@/modules/fixed-assets/views/MaintenanceView.vue'),
      meta: { title: 'Maintenance' }
    }
  ]),
  
  payroll: createModuleRoute('Payroll', 'payroll', [
    {
      path: '',
      name: 'PayrollDashboard',
      component: () => import('@/modules/payroll/views/AnalyticsDashboard.vue'),
      meta: { title: 'Dashboard' }
    },
    {
      path: 'employees',
      name: 'PayrollEmployees',
      component: () => import('@/modules/payroll/views/EmployeeManagementView.vue'),
      meta: { title: 'Employee Management', requiresAdmin: true }
    },
    {
      path: 'pay-runs',
      name: 'PayRuns',
      component: () => import('@/modules/payroll/views/PayRunListView.vue'),
      meta: { title: 'Pay Runs', requiresAdmin: true }
    },
    {
      path: 'pay-runs/create',
      name: 'PayRunCreate',
      component: () => import('@/modules/payroll/views/PayRunCreateView.vue'),
      meta: { title: 'Create Pay Run', requiresAdmin: true }
    },
    {
      path: 'pay-runs/:id',
      name: 'PayRunDetail',
      component: () => import('@/modules/payroll/views/PayRunView.vue'),
      meta: { title: 'Pay Run Details', requiresAdmin: true }
    },
    {
      path: 'payslips',
      name: 'Payslips',
      component: () => import('@/modules/payroll/views/PayslipsView.vue'),
      meta: { title: 'Payslips' }
    },
    {
      path: 'deductions-benefits',
      name: 'DeductionsBenefits',
      component: () => import('@/modules/payroll/views/PayrollDeductionsBenefitsView.vue'),
      meta: { title: 'Deductions & Benefits', requiresAdmin: true }
    },
    {
      path: 'reports',
      name: 'PayrollReports',
      component: () => import('@/modules/payroll/views/PayrollReportsView.vue'),
      meta: { title: 'Reports' }
    },
    {
      path: 'settings',
      name: 'PayrollSettings',
      component: () => import('@/modules/payroll/views/PayrollSettingsView.vue'),
      meta: { title: 'Settings', requiresAdmin: true }
    }
  ]),
  
  budget: createModuleRoute('Budget Management', 'budget', [
    {
      path: '',
      name: 'BudgetDashboard',
      component: () => import('@/modules/budget/views/BudgetDashboard.vue'),
      meta: { title: 'Dashboard' }
    },
    {
      path: 'planning',
      name: 'BudgetPlanning',
      component: () => import('@/modules/budget/views/BudgetPlanningView.vue'),
      meta: { title: 'Budget Planning' }
    },
    {
      path: 'monitoring',
      name: 'BudgetMonitoring',
      component: () => import('@/modules/budget/views/BudgetMonitoringView.vue'),
      meta: { title: 'Budget Monitoring' }
    },
    {
      path: 'approval',
      name: 'BudgetApproval',
      component: () => import('@/modules/budget/views/BudgetApprovalView.vue'),
      meta: { title: 'Budget Approval', requiresAdmin: true }
    },
    {
      path: 'forecasts',
      name: 'BudgetForecasts',
      component: () => import('@/modules/budget/views/Forecasts.vue'),
      meta: { title: 'Forecasts' }
    },
    {
      path: 'scenarios',
      name: 'BudgetScenarios',
      component: () => import('@/modules/budget/views/Scenarios.vue'),
      meta: { title: 'Scenarios' }
    },
    {
      path: 'reports',
      name: 'BudgetReports',
      component: () => import('@/modules/budget/views/BudgetReportView.vue'),
      meta: { title: 'Reports' }
    }
  ]),
  
  inventory: createModuleRoute('Inventory Management', 'inventory', [
    {
      path: '',
      name: 'InventoryDashboard',
      component: () => import('@/modules/inventory/views/InventoryManagementView.vue'),
      meta: { title: 'Dashboard' }
    },
    {
      path: 'items',
      name: 'InventoryItems',
      component: () => import('@/modules/inventory/views/ItemsView.vue'),
      meta: { title: 'Items' }
    },
    {
      path: 'locations',
      name: 'InventoryLocations',
      component: () => import('@/modules/inventory/views/LocationsView.vue'),
      meta: { title: 'Locations' }
    },
    {
      path: 'adjustments',
      name: 'InventoryAdjustments',
      component: () => import('@/modules/inventory/views/AdjustmentsView.vue'),
      meta: { title: 'Adjustments' }
    },
    {
      path: 'reports',
      name: 'InventoryReports',
      component: () => import('@/modules/inventory/views/ReportsView.vue'),
      meta: { title: 'Reports' }
    }
  ]),
  
  tax: createModuleRoute('Tax Management', 'tax', [
    {
      path: '',
      name: 'TaxDashboard',
      component: () => import('@/modules/tax/views/TaxDashboard.vue'),
      meta: { title: 'Dashboard' }
    },
    {
      path: 'rates',
      name: 'TaxRates',
      component: () => import('@/modules/tax/views/TaxRates.vue'),
      meta: { title: 'Tax Rates' }
    },
    {
      path: 'codes',
      name: 'TaxCodes',
      component: () => import('@/modules/tax/views/TaxCodes.vue'),
      meta: { title: 'Tax Codes' }
    },
    {
      path: 'jurisdictions',
      name: 'TaxJurisdictions',
      component: () => import('@/modules/tax/views/TaxJurisdictions.vue'),
      meta: { title: 'Jurisdictions' }
    },
    {
      path: 'returns',
      name: 'TaxReturns',
      component: () => import('@/modules/tax/views/TaxReturns.vue'),
      meta: { title: 'Tax Returns' }
    },
    {
      path: 'exemptions',
      name: 'TaxExemptions',
      component: () => import('@/modules/tax/views/TaxExemptionsView.vue'),
      meta: { title: 'Tax Exemptions' }
    },
    {
      path: 'compliance',
      name: 'TaxCompliance',
      component: () => import('@/modules/tax/views/TaxComplianceDashboard.vue'),
      meta: { title: 'Compliance' }
    },
    {
      path: 'analytics',
      name: 'TaxAnalytics',
      component: () => import('@/modules/tax/views/TaxAnalyticsDashboard.vue'),
      meta: { title: 'Analytics' }
    },
    {
      path: 'reports',
      name: 'TaxReports',
      component: () => import('@/modules/tax/views/TaxReports.vue'),
      meta: { title: 'Reports' }
    }
  ]),
  
  hrm: createModuleRoute('Human Resources', 'hrm', [
    {
      path: '',
      name: 'HRMDashboard',
      component: () => import('@/modules/hrm/views/HRMView.vue'),
      meta: { title: 'Dashboard' }
    },
    {
      path: 'attendance',
      name: 'Attendance',
      component: () => import('@/modules/hrm/views/AttendanceView.vue'),
      meta: { title: 'Attendance' }
    },
    {
      path: 'leave-management',
      name: 'LeaveManagement',
      component: () => import('@/modules/hrm/views/LeaveManagementView.vue'),
      meta: { title: 'Leave Management' }
    },
    {
      path: 'performance',
      name: 'Performance',
      component: () => import('@/modules/hrm/views/PerformanceView.vue'),
      meta: { title: 'Performance' }
    }
  ]),
  
  reports: createModuleRoute('Reports', 'reports', [
    {
      path: '',
      name: 'ReportsDashboard',
      component: () => import('@/modules/reports/views/ReportsView.vue'),
      meta: { title: 'Dashboard' }
    },
    {
      path: 'financial',
      name: 'FinancialReports',
      component: () => import('@/modules/reports/views/FinancialReportsView.vue'),
      meta: { title: 'Financial Reports' }
    },
    {
      path: 'balance-sheet',
      name: 'BalanceSheet',
      component: () => import('@/modules/reports/views/BalanceSheetReport.vue'),
      meta: { title: 'Balance Sheet' }
    },
    {
      path: 'income-statement',
      name: 'IncomeStatement',
      component: () => import('@/modules/reports/views/IncomeStatementReport.vue'),
      meta: { title: 'Income Statement' }
    },
    {
      path: 'cash-flow',
      name: 'CashFlowReport',
      component: () => import('@/modules/reports/views/CashFlowReport.vue'),
      meta: { title: 'Cash Flow' }
    },
    {
      path: 'ap-aging',
      name: 'APAging',
      component: () => import('@/modules/reports/views/APAgingReport.vue'),
      meta: { title: 'AP Aging' }
    },
    {
      path: 'ar-aging',
      name: 'ARAging',
      component: () => import('@/modules/reports/views/ARAgingReport.vue'),
      meta: { title: 'AR Aging' }
    },
    {
      path: 'templates',
      name: 'ReportTemplates',
      component: () => import('@/modules/reports/views/ReportTemplatesView.vue'),
      meta: { title: 'Templates' }
    },
    {
      path: 'schedules',
      name: 'ReportSchedules',
      component: () => import('@/modules/reports/views/ReportSchedulesView.vue'),
      meta: { title: 'Schedules' }
    }
  ]),
  
  aiBi: createModuleRoute('AI & Business Intelligence', 'ai-bi', [
    {
      path: '',
      name: 'AIBIDashboard',
      component: () => import('@/modules/ai-bi/views/AIDashboard.vue'),
      meta: { title: 'Dashboard' }
    },
    {
      path: 'assistant',
      name: 'AIAssistant',
      component: () => import('@/modules/ai-bi/views/AIAssistant.vue'),
      meta: { title: 'AI Assistant' }
    },
    {
      path: 'business-intelligence',
      name: 'BusinessIntelligence',
      component: () => import('@/modules/ai-bi/views/BusinessIntelligence.vue'),
      meta: { title: 'Business Intelligence' }
    },
    {
      path: 'reports',
      name: 'AIReports',
      component: () => import('@/modules/ai-bi/views/Reports.vue'),
      meta: { title: 'AI Reports' }
    }
  ]),
  
  settings: createModuleRoute('Settings', 'settings', [
    {
      path: '',
      name: 'SettingsDashboard',
      component: () => import('@/modules/settings/views/SystemConfigurationView.vue'),
      meta: { title: 'System Configuration', requiresAdmin: true }
    },
    {
      path: 'company',
      name: 'CompanySettings',
      component: () => import('@/modules/settings/views/CompanySettingsView.vue'),
      meta: { title: 'Company Settings', requiresAdmin: true }
    },
    {
      path: 'currency',
      name: 'CurrencyManagement',
      component: () => import('@/modules/settings/views/CurrencyManagementView.vue'),
      meta: { title: 'Currency Management', requiresAdmin: true }
    }
  ]),
  
  userManagement: createModuleRoute('User Management', 'users', [
    {
      path: '',
      name: 'UserManagement',
      component: () => import('@/modules/user/views/UserManagementView.vue'),
      meta: { title: 'User Management', requiresAdmin: true }
    }
  ]),
  
  superAdmin: createModuleRoute('Super Admin', 'super-admin', [
    {
      path: '',
      name: 'SuperAdminDashboard',
      component: () => import('@/modules/super-admin/views/SuperAdminView.vue'),
      meta: { title: 'Super Admin Dashboard', requiresAdmin: true }
    }
  ]),
  
  compliance: createModuleRoute('Compliance', 'compliance', [
    {
      path: '',
      name: 'ComplianceDashboard',
      component: () => import('@/modules/compliance/views/DashboardView.vue'),
      meta: { title: 'Compliance Dashboard' }
    },
    {
      path: 'settings',
      name: 'ComplianceSettings',
      component: () => import('@/modules/compliance/views/SettingsView.vue'),
      meta: { title: 'Compliance Settings', requiresAdmin: true }
    }
  ])
};

// Define the main application routes
const appRoutes: RouteRecordRaw[] = [
  // Public routes (auth, errors, etc.)
  ...publicRoutes,
  
  // Main app routes (require authentication)
  {
    path: '/',
    component: () => import('@/layouts/AppLayout.vue'),
    meta: { 
      requiresAuth: true,
      layout: null  // Set to null since AppLayout is used as component
    },
    children: [
      // Dashboard
      // Root path loads Home component directly
      {
        path: '',
        name: 'Dashboard',
        component: () => import('@/views/home/Home.vue'),
        meta: { title: 'Dashboard' }
      },
      // Root-level module routes
      {
        path: '/ap',
        redirect: { name: 'APDashboard' },
        meta: { title: 'Accounts Payable' }
      },
      {
        path: '/ar',
        redirect: { name: 'ARDashboard' },
        meta: { title: 'Accounts Receivable' }
      },
      {
        path: '/gl',
        redirect: { name: 'GLDashboard' },
        meta: { title: 'General Ledger' }
      },
      {
        path: '/cash',
        redirect: { name: 'CashDashboard' },
        meta: { title: 'Cash Management' }
      },
      {
        path: '/fixed-assets',
        redirect: { name: 'FixedAssetsDashboard' },
        meta: { title: 'Fixed Assets' }
      },
      {
        path: '/payroll',
        redirect: { name: 'PayrollDashboard' },
        meta: { title: 'Payroll' }
      },
      {
        path: '/budget',
        redirect: { name: 'BudgetDashboard' },
        meta: { title: 'Budget Management' }
      },
      {
        path: '/inventory',
        redirect: { name: 'InventoryDashboard' },
        meta: { title: 'Inventory Management' }
      },
      {
        path: '/tax',
        redirect: { name: 'TaxDashboard' },
        meta: { title: 'Tax Management' }
      },
      {
        path: '/hrm',
        redirect: { name: 'HRMDashboard' },
        meta: { title: 'Human Resources' }
      },
      {
        path: '/reports',
        redirect: { name: 'ReportsDashboard' },
        meta: { title: 'Reports' }
      },
      {
        path: '/ai-bi',
        redirect: { name: 'AIBIDashboard' },
        meta: { title: 'AI & Business Intelligence' }
      },
      {
        path: '/settings',
        redirect: { name: 'SettingsDashboard' },
        meta: { title: 'Settings' }
      },
      {
        path: '/users',
        redirect: { name: 'UserManagement' },
        meta: { title: 'User Management' }
      },
      {
        path: '/super-admin',
        redirect: { name: 'SuperAdminDashboard' },
        meta: { title: 'Super Admin' }
      },
      {
        path: '/compliance',
        redirect: { name: 'ComplianceDashboard' },
        meta: { title: 'Compliance' }
      },
      // Module routes
      ...Object.values(moduleRoutes),
      // 404 page for authenticated users
      {
        path: ':pathMatch(.*)*',
        name: 'NotFound',
        component: () => import('@/views/errors/NotFound.vue'),
        meta: { requiresAuth: false }
      }
    ]
  }
];

// Create the router instance with all routes
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: appRoutes,
  // Using _ for unused parameters
  scrollBehavior(_, _savedPosition) {
    return { top: 0 };
  }
});

// Router guard for authentication
router.beforeEach(async (to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const requiresGuest = to.matched.some(record => record.meta.requiresGuest)
  const token = localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token')
  
  if (requiresAuth && !token) {
    // Redirect to login if authentication is required but user is not logged in
    next('/auth/login')
  } else if (requiresGuest && token) {
    // Redirect to dashboard if user is already logged in and trying to access guest pages
    next('/')
  } else {
    next()
  }
});

// Handle navigation errors
router.onError((error) => {
  console.error('Router error:', error);
  // You can add error reporting here
});

export default router;