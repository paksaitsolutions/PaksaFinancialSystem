import { defineStore } from 'pinia'

export interface NavigationItem {
  title: string
  icon: string
  to?: string
  children?: NavigationItem[]
  badge?: string | number
  disabled?: boolean
}

export const useNavigationStore = defineStore('navigation', {
  state: () => ({
    drawer: true,
    items: [
      {
        title: 'Dashboard',
        icon: 'mdi-view-dashboard',
        to: '/'
      },
      {
        title: 'General Ledger',
        icon: 'mdi-book-open-variant',
        children: [
          { title: 'Chart of Accounts', icon: 'mdi-format-list-numbered', to: '/gl/accounts' },
          { title: 'Journal Entries', icon: 'mdi-book-edit', to: '/gl/journal-entries' },
          { title: 'Trial Balance', icon: 'mdi-scale-balance', to: '/gl/trial-balance' },
          { title: 'Financial Statements', icon: 'mdi-file-chart', to: '/gl/financial-statements' }
        ]
      },
      {
        title: 'Accounts Payable',
        icon: 'mdi-credit-card-outline',
        children: [
          { title: 'Vendors', icon: 'mdi-domain', to: '/ap/vendors' },
          { title: 'Bills', icon: 'mdi-receipt', to: '/ap/bills' },
          { title: 'Payments', icon: 'mdi-cash-multiple', to: '/ap/payments' }
        ]
      },
      {
        title: 'Accounts Receivable',
        icon: 'mdi-receipt',
        children: [
          { title: 'Customers', icon: 'mdi-account-group', to: '/ar/customers' },
          { title: 'Invoices', icon: 'mdi-file-document', to: '/ar/invoices' },
          { title: 'Payments', icon: 'mdi-cash', to: '/ar/payments' }
        ]
      },
      {
        title: 'Payroll',
        icon: 'mdi-account-group',
        children: [
          { title: 'Employees', icon: 'mdi-account-multiple', to: '/payroll/employees' },
          { title: 'Processing', icon: 'mdi-cogs', to: '/payroll/processing' },
          { title: 'Benefits', icon: 'mdi-heart', to: '/payroll/benefits' },
          { title: 'Tax Calculator', icon: 'mdi-calculator', to: '/payroll/tax-calculator' },
          { title: 'Reporting', icon: 'mdi-file-chart', to: '/payroll/reporting' }
        ]
      },
      {
        title: 'Tax Management',
        icon: 'mdi-percent',
        children: [
          { title: 'Dashboard', icon: 'mdi-view-dashboard', to: '/tax' },
          { title: 'Tax Codes', icon: 'mdi-code-tags', to: '/tax/codes' },
          { title: 'Tax Rates', icon: 'mdi-percent', to: '/tax/rates' },
          { title: 'Jurisdictions', icon: 'mdi-map-marker', to: '/tax/jurisdictions' },
          { title: 'Exemptions', icon: 'mdi-shield-check', to: '/tax/exemptions' },
          { title: 'Tax Returns', icon: 'mdi-file-document-outline', to: '/tax/returns' },
          { title: 'Compliance', icon: 'mdi-check-circle', to: '/tax/compliance' },
          { title: 'Reports', icon: 'mdi-chart-line', to: '/tax/reports' }
        ]
      },
      {
        title: 'HRM',
        icon: 'mdi-account-tie',
        to: '/hrm',
        children: [
          { title: 'Dashboard', icon: 'mdi-view-dashboard', to: '/hrm' },
          { title: 'Employees', icon: 'mdi-account-group', to: '/hrm/employees' },
          { title: 'Departments', icon: 'mdi-office-building', to: '/hrm/departments' },
          { title: 'Positions', icon: 'mdi-briefcase-account', to: '/hrm/positions' },
          { title: 'Attendance', icon: 'mdi-calendar-check', to: '/hrm/attendance' },
          { title: 'Leave', icon: 'mdi-calendar-remove', to: '/hrm/leave' },
          { title: 'Recruitment', icon: 'mdi-account-multiple-plus', to: '/hrm/recruitment' },
          { title: 'Performance', icon: 'mdi-chart-line', to: '/hrm/performance' },
          { title: 'Reports', icon: 'mdi-file-chart', to: '/hrm/reports' }
        ]
      },
      {
        title: 'Reports',
        icon: 'mdi-chart-box',
        to: '/reports'
      },
      {
        title: 'Settings',
        icon: 'mdi-cog',
        children: [
          { title: 'Currency Management', icon: 'mdi-currency-usd', to: '/settings/currency' },
          { title: 'Period Close', icon: 'mdi-calendar-check', to: '/period-close' },
          { title: 'Allocation Rules', icon: 'mdi-distribute-horizontal-left', to: '/allocation' },
          { title: 'Intercompany', icon: 'mdi-swap-horizontal', to: '/intercompany' }
        ]
      },
      {
        title: 'Super Admin',
        icon: 'mdi-shield-crown',
        children: [
          { title: 'Dashboard', icon: 'mdi-view-dashboard', to: '/super-admin' },
          { title: 'Company Management', icon: 'mdi-domain', to: '/super-admin/companies' },
          { title: 'User Management', icon: 'mdi-account-group', to: '/super-admin/users' },
          { title: 'System Settings', icon: 'mdi-cog', to: '/super-admin/settings' },
          { title: 'Audit Logs', icon: 'mdi-clipboard-list', to: '/super-admin/audit-logs' }
        ]
      }
    ] as NavigationItem[]
  }),

  actions: {
    toggleDrawer() {
      this.drawer = !this.drawer
    },

    setDrawer(value: boolean) {
      this.drawer = value
    }
  }
})