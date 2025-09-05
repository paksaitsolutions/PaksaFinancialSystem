<template>
  <div class="p-4">
    <!-- Header Section -->
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="text-3xl font-bold m-0">HRM Dashboard</h1>
        <p class="text-color-secondary m-0 mt-2">Manage your human resources efficiently</p>
      </div>
      <div class="flex gap-2">
        <Button icon="pi pi-cog" severity="secondary" @click="showSettings" />
        <Button icon="pi pi-question-circle" severity="secondary" @click="showHelp" />
      </div>
    </div>

    <!-- Quick Navigation Menu -->
    <div class="grid mb-4">
      <div class="col-12 md:col-6 lg:col-2" v-for="(item, index) in quickLinks" :key="index">
        <Button 
          :label="item.label" 
          :icon="item.icon"
          class="w-full"
          severity="secondary"
          @click="navigateTo(item.path)"
        />
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid mb-4">
      <div class="col-12 md:col-6 lg:col-3" v-for="(stat, index) in stats" :key="index">
        <Card>
          <template #content>
            <div class="flex align-items-center">
              <div class="flex align-items-center justify-content-center w-3rem h-3rem border-circle mr-3" 
                   :class="stat.trend >= 0 ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'">
                <i :class="stat.icon" class="text-xl"></i>
              </div>
              <div>
                <div class="text-color-secondary text-sm">{{ stat.title }}</div>
                <div class="text-2xl font-bold">{{ formatNumber(stat.value) || 0 }}</div>
                <div class="text-sm" :class="stat.trend >= 0 ? 'text-green-600' : 'text-red-600'">
                  <i :class="getTrendIcon(stat.trend)" class="mr-1"></i>
                  {{ Math.abs(stat.trend) }}% from last month
                </div>
              </div>
            </div>
          </template>
        </Card>
      </div>
    </div>

    <!-- Main Content -->
    <div class="grid">
      <div class="col-12 lg:col-8">
        <Card>
          <template #title>
            <div class="flex align-items-center gap-2">
              <i class="pi pi-chart-bar text-primary"></i>
              <span>Employee Distribution</span>
            </div>
          </template>
          <template #content>
            <div class="flex align-items-center justify-content-center" style="height: 300px;">
              <p class="text-color-secondary">Employee distribution chart will be displayed here</p>
            </div>
          </template>
        </Card>
      </div>

      <div class="col-12 lg:col-4">
        <Card>
          <template #title>
            <div class="flex align-items-center gap-2">
              <i class="pi pi-calendar text-primary"></i>
              <span>Leave Balance</span>
            </div>
          </template>
          <template #content>
            <div class="flex align-items-center justify-content-center" style="height: 300px;">
              <p class="text-color-secondary">Leave balance chart will be displayed here</p>
            </div>
          </template>
        </Card>
      </div>
    </div>

    <!-- Recent Hires -->
    <div class="grid mt-4">
      <div class="col-12">
        <Card>
          <template #title>Recent Hires</template>
          <template #content>
            <DataTable :value="recentHires" :loading="loading" paginator :rows="5">
              <Column field="name" header="Name" sortable></Column>
              <Column field="position" header="Position" sortable></Column>
              <Column field="department" header="Department" sortable></Column>
              <Column field="startDate" header="Start Date" sortable>
                <template #body="{ data }">
                  {{ formatDate(data.startDate) }}
                </template>
              </Column>
              <Column header="Actions">
                <template #body>
                  <Button icon="pi pi-eye" size="small" />
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
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'primevue/usetoast';
import { useStandardLayout } from '@/composables/useStandardLayout';

const toast = useToast();

// Types
interface StatCard {
  title: string;
  value: number;
  trend: number;
  icon: string;
}

interface QuickLink {
  label: string;
  icon: string;
  path: string;
}

const router = useRouter();
const loading = ref(true);
const { getPageHeaderClass, getStatsGridClass, getStatCardClass } = useStandardLayout();

// Quick navigation links
const quickLinks = ref<QuickLink[]>([
  { label: 'Employees', icon: 'pi pi-users', path: '/hrm/employees' },
  { label: 'Attendance', icon: 'pi pi-calendar-check', path: '/hrm/attendance' },
  { label: 'Leave', icon: 'pi pi-calendar-times', path: '/hrm/leave' },
  { label: 'Payroll', icon: 'pi pi-money-bill', path: '/hrm/payroll' },
  { label: 'Recruitment', icon: 'pi pi-briefcase', path: '/hrm/recruitment' },
  { label: 'Training', icon: 'pi pi-book', path: '/hrm/training' }
]);

// Stats data
const stats = ref<StatCard[]>([
  { title: 'Total Employees', value: 245, trend: 5.2, icon: 'pi pi-users' },
  { title: 'Active Today', value: 218, trend: 2.8, icon: 'pi pi-user-check' },
  { title: 'On Leave', value: 15, trend: -1.2, icon: 'pi pi-calendar-times' },
  { title: 'New Hires', icon: 'pi pi-user-plus', value: 12, trend: 3.5 }
]);

const recentHires = ref([
  { id: 1, name: 'John Doe', position: 'Software Engineer', department: 'IT', startDate: '2023-01-15' },
  { id: 2, name: 'Jane Smith', position: 'HR Manager', department: 'HR', startDate: '2023-01-20' },
  { id: 3, name: 'Mike Johnson', position: 'Accountant', department: 'Finance', startDate: '2023-01-25' },
]);

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
};

const showSettings = () => {
  toast.add({ severity: 'info', summary: 'Settings', detail: 'Opening HRM settings...', life: 3000 });
  router.push('/settings');
};

const showHelp = () => {
  toast.add({ severity: 'info', summary: 'Help', detail: 'Opening help documentation...', life: 3000 });
};

// Navigation
const navigateTo = (path: string) => {
  router.push(path);
};

// Helper functions
const formatNumber = (value: number): string => {
  return new Intl.NumberFormat().format(value);
};



const getTrendIcon = (trend: number): string => {
  return trend > 0 ? 'pi pi-arrow-up' : trend < 0 ? 'pi pi-arrow-down' : 'pi pi-minus';
};

// Simulate loading data
onMounted(async () => {
  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Update stats with dummy data
    stats.value = [
      { title: 'Total Employees', value: 245, trend: 5.2, icon: 'pi pi-users' },
      { title: 'Active Employees', value: 218, trend: 2.8, icon: 'pi pi-user-check' },
      { title: 'On Leave', value: 15, trend: -1.2, icon: 'pi pi-calendar-times' },
      { title: 'New Hires', value: 12, trend: 3.5, icon: 'pi pi-user-plus' }
    ];
  } catch (error) {
    console.error('Error loading dashboard data:', error);
    console.error('Failed to load dashboard data');
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
/* Minimal custom styles - using PrimeFlex for layout */
</style>
