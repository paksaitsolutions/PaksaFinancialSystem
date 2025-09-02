<template>
  <div class="departments-view">
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="text-3xl font-bold mb-2">Departments</h1>
        <Breadcrumb :home="home" :model="items" class="mb-4" />
      </div>
      <Button 
        label="Add Department" 
        icon="pi pi-plus" 
        @click="showAddDepartmentDialog" 
        class="p-button-primary"
      />
    </div>

    <Card>
      <template #title>
        <div class="flex justify-content-between align-items-center">
          <span>Department List</span>
          <span class="p-input-icon-left">
            <i class="pi pi-search" />
            <InputText v-model="filters['global'].value" placeholder="Search departments..." />
          </span>
        </div>
      </template>
      <template #content>
        <DataTable 
          :value="departments" 
          :paginator="true" 
          :rows="10"
          :rowsPerPageOptions="[5,10,25,50]"
          :loading="loading"
          :filters="filters"
          :globalFilterFields="['name', 'code', 'manager.name']"
          class="p-datatable-sm"
          scrollable
        >
          <Column field="code" header="Code" :sortable="true">
            <template #body="{ data }">
              <span class="font-semibold">{{ data.code }}</span>
            </template>
          </Column>
          <Column field="name" header="Name" :sortable="true"></Column>
          <Column field="manager.name" header="Manager" :sortable="true">
            <template #body="{ data }">
              <div v-if="data.manager" class="flex align-items-center">
                <Avatar 
                  :image="data.manager?.avatar || 'https://www.primefaces.org/cdn/primevue/images/avatar/annafali.png'" 
                  :label="data.manager?.name?.charAt(0) || '?'" 
                  shape="circle" 
                  class="mr-2" 
                  size="normal"
                />
                <span>{{ data.manager.name }}</span>
              </div>
              <span v-else class="text-500">Not assigned</span>
            </template>
          </Column>
          <Column field="employeeCount" header="Employees" :sortable="true" class="text-center">
            <template #body="{ data }">
              <Tag :value="data.employeeCount" class="p-tag-rounded" />
            </template>
          </Column>
          <Column header="Status" :sortable="true" sortField="active">
            <template #body="{ data }">
              <Tag 
                :value="data.active ? 'Active' : 'Inactive'" 
                :severity="data.active ? 'success' : 'danger'"
                class="p-tag-rounded"
              />
            </template>
          </Column>
          <Column header="Actions" style="width: 10rem">
            <template #body="{ data }">
              <div class="flex gap-1">
                <Button 
                  icon="pi pi-pencil" 
                  class="p-button-text p-button-rounded p-button-sm"
                  @click="editDepartment(data)"
                />
                <Button 
                  icon="pi pi-trash" 
                  class="p-button-text p-button-rounded p-button-sm p-button-danger"
                  @click="confirmDeleteDepartment(data)"
                />
              </div>
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <!-- Add/Edit Department Dialog -->
    <Dialog 
      v-model:visible="departmentDialog" 
      :header="editingDepartment ? 'Edit Department' : 'Add Department'"
      :modal="true"
      :style="{ width: '500px' }"
    >
      <div class="p-fluid">
        <div class="field">
          <label for="code">Department Code *</label>
          <InputText 
            id="code" 
            :modelValue="department.code"
            @update:modelValue="(val) => department.code = val"
            required="true" 
            :class="{ 'p-invalid': submitted && !department.code }"
          />
          <small class="p-error" v-if="submitted && !department.code">Code is required.</small>
        </div>
        <div class="field">
          <label for="name">Department Name *</label>
          <InputText 
            id="name" 
            :modelValue="department.name"
            @update:modelValue="(val) => department.name = val"
            required="true" 
            :class="{ 'p-invalid': submitted && !department.name }"
          />
          <small class="p-error" v-if="submitted && !department.name">Name is required.</small>
        </div>
        <div class="field">
          <label for="manager">Department Head</label>
          <Dropdown 
            v-model="department.managerId"
            :options="managers"
            optionLabel="name"
            optionValue="id"
            placeholder="Select a manager"
            :filter="true"
            :filterFields="['name']"
          >
            <template #value="slotProps">
              <div v-if="slotProps.value" class="flex align-items-center">
                <Avatar 
                  :image="getManagerById(slotProps.value)?.avatar" 
                  :label="getManagerById(slotProps.value)?.name?.charAt(0) || '?'" 
                  shape="circle" 
                  class="mr-2" 
                  size="normal"
                />
                <div>{{ getManagerById(slotProps.value)?.name || 'Select a manager' }}</div>
              </div>
              <span v-else>
                {{ slotProps.placeholder }}
              </span>
            </template>
            <template #option="slotProps">
              <div class="flex align-items-center">
                <Avatar 
                  :image="slotProps.option.avatar" 
                  :label="slotProps.option.name?.charAt(0) || '?'" 
                  shape="circle" 
                  class="mr-2" 
                  size="normal"
                />
                <div>{{ slotProps.option.name }}</div>
              </div>
            </template>
          </Dropdown>
        </div>
        <div class="field-checkbox">
          <Checkbox 
            v-model="department.active" 
            :binary="true" 
            inputId="active"
          />
          <label for="active">Active</label>
        </div>
      </div>
      <template #footer>
        <Button 
          label="Cancel" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="hideDialog"
        />
        <Button 
          label="Save" 
          icon="pi pi-check" 
          class="p-button-text" 
          @click="saveDepartment" 
          :loading="saving"
        />
      </template>
    </Dialog>

    <!-- Delete Confirmation Dialog -->
    <Dialog 
      v-model:visible="deleteDepartmentDialog" 
      header="Confirm" 
      :modal="true"
      :style="{ width: '450px' }"
    >
      <div class="flex align-items-center justify-content-center">
        <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
        <span v-if="department">
          Are you sure you want to delete <b>{{ department.name }}</b>?
        </span>
      </div>
      <template #footer>
        <Button 
          label="No" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="deleteDepartmentDialog = false"
        />
        <Button 
          label="Yes" 
          icon="pi pi-check" 
          class="p-button-text" 
          @click="deleteDepartment" 
          :loading="deleting"
        />
      </template>
    </Dialog>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import { useToast } from 'primevue/usetoast';

export default defineComponent({
  name: 'DepartmentsView',
  setup() {
    const toast = useToast();
    const loading = ref(false);
    const saving = ref(false);
    const deleting = ref(false);
    const submitted = ref(false);
    const departmentDialog = ref(false);
    const deleteDepartmentDialog = ref(false);
    
    const departments = ref([
      { 
        id: 1, 
        code: 'HR', 
        name: 'Human Resources', 
        managerId: 1, 
        employeeCount: 12, 
        active: true,
        manager: { id: 1, name: 'Sarah Johnson', avatar: 'https://www.primefaces.org/cdn/primevue/images/avatar/sarah.png' }
      },
      { 
        id: 2, 
        code: 'IT', 
        name: 'Information Technology', 
        managerId: 2, 
        employeeCount: 8, 
        active: true,
        manager: { id: 2, name: 'Michael Chen', avatar: 'https://www.primefaces.org/cdn/primevue/images/avatar/michael.png' }
      },
      { 
        id: 3, 
        code: 'FIN', 
        name: 'Finance', 
        managerId: 3, 
        employeeCount: 5, 
        active: true,
        manager: { id: 3, name: 'Robert Wilson', avatar: 'https://www.primefaces.org/cdn/primevue/images/avatar/robert.png' }
      },
      { 
        id: 4, 
        code: 'MKT', 
        name: 'Marketing', 
        managerId: null, 
        employeeCount: 0, 
        active: false,
        manager: null
      },
      { 
        id: 5, 
        code: 'OPS', 
        name: 'Operations', 
        managerId: 4, 
        employeeCount: 15, 
        active: true,
        manager: { id: 4, name: 'Emily Davis', avatar: 'https://www.primefaces.org/cdn/primevue/images/avatar/emily.png' }
      },
    ]);

    const managers = ref([
      { id: 1, name: 'Sarah Johnson', avatar: 'https://www.primefaces.org/cdn/primevue/images/avatar/sarah.png' },
      { id: 2, name: 'Michael Chen', avatar: 'https://www.primefaces.org/cdn/primevue/images/avatar/michael.png' },
      { id: 3, name: 'Robert Wilson', avatar: 'https://www.primefaces.org/cdn/primevue/images/avatar/robert.png' },
      { id: 4, name: 'Emily Davis', avatar: 'https://www.primefaces.org/cdn/primevue/images/avatar/emily.png' },
      { id: 5, name: 'David Kim', avatar: 'https://www.primefaces.org/cdn/primevue/images/avatar/david.png' },
    ]);

    const emptyDepartment = {
      id: null,
      code: '',
      name: '',
      managerId: null,
      active: true,
      manager: null,
      employeeCount: 0
    };

    interface DepartmentBase {
      id: number;
      code: string;
      name: string;
      managerId: number | null;
      employeeCount: number;
      active: boolean;
    }

    interface DepartmentWithManager extends DepartmentBase {
      managerId: number;
      manager: {
        id: number;
        name: string;
        avatar: string;
      };
    }

    interface DepartmentWithoutManager extends DepartmentBase {
      managerId: null;
      manager: null;
    }

    type Department = DepartmentWithManager | DepartmentWithoutManager;

    interface Manager {
      id: number;
      name: string;
      avatar: string;
    }

    const department = ref({
      id: null as number | null,
      code: '',
      name: '',
      managerId: null as number | null,
      manager: null as { id: number; name: string; avatar: string } | null,
      active: true,
      employeeCount: 0
    });
    const editingDepartment = ref(false);
    
    const filters = ref({
      global: { value: '', matchMode: 'contains' as const },
    });

    const home = ref({ icon: 'pi pi-home', to: { name: 'Dashboard' } });
    const items = ref([
      { label: 'HRM', to: { name: 'HRM' } },
      { label: 'Departments' }
    ]);

    const getManagerById = (id: number | null): Manager | null => {
      return managers.value.find(m => m.id === id) || null;
    };

    const showAddDepartmentDialog = () => {
      department.value = {
        id: null,
        code: '',
        name: '',
        managerId: null,
        manager: null,
        active: true,
        employeeCount: 0
      };
      submitted.value = false;
      editingDepartment.value = false;
      departmentDialog.value = true;
    };

    const editDepartment = (dept: Department) => {
      department.value = {
        id: dept.id,
        code: dept.code,
        name: dept.name,
        managerId: dept.managerId,
        manager: dept.manager,
        active: dept.active,
        employeeCount: dept.employeeCount
      };
      editingDepartment.value = true;
      departmentDialog.value = true;
    };

    const hideDialog = () => {
      departmentDialog.value = false;
      submitted.value = false;
    };

    const saveDepartment = () => {
      submitted.value = true;
      
      if (department.value.name && department.value.code) {
        saving.value = true;
        
        // Simulate API call
        setTimeout(() => {
          if (editingDepartment.value && department.value.id) {
            // Update existing department
            const index = departments.value.findIndex(d => d.id === department.value.id);
            if (index !== -1) {
              const manager = department.value.managerId ? getManagerById(department.value.managerId) : null;
              const currentDept = departments.value[index];
              if (!currentDept) return;
              
              // Create updated department with proper types
              const updatedDept = {
                id: department.value.id,
                code: department.value.code,
                name: department.value.name,
                managerId: manager?.id || null,
                manager: manager,
                employeeCount: currentDept.employeeCount,
                active: department.value.active
              };
              
              // Create a new array to trigger reactivity
              const updatedDepartments = [...departments.value];
              updatedDepartments[index] = updatedDept as Department;
              departments.value = updatedDepartments as Department[];
              
              toast.add({
                severity: 'success',
                summary: 'Success',
                detail: 'Department updated',
                life: 3000
              });
            }
          } else {
            // Add new department
            const newId = Math.max(0, ...departments.value.map(d => d.id), 0) + 1;
            const manager = department.value.managerId ? getManagerById(department.value.managerId) : null;
            
            // Create new department with proper types
            const newDept: Department = manager ? {
              id: newId,
              code: department.value.code,
              name: department.value.name,
              managerId: manager.id,
              manager: manager,
              employeeCount: 0,
              active: department.value.active
            } : {
              id: newId,
              code: department.value.code,
              name: department.value.name,
              managerId: null,
              manager: null,
              employeeCount: 0,
              active: department.value.active
            };
            
            // Create a new array to trigger reactivity
            departments.value = [...departments.value, newDept];
            
            toast.add({
              severity: 'success',
              summary: 'Success',
              detail: 'Department created',
              life: 3000
            });
          }
          
          departmentDialog.value = false;
          saving.value = false;
          department.value = {
            id: null,
            code: '',
            name: '',
            managerId: null,
            manager: null,
            active: true,
            employeeCount: 0
          };
        }, 300);
      }
    };

    const confirmDeleteDepartment = (dept: Department) => {
      department.value = {
        id: dept.id,
        code: dept.code,
        name: dept.name,
        managerId: dept.managerId,
        manager: dept.manager,
        active: dept.active,
        employeeCount: dept.employeeCount
      };
      deleteDepartmentDialog.value = true;
    };

    const deleteDepartment = () => {
      if (!department.value.id) return;
      
      deleting.value = true;
      
      // Simulate API call
      setTimeout(() => {
        departments.value = departments.value.filter(d => d.id !== department.value.id);
        deleteDepartmentDialog.value = false;
        department.value = {
          id: null,
          code: '',
          name: '',
          managerId: null,
          manager: null,
          active: true,
          employeeCount: 0
        };
        deleting.value = false;
        
        toast.add({
          severity: 'success',
          summary: 'Success',
          detail: 'Department deleted',
          life: 3000
        });
      }, 300);
    };

    return {
      departments,
      department,
      managers,
      filters,
      loading,
      saving,
      deleting,
      submitted,
      departmentDialog,
      deleteDepartmentDialog,
      editingDepartment,
      home,
      items,
      showAddDepartmentDialog,
      editDepartment,
      hideDialog,
      saveDepartment,
      confirmDeleteDepartment,
      deleteDepartment,
      getManagerById
    };
  }
});
</script>

<style scoped>
.departments-view {
  padding: 1rem;
}

:deep(.p-datatable .p-datatable-thead > tr > th) {
  background: var(--surface-50);
  font-weight: 600;
}

:deep(.p-datatable .p-datatable-tbody > tr > td) {
  padding: 0.75rem 1rem;
}

:deep(.p-datatable .p-datatable-tbody > tr > td .p-button) {
  width: 2rem;
  height: 2rem;
}

:deep(.p-datatable .p-datatable-tbody > tr > td .p-button.p-button-sm) {
  width: 1.75rem;
  height: 1.75rem;
}

:deep(.p-datatable .p-datatable-tbody > tr > td .p-button + .p-button) {
  margin-left: 0.25rem;
}
</style>
