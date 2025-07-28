import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router';
import { defineComponent } from 'vue';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        component: () => import('@/views/Home.vue')
      }
    ]
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        component: () => import('@/views/AdvancedDashboard.vue')
      }
    ]
  },
  {
    path: '/auth/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue')
  },
  {
    path: '/auth/register',
    name: 'Register',
    component: () => import('@/views/auth/Register.vue')
  },
  {
    path: '/auth/forgot-password',
    name: 'ForgotPassword',
    component: () => import('@/views/auth/ForgotPassword.vue')
  },
  {
    path: '/gl',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'GeneralLedger',
        component: () => import(/* webpackChunkName: "general-ledger" */ '@/modules/general-ledger/views/Dashboard.vue')
      },
      {
        path: 'accounts',
        name: 'GLAccounts',
        component: () => import('@/modules/general-ledger/views/ChartOfAccounts.vue')
      },
      {
        path: 'journal-entries',
        name: 'GLJournalEntries',
        component: () => import('@/modules/general-ledger/views/journal-entries/JournalEntriesView.vue')
      },
      {
        path: 'trial-balance',
        name: 'GLTrialBalance',
        component: () => import('@/modules/general-ledger/views/reports/TrialBalanceView.vue')
      },
      {
        path: 'financial-statements',
        name: 'GLFinancialStatements',
        component: () => import('@/views/reports/FinancialReportsView.vue')
      }
    ]
  },
  {
    path: '/ap',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'AccountsPayable',
        component: () => import('@/modules/accounts-payable/views/VendorsAdvancedView.vue')
      },
      {
        path: 'vendors',
        name: 'APVendors',
        component: () => import('@/modules/accounts-payable/views/VendorsAdvancedView.vue')
      },
      {
        path: 'bills',
        name: 'APBills',
        component: () => import('@/modules/accounts-payable/views/BillProcessingView.vue')
      },
      {
        path: 'payments',
        name: 'APPayments',
        component: () => import('@/modules/accounts-payable/views/payments/PaymentsView.vue')
      }
    ]
  },
  {
    path: '/ar',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'AccountsReceivable',
        component: () => import('@/views/accounts-receivable/CustomersView.vue')
      },
      {
        path: 'customers',
        name: 'ARCustomers',
        component: () => import('@/views/accounts-receivable/CustomersView.vue')
      },
      {
        path: 'invoices',
        name: 'ARInvoices',
        component: () => import('@/modules/accounts-receivable/views/ARInvoicesAdvanced.vue')
      },
      {
        path: 'payments',
        name: 'ARPayments',
        component: () => import('@/modules/accounts-receivable/views/ARPaymentsAdvanced.vue')
      }
    ]
  },
  {
    path: '/reports',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Reports',
        component: () => import('@/views/reports/FinancialReportsView.vue')
      }
    ]
  },
  {
    path: '/admin',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true, role: 'admin' },
    children: [
      {
        path: '',
        name: 'SuperAdmin',
        component: () => import('@/views/admin/SuperAdminView.vue')
      }
    ]
  },
  {
    path: '/settings',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Settings',
        component: () => import('@/views/settings/CompanySettingsView.vue')
      },
      {
        path: 'users',
        name: 'UserManagement',
        component: () => import('@/modules/user/views/UserManagementView.vue')
      },
      {
        path: 'system',
        name: 'SystemConfiguration',
        component: () => import('@/views/settings/SystemConfigurationView.vue')
      }
    ]
  },
  {
    path: '/settings/currency',
    name: 'CurrencySettings',
    component: () => import('@/views/settings/CurrencyManagementView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/invoicing/create',
    name: 'CreateInvoice',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        component: () => import('@/views/invoicing/CreateInvoice.vue')
      }
    ]
  },
  {
    path: '/rbac',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true, role: 'admin' },
    children: [
      {
        path: '',
        name: 'RoleManagement',
        component: () => import('@/views/rbac/RoleManagementView.vue')
      }
    ]
  },
  {
    path: '/cash',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'CashManagement',
        component: () => import('@/views/cash/CashManagementView.vue')
      },
      {
        path: 'accounts',
        name: 'CashAccounts',
        component: () => import('@/modules/cash-management/views/BankAccounts.vue')
      },
      {
        path: 'reconciliation',
        name: 'CashReconciliation',
        component: () => import('@/modules/cash-management/views/Reconciliation.vue')
      },
      {
        path: 'forecast',
        name: 'CashForecast',
        component: () => import('@/modules/cash-management/views/CashFlowForecastingView.vue')
      }
    ]
  },
  {
    path: '/assets',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'FixedAssets',
        component: () => import('@/views/assets/FixedAssetsView.vue')
      },
      {
        path: 'depreciation',
        name: 'AssetDepreciation',
        component: () => import('@/modules/fixed-assets/views/DepreciationView.vue')
      },
      {
        path: 'maintenance',
        name: 'AssetMaintenance',
        component: () => import('@/modules/fixed-assets/views/MaintenanceView.vue')
      }
    ]
  },
  {
    path: '/inventory',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Inventory',
        component: () => import('@/views/inventory/InventoryView.vue')
      },
      {
        path: 'items',
        name: 'InventoryItems',
        component: () => import('@/modules/inventory/views/ItemsView.vue')
      },
      {
        path: 'locations',
        name: 'InventoryLocations',
        component: () => import('@/modules/inventory/views/LocationsView.vue')
      },
      {
        path: 'adjustments',
        name: 'InventoryAdjustments',
        component: () => import('@/modules/inventory/views/AdjustmentsView.vue')
      },
      {
        path: 'reports',
        name: 'InventoryReports',
        component: () => import('@/modules/inventory/views/ReportsView.vue')
      }
    ]
  },
  {
    path: '/budget',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Budgeting',
        component: () => import('@/views/budget/BudgetingView.vue')
      },
      {
        path: 'planning',
        name: 'BudgetPlanning',
        component: () => import('@/modules/budget/views/BudgetPlanningView.vue')
      },
      {
        path: 'monitoring',
        name: 'BudgetMonitoring',
        component: () => import('@/modules/budget/views/BudgetMonitoringView.vue')
      },
      {
        path: 'forecasts',
        name: 'BudgetForecasts',
        component: () => import('@/modules/budget/views/Forecasts.vue')
      },
      {
        path: 'scenarios',
        name: 'BudgetScenarios',
        component: () => import('@/modules/budget/views/Scenarios.vue')
      }
    ]
  },
  {
    path: '/payroll',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Payroll',
        component: () => import('@/views/payroll/PayrollView.vue')
      },
      {
        path: 'employees',
        name: 'PayrollEmployees',
        component: () => import('@/modules/payroll/views/EmployeePayrollListView.vue')
      },
      {
        path: 'pay-runs',
        name: 'PayrollRuns',
        component: () => import('@/modules/payroll/views/PayrollRunView.vue')
      },
      {
        path: 'payslips',
        name: 'PayrollPayslips',
        component: () => import('@/modules/payroll/views/PayslipsView.vue')
      },
      {
        path: 'deductions',
        name: 'PayrollDeductions',
        component: () => import('@/modules/payroll/views/PayrollDeductionsBenefitsView.vue')
      },
      {
        path: 'tax-config',
        name: 'PayrollTaxConfig',
        component: () => import('@/modules/payroll/views/PayrollTaxesView.vue')
      },
      {
        path: 'reports',
        name: 'PayrollReports',
        component: () => import('@/modules/payroll/views/PayrollReportsView.vue')
      }
    ]
  },
  {
    path: '/hrm',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'HRM',
        component: () => import('@/views/hrm/HRMView.vue')
      },
      {
        path: 'employees',
        name: 'HRMEmployees',
        component: () => import('@/modules/hrm/components/EmployeeManagement.vue')
      },
      {
        path: 'leave',
        name: 'HRMLeave',
        component: () => import('@/modules/hrm/views/LeaveManagementView.vue')
      },
      {
        path: 'attendance',
        name: 'HRMAttendance',
        component: () => import('@/modules/hrm/views/AttendanceView.vue')
      },
      {
        path: 'performance',
        name: 'HRMPerformance',
        component: () => import('@/modules/hrm/views/PerformanceView.vue')
      }
    ]
  },
  {
    path: '/tax',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'TaxManagement',
        component: () => import('@/modules/tax/views/TaxManagementView.vue')
      },
      {
        path: 'codes',
        name: 'TaxCodes',
        component: () => import('@/modules/tax/views/TaxCodes.vue')
      },
      {
        path: 'rates',
        name: 'TaxRates',
        component: () => import('@/modules/tax/views/TaxRates.vue')
      },
      {
        path: 'exemptions',
        name: 'TaxExemptions',
        component: () => import('@/modules/tax/views/TaxExemptionsView.vue')
      },
      {
        path: 'returns',
        name: 'TaxReturns',
        component: () => import('@/modules/tax/views/TaxReturns.vue')
      },
      {
        path: 'compliance',
        name: 'TaxCompliance',
        component: () => import('@/modules/tax/views/TaxCompliance.vue')
      }
    ]
  },
  {
    path: '/main-dashboard',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'MainDashboard',
        component: () => import('@/views/Dashboard.vue')
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue')
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('token') !== null
  const userRole = localStorage.getItem('userRole') || 'user'
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/auth/login')
  } else if (to.meta.role && to.meta.role !== userRole) {
    next('/')
  } else {
    next()
  }
})

export default router;