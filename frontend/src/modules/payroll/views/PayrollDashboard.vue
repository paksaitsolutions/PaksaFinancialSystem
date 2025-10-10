<template>
  <div class="payroll-module">
    <div class="flex justify-content-between align-items-center mb-4">
      <h1>Payroll Management</h1>
      <Button 
        label="New Pay Run" 
        icon="pi pi-plus" 
        class="p-button-primary"
        @click="startNewPayRun"
      />
    </div>
    
    <!-- Stats Cards -->
    <div class="grid">
      <div 
        v-for="(stat, index) in stats" 
        :key="index" 
        class="col-12 md:col-6 lg:col-3"
      >
        <Card class="h-full">
          <template #title>
            <div class="text-500 text-sm font-medium">{{ stat.title }}</div>
          </template>
          <template #content>
            <div class="text-3xl font-bold mb-2">{{ stat.value }}</div>
            <div class="flex align-items-center">
              <span 
                class="flex align-items-center" 
                :class="stat.trend > 0 ? 'text-green-500' : 'text-red-500'"
              >
                <i :class="stat.trend > 0 ? 'pi pi-arrow-up' : 'pi pi-arrow-down'" class="mr-1"></i>
                {{ Math.abs(stat.trend) }}%
              </span>
              <span class="text-500 text-sm ml-2">vs last period</span>
            </div>
          </template>
        </Card>
      </div>
    </div>
    
    <!-- Main Content -->
    <div class="grid mt-4">
      <!-- Payroll Summary Chart -->
      <div class="col-12 lg:col-8">
        <Card>
          <template #title>Payroll Summary</template>
          <template #content>
            <div ref="payrollChart" style="height: 350px;"></div>
          </template>
        </Card>
      </div>
      
      <!-- Quick Actions & Recent Activity -->
      <div class="col-12 lg:col-4">
        <!-- Quick Actions -->
        <Card class="mb-4">
          <template #title>Quick Actions</template>
          <template #content>
            <div class="flex flex-column gap-3">
              <Button 
                v-for="(action, i) in quickActions"
                :key="'action-' + i"
                :label="action.label"
                :icon="action.icon"
                class="p-button-outlined p-button-secondary text-left justify-content-start"
                @click="handleQuickAction(action)"
              />
            </div>
          </template>
        </Card>
        
        <!-- Recent Activity -->
        <Card>
          <template #title>Recent Activity</template>
          <template #content>
            <ul class="list-none p-0 m-0">
              <li 
                v-for="(activity, i) in recentActivities" 
                :key="'activity-' + i"
                class="flex align-items-start mb-3 pb-2 border-bottom-1 surface-border"
              >
                <div 
                  class="flex align-items-center justify-content-center border-circle w-3rem h-3rem"
                  :class="'bg-' + activity.color + '100'"
                >
                  <i :class="activity.icon" :class="'text-' + activity.color + '500'"></i>
                </div>
                <div class="ml-3">
                  <div class="font-medium">{{ activity.title }}</div>
                  <div class="text-500 text-sm">{{ activity.time }}</div>
                  <div class="text-500 text-sm">{{ activity.details }}</div>
                </div>
              </li>
            </ul>
          </template>
        </Card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'primevue/usetoast';
import * as echarts from 'echarts';
import { payrollService } from '@/services/payrollService';
import { formatCurrency } from '@/utils/formatters';

const router = useRouter();
const toast = useToast();
const payrollChart = ref<HTMLElement | null>(null);
const loading = ref(false);

// Stats data
const stats = ref([
  { title: 'Total Payroll', value: '$0', trend: 0 },
  { title: 'Employees', value: '0', trend: 0 },
  { title: 'Avg. Salary', value: '$0', trend: 0 },
  { title: 'Upcoming Payroll', value: '$0', trend: 0 }
]);

// Quick actions
const quickActions = ref([
  { label: 'Process Payroll', icon: 'pi pi-calculator', action: 'process' },
  { label: 'Add Employee', icon: 'pi pi-user-plus', action: 'addEmployee' },
  { label: 'Run Reports', icon: 'pi pi-chart-bar', action: 'reports' },
  { label: 'Tax Filings', icon: 'pi pi-file-pdf', action: 'taxes' }
]);

// Recent activities
const recentActivities = ref([]);

// Methods
const startNewPayRun = () => {
  router.push({ name: 'payroll-run-create' });
};

const handleQuickAction = (action: { action: string }) => {
  switch (action.action) {
    case 'process':
      router.push({ name: 'payroll-run' });
      break;
    case 'addEmployee':
      router.push({ name: 'employee-create' });
      break;
    case 'reports':
      router.push({ name: 'payroll-reports' });
      break;
    case 'taxes':
      router.push({ name: 'payroll-taxes' });
      break;
  }
};

// Load dashboard data
const loadDashboardData = async () => {
  loading.value = true;
  try {
    const [kpiData, summaryData, activityData] = await Promise.all([
      payrollService.getPayrollKPIs(),
      payrollService.getPayrollSummary(6),
      payrollService.getRecentActivity(4)
    ]);
    
    // Update stats
    stats.value = [
      { title: 'Total Payroll', value: formatCurrency(kpiData.total_payroll), trend: kpiData.payroll_change },
      { title: 'Employees', value: kpiData.total_employees.toString(), trend: kpiData.employee_change },
      { title: 'Avg. Salary', value: formatCurrency(kpiData.average_salary), trend: kpiData.salary_change },
      { title: 'Upcoming Payroll', value: formatCurrency(kpiData.upcoming_payroll), trend: 3.8 }
    ];
    
    // Update recent activities
    recentActivities.value = activityData.map(activity => ({
      title: activity.title,
      details: activity.details,
      time: formatTimeAgo(new Date(activity.timestamp)),
      icon: getActivityIcon(activity.type),
      color: getActivityColor(activity.type)
    }));
    
    // Initialize chart with real data
    if (payrollChart.value) {
      const chart = echarts.init(payrollChart.value);
      const option = {
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'shadow' }
        },
        legend: { data: ['Budget', 'Actual'] },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: {
          type: 'category',
          data: summaryData.monthly_data.map(d => d.month)
        },
        yAxis: {
          type: 'value',
          axisLabel: { formatter: '${value}' }
        },
        series: [
          {
            name: 'Budget',
            type: 'bar',
            data: summaryData.monthly_data.map(d => d.budget),
            itemStyle: { color: '#6366F1' }
          },
          {
            name: 'Actual',
            type: 'bar',
            data: summaryData.monthly_data.map(d => d.actual),
            itemStyle: { color: '#10B981' }
          }
        ]
      };
      chart.setOption(option);
      
      const handleResize = () => chart.resize();
      window.addEventListener('resize', handleResize);
    }
    
  } catch (error) {
    console.error('Error loading dashboard data:', error);
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load payroll data' });
  } finally {
    loading.value = false;
  }
};

const formatTimeAgo = (date: Date) => {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffHours / 24);
  
  if (diffHours < 24) return `${diffHours} hours ago`;
  if (diffDays === 1) return '1 day ago';
  if (diffDays < 7) return `${diffDays} days ago`;
  return `${Math.floor(diffDays / 7)} week${Math.floor(diffDays / 7) > 1 ? 's' : ''} ago`;
};

const getActivityIcon = (type: string) => {
  const icons = {
    payroll_processed: 'pi pi-check-circle',
    employee_added: 'pi pi-user-plus',
    tax_filing: 'pi pi-file-export',
    bonus_processed: 'pi pi-money-bill'
  };
  return icons[type] || 'pi pi-circle';
};

const getActivityColor = (type: string) => {
  const colors = {
    payroll_processed: 'green',
    employee_added: 'blue',
    tax_filing: 'purple',
    bonus_processed: 'yellow'
  };
  return colors[type] || 'gray';
};

// Initialize dashboard
onMounted(() => {
  loadDashboardData();
});
</script>

<style scoped>
.payroll-module {
  padding: 1.5rem;
}

h1 {
  color: var(--primary-color);
  margin: 0;
}

:deep(.p-card) {
  height: 100%;
  display: flex;
  flex-direction: column;
}

:deep(.p-card-content) {
  flex: 1;
}
</style>
