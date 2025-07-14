<template>
  <div class="trend-analysis">
    <div class="chart-container">
      <apexchart
        type="line"
        height="350"
        :options="chartOptions"
        :series="chartSeries"
      ></apexchart>
    </div>
    <div class="controls">
      <div class="period-selector">
        <label for="period">Period:</label>
        <select v-model="selectedPeriod" id="period">
          <option value="month">Monthly</option>
          <option value="quarter">Quarterly</option>
          <option value="year">Yearly</option>
        </select>
      </div>
      <div class="months-selector">
        <label for="months">Months:</label>
        <select v-model="selectedMonths" id="months">
          <option value="3">3 Months</option>
          <option value="6">6 Months</option>
          <option value="12">12 Months</option>
          <option value="24">24 Months</option>
        </select>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ApexCharts } from 'apexcharts'
import { BudgetTrendData } from '@/types/budget'

interface Props {
  data: BudgetTrendData[]
  loading?: boolean
}

const props = defineProps<Props>()

const selectedPeriod = ref('month')
const selectedMonths = ref('12')

const chartSeries = computed(() => [{
  name: 'Budgeted',
  data: props.data.map(d => d.budgeted_amount)
}, {
  name: 'Actual',
  data: props.data.map(d => d.actual_amount)
}])

const chartOptions = computed(() => ({
  chart: {
    type: 'line',
    height: 350,
    zoom: {
      enabled: false
    }
  },
  dataLabels: {
    enabled: false
  },
  stroke: {
    curve: 'smooth'
  },
  xaxis: {
    categories: props.data.map(d => d.period),
    title: {
      text: 'Period'
    }
  },
  yaxis: {
    title: {
      text: 'Amount ($)',
      style: {
        color: '#787878'
      }
    }
  },
  legend: {
    position: 'top',
    horizontalAlign: 'left',
    offsetX: 40
  },
  tooltip: {
    y: {
      formatter: (val: number) => formatValue(val)
    }
  }
}))

const formatValue = (value: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value)
}

watch([selectedPeriod, selectedMonths], () => {
  // Handle period and months selection changes
  // This would typically trigger a data refetch from the API
})
</script>

<style scoped>
.trend-analysis {
  background: var(--card-background);
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: var(--card-shadow);
}

.chart-container {
  margin-bottom: 1.5rem;
}

.controls {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.period-selector,
.months-selector {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

label {
  color: var(--text-color);
  font-weight: 500;
}

select {
  padding: 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  background: white;
  color: var(--text-color);
}

@media (max-width: 768px) {
  .trend-analysis {
    padding: 1rem;
  }
  
  .chart-container {
    height: 400px;
  }
  
  .controls {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>
