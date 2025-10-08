<template>
  <div class="grid">
    <div class="col-12">
      <div class="flex flex-column md:flex-row justify-content-between align-items-start md:align-items-center mb-4 gap-3">
        <div>
          <h1>Budget Forecasting</h1>
          <p class="text-color-secondary">Create financial forecasts and scenario planning for future budget periods.</p>
        </div>
        <div>
          <Button label="New Forecast" icon="pi pi-plus" class="p-button-success" @click="showNewForecastDialog" />
        </div>
      </div>
    </div>

    <!-- Forecast Controls -->
    <div class="col-12">
      <Card>
        <template #title>
          <div class="flex align-items-center gap-2">
            <i class="pi pi-chart-line"></i>
            <span>Forecast Parameters</span>
          </div>
        </template>
        <template #content>
          <div class="grid">
            <div class="col-12 md:col-3">
              <div class="field">
                <label for="period">Forecast Period</label>
                <Dropdown id="period" v-model="forecastPeriod" :options="periodOptions" optionLabel="label" optionValue="value" />
              </div>
            </div>
            <div class="col-12 md:col-3">
              <div class="field">
                <label for="method">Forecast Method</label>
                <Dropdown id="method" v-model="forecastMethod" :options="methodOptions" optionLabel="label" optionValue="value" />
              </div>
            </div>
            <div class="col-12 md:col-3">
              <div class="field">
                <label for="growth">Growth Rate (%)</label>
                <InputNumber id="growth" v-model="growthRate" :min="0" :max="100" suffix="%" />
              </div>
            </div>
            <div class="col-12 md:col-3">
              <div class="field">
                <label>&nbsp;</label>
                <Button label="Generate Forecast" icon="pi pi-refresh" @click="generateForecast" class="w-full" :loading="loading" />
              </div>
            </div>
          </div>
        </template>
      </Card>
    </div>

    <!-- Forecast Chart -->
    <div class="col-12">
      <Card>
        <template #title>
          <div class="flex justify-content-between align-items-center w-full">
            <span>Budget Forecast Trend</span>
            <div class="flex gap-2">
              <Button label="Historical" :outlined="!showHistorical" @click="toggleHistorical" size="small" />
              <Button label="Scenarios" icon="pi pi-sitemap" @click="showScenarios = true" size="small" />
            </div>
          </div>
        </template>
        <template #content>
          <Chart type="line" :data="forecastChartData" :options="forecastChartOptions" />
        </template>
      </Card>
    </div>

    <!-- Forecast Details -->
    <div class="col-12 lg:col-8">
      <Card>
        <template #title>
          <span>Detailed Forecast Breakdown</span>
        </template>
        <template #content>
          <DataTable :value="forecastDetails" responsiveLayout="scroll" :loading="loading">
            <Column field="period" header="Period" :sortable="true" />
            <Column field="category" header="Category" :sortable="true" />
            <Column field="historical" header="Historical" :sortable="true">
              <template #body="{ data }">
                <span class="text-blue-600 font-medium">{{ formatCurrency(data.historical) }}</span>
              </template>
            </Column>
            <Column field="forecast" header="Forecast" :sortable="true">
              <template #body="{ data }">
                <span class="text-orange-600 font-medium">{{ formatCurrency(data.forecast) }}</span>
              </template>
            </Column>
            <Column field="variance" header="Variance" :sortable="true">
              <template #body="{ data }">
                <span :class="data.variance >= 0 ? 'text-green-600' : 'text-red-600'" class="font-medium">
                  {{ formatCurrency(data.variance) }}
                </span>
              </template>
            </Column>
            <Column field="confidence" header="Confidence" :sortable="true">
              <template #body="{ data }">
                <div class="flex align-items-center gap-2">
                  <ProgressBar :value="data.confidence" class="w-full" />
                  <span class="text-sm font-medium">{{ data.confidence }}%</span>
                </div>
              </template>
            </Column>
          </DataTable>
        </template>
      </Card>
    </div>

    <div class="col-12 lg:col-4">
      <Card>
        <template #title>
          <span>Forecast Summary</span>
        </template>
        <template #content>
          <div class="flex flex-column gap-3 mb-4">
            <div class="p-3 border-round surface-100">
              <div class="text-sm text-color-secondary mb-1">Total Forecast</div>
              <div class="text-xl font-bold text-orange-600">{{ formatCurrency(forecastSummary.total) }}</div>
            </div>
            <div class="p-3 border-round surface-100">
              <div class="text-sm text-color-secondary mb-1">Growth Rate</div>
              <div class="text-xl font-bold text-purple-600">{{ forecastSummary.growthRate }}%</div>
            </div>
            <div class="p-3 border-round surface-100">
              <div class="text-sm text-color-secondary mb-1">Confidence Level</div>
              <div class="text-xl font-bold text-green-600">{{ forecastSummary.confidence }}%</div>
            </div>
            <div class="p-3 border-round surface-100">
              <div class="text-sm text-color-secondary mb-1">Risk Level</div>
              <Tag :value="forecastSummary.riskLevel" :severity="getRiskSeverity(forecastSummary.riskLevel)" />
            </div>
          </div>
          
          <div class="flex flex-column gap-2">
            <Button label="Save Forecast" icon="pi pi-save" @click="saveForecast" class="w-full" />
            <Button label="Export Report" icon="pi pi-download" outlined @click="exportForecast" class="w-full" />
            <Button label="Create Budget" icon="pi pi-plus" severity="success" @click="createBudgetFromForecast" class="w-full" />
          </div>
        </template>
      </Card>
    </div>
  </div>

  <!-- Scenario Planning Dialog -->
  <Dialog v-model:visible="showScenarios" header="Scenario Planning" :style="{ width: '80vw' }" :modal="true">
    <TabView>
      <TabPanel header="Optimistic">
        <div class="p-3">
          <p class="mb-3">Best case scenario with 15% growth rate</p>
          <Chart type="line" :data="optimisticScenario" :options="scenarioChartOptions" />
        </div>
      </TabPanel>
      <TabPanel header="Realistic">
        <div class="p-3">
          <p class="mb-3">Most likely scenario with 8% growth rate</p>
          <Chart type="line" :data="realisticScenario" :options="scenarioChartOptions" />
        </div>
      </TabPanel>
      <TabPanel header="Pessimistic">
        <div class="p-3">
          <p class="mb-3">Conservative scenario with 3% growth rate</p>
          <Chart type="line" :data="pessimisticScenario" :options="scenarioChartOptions" />
        </div>
      </TabPanel>
    </TabView>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { budgetForecastService } from '@/api/budgetForecastService'

const toast = useToast()
const loading = ref(false)

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

const generateForecast = async () => {
  try {
    loading.value = true
    const result = await budgetForecastService.generateForecast(
      forecastPeriod.value,
      forecastMethod.value,
      growthRate.value
    )
    forecastDetails.value = result.forecast_details
    toast.add({ severity: 'success', summary: 'Forecast Generated', detail: 'Forecast has been calculated successfully' })
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to generate forecast' })
  } finally {
    loading.value = false
  }
}

const saveForecast = async () => {
  try {
    const forecastData = {
      name: `Forecast ${new Date().toLocaleDateString()}`,
      period: forecastPeriod.value,
      method: forecastMethod.value,
      growth_rate: growthRate.value,
      total_forecast: forecastSummary.value.total,
      confidence_level: forecastSummary.value.confidence,
      risk_level: forecastSummary.value.riskLevel,
      status: 'Active',
      forecast_details: forecastDetails.value
    }
    await budgetForecastService.createForecast(forecastData)
    toast.add({ severity: 'success', summary: 'Forecast Saved', detail: 'Forecast has been saved successfully' })
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to save forecast' })
  }
}

const exportForecast = () => {
  toast.add({ severity: 'info', summary: 'Exporting', detail: 'Forecast report is being exported...' })
}

const createBudgetFromForecast = () => {
  toast.add({ severity: 'success', summary: 'Budget Created', detail: 'New budget created from forecast data' })
}

const showNewForecastDialog = () => {
  toast.add({ severity: 'info', summary: 'New Forecast', detail: 'New forecast dialog would open here' })
}

onMounted(() => {
  generateForecast()
})
</script>

<style scoped>
.field {
  margin-bottom: 1rem;
}

.field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
}
</style>