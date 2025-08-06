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
    meta: { requiresGuest: true },
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
      layout: 'MainLayout'  // Explicitly set layout for module routes
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
      name: 'Employees',
      component: () => import('@/modules/payroll/views/EmployeesView.vue'),
      meta: { 
        title: 'Employees',
        requiresAdmin: true
      }
    },
    {
      path: 'pay-runs',
      name: 'PayRuns',
      component: () => import('@/modules/payroll/views/PayRunsView.vue'),
      meta: { 
        title: 'Pay Runs',
        requiresAdmin: true
      }
    },
    {
      path: 'reports',
      name: 'PayrollReports',
      component: () => import('@/modules/payroll/views/ReportsView.vue'),
      meta: { title: 'Reports' }
    },
    {
      path: 'taxes',
      name: 'TaxSettings',
      component: () => import('@/modules/payroll/views/TaxSettingsView.vue'),
      meta: { 
        title: 'Tax Settings',
        requiresAdmin: true
      }
    }
  ]),
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
      layout: 'AppLayout'  // Explicitly set layout for app routes
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

// Temporarily disabled router guard for testing
// router.beforeEach((to, from, next) => {
//   next();
// });

// Handle navigation errors
router.onError((error) => {
  console.error('Router error:', error);
  // You can add error reporting here
});

export default router;