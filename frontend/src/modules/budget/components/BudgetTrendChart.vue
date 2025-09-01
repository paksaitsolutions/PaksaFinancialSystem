<template>
  <Card>
    <template #header>
      <h3 class="p-4 m-0">Budget Trend Analysis</h3>
    </template>
    <template #content>
      <div v-if="data && data.length > 0">
        <canvas ref="chartCanvas" width="400" height="200"></canvas>
      </div>
      <div v-else class="text-center p-4">
        <i class="pi pi-chart-line text-6xl text-500"></i>
        <p class="text-xl mt-2">No trend data available</p>
      </div>
    </template>
  </Card>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

interface TrendData {
  period: string
  budget: number
  actual: number
}

interface Props {
  data: TrendData[]
}

const props = defineProps<Props>()
const chartCanvas = ref<HTMLCanvasElement>()
let chart: Chart | null = null

const createChart = () => {
  if (!chartCanvas.value || !props.data?.length) return

  const ctx = chartCanvas.value.getContext('2d')
  if (!ctx) return

  if (chart) {
    chart.destroy()
  }

  chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: props.data.map(d => d.period),
      datasets: [
        {
          label: 'Budget',
          data: props.data.map(d => d.budget),
          borderColor: '#2196F3',
          backgroundColor: 'rgba(33, 150, 243, 0.1)',
          tension: 0.4
        },
        {
          label: 'Actual',
          data: props.data.map(d => d.actual),
          borderColor: '#4CAF50',
          backgroundColor: 'rgba(76, 175, 80, 0.1)',
          tension: 0.4
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
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
      plugins: {
        tooltip: {
          callbacks: {
            label: function(context) {
              return context.dataset.label + ': $' + 
                new Intl.NumberFormat('en-US').format(context.parsed.y)
            }
          }
        }
      }
    }
  })
}

onMounted(() => {
  createChart()
})

watch(() => props.data, () => {
  createChart()
}, { deep: true })
</script>