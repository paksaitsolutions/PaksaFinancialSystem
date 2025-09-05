<template>
  <div class="departments-view">
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1>Department Management</h1>
        <p class="text-color-secondary">Manage organizational departments and structure</p>
      </div>
      <Button label="Add Department" icon="pi pi-plus" @click="showDialog" />
    </div>

    <Card>
      <template #content>
        <DataTable :value="departments" :loading="loading" paginator :rows="10">
          <Column field="name" header="Department Name" sortable />
          <Column field="code" header="Code" sortable />
          <Column field="manager" header="Manager" sortable />
          <Column field="employeeCount" header="Employees" sortable />
          <Column field="budget" header="Budget" sortable>
            <template #body="{ data }">
              ${{ data.budget.toLocaleString() }}
            </template>
          </Column>
          <Column field="status" header="Status" sortable>
            <template #body="{ data }">
              <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
            </template>
          </Column>
          <Column header="Actions">
            <template #body="{ data }">
              <Button icon="pi pi-pencil" class="p-button-text p-button-warning" @click="editDepartment(data)" />
              <Button icon="pi pi-eye" class="p-button-text" @click="viewDepartment(data)" />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <Dialog v-model:visible="dialogVisible" header="Department Details" :modal="true" :style="{width: '500px'}">
      <div class="field">
        <label>Department Name</label>
        <InputText v-model="newDepartment.name" class="w-full" />
      </div>
      <div class="field">
        <label>Department Code</label>
        <InputText v-model="newDepartment.code" class="w-full" />
      </div>
      <div class="field">
        <label>Manager</label>
        <InputText v-model="newDepartment.manager" class="w-full" />
      </div>
      <div class="field">
        <label>Budget</label>
        <InputNumber v-model="newDepartment.budget" mode="currency" currency="USD" class="w-full" />
      </div>
      <div class="field">
        <label>Description</label>
        <Textarea v-model="newDepartment.description" rows="3" class="w-full" />
      </div>
      <template #footer>
        <Button label="Cancel" class="p-button-text" @click="dialogVisible = false" />
        <Button label="Save" @click="saveDepartment" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';

interface Department {
  id: number;
  name: string;
  code: string;
  manager: string;
  employeeCount: number;
  budget: number;
  status: string;
  description: string;
}

const toast = useToast();
const loading = ref(false);
const dialogVisible = ref(false);

const departments = ref<Department[]>([]);

const newDepartment = ref({
  name: '',
  code: '',
  manager: '',
  budget: 0,
  description: ''
});

const showDialog = () => {
  newDepartment.value = {
    name: '',
    code: '',
    manager: '',
    budget: 0,
    description: ''
  };
  dialogVisible.value = true;
};

const saveDepartment = () => {
  if (newDepartment.value.name && newDepartment.value.code) {
    const department: Department = {
      id: Date.now(),
      name: newDepartment.value.name,
      code: newDepartment.value.code,
      manager: newDepartment.value.manager,
      employeeCount: 0,
      budget: newDepartment.value.budget,
      status: 'Active',
      description: newDepartment.value.description
    };
    
    departments.value.push(department);
    dialogVisible.value = false;
    toast.add({ severity: 'success', summary: 'Success', detail: 'Department created', life: 3000 });
  }
};

const editDepartment = (department: Department) => {
  toast.add({ severity: 'info', summary: 'Edit Department', detail: `Editing ${department.name}`, life: 3000 });
};

const viewDepartment = (department: Department) => {
  toast.add({ severity: 'info', summary: 'View Department', detail: `Viewing ${department.name}`, life: 3000 });
};

const getStatusSeverity = (status: string) => {
  switch (status.toLowerCase()) {
    case 'active': return 'success';
    case 'inactive': return 'danger';
    default: return 'info';
  }
};

onMounted(async () => {
  loading.value = true;
  try {
    await new Promise(resolve => setTimeout(resolve, 1000));
    departments.value = [
      { id: 1, name: 'Information Technology', code: 'IT', manager: 'John Smith', employeeCount: 15, budget: 500000, status: 'Active', description: 'Technology and systems management' },
      { id: 2, name: 'Human Resources', code: 'HR', manager: 'Jane Doe', employeeCount: 8, budget: 200000, status: 'Active', description: 'Employee relations and management' },
      { id: 3, name: 'Finance', code: 'FIN', manager: 'Mike Johnson', employeeCount: 12, budget: 300000, status: 'Active', description: 'Financial planning and accounting' },
      { id: 4, name: 'Sales', code: 'SAL', manager: 'Sarah Wilson', employeeCount: 20, budget: 400000, status: 'Active', description: 'Sales and customer relations' }
    ];
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.departments-view {
  padding: 0;
}

.field {
  margin-bottom: 1rem;
}
</style>