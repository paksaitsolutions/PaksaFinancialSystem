<template>
  <div class="cash-flow-chart">
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'

interface Props {
  data: Array<{
    month: string
    inflow: number
    outflow: number
  }>
}

const props = defineProps<Props>()
const chartCanvas = ref<HTMLCanvasElement>()

onMounted(() => {
  if (chartCanvas.value) {
    const ctx = chartCanvas.value.getContext('2d')
    if (ctx) {
      drawChart(ctx)
    }
  }
})

const drawChart = (ctx: CanvasRenderingContext2D) => {
  const canvas = ctx.canvas
  canvas.width = canvas.offsetWidth
  canvas.height = canvas.offsetHeight
  
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  
  const barWidth = canvas.width / (props.data.length * 2 + 1)
  const maxValue = Math.max(...props.data.flatMap(d => [d.inflow, d.outflow]))
  
  props.data.forEach((item, index) => {
    const x = (index * 2 + 1) * barWidth
    const inflowHeight = (item.inflow / maxValue) * (canvas.height - 40)
    const outflowHeight = (item.outflow / maxValue) * (canvas.height - 40)
    
    ctx.fillStyle = '#4CAF50'
    ctx.fillRect(x, canvas.height - inflowHeight - 20, barWidth * 0.8, inflowHeight)
    
    ctx.fillStyle = '#F44336'
    ctx.fillRect(x + barWidth, canvas.height - outflowHeight - 20, barWidth * 0.8, outflowHeight)
    
    ctx.fillStyle = '#333'
    ctx.font = '12px Arial'
    ctx.textAlign = 'center'
    ctx.fillText(item.month, x + barWidth, canvas.height - 5)
  })
}

watch(() => props.data, () => {
  if (chartCanvas.value) {
    const ctx = chartCanvas.value.getContext('2d')
    if (ctx) {
      drawChart(ctx)
    }
  }
}, { deep: true })
</script>

<style scoped>
.cash-flow-chart {
  height: 300px;
  position: relative;
}

canvas {
  width: 100%;
  height: 100%;
}
</style>