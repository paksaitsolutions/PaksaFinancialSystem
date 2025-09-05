<template>
  <div class="hrm-training">
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1>Training Management</h1>
        <p class="text-color-secondary">Manage employee training programs and certifications</p>
      </div>
      <Button label="New Training Program" icon="pi pi-plus" @click="showDialog" />
    </div>

    <div class="grid">
      <div class="col-12 md:col-6 lg:col-3">
        <Card>
          <template #content>
            <div class="flex align-items-center">
              <div class="flex align-items-center justify-content-center w-3rem h-3rem border-circle bg-blue-100 text-blue-600 mr-3">
                <i class="pi pi-book text-xl"></i>
              </div>
              <div>
                <div class="text-color-secondary text-sm">Active Programs</div>
                <div class="text-2xl font-bold">{{ stats.activePrograms }}</div>
              </div>
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 md:col-6 lg:col-3">
        <Card>
          <template #content>
            <div class="flex align-items-center">
              <div class="flex align-items-center justify-content-center w-3rem h-3rem border-circle bg-green-100 text-green-600 mr-3">
                <i class="pi pi-users text-xl"></i>
              </div>
              <div>
                <div class="text-color-secondary text-sm">Enrolled Employees</div>
                <div class="text-2xl font-bold">{{ stats.enrolledEmployees }}</div>
              </div>
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 md:col-6 lg:col-3">
        <Card>
          <template #content>
            <div class="flex align-items-center">
              <div class="flex align-items-center justify-content-center w-3rem h-3rem border-circle bg-orange-100 text-orange-600 mr-3">
                <i class="pi pi-check-circle text-xl"></i>
              </div>
              <div>
                <div class="text-color-secondary text-sm">Completed</div>
                <div class="text-2xl font-bold">{{ stats.completed }}</div>
              </div>
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 md:col-6 lg:col-3">
        <Card>
          <template #content>
            <div class="flex align-items-center">
              <div class="flex align-items-center justify-content-center w-3rem h-3rem border-circle bg-purple-100 text-purple-600 mr-3">
                <i class="pi pi-percentage text-xl"></i>
              </div>
              <div>
                <div class="text-color-secondary text-sm">Completion Rate</div>
                <div class="text-2xl font-bold">{{ stats.completionRate }}%</div>
              </div>
            </div>
          </template>
        </Card>
      </div>
    </div>

    <Card>
      <template #title>Training Programs</template>
      <template #content>
        <DataTable :value="trainingPrograms" :loading="loading" paginator :rows="10">
          <Column field="title" header="Program Title" sortable />
          <Column field="category" header="Category" sortable />
          <Column field="duration" header="Duration" sortable />
          <Column field="instructor" header="Instructor" sortable />
          <Column field="startDate" header="Start Date" sortable />
          <Column field="status" header="Status" sortable>
            <template #body="{ data }">
              <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
            </template>
          </Column>
          <Column field="enrolled" header="Enrolled" sortable />
          <Column header="Actions">
            <template #body="{ data }">
              <Button icon="pi pi-eye" class="p-button-text" @click="viewProgram(data)" />
              <Button icon="pi pi-pencil" class="p-button-text p-button-warning" @click="editProgram(data)" />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <Dialog v-model:visible="dialogVisible" header="Training Program" :modal="true" :style="{width: '600px'}">
      <div class="grid">
        <div class="col-12">
          <div class="field">
            <label>Program Title</label>
            <InputText v-model="newProgram.title" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Category</label>
            <Dropdown v-model="newProgram.category" :options="categories" placeholder="Select Category" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Duration (hours)</label>
            <InputNumber v-model="newProgram.duration" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Instructor</label>
            <InputText v-model="newProgram.instructor" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Start Date</label>
            <Calendar v-model="newProgram.startDate" class="w-full" />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label>Description</label>
            <Textarea v-model="newProgram.description" rows="3" class="w-full" />
          </div>
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" class="p-button-text" @click="dialogVisible = false" />
        <Button label="Save" @click="saveProgram" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';

interface TrainingProgram {
  id: number;
  title: string;
  category: string;
  duration: number;
  instructor: string;
  startDate: string;
  status: string;
  enrolled: number;
  description: string;
}

const toast = useToast();
const loading = ref(false);
const dialogVisible = ref(false);

const stats = ref({
  activePrograms: 12,
  enrolledEmployees: 85,
  completed: 67,
  completionRate: 79
});

const trainingPrograms = ref<TrainingProgram[]>([]);
const categories = ref(['Technical Skills', 'Soft Skills', 'Leadership', 'Compliance', 'Safety', 'Professional Development']);

const newProgram = ref({
  title: '',
  category: '',
  duration: 0,
  instructor: '',
  startDate: null,
  description: ''
});

const showDialog = () => {
  newProgram.value = {
    title: '',
    category: '',
    duration: 0,
    instructor: '',
    startDate: null,
    description: ''
  };
  dialogVisible.value = true;
};

const saveProgram = () => {
  if (newProgram.value.title && newProgram.value.category) {
    const program: TrainingProgram = {
      id: Date.now(),
      title: newProgram.value.title,
      category: newProgram.value.category,
      duration: newProgram.value.duration,
      instructor: newProgram.value.instructor,
      startDate: newProgram.value.startDate ? new Date(newProgram.value.startDate).toLocaleDateString() : '',
      status: 'Scheduled',
      enrolled: 0,
      description: newProgram.value.description
    };
    
    trainingPrograms.value.push(program);
    dialogVisible.value = false;
    toast.add({ severity: 'success', summary: 'Success', detail: 'Training program created', life: 3000 });
  }
};

const viewProgram = (program: TrainingProgram) => {
  toast.add({ severity: 'info', summary: 'View Program', detail: `Viewing ${program.title}`, life: 3000 });
};

const editProgram = (program: TrainingProgram) => {
  toast.add({ severity: 'info', summary: 'Edit Program', detail: `Editing ${program.title}`, life: 3000 });
};

const getStatusSeverity = (status: string) => {
  switch (status.toLowerCase()) {
    case 'active': return 'success';
    case 'completed': return 'info';
    case 'scheduled': return 'warning';
    case 'cancelled': return 'danger';
    default: return 'info';
  }
};

onMounted(async () => {
  loading.value = true;
  try {
    await new Promise(resolve => setTimeout(resolve, 1000));
    trainingPrograms.value = [
      { id: 1, title: 'Leadership Development', category: 'Leadership', duration: 40, instructor: 'Dr. Smith', startDate: '2024-02-01', status: 'Active', enrolled: 15, description: 'Comprehensive leadership training program' },
      { id: 2, title: 'Technical Skills Workshop', category: 'Technical Skills', duration: 24, instructor: 'John Doe', startDate: '2024-01-15', status: 'Completed', enrolled: 20, description: 'Advanced technical skills development' },
      { id: 3, title: 'Safety Training', category: 'Safety', duration: 8, instructor: 'Jane Wilson', startDate: '2024-02-15', status: 'Scheduled', enrolled: 0, description: 'Workplace safety and compliance training' }
    ];
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.hrm-training {
  padding: 0;
}

.field {
  margin-bottom: 1rem;
}
</style>