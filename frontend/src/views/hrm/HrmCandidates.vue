<template>
  <div class="candidates-view">
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1>Candidate Management</h1>
        <p class="text-color-secondary">Manage job candidates and recruitment pipeline</p>
      </div>
      <Button label="Add Candidate" icon="pi pi-plus" @click="showDialog" />
    </div>

    <Card>
      <template #content>
        <DataTable :value="candidates" :loading="loading" paginator :rows="10">
          <Column field="name" header="Candidate Name" sortable />
          <Column field="position" header="Applied Position" sortable />
          <Column field="email" header="Email" sortable />
          <Column field="phone" header="Phone" sortable />
          <Column field="appliedDate" header="Applied Date" sortable />
          <Column field="status" header="Status" sortable>
            <template #body="{ data }">
              <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
            </template>
          </Column>
          <Column header="Actions">
            <template #body="{ data }">
              <Button icon="pi pi-eye" class="p-button-text" @click="viewCandidate(data)" />
              <Button icon="pi pi-calendar" class="p-button-text p-button-success" @click="scheduleInterview(data)" />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <Dialog v-model:visible="dialogVisible" header="Candidate Details" :modal="true" :style="{width: '600px'}">
      <div class="grid">
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Full Name</label>
            <InputText v-model="newCandidate.name" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Email</label>
            <InputText v-model="newCandidate.email" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Phone</label>
            <InputText v-model="newCandidate.phone" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Applied Position</label>
            <Dropdown v-model="newCandidate.position" :options="positions" placeholder="Select Position" class="w-full" />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label>Resume/CV</label>
            <FileUpload mode="basic" name="resume" accept=".pdf,.doc,.docx" :maxFileSize="5000000" class="w-full" />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label>Notes</label>
            <Textarea v-model="newCandidate.notes" rows="3" class="w-full" />
          </div>
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" class="p-button-text" @click="dialogVisible = false" />
        <Button label="Save" @click="saveCandidate" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';

interface Candidate {
  id: number;
  name: string;
  position: string;
  email: string;
  phone: string;
  appliedDate: string;
  status: string;
  notes: string;
}

const toast = useToast();
const loading = ref(false);
const dialogVisible = ref(false);

const candidates = ref<Candidate[]>([]);
const positions = ref(['Software Engineer', 'HR Manager', 'Financial Analyst', 'Sales Representative', 'Marketing Specialist']);

const newCandidate = ref({
  name: '',
  position: '',
  email: '',
  phone: '',
  notes: ''
});

const showDialog = () => {
  newCandidate.value = {
    name: '',
    position: '',
    email: '',
    phone: '',
    notes: ''
  };
  dialogVisible.value = true;
};

const saveCandidate = () => {
  if (newCandidate.value.name && newCandidate.value.email) {
    const candidate: Candidate = {
      id: Date.now(),
      name: newCandidate.value.name,
      position: newCandidate.value.position,
      email: newCandidate.value.email,
      phone: newCandidate.value.phone,
      appliedDate: new Date().toLocaleDateString(),
      status: 'Applied',
      notes: newCandidate.value.notes
    };
    
    candidates.value.push(candidate);
    dialogVisible.value = false;
    toast.add({ severity: 'success', summary: 'Success', detail: 'Candidate added', life: 3000 });
  }
};

const viewCandidate = (candidate: Candidate) => {
  toast.add({ severity: 'info', summary: 'View Candidate', detail: `Viewing ${candidate.name}`, life: 3000 });
};

const scheduleInterview = (candidate: Candidate) => {
  toast.add({ severity: 'success', summary: 'Interview Scheduled', detail: `Interview scheduled for ${candidate.name}`, life: 3000 });
};

const getStatusSeverity = (status: string) => {
  switch (status.toLowerCase()) {
    case 'hired': return 'success';
    case 'interviewed': return 'info';
    case 'applied': return 'warning';
    case 'rejected': return 'danger';
    default: return 'info';
  }
};

onMounted(async () => {
  loading.value = true;
  try {
    await new Promise(resolve => setTimeout(resolve, 1000));
    candidates.value = [
      { id: 1, name: 'Alice Johnson', position: 'Software Engineer', email: 'alice@example.com', phone: '(555) 123-4567', appliedDate: '2024-01-15', status: 'Applied', notes: 'Strong technical background' },
      { id: 2, name: 'Bob Smith', position: 'HR Manager', email: 'bob@example.com', phone: '(555) 123-4568', appliedDate: '2024-01-14', status: 'Interviewed', notes: 'Good communication skills' },
      { id: 3, name: 'Carol Davis', position: 'Financial Analyst', email: 'carol@example.com', phone: '(555) 123-4569', appliedDate: '2024-01-13', status: 'Hired', notes: 'Excellent analytical skills' }
    ];
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.candidates-view {
  padding: 0;
}

.field {
  margin-bottom: 1rem;
}
</style>