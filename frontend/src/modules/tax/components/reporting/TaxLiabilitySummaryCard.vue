<template>
  <div class="tax-liability-summary-card" :class="[size, { 'with-chart': showChart }]">
    <div class="card-header">
      <div class="title-container">
        <i :class="icon" class="icon"></i>
        <h3 class="title">{{ title }}</h3>
        <Button 
          v-if="tooltip"
          icon="pi pi-info-circle" 
          class="p-button-text p-button-rounded p-button-sm info-button"
          v-tooltip.top="tooltip"
        />
      </div>
      
      <div v-if="showTrend" class="trend-indicator" :class="trendClass">
        <i :class="trendIcon"></i>
        <span class="trend-value">{{ trendValue }}</span>
      </div>
    </div>
    
    <div class="card-content">
      <div class="main-value" :class="{ 'with-trend': showTrend }">
        {{ formattedValue }}
        <span v-if="secondaryValue" class="secondary-value">{{ secondaryValue }}</span>
      </div>
      
      <div v-if="showChart && chartData" class="chart-container">
        <Chart 
          type="line" 
          :data="chartData" 
          :options="chartOptions"
          class="chart"
        />
      </div>
      
      <div v-if="footerText" class="footer">
        <span class="footer-text">{{ footerText }}</span>
        <Button 
          v-if="actionLabel"
          :label="actionLabel"
          class="p-button-text p-button-sm action-button"
          :icon="actionIcon"
          @click="onAction"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { formatCurrency, formatPercentage } from '@/utils/formatters';

const props = defineProps({
  // Card appearance
  title: {
    type: String,
    required: true
  },
  icon: {
    type: String,
    default: 'pi pi-chart-line'
  },
  tooltip: {
    type: String,
    default: ''
  },
  size: {
    type: String,
    default: 'medium', // 'small', 'medium', 'large'
    validator: (value: string) => ['small', 'medium', 'large'].includes(value)
  },
  
  // Main value
  value: {
    type: [Number, String],
    default: 0
  },
  valuePrefix: {
    type: String,
    default: ''
  },
  valueSuffix: {
    type: String,
    default: ''
  },
  isCurrency: {
    type: Boolean,
    default: false
  },
  currency: {
    type: String,
    default: 'USD'
  },
  isPercentage: {
    type: Boolean,
    default: false
  },
  decimalPlaces: {
    type: Number,
    default: 2
  },
  
  // Secondary value (e.g., comparison value)
  secondaryValue: {
    type: String,
    default: ''
  },
  
  // Trend indicator
  showTrend: {
    type: Boolean,
    default: false
  },
  trendValue: {
    type: [Number, String],
    default: 0
  },
  isTrendPositive: {
    type: Boolean,
    default: true
  },
  trendUnit: {
    type: String,
    default: '%'
  },
  
  // Chart
  showChart: {
    type: Boolean,
    default: false
  },
  chartData: {
    type: Object,
    default: null
  },
  
  // Footer
  footerText: {
    type: String,
    default: ''
  },
  actionLabel: {
    type: String,
    default: ''
  },
  actionIcon: {
    type: String,
    default: 'pi pi-arrow-right'
  }
});

const emit = defineEmits(['action']);

// Computed properties
const formattedValue = computed(() => {
  let formatted = '';
  
  if (props.isCurrency) {
    formatted = formatCurrency(Number(props.value), props.currency, props.decimalPlaces);
  } else if (props.isPercentage) {
    formatted = formatPercentage(Number(props.value), props.decimalPlaces);
  } else {
    // Format as number with thousands separators
    const numValue = Number(props.value);
    formatted = isNaN(numValue) 
      ? String(props.value) 
      : numValue.toLocaleString(undefined, {
          minimumFractionDigits: props.decimalPlaces,
          maximumFractionDigits: props.decimalPlaces
        });
  }
  
  return `${props.valuePrefix}${formatted}${props.valueSuffix}`;
});

const trendClass = computed(() => ({
  'trend-up': props.isTrendPositive,
  'trend-down': !props.isTrendPositive
}));

const trendIcon = computed(() => 
  props.isTrendPositive ? 'pi pi-arrow-up' : 'pi pi-arrow-down'
);

const chartOptions = computed(() => ({
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      enabled: false
    }
  },
  scales: {
    x: { display: false },
    y: { display: false }
  },
  elements: {
    line: {
      borderWidth: 2,
      tension: 0.4,
      fill: true
    },
    point: {
      radius: 0
    }
  },
  responsive: true,
  maintainAspectRatio: false,
  animation: {
    duration: 0
  }
}));

// Methods
const onAction = () => {
  emit('action');
};
</script>

<style scoped>
.tax-liability-summary-card {
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  padding: 1.25rem;
  height: 100%;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
  border: 1px solid #e9ecef;
}

.tax-liability-summary-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

/* Card sizes */
.tax-liability-summary-card.small {
  padding: 1rem;
}

.tax-liability-summary-card.medium {
  padding: 1.25rem;
}

.tax-liability-summary-card.large {
  padding: 1.5rem;
}

/* Card header */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.title-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.icon {
  font-size: 1.25rem;
  color: var(--primary-color);
  opacity: 0.9;
}

.title {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: #495057;
  line-height: 1.2;
}

.info-button {
  color: #6c757d;
  width: 1.5rem;
  height: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: 0.25rem;
  opacity: 0.7;
}

.info-button:hover {
  opacity: 1;
  background: rgba(0, 0, 0, 0.05);
}

/* Trend indicator */
.trend-indicator {
  display: flex;
  align-items: center;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.2rem 0.5rem;
  border-radius: 12px;
  background-color: #f8f9fa;
}

.trend-up {
  color: #10b981;
}

.trend-down {
  color: #ef4444;
}

.trend-indicator i {
  font-size: 0.65rem;
  margin-right: 0.25rem;
}

/* Card content */
.card-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.main-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #2c3e50;
  margin: 0.5rem 0;
  line-height: 1.2;
}

.tax-liability-summary-card.small .main-value {
  font-size: 1.25rem;
}

.tax-liability-summary-card.large .main-value {
  font-size: 1.75rem;
}

.secondary-value {
  display: block;
  font-size: 0.875rem;
  font-weight: 400;
  color: #6c757d;
  margin-top: 0.25rem;
}

/* Chart */
.chart-container {
  flex: 1;
  min-height: 60px;
  margin: 0.5rem 0;
}

.chart {
  width: 100%;
  height: 100%;
}

/* Footer */
.footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid #f1f3f5;
  font-size: 0.75rem;
  color: #6c757d;
}

.action-button {
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
  color: var(--primary-color);
}

.action-button:hover {
  background: rgba(13, 110, 253, 0.05);
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .tax-liability-summary-card {
    padding: 1rem;
  }
  
  .main-value {
    font-size: 1.25rem;
  }
  
  .secondary-value {
    font-size: 0.75rem;
  }
}
</style>
