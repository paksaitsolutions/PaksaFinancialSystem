<template>
  <div class="app-layout" :class="{ 'dark-theme': isDarkMode }">
    <!-- Top Navigation Bar -->
    <header v-if="!hideTopMenu" class="app-header">
      <div class="header-container">
        <!-- Left Section: Logo and Toggle -->
        <div class="header-left">
          <Button 
            icon="pi pi-bars" 
            text 
            @click="toggleSidebar" 
            class="sidebar-toggle"
            aria-label="Toggle Sidebar"
          />
          <router-link to="/" class="logo-link">
            <img 
              v-if="!isDarkMode"
              src="@/assets/logo.svg" 
              alt="Paksa Financial System"
              class="logo"
            >
            <img 
              v-else
              src="@/assets/logo.svg" 
              alt="Paksa Financial System"
              class="logo"
            >
          </router-link>
        </div>

        <!-- Center Section: Main Navigation -->
        <nav class="main-nav">
          <ul class="nav-list">
            <li 
              v-for="item in mainNav" 
              :key="item.path" 
              class="nav-item"
            >
              <router-link 
                :to="item.path" 
                class="nav-link"
                :class="{ 'active': route.path.startsWith(item.path) }"
              >
                <i :class="item.icon" class="nav-icon"></i>
                <span class="nav-text">{{ item.label }}</span>
              </router-link>
            </li>
          </ul>
        </nav>

        <!-- Right Section: User Controls -->
        <div class="header-actions">
          <!-- Theme Toggle -->
          <Button 
            :icon="isDarkMode ? 'pi pi-sun' : 'pi pi-moon'"
            text 
            @click="toggleTheme"
            :aria-label="isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'"
            class="theme-toggle"
          />
          
          <!-- User Menu -->
          <Menu :model="userMenuItems" :popup="true" ref="userMenu" />
          <Button 
            icon="pi pi-user" 
            text 
            @click="toggleUserMenu" 
            aria-label="User menu"
            class="user-menu-button"
          />
        </div>
      </div>
    </header>

    <!-- Main Content Area -->
    <main class="app-main">
      <!-- Sidebar Navigation -->
      <Sidebar 
        v-model:visible="sidebarVisible" 
        position="left" 
        :modal="false"
        :dismissable="true"
        :showCloseIcon="false"
        class="app-sidebar"
      >
        <AppMenu :model="menuItems" />
      </Sidebar>

      <!-- Page Content -->
      <div class="content-wrapper">
        <div class="content-container">
          <slot />
        </div>
      </div>
    </main>

    <!-- App Footer -->
    <footer class="app-footer">
      <div class="footer-content">
        <span>&copy; {{ currentYear }} Paksa Financial System. All rights reserved.</span>
        <div class="footer-links">
          <router-link to="/privacy">Privacy Policy</router-link>
          <router-link to="/terms">Terms of Service</router-link>
          <router-link to="/contact">Contact Us</router-link>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
/* Component-specific styles only */
.sidebar-toggle {
  margin-right: 1rem;
}

/* Dark theme variables */
:deep(.dark-theme) {
  --text-color: #ffffff;
  --header-bg: #1e1e1e;
  --sidebar-bg: #2d2d2d;
  --card-bg: #2d2d2d;
  --border-color: #3e3e3e;
}
</style>

<script setup lang="ts">
import { ref, computed, watch, onUnmounted } from 'vue';
import { useRouter, useRoute, type RouteLocationNormalizedLoaded } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useTheme } from '@/composables/useTheme';
import type { MenuItem } from 'primevue/menuitem';
import AppMenu from '@/components/layout/AppMenu.vue';

// Router and route setup
const router = useRouter();
const route: RouteLocationNormalizedLoaded = useRoute();
const authStore = useAuthStore();
const { isDarkMode, toggleTheme } = useTheme();

// Computed properties
const hideTopMenu = computed<boolean>(() => {
  const meta = route.meta as { hideTopMenu?: boolean };
  return meta.hideTopMenu === true;
});

// Types
interface NavItem {
  label: string;
  path: string;
  icon: string;
  children?: NavItem[];
  visible?: boolean;
}

// Component props with default values
defineProps<{
  title?: string;
}>();

// Default title value
const title = 'Paksa Financial System';

// Refs for component state

// Refs
const isSidebarCollapsed = ref(false);
const sidebarVisible = ref(false);
const userMenuVisible = ref(false);
const userMenuButtonRef = ref<HTMLElement | null>(null);
const currentYear = ref(new Date().getFullYear());

// Navigation items
const mainNav: NavItem[] = [
  { label: 'Dashboard', path: '/dashboard', icon: 'pi pi-fw pi-home' },
  { label: 'Reports', path: '/reports', icon: 'pi pi-fw pi-chart-bar' },
  { label: 'Transactions', path: '/transactions', icon: 'pi pi-fw pi-sync' },
  { label: 'Settings', path: '/settings', icon: 'pi pi-fw pi-cog' },
];

const menuItems = ref([
  {
    label: 'Dashboard',
    icon: 'pi pi-fw pi-home',
    path: '/dashboard'
  },
  // Add more menu items here
]);

// User menu items
const userMenuItems: MenuItem[] = [
  {
    label: 'Profile',
    icon: 'pi pi-fw pi-user',
    command: () => router.push('/profile')
  },
  {
    label: 'Settings',
    icon: 'pi pi-fw pi-cog',
    command: () => router.push('/settings')
  },
  { separator: true },
  {
    label: 'Logout',
    icon: 'pi pi-fw pi-sign-out',
    command: () => handleLogout()
  }
];

// Methods
const toggleSidebar = (): void => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value;
};

const toggleUserMenu = (event: Event): void => {
  event.preventDefault();
  event.stopPropagation();
  userMenuVisible.value = !userMenuVisible.value;
};

const handleLogout = async (): Promise<void> => {
  try {
    await authStore.logout();
    router.push('/login');
  } catch (error) {
    console.error('Logout failed:', error);
  }
};

// Click outside handler for user menu
const handleClickOutside = (event: MouseEvent): void => {
  if (userMenuButtonRef.value && !userMenuButtonRef.value.contains(event.target as Node)) {
    userMenuVisible.value = false;
  }
};

// Watch for menu visibility changes
watch(userMenuVisible, (isVisible: boolean) => {
  if (isVisible) {
    document.addEventListener('click', handleClickOutside);
  } else {
    document.removeEventListener('click', handleClickOutside);
  }
});

// Cleanup
onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});
</script>