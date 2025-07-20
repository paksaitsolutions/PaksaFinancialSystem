import type { RouteLocationRaw } from 'vue-router';

type BadgeSeverity = 'success' | 'info' | 'warning' | 'danger' | 'contrast' | 'secondary' | null | undefined;

export interface SidebarMenuItem {
  id: string;
  label: string;
  icon: string;
  route?: RouteLocationRaw;
  visible: boolean | (() => boolean);
  items?: SidebarMenuItem[];
  badge?: string;
  badgeSeverity?: BadgeSeverity;
  disabled?: boolean;
  permission?: string | string[];
}

export const menuItems: SidebarMenuItem[] = [
  // Dashboard
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: 'pi pi-home',
    route: { name: 'Dashboard' },
    visible: true,
    permission: 'view_dashboard'
  },
  
  // General Ledger
  {
    id: 'gl',
    label: 'General Ledger',
    icon: 'pi pi-book',
    permission: 'view_gl',
    visible: true,
    items: [
      { 
        id: 'gl-dashboard',
        label: 'Dashboard', 
        icon: 'pi pi-chart-bar', 
        route: { name: 'GLDashboard' }, 
        visible: true 
      },
      { 
        id: 'gl-accounts',
        label: 'Chart of Accounts', 
        icon: 'pi pi-sitemap', 
        route: { name: 'ChartOfAccounts' }, 
        visible: true 
      },
      { 
        id: 'gl-journal-entries',
        label: 'Journal Entries', 
        icon: 'pi pi-book', 
        route: { name: 'JournalEntries' }, 
        visible: true 
      },
      { 
        id: 'gl-trial-balance',
        label: 'Trial Balance', 
        icon: 'pi pi-balance-scale', 
        route: { name: 'TrialBalance' }, 
        visible: true 
      },
      { 
        id: 'gl-financial-statements',
        label: 'Financial Statements', 
        icon: 'pi pi-file-pdf', 
        route: { name: 'FinancialStatements' }, 
        visible: true 
      },
      { 
        id: 'gl-recurring-journals',
        label: 'Recurring Journals', 
        icon: 'pi pi-sync', 
        route: { name: 'RecurringJournals' }, 
        visible: true 
      },
      { 
        id: 'gl-allocation-rules',
        label: 'Allocation Rules', 
        icon: 'pi pi-share-alt', 
        route: { name: 'AllocationRules' }, 
        visible: true 
      },
      { 
        id: 'gl-period-close',
        label: 'Period Close', 
        icon: 'pi pi-lock', 
        route: { name: 'PeriodClose' }, 
        visible: true 
      },
      { 
        id: 'gl-advanced',
        label: 'Advanced', 
        icon: 'pi pi-cog', 
        route: { name: 'GLAdvanced' }, 
        visible: true 
      }
    ]
  },
  
  // Accounts Payable
  {
    id: 'ap',
    label: 'Accounts Payable',
    icon: 'pi pi-credit-card',
    permission: 'view_ap',
    visible: true,
    items: [
      { 
        id: 'ap-dashboard', 
        label: 'Dashboard', 
        icon: 'pi pi-chart-bar', 
        route: { name: 'APDashboard' }, 
        visible: true 
      },
      { 
        id: 'ap-vendors', 
        label: 'Vendors', 
        icon: 'pi pi-users', 
        route: { name: 'Vendors' }, 
        visible: true 
      },
      { 
        id: 'ap-bills', 
        label: 'Bills', 
        icon: 'pi pi-file', 
        route: { name: 'Bills' }, 
        visible: true 
      },
      { 
        id: 'ap-payments', 
        label: 'Payments', 
        icon: 'pi pi-money-bill', 
        route: { name: 'APPayments' }, 
        visible: true 
      },
      { 
        id: 'ap-reports', 
        label: 'Reports', 
        icon: 'pi pi-chart-line', 
        route: { name: 'APReports' }, 
        visible: true 
      }
    ]
  },
  
  // Accounts Receivable
  {
    id: 'ar',
    label: 'Accounts Receivable',
    icon: 'pi pi-wallet',
    permission: 'view_ar',
    visible: true,
    items: [
      { 
        id: 'ar-dashboard', 
        label: 'Dashboard', 
        icon: 'pi pi-chart-bar', 
        route: { name: 'ARDashboard' }, 
        visible: true 
      },
      { 
        id: 'ar-customers', 
        label: 'Customers', 
        icon: 'pi pi-users', 
        route: { name: 'Customers' }, 
        visible: true 
      },
      { 
        id: 'ar-invoices', 
        label: 'Invoices', 
        icon: 'pi pi-file', 
        route: { name: 'Invoices' }, 
        visible: true 
      },
      { 
        id: 'ar-receipts', 
        label: 'Receipts', 
        icon: 'pi pi-money-bill', 
        route: { name: 'Receipts' }, 
        visible: true 
      },
      { 
        id: 'ar-reports', 
        label: 'Reports', 
        icon: 'pi pi-chart-line', 
        route: { name: 'ARReports' }, 
        visible: true 
      }
    ]
  },
  
  // Payroll
  {
    id: 'payroll',
    label: 'Payroll',
    icon: 'pi pi-money-bill-wave',
    permission: 'view_payroll',
    visible: true,
    items: [
      { 
        id: 'payroll-dashboard', 
        label: 'Dashboard', 
        icon: 'pi pi-chart-bar', 
        route: { name: 'PayrollDashboard' }, 
        visible: true 
      },
      { 
        id: 'payroll-employees', 
        label: 'Employees', 
        icon: 'pi pi-users', 
        route: { name: 'Employees' }, 
        visible: true 
      },
      { 
        id: 'payroll-payruns', 
        label: 'Payruns', 
        icon: 'pi pi-calendar', 
        route: { name: 'Payruns' }, 
        visible: true 
      },
      { 
        id: 'payroll-taxes', 
        label: 'Taxes', 
        icon: 'pi pi-percentage', 
        route: { name: 'PayrollTaxes' }, 
        visible: true 
      },
      { 
        id: 'payroll-reports', 
        label: 'Reports', 
        icon: 'pi pi-chart-line', 
        route: { name: 'PayrollReports' }, 
        visible: true 
      }
    ]
  },
  
  // Cash Management
  {
    id: 'cash',
    label: 'Cash Management',
    icon: 'pi pi-cash',
    permission: 'view_cash',
    visible: true,
    items: [
      { 
        id: 'cash-dashboard', 
        label: 'Dashboard', 
        icon: 'pi pi-chart-bar', 
        route: { name: 'CashDashboard' }, 
        visible: true 
      },
      { 
        id: 'cash-accounts', 
        label: 'Bank Accounts', 
        icon: 'pi pi-bank', 
        route: { name: 'BankAccounts' }, 
        visible: true 
      },
      { 
        id: 'cash-transactions', 
        label: 'Transactions', 
        icon: 'pi pi-exchange', 
        route: { name: 'Transactions' }, 
        visible: true 
      },
      { 
        id: 'cash-reconciliation', 
        label: 'Reconciliation', 
        icon: 'pi pi-check-circle', 
        route: { name: 'Reconciliation' }, 
        visible: true 
      },
      { 
        id: 'cash-reports', 
        label: 'Reports', 
        icon: 'pi pi-chart-line', 
        route: { name: 'CashReports' }, 
        visible: true 
      }
    ]
  },
  
  // Fixed Assets
  {
    id: 'assets',
    label: 'Fixed Assets',
    icon: 'pi pi-building',
    permission: 'view_assets',
    visible: true,
    items: [
      { 
        id: 'assets-dashboard', 
        label: 'Dashboard', 
        icon: 'pi pi-chart-bar', 
        route: { name: 'AssetsDashboard' }, 
        visible: true 
      },
      { 
        id: 'assets-register', 
        label: 'Asset Register', 
        icon: 'pi pi-list', 
        route: { name: 'AssetRegister' }, 
        visible: true 
      },
      { 
        id: 'assets-depreciation', 
        label: 'Depreciation', 
        icon: 'pi pi-calculator', 
        route: { name: 'Depreciation' }, 
        visible: true 
      },
      { 
        id: 'assets-disposals', 
        label: 'Disposals', 
        icon: 'pi pi-trash', 
        route: { name: 'AssetDisposals' }, 
        visible: true 
      },
      { 
        id: 'assets-reports', 
        label: 'Reports', 
        icon: 'pi pi-chart-line', 
        route: { name: 'AssetReports' }, 
        visible: true 
      }
    ]
  },
  
  // Tax
  {
    id: 'tax',
    label: 'Tax',
    icon: 'pi pi-percentage',
    permission: 'view_tax',
    visible: true,
    items: [
      { 
        id: 'tax-dashboard', 
        label: 'Dashboard', 
        icon: 'pi pi-chart-bar', 
        route: { name: 'TaxDashboard' }, 
        visible: true 
      },
      { 
        id: 'tax-codes', 
        label: 'Tax Codes', 
        icon: 'pi pi-tag', 
        route: { name: 'TaxCodes' }, 
        visible: true 
      },
      { 
        id: 'tax-returns', 
        label: 'Tax Returns', 
        icon: 'pi pi-file-pdf', 
        route: { name: 'TaxReturns' }, 
        visible: true 
      },
      { 
        id: 'tax-payments', 
        label: 'Tax Payments', 
        icon: 'pi pi-money-bill', 
        route: { name: 'TaxPayments' }, 
        visible: true 
      },
      { 
        id: 'tax-reports', 
        label: 'Reports', 
        icon: 'pi pi-chart-line', 
        route: { name: 'TaxReports' }, 
        visible: true 
      }
    ]
  },
  
  // Reports
  {
    id: 'reports',
    label: 'Reports',
    icon: 'pi pi-chart-bar',
    permission: 'view_reports',
    visible: true,
    items: [
      { 
        id: 'reports-financial', 
        label: 'Financial', 
        icon: 'pi pi-money-bill', 
        route: { name: 'FinancialReports' }, 
        visible: true 
      },
      { 
        id: 'reports-operational', 
        label: 'Operational', 
        icon: 'pi pi-chart-line', 
        route: { name: 'OperationalReports' }, 
        visible: true 
      },
      { 
        id: 'reports-tax', 
        label: 'Tax', 
        icon: 'pi pi-percentage', 
        route: { name: 'TaxReports' }, 
        visible: true 
      },
      { 
        id: 'reports-custom', 
        label: 'Custom Reports', 
        icon: 'pi pi-file-edit', 
        route: { name: 'CustomReports' }, 
        visible: true 
      }
    ]
  },
  
  // Administration
  {
    id: 'admin',
    label: 'Administration',
    icon: 'pi pi-cog',
    permission: 'admin',
    visible: true,
    items: [
      { 
        id: 'admin-users', 
        label: 'Users', 
        icon: 'pi pi-users', 
        route: { name: 'Users' }, 
        visible: true 
      },
      { 
        id: 'admin-roles', 
        label: 'Roles & Permissions', 
        icon: 'pi pi-lock', 
        route: { name: 'Roles' }, 
        visible: true 
      },
      { 
        id: 'admin-settings', 
        label: 'System Settings', 
        icon: 'pi pi-cog', 
        route: { name: 'Settings' }, 
        visible: true 
      },
      { 
        id: 'admin-audit', 
        label: 'Audit Logs', 
        icon: 'pi pi-history', 
        route: { name: 'AuditLogs' }, 
        visible: true 
      }
    ]
  }
];
