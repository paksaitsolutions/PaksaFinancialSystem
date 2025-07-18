import { defineStore } from 'pinia';

export const useMenuStore = defineStore('menu', {
  state: () => ({
    isExpanded: true,
    modules: [
      {
        id: 'dashboard',
        title: 'Dashboard',
        icon: 'mdi-view-dashboard',
        color: '#1E88E5',
        description: 'Financial metrics and KPI overview',
        route: '/dashboard',
        permissions: ['dashboard_access'],
        primaryActions: [
          { name: 'Financial Metrics', route: '/dashboard/financial', icon: 'mdi-finance' },
          { name: 'Analytics', route: '/dashboard/analytics', icon: 'mdi-chart-box' }
        ],
        subItems: [
          { name: 'Financial Metrics', route: '/dashboard/financial', icon: 'mdi-finance' },
          { name: 'Analytics', route: '/dashboard/analytics', icon: 'mdi-chart-box' },
          { name: 'KPI Overview', route: '/dashboard/kpi', icon: 'mdi-chart-timeline-variant' }
        ]
      },
      {
        id: 'gl',
        title: 'General Ledger',
        icon: 'mdi-book-open-page-variant',
        color: '#1867C0',
        description: 'Complete accounting system with multi-dimensional COA',
        route: '/gl',
        permissions: ['gl_access'],
        primaryActions: [
          { name: 'Chart of Accounts', route: '/gl/chart-of-accounts', icon: 'mdi-file-tree' },
          { name: 'Journal Entries', route: '/gl/journal-entries', icon: 'mdi-notebook' }
        ],
        subItems: [
          { name: 'Dashboard', route: '/gl/dashboard', icon: 'mdi-view-dashboard' },
          { name: 'Chart of Accounts', route: '/gl/chart-of-accounts', icon: 'mdi-file-tree' },
          { name: 'Journal Entries', route: '/gl/journal-entries', icon: 'mdi-notebook' },
          { name: 'Trial Balance', route: '/gl/trial-balance', icon: 'mdi-scale-balance' },
          { name: 'Recurring Journals', route: '/gl/recurring', icon: 'mdi-calendar-refresh' }
        ]
      },
      {
        id: 'ap',
        title: 'Accounts Payable',
        icon: 'mdi-cash-minus',
        color: '#4CAF50',
        description: 'Manage vendors, invoices and payments',
        route: '/ap',
        permissions: ['ap_access'],
        primaryActions: [
          { name: 'Vendors', route: '/ap/vendors', icon: 'mdi-account-group' },
          { name: 'AP Invoices', route: '/ap/invoices', icon: 'mdi-file-document-edit' }
        ],
        subItems: [
          { name: 'Dashboard', route: '/ap/dashboard', icon: 'mdi-view-dashboard' },
          { name: 'Vendors', route: '/ap/vendors', icon: 'mdi-account-group' },
          { name: 'Invoices', route: '/ap/invoices', icon: 'mdi-file-document-edit' },
          { name: 'Payments', route: '/ap/payments', icon: 'mdi-cash-fast' },
          { name: 'Analytics', route: '/ap/analytics', icon: 'mdi-chart-box' }
        ]
      },
      {
        id: 'ar',
        title: 'Accounts Receivable',
        icon: 'mdi-cash-plus',
        color: '#FF9800',
        description: 'Manage customers, invoices and collections',
        route: '/ar',
        permissions: ['ar_access'],
        primaryActions: [
          { name: 'Customers', route: '/ar/customers', icon: 'mdi-account-multiple' },
          { name: 'AR Invoices', route: '/ar/invoices', icon: 'mdi-file-document' }
        ],
        subItems: [
          { name: 'Dashboard', route: '/ar/dashboard', icon: 'mdi-view-dashboard' },
          { name: 'Customers', route: '/ar/customers', icon: 'mdi-account-multiple' },
          { name: 'Invoices', route: '/ar/invoices', icon: 'mdi-file-document' },
          { name: 'Payments', route: '/ar/payments', icon: 'mdi-cash-check' },
          { name: 'Analytics', route: '/ar/analytics', icon: 'mdi-chart-box' }
        ]
      },
      {
        id: 'cash',
        title: 'Cash Management',
        icon: 'mdi-bank',
        color: '#2196F3',
        description: 'Bank accounts, transactions and reconciliation',
        route: '/cash',
        permissions: ['cash_access'],
        primaryActions: [
          { name: 'Bank Accounts', route: '/cash/accounts', icon: 'mdi-bank' },
          { name: 'Reconciliation', route: '/cash/reconciliation', icon: 'mdi-file-compare' }
        ],
        subItems: [
          { name: 'Bank Accounts', route: '/cash/accounts', icon: 'mdi-bank' },
          { name: 'Transactions', route: '/cash/transactions', icon: 'mdi-swap-horizontal' },
          { name: 'Reconciliation', route: '/cash/reconciliation', icon: 'mdi-file-compare' }
        ]
      },
      {
        id: 'payroll',
        title: 'Payroll',
        icon: 'mdi-account-cash',
        color: '#9C27B0',
        description: 'Employee management and compensation',
        route: '/payroll',
        permissions: ['payroll_access'],
        primaryActions: [
          { name: 'Employees', route: '/payroll/employees', icon: 'mdi-account-group' },
          { name: 'Pay Runs', route: '/payroll/payruns', icon: 'mdi-calendar-check' }
        ],
        subItems: [
          { name: 'Employees', route: '/payroll/employees', icon: 'mdi-account-group' },
          { name: 'Pay Runs', route: '/payroll/payruns', icon: 'mdi-calendar-check' },
          { name: 'Tax Forms', route: '/payroll/tax-forms', icon: 'mdi-file-document' }
        ]
      },
      {
        id: 'assets',
        title: 'Fixed Assets',
        icon: 'mdi-office-building',
        color: '#795548',
        description: 'Asset lifecycle and depreciation management',
        route: '/assets',
        permissions: ['assets_access'],
        primaryActions: [
          { name: 'Asset Register', route: '/assets/register', icon: 'mdi-clipboard-list' },
          { name: 'Depreciation', route: '/assets/depreciation', icon: 'mdi-chart-line-variant' }
        ],
        subItems: [
          { name: 'Asset Register', route: '/assets/register', icon: 'mdi-clipboard-list' },
          { name: 'Depreciation', route: '/assets/depreciation', icon: 'mdi-chart-line-variant' },
          { name: 'Maintenance', route: '/assets/maintenance', icon: 'mdi-tools' },
          { name: 'Disposal', route: '/assets/disposal', icon: 'mdi-delete' }
        ]
      },
      {
        id: 'tax',
        title: 'Taxation',
        icon: 'mdi-percent',
        color: '#F44336',
        description: 'Tax compliance and reporting',
        route: '/tax',
        permissions: ['tax_access'],
        primaryActions: [
          { name: 'Dashboard', route: '/tax/dashboard', icon: 'mdi-view-dashboard' },
          { name: 'Tax Rates', route: '/tax/rates', icon: 'mdi-percent-box' }
        ],
        subItems: [
          { name: 'Dashboard', route: '/tax/dashboard', icon: 'mdi-view-dashboard' },
          { name: 'Tax Rates', route: '/tax/rates', icon: 'mdi-percent-box' },
          { name: 'Exemptions', route: '/tax/exemptions', icon: 'mdi-shield' },
          { name: 'Compliance', route: '/tax/compliance', icon: 'mdi-check-circle' },
          { name: 'Analytics', route: '/tax/analytics', icon: 'mdi-chart-box' }
        ]
      },
      {
        id: 'budget',
        title: 'Budgeting',
        icon: 'mdi-chart-areaspline',
        color: '#009688',
        description: 'Financial planning and forecasting',
        route: '/budget',
        permissions: ['budget_access'],
        primaryActions: [
          { name: 'Dashboard', route: '/budget/dashboard', icon: 'mdi-view-dashboard' },
          { name: 'Budget Plans', route: '/budget/plans', icon: 'mdi-clipboard-text' }
        ],
        subItems: [
          { name: 'Dashboard', route: '/budget/dashboard', icon: 'mdi-view-dashboard' },
          { name: 'Budget Plans', route: '/budget/plans', icon: 'mdi-clipboard-text' },
          { name: 'Forecasting', route: '/budget/forecast', icon: 'mdi-chart-line' },
          { name: 'Budget vs Actual', route: '/budget/variance', icon: 'mdi-poll' }
        ]
      },
      {
        id: 'inventory',
        title: 'Inventory',
        icon: 'mdi-package-variant-closed',
        color: '#673AB7',
        description: 'Stock management and valuation',
        route: '/inventory',
        permissions: ['inventory_access'],
        primaryActions: [
          { name: 'Products', route: '/inventory/products', icon: 'mdi-package-variant' },
          { name: 'Stock Levels', route: '/inventory/stock', icon: 'mdi-clipboard-list-outline' }
        ],
        subItems: [
          { name: 'Products', route: '/inventory/products', icon: 'mdi-package-variant' },
          { name: 'Stock Levels', route: '/inventory/stock', icon: 'mdi-clipboard-list-outline' },
          { name: 'Adjustments', route: '/inventory/adjustments', icon: 'mdi-tune' },
          { name: 'Valuation', route: '/inventory/valuation', icon: 'mdi-cash-multiple' }
        ]
      },
      {
        id: 'reports',
        title: 'Reports',
        icon: 'mdi-file-chart',
        color: '#607D8B',
        description: 'Financial and operational reports',
        route: '/reports',
        permissions: ['reports_access'],
        primaryActions: [
          { name: 'Financial Reports', route: '/reports/financial', icon: 'mdi-finance' },
          { name: 'Custom Reports', route: '/reports/custom', icon: 'mdi-file-chart-outline' }
        ],
        subItems: [
          { name: 'Financial Reports', route: '/reports/financial', icon: 'mdi-finance' },
          { name: 'Balance Sheet', route: '/reports/balance-sheet', icon: 'mdi-file-document' },
          { name: 'Income Statement', route: '/reports/income-statement', icon: 'mdi-chart-line' },
          { name: 'Cash Flow', route: '/reports/cash-flow', icon: 'mdi-cash-multiple' },
          { name: 'AR Aging', route: '/reports/ar-aging', icon: 'mdi-calendar-clock' },
          { name: 'AP Aging', route: '/reports/ap-aging', icon: 'mdi-calendar-alert' },
          { name: 'Custom Reports', route: '/reports/custom', icon: 'mdi-file-chart-outline' }
        ]
      }
    ]
  }),
  
  getters: {
    visibleModules: (state) => {
      // In a real app, this would filter based on user permissions
      // For now, return all modules
      return state.modules;
    }
  },
  
  actions: {
    toggleExpanded() {
      this.isExpanded = !this.isExpanded;
    },
    
    expandSidebar() {
      this.isExpanded = true;
    },
    
    collapseSidebar() {
      this.isExpanded = false;
    }
  }
});