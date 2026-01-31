<template>
  <v-container fluid class="pa-6">
    <!-- Page Header -->
    <v-row class="mb-6" align="center">
      <v-col cols="12" sm="6" md="8">
        <h1 class="text-h4 font-weight-bold">Employee Payroll</h1>
        <p class="text-subtitle-1 text-medium-emphasis">
          View and manage employee payroll information
        </p>
      </v-col>
      <v-col cols="12" sm="6" md="4" class="text-right">
        <v-btn
          color="primary"
          prepend-icon="mdi-plus"
          @click="addEmployee"
          :loading="isLoading"
          class="mr-2"
        >
          Add Employee
        </v-btn>
        <v-btn
          variant="outlined"
          prepend-icon="mdi-refresh"
          @click="fetchEmployeePayroll"
          :loading="isRefreshing"
        >
          Refresh
        </v-btn>
      </v-col>
    </v-row>

    <!-- Filters -->
    <v-card class="mb-6">
      <v-card-text>
        <v-row dense>
          <v-col cols="12" sm="6" md="3">
            <v-text-field
              v-model="search"
              label="Search employees"
              prepend-inner-icon="mdi-magnify"
              variant="outlined"
              density="compact"
              clearable
              hide-details
              @update:model-value="applyFilters"
            ></v-text-field>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <v-select
              v-model="departmentFilter"
              :items="departments"
              item-title="name"
              item-value="id"
              label="Department"
              variant="outlined"
              density="compact"
              clearable
              hide-details
              @update:model-value="applyFilters"
            ></v-select>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <v-select
              v-model="statusFilter"
              :items="employmentStatuses"
              label="Employment Status"
              variant="outlined"
              density="compact"
              clearable
              hide-details
              @update:model-value="applyFilters"
            ></v-select>
          </v-col>
          <v-col cols="12" sm="6" md="3" class="d-flex align-center">
            <v-btn
              variant="text"
              prepend-icon="mdi-filter-remove"
              @click="resetFilters"
              class="ml-auto"
            >
              Clear Filters
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- Employee Payroll Table -->
    <v-card>
      <v-card-title class="d-flex align-center">
        <span>Employee Payroll</span>
        <v-spacer></v-spacer>
        <v-btn
          variant="text"
          icon="mdi-printer"
          @click="printTable"
          title="Print"
          class="mr-2"
        ></v-btn>
        <v-btn
          variant="text"
          icon="mdi-microsoft-excel"
          @click="exportToExcel"
          title="Export to Excel"
          class="mr-2"
        ></v-btn>
        <v-btn
          variant="text"
          icon="mdi-file-pdf-box"
          @click="exportToPdf"
          title="Export to PDF"
        ></v-btn>
      </v-card-title>

      <v-card-text>
        <v-data-table
          :headers="headers"
          :items="filteredEmployees"
          :loading="isLoading"
          :search="search"
          :items-per-page="10"
          class="elevation-1"
          density="comfortable"
        >
          <template v-slot:item.employee.name="{ item }">
            <div class="d-flex align-center">
              <v-avatar size="36" class="mr-3">
                <v-img :src="item.employee.avatar || '/default-avatar.png'" alt="Avatar"></v-img>
              </v-avatar>
              <div>
                <div class="font-weight-medium">{{ item.employee.name }}</div>
                <div class="text-caption text-medium-emphasis">{{ item.employee.employeeId }}</div>
              </div>
            </div>
          </template>

          <template v-slot:item.salary="{ item }">
            {{ formatCurrency(item.salary) }}
          </template>

          <template v-slot:item.lastPayDate="{ item }">
            {{ formatDate(item.lastPayDate) }}
          </template>

          <template v-slot:item.status="{ item }">
            <v-chip
              :color="getStatusColor(item.status)"
              size="small"
              label
              :text="item.status"
              class="text-capitalize"
            ></v-chip>
          </template>

          <template v-slot:item.actions="{ item }">
            <v-btn
              icon="mdi-eye"
              variant="text"
              color="primary"
              size="small"
              @click="viewEmployeePayroll(item)"
              title="View Details"
              class="mr-1"
            ></v-btn>
            <v-btn
              icon="mdi-pencil"
              variant="text"
              color="secondary"
              size="small"
              @click="editEmployeePayroll(item)"
              title="Edit"
              class="mr-1"
            ></v-btn>
            <v-btn
              icon="mdi-delete"
              variant="text"
              color="error"
              size="small"
              @click="confirmDelete(item)"
              title="Delete"
            ></v-btn>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>

    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="deleteDialog" max-width="500">
      <v-card>
        <v-card-title class="text-h6">Confirm Delete</v-card-title>
        <v-card-text>
          Are you sure you want to delete the payroll record for 
          <strong>{{ selectedEmployee?.employee?.name || 'this employee' }}</strong>?
          This action cannot be undone.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            variant="text"
            @click="deleteDialog = false"
          >
            Cancel
          </v-btn>
          <v-btn
            color="error"
            variant="tonal"
            @click="deleteEmployeePayroll"
            :loading="isDeleting"
          >
            Delete
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useSnackbar } from '@/composables/useSnackbar';

// Router
const router = useRouter();
const { showSuccess, showError } = useSnackbar();

// State
const isLoading = ref(false);
const isRefreshing = ref(false);
const isDeleting = ref(false);
const deleteDialog = ref(false);
const selectedEmployee = ref(null);
const search = ref('');
const departmentFilter = ref('');
const statusFilter = ref('');

// Sample data - replace with API calls
const departments = ref([
  { id: 'dept-001', name: 'Finance' },
  { id: 'dept-002', name: 'Human Resources' },
  { id: 'dept-003', name: 'IT' },
  { id: 'dept-004', name: 'Operations' },
  { id: 'dept-005', name: 'Sales' },
]);

const employmentStatuses = [
  'Active',
  'On Leave',
  'Probation',
  'Terminated',
  'Retired'
];

const employees = ref([
  {
    id: 'emp-001',
    employee: {
      id: 'emp-001',
      employeeId: 'EMP-001',
      name: 'John Doe',
      email: 'john.doe@example.com',
      department: 'Finance',
      position: 'Senior Accountant',
      joinDate: '2020-05-15',
      avatar: 'https://randomuser.me/api/portraits/men/1.jpg'
    },
    salary: 75000,
    payFrequency: 'Monthly',
    paymentMethod: 'Bank Transfer',
    bankAccount: '****4532',
    taxId: 'TAX-001',
    status: 'Active',
    lastPayDate: '2023-11-30',
    nextPayDate: '2023-12-31',
    ytdEarnings: 82500,
    ytdTax: 16500,
    ytdDeductions: 4500,
    ytdNetPay: 61500
  },
  // Add more sample employees as needed
]);

// Computed
const filteredEmployees = computed(() => {
  return employees.value.filter(emp => {
    const matchesSearch = !search.value || 
      emp.employee.name.toLowerCase().includes(search.value.toLowerCase()) ||
      emp.employee.employeeId.toLowerCase().includes(search.value.toLowerCase());
    
    const matchesDept = !departmentFilter.value || 
      emp.employee.department === departmentFilter.value;
    
    const matchesStatus = !statusFilter.value || 
      emp.status.toLowerCase() === statusFilter.value.toLowerCase();
    
    return matchesSearch && matchesDept && matchesStatus;
  });
});

// Table Headers
const headers = [
  { 
    title: 'Employee', 
    key: 'employee.name',
    sortable: true,
    width: '25%'
  },
  { 
    title: 'Department', 
    key: 'employee.department',
    sortable: true,
    width: '15%'
  },
  { 
    title: 'Position', 
    key: 'employee.position',
    sortable: true,
    width: '15%'
  },
  { 
    title: 'Salary', 
    key: 'salary',
    sortable: true,
    align: 'end',
    width: '10%'
  },
  { 
    title: 'Last Pay Date', 
    key: 'lastPayDate',
    sortable: true,
    width: '12%'
  },
  { 
    title: 'Status', 
    key: 'status',
    sortable: true,
    width: '10%'
  },
  { 
    title: 'Actions', 
    key: 'actions',
    sortable: false,
    align: 'end',
    width: '13%'
  },
];

// Methods
const fetchEmployeePayroll = async () => {
  try {
    isLoading.value = true;
    // TODO: Replace with actual API call
    // const response = await payrollService.getEmployeePayrollList();
    // employees.value = response.data;
    await new Promise(resolve => setTimeout(resolve, 800)); // Simulate API delay
  } catch (error) {
    console.error('Error fetching employee payroll:', error);
    showError('Failed to load employee payroll data');
  } finally {
    isLoading.value = false;
    isRefreshing.value = false;
  }
};

const addEmployee = () => {
  router.push({ name: 'payroll-employee-add' });
};

const viewEmployeePayroll = (employee) => {
  router.push({ 
    name: 'payroll-employee-details', 
    params: { id: employee.id } 
  });
};

const editEmployeePayroll = (employee) => {
  router.push({ 
    name: 'payroll-employee-edit', 
    params: { id: employee.id } 
  });
};

const confirmDelete = (employee) => {
  selectedEmployee.value = employee;
  deleteDialog.value = true;
};

const deleteEmployeePayroll = async () => {
  if (!selectedEmployee.value) return;
  
  try {
    isDeleting.value = true;
    // TODO: Replace with actual API call
    // await payrollService.deleteEmployeePayroll(selectedEmployee.value.id);
    await new Promise(resolve => setTimeout(resolve, 500)); // Simulate API delay
    
    // Remove from local state
    const index = employees.value.findIndex(e => e.id === selectedEmployee.value.id);
    if (index !== -1) {
      employees.value.splice(index, 1);
    }
    
    showSuccess('Employee payroll record deleted successfully');
    deleteDialog.value = false;
  } catch (error) {
    console.error('Error deleting employee payroll:', error);
    showError('Failed to delete employee payroll record');
  } finally {
    isDeleting.value = false;
  }
};

const applyFilters = () => {
  // The computed property filteredEmployees will automatically update
  console.log('Filters applied');
};

const resetFilters = () => {
  search.value = '';
  departmentFilter.value = '';
  statusFilter.value = '';
};

const getStatusColor = (status) => {
  const statusMap = {
    'active': 'success',
    'on leave': 'warning',
    'probation': 'info',
    'terminated': 'error',
    'retired': 'grey',
  };
  return statusMap[status.toLowerCase()] || 'default';
};

const exportToExcel = () => {
  // TODO: Implement Excel export
  console.log('Export to Excel');
  showSuccess('Export to Excel will be implemented');
};

const exportToPdf = () => {
  // TODO: Implement PDF export
  console.log('Export to PDF');
  showSuccess('Export to PDF will be implemented');
};

const printTable = () => {
  // TODO: Implement print functionality
  console.log('Print table');
  window.print();
};

// Lifecycle hooks
onMounted(() => {
  fetchEmployeePayroll();
});
</script>

<style scoped>
.v-table {
  --v-table-header-color: rgba(var(--v-theme-on-surface), var(--v-high-emphasis-opacity));
  --v-table-header-font-weight: 600;
}

.v-data-table-footer {
  border-top: thin solid rgba(var(--v-border-color), var(--v-border-opacity));
}

/* Print styles */
@media print {
  .v-toolbar,
  .v-breadcrumbs,
  .v-navigation-drawer,
  .v-footer,
  .no-print {
    display: none !important;
  }
  
  .v-main {
    padding: 0 !important;
  }
  
  .v-container {
    max-width: 100% !important;
    padding: 0 !important;
  }
  
  .v-card {
    box-shadow: none !important;
    border: 1px solid #e0e0e0 !important;
  }
  
  .v-table {
    width: 100% !important;
  }
}
</style>
