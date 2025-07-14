<template>
  <div class="budget-card" :class="{ 'negative': percentage < 0 }">
    <div class="card-header">
      <div class="icon" :style="{ backgroundColor: color }">
        <i :class="icon"></i>
      </div>
      <h3>{{ title }}</h3>
    </div>
    <div class="card-content">
      <div class="value">{{ formatValue(value) }}</div>
      <div class="percentage">
        <i class="mdi" :class="percentageIcon"></i>
        {{ Math.abs(percentage).toFixed(1) }}%
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  title: string
  value: number
  percentage: number
  icon: string
  color: string
}

const props = defineProps<Props>()

const percentageIcon = computed(() => {
  if (props.percentage > 0) return 'mdi-arrow-up'
  if (props.percentage < 0) return 'mdi-arrow-down'
  return 'mdi-minus'
})

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
.budget-card {
  background: var(--card-background);
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: var(--card-shadow);
  transition: transform 0.2s ease-in-out;
}

.budget-card:hover {
  transform: translateY(-5px);
}

.negative {
  border-left: 4px solid #ff4444;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

h3 {
  margin: 0;
  font-size: 1.25rem;
  color: var(--text-color);
}

.card-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.value {
  font-size: 1.75rem;
  font-weight: 600;
  color: var(--text-color);
}

.percentage {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  color: var(--text-color);
}

.percentage i {
  font-size: 1.25rem;
}

@media (max-width: 768px) {
  .budget-card {
    padding: 1rem;
  }
  
  .card-content {
    flex-direction: column;
    gap: 0.5rem;
    align-items: flex-start;
  }
  
  .value {
    font-size: 1.5rem;
  }
  
  .percentage {
    font-size: 0.9rem;
  }
}
</style>
