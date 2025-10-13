<template>
  <div class="hrm-dashboard">
    <!-- Header -->
    <div class="dashboard-header">
      <div class="flex align-items-center">
        <i class="pi pi-users text-3xl text-primary mr-3"></i>
        <h1 class="dashboard-title">Human Resources Dashboard</h1>
      </div>
      <div class="header-actions">
        <Button label="New Employee" icon="pi pi-plus" @click="navigateTo('/hrm/employees/new')" />
        <Button label="Reports" icon="pi pi-chart-line" severity="secondary" @click="navigateTo('/hrm/reports')" />
      </div>
    </div>

    <!-- Metrics Cards -->
    <div class="metrics-grid">
      <Card v-for="(metric, i) in dashboardMetrics" :key="i" class="metric-card">
        <template #content>
          <div class="metric-content">
            <div class="metric-header">
              <i :class="metric.icon" :style="{ color: metric.color }" class="text-2xl"></i>
              <span class="metric-value">{{ metric.value }}</span>
            </div>
            <div class="metric-label">{{ metric.label }}</div>
          </div>
        </template>
      </Card>
    </div>

    <!-- Main Content Grid -->
    <div class="content-grid">
      <!-- Quick Actions -->
      <Card class="quick-actions-card">
        <template #header>
          <h3 class="card-title">Quick Actions</h3>
        </template>
        <template #content>
          <div class="actions-list">
            <Button 
              v-for="action in quickActions" 
              :key="action.path"
              :label="action.label" 
              :icon="action.icon" 
              class="action-btn" 
              severity="secondary"
              @click="navigateTo(action.path)" 
            />
          </div>
        </template>
      </Card>

      <!-- Recent Activities -->
      <Card class="activities-card">
        <template #header>
          <div class="flex justify-content-between align-items-center">
            <h3 class="card-title">Recent Activities</h3>
            <Button label="View All" size="small" severity="secondary" @click="viewAllActivities" />
          </div>
        </template>
        <template #content>
          <DataTable :value="recentActivities" :loading="loading" class="compact-table">
            <Column field="date" header="Date">
              <template #body="{ data }">
                {{ formatDate(data.date) }}
              </template>
            </Column>
            <Column field="employee" header="Employee" />
            <Column field="action" header="Action" />
            <Column field="status" header="Status">
              <template #body="{ data }">
                <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
              </template>
            </Column>
          </DataTable>
        </template>
      </Card>
    </div>

    <!-- Department Overview -->
    <Card class="department-overview">
      <template #header>
        <h3 class="card-title">Department Overview</h3>
      </template>
      <template #content>
        <div class="department-grid">
          <div v-for="dept in departments" :key="dept.id" class="department-card">
            <div class="department-header">
              <span class="department-name">{{ dept.name }}</span>
              <span class="employee-count">{{ dept.employee_count }} employees</span>
            </div>
            <div class="department-manager">Manager: {{ dept.manager || 'Not assigned' }}</div>
          </div>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'primevue/usetoast';
import { hrmService, type HRAnalytics } from '@/services/hrmService';

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
const analytics = ref<HRAnalytics | null>(null);

// Quick navigation links
const quickLinks = ref<QuickLink[]>([
  { label: 'Employees', icon: 'pi pi-users', path: '/hrm/employees' },
  { label: 'Attendance', icon: 'pi pi-calendar-check', path: '/hrm/attendance' },
  { label: 'Leave', icon: 'pi pi-calendar-times', path: '/hrm/leave' },
  { label: 'Performance', icon: 'pi pi-chart-line', path: '/hrm/performance' },
  { label: 'Recruitment', icon: 'pi pi-briefcase', path: '/hrm/job-openings' },
  { label: 'Training', icon: 'pi pi-book', path: '/hrm/training' }
]);

// Dashboard data
const dashboardMetrics = ref([
  { id: 'employees', icon: 'pi pi-users', value: 0, label: 'Total Employees', color: 'var(--primary-500)' },
  { id: 'active', icon: 'pi pi-user-check', value: 0, label: 'Active Employees', color: 'var(--success-500)' },
  { id: 'leave', icon: 'pi pi-calendar-times', value: 0, label: 'Pending Leave', color: 'var(--warning-500)' },
  { id: 'departments', icon: 'pi pi-building', value: 0, label: 'Departments', color: 'var(--info-500)' }
])

const quickActions = ref([
  { label: 'Manage Employees', icon: 'pi pi-users', path: '/hrm/employees' },
  { label: 'Attendance', icon: 'pi pi-calendar-check', path: '/hrm/attendance' },
  { label: 'Leave Requests', icon: 'pi pi-calendar-times', path: '/hrm/leave' },
  { label: 'Performance', icon: 'pi pi-chart-line', path: '/hrm/performance' }
])

const recentActivities = ref([])
const departments = ref([])

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

const loadDashboardData = async () => {
  loading.value = true
  try {
    const [employeesResponse, departmentsResponse] = await Promise.all([
      fetch('/api/v1/hrm/employees'),
      fetch('/api/v1/hrm/departments')
    ])
    
    if (employeesResponse.ok) {
      const employees = await employeesResponse.json()
      dashboardMetrics.value[0].value = employees.length
      dashboardMetrics.value[1].value = employees.filter(e => e.status === 'active').length
      
      recentActivities.value = employees.slice(0, 5).map(emp => ({
        date: new Date().toISOString(),
        employee: emp.name,
        action: 'Profile Updated',
        status: 'completed'
      }))
    }
    
    if (departmentsResponse.ok) {
      const depts = await departmentsResponse.json()
      departments.value = depts
      dashboardMetrics.value[3].value = depts.length
    }
  } catch (error) {
    console.error('Error loading dashboard data:', error)
    dashboardMetrics.value.forEach(metric => { metric.value = 0 })
    recentActivities.value = []
    departments.value = []
  } finally {
    loading.value = false
  }
}

const viewAllActivities = () => {
  router.push('/hrm/activities')
}

const getStatusSeverity = (status: string) => {
  switch (status) {
    case 'completed': return 'success'
    case 'pending': return 'warning'
    case 'failed': return 'danger'
    default: return 'info'
  }
}

onMounted(() => {
  loadDashboardData();
});
</script>

<style scoped>
.hrm-dashboard {
  padding: 1.5rem;
  background: var(--surface-ground);
  min-height: 100vh;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding: 1rem;
  background: var(--surface-card);
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.dashboard-title {
  margin: 0;
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-color);
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.metric-card {
  transition: transform 0.2s;
}

.metric-card:hover {
  transform: translateY(-2px);
}

.metric-content {
  padding: 1.5rem;
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.metric-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-color);
}

.metric-label {
  color: var(--text-color-secondary);
  font-size: 0.875rem;
  font-weight: 500;
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.card-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
}

.actions-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.action-btn {
  width: 100%;
  justify-content: flex-start;
}

.compact-table :deep(.p-datatable-tbody td) {
  padding: 0.5rem;
}

.department-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.department-card {
  padding: 1rem;
  background: var(--surface-50);
  border-radius: 6px;
  border: 1px solid var(--surface-border);
}

.department-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.department-name {
  font-weight: 600;
  color: var(--text-color);
}

.employee-count {
  font-size: 0.875rem;
  color: var(--text-color-secondary);
}

.department-manager {
  font-size: 0.875rem;
  color: var(--text-color-secondary);
}

@media (max-width: 768px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
  
  .metrics-grid {
    grid-template-columns: 1fr;
  }
}
</style>
