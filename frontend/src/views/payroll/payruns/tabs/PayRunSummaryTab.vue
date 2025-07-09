<template>
  <div class="summary-tab">
    <v-row>
      <v-col cols="12" md="6">
        <v-card variant="outlined" class="mb-4">
          <v-card-title class="text-subtitle-1 font-weight-medium">
            <v-icon start>mdi-currency-usd</v-icon>
            Earnings
          </v-card-title>
          <v-divider />
          <v-list density="compact" class="pa-0">
            <v-list-item 
              v-for="(amount, type) in earningsSummary" 
              :key="`earn-${type}`"
            >
              <v-list-item-title>{{ formatEarningType(type) }}</v-list-item-title>
              <v-list-item-subtitle class="text-right">
                {{ formatCurrency(amount) }}
              </v-list-item-subtitle>
            </v-list-item>
            <v-divider />
            <v-list-item class="font-weight-bold">
              <v-list-item-title>Total Earnings</v-list-item-title>
              <v-list-item-subtitle class="text-right">
                {{ formatCurrency(totalEarnings) }}
              </v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="6">
        <v-card variant="outlined" class="mb-4">
          <v-card-title class="text-subtitle-1 font-weight-medium">
            <v-icon start>mdi-minus-circle</v-icon>
            Deductions
          </v-card-title>
          <v-divider />
          <v-list density="compact" class="pa-0">
            <v-list-item 
              v-for="(amount, type) in deductionsSummary" 
              :key="`deduct-${type}`"
            >
              <v-list-item-title>{{ formatDeductionType(type) }}</v-list-item-title>
              <v-list-item-subtitle class="text-right">
                {{ formatCurrency(amount) }}
              </v-list-item-subtitle>
            </v-list-item>
            <v-divider />
            <v-list-item class="font-weight-bold">
              <v-list-item-title>Total Deductions</v-list-item-title>
              <v-list-item-subtitle class="text-right">
                {{ formatCurrency(totalDeductions) }}
              </v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </v-card>
      </v-col>
      
      <v-col cols="12">
        <v-card variant="outlined">
          <v-card-title class="text-subtitle-1 font-weight-medium">
            <v-icon start>mdi-calculator</v-icon>
            Net Pay Summary
          </v-card-title>
          <v-divider />
          <v-list density="comfortable" class="pa-0">
            <v-list-item>
              <v-list-item-title>Total Earnings</v-list-item-title>
              <v-list-item-subtitle class="text-right">
                {{ formatCurrency(totalEarnings) }}
              </v-list-item-subtitle>
            </v-list-item>
            <v-list-item>
              <v-list-item-title>Total Deductions</v-list-item-title>
              <v-list-item-subtitle class="text-right">
                -{{ formatCurrency(totalDeductions) }}
              </v-list-item-subtitle>
            </v-list-item>
            <v-divider />
            <v-list-item class="font-weight-bold text-h6">
              <v-list-item-title>Net Pay</v-list-item-title>
              <v-list-item-subtitle class="text-right">
                {{ formatCurrency(totalNetPay) }}
              </v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </v-card>
      </v-col>
      
      <v-col cols="12">
        <v-card variant="outlined" class="mt-4">
          <v-card-title class="text-subtitle-1 font-weight-medium">
            <v-icon start>mdi-chart-pie</v-icon>
            Distribution
          </v-card-title>
          <v-divider />
          <v-card-text>
            <v-row>
              <v-col cols="12" md="6">
                <div class="d-flex justify-center">
                  <div style="width: 300px; height: 300px;">
                    <canvas ref="earningsChart"></canvas>
                  </div>
                </div>
                <div class="text-center text-subtitle-2 text-medium-emphasis">
                  Earnings Distribution
                </div>
              </v-col>
              <v-col cols="12" md="6">
                <div class="d-flex justify-center">
                  <div style="width: 300px; height: 300px;">
                    <canvas ref="deductionsChart"></canvas>
                  </div>
                </div>
                <div class="text-center text-subtitle-2 text-medium-emphasis">
                  Deductions Distribution
                </div>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, watch, nextTick } from 'vue';
import { Chart, registerables } from 'chart.js';

export default defineComponent({
  name: 'PayRunSummaryTab',
  
  props: {
    earningsSummary: {
      type: Object,
      required: true,
      default: () => ({}),
    },
    deductionsSummary: {
      type: Object,
      required: true,
      default: () => ({}),
    },
    totalEarnings: {
      type: Number,
      required: true,
      default: 0,
    },
    totalDeductions: {
      type: Number,
      required: true,
      default: 0,
    },
    totalNetPay: {
      type: Number,
      required: true,
      default: 0,
    },
  },
  
  setup(props) {
    // Register Chart.js components
    Chart.register(...registerables);
    
    const earningsChart = ref<HTMLCanvasElement | null>(null);
    const deductionsChart = ref<HTMLCanvasElement | null>(null);
    
    let earningsChartInstance: Chart | null = null;
    let deductionsChartInstance: Chart | null = null;
    
    const formatCurrency = (amount: number) => {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
      }).format(amount);
    };
    
    const formatEarningType = (type: string) => {
      // Convert snake_case to Title Case
      return type
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
    };
    
    const formatDeductionType = (type: string) => {
      // Convert snake_case to Title Case
      return type
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
    };
    
    const generateChartData = (data: Record<string, number>, type: 'earnings' | 'deductions') => {
      const labels = Object.keys(data).map(key => 
        type === 'earnings' ? formatEarningType(key) : formatDeductionType(key)
      );
      const values = Object.values(data);
      
      // Generate colors based on the number of items
      const backgroundColors = [
        '#4e79a7', '#f28e2b', '#e15759', '#76b7b2', '#59a14f',
        '#edc948', '#b07aa1', '#ff9da7', '#9c755f', '#bab0ac'
      ];
      
      return {
        labels,
        datasets: [{
          data: values,
          backgroundColor: backgroundColors.slice(0, values.length),
          borderWidth: 1,
        }],
      };
    };
    
    const createChart = (canvas: HTMLCanvasElement, data: any, title: string) => {
      return new Chart(canvas, {
        type: 'pie',
        data: data,
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'right',
              labels: {
                boxWidth: 12,
                padding: 15,
                font: {
                  size: 12,
                },
              },
            },
            title: {
              display: true,
              text: title,
              font: {
                size: 14,
              },
              padding: {
                bottom: 10,
              },
            },
            tooltip: {
              callbacks: {
                label: (context) => {
                  const label = context.label || '';
                  const value = context.raw as number;
                  const total = context.dataset.data.reduce((a: number, b: number) => a + b, 0);
                  const percentage = Math.round((value / total) * 100);
                  return `${label}: ${formatCurrency(value)} (${percentage}%)`;
                },
              },
            },
          },
        },
      });
    };
    
    const updateCharts = () => {
      // Destroy existing charts if they exist
      if (earningsChartInstance) {
        earningsChartInstance.destroy();
      }
      
      if (deductionsChartInstance) {
        deductionsChartInstance.destroy();
      }
      
      // Create new charts
      if (earningsChart.value && Object.keys(props.earningsSummary).length > 0) {
        const earningsData = generateChartData(props.earningsSummary, 'earnings');
        earningsChartInstance = createChart(earningsChart.value, earningsData, 'Earnings');
      }
      
      if (deductionsChart.value && Object.keys(props.deductionsSummary).length > 0) {
        const deductionsData = generateChartData(props.deductionsSummary, 'deductions');
        deductionsChartInstance = createChart(deductionsChart.value, deductionsData, 'Deductions');
      }
    };
    
    // Watch for changes in the data and update charts
    watch(
      [() => props.earningsSummary, () => props.deductionsSummary],
      () => {
        nextTick(() => {
          updateCharts();
        });
      },
      { deep: true }
    );
    
    // Initialize charts when component is mounted
    onMounted(() => {
      nextTick(() => {
        updateCharts();
      });
    });
    
    // Clean up charts when component is unmounted
    onUnmounted(() => {
      if (earningsChartInstance) {
        earningsChartInstance.destroy();
      }
      if (deductionsChartInstance) {
        deductionsChartInstance.destroy();
      }
    });
    
    return {
      // Refs
      earningsChart,
      deductionsChart,
      // Methods
      formatCurrency,
      formatEarningType,
      formatDeductionType,
    };
  },
});
</script>

<style scoped>
.summary-tab {
  width: 100%;
}

.v-list-item {
  min-height: 40px;
}
</style>
