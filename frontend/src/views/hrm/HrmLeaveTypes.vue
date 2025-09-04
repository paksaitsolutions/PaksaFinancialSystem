<template>
  <div class="employees-view">
    <div class="grid">
      <div class="col-12">
        <div class="flex justify-content-between align-items-center mb-4">
          <div>
            <h1>Leave Types Management</h1>
            <Breadcrumb :home="home" :model="items" />
          </div>
          <div>
            <Button label="New Leave Type" icon="pi pi-plus" class="p-button-success" @click="showNewLeaveTypeDialog" />
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
                <Button label="Filter" icon="pi pi-filter" class="p-button-outlined w-full" @click="loadLeaveTypes" />
              </div>
            </div>
          </template>
        </Card>
      </div>

      <!-- Leave Type List -->
      <div class="col-12">
        <Card>
          <template #header>
            <div class="flex justify-content-between align-items-center">
              <h3>Leave Type List</h3>
              <div>
                <Button icon="pi pi-download" class="p-button-text" @click="exportToCSV" />
                <Button icon="pi pi-refresh" class="p-button-text" @click="loadLeaveTypes" />
              </div>
            </div>
          </template>
          <template #content>
            <DataTable 
              :value="leaveTypes" 
              :paginator="true" 
              :rows="10" 
              :loading="loading"
              :rowsPerPageOptions="[5,10,25,50]"
              paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
              currentPageReportTemplate="Showing {first} to {last} of {totalRecords} leave types"
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
                  <Button icon="pi pi-pencil" class="p-button-text p-button-rounded p-button-success" @click="editLeaveType(data)" />
                  <Button icon="pi pi-trash" class="p-button-text p-button-rounded p-button-danger" @click="confirmDeleteLeaveType(data)" />
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </div>
    </div>

    <!-- New/Edit Leave Type Dialog -->
    <Dialog 
      v-model:visible="leaveTypeDialog" 
      :header="editing ? 'Edit Leave Type' : 'New Leave Type'" 
      :modal="true"
      :style="{width: '600px'}"
      :closable="!submitting"
      :closeOnEscape="!submitting"
    >
      <div class="grid p-fluid">
        <div class="col-12">
          <div class="field">
            <label for="name" class="block mb-2">Full Name <span class="text-red-500">*</span></label>
            <InputText id="name" v-model="leaveType.name" class="w-full" :class="{'p-invalid': submitted && !leaveType.name}" />
            <small v-if="submitted && !leaveType.name" class="p-error">Name is required.</small>
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="email" class="block mb-2">Email <span class="text-red-500">*</span></label>
            <InputText id="email" v-model="leaveType.email" class="w-full" :class="{'p-invalid': submitted && !leaveType.email}" />
            <small v-if="submitted && !leaveType.email" class="p-error">Email is required.</small>
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="phone" class="block mb-2">Phone</label>
            <InputText id="phone" v-model="leaveType.phone" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="department" class="block mb-2">Department</label>
            <Dropdown 
              id="department" 
              v-model="leaveType.departmentId" 
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
            <InputText id="position" v-model="leaveType.position" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="hireDate" class="block mb-2">Hire Date</label>
            <Calendar id="hireDate" v-model="leaveType.hireDate" dateFormat="yy-mm-dd" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="status" class="block mb-2">Status</label>
            <Dropdown 
              id="status" 
              v-model="leaveType.status" 
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
        <Button label="Save" icon="pi pi-check" class="p-button-text" @click="saveLeaveType" :loading="submitting" />
      </template>
    </Dialog>

    <!-- Delete Confirmation Dialog -->
    <Dialog v-model:visible="deleteLeaveTypeDialog" :style="{width: '450px'}" header="Confirm" :modal="true">
      <div class="flex align-items-center justify-content-center">
        <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
        <span v-if="leaveType">Are you sure you want to delete <b>{{leaveType.name}}</b>?</span>
      </div>
      <template #footer>
        <Button label="No" icon="pi pi-times" class="p-button-text" @click="deleteLeaveTypeDialog = false" />
        <Button label="Yes" icon="pi pi-check" class="p-button-danger" @click="deleteLeaveType" />
      </template>
    </Dialog>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import * as XLSX from 'xlsx';
import { FilterMatchMode } from 'primevue/api';
import Card from 'primevue/card';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import Dropdown from 'primevue/dropdown';
import Calendar from 'primevue/calendar';
import Dialog from 'primevue/dialog';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import Avatar from 'primevue/avatar';
import Tag from 'primevue/tag';

interface LeaveType {
  id: number | null;
  employeeId: string;
  name: string;
  email: string;
  phone: string;
  departmentId: number | null;
  position: string;
  hireDate: Date | null;
  status: string;
  avatar?: string;
}

interface LeaveType {
  id: number | null;
  employeeId: string;
  name: string;
  email: string;
  phone: string;
  departmentId: number | null;
  position: string;
  hireDate: Date | null;
  status: string;
  avatar?: string;
}

export default defineComponent({
  name: 'HrmLeaveTypes',
  setup() {
    const toast = useToast();
    const loading = ref(false);
    const submitting = ref(false);
    const leaveTypeDialog = ref(false);
    const deleteLeaveTypeDialog = ref(false);
    const editing = ref(false);
    const submitted = ref(false);
    
    const leaveTypes = ref<LeaveType[]>([]);
    const leaveType = ref<LeaveType>({} as LeaveType);
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
    const items = ref([{ label: 'HRM', to: '/hrm' }, { label: 'Leave Types' }]);

    const loadLeaveTypes = async () => {
      loading.value = true;
      try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Mock data - replace with actual API call
        leaveTypes.value = [
          { id: 1, employeeId: 'POS-001', name: 'Software Engineer', email: 'software.engineer@example.com', phone: '+1234567890',
            departmentId: 3, position: 'Senior Developer', hireDate: new Date('2020-05-15'), status: 'Active',
            avatar: 'https://primefaces.org/cdn/primevue/images/avatar/amyelsner.png' },
          { id: 2, employeeId: 'POS-002', name: 'Marketing Specialist', email: 'marketing.specialist@example.com', phone: '+1987654321',
            departmentId: 2, position: 'Marketing Manager', hireDate: new Date('2019-11-10'), status: 'Active',
            avatar: 'https://primefaces.org/cdn/primevue/images/avatar/asiyajavayant.png' },
          { id: 3, employeeId: 'POS-003', name: 'Sales Representative', email: 'sales.representative@example.com', phone: '+1122334455',
            departmentId: 1, position: 'Sales Executive', hireDate: new Date('2021-02-20'), status: 'On Leave',
            avatar: 'https://primefaces.org/cdn/primevue/images/avatar/onyamalimba.png' },
          { id: 4, employeeId: 'POS-004', name: 'HR Coordinator', email: 'hr.coordinator@example.com', phone: '+1555666777',
            departmentId: 4, position: 'HR Manager', hireDate: new Date('2018-08-05'), status: 'Active',
            avatar: 'https://primefaces.org/cdn/primevue/images/avatar/ionibowcher.png' },
          { id: 5, employeeId: 'POS-005', name: 'Financial Analyst', email: 'financial.analyst@example.com', phone: '+1444555666',
            departmentId: 5, position: 'Financial Analyst', hireDate: new Date('2022-01-10'), status: 'Active',
            avatar: 'https://primefaces.org/cdn/primevue/images/avatar/xuxuefeng.png' }
        ] as unknown as LeaveType[];
      } catch (error) {
        console.error('Error loading leave types:', error);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to load leave types',
          life: 3000
        });
      } finally {
        loading.value = false;
      }
    };

    const showNewLeaveTypeDialog = () => {
      leaveType.value = {
        id: null,
        employeeId: '',
        name: '',
        email: '',
        phone: '',
        departmentId: null,
        position: '',
        hireDate: new Date(),
        status: 'Active',
        avatar:''
      };
      submitted.value = false;
      editing.value = false;
      leaveTypeDialog.value = true;
    };

    const editLeaveType = (pos) => {
      leaveType.value = { ...pos };
      editing.value = true;
      leaveTypeDialog.value = true;
    };

    const hideDialog = () => {
      leaveTypeDialog.value = false;
      submitted.value = false;
    };

    const saveLeaveType = () => {
      submitted.value = true;
      
      if (!leaveType.value.name || !leaveType.value.email) {
        return;
      }

      submitting.value = true;
      
      // Simulate API call
      setTimeout(() => {
        const index = leaveTypes.value.findIndex(pos => pos.id === leaveType.value.id);
        
        if (index > -1) {
          // Update existing leave type
          leaveTypes.value[index] = { ...leaveType.value };
          toast.add({
            severity: 'success',
            summary: 'Successful',
            detail: 'Leave Type Updated',
            life: 3000
          });
        } else {
          // Add new leave type
          leaveType.value.id = leaveTypes.value.length + 1;
          leaveType.value.employeeId = `POS-${String(leaveType.value.id).padStart(3, '0')}`;
          leaveTypes.value.push({ ...leaveType.value });
          
          toast.add({
            severity: 'success',
            summary: 'Successful',
            detail: 'Leave Type Created',
            life: 3000
          });
        }
        
        leaveTypeDialog.value = false;
        submitting.value = false;
      }, 1000);
    };

    const confirmDeleteLeaveType = (pos) => {
      leaveType.value = pos;
      deleteLeaveTypeDialog.value = true;
    };

    const deleteLeaveType = () => {
      leaveTypes.value = leaveTypes.value.filter(pos => pos.id !== leaveType.value.id);
      deleteLeaveTypeDialog.value = false;
      leaveType.value = {};
      
      toast.add({
        severity: 'success',
        summary: 'Successful',
        detail: 'Leave Type Deleted',
        life: 3000
      });
    };

    const exportToCSV = () => {
      try {
        const worksheet = XLSX.utils.json_to_sheet(leaveTypes.value);
        const workbook = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(workbook, worksheet, 'Leave Types');
        
        // Generate XLSX file and trigger download
        XLSX.writeFile(workbook, 'leaveTypes.xlsx', { bookType: 'xlsx', type: 'file' });
      } catch (error) {
        console.error('Error exporting to Excel:', error);
        toast.add({
          severity: 'error',
          summary: 'Export Failed',
          detail: 'Failed to export leave types data',
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

    const getDepartmentName = (departmentId: number) => {
      const department = departments.value.find(d => d.id === departmentId);
      return department ? department.name : '';
    }

    onMounted(() => {
      loadLeaveTypes();
    });

    return {
      leaveTypes,
      leaveType,
      departments,
      statuses,
      filters,
      loading,
      submitting,
      leaveTypeDialog,
      deleteLeaveTypeDialog,
      editing,
      submitted,
      home,
      items,
      loadLeaveTypes,
      showNewLeaveTypeDialog,
      editLeaveType,
      hideDialog,
      saveLeaveType,
      confirmDeleteLeaveType,
      deleteLeaveType,
      exportToCSV,
      formatDate,
      getStatusSeverity,
      getDepartmentName
    };
  },
  components: {
    Card,
    InputText,
    Button,
    Dropdown,
    Calendar,
    Dialog,
    Column,
    DataTable,
    Avatar,
    Tag
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