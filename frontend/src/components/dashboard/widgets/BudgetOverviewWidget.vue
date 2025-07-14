<template>
  <v-card>
    <v-card-title>Budget Overview</v-card-title>
    <v-card-text>
      <v-row>
        <!-- Budget Status Cards -->
        <v-col cols="12" sm="6" md="3">
          <v-card class="pa-4">
            <div class="d-flex justify-space-between align-center">
              <div>
                <h3 class="text-h6 mb-1">Total Budgets</h3>
                <p class="text-caption">Active budgets</p>
              </div>
              <v-icon size="40" color="primary">mdi-chart-box</v-icon>
            </div>
            <div class="text-h4 mt-4">{{ stats.totalBudgets }}</div>
          </v-card>
        </v-col>

        <v-col cols="12" sm="6" md="3">
          <v-card class="pa-4">
            <div class="d-flex justify-space-between align-center">
              <div>
                <h3 class="text-h6 mb-1">Budget Usage</h3>
                <p class="text-caption">Current usage</p>
              </div>
              <v-icon size="40" color="success">mdi-currency-usd</v-icon>
            </div>
            <div class="text-h4 mt-4">{{ stats.usagePercentage }}%</div>
          </v-card>
        </v-col>

        <v-col cols="12" sm="6" md="3">
          <v-card class="pa-4">
            <div class="d-flex justify-space-between align-center">
              <div>
                <h3 class="text-h6 mb-1">Pending Approval</h3>
                <p class="text-caption">Waiting for approval</p>
              </div>
              <v-icon size="40" color="warning">mdi-clock-alert</v-icon>
            </div>
            <div class="text-h4 mt-4">{{ stats.pendingApproval }}</div>
          </v-card>
        </v-col>

        <v-col cols="12" sm="6" md="3">
          <v-card class="pa-4">
            <div class="d-flex justify-space-between align-center">
              <div>
                <h3 class="text-h6 mb-1">Budget Variance</h3>
                <p class="text-caption">Current variance</p>
              </div>
              <v-icon size="40" :color="stats.varianceColor">mdi-chart-line</v-icon>
            </div>
            <div class="text-h4 mt-4">{{ stats.variancePercentage }}%</div>
          </v-card>
        </v-col>
      </v-row>

      <!-- Budget Trend Chart -->
      <v-row class="mt-4">
        <v-col cols="12">
          <apexchart
            type="line"
            :options="trendChartOptions"
            :series="trendChartSeries"
            height="300"
          ></apexchart>
        </v-col>
      </v-row>

      <!-- Budget Alerts -->
      <v-row class="mt-4">
        <v-col cols="12">
          <v-alert
            v-for="alert in alerts"
            :key="alert.id"
            :type="alert.type"
            :icon="alert.icon"
            class="mb-2"
          >
            {{ alert.message }}
          </v-alert>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useBudgetStore } from '@/stores/budget'
import { useApi } from '@/composables/useApi'

const api = useApi()
const budgetStore = useBudgetStore()

// State
const stats = ref({
  totalBudgets: 0,
  usagePercentage: 0,
  pendingApproval: 0,
  variancePercentage: 0,
  varianceColor: 'success'
})

const alerts = ref([])

// Computed
const trendChartSeries = computed(() => [{
  name: 'Budget Usage',
  data: stats.value.usageHistory
}])

const trendChartOptions = {
  xaxis: {
    type: 'datetime',
    categories: stats.value.usageDates
  },
  colors: ['#4CAF50'],
  dataLabels: {
    enabled: true
  },
  markers: {
    size: 4
  }
}

// Methods
const fetchBudgetStats = async () => {
  try {
    const response = await api.get('/budget/stats')
    stats.value = {
      ...stats.value,
      ...response.data
    }
    
    // Update alerts based on stats
    updateBudgetAlerts()
  } catch (err) {
    console.error('Error fetching budget stats:', err)
  }
}

const updateBudgetAlerts = () => {
  alerts.value = []
  
  // Add alerts based on budget stats
  if (stats.value.usagePercentage >= 80) {
    alerts.value.push({
      id: 'high-usage',
      type: 'warning',
      icon: 'mdi-alert',
      message: 'Budget usage is approaching capacity (80% or higher)'
    })
  }

  if (stats.value.variancePercentage > 10) {
    alerts.value.push({
      id: 'high-variance',
      type: 'error',
      icon: 'mdi-chart-line',
      message: 'Budget variance exceeds 10%'
    })
  }

  if (stats.value.pendingApproval > 5) {
    alerts.value.push({
      id: 'pending-approval',
      type: 'warning',
      icon: 'mdi-clock-alert',
      message: 'Multiple budgets pending approval'
    })
  }
}

// Lifecycle
onMounted(() => {
  fetchBudgetStats()
  // Refresh stats every 5 minutes
  setInterval(fetchBudgetStats, 300000)
})
</script>
