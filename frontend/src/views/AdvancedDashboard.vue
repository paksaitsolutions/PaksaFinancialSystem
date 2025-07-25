<template>
  <v-container fluid class="advanced-dashboard">
    <!-- Header -->
    <v-row class="mb-4">
      <v-col>
        <div class="d-flex align-center justify-space-between">
          <div>
            <h1 class="text-h4 font-weight-bold mb-1">AI/BI Analytics Dashboard</h1>
            <p class="text-subtitle-1 text-medium-emphasis">Advanced financial insights and predictions</p>
          </div>
          <v-btn
            color="primary"
            prepend-icon="mdi-refresh"
            @click="refreshData"
            :loading="loading"
          >
            Refresh Data
          </v-btn>
        </div>
      </v-col>
    </v-row>

    <!-- KPI Cards -->
    <v-row class="mb-6">
      <v-col v-for="kpi in kpiMetrics" :key="kpi.title" cols="12" sm="6" md="3">
        <v-card class="kpi-card" elevation="2">
          <v-card-text>
            <div class="d-flex align-center justify-space-between">
              <div>
                <p class="text-caption text-medium-emphasis mb-1">{{ kpi.title }}</p>
                <h3 class="text-h5 font-weight-bold">{{ kpi.value }}</h3>
                <div class="d-flex align-center mt-1">
                  <v-icon 
                    :color="kpi.trend === 'up' ? 'success' : kpi.trend === 'down' ? 'error' : 'warning'"
                    size="small"
                    class="mr-1"
                  >
                    {{ kpi.trend === 'up' ? 'mdi-trending-up' : kpi.trend === 'down' ? 'mdi-trending-down' : 'mdi-trending-neutral' }}
                  </v-icon>
                  <span 
                    :class="kpi.trend === 'up' ? 'text-success' : kpi.trend === 'down' ? 'text-error' : 'text-warning'"
                    class="text-caption"
                  >
                    {{ kpi.change }}
                  </span>
                </div>
              </div>
              <v-avatar :color="kpi.color" size="48">
                <v-icon color="white">{{ kpi.icon }}</v-icon>
              </v-avatar>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Charts Row -->
    <v-row class="mb-6">
      <!-- Revenue vs Expenses Chart -->
      <v-col cols="12" md="8">
        <v-card elevation="2">
          <v-card-title>
            <v-icon class="mr-2">mdi-chart-line</v-icon>
            Revenue vs Expenses Trend
          </v-card-title>
          <v-card-text>
            <canvas ref="revenueChart" height="300"></canvas>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Profit Margin -->
      <v-col cols="12" md="4">
        <v-card elevation="2">
          <v-card-title>
            <v-icon class="mr-2">mdi-chart-donut</v-icon>
            Profit Margin
          </v-card-title>
          <v-card-text>
            <div class="text-center">
              <canvas ref="profitChart" height="200"></canvas>
              <h2 class="text-h4 font-weight-bold mt-3">{{ profitMargin }}%</h2>
              <p class="text-subtitle-2 text-medium-emphasis">Current Margin</p>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Predictive Analytics -->
    <v-row class="mb-6">
      <v-col cols="12" md="8">
        <v-card elevation="2">
          <v-card-title>
            <v-icon class="mr-2">mdi-crystal-ball</v-icon>
            Cash Flow Predictions
            <v-chip class="ml-2" color="primary" size="small">AI Powered</v-chip>
          </v-card-title>
          <v-card-text>
            <canvas ref="predictionChart" height="300"></canvas>
            <div class="mt-3">
              <v-chip color="success" size="small" class="mr-2">
                <v-icon start>mdi-check-circle</v-icon>
                {{ forecastAccuracy }}% Accuracy
              </v-chip>
              <v-chip :color="trendDirection === 'positive' ? 'success' : 'error'" size="small">
                <v-icon start>{{ trendDirection === 'positive' ? 'mdi-trending-up' : 'mdi-trending-down' }}</v-icon>
                {{ trendDirection }} Trend
              </v-chip>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Anomaly Detection -->
      <v-col cols="12" md="4">
        <v-card elevation="2">
          <v-card-title>
            <v-icon class="mr-2">mdi-alert-circle</v-icon>
            Anomaly Detection
          </v-card-title>
          <v-card-text>
            <div v-if="anomalies.length === 0" class="text-center py-4">
              <v-icon size="48" color="success">mdi-shield-check</v-icon>
              <p class="text-subtitle-1 mt-2">No anomalies detected</p>
            </div>
            <div v-else>
              <v-list density="compact">
                <v-list-item
                  v-for="anomaly in anomalies.slice(0, 5)"
                  :key="anomaly.id"
                  class="px-0"
                >
                  <template #prepend>
                    <v-avatar :color="anomaly.severity === 'high' ? 'error' : 'warning'" size="32">
                      <v-icon color="white" size="16">mdi-alert</v-icon>
                    </v-avatar>
                  </template>
                  <v-list-item-title class="text-body-2">
                    {{ anomaly.description }}
                  </v-list-item-title>
                  <v-list-item-subtitle>
                    ${{ anomaly.amount.toLocaleString() }} - {{ anomaly.category }}
                  </v-list-item-subtitle>
                </v-list-item>
              </v-list>
              <v-btn
                v-if="anomalies.length > 5"
                variant="text"
                size="small"
                class="mt-2"
                @click="showAllAnomalies"
              >
                View All {{ anomalies.length }} Anomalies
              </v-btn>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- AI Insights -->
    <v-row>
      <v-col cols="12">
        <v-card elevation="2">
          <v-card-title>
            <v-icon class="mr-2">mdi-brain</v-icon>
            AI-Generated Insights
          </v-card-title>
          <v-card-text>
            <v-row>
              <v-col v-for="insight in aiInsights" :key="insight.id" cols="12" md="4">
                <v-alert
                  :type="insight.type"
                  variant="tonal"
                  class="mb-2"
                >
                  <template #prepend>
                    <v-icon>{{ insight.icon }}</v-icon>
                  </template>
                  <div>
                    <strong>{{ insight.title }}</strong>
                    <p class="text-body-2 mt-1 mb-0">{{ insight.description }}</p>
                  </div>
                </v-alert>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { Chart, registerables } from 'chart.js'
import axios from 'axios'

Chart.register(...registerables)

// Reactive data
const loading = ref(false)
const kpiMetrics = ref([])
const profitMargin = ref(0)
const forecastAccuracy = ref(85)
const trendDirection = ref('positive')
const anomalies = ref([])
const aiInsights = ref([])

// Chart refs
const revenueChart = ref(null)
const profitChart = ref(null)
const predictionChart = ref(null)

// Chart instances
let revenueChartInstance = null
let profitChartInstance = null
let predictionChartInstance = null

const refreshData = async () => {
  loading.value = true
  try {
    await Promise.all([
      loadFinancialOverview(),
      loadPredictiveAnalytics(),
      loadAnomalyDetection(),
      loadKPIMetrics()
    ])
    generateAIInsights()
  } catch (error) {
    console.error('Error loading dashboard data:', error)
  } finally {
    loading.value = false
  }
}

const loadFinancialOverview = async () => {
  try {
    const response = await axios.get('/api/v1/analytics/financial-overview')
    const data = response.data.data
    
    profitMargin.value = data.profit_margin
    
    await nextTick()
    createRevenueChart(data.revenue_trends, data.expense_trends)
    createProfitChart(data.profit_margin)
  } catch (error) {
    console.error('Error loading financial overview:', error)
  }
}

const loadPredictiveAnalytics = async () => {
  try {
    const response = await axios.get('/api/v1/analytics/predictive-analytics')
    const data = response.data.data
    
    forecastAccuracy.value = Math.round(data.forecast_accuracy * 100)
    trendDirection.value = data.trend_direction
    
    await nextTick()
    createPredictionChart(data.historical_cash_flow, data.predictions)
  } catch (error) {
    console.error('Error loading predictive analytics:', error)
  }
}

const loadAnomalyDetection = async () => {
  try {
    const response = await axios.get('/api/v1/analytics/anomaly-detection')
    anomalies.value = response.data.data.anomalies
  } catch (error) {
    console.error('Error loading anomaly detection:', error)
  }
}

const loadKPIMetrics = async () => {
  try {
    const response = await axios.get('/api/v1/analytics/kpi-metrics')
    const data = response.data.data
    
    kpiMetrics.value = [
      {
        title: 'Revenue',
        value: `$${data.revenue?.current_value?.toLocaleString() || '0'}`,
        change: `${data.revenue?.change_percentage || 0}%`,
        trend: data.revenue?.trend || 'stable',
        icon: 'mdi-currency-usd',
        color: 'success'
      },
      {
        title: 'Expenses',
        value: `$${data.expenses?.current_value?.toLocaleString() || '0'}`,
        change: `${data.expenses?.change_percentage || 0}%`,
        trend: data.expenses?.trend || 'stable',
        icon: 'mdi-credit-card',
        color: 'error'
      },
      {
        title: 'Profit Margin',
        value: `${profitMargin.value}%`,
        change: '+2.3%',
        trend: 'up',
        icon: 'mdi-chart-line',
        color: 'primary'
      },
      {
        title: 'Anomalies',
        value: anomalies.value.length.toString(),
        change: '-15%',
        trend: 'down',
        icon: 'mdi-alert-circle',
        color: 'warning'
      }
    ]
  } catch (error) {
    console.error('Error loading KPI metrics:', error)
  }
}

const createRevenueChart = (revenueData, expenseData) => {
  if (revenueChartInstance) {
    revenueChartInstance.destroy()
  }
  
  const ctx = revenueChart.value.getContext('2d')
  revenueChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: revenueData.map(item => item.month),
      datasets: [
        {
          label: 'Revenue',
          data: revenueData.map(item => item.revenue),
          borderColor: '#4CAF50',
          backgroundColor: 'rgba(76, 175, 80, 0.1)',
          tension: 0.4
        },
        {
          label: 'Expenses',
          data: expenseData.map(item => item.expenses),
          borderColor: '#F44336',
          backgroundColor: 'rgba(244, 67, 54, 0.1)',
          tension: 0.4
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top'
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
}

const createProfitChart = (margin) => {
  if (profitChartInstance) {
    profitChartInstance.destroy()
  }
  
  const ctx = profitChart.value.getContext('2d')
  profitChartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      datasets: [{
        data: [margin, 100 - margin],
        backgroundColor: ['#4CAF50', '#E0E0E0'],
        borderWidth: 0
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '70%',
      plugins: {
        legend: {
          display: false
        }
      }
    }
  })
}

const createPredictionChart = (historical, predictions) => {
  if (predictionChartInstance) {
    predictionChartInstance.destroy()
  }
  
  const ctx = predictionChart.value.getContext('2d')
  const allData = [...historical, ...predictions]
  
  predictionChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: allData.map(item => item.week),
      datasets: [
        {
          label: 'Historical Cash Flow',
          data: historical.map(item => item.net_flow),
          borderColor: '#2196F3',
          backgroundColor: 'rgba(33, 150, 243, 0.1)',
          tension: 0.4
        },
        {
          label: 'Predicted Cash Flow',
          data: [...Array(historical.length).fill(null), ...predictions.map(item => item.predicted_flow)],
          borderColor: '#FF9800',
          backgroundColor: 'rgba(255, 152, 0, 0.1)',
          borderDash: [5, 5],
          tension: 0.4
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top'
        }
      },
      scales: {
        y: {
          ticks: {
            callback: function(value) {
              return '$' + value.toLocaleString()
            }
          }
        }
      }
    }
  })
}

const generateAIInsights = () => {
  aiInsights.value = [
    {
      id: 1,
      type: 'success',
      icon: 'mdi-trending-up',
      title: 'Revenue Growth',
      description: 'Revenue has increased by 15% compared to last month, indicating strong business performance.'
    },
    {
      id: 2,
      type: 'warning',
      icon: 'mdi-alert-triangle',
      title: 'Expense Alert',
      description: 'Office supplies expenses are 23% higher than usual. Consider reviewing procurement processes.'
    },
    {
      id: 3,
      type: 'info',
      icon: 'mdi-lightbulb',
      title: 'Optimization Opportunity',
      description: 'Based on cash flow patterns, consider investing surplus funds in short-term instruments.'
    }
  ]
}

const showAllAnomalies = () => {
  // Navigate to detailed anomaly view
  console.log('Show all anomalies')
}

onMounted(() => {
  refreshData()
})
</script>

<style scoped>
.advanced-dashboard {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: 100vh;
}

.kpi-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15) !important;
}

:deep(.v-card-title) {
  font-weight: 600;
  display: flex;
  align-items: center;
}

:deep(.v-alert) {
  border-radius: 12px;
}
</style>