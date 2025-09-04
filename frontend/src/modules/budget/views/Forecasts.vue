<template>
  <div class="budget-forecasts">
    <div class="dashboard-header">
      <h1>Budget Forecasting</h1>
      <p>Create financial forecasts and scenario planning for future budget periods.</p>
    </div>

    <div class="forecasting-content">
      <!-- Forecast Controls -->
      <Card class="controls-card">
        <template #title>
          <div class="card-title">
            <i class="pi pi-chart-line"></i>
            <span>Forecast Parameters</span>
          </div>
        </template>
        <template #content>
          <div class="grid">
            <div class="col-12 md:col-3">
              <div class="field">
                <label>Forecast Period</label>
                <Dropdown v-model="forecastPeriod" :options="periodOptions" option-label="label" option-value="value" />
              </div>
            </div>
            <div class="col-12 md:col-3">
              <div class="field">
                <label>Forecast Method</label>
                <Dropdown v-model="forecastMethod" :options="methodOptions" option-label="label" option-value="value" />
              </div>
            </div>
            <div class="col-12 md:col-3">
              <div class="field">
                <label>Growth Rate (%)</label>
                <InputNumber v-model="growthRate" :min="0" :max="100" suffix="%" />
              </div>
            </div>
            <div class="col-12 md:col-3">
              <div class="field">
                <label>&nbsp;</label>
                <Button label="Generate Forecast" icon="pi pi-refresh" @click="generateForecast" class="w-full" />
              </div>
            </div>
          </div>
        </template>
      </Card>

      <!-- Forecast Chart -->
      <Card class="chart-card">
        <template #title>
          <div class="card-title-with-action">
            <span>Budget Forecast Trend</span>
            <div class="chart-controls">
              <Button label="Historical" :class="{ 'p-button-outlined': !showHistorical }" @click="toggleHistorical" size="small" />
              <Button label="Scenarios" icon="pi pi-sitemap" @click="showScenarios = true" size="small" />
            </div>
          </div>
        </template>
        <template #content>
          <Chart type="line" :data="forecastChartData" :options="forecastChartOptions" />
        </template>
      </Card>

      <!-- Forecast Details -->
      <div class="forecast-details">
        <Card class="forecast-table-card">
          <template #title>
            <span>Detailed Forecast Breakdown</span>
          </template>
          <template #content>
            <DataTable :value="forecastDetails" responsive-layout="scroll">
              <Column field="period" header="Period" sortable />
              <Column field="category" header="Category" sortable />
              <Column field="historical" header="Historical" sortable>
                <template #body="{ data }">
                  <span class="amount historical">{{ formatCurrency(data.historical) }}</span>
                </template>
              </Column>
              <Column field="forecast" header="Forecast" sortable>
                <template #body="{ data }">
                  <span class="amount forecast">{{ formatCurrency(data.forecast) }}</span>
                </template>
              </Column>
              <Column field="variance" header="Variance" sortable>
                <template #body="{ data }">
                  <span class="amount variance" :class="data.variance >= 0 ? 'positive' : 'negative'">
                    {{ formatCurrency(data.variance) }}
                  </span>
                </template>
              </Column>
              <Column field="confidence" header="Confidence" sortable>
                <template #body="{ data }">
                  <ProgressBar :value="data.confidence" :class="getConfidenceClass(data.confidence)" />
                  <span class="confidence-text">{{ data.confidence }}%</span>
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>

        <Card class="summary-card">
          <template #title>
            <span>Forecast Summary</span>
          </template>
          <template #content>
            <div class="forecast-summary">
              <div class="summary-item">
                <label>Total Forecast</label>
                <span class="amount forecast">{{ formatCurrency(forecastSummary.total) }}</span>
              </div>
              <div class="summary-item">
                <label>Growth Rate</label>
                <span class="percentage">{{ forecastSummary.growthRate }}%</span>
              </div>
              <div class="summary-item">
                <label>Confidence Level</label>
                <span class="confidence">{{ forecastSummary.confidence }}%</span>
              </div>
              <div class="summary-item">
                <label>Risk Level</label>
                <Tag :value="forecastSummary.riskLevel" :severity="getRiskSeverity(forecastSummary.riskLevel)" />
              </div>
            </div>
            
            <div class="forecast-actions">
              <Button label="Save Forecast" icon="pi pi-save" @click="saveForecast" />
              <Button label="Export Report" icon="pi pi-download" outlined @click="exportForecast" />
              <Button label="Create Budget" icon="pi pi-plus" severity="success" @click="createBudgetFromForecast" />
            </div>
          </template>
        </Card>
      </div>
    </div>

    <!-- Scenario Planning Dialog -->
    <Dialog v-model:visible="showScenarios" header="Scenario Planning" :style="{ width: '80vw' }" modal>
      <div class="scenarios-content">
        <div class="scenario-tabs">
          <TabView>
            <TabPanel header="Optimistic">
              <div class="scenario-details">
                <p>Best case scenario with 15% growth rate</p>
                <Chart type="line" :data="optimisticScenario" :options="scenarioChartOptions" />
              </div>
            </TabPanel>
            <TabPanel header="Realistic">
              <div class="scenario-details">
                <p>Most likely scenario with 8% growth rate</p>
                <Chart type="line" :data="realisticScenario" :options="scenarioChartOptions" />
              </div>
            </TabPanel>
            <TabPanel header="Pessimistic">
              <div class="scenario-details">
                <p>Conservative scenario with 3% growth rate</p>
                <Chart type="line" :data="pessimisticScenario" :options="scenarioChartOptions" />
              </div>
            </TabPanel>
          </TabView>
        </div>
      </div>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'

// PrimeVue Components
import Card from 'primevue/card'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import Dropdown from 'primevue/dropdown'
import InputNumber from 'primevue/inputnumber'
import Chart from 'primevue/chart'
import ProgressBar from 'primevue/progressbar'
import Dialog from 'primevue/dialog'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'

const toast = useToast()

const forecastPeriod = ref('next_year')
const forecastMethod = ref('linear')
const growthRate = ref(8)
const showHistorical = ref(true)
const showScenarios = ref(false)

const periodOptions = [
  { label: 'Next Quarter', value: 'next_quarter' },
  { label: 'Next Year', value: 'next_year' },
  { label: 'Next 2 Years', value: 'next_2_years' },
  { label: 'Next 5 Years', value: 'next_5_years' }
]

const methodOptions = [
  { label: 'Linear Regression', value: 'linear' },
  { label: 'Exponential Smoothing', value: 'exponential' },
  { label: 'Moving Average', value: 'moving_average' },
  { label: 'Seasonal Decomposition', value: 'seasonal' }
]

const forecastDetails = ref([
  { period: 'Q1 2024', category: 'Marketing', historical: 45000, forecast: 48600, variance: 3600, confidence: 85 },
  { period: 'Q1 2024', category: 'Operations', historical: 65000, forecast: 70200, variance: 5200, confidence: 90 },
  { period: 'Q1 2024', category: 'IT', historical: 35000, forecast: 37800, variance: 2800, confidence: 80 },
  { period: 'Q2 2024', category: 'Marketing', historical: 50000, forecast: 54000, variance: 4000, confidence: 82 },
  { period: 'Q2 2024', category: 'Operations', historical: 70000, forecast: 75600, variance: 5600, confidence: 88 },
  { period: 'Q2 2024', category: 'IT', historical: 40000, forecast: 43200, variance: 3200, confidence: 78 }
])

const forecastSummary = ref({
  total: 1250000,
  growthRate: 8.5,
  confidence: 85,
  riskLevel: 'Medium'
})

const forecastChartData = ref({
  labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
  datasets: [
    {
      label: 'Historical',
      data: [45000, 48000, 52000, 49000, 55000, 58000, 60000, 62000, 59000, 65000, 68000, 70000],
      borderColor: '#42A5F5',
      backgroundColor: 'rgba(66, 165, 245, 0.1)',
      fill: true
    },
    {
      label: 'Forecast',
      data: [null, null, null, null, null, null, null, null, 64000, 69000, 74000, 79000],
      borderColor: '#FFA726',
      backgroundColor: 'rgba(255, 167, 38, 0.1)',
      borderDash: [5, 5],
      fill: true
    }
  ]
})

const forecastChartOptions = ref({
  responsive: true,
  plugins: {
    legend: { position: 'top' },
    tooltip: {
      callbacks: {
        label: (context) => `${context.dataset.label}: $${context.parsed.y.toLocaleString()}`
      }
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: { callback: (value) => '$' + value.toLocaleString() }
    }
  }
})

const optimisticScenario = ref({
  labels: ['Q1', 'Q2', 'Q3', 'Q4'],
  datasets: [{
    label: 'Optimistic (15% growth)',
    data: [575000, 661250, 760438, 874504],
    borderColor: '#66BB6A',
    backgroundColor: 'rgba(102, 187, 106, 0.1)',
    fill: true
  }]
})

const realisticScenario = ref({
  labels: ['Q1', 'Q2', 'Q3', 'Q4'],
  datasets: [{
    label: 'Realistic (8% growth)',
    data: [540000, 583200, 629856, 680285],
    borderColor: '#42A5F5',
    backgroundColor: 'rgba(66, 165, 245, 0.1)',
    fill: true
  }]
})

const pessimisticScenario = ref({
  labels: ['Q1', 'Q2', 'Q3', 'Q4'],
  datasets: [{
    label: 'Pessimistic (3% growth)',
    data: [515000, 530450, 546364, 562754],
    borderColor: '#EF5350',
    backgroundColor: 'rgba(239, 83, 80, 0.1)',
    fill: true
  }]
})

const scenarioChartOptions = ref({
  responsive: true,
  plugins: { legend: { position: 'top' } },
  scales: {
    y: {
      beginAtZero: true,
      ticks: { callback: (value) => '$' + value.toLocaleString() }
    }
  }
})

const formatCurrency = (amount) => 
  new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount)

const getConfidenceClass = (confidence) => {
  if (confidence >= 80) return 'progress-success'
  if (confidence >= 60) return 'progress-warning'
  return 'progress-danger'
}

const getRiskSeverity = (risk) => {
  switch (risk) {
    case 'Low': return 'success'
    case 'Medium': return 'warning'
    case 'High': return 'danger'
    default: return 'info'
  }
}

const toggleHistorical = () => {
  showHistorical.value = !showHistorical.value
}

const generateForecast = () => {
  toast.add({ severity: 'info', summary: 'Generating Forecast', detail: 'Forecast is being calculated...' })
}

const saveForecast = () => {
  toast.add({ severity: 'success', summary: 'Forecast Saved', detail: 'Forecast has been saved successfully' })
}

const exportForecast = () => {
  toast.add({ severity: 'info', summary: 'Exporting', detail: 'Forecast report is being exported...' })
}

const createBudgetFromForecast = () => {
  toast.add({ severity: 'success', summary: 'Budget Created', detail: 'New budget created from forecast data' })
}

onMounted(() => {
  generateForecast()
})
</script>

<style scoped>
.budget-forecasts {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard-header {
  margin-bottom: 2rem;
}

.dashboard-header h1 {
  font-size: 2rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 0.5rem 0;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
}

.card-title-with-action {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.chart-controls {
  display: flex;
  gap: 0.5rem;
}

.controls-card {
  margin-bottom: 2rem;
}

.chart-card {
  margin-bottom: 2rem;
}

.field {
  margin-bottom: 1rem;
}

.field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.forecast-details {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1.5rem;
}

.forecast-summary {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-bottom: 2rem;
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 0.5rem;
}

.summary-item label {
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 600;
}

.amount.historical { color: #3b82f6; }
.amount.forecast { color: #f59e0b; }
.amount.variance.positive { color: #10b981; }
.amount.variance.negative { color: #ef4444; }

.percentage { color: #8b5cf6; font-weight: 600; }
.confidence { color: #10b981; font-weight: 600; }

.confidence-text {
  margin-left: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
}

.forecast-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.scenario-details {
  padding: 1rem 0;
}

.progress-success :deep(.p-progressbar-value) { background: #10b981; }
.progress-warning :deep(.p-progressbar-value) { background: #f59e0b; }
.progress-danger :deep(.p-progressbar-value) { background: #ef4444; }

@media (max-width: 768px) {
  .forecast-details {
    grid-template-columns: 1fr;
  }
  
  .forecast-summary {
    grid-template-columns: 1fr;
  }
  
  .chart-controls {
    flex-direction: column;
  }
}
</style>