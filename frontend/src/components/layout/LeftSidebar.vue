<template>
  <v-navigation-drawer
    v-model="drawer"
    :rail="!isExpanded"
    permanent
    class="left-sidebar"
    elevation="2"
    width="280"
    rail-width="72"
  >
    <!-- Header -->
    <div class="sidebar-header">
      <div class="d-flex align-center px-4 py-3">
        <v-avatar size="40" color="primary" class="mr-3 cursor-pointer" @click="goToHome">
          <v-icon color="white">mdi-currency-usd</v-icon>
        </v-avatar>
        <div v-if="isExpanded" class="flex-grow-1 cursor-pointer" @click="goToHome">
          <div class="text-h6 font-weight-bold text-primary">Paksa Financial</div>
          <div class="text-caption text-medium-emphasis">Enterprise System</div>
        </div>
        <v-btn
          :icon="isExpanded ? 'mdi-chevron-left' : 'mdi-chevron-right'"
          variant="text"
          size="small"
          @click="toggleMenu"
        />
      </div>
    </div>

    <v-divider />

    <!-- Navigation Menu -->
    <div class="sidebar-scroll">
      <v-list nav class="pa-2">
        <!-- Dashboard -->
        <v-list-item
          prepend-icon="mdi-view-dashboard"
          title="Dashboard"
          to="/dashboard"
          rounded="lg"
          class="mb-1"
        />

        <!-- General Ledger -->
        <v-list-group value="gl">
          <template #activator="{ props }">
            <v-list-item
              v-bind="props"
              prepend-icon="mdi-book-open-variant"
              title="General Ledger"
              rounded="lg"
              class="mb-1"
            />
          </template>
          
          <v-list-item
            prepend-icon="mdi-file-tree"
            title="Chart of Accounts"
            to="/gl/chart-of-accounts"
            rounded="lg"
            class="ml-4 mb-1"
          />
          <v-list-item
            prepend-icon="mdi-book-edit"
            title="Journal Entries"
            to="/gl/journal-entries"
            rounded="lg"
            class="ml-4 mb-1"
          />
          <v-list-item
            prepend-icon="mdi-scale-balance"
            title="Trial Balance"
            to="/gl/trial-balance"
            rounded="lg"
            class="ml-4 mb-1"
          />
          <v-list-item
            prepend-icon="mdi-file-document"
            title="Financial Statements"
            to="/gl/financial-statements"
            rounded="lg"
            class="ml-4 mb-1"
          />
        </v-list-group>

        <!-- Accounts Payable -->
        <v-list-group value="ap">
          <template #activator="{ props }">
            <v-list-item
              v-bind="props"
              prepend-icon="mdi-credit-card"
              title="Accounts Payable"
              rounded="lg"
              class="mb-1"
            />
          </template>
          
          <v-list-item
            prepend-icon="mdi-account-group"
            title="Vendors"
            to="/ap/vendors"
            rounded="lg"
            class="ml-4 mb-1"
          />
          <v-list-item
            prepend-icon="mdi-file-document-outline"
            title="Bills"
            to="/ap/bills"
            rounded="lg"
            class="ml-4 mb-1"
          />
          <v-list-item
            prepend-icon="mdi-cash"
            title="Payments"
            to="/ap/payments"
            rounded="lg"
            class="ml-4 mb-1"
          />
        </v-list-group>

        <!-- Accounts Receivable -->
        <v-list-group value="ar">
          <template #activator="{ props }">
            <v-list-item
              v-bind="props"
              prepend-icon="mdi-wallet"
              title="Accounts Receivable"
              rounded="lg"
              class="mb-1"
            />
          </template>
          
          <v-list-item
            prepend-icon="mdi-account-multiple"
            title="Customers"
            to="/ar/customers"
            rounded="lg"
            class="ml-4 mb-1"
          />
          <v-list-item
            prepend-icon="mdi-file-document"
            title="Invoices"
            to="/ar/invoices"
            rounded="lg"
            class="ml-4 mb-1"
          />
          <v-list-item
            prepend-icon="mdi-cash-register"
            title="Receipts"
            to="/ar/receipts"
            rounded="lg"
            class="ml-4 mb-1"
          />
        </v-list-group>

        <!-- Cash Management -->
        <v-list-group value="cash">
          <template #activator="{ props }">
            <v-list-item
              v-bind="props"
              prepend-icon="mdi-bank"
              title="Cash Management"
              rounded="lg"
              class="mb-1"
            />
          </template>
          
          <v-list-item
            prepend-icon="mdi-bank-outline"
            title="Bank Accounts"
            to="/cash/accounts"
            rounded="lg"
            class="ml-4 mb-1"
          />
          <v-list-item
            prepend-icon="mdi-swap-horizontal"
            title="Transactions"
            to="/cash/transactions"
            rounded="lg"
            class="ml-4 mb-1"
          />
          <v-list-item
            prepend-icon="mdi-check-circle"
            title="Reconciliation"
            to="/cash/reconciliation"
            rounded="lg"
            class="ml-4 mb-1"
          />
        </v-list-group>

        <!-- Fixed Assets -->
        <v-list-item
          prepend-icon="mdi-office-building"
          title="Fixed Assets"
          to="/assets"
          rounded="lg"
          class="mb-1"
        />

        <!-- Payroll -->
        <v-list-item
          prepend-icon="mdi-account-cash"
          title="Payroll"
          to="/payroll"
          rounded="lg"
          class="mb-1"
        />

        <!-- Inventory -->
        <v-list-item
          prepend-icon="mdi-package-variant"
          title="Inventory"
          to="/inventory"
          rounded="lg"
          class="mb-1"
        />

        <!-- Reports -->
        <v-list-group value="reports">
          <template #activator="{ props }">
            <v-list-item
              v-bind="props"
              prepend-icon="mdi-chart-line"
              title="Reports"
              rounded="lg"
              class="mb-1"
            />
          </template>
          
          <v-list-item
            prepend-icon="mdi-finance"
            title="Financial Reports"
            to="/reports/financial"
            rounded="lg"
            class="ml-4 mb-1"
          />
          <v-list-item
            prepend-icon="mdi-chart-bar"
            title="Analytics"
            to="/reports/analytics"
            rounded="lg"
            class="ml-4 mb-1"
          />
        </v-list-group>

        <!-- Compliance -->
        <v-list-group value="compliance">
          <template #activator="{ props }">
            <v-list-item
              v-bind="props"
              prepend-icon="mdi-shield-check"
              title="Compliance"
              rounded="lg"
              class="mb-1"
            />
          </template>
          
          <v-list-item
            prepend-icon="mdi-view-dashboard-outline"
            title="Dashboard"
            to="/compliance/dashboard"
            rounded="lg"
            class="ml-4 mb-1"
          />
          <v-list-item
            prepend-icon="mdi-security"
            title="Security Events"
            to="/compliance/security/events"
            rounded="lg"
            class="ml-4 mb-1"
          />
          <v-list-item
            prepend-icon="mdi-file-lock"
            title="Policies"
            to="/compliance/security/policies"
            rounded="lg"
            class="ml-4 mb-1"
          />
        </v-list-group>
      </v-list>
    </div>

    <!-- Footer -->
    <template #append>
      <v-divider class="mb-2" />
      <div class="pa-2">
        <v-list nav density="compact">
          <v-list-item
            prepend-icon="mdi-cog"
            title="Settings"
            to="/settings"
            rounded="lg"
            class="mb-1"
          />
          <v-list-item
            prepend-icon="mdi-help-circle"
            title="Help"
            to="/help"
            rounded="lg"
            class="mb-1"
          />
          <v-list-item
            prepend-icon="mdi-logout"
            title="Logout"
            @click="logout"
            rounded="lg"
          />
        </v-list>
      </div>
    </template>
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
  router.push('/')
}

const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  router.push('/auth/login')
}
</script>

<style scoped>
.sidebar-header {
  border-bottom: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}

.left-sidebar {
  border-right: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}

.sidebar-scroll {
  height: calc(100vh - 140px);
  overflow-y: auto;
}

:deep(.v-list-item--active) {
  background-color: rgba(var(--v-theme-primary), 0.12);
  color: rgb(var(--v-theme-primary));
}

:deep(.v-list-item--active .v-list-item__prepend .v-icon) {
  color: rgb(var(--v-theme-primary));
}

:deep(.v-list-item:hover) {
  background-color: rgba(var(--v-theme-on-surface), 0.04);
}

:deep(.v-navigation-drawer--rail .v-list-item-title) {
  opacity: 0;
}

:deep(.v-list-group__items .v-list-item) {
  padding-inline-start: 16px !important;
}

.cursor-pointer {
  cursor: pointer;
}
</style>