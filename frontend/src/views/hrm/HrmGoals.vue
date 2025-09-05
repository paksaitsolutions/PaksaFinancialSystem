<template>
  <div class="goals-view">
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1>Goals & Objectives</h1>
        <p class="text-color-secondary">Track employee goals and performance objectives</p>
      </div>
      <Button label="Set New Goal" icon="pi pi-plus" @click="showDialog" />
    </div>

    <Card>
      <template #content>
        <DataTable :value="goals" :loading="loading" paginator :rows="10">
          <Column field="employeeName" header="Employee" sortable />
          <Column field="title" header="Goal Title" sortable />
          <Column field="category" header="Category" sortable />
          <Column field="targetDate" header="Target Date" sortable />
          <Column field="progress" header="Progress" sortable>
            <template #body="{ data }">
              <ProgressBar :value="data.progress" :showValue="true" />
            </template>
          </Column>
          <Column field="status" header="Status" sortable>
            <template #body="{ data }">
              <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
            </template>
          </Column>
          <Column header="Actions">
            <template #body="{ data }">
              <Button icon="pi pi-eye" class="p-button-text" @click="viewGoal(data)" />
              <Button icon="pi pi-arrow-up" class="p-button-text p-button-success" @click="updateProgress(data)" />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <Dialog v-model:visible="dialogVisible" header="Set Goal" :modal="true" :style="{width: '600px'}">
      <div class="grid">
        <div class="col-12">
          <div class="field">
            <label>Employee</label>
            <Dropdown v-model="newGoal.employeeId" :options="employees" optionLabel="name" optionValue="id" placeholder="Select Employee" class="w-full" />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label>Goal Title</label>
            <InputText v-model="newGoal.title" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Category</label>
            <Dropdown v-model="newGoal.category" :options="categories" placeholder="Select Category" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Target Date</label>
            <Calendar v-model="newGoal.targetDate" class="w-full" />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label>Description</label>
            <Textarea v-model="newGoal.description" rows="3" class="w-full" />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label>Success Criteria</label>
            <Textarea v-model="newGoal.successCriteria" rows="3" class="w-full" />
          </div>
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" class="p-button-text" @click="dialogVisible = false" />
        <Button label="Set Goal" @click="saveGoal" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';

interface Goal {
  id: number;
  employeeName: string;
  title: string;
  category: string;
  targetDate: string;
  progress: number;
  status: string;
  description: string;
  successCriteria: string;
}

const toast = useToast();
const loading = ref(false);
const dialogVisible = ref(false);

const goals = ref<Goal[]>([]);
const employees = ref([
  { id: 1, name: 'John Doe' },
  { id: 2, name: 'Jane Smith' },
  { id: 3, name: 'Mike Johnson' },
  { id: 4, name: 'Sarah Wilson' }
]);
const categories = ref(['Performance', 'Skill Development', 'Leadership', 'Innovation', 'Customer Service', 'Sales']);

const newGoal = ref({
  employeeId: null,
  title: '',
  category: '',
  targetDate: null,
  description: '',
  successCriteria: ''
});

const showDialog = () => {
  newGoal.value = {
    employeeId: null,
    title: '',
    category: '',
    targetDate: null,
    description: '',
    successCriteria: ''
  };
  dialogVisible.value = true;
};

const saveGoal = () => {
  if (newGoal.value.employeeId && newGoal.value.title) {
    const employee = employees.value.find(e => e.id === newGoal.value.employeeId);
    const goal: Goal = {
      id: Date.now(),
      employeeName: employee?.name || '',
      title: newGoal.value.title,
      category: newGoal.value.category,
      targetDate: newGoal.value.targetDate ? new Date(newGoal.value.targetDate).toLocaleDateString() : '',
      progress: 0,
      status: 'In Progress',
      description: newGoal.value.description,
      successCriteria: newGoal.value.successCriteria
    };
    
    goals.value.push(goal);
    dialogVisible.value = false;
    toast.add({ severity: 'success', summary: 'Success', detail: 'Goal set successfully', life: 3000 });
  }
};

const viewGoal = (goal: Goal) => {
  toast.add({ severity: 'info', summary: 'View Goal', detail: `Viewing goal: ${goal.title}`, life: 3000 });
};

const updateProgress = (goal: Goal) => {
  goal.progress = Math.min(goal.progress + 25, 100);
  if (goal.progress === 100) {
    goal.status = 'Completed';
  }
  toast.add({ severity: 'success', summary: 'Progress Updated', detail: `Progress updated for: ${goal.title}`, life: 3000 });
};

const getStatusSeverity = (status: string) => {
  switch (status.toLowerCase()) {
    case 'completed': return 'success';
    case 'in progress': return 'info';
    case 'overdue': return 'danger';
    case 'on hold': return 'warning';
    default: return 'info';
  }
};

onMounted(async () => {
  loading.value = true;
  try {
    await new Promise(resolve => setTimeout(resolve, 1000));
    goals.value = [
      { id: 1, employeeName: 'John Doe', title: 'Complete React Certification', category: 'Skill Development', targetDate: '2024-03-31', progress: 75, status: 'In Progress', description: 'Complete advanced React certification course', successCriteria: 'Pass certification exam with 85% or higher' },
      { id: 2, employeeName: 'Jane Smith', title: 'Improve Team Satisfaction Score', category: 'Leadership', targetDate: '2024-06-30', progress: 50, status: 'In Progress', description: 'Increase team satisfaction from 7.5 to 8.5', successCriteria: 'Achieve 8.5+ in quarterly team survey' },
      { id: 3, employeeName: 'Mike Johnson', title: 'Reduce Processing Time by 20%', category: 'Performance', targetDate: '2024-02-28', progress: 100, status: 'Completed', description: 'Optimize financial reporting processes', successCriteria: 'Reduce monthly close time from 10 to 8 days' }
    ];
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.goals-view {
  padding: 0;
}

.field {
  margin-bottom: 1rem;
}
</style>