<template>
  <div class="metrics-grid">
    <Card v-for="metric in metrics" :key="metric.id" class="metric-card">
      <template #content>
        <div class="metric-content">
          <i :class="metric.icon" class="metric-icon" :style="{ color: metric.color }"></i>
          <div class="metric-value">{{ metric.value }}</div>
          <div class="metric-label">{{ metric.label }}</div>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import Card from 'primevue/card'

interface Metric {
  id: string
  icon: string
  value: string | number
  label: string
  color?: string
}

interface Props {
  metrics: Metric[]
}

defineProps<Props>()
</script>

<style scoped>
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-lg);
}

.metric-card {
  height: 100%;
}

.metric-content {
  text-align: center;
  padding: var(--spacing-sm);
}

.metric-icon {
  font-size: 2.5rem;
  margin-bottom: var(--spacing-md);
  display: block;
}

.metric-value {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--text-color);
  margin-bottom: var(--spacing-xs);
  line-height: var(--line-height-tight);
}

.metric-label {
  font-size: var(--font-size-sm);
  color: var(--text-color-secondary);
  font-weight: var(--font-weight-medium);
}

@media (max-width: 768px) {
  .metrics-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: var(--spacing-md);
  }
  
  .metric-icon {
    font-size: 2rem;
  }
  
  .metric-value {
    font-size: var(--font-size-xl);
  }
}

@media (max-width: 480px) {
  .metrics-grid {
    grid-template-columns: 1fr;
  }
}
</style>