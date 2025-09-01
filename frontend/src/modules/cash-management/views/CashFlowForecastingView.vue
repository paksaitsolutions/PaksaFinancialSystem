<template>
  <div class="cash-flow-management">
    <div class="flex justify-content-between align-items-center mb-4">
      <h1>Cash Flow Management</h1>
      <Button 
        label="Refresh" 
        icon="pi pi-refresh" 
        @click="refreshData"
        :loading="loading"
      />
    </div>
    
    <TabView v-model:activeIndex="activeTab">
      <TabPanel header="Cash Flow Forecasting">
        <CashFlowForecastingDashboard @forecast="generateForecast" />
      </TabPanel>
      
      <TabPanel header="Bank Reconciliation">
        <BankReconciliationInterface @reconcile="performReconciliation" />
      </TabPanel>
      
      <TabPanel header="Cash Position">
        <CashPositionMonitoring />
      </TabPanel>
    </TabView>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import CashFlowForecastingDashboard from '../components/CashFlowForecastingDashboard.vue'
import BankReconciliationInterface from '../components/BankReconciliationInterface.vue'
import CashPositionMonitoring from '../components/CashPositionMonitoring.vue'
import { useCashManagementStore } from '../store/cash-management'

const cashStore = useCashManagementStore()
const activeTab = ref(0)
const loading = ref(false)

const refreshData = async () => {
  loading.value = true
  try {
    await cashStore.refreshAllData()
  } finally {
    loading.value = false
  }
}

const generateForecast = async (forecastParams: any) => {
  await cashStore.generateCashFlowForecast(forecastParams)
}

const performReconciliation = async (reconciliationData: any) => {
  await cashStore.performBankReconciliation(reconciliationData)
}
</script>

<style scoped>
.cash-flow-management {
  padding: 1rem;
}
</style>