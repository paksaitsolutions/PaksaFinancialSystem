<template>
  <div class="onboarding-view">
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1>Employee Onboarding</h1>
        <p class="text-color-secondary">Manage new employee onboarding process</p>
      </div>
      <Button label="Start Onboarding" icon="pi pi-user-plus" @click="showDialog" />
    </div>

    <Card>
      <template #content>
        <DataTable :value="onboardingList" :loading="loading" paginator :rows="10">
          <Column field="employeeName" header="Employee" sortable />
          <Column field="position" header="Position" sortable />
          <Column field="department" header="Department" sortable />
          <Column field="startDate" header="Start Date" sortable />
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
              <Button icon="pi pi-eye" class="p-button-text" @click="viewOnboarding(data)" />
              <Button icon="pi pi-check" class="p-button-text p-button-success" @click="updateProgress(data)" />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <Dialog v-model:visible="dialogVisible" header="Start Onboarding" :modal="true" :style="{width: '600px'}">
      <div class="grid">
        <div class="col-12">
          <div class="field">
            <label>Employee Name</label>
            <InputText v-model="newOnboarding.employeeName" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Position</label>
            <InputText v-model="newOnboarding.position" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Department</label>
            <Dropdown v-model="newOnboarding.department" :options="departments" placeholder="Select Department" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Start Date</label>
            <Calendar v-model="newOnboarding.startDate" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Buddy/Mentor</label>
            <Dropdown v-model="newOnboarding.buddy" :options="buddies" placeholder="Select Buddy" class="w-full" />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label>Onboarding Checklist</label>
            <div class="flex flex-column gap-2">
              <div v-for="item in checklistItems" :key="item.id" class="flex align-items-center">
                <Checkbox v-model="newOnboarding.checklist" :inputId="item.id" :value="item.id" />
                <label :for="item.id" class="ml-2">{{ item.label }}</label>
              </div>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" class="p-button-text" @click="dialogVisible = false" />
        <Button label="Start Onboarding" @click="saveOnboarding" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';

interface OnboardingItem {
  id: number;
  employeeName: string;
  position: string;
  department: string;
  startDate: string;
  progress: number;
  status: string;
  buddy: string;
  checklist: string[];
}

const toast = useToast();
const loading = ref(false);
const dialogVisible = ref(false);

const onboardingList = ref<OnboardingItem[]>([]);
const departments = ref(['IT', 'HR', 'Finance', 'Sales', 'Marketing', 'Operations']);
const buddies = ref(['John Doe', 'Jane Smith', 'Mike Johnson', 'Sarah Wilson']);

const checklistItems = ref([
  { id: 'workspace', label: 'Set up workspace' },
  { id: 'equipment', label: 'Provide equipment' },
  { id: 'accounts', label: 'Create system accounts' },
  { id: 'orientation', label: 'Company orientation' },
  { id: 'training', label: 'Role-specific training' },
  { id: 'documentation', label: 'Complete documentation' }
]);

const newOnboarding = ref({
  employeeName: '',
  position: '',
  department: '',
  startDate: null,
  buddy: '',
  checklist: []
});

const showDialog = () => {
  newOnboarding.value = {
    employeeName: '',
    position: '',
    department: '',
    startDate: null,
    buddy: '',
    checklist: []
  };
  dialogVisible.value = true;
};

const saveOnboarding = () => {
  if (newOnboarding.value.employeeName && newOnboarding.value.position) {
    const onboarding: OnboardingItem = {
      id: Date.now(),
      employeeName: newOnboarding.value.employeeName,
      position: newOnboarding.value.position,
      department: newOnboarding.value.department,
      startDate: newOnboarding.value.startDate ? new Date(newOnboarding.value.startDate).toLocaleDateString() : '',
      progress: 0,
      status: 'In Progress',
      buddy: newOnboarding.value.buddy,
      checklist: newOnboarding.value.checklist
    };
    
    onboardingList.value.push(onboarding);
    dialogVisible.value = false;
    toast.add({ severity: 'success', summary: 'Success', detail: 'Onboarding process started', life: 3000 });
  }
};

const viewOnboarding = (onboarding: OnboardingItem) => {
  toast.add({ severity: 'info', summary: 'View Onboarding', detail: `Viewing onboarding for ${onboarding.employeeName}`, life: 3000 });
};

const updateProgress = (onboarding: OnboardingItem) => {
  onboarding.progress = Math.min(onboarding.progress + 20, 100);
  if (onboarding.progress === 100) {
    onboarding.status = 'Completed';
  }
  toast.add({ severity: 'success', summary: 'Progress Updated', detail: `Progress updated for ${onboarding.employeeName}`, life: 3000 });
};

const getStatusSeverity = (status: string) => {
  switch (status.toLowerCase()) {
    case 'completed': return 'success';
    case 'in progress': return 'info';
    case 'pending': return 'warning';
    case 'delayed': return 'danger';
    default: return 'info';
  }
};

onMounted(async () => {
  loading.value = true;
  try {
    await new Promise(resolve => setTimeout(resolve, 1000));
    onboardingList.value = [
      { id: 1, employeeName: 'Alice Johnson', position: 'Software Engineer', department: 'IT', startDate: '2024-01-22', progress: 60, status: 'In Progress', buddy: 'John Doe', checklist: ['workspace', 'equipment', 'accounts'] },
      { id: 2, employeeName: 'Bob Smith', position: 'HR Coordinator', department: 'HR', startDate: '2024-01-15', progress: 100, status: 'Completed', buddy: 'Jane Smith', checklist: ['workspace', 'equipment', 'accounts', 'orientation', 'training', 'documentation'] },
      { id: 3, employeeName: 'Carol Davis', position: 'Marketing Specialist', department: 'Marketing', startDate: '2024-01-25', progress: 20, status: 'In Progress', buddy: 'Sarah Wilson', checklist: ['workspace'] }
    ];
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.onboarding-view {
  padding: 0;
}

.field {
  margin-bottom: 1rem;
}
</style>