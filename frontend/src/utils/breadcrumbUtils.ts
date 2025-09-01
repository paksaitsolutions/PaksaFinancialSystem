import type { BreadcrumbItem } from '@/composables/useBreadcrumbs'
import { useBreadcrumbStore } from '@/stores/breadcrumb'

/**
 * Utility functions for managing breadcrumbs
 */

/**
 * Set custom breadcrumbs for a specific page
 * @param items Array of breadcrumb items
 */
export const setBreadcrumbs = (items: BreadcrumbItem[]) => {
  const breadcrumbStore = useBreadcrumbStore()
  breadcrumbStore.setCustomBreadcrumbs(items)
}

/**
 * Clear custom breadcrumbs and return to route-based breadcrumbs
 */
export const clearBreadcrumbs = () => {
  const breadcrumbStore = useBreadcrumbStore()
  breadcrumbStore.clearCustomBreadcrumbs()
}

/**
 * Add a breadcrumb item to the current breadcrumbs
 * @param item Breadcrumb item to add
 */
export const addBreadcrumb = (item: BreadcrumbItem) => {
  const breadcrumbStore = useBreadcrumbStore()
  breadcrumbStore.addBreadcrumb(item)
}

/**
 * Create breadcrumbs for a specific module with dynamic page
 * @param module Module name (e.g., 'General Ledger')
 * @param modulePath Module path (e.g., '/gl')
 * @param pageName Current page name
 * @param pageIcon Optional page icon
 */
export const createModuleBreadcrumbs = (
  module: string,
  modulePath: string,
  pageName: string,
  pageIcon?: string
): BreadcrumbItem[] => {
  return [
    {
      label: 'Home',
      route: '/',
      icon: 'pi pi-home'
    },
    {
      label: module,
      route: modulePath,
      icon: getModuleIcon(module)
    },
    {
      label: pageName,
      icon: pageIcon || 'pi pi-file'
    }
  ]
}

/**
 * Get icon for a module
 * @param module Module name
 */
const getModuleIcon = (module: string): string => {
  const iconMap: Record<string, string> = {
    'General Ledger': 'pi pi-book',
    'Accounts Payable': 'pi pi-credit-card',
    'Accounts Receivable': 'pi pi-receipt',
    'Cash Management': 'pi pi-wallet',
    'Inventory': 'pi pi-box',
    'Fixed Assets': 'pi pi-building',
    'Budget Management': 'pi pi-chart-line',
    'Human Resources': 'pi pi-users',
    'Payroll': 'pi pi-money-bill',
    'Settings': 'pi pi-cog'
  }
  
  return iconMap[module] || 'pi pi-folder'
}