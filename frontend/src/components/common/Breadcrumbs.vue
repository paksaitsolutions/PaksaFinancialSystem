<template>
  <v-breadcrumbs
    :items="breadcrumbItems"
    class="pa-0"
    :class="breadcrumbClass"
  >
    <template v-slot:prepend>
      <v-icon
        icon="mdi-home"
        size="small"
        @click="$router.push('/')"
        class="cursor-pointer"
      />
    </template>
    
    <template v-slot:item="{ item }">
      <v-breadcrumbs-item
        :to="item.disabled ? undefined : item.to"
        :disabled="item.disabled"
        class="breadcrumb-item"
      >
        <v-icon
          v-if="item.icon"
          :icon="item.icon"
          size="small"
          class="mr-1"
        />
        {{ item.title }}
      </v-breadcrumbs-item>
    </template>
    
    <template v-slot:divider>
      <v-icon icon="mdi-chevron-right" size="small" />
    </template>
  </v-breadcrumbs>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useResponsive } from '@/composables/useResponsive'

const route = useRoute()
const { isMobile } = useResponsive()

const breadcrumbClass = computed(() => ({
  'breadcrumbs': true,
  'breadcrumbs--mobile': isMobile.value
}))

const breadcrumbItems = computed(() => {
  const pathSegments = route.path.split('/').filter(segment => segment)
  const items = []
  
  // Add home if not on home page
  if (route.path !== '/') {
    items.push({
      title: 'Dashboard',
      to: '/',
      icon: 'mdi-view-dashboard'
    })
  }
  
  // Build breadcrumb items from route segments
  let currentPath = ''
  pathSegments.forEach((segment, index) => {
    currentPath += `/${segment}`
    const isLast = index === pathSegments.length - 1
    
    // Get title from route meta or format segment
    const title = getSegmentTitle(segment, currentPath)
    const icon = getSegmentIcon(segment)
    
    items.push({
      title,
      to: isLast ? undefined : currentPath,
      disabled: isLast,
      icon
    })
  })
  
  return items
})

const getSegmentTitle = (segment, path) => {
  // Check if route has meta title
  const matchedRoute = route.matched.find(r => r.path === path)
  if (matchedRoute?.meta?.breadcrumb) {
    return matchedRoute.meta.breadcrumb
  }
  
  // Format segment name
  const titleMap = {
    'accounts-payable': 'Accounts Payable',
    'accounts-receivable': 'Accounts Receivable',
    'general-ledger': 'General Ledger',
    'payroll': 'Payroll',
    'reports': 'Reports',
    'settings': 'Settings',
    'employees': 'Employees',
    'processing': 'Processing',
    'benefits': 'Benefits',
    'tax-calculator': 'Tax Calculator',
    'reporting': 'Reporting',
    'vendors': 'Vendors',
    'invoices': 'Invoices',
    'payments': 'Payments',
    'journal-entries': 'Journal Entries',
    'chart-of-accounts': 'Chart of Accounts',
    'period-close': 'Period Close',
    'allocation': 'Allocation Rules',
    'intercompany': 'Intercompany',
    'currency': 'Currency Management'
  }
  
  return titleMap[segment] || segment.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const getSegmentIcon = (segment) => {
  const iconMap = {
    'accounts-payable': 'mdi-credit-card-outline',
    'accounts-receivable': 'mdi-receipt',
    'general-ledger': 'mdi-book-open-variant',
    'payroll': 'mdi-account-group',
    'reports': 'mdi-chart-box',
    'settings': 'mdi-cog',
    'employees': 'mdi-account-multiple',
    'processing': 'mdi-cogs',
    'benefits': 'mdi-heart',
    'tax-calculator': 'mdi-calculator',
    'reporting': 'mdi-file-chart',
    'vendors': 'mdi-domain',
    'invoices': 'mdi-file-document',
    'payments': 'mdi-cash-multiple',
    'journal-entries': 'mdi-book-edit',
    'chart-of-accounts': 'mdi-format-list-numbered',
    'period-close': 'mdi-calendar-check',
    'allocation': 'mdi-distribute-horizontal-left',
    'intercompany': 'mdi-swap-horizontal',
    'currency': 'mdi-currency-usd'
  }
  
  return iconMap[segment]
}
</script>

<style scoped>
.breadcrumbs {
  background: rgba(0, 0, 0, 0.02);
  border-radius: 8px;
  padding: 8px 16px;
  margin-bottom: 16px;
}

.breadcrumbs--mobile {
  padding: 6px 12px;
  margin-bottom: 12px;
}

.breadcrumb-item {
  font-size: 0.875rem;
  font-weight: 500;
}

.cursor-pointer {
  cursor: pointer;
  transition: color 0.2s ease;
}

.cursor-pointer:hover {
  color: rgb(var(--v-theme-primary));
}

@media (max-width: 600px) {
  .breadcrumbs {
    font-size: 0.75rem;
  }
  
  .breadcrumb-item {
    font-size: 0.75rem;
  }
}

[data-theme="dark"] .breadcrumbs {
  background: rgba(255, 255, 255, 0.05);
}
</style>