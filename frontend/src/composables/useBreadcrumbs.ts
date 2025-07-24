import { computed } from 'vue'
import { useRoute } from 'vue-router'

export interface BreadcrumbItem {
  title: string
  to?: string
  disabled?: boolean
  icon?: string
}

export function useBreadcrumbs() {
  const route = useRoute()

  const breadcrumbs = computed<BreadcrumbItem[]>(() => {
    const items: BreadcrumbItem[] = []
    
    // Add home/dashboard if not on home page
    if (route.path !== '/') {
      items.push({
        title: 'Dashboard',
        to: '/',
        icon: 'mdi-view-dashboard'
      })
    }

    // Build breadcrumbs from matched routes
    route.matched.forEach((match, index) => {
      if (match.meta?.breadcrumb) {
        const isLast = index === route.matched.length - 1
        items.push({
          title: match.meta.breadcrumb as string,
          to: isLast ? undefined : match.path,
          disabled: isLast,
          icon: getRouteIcon(match.name as string)
        })
      }
    })

    return items
  })

  const getRouteIcon = (routeName: string): string | undefined => {
    const iconMap: Record<string, string> = {
      'Payroll': 'mdi-account-group',
      'AP': 'mdi-credit-card-outline',
      'AR': 'mdi-receipt',
      'GL': 'mdi-book-open-variant',
      'Dashboard': 'mdi-view-dashboard',
      'Reports': 'mdi-chart-box',
      'Settings': 'mdi-cog'
    }
    
    return iconMap[routeName]
  }

  return {
    breadcrumbs
  }
}