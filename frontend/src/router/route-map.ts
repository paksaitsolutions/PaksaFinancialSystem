import type { RouteRecordRaw } from 'vue-router';
import lazyLoad from './modules/allRoutes';
import { taxRoutes } from '@/modules/tax/routes';

/**
 * Complete route map for the application
 * This ensures all routes are properly defined and match the menu structure
 */

export const routeMap: RouteRecordRaw[] = [
  // Auth routes
  {
    path: '/auth',
    name: 'Auth',
    component: () => import('@/layouts/AuthLayout.vue'),
    meta: { requiresGuest: true },
    children: [
      {
        path: 'login',
        name: 'Login',
        component: () => import('@/views/auth/Login.vue'),
        meta: { title: 'Login' }
      },
      {
        path: 'register',
        name: 'Register',
        component: () => import('@/views/auth/Register.vue'),
        meta: { title: 'Register' }
      },
      {
        path: 'forgot-password',
        name: 'ForgotPassword',
        component: () => import('@/views/auth/ForgotPassword.vue'),
        meta: { title: 'Forgot Password' }
      },
      {
        path: 'reset-password',
        name: 'ResetPassword',
        component: () => import('@/views/auth/ResetPassword.vue'),
        meta: { title: 'Reset Password' }
      }
    ]
  },

  // Main app routes
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      // Dashboard
      {
        path: '',
        name: 'Home',
        component: () => import('@/views/Home.vue'),
        meta: { title: 'Dashboard' }
      },

      // General Ledger
      {
        path: 'gl',
        name: 'GL',
        redirect: '/gl/dashboard',
        meta: { 
          title: 'General Ledger', 
          icon: 'mdi-book-open-page-variant',
          requiresAuth: true 
        },
        children: [
          {
            path: 'dashboard',
            name: 'GLDashboard',
            component: () => import('@/modules/general-ledger/views/Dashboard.vue'),
            meta: { title: 'GL Dashboard' }
          },
          {
            path: 'accounts',
            name: 'ChartOfAccounts',
            component: () => import('@/modules/general-ledger/views/accounts/GLAccountsView.vue'),
            meta: { title: 'Chart of Accounts' }
          },
          {
            path: 'journal-entries',
            name: 'JournalEntries',
            component: () => import('@/modules/general-ledger/views/journal-entries/JournalEntriesView.vue'),
            meta: { title: 'Journal Entries' }
          },
          {
            path: 'recurring',
            name: 'RecurringTransactions',
            component: () => import('@/modules/general-ledger/views/recurring/RecurringJournalListView.vue'),
            meta: { title: 'Recurring Transactions' }
          },
          {
            path: 'financial-statements',
            name: 'FinancialStatements',
            component: () => import('@/modules/general-ledger/views/financial-statements/FinancialStatementsView.vue'),
            meta: { title: 'Financial Statements' }
          },
          {
            path: 'trial-balance',
            name: 'TrialBalance',
            component: () => import('@/modules/general-ledger/views/reports/TrialBalanceView.vue'),
            meta: { title: 'Trial Balance' }
          },
          {
            path: 'advanced',
            name: 'AdvancedGL',
            component: () => import('@/modules/general-ledger/views/AdvancedGL.vue'),
            meta: { title: 'Advanced GL' }
          }
        ]
      },

      // Accounts Payable
      {
        path: 'ap',
        name: 'AP',
        redirect: '/ap/vendors',
        meta: { 
          title: 'Accounts Payable', 
          icon: 'mdi-account-arrow-right',
          requiresAuth: true 
        },
        children: [
          {
            path: 'vendors',
            name: 'Vendors',
            component: () => import('@/modules/accounts-payable/views/VendorsAdvancedView.vue'),
            meta: { title: 'Vendors' }
          },
          {
            path: 'invoices',
            name: 'Invoices',
            component: () => import('@/modules/accounts-payable/views/invoices/InvoicesView.vue'),
            meta: { title: 'Invoices' }
          },
          {
            path: 'payments',
            name: 'APPayments',
            component: () => import('@/modules/accounts-payable/views/payments/PaymentsView.vue'),
            meta: { title: 'Payments' }
          }
        ]
      },

      // Accounts Receivable
      {
        path: 'ar',
        name: 'AR',
        redirect: '/ar/customers',
        meta: { 
          title: 'Accounts Receivable', 
          icon: 'mdi-account-arrow-left',
          requiresAuth: true 
        },
        children: [
          {
            path: 'customers',
            name: 'Customers',
            component: () => import('@/modules/accounts-receivable/views/CustomersAdvanced.vue'),
            meta: { title: 'Customers' }
          },
          {
            path: 'invoices',
            name: 'Invoices',
            component: () => import('@/modules/accounts-receivable/views/ARInvoicesAdvanced.vue'),
            meta: { title: 'Invoices' }
          },
          {
            path: 'payments',
            name: 'ARPayments',
            component: () => import('@/modules/accounts-receivable/views/ARPaymentsAdvanced.vue'),
            meta: { title: 'Receipts' }
          }
        ]
      },

      // Budget
      {
        path: 'budget',
        name: 'Budget',
        redirect: '/budget/plans',
        meta: { 
          title: 'Budget',
          icon: 'mdi-chart-areaspline',
          requiresAuth: true 
        },
        children: [
          {
            path: 'plans',
            name: 'BudgetPlans',
            component: () => import('@/modules/budget/views/BudgetView.vue'),
            meta: { title: 'Budget Plans' }
          },
          {
            path: 'forecasts',
            name: 'BudgetForecasts',
            component: () => import('@/modules/budget/views/Forecasts.vue'),
            meta: { title: 'Budget Forecasts' }
          },
          {
            path: 'scenarios',
            name: 'BudgetScenarios',
            component: () => import('@/modules/budget/views/Scenarios.vue'),
            meta: { title: 'Budget Scenarios' }
          },
          {
            path: 'reports',
            name: 'BudgetReports',
            component: () => import('@/modules/budget/views/BudgetReportView.vue'),
            meta: { title: 'Budget Reports' }
          },
          {
            path: 'approvals',
            name: 'BudgetApprovals',
            component: () => import('@/modules/budget/views/BudgetApprovalView.vue'),
            meta: { title: 'Budget Approvals' }
          }
        ]
      },

      // Cash Management
      {
        path: 'cash',
        name: 'CashManagement',
        redirect: '/cash/transactions',
        meta: { 
          title: 'Cash Management', 
          icon: 'mdi-cash-multiple',
          requiresAuth: true 
        },
        children: [
          {
            path: 'transactions',
            name: 'CashTransactions',
            component: () => import('@/modules/cash/views/Transactions.vue'),
            meta: { title: 'Transactions' }
          },
          {
            path: 'reconciliation',
            name: 'CashReconciliation',
            component: () => import('@/modules/cash/views/Reconciliation.vue'),
            meta: { title: 'Bank Reconciliation' }
          },
          {
            path: 'forecasting',
            name: 'CashForecasting',
            component: () => import('@/modules/cash/views/Forecasting.vue'),
            meta: { title: 'Cash Forecasting' }
          },
          {
            path: 'bank-accounts',
            name: 'BankAccounts',
            component: () => import('@/modules/cash/views/BankAccounts.vue'),
            meta: { title: 'Bank Accounts' }
          }
        ]
      },

      // Tax
      taxRoutes,
      
      // Payroll
      {
        path: 'payroll',
        name: 'Payroll',
        redirect: '/payroll/payruns',
        meta: { 
          title: 'Payroll', 
          icon: 'mdi-account-cash',
          requiresAuth: true 
        },
        children: [
          {
            path: 'payruns',
            name: 'Payruns',
            component: () => import('@/modules/payroll/views/PayRunListView.vue'),
            meta: { title: 'Pay Runs' }
          },
          {
            path: 'payruns/create',
            name: 'PayRunCreate',
            component: () => import('@/modules/payroll/views/PayRunCreateView.vue'),
            meta: { title: 'Create Pay Run' },
            props: true
          },
          {
            path: 'payruns/:id',
            name: 'PayRunView',
            component: () => import('@/modules/payroll/views/PayRunView.vue'),
            meta: { title: 'View Pay Run' },
            props: true
          }
          // Additional payroll routes can be added here as needed
        ]
      },

      // Tax
      {
        path: 'tax',
        name: 'Tax',
        redirect: '/tax/dashboard',
        meta: { title: 'Tax', icon: 'mdi-calculator' },
        children: [
          {
            path: 'dashboard',
            name: 'TaxDashboard',
            component: lazyLoad('@/modules/tax/views/TaxDashboard'),
            meta: { title: 'Tax Dashboard' }
          },
          {
            path: 'filing',
            name: 'TaxFiling',
            component: lazyLoad('@/modules/tax/views/TaxCompliance'),
            meta: { title: 'Tax Filing' }
          },
          {
            path: 'reports',
            name: 'TaxReports',
            component: lazyLoad('@/modules/tax/views/TaxReports'),
            meta: { title: 'Tax Reports' }
          }
        ]
      },

      // Reports
      {
        path: 'reports',
        name: 'Reports',
        redirect: '/reports/financial',
        meta: { 
          title: 'Reports',
          icon: 'mdi-chart-box',
          requiresAuth: true 
        },
        children: [
          {
            path: 'financial',
            name: 'FinancialReports',
            component: lazyLoad('reports/Financial'),
            meta: { title: 'Financial Reports' }
          },
          {
            path: 'operational',
            name: 'OperationalReports',
            component: lazyLoad('reports/Operational'),
            meta: { title: 'Operational Reports' }
          },
          {
            path: 'tax',
            name: 'TaxReports',
            component: lazyLoad('reports/Tax'),
            meta: { title: 'Tax Reports' }
          },
          {
            path: 'custom',
            name: 'CustomReports',
            component: lazyLoad('reports/Custom'),
            meta: { title: 'Custom Reports' }
          },
          {
            path: 'scheduled',
            name: 'ScheduledReports',
            component: lazyLoad('reports/Scheduled'),
            meta: { title: 'Scheduled Reports' }
          }
        ]
      },

      // Settings
      {
        path: 'settings',
        name: 'Settings',
        component: lazyLoad('settings/Index'),
        meta: { 
          title: 'Settings',
          icon: 'mdi-cog',
          requiresAuth: true
        },
        children: [
          {
            path: 'company',
            name: 'CompanySettings',
            component: lazyLoad('settings/Company'),
            meta: { title: 'Company' }
          },
          {
            path: 'users',
            name: 'UserManagement',
            component: lazyLoad('settings/Users'),
            meta: { title: 'Users & Permissions' }
          },
          {
            path: 'integrations',
            name: 'Integrations',
            component: lazyLoad('settings/Integrations'),
            meta: { title: 'Integrations' }
          }
        ]
      },

      // 404 Catch-all
      {
        path: ':pathMatch(.*)*',
        name: 'NotFound',
        component: () => import('@/views/NotFound.vue'),
        meta: { title: 'Page Not Found' }
      }
    ]
  }
];

export default routeMap;
