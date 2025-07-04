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
      <Menu :model="menuItems" class="sidebar-menu">
        <template #item="{ item, props, hasSubmenu, root }">
          <router-link 
            v-if="item.route" 
            v-slot="{ href, navigate }" 
            :to="item.route"
            custom
          >
            <a 
              :href="href" 
              v-bind="props.action"
              @click="[navigate, $emit('navigate')]"
              class="p-menuitem-link"
              :class="{ 'p-disabled': item.disabled }"
            >
              <span :class="item.icon"></span>
              <span class="ml-2">{{ item.label }}</span>
              <span v-if="item.badge" class="ml-auto">
                <Badge :value="item.badge" :severity="item.badgeSeverity" />
              </span>
              <span v-if="hasSubmenu" class="ml-auto">
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

const props = defineProps({
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
// Define our own menu item type to avoid conflicts with PrimeVue's MenuItem
type SidebarMenuItem = {
  label: string;
  icon: string;
  route?: RouteLocationRaw;
  visible: boolean;
  items?: SidebarMenuItem[];
  badge?: string;
  badgeSeverity?: 'success' | 'info' | 'warning' | 'danger' | 'contrast' | 'secondary';
  disabled?: boolean;
};

// Menu items
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
    route: '/general-ledger',
    visible: authStore.hasPermission('view_general_ledger')
  },
  {
    label: 'Accounts Payable',
    icon: 'pi pi-credit-card',
    route: '/accounts-payable',
    visible: authStore.hasPermission('view_accounts_payable')
  },
  {
    label: 'Accounts Receivable',
    icon: 'pi pi-money-bill',
    route: '/accounts-receivable',
    visible: authStore.hasPermission('view_accounts_receivable')
  },
  {
    label: 'Cash Management',
    icon: 'pi pi-wallet',
    route: '/cash-management',
    visible: authStore.hasPermission('view_cash_management')
  },
  {
    label: 'Fixed Assets',
    icon: 'pi pi-building',
    route: '/fixed-assets',
    visible: authStore.hasPermission('view_fixed_assets')
  },
  {
    label: 'Payroll',
    icon: 'pi pi-users',
    route: '/payroll',
    visible: authStore.hasPermission('view_payroll')
  },
  {
    label: 'Compliance & Security',
    icon: 'pi pi-shield',
    visible: authStore.hasAnyPermission([
      'view_compliance_dashboard',
      'view_audit_logs',
      'manage_data_subject_requests',
      'manage_security_policies',
      'view_security_events',
      'manage_encryption_keys'
    ]),
    items: [
      {
        label: 'Dashboard',
        icon: 'pi pi-chart-bar',
        route: '/compliance',
        visible: authStore.hasPermission('view_compliance_dashboard')
      },
      {
        label: 'Audit Logs',
        icon: 'pi pi-history',
        route: '/compliance/audit-logs',
        visible: authStore.hasPermission('view_audit_logs'),
        badge: 'New',
        badgeSeverity: 'info' as const
      },
      {
        label: 'Data Subject Requests',
        icon: 'pi pi-database',
        route: '/compliance/data-subject-requests',
        visible: authStore.hasPermission('manage_data_subject_requests')
      },
      {
        label: 'Security Policies',
        icon: 'pi pi-lock',
        route: '/compliance/security-policies',
        visible: authStore.hasPermission('manage_security_policies')
      },
      {
        label: 'Security Events',
        icon: 'pi pi-exclamation-triangle',
        route: '/compliance/security-events',
        visible: authStore.hasPermission('view_security_events')
      },
      {
        label: 'Encryption Keys',
        icon: 'pi pi-key',
        route: '/compliance/encryption-keys',
        visible: authStore.hasPermission('manage_encryption_keys')
      },
      {
        label: 'Encryption Management',
        icon: 'pi pi-lock',
        route: '/compliance/encryption-management',
        visible: authStore.hasPermission('manage_encryption_keys'),
        badge: 'New',
        badgeSeverity: 'success' as const
      }
    ]
  },
  {
    label: 'Reports',
    icon: 'pi pi-chart-line',
    route: '/reports',
    visible: authStore.hasPermission('view_reports')
  },
  {
    label: 'Administration',
    icon: 'pi pi-cog',
    route: '/admin',
    visible: authStore.hasAnyPermission([
      'manage_users',
      'manage_roles',
      'manage_settings'
    ])
  }
].filter(item => item.visible));

// Methods
const navigateToSettings = () => {
  router.push('/settings');
  emit('navigate');
};

const handleClick = (event: Event) => {
  // Prevent click events from propagating when sidebar is collapsed or in mobile mode
  if (props.collapsed || props.isMobileMenuOpen) {
    event.stopPropagation();
  }
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
