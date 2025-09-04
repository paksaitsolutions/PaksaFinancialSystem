<template>
  <div class="leave-requests-view">
    <Breadcrumb :home="home" :model="breadcrumbItems" class="mb-3" />
    <div class="card">
      <div class="flex justify-content-between align-items-center mb-4">
        <div>
          <h1>Leave Requests</h1>
        </div>
        <div>
          <Button label="New Leave Request" icon="pi pi-plus" class="p-button-success" @click="showNewLeaveRequestDialog" />
        </div>
      </div>
      
      <div class="card">
        <DataTable
          :value="leaveRequests"
          :paginator="true"
          :rows="10"
          :rowsPerPageOptions="[5,10,25,50]"
          paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
          currentPageReportTemplate="Showing {first} to {last} of {totalRecords} leave requests"
          :globalFilterFields="['name', 'employeeId']"
          v-model:filters="dataTableFilters"
          class="p-datatable-sm"
          scrollable
          scrollHeight="400px"
          v-model:selection="selectedLeaveRequests"
          dataKey="id"
          :loading="loading">
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
          <Column field="departmentId" header="Department" :sortable="true">
            <template #body="{ data }">
              {{ getDepartmentName(data.departmentId) }}
            </template>
          </Column>
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
              <Button icon="pi pi-pencil" class="p-button-text p-button-rounded p-button-success" @click="editLeaveRequest(data)" />
              <Button icon="pi pi-trash" class="p-button-text p-button-rounded p-button-danger" @click="confirmDeleteLeaveRequest(data)" />
            </template>
          </Column>
        </DataTable>
      </div>
    </div>

    <!-- New/Edit Leave Request Dialog -->
    <Dialog 
      v-model:visible="leaveRequestDialog" 
      :header="editing ? 'Edit Leave Request' : 'New Leave Request'" 
      :modal="true"
      :style="{width: '600px'}"
      :closable="!submitting"
      :closeOnEscape="!submitting"
    >
      <div class="grid p-fluid">
        <div class="col-12">
          <div class="field">
            <label for="name" class="block mb-2">Full Name <span class="text-red-500">*</span></label>
            <InputText id="name" v-model="leaveRequest.name" class="w-full" :class="{'p-invalid': submitted && !leaveRequest.name}" />
            <small v-if="submitted && !leaveRequest.name" class="p-error">Name is required.</small>
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="email" class="block mb-2">Email <span class="text-red-500">*</span></label>
            <InputText id="email" v-model="leaveRequest.email" class="w-full" :class="{'p-invalid': submitted && !leaveRequest.email}" />
            <small v-if="submitted && !leaveRequest.email" class="p-error">Email is required.</small>
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="phone" class="block mb-2">Phone</label>
            <InputText id="phone" v-model="leaveRequest.phone" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="department" class="block mb-2">Department</label>
            <Dropdown 
              id="department" 
              v-model="leaveRequest.departmentId" 
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
            <InputText id="position" v-model="leaveRequest.position" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="hireDate" class="block mb-2">Hire Date</label>
            <Calendar id="hireDate" v-model="leaveRequest.hireDate" dateFormat="yy-mm-dd" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="status" class="block mb-2">Status</label>
            <Dropdown 
              id="status" 
              v-model="leaveRequest.status" 
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
        <Button label="Save" icon="pi pi-check" class="p-button-text" @click="saveLeaveRequest" :loading="submitting" />
      </template>
    </Dialog>

    <!-- Delete Confirmation Dialog -->
    <Dialog v-model:visible="deleteLeaveRequestDialog" :style="{width: '450px'}" header="Confirm" :modal="true">
      <div class="flex align-items-center justify-content-center">
        <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
        <span v-if="leaveRequest">Are you sure you want to delete <b>{{leaveRequest.name}}</b>?</span>
      </div>
      <template #footer>
        <Button label="No" icon="pi pi-times" class="p-button-text" @click="deleteLeaveRequestDialog = false"/>
        <Button label="Yes" icon="pi pi-check" class="p-button-text" @click="deleteLeaveRequest"/>
      </template>
    </Dialog>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, defineAsyncComponent } from 'vue';
import { useToast } from 'primevue/usetoast';
import { FilterMatchMode } from 'primevue/api';
import type { DataTableFilterMeta } from 'primevue/datatable';
import * as XLSX from 'xlsx';

interface Department {
  id: number;
  name: string;
}

interface StatusOption {
  label: string;
  value: LeaveStatus;
}

type LeaveStatus = 'PENDING' | 'APPROVED' | 'REJECTED';

interface LeaveRequest {
  id: number | null;
  employeeId: string;
  name: string;
  email: string;
  phone: string;
  departmentId: number | null;
  position: string;
  hireDate: Date | null;
  status: LeaveStatus;
  avatar?: string | null;
}

interface LeaveRequestFilter {
  search: string;
  department: number | null;
  status: string | null;
}

export default defineComponent({
  name: 'HrmLeaveRequests',
  components: {
    Breadcrumb: defineAsyncComponent(() => import('primevue/breadcrumb')),
    Button: defineAsyncComponent(() => import('primevue/button')),
    Card: defineAsyncComponent(() => import('primevue/card')),
    InputText: defineAsyncComponent(() => import('primevue/inputtext')),
    Dropdown: defineAsyncComponent(() => import('primevue/dropdown')),
    DataTable: defineAsyncComponent(() => import('primevue/datatable')),
    Column: defineAsyncComponent(() => import('primevue/column')),
    Avatar: defineAsyncComponent(() => import('primevue/avatar')),
    Tag: defineAsyncComponent(() => import('primevue/tag')),
    Dialog: defineAsyncComponent(() => import('primevue/dialog')),
    Calendar: defineAsyncComponent(() => import('primevue/calendar')),
  },
  setup() {
    const toast = useToast();
    
    // Refs
    const home = ref({ 
      icon: 'pi pi-home', 
      to: '/dashboard' 
    });
    
    // Data properties
    const breadcrumbItems = ref([
      { label: 'HRM' },
      { label: 'Leave Requests' }
    ]);
    
    // Component state
    const leaveRequests = ref<LeaveRequest[]>([]);
    const loading = ref(false);
    const leaveRequestDialog = ref(false);
    const deleteLeaveRequestDialog = ref(false);
    const selectedLeaveRequests = ref<LeaveRequest[]>([]);
    const submitting = ref(false);
    const submitted = ref(false);
    const editing = ref(false);
    
    // Data table filters
    const dataTableFilters = ref<DataTableFilterMeta>({
      global: { value: null, matchMode: FilterMatchMode.CONTAINS },
      status: { value: null, matchMode: FilterMatchMode.EQUALS },
      departmentId: { value: null, matchMode: FilterMatchMode.EQUALS }
    });
    
    // Form data
    const leaveRequest = ref<Partial<LeaveRequest>>({
      id: null,
      employeeId: '',
      name: '',
      email: '',
      phone: '',
      departmentId: null,
      position: '',
      hireDate: null,
      status: 'PENDING',
      avatar: null
    });
    
    // Dropdown options
    const departments = ref<Department[]>([
      { id: 1, name: 'HR' },
      { id: 2, name: 'Finance' },
      { id: 3, name: 'IT' },
      { id: 4, name: 'Operations' },
      { id: 5, name: 'Sales' }
    ]);
    
    const statuses = ref<StatusOption[]>([
      { label: 'Pending', value: 'PENDING' },
      { label: 'Approved', value: 'APPROVED' },
      { label: 'Rejected', value: 'REJECTED' }
    ]);

    // Helper functions
    const formatDate = (date: Date | null | undefined): string => {
      if (!date) return '';
      return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    };

    const getStatusSeverity = (status: LeaveStatus) => {
      switch (status) {
        case 'APPROVED':
          return 'success';
        case 'REJECTED':
          return 'danger';
        default:
          return 'warning';
      }
    };

    const showNewLeaveRequestDialog = () => {
      leaveRequest.value = {
        id: null,
        employeeId: '',
        name: '',
        email: '',
        phone: '',
        departmentId: null,
        position: '',
        hireDate: null,
        status: 'PENDING',
        avatar: null
      };
      submitted.value = false;
      editing.value = false;
      leaveRequestDialog.value = true;
    };

    const hideDialog = () => {
      leaveRequestDialog.value = false;
      submitted.value = false;
    };

    const getDepartmentName = (departmentId: number | null): string => {
      if (!departmentId) return '';
      const dept = departments.value.find(d => d.id === departmentId);
      return dept ? dept.name : '';
    };

    const saveLeaveRequest = async () => {
      submitted.value = true;
      
      // Validate required fields
      if (!leaveRequest.value.name || !leaveRequest.value.email) {
        return;
      }

      // Simulate API call
      submitting.value = true;
      
      try {
        // Simulate network delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        if (editing.value) {
          // Update existing request
          const index = leaveRequests.value.findIndex(lr => lr.id === leaveRequest.value.id);
          if (index !== -1) {
            leaveRequests.value[index] = { ...leaveRequest.value as LeaveRequest };
          }
          toast.add({ severity: 'success', summary: 'Success', detail: 'Leave Request Updated', life: 3000 });
        } else {
          // Add new request
          const newRequest: LeaveRequest = {
            ...leaveRequest.value as LeaveRequest,
            id: Math.floor(Math.random() * 1000),
            employeeId: `EMP${Math.floor(1000 + Math.random() * 9000)}`
          };
          leaveRequests.value = [newRequest, ...leaveRequests.value];
          toast.add({ severity: 'success', summary: 'Success', detail: 'Leave Request Created', life: 3000 });
        }
        
        leaveRequestDialog.value = false;
        leaveRequest.value = {
          id: null,
          employeeId: '',
          name: '',
          email: '',
          phone: '',
          departmentId: null,
          position: '',
          hireDate: null,
          status: 'PENDING',
          avatar: null
        };
      } catch (error) {
        console.error('Error saving leave request:', error);
        toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to save leave request', life: 3000 });
      } finally {
        submitting.value = false;
      }
    };

    const editLeaveRequest = (request: LeaveRequest) => {
      leaveRequest.value = { ...request };
      editing.value = true;
      leaveRequestDialog.value = true;
    };

    const confirmDeleteLeaveRequest = (request: LeaveRequest) => {
      leaveRequest.value = { ...request };
      deleteLeaveRequestDialog.value = true;
    };

    const deleteLeaveRequest = async () => {
      try {
        leaveRequests.value = leaveRequests.value.filter(lr => lr.id !== leaveRequest.value.id);
        deleteLeaveRequestDialog.value = false;
        toast.add({ severity: 'success', summary: 'Success', detail: 'Leave Request Deleted', life: 3000 });
      } catch (error) {
        console.error('Error deleting leave request:', error);
        toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to delete leave request', life: 3000 });
      }
    };

    const exportToExcel = () => {
      import('xlsx').then((xlsx) => {
        const worksheet = xlsx.utils.json_to_sheet(leaveRequests.value);
        const workbook = { Sheets: { data: worksheet }, SheetNames: ['data'] };
        const excelBuffer = xlsx.write(workbook, { bookType: 'xlsx', type: 'array' });
        saveAsExcelFile(excelBuffer, 'leave_requests');
      });
    };

    const saveAsExcelFile = (buffer: any, fileName: string) => {
      import('file-saver').then((module) => {
        if (module && module.default) {
          const EXCEL_TYPE = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;charset=UTF-8';
          const data = new Blob([buffer], { type: EXCEL_TYPE });
          module.default.saveAs(data, `${fileName}_export_${new Date().getTime()}.xlsx`);
        }
      });
    };

    // Load initial data
    onMounted(() => {
      loading.value = true;
      // Simulate API call
      setTimeout(() => {
        leaveRequests.value = [
          {
            id: 1,
            employeeId: 'EMP1001',
            name: 'John Doe',
            email: 'john.doe@example.com',
            phone: '123-456-7890',
            departmentId: 1,
            position: 'HR Manager',
            hireDate: new Date('2020-01-15'),
            status: 'APPROVED',
            avatar: null
          },
          {
            id: 2,
            employeeId: 'EMP1002',
            name: 'Jane Smith',
            email: 'jane.smith@example.com',
            phone: '123-456-7891',
            departmentId: 2,
            position: 'Financial Analyst',
            hireDate: new Date('2021-03-22'),
            status: 'PENDING',
            avatar: null
          }
        ];
        loading.value = false;
      }, 1000);
    });

    // Return all reactive references and methods
    return {
      // Refs
      home: home.value,
      breadcrumbItems,
      
      // State
      leaveRequests,
      loading,
      leaveRequestDialog,
      deleteLeaveRequestDialog,
      selectedLeaveRequests,
      departments,
      leaveRequest,
      submitting,
      submitted,
      editing,
      dataTableFilters,
      statuses,
      
      // Methods
      showNewLeaveRequestDialog,
      hideDialog,
      saveLeaveRequest,
      editLeaveRequest,
      confirmDeleteLeaveRequest,
      deleteLeaveRequest,
      exportToExcel,
      getStatusSeverity,
      formatDate,
      getDepartmentName
    };
  }
});
</script>

<style scoped>
.leave-requests-view {
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
  background: var(--surface-50);
  color: var(--text-color);
  font-weight: 600;
}

:deep(.p-datatable .p-datatable-tbody > tr > td) {
  padding: 0.5rem 1rem;
  border: 1px solid var(--surface-200);
}

:deep(.p-dialog .p-dialog-header) {
  padding: 1.5rem 1.5rem 0.5rem 1.5rem;
}

:deep(.p-dialog .p-dialog-content) {
  padding: 0 1.5rem 1.5rem 1.5rem;
}

:deep(.p-dialog .p-dialog-footer) {
  padding: 0.5rem 1.5rem 1.5rem 1.5rem;
  border-top: 1px solid var(--surface-200);
}

.field {
  margin-bottom: 1.5rem;
}
</style>