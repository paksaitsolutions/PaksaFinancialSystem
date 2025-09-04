<template>
  <div class="hrm-positions">
    <div class="grid">
      <div class="col-12">
        <div class="flex justify-content-between align-items-center mb-4">
          <div>
            <h1 class="text-3xl font-bold mb-2">Positions Management</h1>
            <Breadcrumb :home="home" :model="breadcrumbItems" class="p-0 border-none bg-transparent" />
          </div>
          <div>
            <Button 
              label="New Position" 
              icon="pi pi-plus" 
              class="p-button-success" 
              @click="showNewPositionDialog"
              v-tooltip="'Create a new position'"
            />
          </div>
        </div>
      </div>

      <!-- Filters -->
      <div class="col-12">
        <Card class="mb-4">
          <template #title>
            <div class="flex align-items-center">
              <i class="pi pi-filter mr-2"></i>
              <span>Filter Positions</span>
            </div>
          </template>
          <template #content>
            <div class="grid p-fluid">
              <div class="col-12 md:col-4">
                <span class="p-float-label">
                  <InputText 
                    id="search" 
                    v-model="filters.global.value"
                    class="w-full" 
                    placeholder="Search positions..."
                  />
                  <label for="search">Search by name or ID</label>
                </span>
              </div>
              <div class="col-12 md:col-3">
                <span class="p-float-label">
                  <Dropdown 
                    :model-value="filters.department.value"
                    @update:model-value="(val: number | null) => {
                      filters.department.value = val;
                    }"
                    :options="departments" 
                    optionLabel="name" 
                    optionValue="id"
                    :filter="true"
                    filterPlaceholder="Search department"
                    :showClear="true"
                    placeholder="Select Department"
                    class="w-full"
                  />
                  <label>Department</label>
                </span>
              </div>
              <div class="col-12 md:col-3">
                <span class="p-float-label">
                  <Dropdown 
                    :model-value="filters.status.value"
                    @update:model-value="(val: string | null) => {
                      filters.status.value = val;
                    }"
                    :options="statuses" 
                    optionLabel="label" 
                    optionValue="value"
                    :filter="true"
                    filterPlaceholder="Search status"
                    :showClear="true"
                    placeholder="Select Status"
                    class="w-full"
                  />
                  <label>Status</label>
                </span>
              </div>
              <div class="col-12 md:col-2 flex align-items-end">
                <Button label="Filter" icon="pi pi-filter" class="p-button-outlined w-full" @click="loadPositions" />
              </div>
            </div>
          </template>
        </Card>
      </div>

      <!-- Position List -->
      <div class="col-12">
        <Card>
          <template #header>
            <div class="flex justify-content-between align-items-center">
              <div class="flex align-items-center">
                <i class="pi pi-briefcase mr-2"></i>
                <h3 class="m-0">Position List</h3>
              </div>
              <div class="flex">
                <Button 
                  icon="pi pi-refresh" 
                  class="p-button-text p-button-rounded p-button-plain" 
                  @click="loadPositions"
                  v-tooltip="'Refresh positions'"
                />
                <Button 
                  icon="pi pi-download" 
                  class="p-button-text p-button-rounded p-button-plain" 
                  @click="exportToCSV"
                  v-tooltip="'Export to CSV'"
                />
              </div>
            </div>
          </template>
          <template #content>
            <DataTable 
              :value="positions" 
              :paginator="true" 
              :rows="10" 
              :rowsPerPageOptions="[5,10,25,50]"
              :loading="loading"
              :filters="filters.value"
              scrollable
              scrollHeight="flex"
              :globalFilterFields="['name', 'employeeId', 'email', 'phone', 'department', 'status']"
              class="p-datatable-gridlines"
              :paginatorTemplate="'FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown'"
              :currentPageReportTemplate="'Showing {first} to {last} of {totalRecords} positions'"
              dataKey="id"
              :lazy="true"
              :totalRecords="positions.length"
            >
              <template #empty>
                <div class="text-center p-4">No positions found.</div>
              </template>
              <template #loading>
                <div class="text-center p-4">
                  <i class="pi pi-spinner pi-spin" style="font-size: 2rem"></i>
                  <p>Loading...</p>
                </div>
              </template>
              <Column field="employeeId" header="ID" :sortable="true" style="width: 100px" />
              <Column field="name" header="Name" :sortable="true" style="min-width: 200px">
                <template #body="{ data }">
                  <div v-if="data" class="flex align-items-center">
                    <Avatar :image="data.avatar || undefined" :label="data.avatar ? '' : data.name?.charAt(0) || ''" shape="circle" class="mr-2" />
                    <span>{{ data.name || '' }}</span>
                  </div>
                </template>
              </Column>
              <Column field="email" header="Email" :sortable="true" style="min-width: 200px" />
              <Column field="phone" header="Phone" :sortable="true" style="min-width: 150px" />
              <Column field="department" header="Department" :sortable="true" style="min-width: 150px" />
              <Column field="position" header="Position" :sortable="true" style="min-width: 150px" />
              <Column field="hireDate" header="Hire Date" :sortable="true" style="min-width: 150px">
                <template #body="{ data }">
                  {{ data?.hireDate ? formatDate(data.hireDate) : '' }}
                </template>
              </Column>
              <Column field="status" header="Status" :sortable="true" style="min-width: 150px">
                <template #body="{ data }">
                  <Tag v-if="data?.status" :value="data.status" :severity="getStatusSeverity(data.status)" />
                </template>
              </Column>
              <Column header="Actions" style="width: 150px">
                <template #body="{ data }">
                  <div class="flex gap-2">
                    <Button 
                      icon="pi pi-pencil" 
                      class="p-button-text p-button-rounded p-button-success" 
                      @click="editPosition(data as Position)" 
                      v-tooltip="'Edit Position'"
                    />
                    <Button 
                      icon="pi pi-trash" 
                      class="p-button-text p-button-rounded p-button-danger" 
                      @click="confirmDeletePosition(data as Position)" 
                      v-tooltip="'Delete Position'"
                    />
                  </div>
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </div>
    </div>

    <!-- New/Edit Position Dialog -->
    <Dialog 
      v-model:visible="positionDialog" 
      :header="editing ? 'Edit Position' : 'New Position'" 
      :modal="true"
      :style="{width: '600px'}"
      :closable="!submitting"
      :closeOnEscape="!submitting"
    >
      <div class="grid p-fluid">
        <div class="col-12">
          <div class="field">
            <label for="name" class="block mb-2">Full Name <span class="text-red-500">*</span></label>
            <InputText 
              id="name" 
              :model-value="position.name || ''"
              @update:model-value="(val: unknown) => { position.name = (val as string) || ''; }"
              :class="{ 'p-invalid': submitted && !position.name }" 
              class="w-full" 
              @keydown.enter="savePosition"
              autofocus
              placeholder="Enter full name"
            />
            <small v-if="submitted && !position.name" class="p-error">Name is required.</small>
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="email" class="block mb-2">Email <span class="text-red-500">*</span></label>
            <InputText 
              id="email" 
              :model-value="position.email || ''"
              @update:model-value="(val: unknown) => { position.email = (val as string) || ''; }"
              :class="{ 'p-invalid': submitted && !position.email }" 
              class="w-full" 
              type="email"
              placeholder="Enter email"
            />
            <small v-if="submitted && !position.email" class="p-error">Email is required.</small>
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="phone" class="block mb-2">Phone</label>
            <InputText 
              id="phone" 
              :model-value="position.phone || ''"
              @update:model-value="(val: unknown) => { position.phone = (val as string) || ''; }"
              class="w-full" 
              placeholder="Enter phone number"
              @keydown.enter="savePosition"
            />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="department" class="block mb-2">Department</label>
            <Dropdown 
              v-model="position.departmentId" 
              :options="departments" 
              optionLabel="name" 
              optionValue="id" 
              class="w-full"
              placeholder="Select Department"
              :filter="true"
              filterPlaceholder="Search department"
            />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="position" class="block mb-2">Position</label>
            <InputText 
              id="position" 
              :model-value="position.position || ''"
              @update:model-value="(val: unknown) => { position.position = (val as string) || ''; }"
              class="w-full" 
              placeholder="Enter position"
            />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="hireDate" class="block mb-2">Hire Date</label>
            <Calendar 
              :model-value="position.hireDate"
              @update:model-value="(val: unknown) => {
                if (Array.isArray(val)) {
                  position.hireDate = (val[0] as Date) || null;
                } else {
                  position.hireDate = (val as Date) || null;
                }
              }"
              dateFormat="yy-mm-dd" 
              class="w-full"
              :showIcon="true"
              :showButtonBar="true"
            />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="status" class="block mb-2">Status</label>
            <Dropdown 
              :model-value="position.status || ''"
              @update:model-value="(val: string) => position.status = val"
              :options="statuses" 
              optionLabel="label" 
              optionValue="value" 
              :class="{ 'p-invalid': submitted && !position.status }"
              class="w-full"
              placeholder="Select Status"
              :filter="true"
              filterPlaceholder="Search status"
            />
          </div>
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" icon="pi pi-times" class="p-button-text" @click="hideDialog" :disabled="submitting" />
        <Button label="Save" icon="pi pi-check" class="p-button-text" @click="savePosition" :loading="submitting" />
      </template>
    </Dialog>

    <!-- Delete Confirmation Dialog -->
    <Dialog v-model:visible="deletePositionDialog" :style="{width: '450px'}" header="Confirm" :modal="true">
      <div class="flex align-items-center justify-content-center">
        <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
        <span v-if="position">Are you sure you want to delete <b>{{position.name}}</b>?</span>
      </div>
      <template #footer>
        <Button label="No" icon="pi pi-times" class="p-button-text" @click="deletePositionDialog = false" />
        <Button label="Yes" icon="pi pi-check" class="p-button-danger" @click="deletePosition" />
      </template>
    </Dialog>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import { FilterMatchMode } from 'primevue/api';
import Tooltip from 'primevue/tooltip';
import * as XLSX from 'xlsx';

// PrimeVue Components
import Button from 'primevue/button';
import Card from 'primevue/card';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import Dialog from 'primevue/dialog';
import Dropdown from 'primevue/dropdown';
import InputText from 'primevue/inputtext';
import Tag from 'primevue/tag';
import Avatar from 'primevue/avatar';
import Calendar from 'primevue/calendar';
import Breadcrumb from 'primevue/breadcrumb';

interface Department {
  id: number;
  name: string;
}

interface StatusOption {
  label: string;
  value: string;
}

interface Position {
  id: number | null;
  employeeId: string;
  name: string;
  email: string;
  phone: string;
  departmentId: number | null;
  position: string;
  hireDate: Date | null;
  status: string;
  avatar?: string | null;
  department?: string;
}

// Type for DataTable filters

export default defineComponent({
  name: 'HrmPositions',
  directives: {
    'tooltip': Tooltip
  },
  components: {
    Button,
    Breadcrumb,
    Card,
    Column,
    DataTable,
    Dialog,
    Dropdown,
    InputText,
    Tag,
    Avatar,
    Calendar
  },
  setup() {
    const toast = useToast();
    const loading = ref(false);
    const submitting = ref(false);
    const positionDialog = ref(false);
    const deletePositionDialog = ref(false);
    const editing = ref(false);
    const submitted = ref(false);
    
    const positions = ref<Position[]>([]);
    const position = ref<Position>({
      id: null,
      employeeId: '',
      name: '',
      email: '',
      phone: '',
      departmentId: null,
      position: '',
      hireDate: new Date(),
      status: 'Active',
      avatar: null,
      department: ''
    });
    const departments = ref<Department[]>([
      { id: 1, name: 'Sales' },
      { id: 2, name: 'Marketing' },
      { id: 3, name: 'Development' },
      { id: 4, name: 'HR' },
      { id: 5, name: 'Finance' },
      { id: 6, name: 'Operations' }
    ]);
    
    const statuses = ref<StatusOption[]>([
      { label: 'Active', value: 'Active' },
      { label: 'On Leave', value: 'On Leave' },
      { label: 'Inactive', value: 'Inactive' },
      { label: 'Terminated', value: 'Terminated' }
    ]);

    const filters = ref({
      global: { value: null, matchMode: FilterMatchMode.CONTAINS },
      name: { value: null, matchMode: FilterMatchMode.CONTAINS },
      employeeId: { value: null, matchMode: FilterMatchMode.CONTAINS },
      email: { value: null, matchMode: FilterMatchMode.CONTAINS },
      phone: { value: null, matchMode: FilterMatchMode.CONTAINS },
      department: { value: null, matchMode: FilterMatchMode.EQUALS },
      status: { value: null, matchMode: FilterMatchMode.EQUALS }
    } as Record<string, { value: any; matchMode: string }>);

    const home = ref({
      icon: 'pi pi-home',
      to: '/'
    });
    const breadcrumbItems = ref([
      { label: 'HRM', to: '/hrm' },
      { label: 'Positions', to: '/hrm/positions' }
    ]);
    
    // Explicitly type the items ref for the breadcrumb

    const getDepartmentName = (id: number | null): string => {
      if (!id) return '';
      const dept = departments.value.find(d => d.id === id);
      return dept ? dept.name : '';
    };

    const loadPositions = async () => {
      loading.value = true;
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
      try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Mock data - replace with actual API call
        const mockData = [
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
        ];
        
        // Add department names to positions
        positions.value = mockData.map(pos => ({
          ...pos,
          department: getDepartmentName(pos.departmentId)
        }));
      } catch (error) {
        console.error('Error loading positions:', error);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to load positions',
          life: 3000
        });
      } finally {
        loading.value = false;
      }
    };

    const showNewPositionDialog = () => {
      position.value = {
        id: null,
        employeeId: '',
        name: '',
        email: '',
        phone: '',
        departmentId: null,
        position: '',
        hireDate: new Date(),
        status: 'Active',
        avatar: null,
        department: ''
      };
      submitted.value = false;
      editing.value = false;
      positionDialog.value = true;
    };

    const editPosition = (pos: Position) => {
      position.value = { ...pos };
      editing.value = true;
      positionDialog.value = true;
    };

    const hideDialog = () => {
      positionDialog.value = false;
      submitted.value = false;
    };

    const savePosition = () => {
      submitted.value = true;
      
      if (position.value.name && position.value.email) {
        submitting.value = true;
        
        // Simulate API call
        setTimeout(() => {
          if (editing.value) {
            const index = positions.value.findIndex(p => p.id === position.value.id);
            if (index !== -1) {
              positions.value[index] = { 
                ...position.value,
                department: getDepartmentName(position.value.departmentId)
              };
            }
            toast.add({
              severity: 'success',
              summary: 'Success',
              detail: 'Position Updated',
              life: 3000
            });
          } else {
            const newPosition: Position = {
              ...position.value,
              id: positions.value.length + 1,
              department: getDepartmentName(position.value.departmentId) || ''
            };
            positions.value.push(newPosition);
            toast.add({
              severity: 'success',
              summary: 'Success',
              detail: 'Position Created',
              life: 3000
            });
          }
          
          positionDialog.value = false;
          position.value = {
            id: null,
            employeeId: '',
            name: '',
            email: '',
            phone: '',
            departmentId: null,
            position: '',
            hireDate: new Date(),
            status: 'Active',
            avatar: null,
            department: ''
          };
          submitted.value = false;
          submitting.value = false;
        }, 1000);
      }
    };

    const confirmDeletePosition = (pos: Position) => {
      position.value = { ...pos };
      deletePositionDialog.value = true;
    };

    const deletePosition = () => {
      if (position.value.id !== null) {
        positions.value = positions.value.filter(pos => pos.id !== position.value.id);
        deletePositionDialog.value = false;
        
        // Reset the position form
        position.value = {
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
        
        toast.add({
          severity: 'success',
          summary: 'Successful',
          detail: 'Position Deleted',
          life: 3000
        });
      }
    };

    const exportToCSV = () => {
      try {
        const worksheet = XLSX.utils.json_to_sheet(positions.value);
        const workbook = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(workbook, worksheet, 'Positions');
        
        // Generate XLSX file and trigger download
        XLSX.writeFile(workbook, 'positions.xlsx', { bookType: 'xlsx', type: 'file' });
      } catch (error) {
        console.error('Error exporting to Excel:', error);
        toast.add({
          severity: 'error',
          summary: 'Export Failed',
          detail: 'Failed to export positions data',
          life: 3000
        });
      }
    };

    const formatDate = (date: Date | string | null | undefined): string => {
      if (!date) return '';
      const dateObj = typeof date === 'string' ? new Date(date) : date;
      return dateObj.toLocaleDateString();
    };

    const getStatusSeverity = (status: string | null | undefined): string => {
      if (!status) return 'info';
      const statusLower = status.toLowerCase();
      switch (statusLower) {
        case 'active':
          return 'success';
        case 'on leave':
          return 'warning';
        case 'inactive':
          return 'info';
        case 'terminated':
          return 'danger';
        default:
          return 'info';
      }
    };

    onMounted(() => {
      loadPositions();
    });

    return {
      // Refs
      home,
      breadcrumbItems,
      
      // State
      positions,
      loading,
      positionDialog,
      deletePositionDialog,
      position,
      departments,
      statuses,
      filters,
      submitting,
      submitted,
      editing,
      
      // Constants
      FilterMatchMode,
      
      // Methods
      loadPositions,
      showNewPositionDialog,
      editPosition,
      hideDialog,
      savePosition,
      confirmDeletePosition,
      deletePosition,
      exportToCSV,
      formatDate,
      getStatusSeverity,
      getDepartmentName
    };
  }
});
</script>

<style lang="scss" scoped>
.hrm-positions {
  padding: 1.5rem;
  
  .p-card {
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    margin-bottom: 1.5rem;
    
    .p-card-header {
      border-bottom: 1px solid var(--surface-100);
      padding: 1.25rem 1.5rem;
      
      h3 {
        margin: 0;
        font-size: 1.25rem;
      }
    }
    
    .p-card-content {
      padding: 1.5rem;
    }
  }
  
  .p-datatable {
    .p-datatable-thead > tr > th {
      background-color: var(--surface-50);
      font-weight: 600;
      text-transform: uppercase;
      font-size: 0.75rem;
      letter-spacing: 0.5px;
      border: none;
    }
    
    .p-datatable-tbody > tr {
      transition: background-color 0.2s;
      
      &:hover {
        background-color: var(--surface-50) !important;
      }
      
      > td {
        padding: 0.5rem 1rem;
      }
    }
    
    .action-buttons {
      .p-button {
        margin-right: 0.5rem;
        
        &:last-child {
          margin-right: 0;
        }
      }
    }
    
    .p-paginator {
      border: none;
      background: transparent;
      padding: 1rem 0 0 0;
    }
  }
  
  .p-inputtext {
    width: 100%;
  }
  
  .p-button {
    min-width: 2.5rem;
    height: 2.5rem;
    
    &.p-button-sm {
      width: 2rem;
      height: 2rem;
    }
  }
  
  .p-tag {
    font-size: 0.75rem;
    font-weight: 600;
    padding: 0.25rem 0.5rem;
    min-width: 6rem;
    text-align: center;
    
    &.status-active {
      background: var(--green-100);
      color: var(--green-700);
    }
    
    &.status-inactive {
      background: var(--red-100);
      color: var(--red-700);
    }
  }
}

:deep(.p-dialog) {
  .p-dialog-header {
    padding: 1.5rem 1.5rem 0.5rem;
  }
  
  .p-dialog-content {
    padding: 1.5rem;
  }

  .p-dialog-footer {
    padding: 0.5rem 1.5rem 1.5rem;
  }
}

.field {
  margin-bottom: 1.5rem;
}
</style>