<template>
  <v-card>
    <v-card-title class="text-subtitle-1 font-weight-bold">
      Tax Trends Over Time
    </v-card-title>
    <v-card-text>
      <apexchart
        type="line"
        height="350"
        :options="chartOptions"
        :series="chartSeries"
      ></apexchart>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useTaxAnalyticsStore } from '@/stores/tax/analytics';
import { formatCurrency } from '@/utils/formatters';

const taxAnalyticsStore = useTaxAnalyticsStore();

const chartOptions = ref({
  chart: {
    type: 'line',
    height: 350,
    toolbar: {
      show: true,
      autoSelected: 'zoom'
    }
  },
  colors: ['#2196F3', '#4CAF50', '#FF9800'],
  dataLabels: {
    enabled: false
  },
  stroke: {
    curve: 'smooth'
  },
  xaxis: {
    type: 'datetime',
    labels: {
      datetimeFormatter: {
        year: 'yyyy',
        month: 'MMM yyyy',
        day: 'dd MMM yyyy',
        hour: 'HH:mm'
      }
    }
  },
  yaxis: {
    labels: {
      formatter: (value: number) => formatCurrency(value)
    }
  },
  tooltip: {
    y: {
      formatter: (value: number) => formatCurrency(value)
    }
  },
  legend: {
    position: 'top'
  }
});

const chartSeries = computed(() => {
  if (!taxAnalyticsStore.analyticsData) return [];
  
  return [
    {
      name: 'Total Tax Amount',
      data: Object.entries(taxAnalyticsStore.analyticsData.jurisdictionalBreakdown)
        .map(([date, amount]) => ({ x: new Date(date), y: amount }))
    },
    {
      name: 'Average Tax per Employee',
      data: Object.entries(taxAnalyticsStore.analyticsData.exemptionUsage)
        .map(([date, amount]) => ({ x: new Date(date), y: amount }))
    }
  ];
});

onMounted(() => {
  // Initialize chart options with current data
  chartOptions.value = {
    ...chartOptions.value,
    xaxis: {
      ...chartOptions.value.xaxis,
      categories: Object.keys(taxAnalyticsStore.analyticsData.jurisdictionalBreakdown)
    }
  };
});
</script>
