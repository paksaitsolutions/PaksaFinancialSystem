<template>
  <div class="payroll-dashboard">
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1>Payroll Overview</h1>
        <p class="text-color-secondary">Manage payroll processing and employee compensation</p>
      </div>
      <Button label="New Pay Run" icon="pi pi-plus" @click="createPayRun" />
    </div>

    <Card class="mb-4">
      <template #content>
        <div class="grid">
          <div class="col-12 sm:col-6 md:col-3" v-for="(stat, index) in stats" :key="index">
            <Card class="text-center">
              <template #content>
                <div class="text-color-secondary text-sm mb-2">{{ stat.title }}</div>
                <div class="text-3xl font-bold mb-2">{{ stat.value }}</div>
                <Divider />
                <div class="text-sm" :class="stat.trend > 0 ? 'text-green-600' : 'text-red-600'">
                  <i :class="stat.trend > 0 ? 'pi pi-arrow-up' : 'pi pi-arrow-down'" class="mr-1"></i>
                  {{ Math.abs(stat.trend) }}% from last period
                </div>
              </template>
            </Card>
          </div>
        </div>
      </template>
    </Card>

    <div class="grid">
      <div class="col-12 md:col-8">
        <Card class="mb-4">
          <template #title>Payroll Summary</template>
          <template #content>
            <div ref="payrollChart" style="height: 300px;" class="flex align-items-center justify-content-center">
              <div class="text-center">
                <i class="pi pi-chart-bar text-4xl text-primary mb-3"></i>
                <p class="text-color-secondary">Payroll chart will be displayed here</p>
              </div>
            </div>
          </template>
        </Card>
      </div>
      
      <div class="col-12 md:col-4">
        <Card class="mb-4">
          <template #title>Quick Actions</template>
          <template #content>
            <div class="flex flex-column gap-2">
              <Button
                v-for="(action, i) in quickActions"
                :key="i"
                :label="action.title"
                :icon="action.icon"
                class="w-full p-button-outlined"
                @click="navigateToAction(action)"
              />
            </div>
          </template>
        </Card>
        
        <Card>
          <template #title>Recent Activity</template>
          <template #content>
            <Timeline :value="recentActivities" class="w-full">
              <template #content="{ item }">
                <div>
                  <div class="text-sm text-color-secondary">{{ item.time }}</div>
                  <div class="font-bold">{{ item.title }}</div>
                  <div class="text-sm text-color-secondary">{{ item.details }}</div>
                </div>
              </template>
            </Timeline>
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

const router = useRouter();
const toast = useToast();
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
    icon: 'pi pi-dollar',
    action: 'process-payroll'
  },
  { 
    title: 'View Pay Runs', 
    subtitle: 'View all pay run history',
    icon: 'pi pi-calendar',
    action: 'view-payruns'
  },
  { 
    title: 'Employee Management', 
    subtitle: 'Manage employee payroll details',
    icon: 'pi pi-users',
    action: 'manage-employees'
  },
  { 
    title: 'Run Reports', 
    subtitle: 'Generate payroll reports',
    icon: 'pi pi-file',
    action: 'run-reports'
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

const createPayRun = () => {
  toast.add({ severity: 'info', summary: 'Pay Run', detail: 'Creating new pay run...', life: 3000 })
  router.push('/payroll/pay-runs/create')
}

const navigateToAction = (action: any) => {
  switch (action.action) {
    case 'process-payroll':
      toast.add({ severity: 'info', summary: 'Process Payroll', detail: 'Processing payroll...', life: 3000 })
      break
    case 'view-payruns':
      router.push('/payroll/pay-runs')
      break
    case 'manage-employees':
      router.push('/payroll/employees')
      break
    case 'run-reports':
      router.push('/payroll/reports')
      break
    default:
      toast.add({ severity: 'info', summary: 'Action', detail: action.title, life: 3000 })
  }
}

onMounted(() => {
  // Initialize component
});
</script>

<style scoped>
.payroll-dashboard {
  height: 100%;
  overflow-y: auto;
}
</style>
