<template>
  <v-navigation-drawer v-model="drawer" app>
    <!-- Company Header -->
    <v-list-item class="company-header">
      <template v-slot:prepend>
        <v-avatar>
          <v-img v-if="currentCompany?.logo" :src="currentCompany.logo"></v-img>
          <span v-else>{{ currentCompany?.name?.charAt(0) }}</span>
        </v-avatar>
      </template>
      
      <v-list-item-title>{{ currentCompany?.name }}</v-list-item-title>
      <v-list-item-subtitle>{{ currentCompany?.subscription_plan }}</v-list-item-subtitle>
      
      <template v-slot:append>
        <CompanySwitcher />
      </template>
    </v-list-item>
    
    <v-divider></v-divider>
    
    <!-- Navigation Items -->
    <v-list>
      <v-list-item to="/" exact>
        <template v-slot:prepend>
          <v-icon>mdi-view-dashboard</v-icon>
        </template>
        <v-list-item-title>Dashboard</v-list-item-title>
      </v-list-item>
      
      <v-list-item v-if="canAccessBudgets" to="/budget">
        <template v-slot:prepend>
          <v-icon>mdi-calculator</v-icon>
        </template>
        <v-list-item-title>Budget</v-list-item-title>
      </v-list-item>
      
      <v-list-item v-if="canAccessFixedAssets" to="/fixed-assets">
        <template v-slot:prepend>
          <v-icon>mdi-office-building</v-icon>
        </template>
        <v-list-item-title>Fixed Assets</v-list-item-title>
      </v-list-item>
      
      <v-list-item v-if="canAccessTax" to="/tax">
        <template v-slot:prepend>
          <v-icon>mdi-receipt</v-icon>
        </template>
        <v-list-item-title>Tax Management</v-list-item-title>
      </v-list-item>
      
      <v-list-item v-if="canAccessInventory" to="/inventory">
        <template v-slot:prepend>
          <v-icon>mdi-package-variant</v-icon>
        </template>
        <v-list-item-title>Inventory</v-list-item-title>
      </v-list-item>
      
      <v-list-item v-if="canAccessPayroll" to="/payroll">
        <template v-slot:prepend>
          <v-icon>mdi-account-group</v-icon>
        </template>
        <v-list-item-title>Payroll</v-list-item-title>
      </v-list-item>
      
      <v-list-item v-if="canAccessReports" to="/reports">
        <template v-slot:prepend>
          <v-icon>mdi-chart-line</v-icon>
        </template>
        <v-list-item-title>Reports</v-list-item-title>
      </v-list-item>
    </v-list>
  </v-navigation-drawer>
</template>

<script>
import { useTenantStore } from '@/stores/tenant'
import { useFeatureFlags } from '@/composables/useFeatureFlags'
import CompanySwitcher from '@/components/tenant/CompanySwitcher.vue'


/**
 * TenantNavigation Component
 * 
 * @component
 */

export default {
  name: 'TenantNavigation',
  components: { CompanySwitcher },
  
  props: {
    modelValue: Boolean
  },
  
  emits: ['update:modelValue'],
  
  computed: {
    drawer: {
      get() { return this.modelValue },
      set(value) { this.$emit('update:modelValue', value) }
    },
    currentCompany() {
      return this.tenantStore.currentCompany
    }
  },
  
  setup() {
    const tenantStore = useTenantStore()
    const {
      canAccessBudgets,
      canAccessFixedAssets,
      canAccessTax,
      canAccessInventory,
      canAccessPayroll,
      canAccessReports
    } = useFeatureFlags()
    
    return {
      tenantStore,
      canAccessBudgets,
      canAccessFixedAssets,
      canAccessTax,
      canAccessInventory,
      canAccessPayroll,
      canAccessReports
    }
  }
}
</script>

<style scoped>
.company-header {
  background-color: rgba(0, 0, 0, 0.05);
  margin-bottom: 8px;
}
</style>