<template>
  <div class="allocation-analysis">
    <div class="chart-container">
      <apexchart
        type="pie"
        height="350"
        :options="chartOptions"
        :series="chartSeries"
      ></apexchart>
    </div>
    <div class="table-container">
      <table class="allocation-table">
        <thead>
          <tr>
            <th>Department</th>
            <th>Amount</th>
            <th>Percentage</th>
            <th>Project</th>
            <th>Amount</th>
            <th>Percentage</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>
              <table class="inner-table">
                <tr v-for="dept in allocationData.department_allocations" :key="dept.department_id">
                  <td>{{ dept.department_id }}</td>
                  <td>{{ formatValue(dept.amount) }}</td>
                  <td>{{ dept.percentage.toFixed(1) }}%</td>
                </tr>
              </table>
            </td>
            <td colspan="3"></td>
          </tr>
          <tr>
            <td colspan="3"></td>
            <td>
              <table class="inner-table">
                <tr v-for="proj in allocationData.project_allocations" :key="proj.project_id">
                  <td>{{ proj.project_id }}</td>
                  <td>{{ formatValue(proj.amount) }}</td>
                  <td>{{ proj.percentage.toFixed(1) }}%</td>
                </tr>
              </table>
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
import { BudgetAllocationAnalysis } from '@/types/budget'

interface Props {
  data: BudgetAllocationAnalysis
  loading?: boolean
}

const props = defineProps<Props>()

const chartSeries = computed(() => {
  const deptSeries = props.data.department_allocations.map(d => d.amount)
  const projSeries = props.data.project_allocations.map(p => p.amount)
  return [...deptSeries, ...projSeries]
})

const chartOptions = computed(() => ({
  chart: {
    type: 'pie',
    height: 350,
    toolbar: {
      show: true
    }
  },
  labels: [
    ...props.data.department_allocations.map(d => `Dept ${d.department_id}`),
    ...props.data.project_allocations.map(p => `Proj ${p.project_id}`)
  ],
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
  colors: ['#00B8D9', '#00A34F', '#FFA421', '#FF4444', '#7C5DFA', '#4F5D75']
}))

const formatValue = (value: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value)
}
</script>

<style scoped>
.allocation-analysis {
  background: var(--card-background);
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: var(--card-shadow);
}

.chart-container {
  margin-bottom: 1.5rem;
}

.allocation-table {
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

.inner-table {
  width: 100%;
  border-collapse: collapse;
}

.inner-table td {
  padding: 0.5rem;
  border-bottom: 1px solid var(--border-color);
}

@media (max-width: 768px) {
  .allocation-analysis {
    padding: 1rem;
  }
  
  .chart-container {
    height: 400px;
  }
  
  .allocation-table {
    display: block;
    overflow-x: auto;
  }
  
  th,
  td {
    padding: 0.75rem;
  }
}
</style>
