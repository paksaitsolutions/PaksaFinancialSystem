import { createRouter, createWebHistory } from 'vue-router';
// Import Vue Router types
import type { 
  RouteRecordRaw, 
  RouteMeta,
  RouteRecordRedirectOption
} from 'vue-router';

// Type for route query parameters
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
  interface RouteLocationNormalized {
    query: RouteQuery;
  }
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
      requiresAuth: false,
      layout: 'ErrorLayout'
    }
  },
  {
    path: '/500',
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
  routes: AppRouteRecordRaw[],
  meta: RouteMeta = {}
): AppRouteRecordRaw {
  const route: AppRouteRecordRaw = {
    path: `/${path}`,
    name,
    component: () => import('@/layouts/MainLayout.vue'),
    meta: {
      ...meta,
      module: path,
      requiresAuth: true,
      layout: null  // Set to null since MainLayout is used as component
    },
    children: routes
  };
  
  return route;
}

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
      meta: { title: 'Dashboard' }
    },
    // General Ledger
    {
      path: 'gl',
      name: 'GeneralLedger',
      component: () => import('@/modules/general-ledger/views/Dashboard.vue'),
      meta: { title: 'General Ledger' }
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
    // Accounting
    {
      path: 'accounting/journal-entry',
      name: 'JournalEntry',
      component: () => import('@/modules/accounting/views/JournalEntryView.vue'),
      meta: { title: 'Journal Entry' }
    },
    // Accounts Payable
    {
      path: 'ap',
      name: 'AccountsPayable',
      component: () => import('@/modules/accounts-payable/views/APDashboard.vue'),
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
      path: 'ap/invoices',
      name: 'APInvoices',
      component: () => import('@/modules/accounts-payable/views/invoices/InvoicesView.vue'),
      meta: { title: 'AP Invoices' }
    },
    // Accounts Receivable
    {
      path: 'ar',
      name: 'AccountsReceivable',
      component: () => import('@/modules/accounts-receivable/views/AccountsReceivableView.vue'),
      meta: { title: 'Accounts Receivable' }
    },
    {
      path: 'accounts-receivable/invoices',
      name: 'ARInvoicesList',
      component: () => import('@/modules/accounts-receivable/views/AccountsReceivableView.vue'),
      meta: { title: 'AR Invoices' }
    },
    {
      path: 'ar/customers',
      name: 'ARCustomers',
      component: () => import('@/modules/accounts-receivable/views/CustomersView.vue'),
      meta: { title: 'Customers' }
    },
    // Cash Management
    {
      path: 'cash',
      name: 'CashManagement',
      component: () => import('@/modules/cash-management/views/CashManagementView.vue'),
      meta: { title: 'Cash Management' }
    },
    // Inventory
    {
      path: 'inventory',
      name: 'Inventory',
      component: () => import('@/modules/inventory/views/InventoryManagementView.vue'),
      meta: { title: 'Inventory' }
    },
    // Fixed Assets
    {
      path: 'fixed-assets',
      name: 'FixedAssets',
      component: () => import('@/modules/fixed-assets/views/FixedAssetsView.vue'),
      meta: { title: 'Fixed Assets' }
    },
    // Budget
    {
      path: 'budget',
      name: 'Budget',
      component: () => import('@/modules/budget/views/BudgetDashboard.vue'),
      meta: { title: 'Budget Management' }
    },
    // HRM
    {
      path: 'hrm',
      component: () => import('@/views/hrm/HrmDashboard.vue'),
      meta: { title: 'Human Resources' },
      children: [
        // Dashboard route with empty path and name 'HRM'
        {
          path: '',
          name: 'HRM',
          component: () => import('@/views/hrm/HrmDashboard.vue'),
          meta: { title: 'HRM Dashboard' }
        },
        // Employee Management
        {
          path: 'employees',
          name: 'HrmEmployees',
          component: () => import('@/views/hrm/EmployeesView.vue'),
          meta: { title: 'Employee Management' }
        },
        {
          path: 'departments',
          name: 'HrmDepartments',
          component: () => import('@/views/hrm/DepartmentsView.vue'),
          meta: { title: 'Department Management' }
        },
        {
          path: 'positions',
          name: 'HrmPositions',
          component: () => import('@/views/hrm/EmployeesView.vue'), // Using EmployeesView as a placeholder
          meta: { title: 'Position Management' }
        },
        // Attendance
        {
          path: 'attendance',
          name: 'HrmAttendance',
          component: () => import('@/views/hrm/EmployeesView.vue'), // Placeholder
          meta: { title: 'Attendance' }
        },
        // Leave Management
        {
          path: 'leave',
          name: 'HrmLeave',
          component: { render: () => null },
          meta: { title: 'Leave Management' },
          children: [
            {
              path: 'requests',
              name: 'HrmLeaveRequests',
              component: () => import('@/views/hrm/EmployeesView.vue') // Placeholder
            },
            {
              path: 'types',
              name: 'HrmLeaveTypes',
              component: () => import('@/views/hrm/EmployeesView.vue') // Placeholder
            },
            {
              path: 'calendar',
              name: 'HrmLeaveCalendar',
              component: () => import('@/views/hrm/EmployeesView.vue') // Placeholder
            },
            {
              path: 'balance',
              name: 'HrmLeaveBalance',
              component: () => import('@/views/hrm/EmployeesView.vue') // Placeholder
            }
          ]
        },
        // Recruitment
        {
          path: 'recruitment',
          name: 'HrmRecruitment',
          component: { render: () => null },
          meta: { title: 'Recruitment' },
          children: [
            {
              path: 'job-openings',
              name: 'HrmJobOpenings',
              component: () => import('@/views/hrm/EmployeesView.vue') // Placeholder
            },
            {
              path: 'candidates',
              name: 'HrmCandidates',
              component: () => import('@/views/hrm/EmployeesView.vue') // Placeholder
            },
            {
              path: 'interviews',
              name: 'HrmInterviews',
              component: () => import('@/views/hrm/EmployeesView.vue') // Placeholder
            },
            {
              path: 'onboarding',
              name: 'HrmOnboarding',
              component: () => import('@/views/hrm/EmployeesView.vue') // Placeholder
            }
          ]
        },
        // Performance
        {
          path: 'performance',
          name: 'HrmPerformance',
          component: { render: () => null },
          meta: { title: 'Performance' },
          children: [
            {
              path: 'appraisals',
              name: 'HrmAppraisals',
              component: () => import('@/views/hrm/EmployeesView.vue') // Placeholder
            },
            {
              path: 'goals',
              name: 'HrmGoals',
              component: () => import('@/views/hrm/EmployeesView.vue') // Placeholder
            },
            {
              path: 'training',
              name: 'HrmTraining',
              component: () => import('@/views/hrm/EmployeesView.vue') // Placeholder
            },
            {
              path: 'skills',
              name: 'HrmSkills',
              component: () => import('@/views/hrm/EmployeesView.vue') // Placeholder
            }
          ]
        },
        // Reports
        {
          path: 'reports',
          name: 'HrmReports',
          component: { render: () => null },
          meta: { title: 'Reports' },
          children: [
            {
              path: 'directory',
              name: 'HrmReportDirectory',
              component: () => import('@/views/hrm/EmployeesView.vue') // Placeholder - should be replaced with actual report directory component
            }
            // Additional report routes can be added here
          ]
        },
        // Catch-all route for HRM
        {
          path: ':pathMatch(.*)*',
          redirect: { name: 'HRM' }
        }
      ]
    },
    // Payroll
    {
      path: 'payroll',
      name: 'Payroll',
      component: () => import('@/modules/payroll/views/AnalyticsDashboard.vue'),
      meta: { title: 'Payroll' }
    },
    // Tax Management
    {
      path: 'tax',
      name: 'TaxManagement',
      component: () => import('@/modules/tax/views/TaxDashboard.vue'),
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
      component: () => import('@/modules/tax/views/TaxComplianceDashboard.vue'),
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
    // AI & Business Intelligence
    {
      path: 'ai-bi',
      name: 'AIBIDashboard',
      component: () => import('@/modules/ai-bi/views/AIDashboard.vue'),
      meta: { title: 'AI & BI Dashboard' }
    },
    {
      path: 'ai-bi/assistant',
      name: 'AIAssistant',
      component: () => import('@/modules/ai-bi/views/AIAssistant.vue'),
      meta: { title: 'AI Assistant' }
    },
    {
      path: 'ai-bi/intelligence',
      name: 'BusinessIntelligence',
      component: () => import('@/modules/ai-bi/views/BusinessIntelligence.vue'),
      meta: { title: 'Business Intelligence' }
    },
    {
      path: 'ai-bi/reports',
      name: 'AIBIReports',
      component: () => import('@/modules/ai-bi/views/Reports.vue'),
      meta: { title: 'AI/BI Reports' }
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
          path: 'users',
          name: 'UserManagement',
          component: () => import('@/modules/settings/views/UserManagement.vue'),
          meta: { title: 'User Management' }
        },
        {
          path: 'tenant',
          name: 'TenantSettings',
          component: () => import('@/modules/tenant/views/TenantManagement.vue'),
          meta: { title: 'Tenant Management' }
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

  if (requiresAuth && !token) {
    // Redirect to login if authentication is required but user is not logged in
    next('/auth/login');
  } else if (requiresGuest && token) {
    // Redirect to dashboard if user is already logged in and trying to access guest pages
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
