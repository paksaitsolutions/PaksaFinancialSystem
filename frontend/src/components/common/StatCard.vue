<template>
  <div 
    class="stat-card bg-white rounded-lg shadow-sm border border-gray-200 p-5 hover:shadow-md transition-shadow duration-200 cursor-pointer"
    :class="{ 'opacity-50': loading }"
    @click="$emit('click', $event)"
  >
    <div class="flex items-center justify-between">
      <div>
        <p class="text-sm font-medium text-gray-500 mb-1">
          {{ title }}
        </p>
        <div v-if="!loading" class="text-2xl font-semibold text-gray-900">
          {{ formattedValue }}
        </div>
        <div v-else class="h-8 bg-gray-200 rounded animate-pulse w-3/4"></div>
      </div>
      
      <div 
        class="p-3 rounded-full flex-shrink-0"
        :class="color || 'bg-gray-100 text-gray-600'"
      >
        <i :class="icon" class="text-lg"></i>
      </div>
    </div>
    
    <!-- Trend indicator (optional) -->
    <div v-if="trend !== undefined && !loading" class="mt-3 flex items-center">
      <span 
        class="text-xs font-medium flex items-center"
        :class="{
          'text-green-600': trend > 0,
          'text-red-600': trend < 0,
          'text-gray-500': trend === 0
        }"
      >
        <i 
          v-if="trend !== 0"
          :class="{
            'pi pi-arrow-up': trend > 0,
            'pi pi-arrow-down': trend < 0
          }"
          class="mr-1"
        ></i>
        {{ formatTrend(trend) }}
      </span>
      <span v-if="trendLabel" class="text-xs text-gray-500 ml-2">
        {{ trendLabel }}
      </span>
    </div>
    <div v-else-if="loading" class="mt-3 h-4 bg-gray-200 rounded animate-pulse w-1/2"></div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = withDefaults(defineProps<{
  title: string;
  value: string | number;
  icon: string;
  color?: string;
  loading?: boolean;
  trend?: number;
  trendLabel?: string;
  formatValue?: (val: any) => string;
}>(), {
  loading: false,
  trend: undefined,
  trendLabel: '',
  formatValue: (val: any) => val?.toString() || '0'
});

const emit = defineEmits<{
  (e: 'click', event: Event): void;
}>();

const formattedValue = computed(() => {
  if (typeof props.value === 'number' && !isNaN(props.value)) {
    return props.formatValue(props.value);
  }
  return props.formatValue ? props.formatValue(props.value) : props.value;
});

const formatTrend = (value: number) => {
  if (value === 0) return 'No change';
  const absValue = Math.abs(value);
  const prefix = value > 0 ? '+' : '-';
  return `${prefix}${absValue}%`;
};
</script>

<style scoped>
.stat-card {
  transition: all 0.2s ease-in-out;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}
</style>
