<template>
  <nav class="navigation-menu">
    <div class="menu-header">
      <img src="/logo.png" alt="Paksa Financial" class="logo" />
      <h2 v-if="!collapsed">Paksa Financial</h2>
    </div>
    
    <div class="menu-items">
      <router-link
        v-for="item in menuItems"
        :key="item.path"
        :to="item.path"
        class="menu-item"
        :class="{ active: isActive(item.path) }"
      >
        <i :class="item.icon"></i>
        <span v-if="!collapsed">{{ item.label }}</span>
      </router-link>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { useUIStore } from '@/stores/ui';

const route = useRoute();
const uiStore = useUIStore();

const collapsed = computed(() => uiStore.sidebarCollapsed);

const menuItems = [
  { path: '/', label: 'Dashboard', icon: 'pi pi-home' },
  { path: '/accounts-payable', label: 'Accounts Payable', icon: 'pi pi-credit-card' },
  { path: '/accounts-receivable', label: 'Accounts Receivable', icon: 'pi pi-money-bill' },
  { path: '/general-ledger', label: 'General Ledger', icon: 'pi pi-book' },
  { path: '/payroll', label: 'Payroll', icon: 'pi pi-users' },
  { path: '/inventory', label: 'Inventory', icon: 'pi pi-box' },
  { path: '/reports', label: 'Reports', icon: 'pi pi-chart-bar' },
  { path: '/settings', label: 'Settings', icon: 'pi pi-cog' }
];

const isActive = (path: string) => {
  if (path === '/') {
    return route.path === '/';
  }
  return route.path.startsWith(path);
};
</script>

<style scoped>
.navigation-menu {
  background: var(--surface-card);
  border-right: 1px solid var(--surface-border);
  height: 100vh;
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
}

.menu-header {
  padding: 1rem;
  border-bottom: 1px solid var(--surface-border);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.logo {
  width: 32px;
  height: 32px;
}

.menu-header h2 {
  margin: 0;
  font-size: 1.1rem;
  color: var(--text-color);
}

.menu-items {
  flex: 1;
  padding: 1rem 0;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  color: var(--text-color);
  text-decoration: none;
  transition: all 0.2s ease;
  border-left: 3px solid transparent;
}

.menu-item:hover {
  background: var(--surface-hover);
}

.menu-item.active {
  background: var(--primary-50);
  color: var(--primary-color);
  border-left-color: var(--primary-color);
}

.menu-item i {
  font-size: 1.1rem;
  width: 20px;
  text-align: center;
}
</style>