<template>
  <v-app>
    <app-navigation v-if="isAuthenticated" />
    
    <v-app-bar v-if="isAuthenticated" color="primary" :elevation="1">
      <v-app-bar-nav-icon @click="$emit('toggle-drawer')"></v-app-bar-nav-icon>
      <v-toolbar-title class="text-h6 font-weight-medium">Paksa Financial System</v-toolbar-title>
      
      <v-spacer></v-spacer>
      
      <v-btn icon class="mr-2">
        <v-badge color="error" content="3" dot>
          <v-icon>mdi-bell-outline</v-icon>
        </v-badge>
      </v-btn>
      
      <v-menu>
        <template v-slot:activator="{ props }">
          <v-btn
            variant="text"
            v-bind="props"
            class="text-none"
          >
            <v-avatar size="32" class="mr-2">
              <v-img
                src="https://randomuser.me/api/portraits/men/32.jpg"
                alt="User"
              ></v-img>
            </v-avatar>
            <span class="d-none d-sm-flex">Admin User</span>
            <v-icon end>mdi-chevron-down</v-icon>
          </v-btn>
        </template>
        
        <v-list>
          <v-list-item
            v-for="(item, index) in userMenu"
            :key="index"
            :prepend-icon="item.icon"
            :title="item.title"
            :to="item.to"
            @click="handleUserMenuClick(item.action)"
          ></v-list-item>
        </v-list>
      </v-menu>
    </v-app-bar>
    
    <v-main :class="{ 'ml-0': !isAuthenticated, 'ml-0': !isAuthenticated && $vuetify.display.mobile }">
      <v-container fluid class="fill-height pa-0" :class="{ 'px-4 py-2': isAuthenticated }">
        <!-- Loading state -->
        <v-fade-transition mode="out-in">
          <v-row v-if="isLoading" key="loading" class="fill-height" align="center" justify="center">
            <v-col cols="12" class="text-center">
              <v-progress-circular
                indeterminate
                color="primary"
                :size="64"
                :width="6"
              ></v-progress-circular>
              <div class="text-subtitle-1 mt-4">Loading application...</div>
            </v-col>
          </v-row>
        </v-fade-transition>
        
        <!-- Router view with transition -->
        <router-view v-slot="{ Component, route }">
          <transition name="fade" mode="out-in">
            <component :is="Component" :key="route.path" />
          </transition>
        </router-view>
      </v-container>
    </v-main>
    
    <v-footer app inset color="background" class="justify-end px-4">
      <div class="text-caption text-medium-emphasis">
        &copy; {{ new Date().getFullYear() }} Paksa IT Solutions. All rights reserved.
      </div>
    </v-footer>
    
    <app-snackbar />
    
    <v-fab
      v-if="!isLoading && isAuthenticated"
      v-model="fab"
      location="bottom end"
      :position="'fixed'"
      :style="fabPosition"
      color="primary"
      icon="mdi-plus"
      size="large"
    >
      <v-menu activator="parent" location="top">
        <v-list>
          <v-list-item
            v-for="(item, index) in quickActions"
            :key="index"
            :prepend-icon="item.icon"
            :title="item.title"
            :to="item.to"
            link
          ></v-list-item>
        </v-list>
      </v-menu>
    </v-fab>
  </v-app>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/modules/auth/store';
import { useDisplay } from 'vuetify';
import AppSnackbar from '@/components/AppSnackbar.vue';
import AppNavigation from '@/components/AppNavigation.vue';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const display = useDisplay();

const isAuthenticated = ref(false);
const isLoading = ref(true);
const fab = ref(false);

// User menu items
const userMenu = [
  { title: 'Profile', icon: 'mdi-account-outline', to: '/profile' },
  { title: 'Settings', icon: 'mdi-cog-outline', to: '/settings' },
  { title: 'Logout', icon: 'mdi-logout', action: 'logout' },
];

// Quick action items
const quickActions = [
  { title: 'New Invoice', icon: 'mdi-file-document-outline', to: '/ar/invoices/new' },
  { title: 'New Bill', icon: 'mdi-receipt', to: '/ap/bills/new' },
  { title: 'New Journal Entry', icon: 'mdi-book-open-variant', to: '/gl/journal-entries/new' },
  { title: 'New Payment', icon: 'mdi-cash-multiple', to: '/ap/payments/new' },
];

// Calculate FAB position based on navigation drawer state
const fabPosition = computed(() => {
  const offset = display.mobile ? 16 : 24;
  return { bottom: `${offset}px`, right: `${offset}px` };
});

// Initialize auth state and handle routing
const initializeAuth = async () => {
  try {
    await authStore.initialize();
    isAuthenticated.value = authStore.isAuthenticated;
    
    const publicPages = ['/login', '/forgot-password', '/reset-password'];
    const isPublicPage = publicPages.some(page => route.path.startsWith(page));
    
    if (!isAuthenticated.value && !isPublicPage) {
      // Redirect to login if not authenticated and not on a public page
      const redirect = route.fullPath !== '/' ? { redirect: route.fullPath } : {};
      await router.push({ name: 'login', query: redirect });
    } else if (isAuthenticated.value && isPublicPage) {
      // Redirect to dashboard if authenticated and on a public page
      await router.push('/dashboard');
    }
  } catch (error) {
    console.error('Error initializing auth:', error);
  } finally {
    isLoading.value = false;
  }
};

// Handle user menu actions
const handleUserMenuClick = async (action: string) => {
  if (action === 'logout') {
    try {
      await authStore.logout();
      isAuthenticated.value = false;
      router.push({ name: 'login' });
    } catch (error) {
      console.error('Error during logout:', error);
    }
  }
};

// Watch for auth state changes
const unsubscribe = authStore.$onAction(({ name, after }) => {
  if (name === 'setAuth' || name === 'clearAuth') {
    after(() => {
      isAuthenticated.value = authStore.isAuthenticated;
    });
  }
});

// Initialize on mount
onMounted(() => {
  initializeAuth();
});

// Cleanup on unmount
onUnmounted(() => {
  unsubscribe();
});

// Watch route changes to handle auth redirects
router.beforeEach((to, from, next) => {
  // If route requires auth and user is not authenticated, redirect to login
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } });
  } else {
    next();
  }
});

// Initialize on mount
onMounted(initializeAuth);

// Clean up on unmount
onUnmounted(() => {
  unsubscribe();
});
</script>

<style scoped>
/* Main layout adjustments */
.v-main {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  min-height: 100vh;
  background-color: #f5f7fa;
}

/* FAB button styling */
.v-btn--floating {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.2s ease-in-out;
}

.v-btn--floating:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

/* Page transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>

<style>
/* Global styles */
:root {
  --v-theme-primary: #1976D2;
  --v-theme-secondary: #424242;
  --v-theme-accent: #82B1FF;
  --v-theme-error: #FF5252;
  --v-theme-info: #2196F3;
  --v-theme-success: #4CAF50;
  --v-theme-warning: #FFC107;
  --v-theme-background: #f5f7fa;
  --v-theme-surface: #ffffff;
  --v-theme-on-primary: #ffffff;
  --v-theme-on-secondary: #ffffff;
  --v-theme-on-surface: #212121;
  --v-theme-on-background: #212121;
  --v-border-radius: 8px;
  --v-elevation-1: 0 2px 4px -1px rgba(0, 0, 0, 0.1), 0 4px 5px 0 rgba(0, 0, 0, 0.07), 0 1px 10px 0 rgba(0, 0, 0, 0.06);
  --v-elevation-2: 0 3px 5px -1px rgba(0, 0, 0, 0.1), 0 5px 8px 0 rgba(0, 0, 0, 0.07), 0 1px 14px 0 rgba(0, 0, 0, 0.06);
  --v-elevation-3: 0 6px 10px 0 rgba(0, 0, 0, 0.1), 0 1px 18px 0 rgba(0, 0, 0, 0.06), 0 3px 5px -1px rgba(0, 0, 0, 0.1);
}

/* Base HTML elements */
body {
  font-family: 'Roboto', sans-serif;
  line-height: 1.5;
  color: rgba(0, 0, 0, 0.87);
  background-color: #f5f7fa;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Typography */
h1, h2, h3, h4, h5, h6 {
  font-weight: 500;
  line-height: 1.2;
  margin-bottom: 0.75rem;
  color: rgba(0, 0, 0, 0.87);
}

/* Links */
a {
  color: var(--v-theme-primary);
  text-decoration: none;
  transition: color 0.2s ease;
}

a:hover {
  color: var(--v-theme-accent);
  text-decoration: underline;
}

/* Buttons */
.v-btn {
  text-transform: none;
  letter-spacing: normal;
  font-weight: 500;
  border-radius: var(--v-border-radius);
}

.v-btn--size-default {
  min-height: 42px;
  padding: 0 16px;
}

/* Cards */
.v-card {
  border-radius: var(--v-border-radius);
  box-shadow: var(--v-elevation-1);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.v-card:hover {
  box-shadow: var(--v-elevation-3);
  transform: translateY(-2px);
}

/* Forms */
.v-field {
  border-radius: var(--v-border-radius);
}

.v-field--variant-outlined {
  --v-field-border-opacity: 0.2;
}

.v-field--focused {
  --v-field-border-opacity: 0.8;
}

/* Tables */
.v-table {
  border-radius: var(--v-border-radius);
  overflow: hidden;
  box-shadow: var(--v-elevation-1);
  background-color: var(--v-theme-surface);
}

.v-table thead th {
  background-color: var(--v-theme-background);
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.05em;
  color: rgba(0, 0, 0, 0.6);
}

.v-table tbody tr:hover {
  background-color: rgba(0, 0, 0, 0.02);
}

/* Dialogs */
.v-dialog > .v-card {
  border-radius: 12px;
  overflow: hidden;
}

/* Tooltips */
.v-tooltip__content {
  font-size: 0.75rem;
  padding: 6px 12px;
  background-color: #424242;
  color: white;
  border-radius: 4px;
  font-weight: 500;
  letter-spacing: 0.02em;
  pointer-events: none;
}

/* Alerts */
.v-alert {
  border-radius: var(--v-border-radius);
}

/* Badges */
.v-badge__badge {
  font-size: 10px;
  height: 18px;
  min-width: 18px;
  padding: 0 4px;
}

/* Tabs */
.v-tabs {
  border-radius: var(--v-border-radius) var(--v-border-radius) 0 0;
  overflow: hidden;
}

/* Lists */
.v-list {
  border-radius: var(--v-border-radius);
  overflow: hidden;
}

/* Data tables */
.v-data-table {
  border-radius: var(--v-border-radius);
  overflow: hidden;
  box-shadow: var(--v-elevation-1);
}

/* Chips */
.v-chip {
  border-radius: 16px;
  font-weight: 500;
}

/* Progress */
.v-progress-linear {
  border-radius: 4px;
  overflow: hidden;
}

/* Override Vuetify transitions */
.v-enter-active,
.v-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.v-enter-from,
.v-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

/* Print styles */
@media print {
  .no-print,
  .v-navigation-drawer,
  .v-app-bar,
  .v-footer,
  .v-fab {
    display: none !important;
  }
  
  .v-main {
    padding: 0 !important;
    margin: 0 !important;
  }
  
  .v-container {
    max-width: 100% !important;
    padding: 0 !important;
  }
  
  @page {
    margin: 1cm;
  }
}
</style>