<template>
  <Card>
    <template #header>
      <h3 class="p-4 m-0">Budget Allocation Analysis</h3>
    </template>
    <template #content>
      <div v-if="data && data.length > 0">
        <div class="grid">
          <div class="col-12 md:col-6">
            <canvas ref="chartCanvas" width="300" height="300"></canvas>
          </div>
          <div class="col-12 md:col-6">
            <div class="flex flex-column gap-3">
              <div
                v-for="item in data"
                :key="item.category"
                class="flex justify-content-between align-items-center p-3 border-round surface-border border-1"
              >
                <div>
                  <div class="font-semibold">{{ item.category }}</div>
                  <div class="text-sm text-500">
                    ${{ formatCurrency(item.amount) }} ({{ item.percentage.toFixed(1) }}%)
                  </div>
                </div>
                <Tag :value="`${item.percentage.toFixed(1)}%`" :style="{ backgroundColor: getColor(item.category), color: 'white' }" />
              </div>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="text-center p-4">
        <i class="pi pi-chart-pie text-6xl text-500"></i>
        <p class="text-xl mt-2">No allocation data available</p>
      </div>
    </template>
  </Card>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

interface AllocationData {
  category: string
  amount: number
  percentage: number
}

interface Props {
  data: AllocationData[]
}

const props = defineProps<Props>()
const chartCanvas = ref<HTMLCanvasElement>()
let chart: Chart | null = null

const colors = [
  '#2196F3', '#4CAF50', '#FF9800', '#F44336', '#9C27B0',
  '#00BCD4', '#FFEB3B', '#795548', '#607D8B', '#E91E63'
]

const createChart = () => {
  if (!chartCanvas.value || !props.data?.length) return

  const ctx = chartCanvas.value.getContext('2d')
  if (!ctx) return

  if (chart) {
    chart.destroy()
  }

  chart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: props.data.map(d => d.category),
      datasets: [{
        data: props.data.map(d => d.amount),
        backgroundColor: colors.slice(0, props.data.length),
        borderWidth: 2,
        borderColor: '#fff'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              const label = context.label || ''
              const value = context.parsed
              const percentage = ((value / props.data.reduce((sum, item) => sum + item.amount, 0)) * 100).toFixed(1)
              return `${label}: $${new Intl.NumberFormat('en-US').format(value)} (${percentage}%)`
            }
          }
        }
      }
    }
  })
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount)
}

const getColor = (category: string) => {
  const index = props.data.findIndex(item => item.category === category)
  return colors[index % colors.length]
}

onMounted(() => {
  createChart()
})

watch(() => props.data, () => {
  createChart()
}, { deep: true })
</script>