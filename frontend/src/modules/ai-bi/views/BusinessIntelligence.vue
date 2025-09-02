<template>
  <div class="business-intelligence">
    <!-- Header -->
    <div class="bi-header">
      <div class="flex align-items-center">
        <i class="pi pi-chart-pie text-3xl text-primary mr-3"></i>
        <h1 class="bi-title">Business Intelligence Dashboard</h1>
        <Tag :value="connectionStatus" :severity="connectionSeverity" class="ml-3" />
      </div>
      <div class="header-controls">
        <SelectButton v-model="timeRange" :options="timeRangeOptions" optionLabel="label" optionValue="value" />
        <Button label="Export" icon="pi pi-download" severity="secondary" @click="exportDashboard" />
        <Button label="Refresh" icon="pi pi-refresh" @click="refreshData" :loading="loading" />
      </div>
    </div>

    <!-- KPI Cards -->
    <div class="kpi-grid">
      <Card v-for="(kpi, i) in kpis" :key="i" class="kpi-card">
        <template #content>
          <div class="kpi-content">
            <div class="kpi-header">
              <div class="kpi-info">
                <span class="kpi-label">{{ kpi.title }}</span>
                <div class="kpi-value">{{ formatCurrency(kpi.value) }}</div>
              </div>
              <div class="kpi-trend-icon" :class="kpi.trend >= 0 ? 'positive' : 'negative'">
                <i :class="kpi.trend >= 0 ? 'pi pi-arrow-up' : 'pi pi-arrow-down'"></i>
              </div>
            </div>
            <div class="kpi-trend">
              <span :class="kpi.trend >= 0 ? 'text-green-600' : 'text-red-600'" class="trend-value">
                {{ Math.abs(kpi.trend).toFixed(1) }}% {{ kpi.trend >= 0 ? 'increase' : 'decrease' }}
              </span>
              <span class="trend-period">vs last period</span>
            </div>
            <ProgressBar :value="kpi.progress" class="kpi-progress" :showValue="false" />
          </div>
        </template>
      </Card>
    </div>

    <!-- Main Analytics Grid -->
    <div class="analytics-grid">
      <!-- Revenue vs Expenses Chart -->
      <Card class="chart-card">
        <template #header>
          <div class="flex justify-content-between align-items-center p-4">
            <h3 class="m-0">Revenue vs Expenses Trend</h3>
            <div class="chart-controls">
              <Button icon="pi pi-filter" size="small" severity="secondary" @click="showChartFilters = true" />
              <Button icon="pi pi-expand" size="small" severity="secondary" @click="expandChart" />
            </div>
          </div>
        </template>
        <template #content>
          <div class="chart-container">
            <canvas ref="revenueChart" class="revenue-chart"></canvas>
          </div>
        </template>
      </Card>

      <!-- AI Insights Panel -->
      <Card class="insights-card">
        <template #header>
          <div class="flex justify-content-between align-items-center p-4">
            <h3 class="m-0">AI-Powered Insights</h3>
            <Button label="View All" size="small" severity="secondary" @click="viewAllInsights" />
          </div>
        </template>
        <template #content>
          <div class="insights-list">
            <div v-for="(insight, i) in aiInsights" :key="i" class="insight-item">
              <div class="insight-icon">
                <i :class="insight.icon" :style="{ color: insight.color }"></i>
              </div>
              <div class="insight-content">
                <h4 class="insight-title">{{ insight.title }}</h4>
                <p class="insight-description">{{ insight.description }}</p>
                <div class="insight-confidence">
                  <span class="confidence-label">Confidence:</span>
                  <ProgressBar :value="insight.confidence" class="confidence-bar" :showValue="false" />
                  <span class="confidence-value">{{ insight.confidence }}%</span>
                </div>
              </div>
            </div>
          </div>
        </template>
      </Card>
    </div>

    <!-- Secondary Analytics -->
    <div class="secondary-grid">
      <!-- Performance Metrics -->
      <Card class="performance-card">
        <template #header>
          <h3 class="p-4 m-0">Performance Metrics</h3>
        </template>
        <template #content>
          <div class="performance-metrics">
            <div v-for="(metric, i) in performanceMetrics" :key="i" class="metric-row">
              <div class="metric-info">
                <span class="metric-name">{{ metric.name }}</span>
                <span class="metric-target">Target: {{ metric.target }}</span>
              </div>
              <div class="metric-progress">
                <ProgressBar :value="metric.progress" class="w-full" />
                <span class="metric-value">{{ metric.current }}</span>
              </div>
            </div>
          </div>
        </template>
      </Card>

      <!-- Recent Transactions -->
      <Card class="transactions-card">
        <template #header>
          <div class="flex justify-content-between align-items-center p-4">
            <h3 class="m-0">Recent Transactions</h3>
            <Button label="View All" size="small" severity="secondary" @click="viewAllTransactions" />
          </div>
        </template>
        <template #content>
          <DataTable :value="recentTransactions" responsiveLayout="scroll" :paginator="false">
            <Column field="date" header="Date">
              <template #body="{ data }">
                {{ formatDate(data.date) }}
              </template>
            </Column>
            <Column field="description" header="Description"></Column>
            <Column field="amount" header="Amount">
              <template #body="{ data }">
                <span :class="data.amount > 0 ? 'text-green-600' : 'text-red-600'" class="font-semibold">
                  {{ formatCurrency(data.amount) }}
                </span>
              </template>
            </Column>
            <Column field="category" header="Category">
              <template #body="{ data }">
                <Tag :value="data.category" severity="info" />
              </template>
            </Column>
          </DataTable>
        </template>
      </Card>

      <!-- Predictive Analytics -->
      <Card class="predictions-card">
        <template #header>
          <h3 class="p-4 m-0">Predictive Analytics</h3>
        </template>
        <template #content>
          <div class="predictions-content">
            <div v-for="(prediction, i) in predictions" :key="i" class="prediction-item">
              <div class="prediction-header">
                <span class="prediction-title">{{ prediction.title }}</span>
                <Tag :value="prediction.timeframe" severity="info" />
              </div>
              <div class="prediction-value">{{ prediction.value }}</div>
              <div class="prediction-accuracy">
                <span class="accuracy-label">Accuracy:</span>
                <ProgressBar :value="prediction.accuracy" class="accuracy-bar" :showValue="false" />
                <span class="accuracy-value">{{ prediction.accuracy }}%</span>
              </div>
            </div>
          </div>
        </template>
      </Card>
    </div>

    <!-- Chart Filters Dialog -->
    <Dialog v-model:visible="showChartFilters" modal header="Chart Filters" :style="{ width: '30rem' }">
      <div class="filter-options">
        <div class="field">
          <label class="block text-900 font-medium mb-2">Date Range</label>
          <Calendar v-model="chartFilters.dateRange" selectionMode="range" class="w-full" />
        </div>
        <div class="field">
          <label class="block text-900 font-medium mb-2">Categories</label>
          <MultiSelect v-model="chartFilters.categories" :options="categoryOptions" optionLabel="label" optionValue="value" class="w-full" />
        </div>
      </div>
      <template #footer>
        <Button label="Reset" severity="secondary" @click="resetFilters" />
        <Button label="Apply" @click="applyFilters" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { Chart, registerables } from 'chart.js'
import { useAIStore } from '../store/aiStore'

Chart.register(...registerables)

const aiStore = useAIStore()

// Reactive state
const timeRange = ref('30d')
const loading = ref(false)
const connectionStatus = ref('Connected')
const showChartFilters = ref(false)
const revenueChart = ref<HTMLCanvasElement>()

// Chart and data
let chart: Chart | null = null

const timeRangeOptions = ref([
  { label: '7 Days', value: '7d' },
  { label: '30 Days', value: '30d' },
  { label: '90 Days', value: '90d' },
  { label: '1 Year', value: '1y' }
])

const kpis = ref([
  { 
    title: 'Total Revenue', 
    value: 125000, 
    trend: 12.5, 
    progress: 78,
    target: 160000
  },
  { 
    title: 'Total Expenses', 
    value: 87500, 
    trend: -5.2, 
    progress: 65,
    target: 100000
  },
  { 
    title: 'Net Profit', 
    value: 37500, 
    trend: 8.3, 
    progress: 85,
    target: 45000
  },
  { 
    title: 'Cash Flow', 
    value: 42500, 
    trend: 15.7, 
    progress: 92,
    target: 50000
  }
])

const aiInsights = ref([
  {
    title: 'Revenue Growth Opportunity',
    description: 'AI detected a 23% increase potential in Q4 based on seasonal patterns and market trends.',
    confidence: 87,
    icon: 'pi pi-trending-up',
    color: '#4CAF50'
  },
  {
    title: 'Cost Optimization Alert',
    description: 'Unusual spending pattern in office supplies. Potential savings of $2,340 identified.',
    confidence: 94,
    icon: 'pi pi-exclamation-triangle',
    color: '#FF9800'
  },
  {
    title: 'Cash Flow Prediction',
    description: 'Predicted cash shortage in 45 days. Recommend accelerating receivables collection.',
    confidence: 91,
    icon: 'pi pi-chart-line',
    color: '#2196F3'
  }
])

const performanceMetrics = ref([
  {
    name: 'Revenue Target',
    current: '$125K',
    target: '$160K',
    progress: 78
  },
  {
    name: 'Expense Control',
    current: '$87.5K',
    target: '$100K',
    progress: 87
  },
  {
    name: 'Profit Margin',
    current: '30%',
    target: '35%',
    progress: 86
  },
  {
    name: 'Customer Satisfaction',
    current: '4.2/5',
    target: '4.5/5',
    progress: 93
  }
])

const recentTransactions = ref([
  { 
    date: '2023-11-15', 
    description: 'Client Payment - Project X', 
    amount: 12500,
    category: 'Revenue'
  },
  { 
    date: '2023-11-14', 
    description: 'Office Rent Payment', 
    amount: -2500,
    category: 'Expense'
  },
  { 
    date: '2023-11-13', 
    description: 'Software Subscription', 
    amount: -499,
    category: 'Technology'
  },
  { 
    date: '2023-11-12', 
    description: 'Consulting Services', 
    amount: 3500,
    category: 'Revenue'
  },
  { 
    date: '2023-11-11', 
    description: 'Team Building Event', 
    amount: -320,
    category: 'HR'
  }
])

const predictions = ref([
  {
    title: 'Next Month Revenue',
    value: '$142K',
    timeframe: '30 days',
    accuracy: 89
  },
  {
    title: 'Quarterly Profit',
    value: '$125K',
    timeframe: '90 days',
    accuracy: 82
  },
  {
    title: 'Annual Growth',
    value: '18.5%',
    timeframe: '12 months',
    accuracy: 76
  }
])

const chartFilters = ref({
  dateRange: null,
  categories: []
})

const categoryOptions = ref([
  { label: 'Revenue', value: 'revenue' },
  { label: 'Expenses', value: 'expenses' },
  { label: 'Profit', value: 'profit' }
])

// Computed
const connectionSeverity = computed(() => {
  switch (connectionStatus.value) {
    case 'Connected': return 'success'
    case 'Connecting': return 'warning'
    case 'Disconnected': return 'danger'
    default: return 'info'
  }
})

// Methods
const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(value)
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric'
  })
}

const initRevenueChart = () => {
  if (!revenueChart.value) return
  
  const ctx = revenueChart.value.getContext('2d')
  if (!ctx) return
  
  chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
      datasets: [
        {
          label: 'Revenue',
          data: [65000, 72000, 68000, 78000, 85000, 92000, 88000, 95000, 102000, 98000, 105000, 125000],
          borderColor: '#4CAF50',
          backgroundColor: 'rgba(76, 175, 80, 0.1)',
          tension: 0.4,
          fill: true
        },
        {
          label: 'Expenses',
          data: [45000, 48000, 52000, 55000, 58000, 62000, 65000, 68000, 72000, 75000, 82000, 87500],
          borderColor: '#FF6B6B',
          backgroundColor: 'rgba(255, 107, 107, 0.1)',
          tension: 0.4,
          fill: true
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top'
        },
        tooltip: {
          mode: 'index',
          intersect: false
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: function(value) {
              return '$' + new Intl.NumberFormat('en-US').format(value as number)
            }
          }
        }
      },
      interaction: {
        mode: 'nearest',
        axis: 'x',
        intersect: false
      }
    }
  })
}

const refreshData = async () => {
  loading.value = true
  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    // Update KPIs with new data
    kpis.value = kpis.value.map(kpi => ({
      ...kpi,
      value: Math.floor(kpi.value * (0.95 + Math.random() * 0.1)),
      trend: kpi.trend * (0.8 + Math.random() * 0.4),
      progress: Math.min(100, kpi.progress + (Math.random() - 0.5) * 10)
    }))
    
    // Update chart data
    if (chart) {
      chart.data.datasets[0].data = chart.data.datasets[0].data.map(value => 
        Math.floor((value as number) * (0.95 + Math.random() * 0.1))
      )
      chart.update()
    }
  } finally {
    loading.value = false
  }
}

const exportDashboard = () => {
  const data = {
    kpis: kpis.value,
    transactions: recentTransactions.value,
    insights: aiInsights.value,
    timestamp: new Date().toISOString()
  }
  
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `bi-dashboard-${new Date().toISOString().split('T')[0]}.json`
  a.click()
  URL.revokeObjectURL(url)
}

const expandChart = () => {
  // Implement chart expansion logic
  console.log('Expanding chart')
}

const viewAllInsights = () => {
  // Navigate to insights page
  console.log('Viewing all insights')
}

const viewAllTransactions = () => {
  // Navigate to transactions page
  console.log('Viewing all transactions')
}

const applyFilters = () => {
  // Apply chart filters
  showChartFilters.value = false
  console.log('Applying filters:', chartFilters.value)
}

const resetFilters = () => {
  chartFilters.value = {
    dateRange: null,
    categories: []
  }
}

// Watch for time range changes
watch(timeRange, async (newRange) => {
  console.log('Time range changed to:', newRange)
  await refreshData()
})

// Lifecycle
onMounted(() => {
  initRevenueChart()
  aiStore.connectRealTime()
})

onUnmounted(() => {
  if (chart) {
    chart.destroy()
  }
  aiStore.disconnectRealTime()
})
</script>

<style scoped>
.business-intelligence {
  padding: 1.5rem;
  background: var(--surface-ground);
  min-height: 100vh;
}

.bi-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding: 1rem;
  background: var(--surface-card);
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.bi-title {
  margin: 0;
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-color);
}

.header-controls {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.kpi-card {
  transition: transform 0.2s;
}

.kpi-card:hover {
  transform: translateY(-2px);
}

.kpi-content {
  padding: 1.5rem;
}

.kpi-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.kpi-label {
  color: var(--text-color-secondary);
  font-size: 0.875rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.kpi-value {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--text-color);
  margin-top: 0.5rem;
}

.kpi-trend-icon {
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
}

.kpi-trend-icon.positive {
  background: rgba(76, 175, 80, 0.1);
  color: #4CAF50;
}

.kpi-trend-icon.negative {
  background: rgba(244, 67, 54, 0.1);
  color: #F44336;
}

.kpi-trend {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.trend-value {
  font-weight: 600;
  font-size: 0.875rem;
}

.trend-period {
  color: var(--text-color-secondary);
  font-size: 0.875rem;
}

.kpi-progress {
  height: 0.5rem;
}

.analytics-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.chart-card {
  min-height: 400px;
}

.chart-controls {
  display: flex;
  gap: 0.5rem;
}

.chart-container {
  position: relative;
  height: 300px;
  padding: 1rem;
}

.revenue-chart {
  width: 100%;
  height: 100%;
}

.insights-card {
  min-height: 400px;
}

.insights-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem;
}

.insight-item {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background: var(--surface-50);
  border-radius: 8px;
  border: 1px solid var(--surface-border);
}

.insight-icon {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  background: var(--surface-100);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  flex-shrink: 0;
}

.insight-content {
  flex: 1;
}

.insight-title {
  margin: 0 0 0.5rem 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-color);
}

.insight-description {
  margin: 0 0 0.75rem 0;
  color: var(--text-color-secondary);
  font-size: 0.875rem;
  line-height: 1.4;
}

.insight-confidence {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.confidence-label {
  font-size: 0.75rem;
  color: var(--text-color-secondary);
  font-weight: 500;
}

.confidence-bar {
  flex: 1;
  height: 0.25rem;
}

.confidence-value {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-color);
}

.secondary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 1.5rem;
}

.performance-metrics {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem;
}

.metric-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: var(--surface-50);
  border-radius: 6px;
}

.metric-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.metric-name {
  font-weight: 600;
  color: var(--text-color);
}

.metric-target {
  font-size: 0.75rem;
  color: var(--text-color-secondary);
}

.metric-progress {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  min-width: 120px;
}

.metric-value {
  font-weight: 600;
  color: var(--text-color);
  font-size: 0.875rem;
}

.predictions-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem;
}

.prediction-item {
  padding: 1rem;
  background: var(--surface-50);
  border-radius: 8px;
  border: 1px solid var(--surface-border);
}

.prediction-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.prediction-title {
  font-weight: 600;
  color: var(--text-color);
}

.prediction-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-color);
  margin-bottom: 0.75rem;
}

.prediction-accuracy {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.accuracy-label {
  font-size: 0.75rem;
  color: var(--text-color-secondary);
  font-weight: 500;
}

.accuracy-bar {
  flex: 1;
  height: 0.25rem;
}

.accuracy-value {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-color);
}

.filter-options {
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
  .business-intelligence {
    padding: 1rem;
  }
  
  .bi-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .header-controls {
    flex-direction: column;
    width: 100%;
  }
  
  .kpi-grid {
    grid-template-columns: 1fr;
  }
  
  .analytics-grid {
    grid-template-columns: 1fr;
  }
  
  .secondary-grid {
    grid-template-columns: 1fr;
  }
}

@media (min-width: 769px) and (max-width: 1024px) {
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
