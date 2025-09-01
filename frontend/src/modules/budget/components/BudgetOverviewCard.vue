<template>
  <Card class="p-4">
    <template #content>
      <div class="flex justify-content-between align-items-center">
        <div>
          <h3 class="text-lg font-semibold mb-1">{{ title }}</h3>
          <p class="text-sm text-500">{{ subtitle }}</p>
        </div>
        <i :class="icon" class="text-4xl" :style="{ color: color }"></i>
      </div>
      <div class="text-3xl font-bold mt-4">{{ formattedValue }}</div>
      <div v-if="percentage" class="flex align-items-center mt-2">
        <i 
          :class="percentageIcon"
          :style="{ color: percentageColor }"
          class="text-sm"
        ></i>
        <span :style="{ color: percentageColor }" class="ml-1">{{ percentage }}%</span>
      </div>
    </template>
  </Card>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  title: string
  value: number | string
  percentage?: number
  icon: string
  color?: string
  subtitle?: string
}

const props = withDefaults(defineProps<Props>(), {
  color: 'primary',
  subtitle: ''
})

const formattedValue = computed(() => {
  if (typeof props.value === 'number') {
    return new Intl.NumberFormat('en-US').format(props.value)
  }
  return props.value
})

const percentageColor = computed(() => {
  if (!props.percentage) return '#6c757d'
  return props.percentage >= 0 ? '#28a745' : '#dc3545'
})

const percentageIcon = computed(() => {
  if (!props.percentage) return 'pi pi-minus'
  return props.percentage >= 0 ? 'pi pi-arrow-up' : 'pi pi-arrow-down'
})
</script>