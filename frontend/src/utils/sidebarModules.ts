// frontend/src/utils/sidebarModules.ts

export interface SidebarModuleItem {
    title: string
    icon: string
    to?: string
    children?: SidebarModuleItem[]
  }
  
  export const sidebarModules: SidebarModuleItem[] = [
    // Main Dashboard
    { title: 'Home', icon: 'pi pi-home', to: '/' },
    { title: 'Advanced Dashboard', icon: 'pi pi-th-large', to: '/dashboard' },
  
    // General Ledger
    {
      title: 'General Ledger', icon: 'pi pi-book', children: [
        { title: 'Dashboard', icon: 'pi pi-chart-bar', to: '/gl/dashboard' },
        { title: 'Chart of Accounts', icon: 'pi pi-list', to: '/gl/accounts' },
        { title: 'Journal Entries', icon: 'pi pi-book', to: '/gl/journal-entries' },
        { title: 'Trial Balance', icon: 'pi pi-balance-scale', to: '/gl/trial-balance' },
        { title: 'Financial Statements', icon: 'pi pi-file-pdf', to: '/gl/financial-statements' },
        { title: 'Recurring Journals', icon: 'pi pi-sync', to: '/gl/recurring' },
        { title: 'Period Close', icon: 'pi pi-calendar-check', to: '/gl/period-close' },
        { title: 'GL Settings', icon: 'pi pi-cog', to: '/gl/settings' }
      ]
    },
  
    // Accounts Payable
    {
      title: 'Accounts Payable', icon: 'pi pi-credit-card', children: [
        { title: 'Dashboard', icon: 'pi pi-chart-bar', to: '/ap' },
        { title: 'Vendors', icon: 'pi pi-building', to: '/ap/vendors' },
        { title: 'Invoices', icon: 'pi pi-file', to: '/ap/invoices' },
        { title: 'Payments', icon: 'pi pi-money-bill', to: '/ap/payments' },
        { title: 'Bills', icon: 'pi pi-receipt', to: '/ap/bills' },
        { title: 'Credit Memos', icon: 'pi pi-file-export', to: '/ap/credit-memos' },
        { title: 'Reports', icon: 'pi pi-chart-bar', to: '/ap/reports' }
      ]
    },
  
    // Accounts Receivable
    {
      title: 'Accounts Receivable', icon: 'pi pi-money-bill', children: [
        { title: 'Dashboard', icon: 'pi pi-chart-bar', to: '/ar' },
        { title: 'Customers', icon: 'pi pi-users', to: '/ar/customers' },
        { title: 'Invoices', icon: 'pi pi-file', to: '/ar/invoices' },
        { title: 'Payments', icon: 'pi pi-wallet', to: '/ar/payments' },
        { title: 'Collections', icon: 'pi pi-credit-card', to: '/ar/collections' },
        { title: 'Analytics', icon: 'pi pi-chart-line', to: '/ar/analytics' },
        { title: 'Reports', icon: 'pi pi-chart-bar', to: '/ar/reports' }
      ]
    },
  
    // Cash Management
    {
      title: 'Cash Management', icon: 'pi pi-wallet', children: [
        { title: 'Dashboard', icon: 'pi pi-chart-bar', to: '/cash' },
        { title: 'Bank Accounts', icon: 'pi pi-building-columns', to: '/cash/accounts' },
        { title: 'Transactions', icon: 'pi pi-exchange', to: '/cash/transactions' },
        { title: 'Reconciliation', icon: 'pi pi-refresh', to: '/cash/reconciliation' },
        { title: 'Forecasting', icon: 'pi pi-chart-line', to: '/cash/forecasting' },
        { title: 'Banking Integration', icon: 'pi pi-link', to: '/cash/banking-integration' }
      ]
    },
  
    // Budget
    {
      title: 'Budget', icon: 'pi pi-money-bill', children: [
        { title: 'Dashboard', icon: 'pi pi-chart-bar', to: '/budget' },
        { title: 'Plans', icon: 'pi pi-file-edit', to: '/budget/plans' },
        { title: 'Forecasts', icon: 'pi pi-chart-line', to: '/budget/forecasts' },
        { title: 'Scenarios', icon: 'pi pi-sliders-h', to: '/budget/scenarios' },
        { title: 'Approval', icon: 'pi pi-check-circle', to: '/budget/approval' },
        { title: 'Reports', icon: 'pi pi-chart-bar', to: '/budget/reports' }
      ]
    },
  
    // Tax
    {
      title: 'Tax', icon: 'pi pi-receipt', children: [
        { title: 'Dashboard', icon: 'pi pi-chart-bar', to: '/tax' },
        { title: 'Management', icon: 'pi pi-sliders-h', to: '/tax/management' },
        { title: 'Rates', icon: 'pi pi-percentage', to: '/tax/rates' },
        { title: 'Exemptions', icon: 'pi pi-ban', to: '/tax/exemptions' },
        { title: 'Compliance', icon: 'pi pi-shield', to: '/tax/compliance' },
        { title: 'Returns', icon: 'pi pi-upload', to: '/tax/returns' }
      ]
    },
  
    // Payroll
    {
      title: 'Payroll', icon: 'pi pi-users', children: [
        { title: 'Dashboard', icon: 'pi pi-chart-bar', to: '/payroll' },
        { title: 'Employees', icon: 'pi pi-user', to: '/payroll/employees' },
        { title: 'Pay Runs', icon: 'pi pi-sync', to: '/payroll/payruns' },
        { title: 'Payslips', icon: 'pi pi-file', to: '/payroll/payslips' },
        { title: 'Deductions & Benefits', icon: 'pi pi-heart', to: '/payroll/deductions' },
        { title: 'Payroll Taxes', icon: 'pi pi-calculator', to: '/payroll/taxes' },
        { title: 'Reports', icon: 'pi pi-file-pdf', to: '/payroll/reports' }
      ]
    },
  
    // Human Resource Management (HRM)
    {
      title: 'HRM', icon: 'pi pi-users', children: [
        { title: 'Dashboard', icon: 'pi pi-chart-bar', to: '/hrm' },
        { title: 'Employees', icon: 'pi pi-user', to: '/hrm/employees' },
        { title: 'Leave Management', icon: 'pi pi-calendar', to: '/hrm/leave' },
        { title: 'Attendance', icon: 'pi pi-calendar-check', to: '/hrm/attendance' },
        { title: 'Performance', icon: 'pi pi-trophy', to: '/hrm/performance' }
      ]
    },
  
    // Inventory
    {
      title: 'Inventory', icon: 'pi pi-box', children: [
        { title: 'Dashboard', icon: 'pi pi-chart-bar', to: '/inventory' },
        { title: 'Items', icon: 'pi pi-box', to: '/inventory/items' },
        { title: 'Locations', icon: 'pi pi-map-marker', to: '/inventory/locations' },
        { title: 'Adjustments', icon: 'pi pi-warehouse', to: '/inventory/adjustments' },
        { title: 'Reports', icon: 'pi pi-chart-bar', to: '/inventory/reports' }
      ]
    },
  
    // Fixed Assets
    {
      title: 'Fixed Assets', icon: 'pi pi-building', children: [
        { title: 'Dashboard', icon: 'pi pi-chart-bar', to: '/assets' },
        { title: 'Management', icon: 'pi pi-tools', to: '/assets/management' },
        { title: 'Depreciation', icon: 'pi pi-chart-line', to: '/assets/depreciation' },
        { title: 'Maintenance', icon: 'pi pi-wrench', to: '/assets/maintenance' }
      ]
    },
  
    // Reports
    {
      title: 'Reports', icon: 'pi pi-chart-bar', children: [
        { title: 'Dashboard', icon: 'pi pi-chart-bar', to: '/reports' },
        { title: 'Financial', icon: 'pi pi-dollar', to: '/reports/financial' },
        { title: 'Balance Sheet', icon: 'pi pi-balance-scale', to: '/reports/balance-sheet' },
        { title: 'Income Statement', icon: 'pi pi-chart-line', to: '/reports/income-statement' },
        { title: 'Cash Flow', icon: 'pi pi-money-bill', to: '/reports/cash-flow' },
        { title: 'AP Aging', icon: 'pi pi-calendar-times', to: '/reports/ap-aging' },
        { title: 'AR Aging', icon: 'pi pi-calendar-times', to: '/reports/ar-aging' }
      ]
    },
  
    // AI/BI
    {
      title: 'AI & BI', icon: 'pi pi-robot', children: [
        { title: 'AI Insights', icon: 'pi pi-robot', to: '/ai' },
        { title: 'AI Assistant', icon: 'pi pi-comments', to: '/ai/assistant' },
        { title: 'BI Dashboard', icon: 'pi pi-chart-pie', to: '/bi' },
        { title: 'BI Analytics', icon: 'pi pi-chart-line', to: '/bi/analytics' }
      ]
    },
  
    // Settings
    {
      title: 'Settings', icon: 'pi pi-cog', children: [
        { title: 'Dashboard', icon: 'pi pi-chart-bar', to: '/settings' },
        { title: 'Company', icon: 'pi pi-building', to: '/settings/company' },
        { title: 'Users', icon: 'pi pi-users', to: '/settings/users' },
        { title: 'Currency', icon: 'pi pi-dollar', to: '/settings/currency' },
        { title: 'Regions', icon: 'pi pi-globe', to: '/settings/regions' },
        { title: 'Countries', icon: 'pi pi-flag', to: '/settings/countries' },
        { title: 'System', icon: 'pi pi-cog', to: '/settings/system' },
        { title: 'GL Settings', icon: 'pi pi-cog', to: '/settings/gl' }
      ]
    },
  
    // Admin
    {
      title: 'Admin', icon: 'pi pi-shield', children: [
        { title: 'Dashboard', icon: 'pi pi-chart-bar', to: '/admin' },
        { title: 'Companies', icon: 'pi pi-building', to: '/admin/companies' },
        { title: 'Analytics', icon: 'pi pi-chart-line', to: '/admin/analytics' },
        { title: 'Data Quality', icon: 'pi pi-database', to: '/admin/data-quality' },
        { title: 'Security & Compliance', icon: 'pi pi-lock', to: '/admin/security-compliance' },
        { title: 'Monitoring', icon: 'pi pi-desktop', to: '/admin/monitoring' },
        { title: 'Configuration', icon: 'pi pi-cog', to: '/admin/configuration' },
        { title: 'Role Management', icon: 'pi pi-key', to: '/rbac' },
        { title: 'Compliance', icon: 'pi pi-shield', to: '/compliance' },
        { title: 'Security', icon: 'pi pi-lock', to: '/compliance/security' },
        { title: 'Audit Logs', icon: 'pi pi-file', to: '/compliance/audit' }
      ]
    },
  ]
  
