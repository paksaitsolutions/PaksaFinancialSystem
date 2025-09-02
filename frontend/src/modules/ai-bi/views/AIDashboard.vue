<template>
  <div class="ai-dashboard">
    <!-- Header -->
    <div class="dashboard-header">
      <div class="flex align-items-center">
        <i class="pi pi-chart-line text-3xl text-primary mr-3"></i>
        <h1 class="dashboard-title">AI Insights Dashboard</h1>
        <Tag :value="connectionStatus" :severity="connectionSeverity" class="ml-3" />
      </div>
      <div class="header-actions">
        <Button 
          label="Refresh" 
          icon="pi pi-refresh" 
          @click="refreshData" 
          :loading="loading"
        />
        <Button 
          label="Settings" 
          icon="pi pi-cog" 
          severity="secondary" 
          @click="showSettings = true"
        />
      </div>
    </div>

    <!-- Real-time Metrics Cards -->
    <div class="metrics-grid">
      <Card v-for="(card, index) in insightCards" :key="index" class="metric-card">
        <template #content>
          <div class="metric-content">
            <div class="metric-header">
              <i :class="card.icon" :style="{ color: card.color }" class="text-2xl"></i>
              <span class="metric-title">{{ card.title }}</span>
            </div>
            <div class="metric-value">{{ card.value }}</div>
            <div class="metric-description">{{ card.description }}</div>
            <ProgressBar 
              v-if="card.progress" 
              :value="card.progress" 
              class="mt-2"
              :style="{ '--p-progressbar-value-bg': card.color }"
            />
            <div class="metric-trend">
              <i :class="card.trend > 0 ? 'pi pi-arrow-up text-green-500' : 'pi pi-arrow-down text-red-500'"></i>
              <span :class="card.trend > 0 ? 'text-green-500' : 'text-red-500'">{{ Math.abs(card.trend) }}%</span>
            </div>
          </div>
        </template>
      </Card>
    </div>

    <!-- Main Content Grid -->
    <div class="content-grid">
      <!-- Real-time Anomaly Detection -->
      <Card class="anomaly-card">
        <template #header>
          <div class="flex justify-content-between align-items-center p-4">
            <h3 class="m-0">Real-time Anomaly Detection</h3>
            <div class="flex gap-2">
              <Button icon="pi pi-filter" size="small" severity="secondary" @click="showFilters = true" />
              <Button icon="pi pi-download" size="small" severity="secondary" @click="exportAnomalies" />
            </div>
          </div>
        </template>
        <template #content>
          <div class="anomaly-content">
            <canvas ref="anomalyChart" class="anomaly-chart"></canvas>
            <div v-if="anomalies.length === 0" class="empty-state">
              <i class="pi pi-check-circle text-6xl text-green-500"></i>
              <p class="text-xl mt-2">No anomalies detected</p>
              <p class="text-500">System is operating normally</p>
            </div>
          </div>
        </template>
      </Card>

      <!-- AI Recommendations -->
      <Card class="recommendations-card">
        <template #header>
          <div class="flex justify-content-between align-items-center p-4">
            <h3 class="m-0">AI Recommendations</h3>
            <Button label="View All" size="small" severity="secondary" @click="showAllRecommendations = true" />
          </div>
        </template>
        <template #content>
          <div class="recommendations-list">
            <div v-for="(item, i) in recommendations" :key="i" class="recommendation-item">
              <div class="recommendation-content">
                <div class="recommendation-header">
                  <i :class="item.icon" :style="{ color: item.color }" class="text-xl"></i>
                  <span class="recommendation-title">{{ item.title }}</span>
                  <Tag :value="item.priority" :severity="getPrioritySeverity(item.priority)" class="ml-auto" />
                </div>
                <p class="recommendation-description">{{ item.description }}</p>
                <div class="recommendation-actions">
                  <Button label="Apply" size="small" @click="applyRecommendation(item)" />
                  <Button label="Dismiss" size="small" severity="secondary" @click="dismissRecommendation(i)" />
                </div>
              </div>
            </div>
          </div>
        </template>
      </Card>
    </div>

    <!-- Real-time Activity Feed -->
    <Card class="activity-card">
      <template #header>
        <h3 class="p-4 m-0">Real-time Activity Feed</h3>
      </template>
      <template #content>
        <DataTable :value="activityFeed" :paginator="true" :rows="10" responsiveLayout="scroll">
          <Column field="timestamp" header="Time">
            <template #body="{ data }">
              {{ formatTime(data.timestamp) }}
            </template>
          </Column>
          <Column field="type" header="Type">
            <template #body="{ data }">
              <Tag :value="data.type" :severity="getActivitySeverity(data.type)" />
            </template>
          </Column>
          <Column field="message" header="Message"></Column>
          <Column field="confidence" header="Confidence">
            <template #body="{ data }">
              <ProgressBar :value="data.confidence" :showValue="false" class="w-full" style="height: 0.5rem" />
              <small>{{ data.confidence }}%</small>
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <!-- Settings Dialog -->
    <Dialog v-model:visible="showSettings" modal header="AI Dashboard Settings" :style="{ width: '30rem' }">
      <div class="settings-content">
        <div class="field">
          <label class="block text-900 font-medium mb-2">Refresh Interval (seconds)</label>
          <InputNumber v-model="refreshInterval" :min="5" :max="300" class="w-full" />
        </div>
        <div class="field">
          <label class="block text-900 font-medium mb-2">Enable Real-time Updates</label>
          <InputSwitch v-model="realTimeEnabled" />
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" severity="secondary" @click="showSettings = false" />
        <Button label="Save" @click="saveSettings" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

// Reactive state
const loading = ref(false)
const showSettings = ref(false)
const showFilters = ref(false)
const showAllRecommendations = ref(false)
const refreshInterval = ref(30)
const realTimeEnabled = ref(true)
const connectionStatus = ref('Connected')
const anomalyChart = ref<HTMLCanvasElement>()

// WebSocket connection
let ws: WebSocket | null = null
let refreshTimer: NodeJS.Timeout | null = null
let chart: Chart | null = null

// Real-time data
const insightCards = ref([
  {
    title: 'Cash Flow Forecast',
    value: '92%',
    description: 'Accuracy rate',
    progress: 92,
    icon: 'pi pi-chart-line',
    color: '#2196F3',
    trend: 2.5
  },
  {
    title: 'Anomalies Detected',
    value: '0',
    description: 'Active alerts',
    progress: 0,
    icon: 'pi pi-exclamation-triangle',
    color: '#FF9800',
    trend: -15
  },
  {
    title: 'Cost Optimization',
    value: '$12,450',
    description: 'Monthly savings',
    progress: 65,
    icon: 'pi pi-dollar',
    color: '#4CAF50',
    trend: 8.2
  },
  {
    title: 'Processing Speed',
    value: '1.2s',
    description: 'Avg response time',
    progress: 85,
    icon: 'pi pi-clock',
    color: '#9C27B0',
    trend: -5.1
  }
])

const recommendations = ref([
  {
    title: 'Optimize Payment Terms',
    description: 'Extend payment terms with 3 vendors to improve cash flow by 15%',
    icon: 'pi pi-money-bill',
    color: '#2196F3',
    priority: 'High',
    action: '/ap/optimization'
  },
  {
    title: 'Review Expense Patterns',
    description: 'Unusual spending detected in office supplies category',
    icon: 'pi pi-search',
    color: '#FF9800',
    priority: 'Medium',
    action: '/reports/expense-analysis'
  },
  {
    title: 'Update Forecast Model',
    description: 'New market data available to improve prediction accuracy',
    icon: 'pi pi-chart-bar',
    color: '#4CAF50',
    priority: 'Low',
    action: '/settings/forecasting'
  }
])

const anomalies = ref([])
const activityFeed = ref([
  {
    timestamp: new Date(),
    type: 'Prediction',
    message: 'Cash flow forecast updated with 94% confidence',
    confidence: 94
  },
  {
    timestamp: new Date(Date.now() - 300000),
    type: 'Alert',
    message: 'Unusual transaction pattern detected in vendor payments',
    confidence: 87
  },
  {
    timestamp: new Date(Date.now() - 600000),
    type: 'Optimization',
    message: 'Payment schedule optimized, saving $2,340 in fees',
    confidence: 96
  }
])

// Computed properties
const connectionSeverity = computed(() => {
  switch (connectionStatus.value) {
    case 'Connected': return 'success'
    case 'Connecting': return 'warning'
    case 'Disconnected': return 'danger'
    default: return 'info'
  }
})

// WebSocket functions
const connectWebSocket = () => {
  if (!realTimeEnabled.value) return
  
  try {
    ws = new WebSocket('ws://localhost:8000/ws/ai-insights')
    
    ws.onopen = () => {
      connectionStatus.value = 'Connected'
      console.log('AI WebSocket connected')
    }
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      handleRealTimeUpdate(data)
    }
    
    ws.onclose = () => {
      connectionStatus.value = 'Disconnected'
      setTimeout(connectWebSocket, 5000) // Reconnect after 5 seconds
    }
    
    ws.onerror = () => {
      connectionStatus.value = 'Disconnected'
    }
  } catch (error) {
    console.error('WebSocket connection failed:', error)
    connectionStatus.value = 'Disconnected'
  }
}

const handleRealTimeUpdate = (data: any) => {
  switch (data.type) {
    case 'metrics':
      updateMetrics(data.payload)
      break
    case 'anomaly':
      addAnomaly(data.payload)
      break
    case 'recommendation':
      addRecommendation(data.payload)
      break
    case 'activity':
      addActivity(data.payload)
      break
  }
}

const updateMetrics = (metrics: any) => {
  insightCards.value.forEach((card, index) => {
    if (metrics[index]) {
      card.value = metrics[index].value
      card.progress = metrics[index].progress
      card.trend = metrics[index].trend
    }
  })
}

const addAnomaly = (anomaly: any) => {
  anomalies.value.unshift(anomaly)
  if (anomalies.value.length > 50) {
    anomalies.value = anomalies.value.slice(0, 50)
  }
  updateAnomalyChart()
}

const addRecommendation = (recommendation: any) => {
  recommendations.value.unshift(recommendation)
  if (recommendations.value.length > 10) {
    recommendations.value = recommendations.value.slice(0, 10)
  }
}

const addActivity = (activity: any) => {
  activityFeed.value.unshift({
    ...activity,
    timestamp: new Date()
  })
  if (activityFeed.value.length > 100) {
    activityFeed.value = activityFeed.value.slice(0, 100)
  }
}

// Chart functions
const initAnomalyChart = () => {
  if (!anomalyChart.value) return
  
  const ctx = anomalyChart.value.getContext('2d')
  if (!ctx) return
  
  chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: [],
      datasets: [{
        label: 'Anomaly Score',
        data: [],
        borderColor: '#FF6B6B',
        backgroundColor: 'rgba(255, 107, 107, 0.1)',
        tension: 0.4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          max: 100
        }
      }
    }
  })
}

const updateAnomalyChart = () => {
  if (!chart) return
  
  const last20Anomalies = anomalies.value.slice(0, 20).reverse()
  chart.data.labels = last20Anomalies.map((_, i) => `T-${20-i}`)
  chart.data.datasets[0].data = last20Anomalies.map(a => a.score || Math.random() * 100)
  chart.update()
}

// Action functions
const refreshData = async () => {
  loading.value = true
  try {
    // Simulate API call with real data updates
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // Update metrics with simulated real-time data
    insightCards.value.forEach(card => {
      const change = (Math.random() - 0.5) * 10
      card.trend = change
      if (card.title.includes('Anomalies')) {
        card.value = Math.floor(Math.random() * 5).toString()
        card.progress = parseInt(card.value) * 20
      }
    })
  } catch (error) {
    console.error('Error refreshing data:', error)
  } finally {
    loading.value = false
  }
}

const applyRecommendation = (recommendation: any) => {
  console.log('Applying recommendation:', recommendation.title)
  // Implement recommendation application logic
}

const dismissRecommendation = (index: number) => {
  recommendations.value.splice(index, 1)
}

const exportAnomalies = () => {
  const csvContent = anomalies.value.map(a => 
    `${a.timestamp},${a.type},${a.score},${a.description}`
  ).join('\n')
  
  const blob = new Blob([`Timestamp,Type,Score,Description\n${csvContent}`], { type: 'text/csv' })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'anomalies.csv'
  a.click()
  window.URL.revokeObjectURL(url)
}

const saveSettings = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
  
  if (realTimeEnabled.value) {
    connectWebSocket()
    refreshTimer = setInterval(refreshData, refreshInterval.value * 1000)
  } else {
    ws?.close()
  }
  
  showSettings.value = false
}

// Utility functions
const formatTime = (timestamp: Date) => {
  return new Intl.DateTimeFormat('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  }).format(new Date(timestamp))
}

const getPrioritySeverity = (priority: string) => {
  switch (priority.toLowerCase()) {
    case 'high': return 'danger'
    case 'medium': return 'warning'
    case 'low': return 'info'
    default: return 'secondary'
  }
}

const getActivitySeverity = (type: string) => {
  switch (type.toLowerCase()) {
    case 'alert': return 'danger'
    case 'warning': return 'warning'
    case 'prediction': return 'info'
    case 'optimization': return 'success'
    default: return 'secondary'
  }
}

// Lifecycle
onMounted(() => {
  refreshData()
  initAnomalyChart()
  connectWebSocket()
  
  // Set up auto-refresh
  refreshTimer = setInterval(refreshData, refreshInterval.value * 1000)
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
  ws?.close()
  chart?.destroy()
})
</script>

<style scoped>
.ai-dashboard {
  padding: 1.5rem;
  min-height: 100vh;
  background: var(--surface-ground);
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding: 1rem;
  background: var(--surface-card);
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.dashboard-title {
  margin: 0;
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-color);
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.metric-card {
  transition: transform 0.2s;
}

.metric-card:hover {
  transform: translateY(-2px);
}

.metric-content {
  padding: 1rem;
}

.metric-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.metric-title {
  font-weight: 600;
  color: var(--text-color-secondary);
}

.metric-value {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--text-color);
  margin-bottom: 0.5rem;
}

.metric-description {
  color: var(--text-color-secondary);
  font-size: 0.875rem;
  margin-bottom: 1rem;
}

.metric-trend {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.875rem;
  font-weight: 600;
}

.content-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.anomaly-card {
  min-height: 400px;
}

.anomaly-content {
  position: relative;
  height: 300px;
}

.anomaly-chart {
  width: 100%;
  height: 100%;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-color-secondary);
}

.recommendations-card {
  min-height: 400px;
}

.recommendations-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.recommendation-item {
  padding: 1rem;
  border: 1px solid var(--surface-border);
  border-radius: 6px;
  background: var(--surface-50);
}

.recommendation-content {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.recommendation-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.recommendation-title {
  font-weight: 600;
  color: var(--text-color);
}

.recommendation-description {
  color: var(--text-color-secondary);
  margin: 0;
  font-size: 0.875rem;
}

.recommendation-actions {
  display: flex;
  gap: 0.5rem;
}

.activity-card {
  margin-bottom: 2rem;
}

.settings-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

@media (max-width: 768px) {
  .ai-dashboard {
    padding: 1rem;
  }
  
  .dashboard-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .metrics-grid {
    grid-template-columns: 1fr;
  }
  
  .content-grid {
    grid-template-columns: 1fr;
  }
}

@media (min-width: 769px) and (max-width: 1024px) {
  .metrics-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1025px) {
  .metrics-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}
</style>
