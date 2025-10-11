<template>
  <nav class="unified-nav" :class="{ 'nav-collapsed': collapsed }">
    <div class="nav-header">
      <div class="nav-brand">
        <img src="/logo.svg" alt="Paksa Financial" class="nav-logo" />
        <span v-if="!collapsed" class="nav-title">Paksa Financial</span>
      </div>
      <Button 
        icon="pi pi-bars" 
        class="nav-toggle" 
        text 
        @click="toggleCollapse"
      />
    </div>

    <div class="nav-content">
      <div class="nav-section">
        <div v-if="!collapsed" class="nav-section-title">Main</div>
        <div class="nav-items">
          <router-link
            v-for="item in mainItems"
            :key="item.name"
            :to="item.to"
            class="nav-item"
            :class="{ active: isActive(item.to) }"
          >
            <i :class="item.icon" class="nav-item-icon"></i>
            <span v-if="!collapsed" class="nav-item-text">{{ item.label }}</span>
          </router-link>
        </div>
      </div>

      <div class="nav-section">
        <div v-if="!collapsed" class="nav-section-title">Modules</div>
        <div class="nav-items">
          <div
            v-for="module in moduleItems"
            :key="module.name"
            class="nav-group"
          >
            <div 
              class="nav-group-header"
              @click="toggleGroup(module.name)"
              :class="{ active: expandedGroups.includes(module.name) }"
            >
              <i :class="module.icon" class="nav-item-icon"></i>
              <span v-if="!collapsed" class="nav-item-text">{{ module.label }}</span>
              <i 
                v-if="!collapsed && module.children" 
                class="pi pi-chevron-down nav-group-arrow"
                :class="{ rotated: expandedGroups.includes(module.name) }"
              ></i>
            </div>
            <div 
              v-if="module.children && expandedGroups.includes(module.name) && !collapsed"
              class="nav-group-items"
            >
              <router-link
                v-for="child in module.children"
                :key="child.name"
                :to="child.to"
                class="nav-item nav-child"
                :class="{ active: isActive(child.to) }"
              >
                <span class="nav-item-text">{{ child.label }}</span>
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="nav-footer">
      <Button 
        icon="pi pi-question-circle" 
        :label="collapsed ? '' : 'Help'"
        text 
        class="nav-footer-btn"
      />
      <Button 
        icon="pi pi-sign-out" 
        :label="collapsed ? '' : 'Logout'"
        text 
        class="nav-footer-btn"
        @click="logout"
      />
    </div>
  </nav>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/modules/auth/store'
import Button from 'primevue/button'

const route = useRoute()
const authStore = useAuthStore()
const collapsed = ref(false)
const expandedGroups = ref<string[]>(['gl', 'ap', 'ar'])

const toggleCollapse = () => {
  collapsed.value = !collapsed.value
}

const toggleGroup = (groupName: string) => {
  if (collapsed.value) return
  
  const index = expandedGroups.value.indexOf(groupName)
  if (index > -1) {
    expandedGroups.value.splice(index, 1)
  } else {
    expandedGroups.value.push(groupName)
  }
}

const isActive = (path: string) => {
  return route.path.startsWith(path)
}

const logout = () => {
  authStore.logout()
}

const mainItems = [
  { name: 'dashboard', label: 'Dashboard', icon: 'pi pi-home', to: '/dashboard' },
  { name: 'reports', label: 'Reports', icon: 'pi pi-chart-bar', to: '/reports' },
  { name: 'ai-assistant', label: 'AI Assistant', icon: 'pi pi-android', to: '/ai' }
]

const moduleItems = [
  {
    name: 'gl',
    label: 'General Ledger',
    icon: 'pi pi-book',
    children: [
      { name: 'accounts', label: 'Chart of Accounts', to: '/gl/accounts' },
      { name: 'journal', label: 'Journal Entries', to: '/gl/journal' },
      { name: 'trial-balance', label: 'Trial Balance', to: '/gl/trial-balance' }
    ]
  },
  {
    name: 'ap',
    label: 'Accounts Payable',
    icon: 'pi pi-arrow-up-right',
    children: [
      { name: 'vendors', label: 'Vendors', to: '/ap/vendors' },
      { name: 'bills', label: 'Bills', to: '/ap/bills' },
      { name: 'payments', label: 'Payments', to: '/ap/payments' }
    ]
  },
  {
    name: 'ar',
    label: 'Accounts Receivable',
    icon: 'pi pi-arrow-down-left',
    children: [
      { name: 'customers', label: 'Customers', to: '/ar/customers' },
      { name: 'invoices', label: 'Invoices', to: '/ar/invoices' },
      { name: 'receipts', label: 'Receipts', to: '/ar/receipts' }
    ]
  },
  { name: 'cash', label: 'Cash Management', icon: 'pi pi-wallet', to: '/cash' },
  { name: 'payroll', label: 'Payroll', icon: 'pi pi-users', to: '/payroll' },
  { name: 'tax', label: 'Tax Management', icon: 'pi pi-percentage', to: '/tax' },
  { name: 'inventory', label: 'Inventory', icon: 'pi pi-box', to: '/inventory' },
  { name: 'fixed-assets', label: 'Fixed Assets', icon: 'pi pi-building', to: '/fixed-assets' },
  { name: 'budget', label: 'Budget', icon: 'pi pi-calculator', to: '/budget' },
  { name: 'hrm', label: 'Human Resources', icon: 'pi pi-user', to: '/hrm' }
]
</script>

<style scoped>
.unified-nav {
  width: 280px;
  height: 100vh;
  background: var(--surface-0);
  border-right: 1px solid var(--surface-200);
  display: flex;
  flex-direction: column;
  transition: width var(--transition-normal);
  position: fixed;
  left: 0;
  top: 0;
  z-index: 1000;
}

.nav-collapsed {
  width: 72px;
}

.nav-header {
  padding: var(--spacing-lg);
  border-bottom: 1px solid var(--surface-200);
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 72px;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.nav-logo {
  width: 32px;
  height: 32px;
}

.nav-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--text-color);
}

.nav-toggle {
  width: 40px;
  height: 40px;
}

.nav-content {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-md) 0;
}

.nav-section {
  margin-bottom: var(--spacing-lg);
}

.nav-section-title {
  padding: 0 var(--spacing-lg);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--text-color-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: var(--spacing-sm);
}

.nav-item {
  display: flex;
  align-items: center;
  padding: var(--spacing-md) var(--spacing-lg);
  color: var(--text-color);
  text-decoration: none;
  transition: all var(--transition-fast);
  border-left: 3px solid transparent;
}

.nav-item:hover {
  background: var(--surface-100);
}

.nav-item.active {
  background: var(--primary-50);
  color: var(--primary-600);
  border-left-color: var(--primary-600);
}

.nav-item-icon {
  width: 20px;
  font-size: 18px;
  margin-right: var(--spacing-md);
}

.nav-collapsed .nav-item-icon {
  margin-right: 0;
}

.nav-item-text {
  font-weight: var(--font-weight-medium);
}

.nav-group-header {
  display: flex;
  align-items: center;
  padding: var(--spacing-md) var(--spacing-lg);
  color: var(--text-color);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.nav-group-header:hover {
  background: var(--surface-100);
}

.nav-group-arrow {
  margin-left: auto;
  transition: transform var(--transition-fast);
}

.nav-group-arrow.rotated {
  transform: rotate(180deg);
}

.nav-group-items {
  background: var(--surface-50);
}

.nav-child {
  padding-left: calc(var(--spacing-lg) + 20px + var(--spacing-md));
  font-size: var(--font-size-sm);
}

.nav-footer {
  padding: var(--spacing-lg);
  border-top: 1px solid var(--surface-200);
}

.nav-footer-btn {
  width: 100%;
  justify-content: flex-start;
  margin-bottom: var(--spacing-sm);
}

.nav-footer-btn:last-child {
  margin-bottom: 0;
}

@media (max-width: 768px) {
  .unified-nav {
    transform: translateX(-100%);
    transition: transform var(--transition-normal);
  }
  
  .unified-nav.mobile-open {
    transform: translateX(0);
  }
}
</style>