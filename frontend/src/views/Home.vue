<template>
  <v-container class="home-page" fluid>
    <!-- Hero Section -->
    <v-sheet
      rounded
      class="pa-8 mb-8 text-center"
      :color="$vuetify.theme.current.dark ? 'grey-darken-4' : 'primary-lighten-5'"
      elevation="1"
    >
      <v-container class="py-12">
        <v-row justify="center">
          <v-col cols="12" md="8">
            <h1 class="text-h3 font-weight-bold mb-4">
              Welcome to Paksa Financial System
            </h1>
            <p class="text-h6 font-weight-regular text-medium-emphasis mb-8">
              Comprehensive financial management for your business
            </p>
            
            <v-fade-transition>
              <v-alert
                v-if="showWelcome && !authStore.isAuthenticated"
                color="primary"
                icon="mdi-information"
                variant="tonal"
                closable
                class="mb-6 mx-auto"
                max-width="600"
                @click:close="showWelcome = false"
              >
                Sign in to access all features or explore the available modules below.
              </v-alert>
            </v-fade-transition>
            
            <div class="d-flex justify-center gap-4 mt-6">
              <v-btn
                v-if="!authStore.isAuthenticated"
                color="primary"
                size="large"
                to="/login"
                prepend-icon="mdi-login"
              >
                Sign In
              </v-btn>
              
              <v-btn
                v-else
                color="primary"
                variant="tonal"
                size="large"
                to="/dashboard"
                prepend-icon="mdi-view-dashboard"
              >
                Go to Dashboard
              </v-btn>
              
              <v-btn
                variant="outlined"
                size="large"
                href="https://paksa.com.pk"
                target="_blank"
                rel="noopener noreferrer"
                prepend-icon="mdi-information"
              >
                Learn More
              </v-btn>
            </div>
          </v-col>
        </v-row>
      </v-container>
    </v-sheet>

    <!-- Modules Grid -->
    <v-container>
      <v-row class="mb-6">
        <v-col cols="12">
          <div class="d-flex align-center justify-space-between mb-4">
            <h2 class="text-h5 font-weight-bold">
              {{ authStore.isAuthenticated ? 'Available Modules' : 'Explore Modules' }}
            </h2>
            <v-btn
              v-if="authStore.isAuthenticated"
              color="primary"
              variant="text"
              prepend-icon="mdi-refresh"
              :loading="menuStore.isLoading"
              @click="refreshData"
            >
              Refresh
            </v-btn>
          </div>
          
          <v-alert
            v-if="menuStore.error"
            type="error"
            variant="tonal"
            class="mb-6"
          >
            {{ menuStore.error }}
          </v-alert>
          
          <v-progress-linear
            v-if="menuStore.isLoading"
            indeterminate
            color="primary"
            class="mb-6"
          ></v-progress-linear>
          
          <v-row v-else-if="filteredModules.length > 0">
            <v-col
              v-for="module in filteredModules"
              :key="module.id"
              cols="12"
              sm="6"
              md="4"
              lg="3"
            >
              <module-card :module="module" />
            </v-col>
          </v-row>
          
          <v-alert
            v-else
            type="info"
            variant="tonal"
            class="mt-4"
          >
            No modules available. Please contact your administrator for access.
          </v-alert>
        </v-col>
      </v-row>
      
      <!-- Quick Actions -->
      <v-row v-if="authStore.isAuthenticated && quickActions.length > 0" class="mt-8">
        <v-col cols="12">
          <h2 class="text-h5 font-weight-bold mb-4">Quick Actions</h2>
          <div class="d-flex flex-wrap gap-2">
            <v-btn
              v-for="action in quickActions"
              :key="action.title"
              :prepend-icon="action.icon"
              :to="action.to"
              variant="tonal"
              size="large"
              class="text-none"
              rounded="lg"
            >
              {{ action.title }}
            </v-btn>
          </div>
        </v-col>
      </v-row>
    </v-container>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useMenuStore } from '@/store/menu';
import { useAuthStore } from '@/modules/auth/store';
import ModuleCard from '@/components/home/ModuleCard.vue';
import { useDisplay } from 'vuetify';

// Initialize stores and utilities
const menuStore = useMenuStore();
const authStore = useAuthStore();
const router = useRouter();
const route = useRoute();
const { mobile } = useDisplay();

// State
const showWelcome = ref(true);

// Computed properties
const filteredModules = computed(() => {
  // Filter modules based on authentication status
  return menuStore.visibleModules.filter(module => {
    // Show all modules to authenticated users
    if (authStore.isAuthenticated) return true;
    // Only show public modules to unauthenticated users
    return module.isPublic === true;
  });
});

// Quick actions for authenticated users
const quickActions = computed(() => {
  if (!authStore.isAuthenticated) return [];
  
  return [
    { title: 'New Invoice', icon: 'mdi-file-document-plus', to: '/invoices/new' },
    { title: 'Record Payment', icon: 'mdi-cash-plus', to: '/payments/new' },
    { title: 'Add Expense', icon: 'mdi-cash-minus', to: '/expenses/new' },
    { title: 'Run Payroll', icon: 'mdi-account-cash', to: '/payroll/process' },
  ];
});

// Methods
const refreshData = async () => {
  try {
    await menuStore.fetchMenuItems();
  } catch (error) {
    console.error('Failed to refresh menu items:', error);
    throw error;
  }
};

// Lifecycle hooks
onMounted(async () => {
  // Load menu items
  if (menuStore.visibleModules.length === 0) {
    await refreshData();
  }
  
  // Show welcome message if it's the first visit
  const hasSeenWelcome = localStorage.getItem('hasSeenWelcome');
  showWelcome.value = !hasSeenWelcome;
  if (!hasSeenWelcome) {
    localStorage.setItem('hasSeenWelcome', 'true');
  }
});

// Watch for authentication changes
watch(() => authStore.isAuthenticated, async (isAuthenticated) => {
  if (isAuthenticated) {
    // Refresh menu items when user logs in
    await refreshData();
  }
});

// Watch for route changes to handle deep links
watch(() => route.path, (newPath) => {
  // If user is redirected to home from a protected route, show login prompt
  if (newPath === '/' && route.query.redirect) {
    showWelcome.value = true;
  }
}, { immediate: true });
</script>

<style scoped>
.home-page {
  padding: 0;
  min-height: calc(100vh - 64px);
  background-color: rgb(var(--v-theme-background));
  transition: background-color 0.3s ease;
}

/* Smooth transitions for theme changes */
:deep(.v-card) {
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

/* Responsive adjustments */
@media (max-width: 600px) {
  .home-page {
    padding-bottom: 80px; /* Add space for mobile nav */
  }
  
  :deep(.v-container) {
    padding: 12px;
  }
}

/* Print styles */
@media print {
  .home-page {
    padding: 0;
    background: white;
  }
  
  .no-print {
    display: none !important;
  }
}

/* Dark mode adjustments */
:global(.v-theme--dark) .home-page {
  background-color: #121212;
}

/* Accessibility focus styles */
:deep(a:focus-visible),
:deep(button:focus-visible) {
  outline: 2px solid var(--v-primary-base);
  outline-offset: 2px;
}

/* Animation for module cards */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

:deep(.module-card) {
  animation: fadeInUp 0.4s ease-out forwards;
  opacity: 0;
}

/* Delay animations for each card */
:deep(.v-col) {
  @for $i from 1 through 12 {
    &:nth-child(#{$i}) .module-card {
      animation-delay: #{$i * 0.05}s;
    }
  }
}

/* Better spacing for mobile */
.v-col {
  padding: 8px !important;
}

/* Responsive typography */
h1 {
  font-size: 2.5rem;
  line-height: 1.2;
}

@media (max-width: 960px) {
  h1 {
    font-size: 2rem;
  }
}

@media (max-width: 600px) {
  h1 {
    font-size: 1.75rem;
  }
  
  .v-btn {
    font-size: 0.875rem;
    padding: 0 16px;
  }
}
</style>