<template>
  <div class="project-analysis">
    <div class="chart-container">
      <apexchart
        type="donut"
        height="350"
        :options="chartOptions"
        :series="chartSeries"
      ></apexchart>
    </div>
    <div class="table-container">
      <table class="project-table">
        <thead>
          <tr>
            <th>Project</th>
            <th>Budgeted</th>
            <th>Actual</th>
            <th>Variance</th>
            <th>Variance %</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="proj in data" :key="proj.id">
            <td>{{ proj.name }}</td>
            <td>{{ formatValue(proj.budgeted) }}</td>
            <td>{{ formatValue(proj.actual) }}</td>
            <td :class="{ negative: proj.variance < 0 }">
              {{ formatValue(proj.variance) }}
            </td>
            <td :class="{ negative: proj.variance_percentage < 0 }">
              {{ formatPercentage(proj.variance_percentage) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ApexCharts } from 'apexcharts'
import { BudgetAnalysisData } from '@/types/budget'

interface Props {
  data: BudgetAnalysisData[]
  loading?: boolean
}

const props = defineProps<Props>()

const chartSeries = computed(() => {
  return props.data.map(d => d.budgeted)
})

const chartOptions = computed(() => ({
  chart: {
    type: 'donut',
    height: 350,
    toolbar: {
      show: true
    }
  },
  labels: props.data.map(d => d.name),
  responsive: [{
    breakpoint: 480,
    options: {
      chart: {
        width: 200
      },
      legend: {
        position: 'bottom'
      }
    }
  }],
  legend: {
    position: 'bottom',
    fontSize: '14px',
    fontFamily: 'Helvetica, Arial, sans-serif',
    labels: {
      colors: '#787878'
    }
  },
  dataLabels: {
    enabled: true,
    formatter: (val: number, opts) => {
      return formatValue(val)
    }
  },
  colors: ['#00B8D9', '#00A34F', '#FFA421', '#FF4444', '#7C5DFA']
}))

const formatValue = (value: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value)
}

const formatPercentage = (value: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'percent',
    minimumFractionDigits: 1,
    maximumFractionDigits: 1
  }).format(value / 100)
}
</script>

<style scoped>
.project-analysis {
  background: var(--card-background);
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: var(--card-shadow);
}

.chart-container {
  margin-bottom: 1.5rem;
}

.project-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

th,
td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

th {
  background: var(--table-header-background);
  color: var(--text-color);
  font-weight: 600;
}

.negative {
  color: #ff4444;
}

@media (max-width: 768px) {
  .project-analysis {
    padding: 1rem;
  }
  
  .chart-container {
    height: 400px;
  }
  
  .project-table {
    display: block;
    overflow-x: auto;
  }
  
  th,
  td {
    padding: 0.75rem;
  }
}
</style>
