<template>
  <Card class="kpi-widget">
    <template #content>
      <div class="kpi-content">
        <div class="kpi-header">
          <h4 class="kpi-title">{{ title }}</h4>
          <div class="kpi-trend" :class="trendClass">
            <i :class="trendIcon"></i>
          </div>
        </div>
        <div class="kpi-value">
          {{ formattedValue }}
        </div>
        <div class="kpi-change" :class="changeClass">
          <i :class="changeIcon"></i>
          <span>{{ formattedChange }} vs last period</span>
        </div>
      </div>
    </template>
  </Card>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  value: {
    type: [Number, String],
    required: true
  },
  trend: {
    type: String,
    default: 'neutral' // 'up', 'down', 'neutral'
  },
  change: {
    type: Number,
    default: 0
  },
  format: {
    type: String,
    default: 'number' // 'currency', 'percent', 'number'
  }
})

const formattedValue = computed(() => {
  if (props.format === 'currency') {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(props.value)
  } else if (props.format === 'percent') {
    return `${props.value}%`
  } else {
    return new Intl.NumberFormat('en-US').format(props.value)
  }
})

const formattedChange = computed(() => {
  const absChange = Math.abs(props.change)
  if (props.format === 'percent') {
    return `${absChange}%`
  }
  return `${absChange}%`
})

const trendClass = computed(() => ({
  'trend-up': props.trend === 'up',
  'trend-down': props.trend === 'down',
  'trend-neutral': props.trend === 'neutral'
}))

const trendIcon = computed(() => {
  switch (props.trend) {
    case 'up': return 'pi pi-arrow-up'
    case 'down': return 'pi pi-arrow-down'
    default: return 'pi pi-minus'
  }
})

const changeClass = computed(() => ({
  'change-positive': props.change > 0,
  'change-negative': props.change < 0,
  'change-neutral': props.change === 0
}))

const changeIcon = computed(() => {
  if (props.change > 0) return 'pi pi-arrow-up'
  if (props.change < 0) return 'pi pi-arrow-down'
  return 'pi pi-minus'
})
</script>

<style scoped>
.kpi-widget {
  height: 100%;
  border-radius: var(--border-radius-lg);
  transition: all 0.3s ease;
}

.kpi-widget:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.kpi-content {
  padding: 0;
}

.kpi-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--spacing-4);
}

.kpi-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-color-secondary);
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.kpi-trend {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
}

.trend-up {
  background: rgba(16, 185, 129, 0.1);
  color: var(--green-500);
}

.trend-down {
  background: rgba(239, 68, 68, 0.1);
  color: var(--red-500);
}

.trend-neutral {
  background: rgba(100, 116, 139, 0.1);
  color: var(--text-color-secondary);
}

.kpi-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-color);
  margin-bottom: var(--spacing-2);
  line-height: 1.2;
}

.kpi-change {
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
  font-size: 0.75rem;
  font-weight: 500;
}

.change-positive {
  color: var(--green-500);
}

.change-negative {
  color: var(--red-500);
}

.change-neutral {
  color: var(--text-color-secondary);
}

.kpi-change i {
  font-size: 0.625rem;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .kpi-value {
    font-size: 1.75rem;
  }
  
  .kpi-title {
    font-size: 0.75rem;
  }
  
  .kpi-trend {
    width: 28px;
    height: 28px;
    font-size: 0.75rem;
  }
}

@media (max-width: 576px) {
  .kpi-value {
    font-size: 1.5rem;
  }
  
  .kpi-change {
    font-size: 0.6875rem;
  }
}
</style>