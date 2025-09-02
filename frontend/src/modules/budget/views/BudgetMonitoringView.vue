<template>
  <div class="p-4">
    <h1 class="text-3xl font-bold mb-4">Budget Monitoring</h1>
    
    <TabView v-model:activeIndex="activeTabIndex">
      <TabPanel header="Real-time Monitoring">
        <realtime-monitoring-dashboard />
      </TabPanel>
      
      <TabPanel header="Alert Management">
        <alert-management-interface @create="createAlert" />
      </TabPanel>
      
      <TabPanel header="Variance Analysis">
        <variance-analysis-reports />
      </TabPanel>
    </TabView>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import RealtimeMonitoringDashboard from '../components/RealtimeMonitoringDashboard.vue'
import AlertManagementInterface from '../components/AlertManagementInterface.vue'
import VarianceAnalysisReports from '../components/VarianceAnalysisReports.vue'
import { useBudgetStore } from '../store/budget'

const budgetStore = useBudgetStore()
const activeTabIndex = ref(0)

const createAlert = async (alertData) => {
  await budgetStore.createBudgetAlert(alertData)
}
</script>