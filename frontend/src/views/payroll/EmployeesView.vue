<template>
  <div class="p-4">
    <Card>
      <template #title>Employee Management</template>
      <template #content>
        <Message severity="info" :closable="false" class="mb-4">
          <p>Manage employee information, compensation, and payroll settings.</p>
        </Message>
        
        <div class="flex justify-content-between mb-4">
          <div class="flex gap-2">
            <Button 
              label="Add Employee" 
              icon="pi pi-user-plus" 
              class="p-button-primary"
              @click="addEmployee"
            />
            <Button 
              label="Import" 
              icon="pi pi-upload" 
              class="p-button-secondary"
              @click="importEmployees"
            />
            <Button 
              label="Export" 
              icon="pi pi-download" 
              class="p-button-help"
              @click="exportEmployees"
            />
          </div>
          
          <span class="p-input-icon-left">
            <i class="pi pi-search" />
            <InputText 
              v-model="filters['global'].value" 
              placeholder="Search employees..." 
              class="w-20rem"
            />
          </span>
        </div>
        
        <DataTable 
          :value="employees" 
          :paginator="true" 
          :rows="10"
          :loading="loading"
          :filters="filters"
          :globalFilterFields="['name', 'employeeId', 'department', 'position', 'status']"
          selectionMode="single"
          dataKey="id"
          responsiveLayout="scroll"
          class="p-datatable-sm"
          v-model:selection="selectedEmployee"
          @rowSelect="onRowSelect"
        >
          <Column field="employeeId" header="ID" :sortable="true" style="width: 100px" />
          
          <Column field="name" header="Name" :sortable="true">
            <template #body="{ data }">
              <div class="flex align-items-center">
                <Avatar 
                  :image="data.avatar" 
                  :label="getInitials(data.name)" 
                  class="mr-2" 
                  shape="circle"
                  size="large"
                />
                <div>
                  <div class="font-medium">{{ data.name }}</div>
                  <div class="text-500 text-sm">{{ data.email }}</div>
                </div>
              </div>
            </template>
          </Column>
          
          <Column field="department" header="Department" :sortable="true">
            <template #body="{ data }">
              <Tag :value="data.department" :severity="getDepartmentSeverity(data.department)" />
            </template>
          </Column>
          
          <Column field="position" header="Position" :sortable="true" />
          
          <Column field="hireDate" header="Hire Date" :sortable="true">
            <template #body="{ data }">
              {{ formatDate(data.hireDate) }}
            </template>
          </Column>
          
          <Column field="salary" header="Salary" :sortable="true">
            <template #body="{ data }">
              {{ formatCurrency(data.salary) }}
            </template>
          </Column>
          
          <Column field="status" header="Status" :sortable="true">
            <template #body="{ data }">
              <Tag 
                :value="data.status" 
                :severity="getStatusSeverity(data.status)" 
                :icon="getStatusIcon(data.status)" 
              />
            </template>
          </Column>
          
          <Column headerStyle="width: 8rem; text-align: center" bodyStyle="text-align: center; overflow: visible">
            <template #body="{ data }">
              <div class="flex gap-2 justify-content-center">
                <Button 
                  icon="pi pi-pencil" 
                  class="p-button-rounded p-button-text p-button-primary"
                  v-tooltip.top="'Edit Employee'"
                  @click="editEmployee(data)"
                />
                <Button 
                  icon="pi pi-trash" 
                  class="p-button-rounded p-button-text p-button-danger"
                  v-tooltip.top="'Delete Employee'"
                  @click="confirmDeleteEmployee(data)"
                />
              </div>
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>
    
    <!-- Employee Dialog -->
    <Dialog 
      v-model:visible="showEmployeeDialog" 
      :header="editingEmployee ? 'Edit Employee' : 'Add New Employee'"
      :modal="true"
      :style="{ width: '50vw' }"
      :maximizable="true"
    >
      <div v-if="editingEmployee" class="grid p-fluid">
        <div class="col-12 md:col-4">
          <div class="flex flex-column align-items-center">
            <Avatar 
              :image="editingEmployee.avatar" 
              :label="getInitials(editingEmployee.name)" 
              size="xlarge" 
              shape="circle" 
              class="mb-3"
            />
            <Button 
              label="Change Photo" 
              icon="pi pi-camera" 
              class="p-button-text"
            />
          </div>
        </div>
        
        <div class="col-12 md:col-8">
          <div class="grid formgrid p-fluid">
            <div class="field col-12 md:col-6">
              <label for="name">Full Name</label>
              <InputText id="name" v-model="editingEmployee.name" />
            </div>
            
            <div class="field col-12 md:col-6">
              <label for="employeeId">Employee ID</label>
              <InputText id="employeeId" v-model="editingEmployee.employeeId" :disabled="!!editingEmployee.id" />
            </div>
            
            <div class="field col-12 md:col-6">
              <label for="email">Email</label>
              <InputText id="email" v-model="editingEmployee.email" />
            </div>
            
            <div class="field col-12 md:col-6">
              <label for="phone">Phone</label>
              <InputText id="phone" v-model="editingEmployee.phone" />
            </div>
            
            <div class="field col-12 md:col-6">
              <label for="department">Department</label>
              <Dropdown 
                id="department" 
                v-model="editingEmployee.department" 
                :options="departments" 
                optionLabel="name" 
                optionValue="value"
                placeholder="Select Department"
              />
            </div>
            
            <div class="field col-12 md:col-6">
              <label for="position">Position</label>
              <InputText id="position" v-model="editingEmployee.position" />
            </div>
            
            <div class="field col-12 md:col-6">
              <label for="hireDate">Hire Date</label>
              <Calendar id="hireDate" v-model="editingEmployee.hireDate" dateFormat="yy-mm-dd" showIcon />
            </div>
            
            <div class="field col-12 md:col-6">
              <label for="salary">Salary</label>
              <InputNumber 
                id="salary" 
                v-model="editingEmployee.salary" 
                mode="currency" 
                currency="USD" 
                locale="en-US"
                class="w-full"
              />
            </div>
            
            <div class="field col-12">
              <label for="status">Status</label>
              <div class="flex flex-wrap gap-3 mt-2">
                <div class="flex align-items-center">
                  <RadioButton 
                    id="status1" 
                    name="status" 
                    value="Active" 
                    v-model="editingEmployee.status"
                  />
                  <label for="status1" class="ml-2">Active</label>
                </div>
                <div class="flex align-items-center">
                  <RadioButton 
                    id="status2" 
                    name="status" 
                    value="On Leave" 
                    v-model="editingEmployee.status"
                  />
                  <label for="status2" class="ml-2">On Leave</label>
                </div>
                <div class="flex align-items-center">
                  <RadioButton 
                    id="status3" 
                    name="status" 
                    value="Terminated" 
                    v-model="editingEmployee.status"
                  />
                  <label for="status3" class="ml-2">Terminated</label>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <template #footer>
        <Button 
          label="Cancel" 
          icon="pi pi-times" 
          @click="showEmployeeDialog = false" 
          class="p-button-text"
        />
        <Button 
          :label="editingEmployee?.id ? 'Update' : 'Save'" 
          icon="pi pi-check" 
          @click="saveEmployee" 
          class="p-button-primary"
        />
      </template>
    </Dialog>
    
    <!-- Delete Confirmation Dialog -->
    <Dialog 
      v-model:visible="showDeleteDialog" 
      header="Confirm Delete" 
      :modal="true" 
      :style="{ width: '450px' }"
    >
      <div class="confirmation-content">
        <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
        <span v-if="editingEmployee">
          Are you sure you want to delete <b>{{ editingEmployee.name }}</b>?
        </span>
      </div>
      
      <template #footer>
        <Button 
          label="No" 
          icon="pi pi-times" 
          @click="showDeleteDialog = false" 
          class="p-button-text"
        />
        <Button 
          label="Yes" 
          icon="pi pi-check" 
          @click="deleteEmployee" 
          class="p-button-danger"
          autofocus
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import { FilterMatchMode } from 'primevue/api';

// Components

type EmployeeStatus = 'Active' | 'On Leave' | 'Terminated';

interface Employee {
  id?: string;
  employeeId: string;
  name: string;
  email: string;
  phone: string;
  department: string;
  position: string;
  hireDate: string;
  salary: number;
  status: EmployeeStatus;
  avatar?: string;
}

const toast = useToast();
const loading = ref(false);
const showEmployeeDialog = ref(false);
const showDeleteDialog = ref(false);
const editingEmployee = ref<Employee | null>(null);
const selectedEmployee = ref<Employee | null>(null);

// Available departments
const departments = ref([
  { name: 'Administration', value: 'Administration' },
  { name: 'Finance', value: 'Finance' },
  { name: 'Human Resources', value: 'Human Resources' },
  { name: 'Information Technology', value: 'IT' },
  { name: 'Marketing', value: 'Marketing' },
  { name: 'Operations', value: 'Operations' },
  { name: 'Sales', value: 'Sales' },
]);

// Mock data
const employees = ref<Employee[]>([
  {
    id: '1',
    employeeId: 'EMP-001',
    name: 'John Doe',
    email: 'john.doe@example.com',
    phone: '(555) 123-4567',
    department: 'IT',
    position: 'Senior Developer',
    hireDate: '2020-06-15',
    salary: 85000,
    status: 'Active',
    avatar: 'https://randomuser.me/api/portraits/men/1.jpg',
  },
  {
    id: '2',
    employeeId: 'EMP-002',
    name: 'Jane Smith',
    email: 'jane.smith@example.com',
    phone: '(555) 987-6543',
    department: 'Finance',
    position: 'Financial Analyst',
    hireDate: '2019-03-22',
    salary: 75000,
    status: 'Active',
    avatar: 'https://randomuser.me/api/portraits/women/1.jpg',
  },
  {
    id: '3',
    employeeId: 'EMP-003',
    name: 'Robert Johnson',
    email: 'robert.j@example.com',
    phone: '(555) 456-7890',
    department: 'Marketing',
    position: 'Marketing Manager',
    hireDate: '2021-01-10',
    salary: 90000,
    status: 'On Leave',
    avatar: 'https://randomuser.me/api/portraits/men/2.jpg',
  },
  {
    id: '4',
    employeeId: 'EMP-004',
    name: 'Emily Davis',
    email: 'emily.d@example.com',
    phone: '(555) 234-5678',
    department: 'Human Resources',
    position: 'HR Specialist',
    hireDate: '2018-11-05',
    salary: 68000,
    status: 'Active',
    avatar: 'https://randomuser.me/api/portraits/women/2.jpg',
  },
  {
    id: '5',
    employeeId: 'EMP-005',
    name: 'Michael Wilson',
    email: 'michael.w@example.com',
    phone: '(555) 345-6789',
    department: 'Operations',
    position: 'Operations Manager',
    hireDate: '2017-08-14',
    salary: 95000,
    status: 'Terminated',
    avatar: 'https://randomuser.me/api/portraits/men/3.jpg',
  },
]);

// Filters for the data table
const filters = ref({
  'global': { value: null, matchMode: FilterMatchMode.CONTAINS },
});

// Format date to YYYY-MM-DD
const formatDate = (dateString: string) => {
  if (!dateString) return '-';
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

// Format currency
const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
};

// Get initials from name
const getInitials = (name: string) => {
  if (!name) return '';
  return name
    .split(' ')
    .map(part => part[0])
    .join('')
    .toUpperCase();
};

// Get severity for department tag
const getDepartmentSeverity = (department: string) => {
  switch (department) {
    case 'IT': return 'info';
    case 'Finance': return 'success';
    case 'Marketing': return 'warning';
    case 'Human Resources': return 'help';
    case 'Operations': return 'danger';
    case 'Sales': return 'success';
    default: return null;
  }
};

// Get severity for status tag
const getStatusSeverity = (status: EmployeeStatus) => {
  switch (status) {
    case 'Active': return 'success';
    case 'On Leave': return 'warning';
    case 'Terminated': return 'danger';
    default: return null;
  }
};

// Get icon for status tag
const getStatusIcon = (status: EmployeeStatus) => {
  switch (status) {
    case 'Active': return 'pi pi-check-circle';
    case 'On Leave': return 'pi pi-clock';
    case 'Terminated': return 'pi pi-times-circle';
    default: return 'pi pi-question-circle';
  }
};

// Add new employee
const addEmployee = () => {
  editingEmployee.value = {
    employeeId: `EMP-${String(employees.value.length + 1).padStart(3, '0')}`,
    name: '',
    email: '',
    phone: '',
    department: '',
    position: '',
    hireDate: new Date().toISOString().split('T')[0],
    salary: 0,
    status: 'Active',
  };
  showEmployeeDialog.value = true;
};

// Edit employee
const editEmployee = (employee: Employee) => {
  editingEmployee.value = { ...employee };
  showEmployeeDialog.value = true;
};

// Save employee
const saveEmployee = () => {
  if (!editingEmployee.value) return;
  
  if (editingEmployee.value.id) {
    // Update existing employee
    const index = employees.value.findIndex(e => e.id === editingEmployee.value?.id);
    if (index !== -1) {
      employees.value[index] = { ...editingEmployee.value };
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Employee updated successfully',
        life: 3000,
      });
    }
  } else {
    // Add new employee
    const newEmployee = {
      ...editingEmployee.value,
      id: String(employees.value.length + 1),
    };
    employees.value.unshift(newEmployee);
    
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Employee added successfully',
      life: 3000,
    });
  }
  
  showEmployeeDialog.value = false;
};

// Confirm delete employee
const confirmDeleteEmployee = (employee: Employee) => {
  editingEmployee.value = { ...employee };
  showDeleteDialog.value = true;
};

// Delete employee
const deleteEmployee = () => {
  if (!editingEmployee.value?.id) return;
  
  const index = employees.value.findIndex(e => e.id === editingEmployee.value?.id);
  if (index !== -1) {
    employees.value.splice(index, 1);
    
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Employee deleted successfully',
      life: 3000,
    });
  }
  
  showDeleteDialog.value = false;
  editingEmployee.value = null;
};

// Row select handler
const onRowSelect = (event: any) => {
  // In a real app, you might want to show a detail view or navigate to employee details
  console.log('Employee selected:', event.data);
};

// Import employees
const importEmployees = () => {
  toast.add({
    severity: 'info',
    summary: 'Import',
    detail: 'Import employees from file',
    life: 3000,
  });
};

// Export employees
const exportEmployees = () => {
  toast.add({
    severity: 'info',
    summary: 'Export',
    detail: 'Export employees to file',
    life: 3000,
  });
};

// Initialize component
onMounted(() => {
  loading.value = true;
  // In a real app, we would fetch employees from an API here
  setTimeout(() => {
    loading.value = false;
  }, 500);
});
</script>

<style scoped>
.p-card {
  margin-bottom: 1rem;
}

:deep(.p-card-title) {
  font-size: 1.25rem;
  font-weight: 600;
}

:deep(.p-datatable) {
  font-size: 0.9rem;
}

:deep(.p-datatable .p-datatable-thead > tr > th) {
  background-color: #f8f9fa;
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.8rem;
  letter-spacing: 0.5px;
}

:deep(.p-datatable .p-datatable-tbody > tr > td) {
  padding: 0.75rem 1rem;
}

:deep(.p-paginator) {
  padding: 0.5rem;
}

.confirmation-content {
  display: flex;
  align-items: center;
  justify-content: center;
}

:deep(.p-avatar) {
  background-color: var(--primary-color);
  color: var(--primary-color-text);
  font-weight: 600;
}
</style>
