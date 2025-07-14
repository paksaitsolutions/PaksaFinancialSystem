<template>
  <div class="department-analysis">
    <div class="chart-container">
      <apexchart
        type="bar"
        height="350"
        :options="chartOptions"
        :series="chartSeries"
      ></apexchart>
    </div>
    <div class="table-container">
      <table class="department-table">
        <thead>
          <tr>
            <th>Department</th>
            <th>Budgeted</th>
            <th>Actual</th>
            <th>Variance</th>
            <th>Variance %</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="dept in data" :key="dept.id">
            <td>{{ dept.name }}</td>
            <td>{{ formatValue(dept.budgeted) }}</td>
            <td>{{ formatValue(dept.actual) }}</td>
            <td :class="{ negative: dept.variance < 0 }">
              {{ formatValue(dept.variance) }}
            </td>
            <td :class="{ negative: dept.variance_percentage < 0 }">
              {{ formatPercentage(dept.variance_percentage) }}
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

const chartSeries = computed(() => [{
  name: 'Budgeted',
  data: props.data.map(d => d.budgeted)
}, {
  name: 'Actual',
  data: props.data.map(d => d.actual)
}])

const chartOptions = computed(() => ({
  chart: {
    type: 'bar',
    height: 350,
    stacked: true,
    toolbar: {
      show: true
    }
  },
  plotOptions: {
    bar: {
      horizontal: true,
      borderRadius: 4,
      dataLabels: {
        position: 'top'
      }
    }
  },
  dataLabels: {
    enabled: true,
    offsetX: -6,
    style: {
      fontSize: '12px',
      colors: ['#fff']
    }
  },
  stroke: {
    show: true,
    width: 1,
    colors: ['#fff']
  },
  xaxis: {
    categories: props.data.map(d => d.name),
    labels: {
      formatter: (val: string) => val
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
  tooltip: {
    y: {
      formatter: (val: number) => formatValue(val)
    }
  },
  fill: {
    opacity: 1
  },
  legend: {
    position: 'top',
    horizontalAlign: 'left',
    offsetX: 40
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

const formatPercentage = (value: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'percent',
    minimumFractionDigits: 1,
    maximumFractionDigits: 1
  }).format(value / 100)
}
</script>

<style scoped>
.department-analysis {
  background: var(--card-background);
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: var(--card-shadow);
}

.chart-container {
  margin-bottom: 1.5rem;
}

.department-table {
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
  .department-analysis {
    padding: 1rem;
  }
  
  .chart-container {
    height: 400px;
  }
  
  .department-table {
    display: block;
    overflow-x: auto;
  }
  
  th,
  td {
    padding: 0.75rem;
  }
}
</style>
