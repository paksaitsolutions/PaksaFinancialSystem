<template>
  <v-navigation-drawer
    v-model="drawer"
    :rail="!isExpanded"
    permanent
    class="modern-sidebar"
    color="surface"
    width="280"
    rail-width="72"
  >
    <!-- Logo Section -->
    <div class="logo-section">
      <div class="d-flex align-center pa-4">
        <div class="logo-container" @click="goToHome">
          <v-avatar size="48" class="logo-avatar">
            <v-img src="/logo.png" alt="Paksa Financial" />
          </v-avatar>
        </div>
        <v-fade-transition>
          <div v-if="isExpanded" class="logo-text ml-3">
            <h2 class="brand-title">Paksa</h2>
            <p class="brand-subtitle">Financial System</p>
          </div>
        </v-fade-transition>
        <v-spacer />
        <v-btn
          :icon="isExpanded ? 'mdi-menu-open' : 'mdi-menu'"
          variant="text"
          size="small"
          class="toggle-btn"
          @click="toggleMenu"
        />
      </div>
    </div>

    <!-- Unified Navigation -->
    <div class="navigation-section">
      <v-list nav class="unified-nav">
        <!-- Dashboard -->
        <v-list-item
          prepend-icon="mdi-view-dashboard-variant"
          title="Dashboard"
          to="/dashboard"
          class="nav-item"
          rounded="xl"
          @click="navigateToDashboard"
        />

        <!-- General Ledger -->
        <v-list-group value="gl" class="nav-group">
          <template #activator="{ props }">
            <v-list-item
              v-bind="props"
              prepend-icon="mdi-calculator-variant"
              title="General Ledger"
              class="nav-item group-activator"
              rounded="xl"
            />
          </template>
          
          <v-list-item
            prepend-icon="mdi-file-tree-outline"
            title="Chart of Accounts"
            to="/gl/chart-of-accounts"
            class="nav-subitem"
          />
          <v-list-item
            prepend-icon="mdi-book-edit-outline"
            title="Journal Entries"
            to="/gl/journal-entries"
            class="nav-subitem"
          />
          <v-list-item
            prepend-icon="mdi-scale-balance"
            title="Trial Balance"
            to="/gl/trial-balance"
            class="nav-subitem"
          />
          <v-list-item
            prepend-icon="mdi-file-document"
            title="Financial Statements"
            to="/gl/financial-statements"
            class="nav-subitem"
          />
        </v-list-group>

        <!-- Accounts Payable -->
        <v-list-item
          prepend-icon="mdi-credit-card"
          title="Accounts Payable"
          to="/ap"
          class="nav-item"
          rounded="xl"
        />

        <!-- Accounts Receivable -->
        <v-list-item
          prepend-icon="mdi-wallet"
          title="Accounts Receivable"
          to="/ar"
          class="nav-item"
          rounded="xl"
        />

        <!-- Cash Management -->
        <v-list-item
          prepend-icon="mdi-bank"
          title="Cash Management"
          to="/cash"
          class="nav-item"
          rounded="xl"
        />

        <!-- Fixed Assets -->
        <v-list-item
          prepend-icon="mdi-office-building"
          title="Fixed Assets"
          to="/assets"
          class="nav-item"
          rounded="xl"
        />

        <!-- Payroll -->
        <v-list-item
          prepend-icon="mdi-account-cash"
          title="Payroll"
          to="/payroll"
          class="nav-item"
          rounded="xl"
        />

        <!-- HRM -->
        <v-list-item
          prepend-icon="mdi-account-group-outline"
          title="Human Resources"
          to="/hrm"
          class="nav-item"
          rounded="xl"
        />

        <!-- Budget -->
        <v-list-item
          prepend-icon="mdi-chart-pie"
          title="Budget"
          to="/budget"
          class="nav-item"
          rounded="xl"
        />

        <!-- Inventory -->
        <v-list-item
          prepend-icon="mdi-package-variant-closed"
          title="Inventory"
          to="/inventory"
          class="nav-item"
          rounded="xl"
        />

        <!-- Reports -->
        <v-list-item
          prepend-icon="mdi-chart-line"
          title="Reports"
          to="/reports"
          class="nav-item"
          rounded="xl"
        />

        <!-- Admin -->
        <v-list-item
          prepend-icon="mdi-shield-account"
          title="Admin"
          to="/admin"
          class="nav-item"
          rounded="xl"
        />

        <!-- RBAC -->
        <v-list-item
          prepend-icon="mdi-account-key"
          title="Role Management"
          to="/rbac"
          class="nav-item"
          rounded="xl"
        />

        <v-divider class="nav-divider" />

        <!-- Settings -->
        <v-list-item
          prepend-icon="mdi-cog-outline"
          title="Settings"
          to="/settings"
          class="nav-item"
          rounded="xl"
        />
        
        <v-list-item
          prepend-icon="mdi-logout-variant"
          title="Logout"
          @click="logout"
          class="nav-item logout-item"
          rounded="xl"
        />
      </v-list>
    </div>
  </v-navigation-drawer>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const drawer = ref(true)
const isExpanded = ref(true)

const toggleMenu = () => {
  isExpanded.value = !isExpanded.value
}

const goToHome = () => {
  router.push('/dashboard')
}

const navigateToDashboard = () => {
  router.push('/dashboard')
}

const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  router.push('/auth/login')
}
</script>

<style scoped>
/* Modern Sidebar Styling */
.modern-sidebar {
  background: linear-gradient(180deg, rgb(var(--v-theme-surface)) 0%, rgba(var(--v-theme-surface), 0.98) 100%);
  backdrop-filter: blur(10px);
  border-right: 1px solid rgba(var(--v-theme-outline), 0.12);
}

/* Logo Section */
.logo-section {
  background: rgba(var(--v-theme-primary), 0.02);
  border-bottom: 1px solid rgba(var(--v-theme-outline), 0.08);
}

.logo-container {
  cursor: pointer;
  transition: transform 0.2s ease;
}

.logo-container:hover {
  transform: scale(1.05);
}

.logo-avatar {
  background: linear-gradient(135deg, rgb(var(--v-theme-primary)), rgb(var(--v-theme-secondary)));
  box-shadow: 0 4px 12px rgba(var(--v-theme-primary), 0.3);
}

.brand-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: rgb(var(--v-theme-primary));
  margin: 0;
  line-height: 1.2;
}

.brand-subtitle {
  font-size: 0.75rem;
  color: rgba(var(--v-theme-on-surface), 0.6);
  margin: 0;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.toggle-btn {
  opacity: 0.7;
  transition: opacity 0.2s ease;
}

.toggle-btn:hover {
  opacity: 1;
}

/* Navigation Section */
.navigation-section {
  flex: 1;
  overflow-y: auto;
  padding: 16px 0;
}

.unified-nav {
  padding: 0 16px;
}

.nav-divider {
  margin: 16px 0;
  opacity: 0.3;
}

/* Navigation Items */
.nav-item {
  margin-bottom: 4px;
  transition: all 0.2s ease;
  border-radius: 12px !important;
}

.nav-item:hover {
  background-color: rgba(var(--v-theme-primary), 0.08) !important;
  transform: translateX(4px);
}

.nav-subitem {
  margin-left: 32px;
  margin-bottom: 2px;
  border-radius: 8px !important;
  opacity: 0.9;
}

.nav-subitem:hover {
  background-color: rgba(var(--v-theme-primary), 0.06) !important;
  transform: translateX(2px);
}

/* Group Styling */
.nav-group {
  margin-bottom: 4px;
}

.group-activator {
  font-weight: 500;
}

/* Logout Item Special Styling */
.logout-item:hover {
  background-color: rgba(var(--v-theme-error), 0.08) !important;
  color: rgb(var(--v-theme-error));
}

.logout-item:hover {
  background-color: rgba(var(--v-theme-error), 0.08) !important;
  color: rgb(var(--v-theme-error));
}

/* Active States */
:deep(.v-list-item--active) {
  background: linear-gradient(90deg, rgba(var(--v-theme-primary), 0.15), rgba(var(--v-theme-primary), 0.08)) !important;
  color: rgb(var(--v-theme-primary));
  font-weight: 600;
  border-left: 3px solid rgb(var(--v-theme-primary));
}

:deep(.v-list-item--active .v-list-item__prepend .v-icon) {
  color: rgb(var(--v-theme-primary));
  transform: scale(1.1);
}

/* Rail Mode */
:deep(.v-navigation-drawer--rail) {
  .nav-item {
    justify-content: center;
  }
  
  .nav-subitem {
    margin-left: 0;
  }
}

/* Scrollbar Styling */
.navigation-section::-webkit-scrollbar {
  width: 4px;
}

.navigation-section::-webkit-scrollbar-track {
  background: transparent;
}

.navigation-section::-webkit-scrollbar-thumb {
  background: rgba(var(--v-theme-on-surface), 0.2);
  border-radius: 2px;
}

.navigation-section::-webkit-scrollbar-thumb:hover {
  background: rgba(var(--v-theme-on-surface), 0.3);
}

/* Animations */
.v-fade-transition-enter-active,
.v-fade-transition-leave-active {
  transition: opacity 0.3s ease;
}

.v-fade-transition-enter-from,
.v-fade-transition-leave-to {
  opacity: 0;
}
</style>