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