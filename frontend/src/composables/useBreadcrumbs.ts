import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useBreadcrumbStore } from '@/stores/breadcrumb'

export interface BreadcrumbItem {
  label: string
  route?: string
  icon?: string
  command?: () => void
}

export function useBreadcrumbs() {
  const route = useRoute()
  const breadcrumbStore = useBreadcrumbStore()

  const breadcrumbs = computed<BreadcrumbItem[]>(() => {
    // If custom breadcrumbs are set, use them instead
    if (breadcrumbStore.customBreadcrumbs.length > 0) {
      return breadcrumbStore.customBreadcrumbs
    }
    const items: BreadcrumbItem[] = []
    
    // Always add Home as first item
    items.push({
      label: 'Home',
      route: '/',
      icon: 'pi pi-home'
    })

    // Build breadcrumbs based on current route
    const pathSegments = route.path.split('/').filter(segment => segment)
    
    if (pathSegments.length > 0) {
      const routeMap = getBreadcrumbMap()
      let currentPath = ''
      
      pathSegments.forEach((segment, index) => {
        currentPath += `/${segment}`
        const isLast = index === pathSegments.length - 1
        
        if (routeMap[currentPath]) {
          items.push({
            label: routeMap[currentPath].label,
            route: isLast ? undefined : currentPath,
            icon: routeMap[currentPath].icon
          })
        }
      })
    }

    return items
  })

  const getBreadcrumbMap = () => {
    return {
      '/gl': { label: 'General Ledger', icon: 'pi pi-book' },
      '/gl/chart-of-accounts': { label: 'Chart of Accounts', icon: 'pi pi-list' },
      '/gl/trial-balance': { label: 'Trial Balance', icon: 'pi pi-calculator' },
      '/gl/general-ledger-report': { label: 'General Ledger Report', icon: 'pi pi-file-pdf' },
      '/gl/reconciliation': { label: 'Account Reconciliation', icon: 'pi pi-check-circle' },
      '/gl/financial-statements': { label: 'Financial Statements', icon: 'pi pi-chart-line' },
      '/gl/period-close': { label: 'Period Close', icon: 'pi pi-lock' },
      '/gl/budget-actual': { label: 'Budget vs Actual', icon: 'pi pi-chart-bar' },
      '/accounting': { label: 'Accounting', icon: 'pi pi-calculator' },
      '/accounting/journal-entry': { label: 'Journal Entry', icon: 'pi pi-pencil' },
      '/ap': { label: 'Accounts Payable', icon: 'pi pi-credit-card' },
      '/ap/create-bill': { label: 'Create Bill', icon: 'pi pi-plus' },
      '/ap/add-vendor': { label: 'Add Vendor', icon: 'pi pi-user-plus' },
      '/ap/record-payment': { label: 'Record Payment', icon: 'pi pi-money-bill' },
      '/ap/import-bills': { label: 'Import Bills', icon: 'pi pi-upload' },
      '/ap/reports': { label: 'AP Reports', icon: 'pi pi-chart-pie' },
      '/ap/invoices': { label: 'AP Invoices', icon: 'pi pi-file' },
      '/ar': { label: 'Accounts Receivable', icon: 'pi pi-receipt' },
      '/accounts-receivable': { label: 'Accounts Receivable', icon: 'pi pi-receipt' },
      '/accounts-receivable/invoices': { label: 'AR Invoices', icon: 'pi pi-file' },
      '/ar/customers': { label: 'Customers', icon: 'pi pi-users' },
      '/cash': { label: 'Cash Management', icon: 'pi pi-wallet' },
      '/inventory': { label: 'Inventory', icon: 'pi pi-box' },
      '/fixed-assets': { label: 'Fixed Assets', icon: 'pi pi-building' },
      '/budget': { label: 'Budget Management', icon: 'pi pi-chart-line' },
      '/hrm': { label: 'Human Resources', icon: 'pi pi-users' },
      '/payroll': { label: 'Payroll', icon: 'pi pi-money-bill' },
      '/settings': { label: 'Settings', icon: 'pi pi-cog' },
      '/settings/general': { label: 'General Settings', icon: 'pi pi-sliders-h' },
      '/settings/users': { label: 'User Management', icon: 'pi pi-user-edit' },
      '/settings/tenant': { label: 'Tenant Management', icon: 'pi pi-building' },
      '/settings/security': { label: 'Security Settings', icon: 'pi pi-shield' }
    }
  }

  return {
    breadcrumbs
  }
}