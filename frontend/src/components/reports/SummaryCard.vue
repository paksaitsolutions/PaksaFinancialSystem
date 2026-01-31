<template>
  <div class="summary-card" :class="{ 'with-trend': showTrend, 'loading': loading }">
    <div v-if="loading" class="loading-overlay">
      <ProgressSpinner style="width: 30px; height: 30px" />
    </div>
    
    <div class="card-icon">
      <i :class="icon"></i>
    </div>
    
    <div class="card-content">
      <div class="card-title">{{ title }}</div>
      <div class="card-value">
        {{ formattedValue }}
        <span v-if="suffix" class="suffix">{{ suffix }}</span>
      </div>
      
      <div v-if="showTrend" class="trend-indicator">
        <div class="trend" :class="trendClass">
          <i :class="trendIcon"></i>
          <span v-if="trendPercentage !== null" class="trend-percentage">
            {{ formatPercentage(trendPercentage) }}
          </span>
        </div>
        <div v-if="trendLabel" class="trend-label">{{ trendLabel }}</div>
      </div>
      
      <div v-if="$slots.footer" class="card-footer">
        <slot name="footer"></slot>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  value: {
    type: [String, Number],
    default: 0
  },
  icon: {
    type: String,
    default: 'pi pi-chart-line'
  },
  prefix: {
    type: String,
    default: ''
  },
  suffix: {
    type: String,
    default: ''
  },
  loading: {
    type: Boolean,
    default: false
  },
  // Trend related props
  trend: {
    type: String,
    validator: (value: string) => ['up', 'down', 'neutral', ''].includes(value),
    default: ''
  },
  trendPercentage: {
    type: Number,
    default: null
  },
  trendLabel: {
    type: String,
    default: ''
  },
  // Formatting options
  formatAs: {
    type: String,
    default: 'currency', // 'currency', 'number', 'percentage'
    validator: (value: string) => ['currency', 'number', 'percentage'].includes(value)
  },
  decimals: {
    type: Number,
    default: 2
  }
});

const showTrend = computed(() => props.trend || props.trendPercentage !== null);

const formattedValue = computed(() => {
  const value = props.value;
  
  if (value === null || value === undefined) return 'N/A';
  
  switch (props.formatAs) {
    case 'currency':
      return formatCurrency(Number(value), props.decimals);
    case 'percentage':
      return formatPercentage(Number(value), props.decimals);
    case 'number':
    default:
      return formatNumber(Number(value), props.decimals);
  }
});

const trendClass = computed(() => {
  if (props.trend) return `trend-${props.trend}`;
  if (props.trendPercentage === null) return '';
  
  return props.trendPercentage >= 0 ? 'trend-up' : 'trend-down';
});

const trendIcon = computed(() => {
  if (props.trend) {
    switch (props.trend) {
      case 'up': return 'pi pi-arrow-up';
      case 'down': return 'pi pi-arrow-down';
      case 'neutral': return 'pi pi-minus';
      default: return '';
    }
  }
  
  return props.trendPercentage >= 0 ? 'pi pi-arrow-up' : 'pi pi-arrow-down';
});

// Formatting helpers
const formatCurrency = (value: number, decimals: number = 2): string => {
  if (isNaN(value)) return 'N/A';
  
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD', // This should be dynamic based on user preferences
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  }).format(value);
};

const formatPercentage = (value: number, decimals: number = 1): string => {
  if (value === null || value === undefined) return 'N/A';
  
  return new Intl.NumberFormat('en-US', {
    style: 'percent',
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  }).format(value / 100);
};

const formatNumber = (value: number, decimals: number = 0): string => {
  if (isNaN(value)) return 'N/A';
  
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  }).format(value);
};
</script>

<style scoped>
.summary-card {
  position: relative;
  background: var(--surface-card);
  border-radius: 8px;
  padding: 1.25rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s, box-shadow 0.2s;
  border-left: 4px solid var(--primary-color);
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.summary-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10;
  border-radius: 8px;
}

.card-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background-color: var(--primary-100);
  color: var(--primary-color);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  margin-bottom: 1rem;
  flex-shrink: 0;
}

.card-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.card-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-color-secondary);
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.card-value {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0.25rem 0;
  line-height: 1.2;
  word-break: break-word;
}

.suffix {
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text-color-secondary);
  margin-left: 0.25rem;
}

.trend-indicator {
  margin-top: 0.75rem;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.trend {
  display: inline-flex;
  align-items: center;
  font-size: 0.8rem;
  font-weight: 500;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.trend-up {
  color: var(--green-600);
  background-color: var(--green-100);
}

.trend-down {
  color: var(--red-600);
  background-color: var(--red-100);
}

.trend-neutral {
  color: var(--yellow-600);
  background-color: var(--yellow-100);
}

.trend i {
  font-size: 0.7rem;
  margin-right: 0.25rem;
}

.trend-percentage {
  font-weight: 600;
  margin-left: 0.15rem;
}

.trend-label {
  font-size: 0.75rem;
  color: var(--text-color-secondary);
}

.card-footer {
  margin-top: auto;
  padding-top: 0.75rem;
  border-top: 1px solid var(--surface-border);
  margin-top: 0.75rem;
}

/* Color variants */
.summary-card.primary {
  border-left-color: var(--primary-color);
}

.summary-card.primary .card-icon {
  background-color: var(--primary-100);
  color: var(--primary-color);
}

.summary-card.success {
  border-left-color: var(--green-500);
}

.summary-card.success .card-icon {
  background-color: var(--green-100);
  color: var(--green-500);
}

.summary-card.warning {
  border-left-color: var(--yellow-500);
}

.summary-card.warning .card-icon {
  background-color: var(--yellow-100);
  color: var(--yellow-500);
}

.summary-card.danger {
  border-left-color: var(--red-500);
}

.summary-card.danger .card-icon {
  background-color: var(--red-100);
  color: var(--red-500);
}

.summary-card.info {
  border-left-color: var(--blue-500);
}

.summary-card.info .card-icon {
  background-color: var(--blue-100);
  color: var(--blue-500);
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .summary-card {
    padding: 1rem;
  }
  
  .card-value {
    font-size: 1.25rem;
  }
  
  .card-icon {
    width: 40px;
    height: 40px;
    font-size: 1rem;
  }
}
</style>
