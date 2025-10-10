<template>
  <div class="cash-flow-analytics">
    <h2>Cash Flow Analytics</h2>
    
    <div class="grid">
      <div class="col-12 lg:col-8">
        <Card>
          <template #title>Cash Flow Forecast (30 Days)</template>
          <template #content>
            <Chart type="line" :data="forecastChartData" :options="chartOptions" class="h-20rem" />
          </template>
        </Card>
      </div>
      
      <div class="col-12 lg:col-4">
        <Card>
          <template #title>Liquidity Ratios</template>
          <template #content>
            <div class="liquidity-metrics">
              <div v-for="metric in liquidityMetrics" :key="metric.name" class="metric-item">
                <div class="metric-name">{{ metric.name }}</div>
                <div class="metric-value" :class="getMetricClass(metric.value, metric.threshold)">
                  {{ metric.value }}
                </div>
              </div>
            </div>
          </template>
        </Card>
      </div>
    </div>

    <div class="grid mt-4">
      <div class="col-12">
        <Card>
          <template #title>Variance Analysis</template>
          <template #content>
            <DataTable :value="varianceData">
              <Column field="period" header="Period"></Column>
              <Column field="budgeted_inflow" header="Budgeted Inflow">
                <template #body="{ data }">
                  {{ formatCurrency(data.budgeted_inflow) }}
                </template>
              </Column>
              <Column field="actual_inflow" header="Actual Inflow">
                <template #body="{ data }">
                  {{ formatCurrency(data.actual_inflow) }}
                </template>
              </Column>
              <Column field="variance" header="Variance">
                <template #body="{ data }">
                  <span :class="data.variance >= 0 ? 'text-green-600' : 'text-red-600'">
                    {{ formatCurrency(data.variance) }}
                  </span>
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { cashService } from '@/api/cashService'
import Chart from 'primevue/chart'

const forecastChartData = ref({})
const liquidityMetrics = ref([])
const varianceData = ref([])

const chartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    y: {
      beginAtZero: true,
      ticks: {
        callback: function(value: number) {
          return '$' + (value / 1000).toFixed(0) + 'K'
        }
      }
    }
  }
})

const loadAnalytics = async () => {
  try {
    const [forecast, liquidity, variance] = await Promise.all([
      cashService.getCashFlowForecast(30),
      fetch('/api/v1/cash/analytics/liquidity').then(r => r.json()),
      fetch('/api/v1/cash/analytics/variance').then(r => r.json())
    ])

    forecastChartData.value = {
      labels: forecast.map(f => f.period),
      datasets: [{
        label: 'Projected Balance',
        data: forecast.map(f => f.ending_balance),
        borderColor: '#3B82F6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4
      }]
    }

    liquidityMetrics.value = [
      { name: 'Current Ratio', value: liquidity.current_ratio, threshold: 2.0 },
      { name: 'Quick Ratio', value: liquidity.quick_ratio, threshold: 1.5 },
      { name: 'Cash Ratio', value: liquidity.cash_ratio, threshold: 1.0 }
    ]

    varianceData.value = [variance]
  } catch (error) {
    console.error('Error loading analytics:', error)
  }
}

const getMetricClass = (value: number, threshold: number) => {
  return value >= threshold ? 'text-green-600' : 'text-red-600'
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}

onMounted(() => {
  loadAnalytics()
})
</script>

<style scoped>
.liquidity-metrics {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.metric-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  border: 1px solid var(--surface-border);
  border-radius: 6px;
}

.metric-name {
  font-weight: 500;
}

.metric-value {
  font-weight: 700;
  font-size: 1.1rem;
}
</style>