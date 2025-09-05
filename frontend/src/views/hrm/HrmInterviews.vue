<template>
  <div class="interviews-view">
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1>Interview Management</h1>
        <p class="text-color-secondary">Schedule and manage candidate interviews</p>
      </div>
      <Button label="Schedule Interview" icon="pi pi-calendar-plus" @click="showDialog" />
    </div>

    <Card>
      <template #content>
        <DataTable :value="interviews" :loading="loading" paginator :rows="10">
          <Column field="candidateName" header="Candidate" sortable />
          <Column field="position" header="Position" sortable />
          <Column field="interviewDate" header="Date" sortable />
          <Column field="interviewTime" header="Time" sortable />
          <Column field="interviewer" header="Interviewer" sortable />
          <Column field="type" header="Type" sortable />
          <Column field="status" header="Status" sortable>
            <template #body="{ data }">
              <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
            </template>
          </Column>
          <Column header="Actions">
            <template #body="{ data }">
              <Button icon="pi pi-eye" class="p-button-text" @click="viewInterview(data)" />
              <Button icon="pi pi-check" class="p-button-text p-button-success" @click="completeInterview(data)" v-if="data.status === 'Scheduled'" />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <Dialog v-model:visible="dialogVisible" header="Schedule Interview" :modal="true" :style="{width: '600px'}">
      <div class="grid">
        <div class="col-12">
          <div class="field">
            <label>Candidate</label>
            <Dropdown v-model="newInterview.candidateId" :options="candidates" optionLabel="name" optionValue="id" placeholder="Select Candidate" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Interview Date</label>
            <Calendar v-model="newInterview.date" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Interview Time</label>
            <Calendar v-model="newInterview.time" timeOnly class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Interviewer</label>
            <Dropdown v-model="newInterview.interviewer" :options="interviewers" placeholder="Select Interviewer" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Interview Type</label>
            <Dropdown v-model="newInterview.type" :options="interviewTypes" placeholder="Select Type" class="w-full" />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label>Notes</label>
            <Textarea v-model="newInterview.notes" rows="3" class="w-full" />
          </div>
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" class="p-button-text" @click="dialogVisible = false" />
        <Button label="Schedule" @click="saveInterview" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';

interface Interview {
  id: number;
  candidateName: string;
  position: string;
  interviewDate: string;
  interviewTime: string;
  interviewer: string;
  type: string;
  status: string;
  notes: string;
}

const toast = useToast();
const loading = ref(false);
const dialogVisible = ref(false);

const interviews = ref<Interview[]>([]);
const candidates = ref([
  { id: 1, name: 'Alice Johnson - Software Engineer' },
  { id: 2, name: 'Bob Smith - HR Manager' },
  { id: 3, name: 'Carol Davis - Financial Analyst' }
]);
const interviewers = ref(['John Doe', 'Jane Smith', 'Mike Johnson', 'Sarah Wilson']);
const interviewTypes = ref(['Phone Screen', 'Technical Interview', 'Behavioral Interview', 'Final Interview']);

const newInterview = ref({
  candidateId: null,
  date: null,
  time: null,
  interviewer: '',
  type: '',
  notes: ''
});

const showDialog = () => {
  newInterview.value = {
    candidateId: null,
    date: null,
    time: null,
    interviewer: '',
    type: '',
    notes: ''
  };
  dialogVisible.value = true;
};

const saveInterview = () => {
  if (newInterview.value.candidateId && newInterview.value.date) {
    const candidate = candidates.value.find(c => c.id === newInterview.value.candidateId);
    const interview: Interview = {
      id: Date.now(),
      candidateName: candidate?.name.split(' - ')[0] || '',
      position: candidate?.name.split(' - ')[1] || '',
      interviewDate: new Date(newInterview.value.date).toLocaleDateString(),
      interviewTime: newInterview.value.time ? new Date(newInterview.value.time).toLocaleTimeString() : '',
      interviewer: newInterview.value.interviewer,
      type: newInterview.value.type,
      status: 'Scheduled',
      notes: newInterview.value.notes
    };
    
    interviews.value.push(interview);
    dialogVisible.value = false;
    toast.add({ severity: 'success', summary: 'Success', detail: 'Interview scheduled successfully', life: 3000 });
  }
};

const viewInterview = (interview: Interview) => {
  toast.add({ severity: 'info', summary: 'View Interview', detail: `Viewing interview for ${interview.candidateName}`, life: 3000 });
};

const completeInterview = (interview: Interview) => {
  interview.status = 'Completed';
  toast.add({ severity: 'success', summary: 'Interview Completed', detail: `Interview marked as completed for ${interview.candidateName}`, life: 3000 });
};

const getStatusSeverity = (status: string) => {
  switch (status.toLowerCase()) {
    case 'completed': return 'success';
    case 'scheduled': return 'info';
    case 'cancelled': return 'danger';
    case 'rescheduled': return 'warning';
    default: return 'info';
  }
};

onMounted(async () => {
  loading.value = true;
  try {
    await new Promise(resolve => setTimeout(resolve, 1000));
    interviews.value = [
      { id: 1, candidateName: 'Alice Johnson', position: 'Software Engineer', interviewDate: '2024-01-20', interviewTime: '10:00 AM', interviewer: 'John Doe', type: 'Technical Interview', status: 'Scheduled', notes: 'Focus on JavaScript and React' },
      { id: 2, candidateName: 'Bob Smith', position: 'HR Manager', interviewDate: '2024-01-18', interviewTime: '2:00 PM', interviewer: 'Jane Smith', type: 'Behavioral Interview', status: 'Completed', notes: 'Good communication skills' },
      { id: 3, candidateName: 'Carol Davis', position: 'Financial Analyst', interviewDate: '2024-01-22', interviewTime: '11:00 AM', interviewer: 'Mike Johnson', type: 'Final Interview', status: 'Scheduled', notes: 'Review financial modeling experience' }
    ];
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.interviews-view {
  padding: 0;
}

.field {
  margin-bottom: 1rem;
}
</style>