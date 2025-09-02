<template>
  <div class="hrm-dashboard">
    <!-- Navigation Menu -->
    <HrmMenu />
    
    <!-- Main Content -->
    <div class="grid">
      <div class="col-12">
        <div class="flex justify-content-between align-items-center">
          <div>
            <h1 class="text-3xl font-bold mb-2">HRM Dashboard</h1>
            <Breadcrumb :home="home" :model="items" class="mb-4" />
          </div>
          <div class="flex gap-2">
            <Button icon="pi pi-cog" class="p-button-text" @click="showSettings" />
            <Button icon="pi pi-question-circle" class="p-button-text" @click="showHelp" />
          </div>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="col-12 md:col-6 lg:col-3">
        <Card>
          <template #title>Total Employees</template>
          <template #content>
            <div class="text-4xl font-bold mb-3">{{ stats.totalEmployees || 0 }}</div>
            <div class="flex justify-content-between">
              <span class="text-green-500 font-medium">+12%</span>
              <span class="text-500">vs last month</span>
            </div>
          </template>
        </Card>
      </div>

      <div class="col-12 md:col-6 lg:col-3">
        <Card>
          <template #title>On Leave Today</template>
          <template #content>
            <div class="text-4xl font-bold mb-3">{{ stats.onLeave || 0 }}</div>
            <div class="flex justify-content-between">
              <span class="text-red-500 font-medium">+3%</span>
              <span class="text-500">vs last month</span>
            </div>
          </template>
        </Card>
      </div>

      <div class="col-12 md:col-6 lg:col-3">
        <Card>
          <template #title>Open Positions</template>
          <template #content>
            <div class="text-4xl font-bold mb-3">{{ stats.openPositions || 0 }}</div>
            <div class="flex justify-content-between">
              <span class="text-yellow-500 font-medium">+5%</span>
              <span class="text-500">vs last month</span>
            </div>
          </template>
        </Card>
      </div>

      <div class="col-12 md:col-6 lg:col-3">
        <Card>
          <template #title>Departments</template>
          <template #content>
            <div class="text-4xl font-bold mb-3">{{ stats.totalDepartments || 0 }}</div>
            <div class="flex justify-content-between">
              <span class="text-green-500 font-medium">+2%</span>
              <span class="text-500">vs last month</span>
            </div>
          </template>
        </Card>
      </div>

      <!-- Main Content -->
      <div class="col-12 lg:col-8">
        <Card>
          <template #title>Employee Distribution</template>
          <template #content>
            <Chart type="bar" :data="departmentChart" :options="chartOptions" />
          </template>
        </Card>
      </div>

      <div class="col-12 lg:col-4">
        <Card>
          <template #title>Leave Balance</template>
          <template #content>
            <Chart type="doughnut" :data="leaveChart" :options="chartOptions" />
          </template>
        </Card>
      </div>

      <!-- Recent Activities -->
      <div class="col-12">
        <Card>
          <template #title>Recent Activities</template>
          <template #content>
            <DataTable :value="recentActivities" :loading="loading" scrollable class="p-datatable-sm" 
               :paginator="recentActivities.length > 5" :rows="5" 
               :rowsPerPageOptions="[5,10,25,50]" 
               paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
               currentPageReportTemplate="Showing {first} to {last} of {totalRecords} entries"
                      responsiveLayout="scroll">
              <Column field="date" header="Date" :sortable="true">
                <template #body="{data}">
                  {{ formatDate(data.date) }}
                </template>
              </Column>
              <Column field="employee" header="Employee" :sortable="true"></Column>
              <Column field="activity" header="Activity" :sortable="true"></Column>
              <Column field="status" header="Status" :sortable="true">
                <template #body="{ data }">
                  <Tag :value="data.status" :severity="getStatusSeverity(data.status) || 'info'" />
                </template>
              </Column>
              <Column header="Actions">
                <template #body>
                  <Button icon="pi pi-eye" class="p-button-text p-button-rounded" />
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, computed } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useRoute } from 'vue-router';
import HrmMenu from '@/components/hrm/HrmMenu.vue';

export default defineComponent({
  name: 'HrmDashboard',
  components: {
    HrmMenu
  },
  setup() {
    const route = useRoute();
    const toast = useToast();
    const loading = ref(false);
    
    const pageTitle = computed(() => {
      // Get the title from the matched route or use default
      return route.meta.title || 'HRM Dashboard';
    });
    interface DashboardStats {
      totalEmployees: number;
      onLeave: number;
      openPositions: number;
      totalDepartments: number;
      loading: boolean;
      error: string | null;
    }

    const stats = ref<DashboardStats>({
      totalEmployees: 0,
      onLeave: 0,
      openPositions: 0,
      totalDepartments: 0,
      loading: false,
      error: null
    });

    const home = ref({ icon: 'pi pi-home', to: { name: 'Dashboard' } });
    interface BreadcrumbItem {
      label: string;
      to?: { name: string };
    }

    const items = computed((): BreadcrumbItem[] => {
      const breadcrumbs: BreadcrumbItem[] = [{ label: 'HRM', to: { name: 'HRM' } }];
      
      // Add dynamic breadcrumbs based on current route
      if (route.name !== 'HRM') {
        const routeName = route.name?.toString() || '';
        const breadcrumb: BreadcrumbItem = {
          label: (route.meta?.title as string) || routeName
        };
        
        if (routeName) {
          breadcrumb.to = { name: routeName };
        }
        
        breadcrumbs.push(breadcrumb);
      } else {
        breadcrumbs.push({ label: 'Dashboard', to: { name: 'HRM' } });
      }
      
      return breadcrumbs;
    });

    interface ChartData {
      labels: string[];
      datasets: Array<{
        label: string;
        backgroundColor: string | string[];
        data: number[];
        borderColor?: string;
        borderWidth?: number;
      }>;
    }

    const departmentChart = ref<ChartData>({
      labels: [],
      datasets: [
        {
          label: 'Employees',
          backgroundColor: '#42A5F5',
          data: [],
          borderColor: '#1E88E5',
          borderWidth: 1
        }
      ]
    });

    const leaveChart = ref({
      labels: ['Annual', 'Sick', 'Maternity', 'Unpaid'],
      datasets: [
        {
          data: [300, 50, 100, 30],
          backgroundColor: [
            '#42A5F5',
            '#66BB6A',
            '#FFA726',
            '#EF5350'
          ]
        }
      ]
    });

    interface Activity {
      id: number;
      employee: string;
      type: string;
      date: string;
      status: string;
    }

    const recentActivities = ref<Activity[]>([
      { id: 1, employee: 'John Doe', type: 'Leave Request', date: '2023-05-15', status: 'Pending' },
      { id: 2, employee: 'Jane Smith', type: 'New Hire', date: '2023-05-14', status: 'Completed' },
      { id: 3, employee: 'Robert Johnson', type: 'Promotion', date: '2023-05-13', status: 'Approved' },
      { id: 4, employee: 'Emily Davis', type: 'Training', date: '2023-05-12', status: 'In Progress' },
      { id: 5, employee: 'Michael Brown', type: 'Leave Request', date: '2023-05-11', status: 'Rejected' }
    ]);

    const chartOptions = ref({
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            usePointStyle: true,
            padding: 20
          }
        },
        tooltip: {
          mode: 'index',
          intersect: false
        }
      },
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            precision: 0
          }
        }
      },
      animation: {
        duration: 1000,
        easing: 'easeInOutQuart'
      }
    });

    const fetchDashboardData = async () => {
      loading.value = true;
      try {
        // Simulate API calls in parallel
        const [employeesRes, departmentsRes, leaveRes] = await Promise.all([
          fetch('/api/hrm/employees').then(res => res.json()),
          fetch('/api/hrm/departments').then(res => res.json()),
          fetch('/api/hrm/leave-requests').then(res => res.json())
        ]);
        
        // Update stats with real data
        stats.value = {
          totalEmployees: employeesRes?.total || 0,
          onLeave: leaveRes?.onLeave || 0,
          openPositions: employeesRes?.openPositions || 0,
          totalDepartments: departmentsRes?.total || 0,
          loading: false,
          error: null
        };
        
        // Update department chart
        if (departmentsRes?.data) {
          departmentChart.value.labels = departmentsRes.data.map((d: { name: string }) => d.name);
          departmentChart.value.datasets[0].data = departmentsRes.data.map((d: { employeeCount?: number }) => d.employeeCount || 0);
        }
        stats.value = {
          totalEmployees: 156,
          onLeave: 12,
          openPositions: 8,
          totalDepartments: 9,
          loading: false,
          error: null
        };

        departmentChart.value = {
          labels: ['Sales', 'Marketing', 'Development', 'HR', 'Finance', 'Operations'],
          datasets: [
            {
              label: 'Employees',
              backgroundColor: '#42A5F5',
              data: [28, 15, 45, 12, 10, 20]
            }
          ]
        };
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to load dashboard data',
          life: 3000
        });
      } finally {
        loading.value = false;
      }
    };

    const formatDate = (dateString: string) => {
      return new Date(dateString).toLocaleDateString();
    };

    const getStatusSeverity = (status: string) => {
      switch (status.toLowerCase()) {
        case 'approved':
          return 'success';
        case 'pending':
          return 'warning';
        case 'rejected':
          return 'danger';
        case 'completed':
          return 'info';
        default:
          return null;
      }
    };

    onMounted(() => {
      fetchDashboardData().catch(error => {
        console.error('Failed to load dashboard data:', error);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to load dashboard data',
          life: 3000
        });
      }).finally(() => {
        loading.value = false;
      });
    });

    const showSettings = () => {
      toast.add({
        severity: 'info',
        summary: 'Settings',
        detail: 'HRM Settings would open here',
        life: 3000
      });
    };

    const showHelp = () => {
      toast.add({
        severity: 'info',
        summary: 'Help',
        detail: 'HRM Help Center would open here',
        life: 3000
      });
    };

    return {
      stats,
      home,
      items,
      departmentChart,
      leaveChart,
      recentActivities,
      chartOptions,
      formatDate,
      getStatusSeverity,
      loading,
      showSettings,
      showHelp,
      pageTitle
    };
  }
});
</script>

<style scoped>
.hrm-dashboard {
  padding: 1rem;
}

:deep(.p-card) {
  margin-bottom: 1rem;
  height: 100%;
}

:deep(.p-card-title) {
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

:deep(.p-datatable) {
  font-size: 0.9rem;
}

:deep(.p-datatable .p-datatable-thead > tr > th) {
  background-color: #f5f5f5;
  font-weight: 600;
}

:deep(.p-datatable .p-datatable-tbody > tr > td) {
  padding: 0.5rem 1rem;
}
</style>
