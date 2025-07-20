<template>
  <div class="payroll-dashboard">
    <v-container fluid>
      <v-row>
        <v-col cols="12">
          <v-card class="mb-6">
            <v-card-title class="d-flex justify-space-between align-center">
              <span>Payroll Overview</span>
              <v-btn
                color="primary"
                :to="{ name: 'payroll-run-create' }"
                prepend-icon="mdi-plus"
              >
                New Pay Run
              </v-btn>
            </v-card-title>
            
            <v-card-text>
              <v-row>
                <v-col v-for="(stat, index) in stats" :key="index" cols="12" sm="6" md="3">
                  <v-card variant="flat" class="text-center pa-4">
                    <div class="text-h6 text-medium-emphasis">{{ stat.title }}</div>
                    <div class="text-h4 font-weight-bold">{{ stat.value }}</div>
                    <v-divider class="my-2"></v-divider>
                    <div class="text-caption" :class="stat.trend > 0 ? 'text-success' : 'text-error'">
                      <v-icon :icon="stat.trend > 0 ? 'mdi-arrow-up' : 'mdi-arrow-down'" size="small"></v-icon>
                      {{ Math.abs(stat.trend) }}% from last period
                    </div>
                  </v-card>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>

          <v-row>
            <v-col cols="12" md="8">
              <v-card class="mb-6">
                <v-card-title>Payroll Summary</v-card-title>
                <v-card-text>
                  <div ref="payrollChart" style="height: 300px;"></div>
                </v-card-text>
              </v-card>
            </v-col>
            
            <v-col cols="12" md="4">
              <v-card class="mb-6">
                <v-card-title>Quick Actions</v-card-title>
                <v-card-text>
                  <v-list>
                    <v-list-item
                      v-for="(action, i) in quickActions"
                      :key="i"
                      :to="action.to"
                      :prepend-icon="action.icon"
                      :title="action.title"
                      :subtitle="action.subtitle"
                      link
                      class="mb-2"
                      variant="tonal"
                    ></v-list-item>
                  </v-list>
                </v-card-text>
              </v-card>
              
              <v-card>
                <v-card-title>Recent Activity</v-card-title>
                <v-card-text>
                  <v-timeline density="compact" align="start">
                    <v-timeline-item
                      v-for="(activity, i) in recentActivities"
                      :key="i"
                      :dot-color="activity.color"
                      size="small"
                    >
                      <div class="d-flex">
                        <div>
                          <div class="text-caption">{{ activity.time }}</div>
                          <div class="font-weight-bold">{{ activity.title }}</div>
                          <div class="text-caption">{{ activity.details }}</div>
                        </div>
                      </div>
                    </v-timeline-item>
                  </v-timeline>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import * as echarts from 'echarts';

export default defineComponent({
  name: 'PayrollView',
  
  setup() {
    const router = useRouter();
    const payrollChart = ref<HTMLElement | null>(null);
    
    const stats = ref([
      { title: 'Total Payroll', value: '$124,560', trend: 5.2 },
      { title: 'Employees', value: '87', trend: 2.3 },
      { title: 'This Period', value: '$62,340', trend: -1.8 },
      { title: 'Pending Approvals', value: '3', trend: 0 },
    ]);
    
    const quickActions = ref([
      { 
        title: 'Process Payroll', 
        subtitle: 'Run payroll for current period',
        icon: 'mdi-cash-multiple',
        to: { name: 'payroll-run-create' }
      },
      { 
        title: 'View Pay Runs', 
        subtitle: 'View all pay run history',
        icon: 'mdi-calendar-check',
        to: { name: 'payroll-runs' }
      },
      { 
        title: 'Employee Management', 
        subtitle: 'Manage employee payroll details',
        icon: 'mdi-account-group',
        to: { name: 'payroll-employees' }
      },
      { 
        title: 'Run Reports', 
        subtitle: 'Generate payroll reports',
        icon: 'mdi-file-chart',
        to: { name: 'payroll-reports' }
      },
    ]);
    
    const recentActivities = ref([
      {
        title: 'Payroll Processed',
        details: 'Bi-weekly payroll for 85 employees',
        time: '2 hours ago',
        color: 'primary'
      },
      {
        title: 'New Employee Added',
        details: 'John Doe (Sales Department)',
        time: '1 day ago',
        color: 'success'
      },
      {
        title: 'Tax Update',
        details: 'Updated tax rates for Q3 2023',
        time: '3 days ago',
        color: 'info'
      },
      {
        title: 'Payroll Approved',
        details: 'Payroll #2023-08-15 approved',
        time: '1 week ago',
        color: 'success'
      },
    ]);
    
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
            data: ['Salary', 'Bonuses', 'Deductions', 'Net Pay']
          },
          grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
          },
          xAxis: {
            type: 'category',
            data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul']
          },
          yAxis: {
            type: 'value',
            axisLabel: {
              formatter: '${value}K'
            }
          },
          series: [
            {
              name: 'Salary',
              type: 'bar',
              stack: 'total',
              emphasis: {
                focus: 'series'
              },
              data: [120, 122, 121, 124, 129, 133, 135]
            },
            {
              name: 'Bonuses',
              type: 'bar',
              stack: 'total',
              emphasis: {
                focus: 'series'
              },
              data: [20, 22, 21, 24, 29, 23, 25]
            },
            {
              name: 'Deductions',
              type: 'bar',
              stack: 'total',
              emphasis: {
                focus: 'series'
              },
              data: [-32, -30, -34, -31, -35, -33, -34]
            },
            {
              name: 'Net Pay',
              type: 'line',
              emphasis: {
                focus: 'series'
              },
              data: [108, 114, 108, 117, 123, 123, 126]
            }
          ]
        };
        
        chart.setOption(option);
        
        // Handle window resize
        const handleResize = () => {
          chart.resize();
        };
        
        window.addEventListener('resize', handleResize);
        
        // Cleanup
        return () => {
          window.removeEventListener('resize', handleResize);
          chart.dispose();
        };
      }
    });
    
    return {
      stats,
      quickActions,
      recentActivities,
      payrollChart
    };
  }
});
</script>

<style scoped>
.payroll-dashboard {
  height: 100%;
  overflow-y: auto;
}
</style>
