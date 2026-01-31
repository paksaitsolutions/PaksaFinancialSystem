<!--
  Paksa Financial System - Stats Card Component
  Copyright (c) 2025 Paksa IT Solutions. All rights reserved.
-->
<template>
  <Card class="stats-card">
    <template #content>
      <div class="stats-content">
        <div class="stats-icon" :style="{ background: iconBg }">
          <i :class="icon" :style="{ color: iconColor }"></i>
        </div>
        <div class="stats-info">
          <span class="stats-label">{{ label }}</span>
          <span class="stats-value">{{ formattedValue }}</span>
          <span v-if="change" :class="['stats-change', changeClass]">
            <i :class="changeIcon"></i>
            {{ Math.abs(change) }}%
          </span>
        </div>
      </div>
    </template>
  </Card>
</template>

<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  label: string;
  value: number | string;
  icon: string;
  iconColor?: string;
  iconBg?: string;
  change?: number;
  format?: 'currency' | 'number' | 'percentage';
}

const props = withDefaults(defineProps<Props>(), {
  iconColor: '#fff',
  iconBg: 'var(--primary-color)',
  format: 'number'
});

const formattedValue = computed(() => {
  if (typeof props.value === 'string') return props.value;
  
  switch (props.format) {
    case 'currency':
      return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(props.value);
    case 'percentage':
      return `${props.value}%`;
    default:
      return new Intl.NumberFormat('en-US').format(props.value);
  }
});

const changeClass = computed(() => props.change && props.change > 0 ? 'positive' : 'negative');
const changeIcon = computed(() => props.change && props.change > 0 ? 'pi pi-arrow-up' : 'pi pi-arrow-down');
</script>

<style scoped>
.stats-card {
  height: 100%;
}

.stats-content {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.stats-icon {
  width: 3rem;
  height: 3rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.stats-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stats-label {
  font-size: 0.875rem;
  color: var(--text-color-secondary);
}

.stats-value {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-color);
}

.stats-change {
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.stats-change.positive {
  color: var(--green-500);
}

.stats-change.negative {
  color: var(--red-500);
}
</style>
