<template>
  <div class="payroll-analytics">
    <div class="grid">
      <div class="col-12">
        <div class="flex justify-content-between align-items-center mb-4">
          <div>
            <h1>Payroll Analytics Dashboard</h1>
            <p>Gain insights into your payroll data with AI-powered analytics</p>
          </div>
          <div class="flex gap-2">
            <Button 
              icon="pi pi-sync" 
              label="Refresh Data" 
              @click="refreshAll" 
              :loading="store.loading"
              class="p-button-outlined"
            />
            <Button 
              icon="pi pi-download" 
              label="Export Report" 
              @click="exportReport" 
              class="p-button-outlined"
            />
          </div>
        </div>
      </div>

      <!-- Summary Cards -->
      <div class="col-12 md:col-6 lg:col-3">
        <Card>
          <template #title>Total Payroll</template>
          <template #content>
            <div class="text-4xl font-bold text-primary">{{ formatCurrency(summary.totalPayroll) }}</div>
            <div class="mt-2 text-sm text-500">{{ summary.periodLabel }}</div>
            <div class="flex align-items-center mt-2">
              <i :class="['mr-2', summary.trend === 'up' ? 'pi pi-arrow-up text-green-500' : 'pi pi-arrow-down text-red-500']"></i>
              <span :class="summary.trend === 'up' ? 'text-green-500' : 'text-red-500'">
                {{ summary.changePercentage }}% vs previous period
              </span>
            </div>
          </template>
        </Card>
      </div>

      <div class="col-12 md:col-6 lg:col-3">
        <Card>
          <template #title>Employees</template>
          <template #content>
            <div class="text-4xl font-bold">{{ summary.employeeCount }}</div>
            <div class="mt-2 text-sm text-500">Active employees</div>
            <div class="mt-2">
              <span class="text-500">Avg. Salary: </span>
              <span class="font-medium">{{ formatCurrency(summary.averageSalary) }}</span>
            </div>
          </template>
        </Card>
      </div>

      <div class="col-12 md:col-6 lg:3">
        <Card>
          <template #title>Benefits & Taxes</template>
          <template #content>
            <div class="grid">
              <div class="col-6">
                <div class="text-2xl font-bold">{{ formatCurrency(summary.benefitsCost) }}</div>
                <div class="text-sm text-500">Benefits</div>
              </div>
              <div class="col-6">
                <div class="text-2xl font-bold">{{ formatCurrency(summary.taxWithheld) }}</div>
                <div class="text-sm text-500">Taxes</div>
              </div>
            </div>
          </template>
        </Card>
      </div>

      <div class="col-12 md:col-6 lg:3">
        <Card>
          <template #title>Anomalies</template>
          <template #content>
            <div class="grid">
              <div class="col-4 text-center">
                <div class="text-2xl font-bold text-red-500">{{ summary.anomalies.high }}</div>
                <div class="text-sm text-500">High</div>
              </div>
              <div class="col-4 text-center">
                <div class="text-2xl font-bold text-orange-500">{{ summary.anomalies.medium }}</div>
                <div class="text-sm text-500">Medium</div>
              </div>
              <div class="col-4 text-center">
                <div class="text-2xl font-bold text-yellow-500">{{ summary.anomalies.low }}</div>
                <div class="text-sm text-500">Low</div>
              </div>
            </div>
          </template>
        </Card>
      </div>

      <!-- Charts Row 1 -->
      <div class="col-12 lg:8">
        <Card>
          <template #title>Payroll Trend Analysis</template>
          <template #content>
            <div class="flex justify-content-between mb-4">
              <div class="flex gap-2">
                <Button 
                  v-for="period in ['monthly', 'quarterly', 'yearly']" 
                  :key="period"
                  :label="period.charAt(0).toUpperCase() + period.slice(1)"
                  :class="{ 'p-button-outlined': trendPeriod !== period }"
                  @click="setTrendPeriod(period as any)"
                />
              </div>
              <Dropdown 
                v-model="selectedDepartment" 
                :options="departments" 
                optionLabel="name" 
                optionValue="id"
                placeholder="All Departments"
                style="width: 200px"
                showClear
              />
            </div>
            <div class="h-25rem">
              <Chart 
                type="line" 
                :data="trendChartData" 
                :options="trendChartOptions" 
              />
            </div>
          </template>
        </Card>
      </div>

      <div class="col-12 lg:4">
        <Card>
          <template #title>Cost Distribution</template>
          <template #content>
            <div class="h-25rem">
              <Chart 
                type="doughnut" 
                :data="costDistributionData" 
                :options="doughnutOptions" 
              />
            </div>
          </template>
        </Card>
      </div>

      <!-- Anomalies Table -->
      <div class="col-12">
        <Card>
          <template #title>
            <div class="flex align-items-center">
              <span>Anomaly Detection</span>
              <Tag 
                :value="`${store.anomalies.length} detected`" 
                :severity="store.anomalies.length > 0 ? 'danger' : 'success'" 
                class="ml-3"
              />
            </div>
          </template>
          <template #content>
            <DataTable 
              :value="store.anomalies" 
              :paginator="true" 
              :rows="5"
              :loading="store.loading"
              class="p-datatable-sm"
            >
              <Column field="date" header="Date" style="width: 120px">
                <template #body="{ data }">
                  {{ formatDate(data.date) }}
                </template>
              </Column>
              <Column field="type" header="Type" style="width: 120px">
                <template #body="{ data }">
                  <Tag 
                    :value="data.type.charAt(0).toUpperCase() + data.type.slice(1)"
                    :severity="getSeverity(data.severity)"
                  />
                </template>
              </Column>
              <Column field="description" header="Description" />
              <Column field="amount" header="Amount" style="width: 150px">
                <template #body="{ data }">
                  {{ formatCurrency(data.amount) }}
                  <span v-if="data.expectedAmount" class="text-500">
                    (exp. {{ formatCurrency(data.expectedAmount) }})
                  </span>
                </template>
              </Column>
              <Column field="variance" header="Variance" style="width: 120px">
                <template #body="{ data }">
                  <span :class="data.variance > 0 ? 'text-green-500' : 'text-red-500'">
                    {{ data.variance > 0 ? '+' : '' }}{{ formatCurrency(data.variance) }}
                  </span>
                </template>
              </Column>
              <Column field="severity" header="Severity" style="width: 120px">
                <template #body="{ data }">
                  <Tag 
                    :value="data.severity.charAt(0).toUpperCase() + data.severity.slice(1)"
                    :severity="getSeverity(data.severity)"
                  />
                </template>
              </Column>
              <Column headerStyle="width: 4rem; text-align: center" bodyStyle="text-align: center; overflow: visible">
                <template #body>
                  <Button icon="pi pi-search" class="p-button-text" @click="viewAnomalyDetails" />
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </div>

      <!-- Predictive Insights -->
      <div class="col-12 lg:6">
        <Card>
          <template #title>Predictive Insights</template>
          <template #content>
            <div v-if="store.predictiveInsights.length === 0" class="text-center p-4">
              <p class="text-500">No predictive insights available. Run analysis to generate insights.</p>
              <Button 
                label="Run Analysis" 
                icon="pi pi-chart-line" 
                class="mt-3"
                @click="runPredictiveAnalysis"
                :loading="store.loading"
              />
            </div>
            <div v-else>
              <div v-for="(insight, index) in store.predictiveInsights" :key="index" class="mb-4">
                <div class="font-medium">{{ insight.metric }}</div>
                <div class="flex align-items-center">
                  <div class="text-2xl font-bold mr-3">{{ formatCurrency(insight.currentValue) }}</div>
                  <div class="flex flex-column">
                    <div class="flex align-items-center">
                      <i :class="['mr-1', insight.trend === 'increasing' ? 'pi pi-arrow-up text-green-500' : 'pi pi-arrow-down text-red-500']"></i>
                      <span>Predicted: {{ formatCurrency(insight.predictedValue) }}</span>
                    </div>
                    <div class="text-xs text-500">Confidence: {{ (insight.confidence * 100).toFixed(1) }}%</div>
                  </div>
                </div>
                <div v-if="insight.recommendations.length > 0" class="mt-2">
                  <div class="text-sm font-medium mb-1">Recommendations:</div>
                  <ul class="m-0 pl-4">
                    <li v-for="(rec, i) in insight.recommendations" :key="i" class="text-sm">
                      {{ rec }}
                    </li>
                  </ul>
                </div>
                <Divider v-if="index < store.predictiveInsights.length - 1" />
              </div>
            </div>
          </template>
        </Card>
      </div>

      <!-- Cost Analysis by Department -->
      <div class="col-12 lg:6">
        <Card>
          <template #title>Cost Analysis by Department</template>
          <template #content>
            <DataTable 
              :value="store.costAnalysis" 
              :paginator="true" 
              :rows="5"
              :loading="store.loading"
              class="p-datatable-sm"
            >
              <Column field="department" header="Department" sortable />
              <Column field="totalPayroll" header="Total Payroll" sortable>
                <template #body="{ data }">
                  {{ formatCurrency(data.totalPayroll) }}
                </template>
              </Column>
              <Column field="employeeCount" header="Employees" sortable />
              <Column field="costPerEmployee" header="Cost/Employee" sortable>
                <template #body="{ data }">
                  {{ formatCurrency(data.costPerEmployee) }}
                </template>
              </Column>
              <Column field="percentageOfTotal" header="% of Total" sortable>
                <template #body="{ data }">
                  <div class="flex align-items-center">
                    <div class="w-8rem">
                      <ProgressBar 
                        :value="data.percentageOfTotal * 100" 
                        :showValue="false"
                        :style="{ height: '0.5rem' }"
                      />
                    </div>
                    <span class="ml-2">{{ (data.percentageOfTotal * 100).toFixed(1) }}%</span>
                  </div>
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { usePayrollAnalyticsStore } from '../store/payroll-analytics';
import { formatCurrency, formatDate } from '@/utils/formatters';
import { useRouter } from 'vue-router';

const router = useRouter();
const store = usePayrollAnalyticsStore();

// State
const trendPeriod = ref<'monthly' | 'quarterly' | 'yearly'>('monthly');
const selectedDepartment = ref<string | null>(null);

// Mock data - replace with actual API calls
const departments = ref([
  { id: 'dept1', name: 'Engineering' },
  { id: 'dept2', name: 'Marketing' },
  { id: 'dept3', name: 'Sales' },
  { id: 'dept4', name: 'HR' },
]);

// Summary data - replace with actual computed properties from store
const summary = computed(() => ({
  totalPayroll: 1250000,
  employeeCount: 42,
  averageSalary: 65000,
  benefitsCost: 250000,
  taxWithheld: 375000,
  periodLabel: 'Current Month',
  trend: 'up',
  changePercentage: 4.2,
  anomalies: {
    high: 2,
    medium: 5,
    low: 3
  }
}));

// Chart data - replace with actual computed properties from store
const trendChartData = computed(() => {
  const documentStyle = getComputedStyle(document.documentElement);
  
  return {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
    datasets: [
      {
        label: 'Gross Payroll',
        data: [65, 59, 80, 81, 56, 55, 40],
        fill: false,
        borderColor: documentStyle.getPropertyValue('--primary-color'),
        tension: 0.4
      },
      {
        label: 'Benefits',
        data: [28, 48, 40, 19, 86, 27, 90],
        fill: false,
        borderColor: documentStyle.getPropertyValue('--green-500'),
        tension: 0.4
      },
      {
        label: 'Taxes',
        data: [35, 40, 45, 42, 43, 42, 40],
        fill: false,
        borderColor: documentStyle.getPropertyValue('--red-500'),
        tension: 0.4
      }
    ]
  };
});

const trendChartOptions = computed(() => ({
  maintainAspectRatio: false,
  aspectRatio: 0.6,
  plugins: {
    legend: {
      position: 'top'
    },
    tooltip: {
      callbacks: {
        label: function(context: any) {
          return `${context.dataset.label}: ${formatCurrency(context.raw)}`;
        }
      }
    }
  },
  scales: {
    y: {
      ticks: {
        callback: function(value) {
          return formatCurrency(Number(value));
        }
      }
    }
  }
}));

const costDistributionData = computed(() => {
  const documentStyle = getComputedStyle(document.documentElement);
  
  return {
    labels: ['Base Salary', 'Bonuses', 'Overtime', 'Benefits', 'Taxes'],
    datasets: [
      {
        data: [60, 15, 5, 12, 8],
        backgroundColor: [
          documentStyle.getPropertyValue('--primary-500'),
          documentStyle.getPropertyValue('--green-500'),
          documentStyle.getPropertyValue('--yellow-500'),
          documentStyle.getPropertyValue('--blue-500'),
          documentStyle.getPropertyValue('--red-500')
        ],
        hoverBackgroundColor: [
          documentStyle.getPropertyValue('--primary-400'),
          documentStyle.getPropertyValue('--green-400'),
          documentStyle.getPropertyValue('--yellow-400'),
          documentStyle.getPropertyValue('--blue-400'),
          documentStyle.getPropertyValue('--red-400')
        ]
      }
    ]
  };
});

const doughnutOptions = {
  cutout: '60%',
  maintainAspectRatio: false,
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
          return `${label}: ${percentage}% (${formatCurrency(value * 1000)})`;
        }
      }
    }
  }
};

// Methods
function setTrendPeriod(period: 'monthly' | 'quarterly' | 'yearly') {
  trendPeriod.value = period;
  // TODO: Fetch data for the selected period
}

function refreshAll() {
  // TODO: Implement refresh logic
  store.fetchTrendAnalysis({
    period: trendPeriod.value,
    limit: 12,
    departmentId: selectedDepartment.value || undefined
  });
  
  store.detectAnomalies({
    startDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    endDate: new Date().toISOString().split('T')[0]
  });
  
  store.fetchCostAnalysis({
    period: 'current_month',
    groupBy: 'department'
  });
}

function exportReport() {
  // TODO: Implement export logic
  console.log('Exporting report...');
}

function viewAnomalyDetails() {
  // TODO: Navigate to anomaly details
  console.log('Viewing anomaly details...');
}

function runPredictiveAnalysis() {
  // TODO: Implement predictive analysis
  store.fetchPredictiveInsights({
    forecastPeriods: 3,
    confidenceThreshold: 0.8
  });
}

function getSeverity(severity: string) {
  switch (severity) {
    case 'high': return 'danger';
    case 'medium': return 'warning';
    case 'low': return 'info';
    default: return 'info';
  }
}

// Lifecycle hooks
onMounted(() => {
  // Initial data load
  refreshAll();
});
</script>

<style scoped>
.payroll-analytics :deep(.p-card) {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.payroll-analytics :deep(.p-card-content) {
  flex: 1;
  display: flex;
  flex-direction: column;
}
</style>
