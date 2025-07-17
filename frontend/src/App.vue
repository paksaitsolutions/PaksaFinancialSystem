<template>
  <v-app>
    <v-layout>
      <!-- App Bar (only shown when authenticated) -->
      <v-app-bar v-if="isAuthenticated" color="primary" app>
        <v-app-bar-nav-icon @click="toggleSidebar"></v-app-bar-nav-icon>
        
        <v-app-bar-title>
          <router-link to="/" class="text-decoration-none text-white">
            Paksa Financial System
          </router-link>
        </v-app-bar-title>
        
        <v-spacer></v-spacer>
        
        <v-btn icon>
          <v-icon>mdi-magnify</v-icon>
        </v-btn>
        
        <v-btn icon>
          <v-badge dot color="error">
            <v-icon>mdi-bell</v-icon>
          </v-badge>
        </v-btn>
        
        <v-menu>
          <template v-slot:activator="{ props }">
            <v-btn v-bind="props">
              <v-avatar size="32" class="mr-2">
                <v-img src="https://randomuser.me/api/portraits/men/85.jpg" alt="User"></v-img>
              </v-avatar>
              {{ userName || 'User' }}
            </v-btn>
          </template>
          <v-list>
            <v-list-item to="/profile">
              <v-list-item-title>Profile</v-list-item-title>
            </v-list-item>
            <v-list-item to="/settings">
              <v-list-item-title>Settings</v-list-item-title>
            </v-list-item>
            <v-divider></v-divider>
            <v-list-item @click="logout">
              <v-list-item-title>Logout</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>
      </v-app-bar>

      <!-- Navigation Drawer (only shown when authenticated) -->
      <v-navigation-drawer
        v-if="isAuthenticated"
        v-model="drawer"
        app
      >
        <v-list>
          <v-list-item
            prepend-avatar="/src/assets/logo.svg"
            title="Paksa Financial"
            subtitle="Enterprise System"
          ></v-list-item>
        </v-list>

        <v-divider></v-divider>

        <v-list density="compact" nav>
          <v-list-item to="/" prepend-icon="mdi-view-dashboard" title="Dashboard"></v-list-item>
          
          <v-list-group value="gl">
            <template v-slot:activator="{ props }">
              <v-list-item v-bind="props" prepend-icon="mdi-book-open-page-variant" title="General Ledger"></v-list-item>
            </template>
            <v-list-item to="/gl/accounts" title="Chart of Accounts"></v-list-item>
            <v-list-item to="/gl/journal-entries" title="Journal Entries"></v-list-item>
            <v-list-item to="/gl/trial-balance" title="Trial Balance"></v-list-item>
          </v-list-group>
          
          <v-list-group>
            <template v-slot:activator="{ props }">
              <v-list-item v-bind="props" prepend-icon="mdi-file-document-outline" title="Accounts Payable"></v-list-item>
            </template>
            <v-list-item to="/ap/vendors" title="Vendors"></v-list-item>
            <v-list-item to="/ap/invoices" title="Invoices"></v-list-item>
            <v-list-item to="/ap/payments" title="Payments"></v-list-item>
          </v-list-group>
          
          <v-list-group>
            <template v-slot:activator="{ props }">
              <v-list-item v-bind="props" prepend-icon="mdi-cash-multiple" title="Accounts Receivable"></v-list-item>
            </template>
            <v-list-item to="/ar/customers" title="Customers"></v-list-item>
            <v-list-item to="/ar/invoices" title="Invoices"></v-list-item>
            <v-list-item to="/ar/payments" title="Payments"></v-list-item>
          </v-list-group>
          
          <v-list-group>
            <template v-slot:activator="{ props }">
              <v-list-item v-bind="props" prepend-icon="mdi-bank" title="Cash Management"></v-list-item>
            </template>
            <v-list-item to="/cash/accounts" title="Bank Accounts"></v-list-item>
            <v-list-item to="/cash/reconciliation" title="Reconciliation"></v-list-item>
            <v-list-item to="/cash/forecast" title="Cash Forecast"></v-list-item>
          </v-list-group>
          
          <v-list-group>
            <template v-slot:activator="{ props }">
              <v-list-item v-bind="props" prepend-icon="mdi-account-cash" title="Payroll"></v-list-item>
            </template>
            <v-list-item to="/payroll/employees" title="Employees"></v-list-item>
            <v-list-item to="/payroll/process" title="Process Payroll"></v-list-item>
            <v-list-item to="/payroll/reports" title="Reports"></v-list-item>
          </v-list-group>
          
          <v-list-group>
            <template v-slot:activator="{ props }">
              <v-list-item v-bind="props" prepend-icon="mdi-calculator-variant" title="Tax"></v-list-item>
            </template>
            <v-list-item to="/tax/exemption-certificate" title="Exemption Certificates"></v-list-item>
            <v-list-item to="/tax/policy" title="Tax Policy"></v-list-item>
          </v-list-group>
        </v-list>
      </v-navigation-drawer>

      <!-- Main Content -->
      <v-main>
        <v-container fluid :class="{ 'pa-0': !isAuthenticated }">
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </v-container>
      </v-main>
    </v-layout>
    
    <!-- Global Loading Overlay -->
    <loading-overlay :loading="globalLoading" message="Loading application..."></loading-overlay>
    
    <!-- Global Snackbar -->
    <global-snackbar
      v-model="snackbar.visible"
      :text="snackbar.text"
      :color="snackbar.color"
      :timeout="snackbar.timeout"
      :location="snackbar.location"
    ></global-snackbar>
  </v-app>
</template>

<script setup>
import { ref, computed, onMounted, provide } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useSnackbar } from '@/composables/useSnackbar';
import LoadingOverlay from '@/components/ui/LoadingOverlay.vue';
import GlobalSnackbar from '@/components/ui/GlobalSnackbar.vue';

const router = useRouter();
const authStore = useAuthStore();
const drawer = ref(true);
const globalLoading = ref(true);

// Setup snackbar
const snackbar = useSnackbar();
// Provide snackbar to all components
provide('snackbar', snackbar);

// Check if user is authenticated
const isAuthenticated = computed(() => authStore.isAuthenticated);
const userName = computed(() => authStore.userName);

// Toggle sidebar
const toggleSidebar = () => {
  drawer.value = !drawer.value;
};

// Logout function
const logout = async () => {
  await authStore.logout();
  router.push('/auth/login');
};

// Check authentication status on app load
onMounted(async () => {
  try {
    await authStore.checkAuth();
  } catch (error) {
    console.error('Auth check failed:', error);
  } finally {
    globalLoading.value = false;
  }
});
</script>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>