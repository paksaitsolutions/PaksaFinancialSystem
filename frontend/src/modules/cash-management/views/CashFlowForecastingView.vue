<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <div class="d-flex justify-space-between align-center mb-4">
          <h1 class="text-h4">Cash Flow Management</h1>
          <v-btn color="primary" @click="refreshData">
            <v-icon left>mdi-refresh</v-icon>
            Refresh
          </v-btn>
        </div>
        
        <v-tabs v-model="activeTab">
          <v-tab value="forecasting">Cash Flow Forecasting</v-tab>
          <v-tab value="reconciliation">Bank Reconciliation</v-tab>
          <v-tab value="position">Cash Position</v-tab>
        </v-tabs>
        
        <v-window v-model="activeTab" class="mt-4">
          <v-window-item value="forecasting">
            <cash-flow-forecasting-dashboard @forecast="generateForecast" />
          </v-window-item>
          
          <v-window-item value="reconciliation">
            <bank-reconciliation-interface @reconcile="performReconciliation" />
          </v-window-item>
          
          <v-window-item value="position">
            <cash-position-monitoring />
          </v-window-item>
        </v-window>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref } from 'vue'
import CashFlowForecastingDashboard from '../components/CashFlowForecastingDashboard.vue'
import BankReconciliationInterface from '../components/BankReconciliationInterface.vue'
import CashPositionMonitoring from '../components/CashPositionMonitoring.vue'
import { useCashManagementStore } from '../store/cash-management'

const cashStore = useCashManagementStore()
const activeTab = ref('forecasting')

const refreshData = async () => {
  await cashStore.refreshAllData()
}

const generateForecast = async (forecastParams) => {
  await cashStore.generateCashFlowForecast(forecastParams)
}

const performReconciliation = async (reconciliationData) => {
  await cashStore.performBankReconciliation(reconciliationData)
}
</script>