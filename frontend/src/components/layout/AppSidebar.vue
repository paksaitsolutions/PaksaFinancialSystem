<template>
  <div 
    class="app-sidebar" 
    :class="{ 'collapsed': collapsed, 'mobile-menu': isMobileMenuOpen }"
    @click="handleClick"
  >
    <div class="sidebar-header">
      <router-link to="/" class="logo-container">
        <img 
          v-if="!collapsed"
          src="@/assets/logo.png" 
          alt="Paksa Financial System" 
          class="logo"
        >
        <img 
          v-else
          src="@/assets/logo-icon.png" 
          alt="PFS" 
          class="logo-icon"
        >
      </router-link>
    </div>

    <div class="sidebar-content">
      <Menu :model="visibleMenuItems" class="sidebar-menu">
        <template #item="{ item }">
          <router-link 
            v-if="item.route" 
            v-slot="{ href, navigate }" 
            :to="item.route"
            custom
          >
            <a 
              :href="href" 
              @click="[navigate, $emit('navigate')]"
              class="p-menuitem-link"
              :class="{ 'p-disabled': item.disabled }"
            >
              <span :class="item.icon"></span>
              <span class="ml-2">{{ item.label }}</span>
              <span v-if="item.badge" class="ml-auto">
                <Badge :value="item.badge" :severity="item.badgeSeverity" />
              </span>
              <span v-if="item.items && item.items.length > 0" class="ml-auto">
                <i class="pi pi-angle-down"></i>
              </span>
            </a>
          </router-link>
        </template>
      </Menu>
    </div>

    <div class="sidebar-footer">
      <Button 
        icon="pi pi-cog" 
        class="p-button-text p-button-plain"
        @click="navigateToSettings"
      >
        <span v-if="!collapsed" class="ml-2">Settings</span>
      </Button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import type { RouteLocationRaw } from 'vue-router';
import { useAuthStore } from '@/store/auth';
import Menu from 'primevue/menu';
import Button from 'primevue/button';
import Badge from 'primevue/badge';

defineProps({
  collapsed: {
    type: Boolean,
    default: false
  },
  isMobileMenuOpen: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['navigate']);
const router = useRouter();
const authStore = useAuthStore();

// Types
type BadgeSeverity = 'success' | 'info' | 'warning' | 'danger' | 'contrast' | 'secondary' | null | undefined;

interface SidebarMenuItem {
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

// Check if menu item should be visible
const isMenuItemVisible = (item: SidebarMenuItem): boolean => {
  // If visibility is a function, call it
  if (typeof item.visible === 'function') {
    return item.visible();
  }
  
  // Check permissions if specified
  if (item.permission) {
    if (Array.isArray(item.permission)) {
      return authStore.hasAnyPermission(item.permission);
    }
    return authStore.hasPermission(item.permission);
  }
  
  // Default to visible if no specific conditions
  return item.visible !== false;
};

// Filter menu items based on visibility
const filterMenuItems = (items: SidebarMenuItem[]): SidebarMenuItem[] => {
  return items
    .map(item => ({
      ...item,
      // Process sub-items if they exist
      items: item.items ? filterMenuItems(item.items) : undefined,
      // Evaluate visibility
      visible: isMenuItemVisible(item)
    }))
    .filter(item => item.visible);
};

// Compute visible menu items based on permissions
const visibleMenuItems = computed(() => filterMenuItems(menuItems.value));

// Menu items configuration
const menuItems = ref<SidebarMenuItem[]>([
  {
    label: 'Dashboard',
    icon: 'pi pi-home',
    route: '/',
    visible: true
  },
  {
    label: 'General Ledger',
    icon: 'pi pi-book',
    permission: 'view_general_ledger',
    visible: true,
    items: [
      { label: 'Dashboard', icon: 'pi pi-chart-bar', route: '/gl/dashboard', visible: true },
      { label: 'Chart of Accounts', icon: 'pi pi-sitemap', route: '/gl/accounts', visible: true },
      { label: 'Journal Entries', icon: 'pi pi-book', route: '/gl/journal-entries', visible: true },
      { label: 'Trial Balance', icon: 'pi pi-balance-scale', route: '/gl/trial-balance', visible: true },
      { label: 'Financial Statements', icon: 'pi pi-file-pdf', route: '/gl/financial-statements', visible: true },
      { label: 'Recurring Journals', icon: 'pi pi-sync', route: '/gl/recurring-journals', visible: true },
      { label: 'Allocation Rules', icon: 'pi pi-share-alt', route: '/gl/allocation-rules', visible: true },
      { label: 'Period Close', icon: 'pi pi-lock', route: '/gl/period-close', visible: true }
    ]
  },
  {
    label: 'Accounts Payable',
    icon: 'pi pi-credit-card',
    permission: 'view_accounts_payable',
    visible: true,
    items: [
      { label: 'Dashboard', icon: 'pi pi-chart-bar', route: '/ap/dashboard', visible: true },
      { label: 'Vendors', icon: 'pi pi-users', route: '/ap/vendors', visible: true },
      { label: 'Invoices', icon: 'pi pi-file-import', route: '/ap/invoices', visible: true },
      { label: 'Payments', icon: 'pi pi-money-bill', route: '/ap/payments', visible: true },
      { label: 'Expense Reports', icon: 'pi pi-receipt', route: '/ap/expense-reports', visible: true },
      { label: 'Purchase Orders', icon: 'pi pi-shopping-cart', route: '/ap/purchase-orders', visible: true },
      { label: 'Aging Report', icon: 'pi pi-clock', route: '/ap/aging-report', visible: true },
      { label: '1099 Reporting', icon: 'pi pi-file-pdf', route: '/ap/1099-reporting', visible: true }
    ]
  },
  {
    label: 'Accounts Receivable',
    icon: 'pi pi-money-bill',
    permission: 'view_accounts_receivable',
    visible: true,
    items: [
      { label: 'Dashboard', icon: 'pi pi-chart-bar', route: '/ar/dashboard', visible: true },
      { label: 'Customers', icon: 'pi pi-users', route: '/ar/customers', visible: true },
      { label: 'Invoices', icon: 'pi pi-file-export', route: '/ar/invoices', visible: true },
      { label: 'Payments', icon: 'pi pi-credit-card', route: '/ar/payments', visible: true },
      { label: 'Credit Notes', icon: 'pi pi-undo', route: '/ar/credit-notes', visible: true },
      { label: 'Collections', icon: 'pi pi-inbox', route: '/ar/collections', visible: true },
      { label: 'Aging Report', icon: 'pi pi-clock', route: '/ar/aging-report', visible: true },
      { label: 'Customer Statements', icon: 'pi pi-file-pdf', route: '/ar/statements', visible: true }
    ]
  },
  {
    label: 'Cash Management',
    icon: 'pi pi-wallet',
    permission: 'view_cash_management',
    visible: true,
    items: [
      { label: 'Cash Position', icon: 'pi pi-chart-line', route: '/cash/position', visible: true },
      { label: 'Bank Accounts', icon: 'pi pi-building', route: '/cash/accounts', visible: true },
      { label: 'Bank Reconciliation', icon: 'pi pi-sync', route: '/cash/reconciliation', visible: true },
      { label: 'Cash Flow Forecast', icon: 'pi pi-chart-bar', route: '/cash/forecast', visible: true },
      { label: 'Funds Transfer', icon: 'pi pi-exchange', route: '/cash/transfer', visible: true },
      { label: 'Cash Receipts', icon: 'pi pi-arrow-down', route: '/cash/receipts', visible: true },
      { label: 'Cash Disbursements', icon: 'pi pi-arrow-up', route: '/cash/disbursements', visible: true },
      { label: 'Bank Feeds', icon: 'pi pi-cloud-download', route: '/cash/bank-feeds', visible: true }
    ]
  },
  {
    label: 'Fixed Assets',
    icon: 'pi pi-building',
    permission: 'view_fixed_assets',
    visible: true,
    items: [
      { label: 'Asset Register', icon: 'pi pi-list', route: '/assets/register', visible: true },
      { label: 'Acquisitions', icon: 'pi pi-plus-circle', route: '/assets/acquisitions', visible: true },
      { label: 'Depreciation', icon: 'pi pi-chart-line', route: '/assets/depreciation', visible: true },
      { label: 'Disposals', icon: 'pi pi-trash', route: '/assets/disposals', visible: true },
      { label: 'Transfers', icon: 'pi pi-sync', route: '/assets/transfers', visible: true },
      { label: 'Maintenance', icon: 'pi pi-wrench', route: '/assets/maintenance', visible: true },
      { label: 'Reports', icon: 'pi pi-file-pdf', route: '/assets/reports', visible: true },
      { label: 'Settings', icon: 'pi pi-cog', route: '/assets/settings', visible: true }
    ]
  },
  {
    label: 'Payroll',
    icon: 'pi pi-users',
    permission: 'view_payroll',
    visible: true,
    items: [
      { label: 'Dashboard', icon: 'pi pi-chart-bar', route: '/payroll/dashboard', visible: true },
      { label: 'Employees', icon: 'pi pi-user', route: '/payroll/employees', visible: true },
      { label: 'Process Payroll', icon: 'pi pi-calculator', route: '/payroll/process', visible: true },
      { label: 'Payslips', icon: 'pi pi-file-pdf', route: '/payroll/payslips', visible: true },
      { label: 'Taxes', icon: 'pi pi-percentage', route: '/payroll/taxes', visible: true },
      { label: 'Benefits', icon: 'pi pi-heart', route: '/payroll/benefits', visible: true },
      { label: 'Reports', icon: 'pi pi-chart-line', route: '/payroll/reports', visible: true },
      { label: 'Year-End', icon: 'pi pi-calendar', route: '/payroll/yearend', visible: true }
    ]
  },
  {
    label: 'Inventory',
    icon: 'pi pi-box',
    permission: 'view_inventory',
    visible: true,
    items: [
      { label: 'Dashboard', icon: 'pi pi-chart-bar', route: '/inventory/dashboard', visible: true },
      { label: 'Items', icon: 'pi pi-tags', route: '/inventory/items', visible: true },
      { label: 'Stock Movements', icon: 'pi pi-arrow-right-arrow-left', route: '/inventory/movements', visible: true },
      { label: 'Transfers', icon: 'pi pi-truck', route: '/inventory/transfers', visible: true },
      { label: 'Adjustments', icon: 'pi pi-sliders-h', route: '/inventory/adjustments', visible: true },
      { label: 'Counts', icon: 'pi pi-list-check', route: '/inventory/counts', visible: true },
      { label: 'Valuation', icon: 'pi pi-dollar', route: '/inventory/valuation', visible: true },
      { label: 'Reports', icon: 'pi pi-file-pdf', route: '/inventory/reports', visible: true }
    ]
  },
  {
    label: 'Project Accounting',
    icon: 'pi pi-briefcase',
    permission: 'view_project_accounting',
    visible: true,
    items: [
      { label: 'Projects', icon: 'pi pi-folder', route: '/projects', visible: true },
      { label: 'Time & Expense', icon: 'pi pi-clock', route: '/projects/time-expense', visible: true },
      { label: 'Billing', icon: 'pi pi-file-invoice', route: '/projects/billing', visible: true },
      { label: 'Budgeting', icon: 'pi pi-chart-pie', route: '/projects/budgets', visible: true },
      { label: 'Profitability', icon: 'pi pi-chart-line', route: '/projects/profitability', visible: true },
      { label: 'Resource Planning', icon: 'pi pi-users', route: '/projects/resource-planning', visible: true },
      { label: 'Reports', icon: 'pi pi-file-pdf', route: '/projects/reports', visible: true },
      { label: 'Settings', icon: 'pi pi-cog', route: '/projects/settings', visible: true }
    ]
  },
  {
    label: 'Procurement',
    icon: 'pi pi-shopping-cart',
    permission: 'view_procurement',
    visible: true,
    items: [
      { label: 'Requisitions', icon: 'pi pi-shopping-bag', route: '/procurement/requisitions', visible: true },
      { label: 'Purchase Orders', icon: 'pi pi-file-edit', route: '/procurement/purchase-orders', visible: true },
      { label: 'Vendors', icon: 'pi pi-building', route: '/procurement/vendors', visible: true },
      { label: 'RFQs', icon: 'pi pi-file', route: '/procurement/rfqs', visible: true },
      { label: 'Receiving', icon: 'pi pi-check-square', route: '/procurement/receiving', visible: true },
      { label: 'Contracts', icon: 'pi pi-file-contract', route: '/procurement/contracts', visible: true },
      { label: 'Spend Analysis', icon: 'pi pi-chart-bar', route: '/procurement/spend-analysis', visible: true },
      { label: 'Settings', icon: 'pi pi-cog', route: '/procurement/settings', visible: true }
    ]
  },
  {
    label: 'Tax Management',
    icon: 'pi pi-percentage',
    permission: 'view_tax_module',
    visible: true,
    items: [
      // Dashboard & Analytics
      { 
        label: 'Dashboard', 
        icon: 'pi pi-chart-bar', 
        route: '/tax/dashboard', 
        permission: 'view_tax_dashboard',
        visible: true 
      },
      { 
        label: 'Compliance', 
        icon: 'pi pi-shield', 
        route: '/tax/compliance', 
        permission: 'view_tax_compliance',
        visible: true 
      },
      
      // Tax Setup & Configuration
      { 
        label: 'Tax Codes', 
        icon: 'pi pi-tag', 
        route: '/tax/codes', 
        permission: 'view_tax_codes',
        visible: true 
      },
      { 
        label: 'Tax Rates', 
        icon: 'pi pi-percent', 
        route: '/tax/rates', 
        permission: 'view_tax_rates',
        visible: true 
      },
      { 
        label: 'Jurisdictions', 
        icon: 'pi pi-globe', 
        route: '/tax/jurisdictions', 
        permission: 'view_tax_jurisdictions',
        visible: true 
      },
      
      // Exemptions & Certificates
      { 
        label: 'Exemptions', 
        icon: 'pi pi-file-export', 
        route: '/tax/exemptions', 
        permission: 'view_tax_exemptions',
        visible: true 
      },
      { 
        label: 'Exemption Certificates', 
        icon: 'pi pi-file-pdf', 
        route: '/tax/exemption-certificates', 
        permission: 'view_tax_exemption_certificates',
        visible: true 
      },
      
      // Tax Operations
      { 
        label: 'Tax Liability', 
        icon: 'pi pi-money-bill', 
        route: '/tax/liability', 
        permission: 'view_tax_liability',
        visible: true 
      },
      { 
        label: 'Tax Filing', 
        icon: 'pi pi-upload', 
        route: '/tax/filing', 
        permission: 'view_tax_filing',
        visible: true 
      },
      
      // Reports & Analytics
      { 
        label: 'Tax Reports', 
        icon: 'pi pi-chart-line', 
        route: '/tax/reports', 
        permission: 'view_tax_reports',
        visible: true 
      },
      
      // Configuration
      { 
        label: 'Tax Policy', 
        icon: 'pi pi-book', 
        route: '/tax/policy', 
        permission: 'view_tax_policy',
        visible: true 
      },
      { 
        label: 'Settings', 
        icon: 'pi pi-cog', 
        route: '/tax/settings', 
        permission: 'manage_tax_settings',
        visible: true 
      }
    ]
  },
  {
    label: 'Compliance',
    icon: 'pi pi-shield',
    permission: 'view_compliance',
    visible: true,
    items: [
      { label: 'Dashboard', icon: 'pi pi-chart-bar', route: '/compliance', visible: true },
      { label: 'Audit Logs', icon: 'pi pi-history', route: '/compliance/audit-logs', visible: true },
      { label: 'Policies', icon: 'pi pi-file', route: '/compliance/policies', visible: true },
      { label: 'Risk Assessment', icon: 'pi pi-exclamation-triangle', route: '/compliance/risk', visible: true },
      { label: 'Training', icon: 'pi pi-graduation-cap', route: '/compliance/training', visible: true },
      { label: 'Incidents', icon: 'pi pi-exclamation-circle', route: '/compliance/incidents', visible: true },
      { label: 'Reports', icon: 'pi pi-file-pdf', route: '/compliance/reports', visible: true },
      { label: 'Settings', icon: 'pi pi-cog', route: '/compliance/settings', visible: true }
    ]
  },
  {
    label: 'Budgeting',
    icon: 'pi pi-chart-bar',
    permission: 'view_budgeting',
    visible: true,
    items: [
      { label: 'Dashboard', icon: 'pi pi-chart-bar', route: '/bi/dashboard', visible: true },
      { label: 'Reports', icon: 'pi pi-file-pdf', route: '/bi/reports', visible: true },
      { label: 'Analytics', icon: 'pi pi-chart-line', route: '/bi/analytics', visible: true },
      { label: 'Data Explorer', icon: 'pi pi-search', route: '/bi/explorer', visible: true },
      { label: 'KPIs', icon: 'pi pi-chart-bar', route: '/bi/kpis', visible: true },
      { label: 'Alerts', icon: 'pi pi-bell', route: '/bi/alerts', visible: true },
      { label: 'Scheduled Reports', icon: 'pi pi-clock', route: '/bi/scheduled-reports', visible: true },
      { label: 'Settings', icon: 'pi pi-cog', route: '/bi/settings', visible: true }
    ]
  },
  {
    label: 'Document Management',
    icon: 'pi pi-folder',
    permission: 'view_document_management',
    visible: true,
    items: [
      { label: 'My Documents', icon: 'pi pi-folder-open', route: '/documents/my', visible: true },
      { label: 'Shared', icon: 'pi pi-users', route: '/documents/shared', visible: true },
      { label: 'Recent', icon: 'pi pi-clock', route: '/documents/recent', visible: true },
      { label: 'Templates', icon: 'pi pi-file', route: '/documents/templates', visible: true },
      { label: 'Trash', icon: 'pi pi-trash', route: '/documents/trash', visible: true },
      { label: 'Search', icon: 'pi pi-search', route: '/documents/search', visible: true },
      { label: 'Workflows', icon: 'pi pi-sitemap', route: '/documents/workflows', visible: true },
      { label: 'Settings', icon: 'pi pi-cog', route: '/documents/settings', visible: true }
    ]
  },
  {
    label: 'Reports',
    icon: 'pi pi-chart-bar',
    permission: 'view_reports',
    route: '/reports',
    visible: true,
    items: [
      // Favorites section
      {
        label: 'Favorites',
        icon: 'pi pi-star',
        visible: true,
        items: [
          { label: 'Report Dashboard', icon: 'pi pi-home', route: '/reports', visible: true },
          { label: 'Recent Reports', icon: 'pi pi-history', route: '/reports?filter=recent', visible: true },
          { label: 'Favorites', icon: 'pi pi-star', route: '/reports?filter=favorites', visible: true }
        ]
      },
      {
        label: 'Financial Statements',
        icon: 'pi pi-file-pdf',
        visible: true,
        items: [
          { label: 'Balance Sheet', icon: 'pi pi-balance-scale', route: '/reports/balance-sheet', visible: true },
          { label: 'Income Statement', icon: 'pi pi-chart-line', route: '/reports/income-statement', visible: true },
          { label: 'Cash Flow', icon: 'pi pi-money-bill', route: '/reports/cash-flow', visible: true },
          { label: 'Statement of Changes', icon: 'pi pi-chart-bar', route: '/reports/changes-in-equity', visible: true }
        ]
      },
      {
        label: 'Receivables & Payables',
        icon: 'pi pi-credit-card',
        visible: true,
        items: [
          { label: 'AR Aging', icon: 'pi pi-credit-card', route: '/reports/ar-aging', visible: true },
          { label: 'AP Aging', icon: 'pi pi-shopping-cart', route: '/reports/ap-aging', visible: true },
          { label: 'Customer Statements', icon: 'pi pi-user', route: '/reports/customer-statements', visible: true },
          { label: 'Vendor Balances', icon: 'pi pi-building', route: '/reports/vendor-balances', visible: true }
        ]
      },
      {
        label: 'General Ledger',
        icon: 'pi pi-book',
        visible: true,
        items: [
          { label: 'Trial Balance', icon: 'pi pi-book', route: '/reports/trial-balance', visible: true },
          { label: 'General Ledger', icon: 'pi pi-book', route: '/reports/general-ledger', visible: true },
          { label: 'Chart of Accounts', icon: 'pi pi-sitemap', route: '/reports/chart-of-accounts', visible: true },
          { label: 'Journal Entries', icon: 'pi pi-file-edit', route: '/reports/journal-entries', visible: true }
        ]
      },
      {
        label: 'Taxation',
        icon: 'pi pi-percentage',
        visible: true,
        items: [
          { label: 'Sales Tax', icon: 'pi pi-percentage', route: '/reports/sales-tax', visible: true },
          { label: 'VAT Report', icon: 'pi pi-euro', route: '/reports/vat', visible: true },
          { label: 'Tax Summary', icon: 'pi pi-file-export', route: '/reports/tax-summary', visible: true },
          { label: 'Tax Liabilities', icon: 'pi pi-exclamation-triangle', route: '/reports/tax-liabilities', visible: true }
        ]
      },
      {
        label: 'Performance',
        icon: 'pi pi-chart-line',
        visible: true,
        items: [
          { label: 'Budget vs Actual', icon: 'pi pi-chart-bar', route: '/reports/budget-vs-actual', visible: true },
          { label: 'Expense Analysis', icon: 'pi pi-chart-pie', route: '/reports/expense-analysis', visible: true },
          { label: 'Revenue by Customer', icon: 'pi pi-users', route: '/reports/revenue-by-customer', visible: true },
          { label: 'Department Performance', icon: 'pi pi-sitemap', route: '/reports/department-performance', visible: true }
        ]
      },
      {
        label: 'Assets & Inventory',
        icon: 'pi pi-box',
        visible: true,
        items: [
          { label: 'Inventory Valuation', icon: 'pi pi-tags', route: '/reports/inventory-valuation', visible: true },
          { label: 'Fixed Assets', icon: 'pi pi-building', route: '/reports/fixed-assets', visible: true },
          { label: 'Asset Depreciation', icon: 'pi pi-chart-line', route: '/reports/asset-depreciation', visible: true },
          { label: 'Stock Movement', icon: 'pi pi-arrow-right-arrow-left', route: '/reports/stock-movement', visible: true }
        ]
      },
      {
        label: 'Human Resources',
        icon: 'pi pi-users',
        visible: true,
        items: [
          { label: 'Payroll Summary', icon: 'pi pi-money-bill', route: '/reports/payroll-summary', visible: true },
          { label: 'Employee Performance', icon: 'pi pi-user-edit', route: '/reports/employee-performance', visible: true },
          { label: 'Time & Attendance', icon: 'pi pi-clock', route: '/reports/attendance', visible: true }
        ]
      },
      // Custom Reports section
      {
        label: 'Custom & Tools',
        icon: 'pi pi-wrench',
        visible: true,
        items: [
          { label: 'Custom Reports', icon: 'pi pi-file-edit', route: '/reports/custom', visible: true, badge: 'New', badgeSeverity: 'info' as BadgeSeverity },
          { label: 'Report Builder', icon: 'pi pi-wrench', route: '/reports/builder', visible: true },
          { label: 'Scheduled Reports', icon: 'pi pi-clock', route: '/reports/scheduled', visible: true },
          { label: 'Report Templates', icon: 'pi pi-copy', route: '/reports/templates', visible: true }
        ]
      }
    ]
  },
  {
    label: 'System Administration',
    icon: 'pi pi-cog',
    permission: 'view_system_administration',
    visible: true,
    items: [
      { label: 'Users', icon: 'pi pi-users', route: '/admin/users', visible: true },
      { label: 'Roles & Permissions', icon: 'pi pi-key', route: '/admin/roles', visible: true },
      { label: 'System Settings', icon: 'pi pi-cog', route: '/admin/settings', visible: true },
      { label: 'Email Templates', icon: 'pi pi-envelope', route: '/admin/email-templates', visible: true },
      { label: 'Audit Trail', icon: 'pi pi-history', route: '/admin/audit-trail', visible: true },
      { label: 'System Logs', icon: 'pi pi-list', route: '/admin/logs', visible: true },
      { label: 'Backup & Restore', icon: 'pi pi-cloud', route: '/admin/backup', visible: true },
      { label: 'System Health', icon: 'pi pi-heart', route: '/admin/health', visible: true }
    ]
  }
]);

// Methods
const navigateToSettings = () => {
  if (authStore.hasPermission('view_settings')) {
    router.push('/settings');
    emit('navigate');
  }
};

const handleClick = (event: Event) => {
  // Prevent event propagation to avoid closing mobile menu when clicking inside
  event.stopPropagation();
};
</script>

<style scoped>
.app-sidebar {
  width: 250px;
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
  z-index: 1000;
  background-color: var(--surface-card);
  box-shadow: 0 0 1px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
  overflow-y: auto;
}

.app-sidebar.collapsed {
  width: 60px;
  overflow: hidden;
}

.sidebar-header {
  padding: 1rem;
  border-bottom: 1px solid var(--surface-border);
  display: flex;
  align-items: center;
  justify-content: center;
  height: 60px;
}

.logo-container {
  display: flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
}

.logo {
  max-height: 40px;
  max-width: 100%;
}

.logo-icon {
  max-height: 30px;
  max-width: 30px;
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem 0;
}

.sidebar-menu {
  border: none;
  width: 100%;
}

.sidebar-menu :deep(.p-menuitem-link) {
  border-radius: 0;
  padding: 0.75rem 1.5rem;
  color: var(--text-color);
  transition: all 0.2s;
}

.sidebar-menu :deep(.p-menuitem-link:hover) {
  background-color: var(--surface-hover);
}

.sidebar-menu :deep(.p-menuitem-link.router-link-active) {
  background-color: var(--primary-color);
  color: var(--primary-color-text);
}

.sidebar-menu :deep(.p-menuitem-link .pi) {
  font-size: 1.1rem;
}

.sidebar-footer {
  padding: 1rem;
  border-top: 1px solid var(--surface-border);
}

/* Mobile menu styles */
@media (max-width: 991px) {
  .app-sidebar {
    transform: translateX(-100%);
    z-index: 1100;
  }
  
  .app-sidebar.mobile-menu {
    transform: translateX(0);
    box-shadow: 4px 0 10px rgba(0, 0, 0, 0.15);
  }
}

/* Collapsed state styles */
.collapsed .menu-item-text,
.collapsed .p-badge,
.collapsed .menu-toggle-icon {
  display: none;
}

.collapsed .p-menuitem-link {
  justify-content: center;
  padding: 0.75rem 0;
}

.collapsed .p-menuitem-link .pi {
  margin-right: 0;
  font-size: 1.25rem;
}

/* Animation */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
