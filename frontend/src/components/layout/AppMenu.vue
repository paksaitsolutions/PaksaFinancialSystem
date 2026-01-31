<template>
  <div class="app-menu">
    <Menu :model="model" class="w-full" />
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useRoute, type RouteLocationRaw } from 'vue-router';
import type { MenuItem } from 'primevue/menuitem';

interface MenuItemWithTo extends MenuItem {
  to?: RouteLocationRaw;
  items?: MenuItemWithTo[];
}

const props = defineProps<{
  model: MenuItemWithTo[];
}>();

const route = useRoute();
const activeItem = ref<MenuItemWithTo | null>(null);

// Update active menu item based on current route
watch(() => route.path, (newPath) => {
  if (!props.model?.length) return;
  
  // Find the menu item that matches the current route
  const findActiveItem = (items: MenuItemWithTo[]): MenuItemWithTo | null => {
    for (const item of items) {
      if (item.to && typeof item.to === 'string' && item.to === newPath) {
        return item;
      }
      if (item.items?.length) {
        const found = findActiveItem(item.items);
        if (found) return found;
      }
    }
    return null;
  };
  
  activeItem.value = findActiveItem(props.model);
}, { immediate: true });
</script>

<style scoped>
.app-menu {
  width: 100%;
  height: 100%;
}

:deep(.p-menu) {
  width: 100%;
  border: none;
  background: transparent;
}

:deep(.p-menuitem) {
  margin: 0.25rem 0;
}

:deep(.p-menuitem-link) {
  border-radius: 6px;
  padding: 0.75rem 1rem;
  transition: all 0.2s;
}

:deep(.p-menuitem-link:hover) {
  background-color: var(--primary-50);
}

:deep(.p-menuitem-link.router-link-active) {
  background-color: var(--primary-100);
  color: var(--primary-700);
  font-weight: 600;
}

:deep(.p-menuitem-link .p-menuitem-icon) {
  margin-right: 0.75rem;
  color: var(--primary-600);
}

:deep(.p-menuitem-link.router-link-active .p-menuitem-icon) {
  color: var(--primary-700);
}

:deep(.p-submenu-header) {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-color-secondary);
  padding: 1rem 1rem 0.5rem;
  margin-top: 0.5rem;
  font-weight: 600;
}

:deep(.p-submenu-list) {
  padding: 0.5rem 0 0.5rem 1rem;
}

:deep(.p-submenu-list .p-menuitem-link) {
  padding-left: 2.5rem;
}
</style>
