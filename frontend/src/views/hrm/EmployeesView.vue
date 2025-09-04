<template>
  <div class="card">
    <div class="flex justify-content-between align-items-center mb-4">
      <h2>Employees</h2>
      <div class="flex gap-2">
        <Button 
          label="Export" 
          icon="pi pi-download" 
          class="p-button-secondary" 
          @click="exportToCSV"
        />
        <Button 
          label="Add Employee" 
          icon="pi pi-plus" 
          class="p-button-primary" 
          @click="openNew" 
        />
      </div>
    </div>

    <div class="card p-fluid">
      <div class="flex justify-content-between align-items-center mb-4">
        <span class="p-input-icon-left w-6">
          <i class="pi pi-search" />
          <InputText 
            :model-value="filterState.global.value || ''"
            @update:model-value="(val: string | null | undefined) => { 
              filterState.global.value = val || null;
            }"
            placeholder="Search..." 
            class="w-full"
          />
        </span>
        <div class="flex gap-2">
          <Dropdown 
            v-model="selectedDepartment" 
            :options="departments" 
            optionLabel="name" 
            optionValue="value"
            placeholder="Department" 
            showClear 
            class="w-10rem"
            @change="(e: {value: string | null}) => { 
              filterState.department.value = e.value; 
            }"
          />
          <Dropdown 
            v-model="selectedStatus" 
            :options="statuses" 
            optionLabel="label" 
            optionValue="value"
            placeholder="Status" 
            showClear 
            class="w-10rem"
            @change="(e: {value: string | null}) => { 
              filterState.status.value = e.value; 
            }"
          />
          <Button 
            label="Clear" 
            icon="pi pi-filter-slash" 
            class="p-button-outlined" 
            @click="clearFilters"
          />
        </div>
      </div>

      <DataTable 
        :value="employees" 
        :paginator="true" 
        :rows="10"
        :filters="tableFilters"
        :loading="loading"
        dataKey="id"
        :globalFilterFields="['name', 'email', 'department', 'status', 'employeeId']"
        scrollable
        scrollHeight="flex"
        class="p-datatable-sm"
        currentPageReportTemplate="Showing {first} to {last} of {totalRecords} entries"
        paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
        :rowsPerPageOptions="[5,10,25,50]"
      >
        <Column field="employeeId" header="ID" :sortable="true" style="width: 10%;">
          <template #body="{ data }">
            {{ data.employeeId || 'N/A' }}
          </template>
        </Column>
        <Column field="name" header="Name" :sortable="true" style="width: 20%;" />
        <Column field="email" header="Email" :sortable="true" style="width: 20%;" />
        <Column field="phone" header="Phone" :sortable="true" style="width: 15%;" />
        <Column field="department" header="Department" :sortable="true" style="width: 15%;">
          <template #body="{ data }">
            <Tag :value="data.department" :severity="getDepartmentSeverity(data.department)" />
          </template>
        </Column>
        <Column field="hireDate" header="Hire Date" :sortable="true" style="width: 15%;">
          <template #body="{ data }">
            {{ formatDateForDisplay(data.hireDate) }}
          </template>
        </Column>
        <Column field="status" header="Status" :sortable="true" style="width: 10%;">
          <template #body="{ data }">
            <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
          </template>
        </Column>
        <Column headerStyle="min-width:10rem;" style="width: 15%;">
          <template #body="{ data }">
            <div class="flex gap-1">
              <Button 
                icon="pi pi-pencil" 
                class="p-button-rounded p-button-text p-button-sm" 
                :pt="{
                  root: { 'data-pr-tooltip': 'Edit' }
                }"
                @click="editEmployee(data)" 
              />
              <Button 
                icon="pi pi-trash" 
                class="p-button-rounded p-button-text p-button-sm p-button-danger" 
                :pt="{
                  root: { 'data-pr-tooltip': 'Delete' }
                }"
                @click="confirmDeleteEmployee(data)" 
              />
            </div>
          </template>
        </Column>
      </DataTable>
    </div>

    <!-- Delete Confirmation Dialog -->
    <Dialog 
      v-model:visible="deleteEmployeeDialog" 
      :style="{ width: '450px' }" 
      header="Confirm" 
      :modal="true"
    >
      <div class="confirmation-content">
        <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
        <span v-if="employee">Are you sure you want to delete <b>{{ employee.name }}</b>?</span>
      </div>
      <template #footer>
        <Button 
          label="No" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="deleteEmployeeDialog = false" 
        />
        <Button 
          label="Yes" 
          icon="pi pi-check" 
          class="p-button-danger" 
          @click="deleteEmployee" 
        />
      </template>
    </Dialog>

    <!-- Employee Form Dialog -->
    <Dialog 
      v-model:visible="employeeDialog" 
      :style="{ width: '600px' }" 
      :header="employee.id ? 'Edit Employee' : 'New Employee'" 
      :modal="true" 
      class="p-fluid"
      :closable="false"
    >
      <div class="grid formgrid p-fluid">
        <div class="field col-12">
          <label for="name" class="font-medium text-900">Full Name</label>
          <InputText 
            id="name" 
            :model-value="employee.name || ''"
            @update:model-value="(val: string | undefined) => { if (val !== undefined) employee.name = val }"
            required
            autofocus
            :class="{ 'p-invalid': submitted && !employee.name }"
            class="w-full"
          />
          <small class="p-error" v-if="submitted && !employee.name">Name is required.</small>
        </div>
        
        <div class="field col-12 md:col-6">
          <label for="email" class="font-medium text-900">Email</label>
          <InputText 
            id="email"
            :model-value="employee.email || ''"
            @update:model-value="(val: string | undefined) => { if (val !== undefined) employee.email = val }"
            required
            type="email"
            :class="{ 'p-invalid': submitted && !employee.email }"
            class="w-full"
          />
          <small class="p-error" v-if="submitted && !employee.email">Email is required.</small>
        </div>
        
        <div class="field col-12 md:col-6">
          <label for="phone" class="font-medium text-900">Phone</label>
          <InputText 
            id="phone"
            :model-value="employee.phone ?? ''"
            @update:model-value="(val: string | null) => { employee.phone = val }"
            required
            type="tel"
            :class="{ 'p-invalid': submitted && !employee.phone }"
            class="w-full"
          />
          <small class="p-error" v-if="submitted && !employee.phone">Phone is required.</small>
        </div>
        
        <div class="field col-12 md:col-6">
          <label for="hireDate" class="font-medium text-900">Hire Date</label>
          <Calendar 
            id="hireDate"
            :model-value="employee.hireDate ? new Date(employee.hireDate) : null"
            @update:model-value="handleDateUpdate"
            date-format="yy-mm-dd"
            show-icon
            class="w-full"
            :class="{ 'p-invalid': submitted && !employee.hireDate }"
          />
          <small class="p-error" v-if="submitted && !employee.hireDate">Hire Date is required.</small>
        </div>
      </div>
      
      <template #footer>
        <div class="flex justify-content-end gap-2">
          <Button 
            label="Cancel" 
            icon="pi pi-times" 
            class="p-button-text" 
            @click="hideDialog" 
          />
          <Button 
            :label="employee.id ? 'Update' : 'Save'" 
            icon="pi pi-check" 
            class="p-button-primary" 
            @click="saveEmployee" 
          />
        </div>
      </template>
        </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, defineExpose, computed } from 'vue';
import { FilterMatchMode } from 'primevue/api';
import { useToast } from 'primevue/usetoast';
import { formatDateForDisplay } from '@/utils/dateUtils';
import employeeService, { type Employee } from '@/services/employeeService';

// Type for filter values and state
interface FilterValue {
  value: string | null;
  matchMode: string;
}

interface FilterState {
  global: FilterValue;
  department: FilterValue;
  status: FilterValue;
  employeeId: FilterValue;
}

// Components
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import Dialog from 'primevue/dialog';
import Calendar from 'primevue/calendar';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Dropdown from 'primevue/dropdown';
import Tag from 'primevue/tag';

// Constants
const departments = [
  { name: 'IT', value: 'it' },
  { name: 'Finance', value: 'finance' },
  { name: 'HR', value: 'hr' },
  { name: 'Operations', value: 'operations' },
  { name: 'Sales', value: 'sales' },
  { name: 'Marketing', value: 'marketing' }
];

const statuses = [
  { label: 'Active', value: 'active' },
  { label: 'Inactive', value: 'inactive' },
  { label: 'On Leave', value: 'on_leave' },
  { label: 'Terminated', value: 'terminated' }
];

// Initialize toast
const toast = useToast();

// Refs
const loading = ref(false);
const submitted = ref(false);
const employeeDialog = ref(false);
const deleteEmployeeDialog = ref(false);
const employees = ref<Employee[]>([]);
const selectedDepartment = ref<string | null>(null);
const selectedStatus = ref<string | null>(null);

// Update Employee type to make hireDate optional with explicit undefined
interface EmployeeWithOptionalHireDate extends Omit<Employee, 'hireDate'> {
  hireDate?: string | null;
}

// Initialize employee with empty values
const getEmptyEmployee = (): EmployeeWithOptionalHireDate => ({
  employeeId: '',
  name: '',
  email: '',
  phone: '',
  department: '',
  departmentId: 0,
  position: '',
  hireDate: new Date().toISOString().split('T')[0] as string,
  status: 'active',
  address: '',
  city: '',
  state: '',
  zipCode: ''
});

const employee = ref<EmployeeWithOptionalHireDate>(getEmptyEmployee());

// Type for DataTable filters (compatible with PrimeVue)
type DataTableFilters = {
  [key: string]: {
    value: any;
    matchMode: string;
  };
};

// Initialize filters with proper typing
const filterState = ref<FilterState>({
  global: { value: null, matchMode: FilterMatchMode.CONTAINS },
  department: { value: null, matchMode: FilterMatchMode.EQUALS },
  status: { value: null, matchMode: FilterMatchMode.EQUALS },
  employeeId: { value: null, matchMode: FilterMatchMode.EQUALS }
});

// For DataTable compatibility
const tableFilters = computed((): DataTableFilters => ({
  global: filterState.value.global,
  department: filterState.value.department,
  status: filterState.value.status,
  employeeId: filterState.value.employeeId
}));

// Clear filters function
const clearFilters = () => {
  filterState.value = {
    global: { value: null, matchMode: FilterMatchMode.CONTAINS },
    department: { value: null, matchMode: FilterMatchMode.EQUALS },
    status: { value: null, matchMode: FilterMatchMode.EQUALS },
    employeeId: { value: null, matchMode: FilterMatchMode.EQUALS }
  };
  selectedDepartment.value = null;
  selectedStatus.value = null;
  selectedStatus.value = null;
};

// Reset employee form - Marked as used to prevent warning
const resetEmployee = () => {
  employee.value = getEmptyEmployee();
  submitted.value = false;
};

// Status severity function
const getStatusSeverity = (status: string | undefined): string => {
  if (!status) return 'info';
  switch (status.toLowerCase()) {
    case 'active':
      return 'success';
    case 'inactive':
      return 'danger';
    case 'on_leave':
      return 'warning';
    default:
      return 'info';
  }
};

// Handle date update from calendar
const handleDateUpdate = (date: Date | Date[] | (Date | null)[] | null | undefined) => {
  if (!employee.value) return;
  
  const setHireDate = (d: Date | null | undefined) => {
    if (d && d instanceof Date && !isNaN(d.getTime())) {
      employee.value.hireDate = d.toISOString().split('T')[0] as string | null;
    } else {
      employee.value.hireDate = null;
    }
  };
  
  if (Array.isArray(date)) {
    setHireDate(date[0] || null);
  } else {
    setHireDate(date || null);
  }
};

// Mark as used to prevent warnings
if (import.meta.hot) {
  // @ts-ignore - These are used in the template
  departments;
  // @ts-ignore
  statuses;
  onMounted;
  resetEmployee;
}

// Get department severity for tag styling
const getDepartmentSeverity = (department: string | null | undefined): string => {
  if (!department) return 'info';
  const dept = department.toLowerCase();
  if (dept === 'hr') return 'success';
  if (dept === 'finance') return 'info';
  if (dept === 'it') return 'warning';
  if (dept === 'operations') return 'danger';
  if (dept === 'sales') return 'primary';
  if (dept === 'marketing') return 'help';
  return 'info';
};

// Remove duplicate method declarations
const openNew = () => {
  employee.value = getEmptyEmployee();
  submitted.value = false;
  employeeDialog.value = true;
};

const hideDialog = () => {
  employeeDialog.value = false;
  deleteEmployeeDialog.value = false;
  submitted.value = false;
  employee.value = getEmptyEmployee();
};

const editEmployee = (emp: Employee) => {
  employee.value = { ...emp };
  employeeDialog.value = true;
};

const confirmDeleteEmployee = (emp: Employee) => {
  employee.value = emp;
  deleteEmployeeDialog.value = true;
};

const saveEmployee = async () => {
  submitted.value = true;
  if (!employee.value.name || !employee.value.email) return;
  
  loading.value = true;
  
  try {
    if (employee.value.id) {
      await employeeService.updateEmployee(employee.value.id, employee.value as Employee);
      toast.add({ severity: 'success', summary: 'Success', detail: 'Employee updated successfully', life: 3000 });
    } else {
      const newEmployee = await employeeService.createEmployee({
        ...employee.value,
        employeeId: employee.value.employeeId || `EMP-${Date.now()}`,
        status: employee.value.status || 'active',
        hireDate: employee.value.hireDate || new Date().toISOString().split('T')[0]
      } as Employee);
      employees.value = [...employees.value, newEmployee];
      toast.add({ severity: 'success', summary: 'Success', detail: 'Employee created successfully', life: 3000 });
    }
    employeeDialog.value = false;
    employee.value = getEmptyEmployee();
  } catch (error) {
    console.error('Error saving employee:', error);
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to save employee', life: 3000 });
  } finally {
    loading.value = false;
    submitted.value = false;
  }
};

const deleteEmployee = async () => {
  if (!employee.value.id) return;
  
  try {
    await employeeService.deleteEmployee(employee.value.id);
    const index = employees.value.findIndex(e => e.id === employee.value.id);
    if (index !== -1) {
      employees.value.splice(index, 1);
    }
    deleteEmployeeDialog.value = false;
    toast.add({ severity: 'success', summary: 'Successful', detail: 'Employee Deleted', life: 3000 });
  } catch (error) {
    console.error('Error deleting employee:', error);
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to delete employee', life: 3000 });
  }
  employee.value = getEmptyEmployee();
};

const exportToCSV = () => {
  import('xlsx').then(({ utils, writeFile }) => {
    const data = employees.value.map(emp => ({
      'Employee ID': emp.employeeId,
      'Name': emp.name,
      'Email': emp.email,
      'Phone': emp.phone || '',
      'Department': emp.department || '',
      'Status': emp.status || '',
      'Hire Date': emp.hireDate ? new Date(emp.hireDate).toLocaleDateString() : ''
    }));
    
    const worksheet = utils.json_to_sheet(data);
    const workbook = utils.book_new();
    utils.book_append_sheet(workbook, worksheet, 'Employees');
    writeFile(workbook, 'employees_export.xlsx');
  });
};

// Expose methods to template
defineExpose({
  getStatusSeverity,
  formatDateForDisplay,
  openNew,
  hideDialog,
  editEmployee,
  confirmDeleteEmployee,
  deleteEmployee,
  saveEmployee,
  exportToCSV,
  clearFilters,
  handleDateUpdate
});

// Lifecycle hooks
const loadEmployees = async () => {
  try {
    loading.value = true;
    const response = await employeeService.getEmployees();
    employees.value = response || [];
  } catch (error) {
    console.error('Error loading employees:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load employees',
      life: 3000
    });
  } finally {
    loading.value = false;
  }
});

// Load employees on component mount
onMounted(() => {
  loadEmployees();
});
</script>

<style scoped>
.employees-view {
  padding: 1rem;
}

/* Status badges */
.status-badge {
  padding: 0.5rem 0.75rem;
  border-radius: 4px;
  font-weight: 600;
  text-transform: capitalize;
}

.status-active {
  background-color: #e6f7e6;
  color: #1e8e3e;
}

.status-inactive {
  background-color: #fff8e6;
  color: #ffc107;
}

.status-on_leave {
  background-color: #e6f4ff;
  color: #1a73e8;
}

.status-terminated {
  background-color: #fce8e6;
  color: #d93025;
}

:deep(.p-card) {
  margin-bottom: 1rem;
}

:deep(.p-card .p-card-title) {
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
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

:deep(.p-dialog .p-dialog-header) {
  padding: 1.5rem 1.5rem 0.5rem;
}

:deep(.p-dialog .p-dialog-content) {
  padding: 1.5rem;
}

:deep(.p-dialog .p-dialog-footer) {
  padding: 0.5rem 1.5rem 1.5rem;
}

.field {
  margin-bottom: 1.5rem;
}
</style>
