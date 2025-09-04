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
import * as echarts from 'echarts';

const router = useRouter();
const payrollChart = ref<HTMLElement | null>(null);

// Stats data
const stats = ref([
  { title: 'Total Payroll', value: '$124,500', trend: 5.2 },
  { title: 'Employees', value: '87', trend: 2.3 },
  { title: 'Avg. Salary', value: '$4,250', trend: -1.5 },
  { title: 'Upcoming Payroll', value: '$98,200', trend: 3.8 }
]);

// Quick actions
const quickActions = ref([
  { label: 'Process Payroll', icon: 'pi pi-calculator', action: 'process' },
  { label: 'Add Employee', icon: 'pi pi-user-plus', action: 'addEmployee' },
  { label: 'Run Reports', icon: 'pi pi-chart-bar', action: 'reports' },
  { label: 'Tax Filings', icon: 'pi pi-file-pdf', action: 'taxes' }
]);

// Recent activities
const recentActivities = ref([
  {
    title: 'Payroll Processed',
    details: 'Bi-weekly payroll for 85 employees',
    time: '2 hours ago',
    icon: 'pi pi-check-circle',
    color: 'green'
  },
  {
    title: 'New Employee Added',
    details: 'John Doe - Senior Developer',
    time: '1 day ago',
    icon: 'pi pi-user-plus',
    color: 'blue'
  },
  {
    title: 'Tax Filing',
    details: 'Q3 2023 Tax Report submitted',
    time: '3 days ago',
    icon: 'pi pi-file-export',
    color: 'purple'
  },
  {
    title: 'Bonus Processed',
    details: 'Q3 Performance Bonuses',
    time: '1 week ago',
    icon: 'pi pi-money-bill',
    color: 'yellow'
  }
]);

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

// Initialize chart
onMounted(() => {
  if (payrollChart.value) {
    const chart = echarts.init(payrollChart.value);
    const option = {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      legend: {
        data: ['Budget', 'Actual']
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
      },
      yAxis: {
        type: 'value',
        axisLabel: {
          formatter: '${value}'
        }
      },
      series: [
        {
          name: 'Budget',
          type: 'bar',
          data: [120000, 125000, 130000, 135000, 140000, 145000],
          itemStyle: {
            color: '#6366F1' // indigo-500
          }
        },
        {
          name: 'Actual',
          type: 'bar',
          data: [115000, 122000, 128000, 132000, 138000, 147000],
          itemStyle: {
            color: '#10B981' // emerald-500
          }
        }
      ]
    };
    chart.setOption(option);
    
    // Handle window resize
    const handleResize = () => chart.resize();
    window.addEventListener('resize', handleResize);
    
    // Cleanup
    return () => {
      chart.dispose();
      window.removeEventListener('resize', handleResize);
    };
  }
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
