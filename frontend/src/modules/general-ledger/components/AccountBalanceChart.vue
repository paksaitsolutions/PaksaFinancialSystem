<template>
  <div class="account-balance-chart">
    <canvas ref="chartCanvas"></canvas>
    <div class="legend">
      <div 
        v-for="item in data" 
        :key="item.label"
        class="legend-item"
      >
        <div 
          class="legend-color"
          :style="{ backgroundColor: item.color }"
        ></div>
        <span class="legend-label">{{ item.label }}</span>
        <span class="legend-value">{{ formatCurrency(item.value) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'

interface Props {
  data: Array<{
    label: string
    value: number
    color: string
  }>
}

const props = defineProps<Props>()
const chartCanvas = ref<HTMLCanvasElement>()

onMounted(() => {
  if (chartCanvas.value) {
    const ctx = chartCanvas.value.getContext('2d')
    if (ctx) {
      drawPieChart(ctx)
    }
  }
})

const drawPieChart = (ctx: CanvasRenderingContext2D) => {
  const canvas = ctx.canvas
  canvas.width = canvas.offsetWidth
  canvas.height = canvas.offsetHeight
  
  const centerX = canvas.width / 2
  const centerY = canvas.height / 2
  const radius = Math.min(centerX, centerY) - 20
  
  const total = props.data.reduce((sum, item) => sum + item.value, 0)
  let currentAngle = -Math.PI / 2
  
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  
  props.data.forEach((item) => {
    const sliceAngle = (item.value / total) * 2 * Math.PI
    
    ctx.beginPath()
    ctx.moveTo(centerX, centerY)
    ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle)
    ctx.closePath()
    ctx.fillStyle = item.color
    ctx.fill()
    
    currentAngle += sliceAngle
  })
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}

watch(() => props.data, () => {
  if (chartCanvas.value) {
    const ctx = chartCanvas.value.getContext('2d')
    if (ctx) {
      drawPieChart(ctx)
    }
  }
}, { deep: true })
</script>

<style scoped>
.account-balance-chart {
  height: 300px;
  display: flex;
  align-items: center;
}

canvas {
  flex: 1;
  height: 100%;
}

.legend {
  flex: 1;
  padding-left: 20px;
}

.legend-item {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
  margin-right: 8px;
}

.legend-label {
  flex: 1;
  font-size: 14px;
}

.legend-value {
  font-size: 12px;
  font-weight: bold;
  color: #666;
}
</style>