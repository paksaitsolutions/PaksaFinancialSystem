<template>
  <div class="hrm-positions">
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1>Position Management</h1>
        <p class="text-color-secondary">Manage job positions and organizational structure</p>
      </div>
      <Button label="Add Position" icon="pi pi-plus" @click="showDialog" />
    </div>

    <Card>
      <template #content>
        <DataTable :value="positions" :loading="loading" paginator :rows="10">
          <Column field="title" header="Position Title" sortable />
          <Column field="department" header="Department" sortable />
          <Column field="level" header="Level" sortable />
          <Column field="minSalary" header="Min Salary" sortable>
            <template #body="{ data }">
              ${{ data.minSalary.toLocaleString() }}
            </template>
          </Column>
          <Column field="maxSalary" header="Max Salary" sortable>
            <template #body="{ data }">
              ${{ data.maxSalary.toLocaleString() }}
            </template>
          </Column>
          <Column field="openings" header="Openings" sortable />
          <Column field="status" header="Status" sortable>
            <template #body="{ data }">
              <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
            </template>
          </Column>
          <Column header="Actions">
            <template #body="{ data }">
              <Button icon="pi pi-pencil" class="p-button-text p-button-warning" @click="editPosition(data)" />
              <Button icon="pi pi-eye" class="p-button-text" @click="viewPosition(data)" />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <Dialog v-model:visible="dialogVisible" header="Position Details" :modal="true" :style="{width: '600px'}">
      <div class="grid">
        <div class="col-12">
          <div class="field">
            <label>Position Title</label>
            <InputText v-model="newPosition.title" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Department</label>
            <Dropdown v-model="newPosition.department" :options="departments" placeholder="Select Department" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Level</label>
            <Dropdown v-model="newPosition.level" :options="levels" placeholder="Select Level" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Minimum Salary</label>
            <InputNumber v-model="newPosition.minSalary" mode="currency" currency="USD" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Maximum Salary</label>
            <InputNumber v-model="newPosition.maxSalary" mode="currency" currency="USD" class="w-full" />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label>Job Description</label>
            <Textarea v-model="newPosition.description" rows="4" class="w-full" />
          </div>
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" class="p-button-text" @click="dialogVisible = false" />
        <Button label="Save" @click="savePosition" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';

interface Position {
  id: number;
  title: string;
  department: string;
  level: string;
  minSalary: number;
  maxSalary: number;
  openings: number;
  status: string;
  description: string;
}

const toast = useToast();
const loading = ref(false);
const dialogVisible = ref(false);

const positions = ref<Position[]>([]);
const departments = ref(['IT', 'HR', 'Finance', 'Sales', 'Marketing', 'Operations']);
const levels = ref(['Entry Level', 'Junior', 'Mid Level', 'Senior', 'Lead', 'Manager', 'Director']);

const newPosition = ref({
  title: '',
  department: '',
  level: '',
  minSalary: 0,
  maxSalary: 0,
  description: ''
});

const showDialog = () => {
  newPosition.value = {
    title: '',
    department: '',
    level: '',
    minSalary: 0,
    maxSalary: 0,
    description: ''
  };
  dialogVisible.value = true;
};

const savePosition = () => {
  if (newPosition.value.title && newPosition.value.department) {
    const position: Position = {
      id: Date.now(),
      title: newPosition.value.title,
      department: newPosition.value.department,
      level: newPosition.value.level,
      minSalary: newPosition.value.minSalary,
      maxSalary: newPosition.value.maxSalary,
      openings: 1,
      status: 'Active',
      description: newPosition.value.description
    };
    
    positions.value.push(position);
    dialogVisible.value = false;
    toast.add({ severity: 'success', summary: 'Success', detail: 'Position created', life: 3000 });
  }
};

const editPosition = (position: Position) => {
  toast.add({ severity: 'info', summary: 'Edit Position', detail: `Editing ${position.title}`, life: 3000 });
};

const viewPosition = (position: Position) => {
  toast.add({ severity: 'info', summary: 'View Position', detail: `Viewing ${position.title}`, life: 3000 });
};

const getStatusSeverity = (status: string) => {
  switch (status.toLowerCase()) {
    case 'active': return 'success';
    case 'inactive': return 'danger';
    case 'draft': return 'warning';
    default: return 'info';
  }
};

onMounted(async () => {
  loading.value = true;
  try {
    await new Promise(resolve => setTimeout(resolve, 1000));
    positions.value = [
      { id: 1, title: 'Software Engineer', department: 'IT', level: 'Mid Level', minSalary: 70000, maxSalary: 90000, openings: 2, status: 'Active', description: 'Develop and maintain software applications' },
      { id: 2, title: 'HR Manager', department: 'HR', level: 'Manager', minSalary: 80000, maxSalary: 100000, openings: 1, status: 'Active', description: 'Manage HR operations and policies' },
      { id: 3, title: 'Financial Analyst', department: 'Finance', level: 'Junior', minSalary: 50000, maxSalary: 65000, openings: 1, status: 'Active', description: 'Analyze financial data and prepare reports' }
    ];
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.hrm-positions {
  padding: 0;
}

.field {
  margin-bottom: 1rem;
}
</style>