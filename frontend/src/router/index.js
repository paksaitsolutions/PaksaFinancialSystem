import { createRouter, createWebHistory } from 'vue-router';
import MainLayout from '../layouts/MainLayout.vue';

// Test view
const TestView = () => import('../views/TestView.vue');

// Auth views
const Login = () => import('../views/auth/Login.vue');
const Register = () => import('../views/auth/Register.vue');
const ForgotPassword = () => import('../views/auth/ForgotPassword.vue');

// Main views
const Home = () => import('../views/Home.vue');
const Dashboard = () => import('../modules/general-ledger/views/Dashboard.vue');

// GL views (modular imports)
const GLDashboard = Dashboard; // Alias for backward compatibility
const ChartOfAccounts = () => import('../modules/general-ledger/views/accounts/GLAccountsView.vue');
const JournalEntries = () => import('../modules/general-ledger/views/journal-entries/JournalEntriesView.vue');
const TrialBalance = () => import('../modules/general-ledger/views/TrialBalance.vue');
const RecurringJournals = () => import('../modules/general-ledger/views/recurring/RecurringJournalsView.vue');
const FinancialStatements = () => import('../modules/general-ledger/views/financial-statements/FinancialStatementsView.vue');
const AdvancedGL = () => import('../modules/general-ledger/views/AdvancedGL.vue');

// AP views (modular imports)
const APDashboard = () => import('@/modules/accounts-payable/views/VendorsAdvancedView.vue');
const Vendors = () => import('@/modules/accounts-payable/views/VendorsAdvancedView.vue');
const APInvoices = () => import('@/modules/accounts-payable/views/invoices/InvoicesView.vue');
const APPayments = () => import('@/modules/accounts-payable/views/payments/PaymentsView.vue');

// AR views (modular imports)
const ARDashboard = () => import('../modules/accounts-receivable/views/CustomersAdvanced.vue');
const Customers = () => import('../modules/accounts-receivable/views/CustomersAdvanced.vue');
const ARInvoices = () => import('../modules/accounts-receivable/views/ARInvoicesAdvanced.vue');
const ARPayments = () => import('../modules/accounts-receivable/views/ARPaymentsAdvanced.vue');

// Cash Management views (modular imports)
const BankAccounts = () => import('../modules/cash-management/views/BankAccounts.vue');
const Reconciliation = () => import('../modules/cash-management/views/Reconciliation.vue');

// Tax views (modular imports)
const TaxDashboard = () => import('../modules/tax/views/TaxDashboard.vue');
const TaxRates = () => import('../modules/tax/views/TaxRates.vue');
const TaxExemptions = () => import('../modules/tax/views/TaxExemptionsView.vue');
const TaxCompliance = () => import('../modules/tax/views/TaxComplianceDashboard.vue');

// Budget views (modular imports)
const BudgetDashboard = () => import('../modules/budget/views/BudgetDashboard.vue');
const BudgetPlans = () => import('../modules/budget/views/BudgetView.vue');
const BudgetApproval = () => import('../modules/budget/views/BudgetApprovalView.vue');

// Payroll views (modular imports)
const PayrollRuns = () => import('../modules/payroll/views/PayRunListView.vue');
const PayrollRunView = () => import('../modules/payroll/views/PayRunView.vue');

// Module placeholder for missing views
const ModuleView = () => import('@/views/ModuleView.vue');

// Reports views
const ReportsView = () => import('@/views/reports/ReportsView.vue');
const FinancialReportsView = () => import('@/views/reports/FinancialReportsView.vue');
const BalanceSheetReport = () => import('@/views/reports/BalanceSheetReport.vue');
const IncomeStatementReport = () => import('@/views/reports/IncomeStatementReport.vue');
const CashFlowReport = () => import('@/views/reports/CashFlowReport.vue');
const APAgingReport = () => import('@/views/reports/APAgingReport.vue');
const ARAgingReport = () => import('@/views/reports/ARAgingReport.vue');

// Fallback for any missing report views
const FinancialStatementView = ModuleView;
const GeneralLedgerView = ModuleView;
const TrialBalanceView = ModuleView;
const AgingReportView = ModuleView;
const TaxReportView = ModuleView;
const CashFlowView = ModuleView;
const BudgetVsActualView = ModuleView;

const routes = [
  // Auth routes
  {
    path: '/auth',
    children: [
      {
        path: 'login',
        name: 'login',
        component: Login
      },
      {
        path: 'register',
        name: 'register',
        component: Register
      },
      {
        path: 'forgot-password',
        name: 'forgot-password',
        component: ForgotPassword
      }
    ]
  },
  
  // Main application routes
  {
    path: '/',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'home',
        component: Home
      },
      
      // Dashboard routes
      {
        path: 'dashboard',
        name: 'dashboard',
        component: Dashboard
      },
      
      // General Ledger routes
      {
        path: 'gl',
        name: 'gl',
        component: GLDashboard
      },
      {
        path: 'gl/chart-of-accounts',
        name: 'gl-coa',
        component: ChartOfAccounts
      },
      {
        path: 'gl/journal-entries',
        name: 'gl-journal',
        component: JournalEntries
      },
      {
        path: 'gl/trial-balance',
        name: 'gl-trial-balance',
        component: TrialBalance
      },
      {
        path: 'gl/recurring',
        name: 'gl-recurring',
        component: RecurringJournals
      },
      
      // Accounts Payable routes
      {
        path: 'ap',
        name: 'ap',
        component: APDashboard
      },
      {
        path: 'ap/vendors',
        name: 'ap-vendors',
        component: Vendors
      },
      {
        path: 'ap/invoices',
        name: 'ap-invoices',
        component: APInvoices
      },
      {
        path: 'ap/payments',
        name: 'ap-payments',
        component: APPayments
      },
      {
        path: 'ap/analytics',
        name: 'ap-analytics',
        component: APDashboard
      },
      
      // Accounts Receivable routes
      {
        path: 'ar',
        name: 'ar',
        component: ARDashboard
      },
      {
        path: 'ar/customers',
        name: 'ar-customers',
        component: Customers
      },
      {
        path: 'ar/invoices',
        name: 'ar-invoices',
        component: ARInvoices
      },
      {
        path: 'ar/payments',
        name: 'ar-payments',
        component: ARPayments
      },
      {
        path: 'ar/analytics',
        name: 'ar-analytics',
        component: ARDashboard
      },
      
      // Cash Management routes
      {
        path: 'cash',
        name: 'cash',
        component: ModuleView,
        props: { title: 'Cash Management', color: '#2196F3' }
      },
      {
        path: 'cash/accounts',
        name: 'cash-accounts',
        component: BankAccounts
      },
      {
        path: 'cash/reconciliation',
        name: 'cash-reconciliation',
        component: Reconciliation
      },
      
      // Payroll routes
      {
        path: 'payroll',
        name: 'payroll',
        component: ModuleView,
        props: { title: 'Payroll', color: '#9C27B0' }
      },
      {
        path: 'payroll/payruns',
        name: 'payroll-runs',
        component: PayrollRuns
      },
      {
        path: 'payroll/payruns/:id',
        name: 'payroll-run-view',
        component: PayrollRunView,
        props: true
      },
      
      // Fixed Assets routes
      {
        path: 'assets',
        name: 'assets',
        component: ModuleView,
        props: { title: 'Fixed Assets', color: '#795548' }
      },
      
      // Taxation routes
      {
        path: 'tax',
        name: 'tax',
        component: TaxDashboard
      },
      {
        path: 'tax/rates',
        name: 'tax-rates',
        component: TaxRates
      },
      {
        path: 'tax/exemptions',
        name: 'tax-exemptions',
        component: TaxExemptions
      },
      {
        path: 'tax/compliance',
        name: 'tax-compliance',
        component: TaxCompliance
      },
      {
        path: 'tax/analytics',
        name: 'tax-analytics',
        component: TaxDashboard
      },
      
      // Budgeting routes
      {
        path: 'budget',
        name: 'budget',
        component: BudgetDashboard
      },
      {
        path: 'budget/plans',
        name: 'budget-plans',
        component: BudgetPlans
      },
      {
        path: 'budget/approval',
        name: 'budget-approval',
        component: BudgetApproval
      },
      
      // Inventory routes
      {
        path: 'inventory',
        name: 'inventory',
        component: ModuleView,
        props: { title: 'Inventory', color: '#673AB7' }
      },
      
      // Reports routes
      {
        path: 'reports',
        name: 'reports',
        component: ReportsView
      },
      {
        path: 'reports/financial',
        name: 'reports-financial',
        component: FinancialReportsView
      },
      {
        path: 'reports/balance-sheet',
        name: 'reports-balance-sheet',
        component: BalanceSheetReport
      },
      {
        path: 'reports/income-statement',
        name: 'reports-income-statement',
        component: IncomeStatementReport
      },
      {
        path: 'reports/cash-flow',
        name: 'reports-cash-flow',
        component: CashFlowReport
      },
      {
        path: 'reports/ap-aging',
        name: 'reports-ap-aging',
        component: APAgingReport
      },
      {
        path: 'reports/ar-aging',
        name: 'reports-ar-aging',
        component: ARAgingReport
      },
      
      // Settings and Help routes
      {
        path: 'settings',
        name: 'settings',
        component: ModuleView,
        props: { title: 'Settings' }
      },
      {
        path: 'settings/currency',
        name: 'settings-currency',
        component: () => import('../views/settings/CurrencyManagementView.vue')
      },
      {
        path: 'intercompany',
        name: 'intercompany',
        component: () => import('../views/intercompany/IntercompanyTransactionsView.vue')
      },
      {
        path: 'allocation',
        name: 'allocation',
        component: () => import('../views/allocation/AllocationRulesView.vue')
      },
      {
        path: 'period-close',
        name: 'period-close',
        component: () => import('../views/period-close/PeriodCloseView.vue')
      },
      {
        path: 'roles',
        name: 'roles',
        component: () => import('../views/rbac/RoleManagementView.vue')
      },
      {
        path: 'help',
        name: 'help',
        component: ModuleView,
        props: { title: 'Help & Support' }
      }
    ]
  },
  
  // Catch-all route
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// Navigation guard
router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('token') !== null;
  
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!isAuthenticated) {
      next('/auth/login');
    } else {
      next();
    }
  } else {
    next();
  }
});

export default router;