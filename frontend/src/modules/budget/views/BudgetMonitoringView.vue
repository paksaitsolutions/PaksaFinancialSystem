<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-4">Budget Monitoring</h1>
        
        <v-tabs v-model="activeTab">
          <v-tab value="realtime">Real-time Monitoring</v-tab>
          <v-tab value="alerts">Alert Management</v-tab>
          <v-tab value="variance">Variance Analysis</v-tab>
        </v-tabs>
        
        <v-window v-model="activeTab" class="mt-4">
          <v-window-item value="realtime">
            <realtime-monitoring-dashboard />
          </v-window-item>
          
          <v-window-item value="alerts">
            <alert-management-interface @create="createAlert" />
          </v-window-item>
          
          <v-window-item value="variance">
            <variance-analysis-reports />
          </v-window-item>
        </v-window>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref } from 'vue'
import RealtimeMonitoringDashboard from '../components/RealtimeMonitoringDashboard.vue'
import AlertManagementInterface from '../components/AlertManagementInterface.vue'
import VarianceAnalysisReports from '../components/VarianceAnalysisReports.vue'
import { useBudgetStore } from '../store/budget'

const budgetStore = useBudgetStore()
const activeTab = ref('realtime')

const createAlert = async (alertData) => {
  await budgetStore.createBudgetAlert(alertData)
}
</script>