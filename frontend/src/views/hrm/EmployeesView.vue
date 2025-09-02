<template>
  <div class="employees-view">
    <div class="grid">
      <div class="col-12">
        <div class="flex justify-content-between align-items-center mb-4">
          <div>
            <h1>Employees</h1>
            <Breadcrumb :home="home" :model="items" />
          </div>
          <div>
            <Button label="New Employee" icon="pi pi-plus" class="p-button-success" @click="showNewEmployeeDialog" />
          </div>
        </div>
      </div>

      <!-- Filters -->
      <div class="col-12">
        <Card>
          <template #content>
            <div class="grid p-fluid">
              <div class="col-12 md:col-4">
                <span class="p-float-label">
                  <InputText id="search" v-model="filters.search" class="w-full" />
                  <label for="search">Search by name or ID</label>
                </span>
              </div>
              <div class="col-12 md:col-3">
                <span class="p-float-label">
                  <Dropdown 
                    v-model="filters.department" 
                    :options="departments" 
                    optionLabel="name" 
                    optionValue="id" 
                    :showClear="true"
                    class="w-full"
                  />
                  <label>Department</label>
                </span>
              </div>
              <div class="col-12 md:col-3">
                <span class="p-float-label">
                  <Dropdown 
                    v-model="filters.status" 
                    :options="statuses" 
                    optionLabel="label" 
                    optionValue="value" 
                    :showClear="true"
                    class="w-full"
                  />
                  <label>Status</label>
                </span>
              </div>
              <div class="col-12 md:col-2 flex align-items-end">
                <Button label="Filter" icon="pi pi-filter" class="p-button-outlined w-full" @click="loadEmployees" />
              </div>
            </div>
          </template>
        </Card>
      </div>

      <!-- Employee List -->
      <div class="col-12">
        <Card>
          <template #header>
            <div class="flex justify-content-between align-items-center">
              <h3>Employee List</h3>
              <div>
                <Button icon="pi pi-download" class="p-button-text" @click="exportToCSV" />
                <Button icon="pi pi-refresh" class="p-button-text" @click="loadEmployees" />
              </div>
            </div>
          </template>
          <template #content>
            <DataTable 
              :value="employees" 
              :paginator="true" 
              :rows="10" 
              :loading="loading"
              :rowsPerPageOptions="[5,10,25,50]"
              paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
              currentPageReportTemplate="Showing {first} to {last} of {totalRecords} employees"
              responsiveLayout="scroll"
              :globalFilterFields="['name', 'employeeId', 'email', 'phone']"
              v-model:filters="filters"
              filterDisplay="menu"
            >
              <Column field="employeeId" header="ID" :sortable="true" style="width: 100px" />
              <Column field="name" header="Name" :sortable="true">
                <template #body="{ data }">
                  <div class="flex align-items-center">
                    <Avatar :image="data.avatar" :label="data.avatar ? '' : data.name.charAt(0)" shape="circle" class="mr-2" />
                    <span>{{ data.name }}</span>
                  </div>
                </template>
              </Column>
              <Column field="email" header="Email" :sortable="true" />
              <Column field="phone" header="Phone" :sortable="true" />
              <Column field="department" header="Department" :sortable="true" />
              <Column field="position" header="Position" :sortable="true" />
              <Column field="hireDate" header="Hire Date" :sortable="true">
                <template #body="{ data }">
                  {{ formatDate(data.hireDate) }}
                </template>
              </Column>
              <Column field="status" header="Status" :sortable="true">
                <template #body="{ data }">
                  <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
                </template>
              </Column>
              <Column header="Actions" style="width: 150px">
                <template #body="{ data }">
                  <Button icon="pi pi-pencil" class="p-button-text p-button-rounded p-button-success" @click="editEmployee(data)" />
                  <Button icon="pi pi-trash" class="p-button-text p-button-rounded p-button-danger" @click="confirmDeleteEmployee(data)" />
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </div>
    </div>

    <!-- New/Edit Employee Dialog -->
    <Dialog 
      v-model:visible="employeeDialog" 
      :header="editing ? 'Edit Employee' : 'New Employee'" 
      :modal="true"
      :style="{width: '600px'}"
      :closable="!submitting"
      :closeOnEscape="!submitting"
    >
      <div class="grid p-fluid">
        <div class="col-12">
          <div class="field">
            <label for="name" class="block mb-2">Full Name <span class="text-red-500">*</span></label>
            <InputText id="name" v-model="employee.name" class="w-full" :class="{'p-invalid': submitted && !employee.name}" />
            <small v-if="submitted && !employee.name" class="p-error">Name is required.</small>
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="email" class="block mb-2">Email <span class="text-red-500">*</span></label>
            <InputText id="email" v-model="employee.email" class="w-full" :class="{'p-invalid': submitted && !employee.email}" />
            <small v-if="submitted && !employee.email" class="p-error">Email is required.</small>
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="phone" class="block mb-2">Phone</label>
            <InputText id="phone" v-model="employee.phone" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="department" class="block mb-2">Department</label>
            <Dropdown 
              id="department" 
              v-model="employee.departmentId" 
              :options="departments" 
              optionLabel="name" 
              optionValue="id" 
              class="w-full"
            />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="position" class="block mb-2">Position</label>
            <InputText id="position" v-model="employee.position" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="hireDate" class="block mb-2">Hire Date</label>
            <Calendar id="hireDate" v-model="employee.hireDate" dateFormat="yy-mm-dd" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="status" class="block mb-2">Status</label>
            <Dropdown 
              id="status" 
              v-model="employee.status" 
              :options="statuses" 
              optionLabel="label" 
              optionValue="value" 
              class="w-full"
            />
          </div>
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" icon="pi pi-times" class="p-button-text" @click="hideDialog" :disabled="submitting" />
        <Button label="Save" icon="pi pi-check" class="p-button-text" @click="saveEmployee" :loading="submitting" />
      </template>
    </Dialog>

    <!-- Delete Confirmation Dialog -->
    <Dialog v-model:visible="deleteEmployeeDialog" :style="{width: '450px'}" header="Confirm" :modal="true">
      <div class="flex align-items-center justify-content-center">
        <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
        <span v-if="employee">Are you sure you want to delete <b>{{employee.name}}</b>?</span>
      </div>
      <template #footer>
        <Button label="No" icon="pi pi-times" class="p-button-text" @click="deleteEmployeeDialog = false" />
        <Button label="Yes" icon="pi pi-check" class="p-button-danger" @click="deleteEmployee" />
      </template>
    </Dialog>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import * as XLSX from 'xlsx';
import { FilterMatchMode } from 'primevue/api';

export default defineComponent({
  name: 'EmployeesView',
  setup() {
    const toast = useToast();
    const loading = ref(false);
    const submitting = ref(false);
    const employeeDialog = ref(false);
    const deleteEmployeeDialog = ref(false);
    const editing = ref(false);
    const submitted = ref(false);
    
    const employees = ref([]);
    const employee = ref({});
    const departments = ref([
      { id: 1, name: 'Sales' },
      { id: 2, name: 'Marketing' },
      { id: 3, name: 'Development' },
      { id: 4, name: 'HR' },
      { id: 5, name: 'Finance' },
      { id: 6, name: 'Operations' }
    ]);
    
    const statuses = ref([
      { label: 'Active', value: 'Active' },
      { label: 'On Leave', value: 'On Leave' },
      { label: 'Inactive', value: 'Inactive' },
      { label: 'Terminated', value: 'Terminated' }
    ]);

    const filters = ref({
      search: null,
      department: null,
      status: null,
      global: { value: null, matchMode: FilterMatchMode.CONTAINS }
    });

    const home = ref({ icon: 'pi pi-home', to: '/' });
    const items = ref([{ label: 'HRM', to: '/hrm' }, { label: 'Employees' }]);

    const loadEmployees = async () => {
      loading.value = true;
      try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Mock data - replace with actual API call
        employees.value = [
          { id: 1, employeeId: 'EMP-001', name: 'John Doe', email: 'john.doe@example.com', phone: '+1234567890', 
            department: 'Development', position: 'Senior Developer', hireDate: '2020-05-15', status: 'Active',
            avatar: 'https://primefaces.org/cdn/primevue/images/avatar/amyelsner.png' },
          { id: 2, employeeId: 'EMP-002', name: 'Jane Smith', email: 'jane.smith@example.com', phone: '+1987654321', 
            department: 'Marketing', position: 'Marketing Manager', hireDate: '2019-11-10', status: 'Active',
            avatar: 'https://primefaces.org/cdn/primevue/images/avatar/asiyajavayant.png' },
          { id: 3, employeeId: 'EMP-003', name: 'Mike Johnson', email: 'mike.johnson@example.com', phone: '+1122334455', 
            department: 'Sales', position: 'Sales Executive', hireDate: '2021-02-20', status: 'On Leave',
            avatar: 'https://primefaces.org/cdn/primevue/images/avatar/onyamalimba.png' },
          { id: 4, employeeId: 'EMP-004', name: 'Sarah Williams', email: 'sarah.williams@example.com', phone: '+1555666777', 
            department: 'HR', position: 'HR Manager', hireDate: '2018-08-05', status: 'Active',
            avatar: 'https://primefaces.org/cdn/primevue/images/avatar/ionibowcher.png' },
          { id: 5, employeeId: 'EMP-005', name: 'David Brown', email: 'david.brown@example.com', phone: '+1444555666', 
            department: 'Finance', position: 'Financial Analyst', hireDate: '2022-01-10', status: 'Active',
            avatar: 'https://primefaces.org/cdn/primevue/images/avatar/xuxuefeng.png' }
        ];
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
    };

    const showNewEmployeeDialog = () => {
      employee.value = {
        id: null,
        employeeId: '',
        name: '',
        email: '',
        phone: '',
        departmentId: null,
        position: '',
        hireDate: new Date(),
        status: 'Active'
      };
      submitted.value = false;
      editing.value = false;
      employeeDialog.value = true;
    };

    const editEmployee = (emp) => {
      employee.value = { ...emp };
      editing.value = true;
      employeeDialog.value = true;
    };

    const hideDialog = () => {
      employeeDialog.value = false;
      submitted.value = false;
    };

    const saveEmployee = () => {
      submitted.value = true;
      
      if (!employee.value.name || !employee.value.email) {
        return;
      }

      submitting.value = true;
      
      // Simulate API call
      setTimeout(() => {
        const index = employees.value.findIndex(emp => emp.id === employee.value.id);
        
        if (index > -1) {
          // Update existing employee
          employees.value[index] = { ...employee.value };
          toast.add({
            severity: 'success',
            summary: 'Successful',
            detail: 'Employee Updated',
            life: 3000
          });
        } else {
          // Add new employee
          employee.value.id = employees.value.length + 1;
          employee.value.employeeId = `EMP-${String(employee.value.id).padStart(3, '0')}`;
          employees.value.push({ ...employee.value });
          
          toast.add({
            severity: 'success',
            summary: 'Successful',
            detail: 'Employee Created',
            life: 3000
          });
        }
        
        employeeDialog.value = false;
        submitting.value = false;
      }, 1000);
    };

    const confirmDeleteEmployee = (emp) => {
      employee.value = emp;
      deleteEmployeeDialog.value = true;
    };

    const deleteEmployee = () => {
      employees.value = employees.value.filter(emp => emp.id !== employee.value.id);
      deleteEmployeeDialog.value = false;
      employee.value = {};
      
      toast.add({
        severity: 'success',
        summary: 'Successful',
        detail: 'Employee Deleted',
        life: 3000
      });
    };

    const exportToCSV = () => {
      try {
        const worksheet = XLSX.utils.json_to_sheet(employees.value);
        const workbook = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(workbook, worksheet, 'Employees');
        
        // Generate XLSX file and trigger download
        XLSX.writeFile(workbook, 'employees.xlsx', { bookType: 'xlsx', type: 'file' });
      } catch (error) {
        console.error('Error exporting to Excel:', error);
        toast.add({
          severity: 'error',
          summary: 'Export Failed',
          detail: 'Failed to export employees data',
          life: 3000
        });
      }
    };

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString();
    };

    const getStatusSeverity = (status) => {
      switch (status.toLowerCase()) {
        case 'active':
          return 'success';
        case 'on leave':
          return 'warning';
        case 'inactive':
          return 'info';
        case 'terminated':
          return 'danger';
        default:
          return null;
      }
    };

    onMounted(() => {
      loadEmployees();
    });

    return {
      employees,
      employee,
      departments,
      statuses,
      filters,
      loading,
      submitting,
      employeeDialog,
      deleteEmployeeDialog,
      editing,
      submitted,
      home,
      items,
      loadEmployees,
      showNewEmployeeDialog,
      editEmployee,
      hideDialog,
      saveEmployee,
      confirmDeleteEmployee,
      deleteEmployee,
      exportToCSV,
      formatDate,
      getStatusSeverity
    };
  }
});
</script>

<style scoped>
.employees-view {
  padding: 1rem;
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
