<template>
  <div class="appraisals-view">
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1>Performance Appraisals</h1>
        <p class="text-color-secondary">Manage employee performance reviews and evaluations</p>
      </div>
      <Button label="New Appraisal" icon="pi pi-plus" @click="showDialog" />
    </div>

    <Card>
      <template #content>
        <DataTable :value="appraisals" :loading="loading" paginator :rows="10">
          <Column field="employeeName" header="Employee" sortable />
          <Column field="department" header="Department" sortable />
          <Column field="reviewPeriod" header="Review Period" sortable />
          <Column field="reviewer" header="Reviewer" sortable />
          <Column field="overallRating" header="Overall Rating" sortable>
            <template #body="{ data }">
              <Rating :modelValue="data.overallRating" :readonly="true" :cancel="false" />
            </template>
          </Column>
          <Column field="status" header="Status" sortable>
            <template #body="{ data }">
              <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
            </template>
          </Column>
          <Column header="Actions">
            <template #body="{ data }">
              <Button icon="pi pi-eye" class="p-button-text" @click="viewAppraisal(data)" />
              <Button icon="pi pi-pencil" class="p-button-text p-button-warning" @click="editAppraisal(data)" />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <Dialog v-model:visible="dialogVisible" header="Performance Appraisal" :modal="true" :style="{width: '700px'}">
      <div class="grid">
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Employee</label>
            <Dropdown v-model="newAppraisal.employeeId" :options="employees" optionLabel="name" optionValue="id" placeholder="Select Employee" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Reviewer</label>
            <Dropdown v-model="newAppraisal.reviewer" :options="reviewers" placeholder="Select Reviewer" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Review Period</label>
            <InputText v-model="newAppraisal.reviewPeriod" placeholder="e.g., Q4 2023" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Overall Rating</label>
            <Rating v-model="newAppraisal.overallRating" :cancel="false" />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label>Key Achievements</label>
            <Textarea v-model="newAppraisal.achievements" rows="3" class="w-full" />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label>Areas for Improvement</label>
            <Textarea v-model="newAppraisal.improvements" rows="3" class="w-full" />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label>Goals for Next Period</label>
            <Textarea v-model="newAppraisal.goals" rows="3" class="w-full" />
          </div>
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" class="p-button-text" @click="dialogVisible = false" />
        <Button label="Save" @click="saveAppraisal" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';

interface Appraisal {
  id: number;
  employeeName: string;
  department: string;
  reviewPeriod: string;
  reviewer: string;
  overallRating: number;
  status: string;
  achievements: string;
  improvements: string;
  goals: string;
}

const toast = useToast();
const loading = ref(false);
const dialogVisible = ref(false);

const appraisals = ref<Appraisal[]>([]);
const employees = ref([
  { id: 1, name: 'John Doe', department: 'IT' },
  { id: 2, name: 'Jane Smith', department: 'HR' },
  { id: 3, name: 'Mike Johnson', department: 'Finance' }
]);
const reviewers = ref(['Sarah Wilson', 'David Brown', 'Lisa Garcia', 'Tom Anderson']);

const newAppraisal = ref({
  employeeId: null,
  reviewer: '',
  reviewPeriod: '',
  overallRating: 0,
  achievements: '',
  improvements: '',
  goals: ''
});

const showDialog = () => {
  newAppraisal.value = {
    employeeId: null,
    reviewer: '',
    reviewPeriod: '',
    overallRating: 0,
    achievements: '',
    improvements: '',
    goals: ''
  };
  dialogVisible.value = true;
};

const saveAppraisal = () => {
  if (newAppraisal.value.employeeId && newAppraisal.value.reviewer) {
    const employee = employees.value.find(e => e.id === newAppraisal.value.employeeId);
    const appraisal: Appraisal = {
      id: Date.now(),
      employeeName: employee?.name || '',
      department: employee?.department || '',
      reviewPeriod: newAppraisal.value.reviewPeriod,
      reviewer: newAppraisal.value.reviewer,
      overallRating: newAppraisal.value.overallRating,
      status: 'Draft',
      achievements: newAppraisal.value.achievements,
      improvements: newAppraisal.value.improvements,
      goals: newAppraisal.value.goals
    };
    
    appraisals.value.push(appraisal);
    dialogVisible.value = false;
    toast.add({ severity: 'success', summary: 'Success', detail: 'Appraisal created successfully', life: 3000 });
  }
};

const viewAppraisal = (appraisal: Appraisal) => {
  toast.add({ severity: 'info', summary: 'View Appraisal', detail: `Viewing appraisal for ${appraisal.employeeName}`, life: 3000 });
};

const editAppraisal = (appraisal: Appraisal) => {
  toast.add({ severity: 'info', summary: 'Edit Appraisal', detail: `Editing appraisal for ${appraisal.employeeName}`, life: 3000 });
};

const getStatusSeverity = (status: string) => {
  switch (status.toLowerCase()) {
    case 'completed': return 'success';
    case 'in review': return 'info';
    case 'draft': return 'warning';
    case 'overdue': return 'danger';
    default: return 'info';
  }
};

onMounted(async () => {
  loading.value = true;
  try {
    await new Promise(resolve => setTimeout(resolve, 1000));
    appraisals.value = [
      { id: 1, employeeName: 'John Doe', department: 'IT', reviewPeriod: 'Q4 2023', reviewer: 'Sarah Wilson', overallRating: 4, status: 'Completed', achievements: 'Led successful project delivery', improvements: 'Communication skills', goals: 'Team leadership development' },
      { id: 2, employeeName: 'Jane Smith', department: 'HR', reviewPeriod: 'Q4 2023', reviewer: 'David Brown', overallRating: 5, status: 'Completed', achievements: 'Improved employee satisfaction', improvements: 'Technical skills', goals: 'HR analytics certification' },
      { id: 3, employeeName: 'Mike Johnson', department: 'Finance', reviewPeriod: 'Q1 2024', reviewer: 'Lisa Garcia', overallRating: 3, status: 'In Review', achievements: 'Cost reduction initiatives', improvements: 'Time management', goals: 'Process automation' }
    ];
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.appraisals-view {
  padding: 0;
}

.field {
  margin-bottom: 1rem;
}
</style>