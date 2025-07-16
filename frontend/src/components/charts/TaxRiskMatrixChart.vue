<template>
  <v-card>
    <v-card-title class="text-subtitle-1 font-weight-bold">
      Tax Risk Matrix
    </v-card-title>
    <v-card-text>
      <apexchart
        type="heatmap"
        height="400"
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
    type: 'heatmap',
    height: 400,
    toolbar: {
      show: true
    }
  },
  colors: ['#008FFB', '#00E396', '#FEB019', '#FF4560', '#775DD0'],
  plotOptions: {
    heatmap: {
      shadeIntensity: 0.5,
      colorScale: {
        ranges: [
          { from: 0, to: 20, name: 'Low Risk', color: '#008FFB' },
          { from: 21, to: 40, name: 'Medium Risk', color: '#00E396' },
          { from: 41, to: 60, name: 'High Risk', color: '#FEB019' },
          { from: 61, to: 80, name: 'Very High Risk', color: '#FF4560' },
          { from: 81, to: 100, name: 'Critical Risk', color: '#775DD0' }
        ]
      }
    }
  },
  dataLabels: {
    enabled: true
  },
  xaxis: {
    type: 'category',
    labels: {
      rotate: -45
    }
  },
  yaxis: {
    type: 'category',
    labels: {
      rotate: -45
    }
  },
  tooltip: {
    y: {
      formatter: (value: number) => formatCurrency(value)
    }
  }
});

const chartSeries = computed(() => {
  if (!taxAnalyticsStore.analyticsData) return [];
  
  // Generate risk matrix data
  const riskMatrix = [
    {
      name: 'Jurisdictions',
      data: Object.entries(taxAnalyticsStore.analyticsData.jurisdictionalBreakdown)
        .map(([jurisdiction, amount]) => ({
          x: jurisdiction,
          y: calculateRiskScore(amount),
          value: amount
        }))
    }
  ];

  return riskMatrix;
});

function calculateRiskScore(amount: number): number {
  // Simple risk calculation based on tax amount
  const maxAmount = Object.values(taxAnalyticsStore.analyticsData.jurisdictionalBreakdown)
    .reduce((max, val) => Math.max(max, val), 0);
  
  return (amount / maxAmount) * 100;
}

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
