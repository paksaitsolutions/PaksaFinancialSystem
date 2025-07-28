<template>
  <v-app>
    <!-- App Bar -->
    <v-app-bar 
      color="white" 
      elevation="1" 
      height="64"
      app
    >
      <v-app-bar-nav-icon @click="drawer = !drawer" />
      
      <div class="d-flex align-center ml-2">
        <v-avatar size="32" class="brand-logo mr-3">
          <v-icon color="white" size="16">mdi-finance</v-icon>
        </v-avatar>
        <div>
          <div class="text-h6 font-weight-bold text-grey-darken-3">Paksa Financial</div>
        </div>
      </div>
      
      <v-spacer />
      
      <!-- User Menu -->
      <v-menu offset-y>
        <template v-slot:activator="{ props }">
          <v-btn 
            icon 
            v-bind="props" 
            class="mr-2"
            variant="text"
          >
            <v-avatar size="32" color="primary">
              <v-icon color="white" size="16">mdi-account</v-icon>
            </v-avatar>
          </v-btn>
        </template>
        
        <v-card min-width="200" elevation="8">
          <v-card-text class="pa-4">
            <div class="text-subtitle-1 font-weight-medium">{{ user?.username || 'User' }}</div>
            <div class="text-caption text-medium-emphasis">{{ user?.email }}</div>
          </v-card-text>
          <v-divider />
          <v-list density="compact">
            <v-list-item @click="logout" prepend-icon="mdi-logout">
              <v-list-item-title>Logout</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-card>
      </v-menu>
    </v-app-bar>

    <!-- Navigation Drawer -->
    <v-navigation-drawer
      v-model="drawer"
      app
      :temporary="$vuetify.display.mobile"
      width="280"
      color="white"
      elevation="2"
    >
      <!-- Sidebar Header -->
      <div class="pa-4 border-b">
        <div class="d-flex align-center cursor-pointer" @click="router.push('/')">
          <v-avatar size="32" class="brand-logo mr-3">
            <v-icon color="white" size="16">mdi-finance</v-icon>
          </v-avatar>
          <div>
            <div class="text-subtitle-1 font-weight-bold text-grey-darken-3">Paksa Financial</div>
            <div class="text-caption text-grey-darken-1">Enterprise System</div>
          </div>
        </div>
      </div>

      <!-- Navigation Menu -->
      <v-list density="compact" nav color="primary" class="pa-2">
        <template v-for="item in menuItems" :key="item.title">
          <!-- Items with submenus -->
          <v-list-group v-if="item.children" :value="item.title" :model-value="openGroups.includes(item.title)">
            <template v-slot:activator="{ props }">
              <v-list-item
                v-bind="props"
                :prepend-icon="item.icon"
                :title="item.title"
                :subtitle="item.subtitle"
                class="mb-1 rounded-lg"
                color="primary"
              />
            </template>
            <v-list-item
              v-for="child in item.children"
              :key="child.title"
              :to="child.route"
              :prepend-icon="child.icon"
              class="ml-4 mb-1 rounded-lg"
              color="primary"
              density="compact"
            >
              <v-list-item-title>{{ child.title }}</v-list-item-title>
            </v-list-item>
          </v-list-group>
          
          <!-- Items without submenus -->
          <v-list-item
            v-else
            :to="item.route"
            :prepend-icon="item.icon"
            class="mb-1 rounded-lg"
            color="primary"
            lines="two"
          >
            <v-list-item-title>{{ item.title }}</v-list-item-title>
            <v-list-item-subtitle>{{ item.subtitle }}</v-list-item-subtitle>
            <template v-slot:append>
              <v-icon size="16" color="grey-lighten-1">mdi-chevron-right</v-icon>
            </template>
          </v-list-item>
        </template>
      </v-list>

      <!-- Sidebar Footer -->
      <template v-slot:append>
        <div class="pa-4 border-t">
          <v-btn 
            variant="outlined" 
            size="small" 
            block
            prepend-icon="mdi-help-circle"
            color="grey"
          >
            Help & Support
          </v-btn>
        </div>
      </template>
    </v-navigation-drawer>

    <!-- Main Content -->
    <v-main class="bg-grey-lighten-4">
      <router-view />
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const drawer = ref(true)

// Close drawer on mobile by default
if (typeof window !== 'undefined' && window.innerWidth < 960) {
  drawer.value = false
}
const user = ref<any>(null)

// Compute which parent menu should be open based on current route
const openGroups = computed(() => {
  const currentPath = route.path
  const groups = []
  
  if (currentPath.startsWith('/gl')) groups.push('General Ledger')
  if (currentPath.startsWith('/ap')) groups.push('Accounts Payable')
  if (currentPath.startsWith('/ar')) groups.push('Accounts Receivable')
  if (currentPath.startsWith('/cash')) groups.push('Cash Management')
  if (currentPath.startsWith('/assets')) groups.push('Fixed Assets')
  if (currentPath.startsWith('/inventory')) groups.push('Inventory')
  if (currentPath.startsWith('/budget')) groups.push('Budget Planning')
  if (currentPath.startsWith('/payroll')) groups.push('Payroll')
  if (currentPath.startsWith('/hrm')) groups.push('Human Resources')
  if (currentPath.startsWith('/tax')) groups.push('Tax Management')
  if (currentPath.startsWith('/settings')) groups.push('Settings')
  
  return groups
})

const menuItems = ref([
  { 
    title: 'General Ledger', 
    subtitle: 'Chart of accounts', 
    icon: 'mdi-book-open-variant', 
    route: '/gl',
    children: [
      { title: 'Dashboard', icon: 'mdi-view-dashboard-outline', route: '/gl' },
      { title: 'Chart of Accounts', icon: 'mdi-format-list-bulleted', route: '/gl/accounts' },
      { title: 'Journal Entries', icon: 'mdi-book-edit', route: '/gl/journal-entries' },
      { title: 'Trial Balance', icon: 'mdi-scale-balance', route: '/gl/trial-balance' },
      { title: 'Financial Statements', icon: 'mdi-file-document-multiple', route: '/gl/financial-statements' }
    ]
  },
  { 
    title: 'Accounts Payable', 
    subtitle: 'Vendor management', 
    icon: 'mdi-credit-card-outline', 
    route: '/ap',
    children: [
      { title: 'Dashboard', icon: 'mdi-view-dashboard-outline', route: '/ap' },
      { title: 'Vendors', icon: 'mdi-account-group', route: '/ap/vendors' },
      { title: 'Bills & Invoices', icon: 'mdi-file-document', route: '/ap/bills' },
      { title: 'Payments', icon: 'mdi-cash', route: '/ap/payments' }
    ]
  },
  { 
    title: 'Accounts Receivable', 
    subtitle: 'Customer invoicing', 
    icon: 'mdi-cash-multiple', 
    route: '/ar',
    children: [
      { title: 'Dashboard', icon: 'mdi-view-dashboard-outline', route: '/ar' },
      { title: 'Customers', icon: 'mdi-account-multiple', route: '/ar/customers' },
      { title: 'Invoices', icon: 'mdi-file-document-outline', route: '/ar/invoices' },
      { title: 'Payments', icon: 'mdi-cash-check', route: '/ar/payments' }
    ]
  },
  { 
    title: 'Cash Management', 
    subtitle: 'Bank reconciliation', 
    icon: 'mdi-bank', 
    route: '/cash',
    children: [
      { title: 'Dashboard', icon: 'mdi-view-dashboard-outline', route: '/cash' },
      { title: 'Bank Accounts', icon: 'mdi-bank-outline', route: '/cash/accounts' },
      { title: 'Reconciliation', icon: 'mdi-check-circle', route: '/cash/reconciliation' },
      { title: 'Cash Forecast', icon: 'mdi-chart-line', route: '/cash/forecast' }
    ]
  },
  { 
    title: 'Fixed Assets', 
    subtitle: 'Asset tracking', 
    icon: 'mdi-office-building', 
    route: '/assets',
    children: [
      { title: 'Assets List', icon: 'mdi-format-list-bulleted', route: '/assets' },
      { title: 'Depreciation', icon: 'mdi-trending-down', route: '/assets/depreciation' },
      { title: 'Maintenance', icon: 'mdi-wrench', route: '/assets/maintenance' }
    ]
  },
  { 
    title: 'Inventory', 
    subtitle: 'Stock management', 
    icon: 'mdi-package-variant', 
    route: '/inventory',
    children: [
      { title: 'Dashboard', icon: 'mdi-view-dashboard-outline', route: '/inventory' },
      { title: 'Items', icon: 'mdi-package', route: '/inventory/items' },
      { title: 'Locations', icon: 'mdi-map-marker', route: '/inventory/locations' },
      { title: 'Adjustments', icon: 'mdi-pencil', route: '/inventory/adjustments' },
      { title: 'Reports', icon: 'mdi-chart-bar', route: '/inventory/reports' }
    ]
  },
  { 
    title: 'Budget Planning', 
    subtitle: 'Budget analysis', 
    icon: 'mdi-chart-pie', 
    route: '/budget',
    children: [
      { title: 'Dashboard', icon: 'mdi-view-dashboard-outline', route: '/budget' },
      { title: 'Budget Planning', icon: 'mdi-calendar-edit', route: '/budget/planning' },
      { title: 'Budget Monitoring', icon: 'mdi-monitor', route: '/budget/monitoring' },
      { title: 'Forecasts', icon: 'mdi-crystal-ball', route: '/budget/forecasts' },
      { title: 'Scenarios', icon: 'mdi-sitemap', route: '/budget/scenarios' }
    ]
  },
  { 
    title: 'Payroll', 
    subtitle: 'Employee payroll', 
    icon: 'mdi-account-cash', 
    route: '/payroll',
    children: [
      { title: 'Dashboard', icon: 'mdi-view-dashboard-outline', route: '/payroll' },
      { title: 'Employees', icon: 'mdi-account-group', route: '/payroll/employees' },
      { title: 'Pay Runs', icon: 'mdi-play-circle', route: '/payroll/pay-runs' },
      { title: 'Payslips', icon: 'mdi-file-document', route: '/payroll/payslips' },
      { title: 'Deductions & Benefits', icon: 'mdi-calculator-variant', route: '/payroll/deductions' },
      { title: 'Tax Configuration', icon: 'mdi-cog', route: '/payroll/tax-config' },
      { title: 'Reports', icon: 'mdi-chart-bar', route: '/payroll/reports' }
    ]
  },
  { 
    title: 'Human Resources', 
    subtitle: 'Employee management', 
    icon: 'mdi-account-group', 
    route: '/hrm',
    children: [
      { title: 'Dashboard', icon: 'mdi-view-dashboard-outline', route: '/hrm' },
      { title: 'Employees', icon: 'mdi-account-multiple', route: '/hrm/employees' },
      { title: 'Leave Management', icon: 'mdi-calendar-clock', route: '/hrm/leave' },
      { title: 'Attendance', icon: 'mdi-clock-check', route: '/hrm/attendance' },
      { title: 'Performance', icon: 'mdi-chart-line', route: '/hrm/performance' }
    ]
  },
  { 
    title: 'Tax Management', 
    subtitle: 'Tax compliance', 
    icon: 'mdi-calculator', 
    route: '/tax',
    children: [
      { title: 'Dashboard', icon: 'mdi-view-dashboard-outline', route: '/tax' },
      { title: 'Tax Codes', icon: 'mdi-code-tags', route: '/tax/codes' },
      { title: 'Tax Rates', icon: 'mdi-percent', route: '/tax/rates' },
      { title: 'Exemptions', icon: 'mdi-shield-check', route: '/tax/exemptions' },
      { title: 'Returns', icon: 'mdi-file-send', route: '/tax/returns' },
      { title: 'Compliance', icon: 'mdi-check-circle', route: '/tax/compliance' }
    ]
  },
  { title: 'Financial Reports', subtitle: 'Reporting suite', icon: 'mdi-chart-bar', route: '/reports' },
  { title: 'System Admin', subtitle: 'Administration', icon: 'mdi-shield-crown', route: '/admin' },
  { title: 'Role Management', subtitle: 'User permissions', icon: 'mdi-account-key', route: '/rbac' },
  { 
    title: 'Settings', 
    subtitle: 'Configuration', 
    icon: 'mdi-cog', 
    route: '/settings',
    children: [
      { title: 'Company Settings', icon: 'mdi-office-building', route: '/settings' },
      { title: 'Currency Management', icon: 'mdi-currency-usd', route: '/settings/currency' },
      { title: 'User Management', icon: 'mdi-account-cog', route: '/settings/users' },
      { title: 'System Configuration', icon: 'mdi-cog-outline', route: '/settings/system' }
    ]
  }
])

onMounted(() => {
  const userData = localStorage.getItem('user')
  if (userData) {
    user.value = JSON.parse(userData)
  }
})

const logout = () => {
  localStorage.removeItem('user')
  localStorage.removeItem('token')
  router.push('/auth/login')
}
</script>

<style scoped>
.brand-logo {
  background: linear-gradient(135deg, #1976d2, #1565c0);
}

.border-b {
  border-bottom: 1px solid rgba(0,0,0,0.12);
}

.border-t {
  border-top: 1px solid rgba(0,0,0,0.12);
}

.rounded-lg {
  border-radius: 8px;
}



.cursor-pointer {
  cursor: pointer;
}
</style>