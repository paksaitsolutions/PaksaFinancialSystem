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
          { title: 'Chart of Accounts', icon: 'mdi-format-list-numbered', to: '/general-ledger/chart-of-accounts' },
          { title: 'Journal Entries', icon: 'mdi-book-edit', to: '/general-ledger/journal-entries' },
          { title: 'Trial Balance', icon: 'mdi-scale-balance', to: '/general-ledger/trial-balance' },
          { title: 'Financial Statements', icon: 'mdi-file-chart', to: '/general-ledger/financial-statements' }
        ]
      },
      {
        title: 'Accounts Payable',
        icon: 'mdi-credit-card-outline',
        children: [
          { title: 'Vendors', icon: 'mdi-domain', to: '/accounts-payable/vendors' },
          { title: 'Bills', icon: 'mdi-receipt', to: '/accounts-payable/bills' },
          { title: 'Payments', icon: 'mdi-cash-multiple', to: '/accounts-payable/payments' }
        ]
      },
      {
        title: 'Accounts Receivable',
        icon: 'mdi-receipt',
        children: [
          { title: 'Customers', icon: 'mdi-account-group', to: '/accounts-receivable/customers' },
          { title: 'Invoices', icon: 'mdi-file-document', to: '/accounts-receivable/invoices' },
          { title: 'Payments', icon: 'mdi-cash', to: '/accounts-receivable/payments' }
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