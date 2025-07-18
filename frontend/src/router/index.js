import { createRouter, createWebHistory } from 'vue-router';
import MainLayout from '@/layouts/MainLayout.vue';

// Auth views
const Login = () => import('@/views/auth/Login.vue');
const Register = () => import('@/views/auth/Register.vue');
const ForgotPassword = () => import('@/views/auth/ForgotPassword.vue');

// Main views
const Home = () => import('@/views/Home.vue');
const Dashboard = () => import('@/views/Dashboard.vue');

// GL views
const GLDashboard = () => import('@/views/gl/Dashboard.vue');
const ChartOfAccounts = () => import('@/views/gl/ChartOfAccounts.vue');
const JournalEntries = () => import('@/views/gl/JournalEntries.vue');
const TrialBalance = () => import('@/views/gl/TrialBalance.vue');
const RecurringJournals = () => import('@/views/gl/recurring/RecurringJournalsView.vue');

// AP views
const APDashboard = () => import('@/views/ap/APAnalyticsDashboard.vue');
const Vendors = () => import('@/views/ap/Vendors.vue');
const APInvoices = () => import('@/views/ap/Invoices.vue');
const APPayments = () => import('@/views/ap/Payments.vue');

// AR views
const ARDashboard = () => import('@/views/ar/ARAnalyticsDashboard.vue');
const Customers = () => import('@/views/ar/CustomersAdvanced.vue');
const ARInvoices = () => import('@/views/ar/ARInvoicesAdvanced.vue');
const ARPayments = () => import('@/views/ar/ARPaymentsAdvanced.vue');

// Cash Management views
const BankAccounts = () => import('@/views/cash/BankAccounts.vue');
const Reconciliation = () => import('@/views/cash/Reconciliation.vue');

// Tax views
const TaxDashboard = () => import('@/views/tax/TaxDashboard.vue');
const TaxRates = () => import('@/views/tax/TaxRates.vue');
const TaxExemptions = () => import('@/views/tax/TaxExemptions.vue');
const TaxCompliance = () => import('@/views/tax/TaxCompliance.vue');

// Budget views
const BudgetDashboard = () => import('@/views/budget/BudgetDashboard.vue');
const BudgetPlans = () => import('@/views/budget/BudgetView.vue');
const BudgetApproval = () => import('@/views/budget/BudgetApprovalView.vue');

// Payroll views
const PayrollRuns = () => import('@/views/payroll/payruns/PayRunListView.vue');
const PayrollRunView = () => import('@/views/payroll/payruns/PayRunView.vue');

// Reports views
const ReportsView = () => import('@/views/reports/ReportsView.vue');
const FinancialReportsView = () => import('@/views/reports/FinancialReportsView.vue');
const BalanceSheetReport = () => import('@/views/reports/BalanceSheetReport.vue');
const IncomeStatementReport = () => import('@/views/reports/IncomeStatementReport.vue');
const CashFlowReport = () => import('@/views/reports/CashFlowReport.vue');
const APAgingReport = () => import('@/views/reports/APAgingReport.vue');
const ARAgingReport = () => import('@/views/reports/ARAgingReport.vue');

// Module placeholder for missing views
const ModuleView = () => import('@/views/ModuleView.vue');

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