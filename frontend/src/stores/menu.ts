import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { SidebarMenuItem } from '@/config/menu';

import { menuItems } from '@/config/menu';

export const useMenuStore = defineStore('menu', () => {
  // State
  const isMenuCollapsed = ref(false);
  const activeMenuItem = ref<string | null>(null);
  const navigationItems = ref<SidebarMenuItem[]>(menuItems);

  // Getters
  const getActiveMenuItem = computed(() => {
    if (!activeMenuItem.value) return null;
    return getMenuItemById(activeMenuItem.value);
  });

  const getIsMenuCollapsed = computed(() => isMenuCollapsed.value);
  const getMenuItems = computed(() => navigationItems.value);

  // Check if a menu item is visible (respects the visible property which can be a boolean or function)
  const isItemVisible = (item: SidebarMenuItem): boolean => {
    if (typeof item.visible === 'function') {
      return item.visible();
    }
    return item.visible !== false; // default to true if not specified
  };

  // Get filtered menu items (only visible ones)
  const getFilteredMenuItems = computed(() => {
    const filterItems = (items: SidebarMenuItem[]): SidebarMenuItem[] => {
      return items
        .filter(item => isItemVisible(item))
        .map(item => ({
          ...item,
          items: item.items ? filterItems(item.items) : undefined
        }));
    };
    
    return filterItems(navigationItems.value);
  });

  // Actions
  function toggleMenu() {
    isMenuCollapsed.value = !isMenuCollapsed.value;
  }

  function setActiveMenuItem(itemId: string) {
    activeMenuItem.value = itemId;
  }

  function setMenuItems(items: SidebarMenuItem[]) {
    navigationItems.value = items;
  }

  function getMenuItemById(id: string): SidebarMenuItem | undefined {
    const findInItems = (items: SidebarMenuItem[]): SidebarMenuItem | undefined => {
      for (const item of items) {
        if (item.id === id) return item;
        if (item.items) {
          const found = findInItems(item.items);
          if (found) return found;
        }
      }
      return undefined;
    };
    return findInItems(navigationItems.value);
  }

  // Check if user has permission to view a menu item
  function hasPermission(item: SidebarMenuItem, userPermissions: string[] = []): boolean {
    if (!item.permission) return true;
    
    const requiredPermissions = Array.isArray(item.permission) 
      ? item.permission 
      : [item.permission];
    
    return requiredPermissions.some(permission => 
      userPermissions.includes(permission)
    );
  }

  // Get menu items filtered by user permissions
  const getAuthorizedMenuItems = computed(() => (userPermissions: string[] = []) => {
    const filterByPermission = (items: SidebarMenuItem[]): SidebarMenuItem[] => {
      return items
        .filter(item => {
          // Check if item is visible and user has permission
          const isVisible = isItemVisible(item);
          const hasPerm = hasPermission(item, userPermissions);
          
          // If item has children, check if any children are visible and authorized
          if (item.items && item.items.length > 0) {
            const hasVisibleChildren = filterByPermission(item.items).length > 0;
            return isVisible && hasPerm && hasVisibleChildren;
          }
          
          return isVisible && hasPerm;
        })
        .map(item => ({
          ...item,
          items: item.items ? filterByPermission(item.items) : undefined
        }));
    };
    
    return filterByPermission(navigationItems.value);
  });

  return {
    // State
    isMenuCollapsed,
    activeMenuItem,
    menuItems: navigationItems,
    
    // Getters
    getActiveMenuItem,
    getIsMenuCollapsed,
    getMenuItems,
    getFilteredMenuItems,
    getAuthorizedMenuItems,
    
    // Actions
    toggleMenu,
    setActiveMenuItem,
    setMenuItems,
    getMenuItemById,
    hasPermission,
  };
});
