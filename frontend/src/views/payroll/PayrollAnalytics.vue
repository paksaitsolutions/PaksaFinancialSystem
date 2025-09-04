<template>
  <div class="payroll-analytics">
    <div class="grid">
      <div class="col-12">
        <div class="flex justify-content-between align-items-center mb-4">
          <div>
            <h1>Payroll Analytics</h1>
            <Breadcrumb :home="home" :model="breadcrumbItems" class="mb-4" />
          </div>
          <div>
            <Button 
              label="Export Report" 
              icon="pi pi-download" 
              class="p-button-outlined mr-2" 
              @click="showExportDialog"
            />
            <Button 
              label="Refresh" 
              icon="pi pi-refresh" 
              class="p-button-outlined" 
              @click="loadAllData"
              :loading="loading"
            />
          </div>
        </div>
      </div>

      <!-- Summary Cards -->
      <div class="col-12 md:col-6 lg:col-3" v-for="(stat, index) in summaryStats" :key="index">
        <Card>
          <template #title>
            <div class="flex align-items-center justify-content-between">
              <span>{{ stat.title }}</span>
              <span :class="['text-2xl', stat.icon, 'text-' + stat.color]"></span>
            </div>
          </template>
          <template #content>
            <div class="text-3xl font-bold mb-2">{{ stat.value }}</div>
            <div class="flex align-items-center">
              <span :class="['mr-2', 'font-medium', 'text-' + stat.trend.color]">
                <i :class="stat.trend.icon"></i> {{ stat.trend.value }}
              </span>
              <span class="text-500">vs last period</span>
            </div>
          </template>
        </Card>
      </div>

      <!-- Payroll Trends Chart -->
      <div class="col-12 lg:col-8">
        <Card>
          <template #title>
            <div class="flex justify-content-between align-items-center">
              <span>Payroll Trends</span>
              <div>
                <Dropdown 
                  v-model="trendsPeriod" 
                  :options="periodOptions" 
                  optionLabel="name" 
                  optionValue="value"
                  class="w-10rem"
                  @change="loadTrendsData"
                />
              </div>
            </div>
          </template>
          <template #content>
            <div v-if="trendsLoading" class="flex justify-content-center p-5">
              <ProgressSpinner style="width: 50px; height: 50px" />
            </div>
            <Chart 
              v-else
              type="line" 
              :data="trendsChartData" 
              :options="trendsChartOptions" 
              class="h-20rem"
            />
          </template>
        </Card>
      </div>

      <!-- Cost Distribution -->
      <div class="col-12 lg:col-4">
        <Card>
          <template #title>
            <div class="flex justify-content-between align-items-center">
              <span>Cost by {{ costGroupBy === 'department' ? 'Department' : 'Position' }}</span>
              <Dropdown 
                v-model="costGroupBy" 
                :options="['department', 'position']" 
                class="w-10rem" 
                @change="loadCostAnalysis"
              />
            </div>
          </template>
          <template #content>
            <div v-if="costLoading" class="flex justify-content-center p-5">
              <ProgressSpinner style="width: 50px; height: 50px" />
            </div>
            <Chart 
              v-else
              type="doughnut" 
              :data="costChartData" 
              :options="costChartOptions" 
              class="h-20rem"
            />
          </template>
        </Card>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import { format, subMonths, startOfMonth, endOfMonth } from 'date-fns';

// PrimeVue Components
import Button from 'primevue/button';
import Card from 'primevue/card';
import Chart from 'primevue/chart';
import Dropdown from 'primevue/dropdown';
import ProgressSpinner from 'primevue/progressspinner';
import Breadcrumb from 'primevue/breadcrumb';

// Services
import PayrollAnalyticsService from '@/services/payroll-analytics.service';

export default defineComponent({
  name: 'PayrollAnalytics',
  components: {
    Button,
    Card,
    Chart,
    Dropdown,
    ProgressSpinner,
    Breadcrumb
  },
  setup() {
    const toast = useToast();
    
    // State
    const loading = ref(false);
    const trendsLoading = ref(false);
    const costLoading = ref(false);
    
    // Data
    const summaryStats = ref([
      {
        title: 'Total Payroll',
        value: '$0',
        icon: 'pi pi-dollar',
        color: 'blue-500',
        trend: { value: '0%', icon: 'pi pi-arrow-up', color: 'green-500' }
      },
      {
        title: 'Employees',
        value: '0',
        icon: 'pi pi-users',
        color: 'green-500',
        trend: { value: '0%', icon: 'pi pi-arrow-up', color: 'green-500' }
      },
      {
        title: 'Avg. Salary',
        value: '$0',
        icon: 'pi pi-chart-line',
        color: 'purple-500',
        trend: { value: '0%', icon: 'pi pi-arrow-down', color: 'red-500' }
      },
      {
        title: 'Anomalies',
        value: '0',
        icon: 'pi pi-exclamation-triangle',
        color: 'orange-500',
        trend: { value: '0', icon: 'pi pi-arrow-up', color: 'red-500' }
      }
    ]);
    
    // Charts
    const trendsChartData = ref({
      labels: [],
      datasets: [
        {
          label: 'Payroll Amount',
          data: [],
          fill: false,
          borderColor: '#3B82F6',
          tension: 0.4
        }
      ]
    });
    
    const trendsChartOptions = ref({
      plugins: {
        legend: {
          display: true,
          position: 'top'
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: function(value: any) {
              return '$' + value.toLocaleString();
            }
          }
        }
      },
      responsive: true,
      maintainAspectRatio: false
    });
    
    const costChartData = ref({
      labels: [],
      datasets: [
        {
          data: [],
          backgroundColor: [
            '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6',
            '#EC4899', '#14B8A6', '#F97316', '#8B5CF6', '#EC4899'
          ]
        }
      ]
    });
    
    const costChartOptions = ref({
      plugins: {
        legend: {
          position: 'right'
        },
        tooltip: {
          callbacks: {
            label: function(context: any) {
              const label = context.label || '';
              const value = context.raw || 0;
              const total = context.dataset.data.reduce((a: number, b: number) => a + b, 0);
              const percentage = Math.round((value / total) * 100);
              return `${label}: $${value.toLocaleString()} (${percentage}%)`;
            }
          }
        }
      },
      responsive: true,
      maintainAspectRatio: false
    });
    
    // UI
    const home = ref({
      icon: 'pi pi-home',
      to: '/'
    });
    
    const breadcrumbItems = ref([
      { label: 'Payroll', to: '/payroll' },
      { label: 'Analytics', to: '/payroll/analytics' }
    ]);
    
    const trendsPeriod = ref('monthly');
    const periodOptions = [
      { name: 'Daily', value: 'daily' },
      { name: 'Weekly', value: 'weekly' },
      { name: 'Monthly', value: 'monthly' },
      { name: 'Yearly', value: 'yearly' }
    ];
    
    const costGroupBy = ref('department');
    
    // Methods
    const loadAllData = async () => {
      loading.value = true;
      try {
        await Promise.all([
          loadSummaryStats(),
          loadTrendsData(),
          loadCostAnalysis()
        ]);
      } catch (error) {
        console.error('Error loading data:', error);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to load payroll analytics data',
          life: 5000
        });
      } finally {
        loading.value = false;
      }
    };
    
    const loadSummaryStats = async () => {
      try {
        const response = await PayrollAnalyticsService.getPayrollSummary('current_month');
        const data = response.data;
        
        summaryStats.value = [
          {
            title: 'Total Payroll',
            value: formatCurrency(data.totalPayroll || 0),
            icon: 'pi pi-dollar',
            color: 'blue-500',
            trend: {
              value: formatPercentage(data.payrollChange || 0),
              icon: (data.payrollChange || 0) >= 0 ? 'pi pi-arrow-up' : 'pi pi-arrow-down',
              color: (data.payrollChange || 0) >= 0 ? 'green-500' : 'red-500'
            }
          },
          {
            title: 'Employees',
            value: (data.employeeCount || 0).toLocaleString(),
            icon: 'pi pi-users',
            color: 'green-500',
            trend: {
              value: formatPercentage(data.employeeChange || 0),
              icon: (data.employeeChange || 0) >= 0 ? 'pi pi-arrow-up' : 'pi pi-arrow-down',
              color: (data.employeeChange || 0) >= 0 ? 'green-500' : 'red-500'
            }
          },
          {
            title: 'Avg. Salary',
            value: formatCurrency(data.avgSalary || 0),
            icon: 'pi pi-chart-line',
            color: 'purple-500',
            trend: {
              value: formatPercentage(data.salaryChange || 0),
              icon: (data.salaryChange || 0) >= 0 ? 'pi pi-arrow-up' : 'pi pi-arrow-down',
              color: (data.salaryChange || 0) >= 0 ? 'green-500' : 'red-500'
            }
          },
          {
            title: 'Anomalies',
            value: (data.anomalyCount || 0).toLocaleString(),
            icon: 'pi pi-exclamation-triangle',
            color: 'orange-500',
            trend: {
              value: `${data.anomalyChange || 0 > 0 ? '+' : ''}${data.anomalyChange || 0}`,
              icon: (data.anomalyChange || 0) > 0 ? 'pi pi-arrow-up' : 'pi pi-arrow-right',
              color: (data.anomalyChange || 0) > 0 ? 'red-500' : 'gray-500'
            }
          }
        ];
      } catch (error) {
        console.error('Error loading summary stats:', error);
        throw error;
      }
    };
    
    const loadTrendsData = async () => {
      trendsLoading.value = true;
      try {
        const response = await PayrollAnalyticsService.getPayrollTrends(trendsPeriod.value, 12);
        const data = response.data;
        
        trendsChartData.value = {
          labels: data.labels,
          datasets: [
            {
              label: 'Payroll Amount',
              data: data.datasets[0].data,
              fill: false,
              borderColor: '#3B82F6',
              tension: 0.4
            }
          ]
        };
      } catch (error) {
        console.error('Error loading trends data:', error);
        throw error;
      } finally {
        trendsLoading.value = false;
      }
    };
    
    const loadCostAnalysis = async () => {
      costLoading.value = true;
      try {
        const response = await PayrollAnalyticsService.getCostAnalysis(
          'current_month',
          costGroupBy.value
        );
        const data = response.data;
        
        costChartData.value = {
          labels: data.labels,
          datasets: [
            {
              data: data.datasets[0].data,
              backgroundColor: [
                '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6',
                '#EC4899', '#14B8A6', '#F97316', '#8B5CF6', '#EC4899'
              ]
            }
          ]
        };
      } catch (error) {
        console.error('Error loading cost analysis:', error);
        throw error;
      } finally {
        costLoading.value = false;
      }
    };
    
    const showExportDialog = () => {
      // Implementation for export dialog
      toast.add({
        severity: 'info',
        summary: 'Export',
        detail: 'Export functionality will be implemented here',
        life: 3000
      });
    };
    
    // Helper functions
    const formatCurrency = (value: number): string => {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
      }).format(value);
    };
    
    const formatPercentage = (value: number): string => {
      return `${value > 0 ? '+' : ''}${value.toFixed(1)}%`;
    };
    
    // Lifecycle hooks
    onMounted(() => {
      loadAllData();
    });
    
    return {
      // State
      loading,
      trendsLoading,
      costLoading,
      
      // Data
      summaryStats,
      trendsChartData,
      trendsChartOptions,
      costChartData,
      costChartOptions,
      
      // UI
      home,
      breadcrumbItems,
      trendsPeriod,
      periodOptions,
      costGroupBy,
      
      // Methods
      loadAllData,
      loadTrendsData,
      loadCostAnalysis,
      showExportDialog
    };
  }
});
</script>

<style scoped>
.payroll-analytics {
  padding: 1rem;
}

:deep(.p-card) {
  margin-bottom: 1rem;
  height: 100%;
}

:deep(.p-card .p-card-title) {
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

:deep(.p-chart) {
  width: 100%;
  min-height: 300px;
}

/* Responsive adjustments */
@media (max-width: 960px) {
  :deep(.p-chart) {
    min-height: 250px;
  }
}
</style>
