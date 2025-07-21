<template>
  <v-navigation-drawer
    v-model="drawer"
    :rail="!isExpanded"
    permanent
    class="left-sidebar"
    elevation="3"
  >
    <div class="sidebar-header">
      <div class="d-flex align-center px-2">
        <v-avatar size="40" color="primary" class="mr-2">
          <v-img src="/favicon.svg" alt="Logo"></v-img>
        </v-avatar>
        <span v-if="isExpanded" class="text-h6 font-weight-bold">Paksa Financial</span>
        <v-spacer></v-spacer>
        <v-btn
          :icon="isExpanded ? 'mdi-chevron-left' : 'mdi-chevron-right'"
          variant="text"
          size="small"
          @click.stop="toggleMenu"
        ></v-btn>
      </div>
    </div>

    <v-divider></v-divider>

    <div class="sidebar-scroll">
      <v-list nav>
        <template v-for="item in menuItems" :key="item.id">
          <!-- Single menu item without children -->
          <v-list-item
            v-if="!item.items || item.items.length === 0"
            :prepend-icon="item.icon"
            :title="item.label"
            :to="item.route"
            :active="isActive(item.route)"
            rounded="lg"
            class="mb-1"
            @click="setActiveMenuItem(item.id)"
          ></v-list-item>

          <!-- Menu item with children -->
          <v-list-group v-else :value="isModuleActive(item)">
            <template v-slot:activator="{ props: groupProps }">
              <v-list-item
                v-bind="groupProps"
                :prepend-icon="item.icon"
                :title="item.label"
                :active="isModuleActive(item)"
                rounded="lg"
                class="mb-1 module-item"
                @click="setActiveMenuItem(item.id)"
              ></v-list-item>
            </template>

            <v-list-item
              v-for="child in item.items"
              :key="child.id"
              :prepend-icon="child.icon"
              :title="child.label"
              :to="child.route"
              :active="isActive(child.route)"
              rounded="lg"
              class="ml-4 mb-1 sub-item"
              @click="setActiveMenuItem(child.id)"
            ></v-list-item>
          </v-list-group>
        </template>
      </v-list>
    </div>

    <template v-slot:append>
      <v-divider class="mb-2"></v-divider>
      <div class="pa-2">
        <v-list nav density="compact">
          <v-list-item 
            prepend-icon="mdi-cog" 
            title="Settings" 
            to="/settings" 
            rounded="lg" 
            class="mb-1"
            @click="setActiveMenuItem('settings')"
          ></v-list-item>
          <v-list-item 
            prepend-icon="mdi-help-circle" 
            title="Help" 
            to="/help" 
            rounded="lg" 
            class="mb-1"
            @click="setActiveMenuItem('help')"
          ></v-list-item>
          <v-list-item 
            prepend-icon="mdi-logout" 
            title="Logout" 
            @click="logout" 
            rounded="lg"
          ></v-list-item>
        </v-list>
      </div>
    </template>
  </v-navigation-drawer>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter, type RouteLocationNormalizedLoaded } from 'vue-router';
import { useMenuStore } from '../../stores/menu';
import type { SidebarMenuItem } from '@/config/menu';

const menuStore = useMenuStore();
const route: RouteLocationNormalizedLoaded = useRoute();
const router = useRouter();
const drawer = ref<boolean>(true);

// Get menu items from store with user permissions
const userPermissions = ref<string[]>([]); // TODO: Replace with actual user permissions
const menuItems = computed(() => menuStore.getAuthorizedMenuItems(userPermissions.value));
const isExpanded = computed(() => !menuStore.getIsMenuCollapsed);

// Check if a route is active
const isActive = (routePath: string | RouteLocationNormalizedLoaded | undefined): boolean => {
  if (!routePath) return false;
  const path = typeof routePath === 'string' ? routePath : routePath.path;
  return route.path === path || route.path.startsWith(`${path}/`);
};

// Check if a module is active (for group items)
const isModuleActive = (menuItem: SidebarMenuItem): boolean => {
  if (menuItem.route && isActive(menuItem.route)) return true;
  if (menuItem.items) {
    return menuItem.items.some(child => isModuleActive(child));
  }
  return false;
};

// Toggle menu expanded/collapsed
const toggleMenu = () => {
  menuStore.toggleMenu();
};

// Set active menu item
const setActiveMenuItem = (itemId: string) => {
  menuStore.setActiveMenuItem(itemId);
};

// Logout function
const logout = () => {
  // Clear authentication
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  
  // Redirect to login
  router.push('/auth/login');
};

// Initialize menu
onMounted(() => {
  // TODO: Load user permissions from auth store or API
  // For now, we'll just show all menu items
  userPermissions.value = [];
});
</script>

<style>
.sidebar-header {
  height: 64px;
  display: flex;
  align-items: center;
}

.left-sidebar {
  border-right: 1px solid rgba(0, 0, 0, 0.12);
}

.sidebar-scroll {
  height: calc(100vh - 180px);
  overflow-y: auto;
}

.v-list-item--active {
  background-color: rgba(25, 118, 210, 0.12) !important;
  color: rgb(25, 118, 210) !important;
}

.v-list-item:hover {
  background-color: rgba(0, 0, 0, 0.04);
}

.v-list-item--active:hover {
  background-color: rgba(25, 118, 210, 0.16) !important;
}

.v-list-group__items .v-list-item--active {
  background-color: rgba(25, 118, 210, 0.12) !important;
}

.v-navigation-drawer--rail .v-list-item-title {
  opacity: 0;
}

.module-item .v-list-item__content,
.sub-item .v-list-item__content {
  opacity: 1 !important;
}
</style>