<template>
  <v-navigation-drawer v-model="drawer" app width="280" permanent>
    <!-- Header -->
    <div class="pa-4 border-b">
      <div class="d-flex align-center">
        <v-img src="/logo.png" height="32" width="32" class="mr-3"></v-img>
        <div>
          <div class="text-h6 font-weight-bold">Paksa Financial</div>
          <div class="text-caption text-medium-emphasis">{{ user?.name || 'User' }}</div>
        </div>
      </div>
    </div>

    <!-- Navigation Menu -->
    <v-list nav density="compact" class="pa-2">
      <!-- Dashboard -->
      <v-list-item 
        :to="'/'"
        prepend-icon="mdi-view-dashboard"
        title="Dashboard"
        rounded="xl"
        class="mb-1"
      ></v-list-item>

      <!-- Accounting Module -->
      <v-list-group value="accounting">
        <template v-slot:activator="{ props }">
          <v-list-item
            v-bind="props"
            prepend-icon="mdi-calculator"
            title="Accounting"
            rounded="xl"
          ></v-list-item>
        </template>
        <v-list-item :to="'/gl'" title="General Ledger" class="ml-4" rounded="xl"></v-list-item>
        <v-list-item :to="'/gl/chart-of-accounts'" title="Chart of Accounts" class="ml-4" rounded="xl"></v-list-item>
        <v-list-item :to="'/gl/journal-entries'" title="Journal Entries" class="ml-4" rounded="xl"></v-list-item>
        <v-list-item :to="'/gl/trial-balance'" title="Trial Balance" class="ml-4" rounded="xl"></v-list-item>
        <v-list-item :to="'/gl/financial-statements'" title="Financial Statements" class="ml-4" rounded="xl"></v-list-item>
      </v-list-group>

      <!-- Accounts Payable -->
      <v-list-group value="ap">
        <template v-slot:activator="{ props }">
          <v-list-item
            v-bind="props"
            prepend-icon="mdi-credit-card-outline"
            title="Accounts Payable"
            rounded="xl"
          ></v-list-item>
        </template>
        <v-list-item :to="'/ap'" title="AP Dashboard" class="ml-4" rounded="xl"></v-list-item>
      </v-list-group>

      <!-- Accounts Receivable -->
      <v-list-group value="ar">
        <template v-slot:activator="{ props }">
          <v-list-item
            v-bind="props"
            prepend-icon="mdi-cash-multiple"
            title="Accounts Receivable"
            rounded="xl"
          ></v-list-item>
        </template>
        <v-list-item :to="'/ar'" title="AR Dashboard" class="ml-4" rounded="xl"></v-list-item>
      </v-list-group>

      <!-- Reports -->
      <v-list-item 
        :to="'/reports'"
        prepend-icon="mdi-chart-bar"
        title="Reports"
        rounded="xl"
        class="mb-1"
      ></v-list-item>

      <v-divider class="my-2"></v-divider>

      <!-- Administration -->
      <v-list-group value="admin">
        <template v-slot:activator="{ props }">
          <v-list-item
            v-bind="props"
            prepend-icon="mdi-cog"
            title="Administration"
            rounded="xl"
          ></v-list-item>
        </template>
        <v-list-item :to="'/admin'" title="Super Admin" class="ml-4" rounded="xl"></v-list-item>
        <v-list-item :to="'/settings'" title="Settings" class="ml-4" rounded="xl"></v-list-item>
        <v-list-item :to="'/rbac'" title="Role Management" class="ml-4" rounded="xl"></v-list-item>
      </v-list-group>
    </v-list>

    <!-- Footer -->
    <template v-slot:append>
      <div class="pa-4 border-t">
        <v-btn
          block
          variant="outlined"
          prepend-icon="mdi-logout"
          @click="logout"
        >
          Logout
        </v-btn>
      </div>
    </template>
  </v-navigation-drawer>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const drawer = ref(true)
const user = ref<any>(null)

onMounted(() => {
  const userData = localStorage.getItem('user')
  if (userData) {
    user.value = JSON.parse(userData)
  }
})

const logout = () => {
  localStorage.removeItem('user')
  localStorage.removeItem('token')
  router.push('/auth/login')
}
</script>

<style scoped>
.border-b {
  border-bottom: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}

.border-t {
  border-top: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}
</style>