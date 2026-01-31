<template>
  <div class="dashboard-main">
    <!-- Page Header -->
    <div class="page-header">
      <h1 class="page-title">Financial Dashboard</h1>
      <p class="page-subtitle">Real-time overview of your financial performance</p>
    </div>

    <!-- KPI Widgets Row -->
    <div class="grid">
      <div class="col-12 sm:col-6 lg:col-3" v-for="(kpi, key) in kpis" :key="key">
        <KPIWidget 
          :title="kpi.label"
          :value="kpi.value"
          :trend="kpi.trend"
          :change="kpi.change_percent"
          :format="getKPIFormat(key)"
        />
      </div>
    </div>

    <!-- Alerts Panel -->
    <div class="grid" v-if="alerts.length > 0">
      <div class="col-12">
        <AlertsPanel :alerts="alerts" @dismiss="dismissAlert" />
      </div>
    </div>

    <!-- Charts Row -->
    <div class="grid">
      <div class="col-12 lg:col-8">
        <Card class="chart-card">
          <template #title>
            <div class="card-title-wrapper">
              <h3>Revenue Trend</h3>
              <small>Last 12 months</small>
            </div>
          </template>
          <template #content>
            <div class="chart-container">
              <canvas ref="revenueChart"></canvas>
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 lg:col-4">
        <Card class="chart-card">
          <template #title>
            <div class="card-title-wrapper">
              <h3>Expense Breakdown</h3>
              <small>Current month</small>
            </div>
          </template>
          <template #content>
            <div class="chart-container">
              <canvas ref="expenseChart"></canvas>
            </div>
          </template>
        </Card>
      </div>
    </div>

    <!-- Cash Flow and Aging Charts -->
    <div class="grid">
      <div class="col-12 md:col-6">
        <Card class="chart-card">
          <template #title>
            <div class="card-title-wrapper">
              <h3>Cash Flow</h3>
              <small>Monthly comparison</small>
            </div>
          </template>
          <template #content>
            <div class="chart-container">
              <canvas ref="cashFlowChart"></canvas>
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 md:col-6">
        <Card class="chart-card">
          <template #title>
            <div class="card-title-wrapper">
              <h3>A/R Aging</h3>
              <small>Outstanding receivables</small>
            </div>
          </template>
          <template #content>
            <div class="chart-container">
              <canvas ref="arAgingChart"></canvas>
            </div>
          </template>
        </Card>
      </div>
    </div>

    <!-- Quick Actions and Activity Feed -->
    <div class="grid">
      <div class="col-12 lg:col-4">
        <QuickActions :actions="quickActions" />
      </div>
      <div class="col-12 lg:col-8">
        <ActivityFeed :activities="recentActivity" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { Chart, registerables } from 'chart.js'
import KPIWidget from './KPIWidget.vue'
import AlertsPanel from './AlertsPanel.vue'
import QuickActions from './QuickActions.vue'
import ActivityFeed from './ActivityFeed.vue'

Chart.register(...registerables)

const kpis = ref({})
const alerts = ref([])
const quickActions = ref([])
const recentActivity = ref([])

const revenueChart = ref(null)
const expenseChart = ref(null)
const cashFlowChart = ref(null)
const arAgingChart = ref(null)

let charts = {}
let refreshInterval = null

onMounted(async () => {
  await loadDashboardData()
  initializeCharts()
  startAutoRefresh()
})

onUnmounted(() => {
  stopAutoRefresh()
  destroyCharts()
})

const loadDashboardData = async () => {
  try {
    // Load dashboard summary
    const response = await fetch('/api/dashboard/summary')
    const data = await response.json()
    
    kpis.value = data.kpis
    alerts.value = data.alerts
    quickActions.value = data.quick_actions
    recentActivity.value = data.recent_activity
    
  } catch (error) {
    console.error('Failed to load dashboard data:', error)
  }
}

const initializeCharts = async () => {
  await initRevenueChart()
  await initExpenseChart()
  await initCashFlowChart()
  await initARAgingChart()
}

const initRevenueChart = async () => {
  try {
    const response = await fetch('/api/dashboard/charts/revenue-trend')
    const data = await response.json()
    
    const ctx = revenueChart.value.getContext('2d')
    charts.revenue = new Chart(ctx, {
      type: 'line',
      data: data,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              callback: function(value) {
                return '$' + value.toLocaleString()
              }
            }
          }
        }
      }
    })
  } catch (error) {
    console.error('Failed to load revenue chart:', error)
  }
}

const initExpenseChart = async () => {
  try {
    const response = await fetch('/api/dashboard/charts/expense-breakdown')
    const data = await response.json()
    
    const ctx = expenseChart.value.getContext('2d')
    charts.expense = new Chart(ctx, {
      type: 'doughnut',
      data: data,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom'
          }
        }
      }
    })
  } catch (error) {
    console.error('Failed to load expense chart:', error)
  }
}

const initCashFlowChart = async () => {
  try {
    const response = await fetch('/api/dashboard/charts/cash-flow')
    const data = await response.json()
    
    const ctx = cashFlowChart.value.getContext('2d')
    charts.cashFlow = new Chart(ctx, {
      type: 'bar',
      data: data,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              callback: function(value) {
                return '$' + value.toLocaleString()
              }
            }
          }
        }
      }
    })
  } catch (error) {
    console.error('Failed to load cash flow chart:', error)
  }
}

const initARAgingChart = async () => {
  try {
    const response = await fetch('/api/dashboard/charts/ar-aging')
    const data = await response.json()
    
    const ctx = arAgingChart.value.getContext('2d')
    charts.arAging = new Chart(ctx, {
      type: 'bar',
      data: data,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        indexAxis: 'y',
        plugins: {
          legend: {
            display: false
          }
        },
        scales: {
          x: {
            beginAtZero: true,
            ticks: {
              callback: function(value) {
                return '$' + value.toLocaleString()
              }
            }
          }
        }
      }
    })
  } catch (error) {
    console.error('Failed to load A/R aging chart:', error)
  }
}

const dismissAlert = async (alertId) => {
  try {
    await fetch(`/api/dashboard/alerts/${alertId}/dismiss`, { method: 'POST' })
    alerts.value = alerts.value.filter(alert => alert.id !== alertId)
  } catch (error) {
    console.error('Failed to dismiss alert:', error)
  }
}

const getKPIFormat = (key) => {
  if (key.includes('balance') || key.includes('income')) return 'currency'
  if (key.includes('percent')) return 'percent'
  return 'number'
}

const startAutoRefresh = () => {
  refreshInterval = setInterval(async () => {
    try {
      const response = await fetch('/api/dashboard/updates')
      const data = await response.json()
      
      if (data.has_updates) {
        kpis.value = data.kpis
        alerts.value = data.alerts
      }
    } catch (error) {
      console.error('Failed to refresh dashboard:', error)
    }
  }, 30000) // Refresh every 30 seconds
}

const stopAutoRefresh = () => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
    refreshInterval = null
  }
}

const destroyCharts = () => {
  Object.values(charts).forEach(chart => {
    if (chart) chart.destroy()
  })
  charts = {}
}
</script>

<style scoped>
.dashboard-main {
  padding: 0;
  background: var(--surface-ground, #f8f9fa);
}

.page-header {
  background: var(--surface-card, #ffffff);
  padding: 2rem;
  margin-bottom: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  border: 1px solid var(--surface-border, #e5e7eb);
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-color, #1e293b);
  margin: 0 0 0.5rem 0;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-subtitle {
  font-size: 1rem;
  color: var(--text-color-secondary, #64748b);
  margin: 0;
}

.grid {
  margin-bottom: 2rem;
}

.chart-card {
  height: 100%;
}

.card-title-wrapper {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.card-title-wrapper h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-color, #1e293b);
  margin: 0;
}

.card-title-wrapper small {
  font-size: 0.875rem;
  color: var(--text-color-secondary, #64748b);
  font-weight: 400;
}

.chart-container {
  position: relative;
  height: 300px;
  width: 100%;
}

.chart-container canvas {
  width: 100% !important;
  height: 100% !important;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .page-header {
    padding: 1.5rem;
    margin-bottom: 1.5rem;
  }
  
  .page-title {
    font-size: 1.75rem;
  }
  
  .chart-container {
    height: 250px;
  }
  
  .grid {
    margin-bottom: 1.5rem;
  }
}

@media (max-width: 576px) {
  .page-header {
    padding: 1rem;
    margin-bottom: 1rem;
  }
  
  .page-title {
    font-size: 1.5rem;
  }
  
  .chart-container {
    height: 200px;
  }
}

/* Loading state */
.chart-container.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--surface-section, #f8f9fa);
  border-radius: 8px;
}

.chart-container.loading::before {
  content: 'Loading chart...';
  color: var(--text-color-secondary, #64748b);
  font-size: 0.875rem;
}
</style>