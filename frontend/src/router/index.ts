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
      name: 'HRM',
      component: () => import('@/modules/hrm/views/HRMView.vue'),
      meta: { title: 'Human Resources' }
    },
    // Payroll
    {
      path: 'payroll',
      name: 'Payroll',
      component: () => import('@/modules/payroll/views/AnalyticsDashboard.vue'),
      meta: { title: 'Payroll' }
    },
    // Settings
    {
      path: 'settings',
      name: 'Settings',
      component: () => import('@/modules/settings/views/SettingsView.vue'),
      meta: { title: 'Settings' },
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
