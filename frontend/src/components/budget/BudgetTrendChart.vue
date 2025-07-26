<template>
  <v-card>
    <v-card-title>Budget Trends</v-card-title>
    <v-card-text>
      <canvas ref="chartCanvas" height="300"></canvas>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const chartCanvas = ref(null)

onMounted(() => {
  // Mock chart implementation
  const ctx = chartCanvas.value.getContext('2d')
  ctx.fillStyle = '#1976d2'
  ctx.fillRect(50, 50, 100, 100)
  ctx.fillStyle = '#fff'
  ctx.font = '16px Arial'
  ctx.fillText('Budget Trend Chart', 60, 110)
})
</script>