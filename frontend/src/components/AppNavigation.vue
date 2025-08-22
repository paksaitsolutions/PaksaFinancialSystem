<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRoute } from 'vue-router';
import { useAuthStore } from '@/modules/auth/store';

const authStore = useAuthStore();
const route = useRoute();
const drawer = ref(true);
const rail = ref(false);

const isActive = (path: string) => {
  return route.path.startsWith(path);
};

const navigationItems = computed(() => [
  {
    title: 'Dashboard',
    icon: 'mdi-view-dashboard',
    to: { name: 'dashboard' },
    active: isActive('/dashboard')
  },
  {
    title: 'General Ledger',
    icon: 'mdi-book-open-variant',
    to: { name: 'gl-accounts' },
    active: isActive('/gl'),
    children: [
      { title: 'Chart of Accounts', to: { name: 'gl-accounts' } },
      { title: 'Journal Entries', to: { name: 'journal-entries' } },
      { title: 'Financial Statements', to: { name: 'financial-statements' } },
      { title: 'Trial Balance', to: { name: 'trial-balance' } },
      { title: 'Reconciliation', to: { name: 'reconciliation' } },
    ]
  },
  {
    title: 'Accounts Payable',
    icon: 'mdi-account-arrow-right',
    to: { name: 'ap-invoices' },
    active: isActive('/ap'),
    children: [
      { title: 'Vendors', to: { name: 'vendors' } },
      { title: 'Bills', to: { name: 'ap-invoices' } },
      { title: 'Payments', to: { name: 'ap-payments' } },
      { title: 'Aging Report', to: { name: 'ap-aging' } },
    ]
  },
  {
    title: 'Accounts Receivable',
    icon: 'mdi-account-arrow-left',
    to: { name: 'ar-invoices' },
    active: isActive('/ar'),
    children: [
      { title: 'Customers', to: { name: 'customers' } },
      { title: 'Invoices', to: { name: 'ar-invoices' } },
      { title: 'Receipts', to: { name: 'ar-receipts' } },
      { title: 'Aging Report', to: { name: 'ar-aging' } },
    ]
  },
  {
    title: 'Payroll',
    icon: 'mdi-account-cash',
    to: { name: 'payroll' },
    active: isActive('/payroll'),
    children: [
      { title: 'Employees', to: { name: 'employees' } },
      { title: 'Pay Runs', to: { name: 'payroll-runs' } },
      { title: 'Tax Filings', to: { name: 'tax-filings' } },
      { title: 'Reports', to: { name: 'payroll-reports' } },
    ]
  },
  {
    title: 'Fixed Assets',
    icon: 'mdi-package-variant-closed',
    to: { name: 'fixed-assets' },
    active: isActive('/fixed-assets'),
    children: [
      { title: 'Asset Register', to: { name: 'fixed-assets' } },
      { title: 'Depreciation', to: { name: 'depreciation' } },
      { title: 'Disposals', to: { name: 'asset-disposals' } },
    ]
  },
  {
    title: 'Reports',
    icon: 'mdi-chart-box',
    to: { name: 'reports' },
    active: isActive('/reports')
  },
  {
    title: 'Settings',
    icon: 'mdi-cog',
    to: { name: 'settings' },
    active: isActive('/settings'),
    children: [
      { title: 'Company Profile', to: { name: 'company-profile' } },
      { title: 'Users & Permissions', to: { name: 'user-management' } },
      { title: 'Tax Settings', to: { name: 'tax-settings' } },
      { title: 'Integration', to: { name: 'integrations' } },
    ]
  },
]);

const toggleDrawer = () => {
  drawer.value = !drawer.value;
};

const toggleRail = () => {
  rail.value = !rail.value;
};
</script>

<template>
  <v-navigation-drawer
    v-model="drawer"
    :rail="rail"
    :rail-width="72"
    permanent
    class="elevation-1"
    @click="rail = false"
  >
    <v-list-item
      prepend-avatar="https://paksa.com.pk/wp-content/uploads/2023/09/cropped-paksa-logo-32x32.png"
      :title="rail ? '' : 'Paksa Financial'"
      nav
    >
      <template v-slot:append>
        <v-btn
          variant="text"
          :icon="rail ? 'mdi-chevron-right' : 'mdi-chevron-left'"
          @click.stop="toggleRail"
        ></v-btn>
      </template>
    </v-list-item>

    <v-divider></v-divider>

    <v-list density="compact" nav>
      <template v-for="(item, i) in navigationItems" :key="i">
        <v-list-group v-if="item.children" :value="item.active">
          <template v-slot:activator="{ props }">
            <v-list-item
              v-bind="props"
              :prepend-icon="item.icon"
              :title="item.title"
              :value="item.active"
            ></v-list-item>
          </template>

          <v-list-item
            v-for="(child, j) in item.children"
            :key="j"
            :to="child.to"
            :title="child.title"
            :active="isActive(child.to.name?.toString() || '')"
          ></v-list-item>
        </v-list-group>

        <v-list-item
          v-else
          :to="item.to"
          :prepend-icon="item.icon"
          :title="item.title"
          :active="isActive(item.to.name?.toString() || '')"
        ></v-list-item>
      </template>
    </v-list>

    <template v-slot:append>
      <div class="pa-2">
        <v-btn
          block
          variant="tonal"
          color="secondary"
          prepend-icon="mdi-help-circle"
          class="mb-2"
          to="/help"
        >
          <span v-if="!rail">Help & Support</span>
        </v-btn>
        
        <v-btn
          v-if="authStore.isAuthenticated"
          block
          variant="tonal"
          color="error"
          prepend-icon="mdi-logout"
          @click="authStore.logout()"
        >
          <span v-if="!rail">Logout</span>
        </v-btn>
      </div>
    </template>
  </v-navigation-drawer>
</template>

<style scoped>
.v-navigation-drawer {
  transition: all 0.2s ease-in-out;
}

.v-list-item--active {
  background-color: rgba(25, 118, 210, 0.08);
}

.v-list-item--active .v-list-item__prepend > .v-icon {
  color: rgb(var(--v-theme-primary));
}

.v-list-item--active::before {
  background-color: rgb(var(--v-theme-primary));
  opacity: 0.24;
}

.v-list-item--active:hover::before {
  opacity: 0.32;
}

.v-list-group__items .v-list-item {
  padding-left: 32px;
}

.v-list-group__items .v-list-item--active {
  font-weight: 600;
}

.v-list-item__prepend > .v-icon {
  margin-inline-end: 16px;
}

.v-list-item--density-compact:not(.v-list-item--nav).v-list-item--one-line {
  padding-inline: 12px;
}
</style>
