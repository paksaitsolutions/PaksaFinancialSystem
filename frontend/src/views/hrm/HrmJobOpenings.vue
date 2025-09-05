<template>
  <div class="job-openings-view">
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1>Job Openings</h1>
        <p class="text-color-secondary">Manage job postings and recruitment</p>
      </div>
      <Button label="Post New Job" icon="pi pi-plus" @click="showDialog" />
    </div>

    <Card>
      <template #content>
        <DataTable :value="jobOpenings" :loading="loading" paginator :rows="10">
          <Column field="title" header="Job Title" sortable />
          <Column field="department" header="Department" sortable />
          <Column field="location" header="Location" sortable />
          <Column field="type" header="Type" sortable />
          <Column field="postedDate" header="Posted Date" sortable />
          <Column field="applications" header="Applications" sortable />
          <Column field="status" header="Status" sortable>
            <template #body="{ data }">
              <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
            </template>
          </Column>
          <Column header="Actions">
            <template #body="{ data }">
              <Button icon="pi pi-eye" class="p-button-text" @click="viewJob(data)" />
              <Button icon="pi pi-pencil" class="p-button-text p-button-warning" @click="editJob(data)" />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <Dialog v-model:visible="dialogVisible" header="Job Opening" :modal="true" :style="{width: '700px'}">
      <div class="grid">
        <div class="col-12">
          <div class="field">
            <label>Job Title</label>
            <InputText v-model="newJob.title" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Department</label>
            <Dropdown v-model="newJob.department" :options="departments" placeholder="Select Department" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Job Type</label>
            <Dropdown v-model="newJob.type" :options="jobTypes" placeholder="Select Type" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Location</label>
            <InputText v-model="newJob.location" class="w-full" />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label>Salary Range</label>
            <InputText v-model="newJob.salaryRange" placeholder="e.g., $50,000 - $70,000" class="w-full" />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label>Job Description</label>
            <Editor v-model="newJob.description" editorStyle="height: 200px">
              <template #toolbar>
                <span class="ql-formats">
                  <button class="ql-bold"></button>
                  <button class="ql-italic"></button>
                  <button class="ql-underline"></button>
                </span>
                <span class="ql-formats">
                  <button class="ql-list" value="ordered"></button>
                  <button class="ql-list" value="bullet"></button>
                </span>
              </template>
            </Editor>
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label>Requirements</label>
            <Textarea v-model="newJob.requirements" rows="4" class="w-full" />
          </div>
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" class="p-button-text" @click="dialogVisible = false" />
        <Button label="Post Job" @click="saveJob" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';

interface JobOpening {
  id: number;
  title: string;
  department: string;
  location: string;
  type: string;
  postedDate: string;
  applications: number;
  status: string;
  description: string;
  requirements: string;
  salaryRange: string;
}

const toast = useToast();
const loading = ref(false);
const dialogVisible = ref(false);

const jobOpenings = ref<JobOpening[]>([]);
const departments = ref(['IT', 'HR', 'Finance', 'Sales', 'Marketing', 'Operations']);
const jobTypes = ref(['Full-time', 'Part-time', 'Contract', 'Internship', 'Remote']);

const newJob = ref({
  title: '',
  department: '',
  location: '',
  type: '',
  description: '',
  requirements: '',
  salaryRange: ''
});

const showDialog = () => {
  newJob.value = {
    title: '',
    department: '',
    location: '',
    type: '',
    description: '',
    requirements: '',
    salaryRange: ''
  };
  dialogVisible.value = true;
};

const saveJob = () => {
  if (newJob.value.title && newJob.value.department) {
    const job: JobOpening = {
      id: Date.now(),
      title: newJob.value.title,
      department: newJob.value.department,
      location: newJob.value.location,
      type: newJob.value.type,
      postedDate: new Date().toLocaleDateString(),
      applications: 0,
      status: 'Active',
      description: newJob.value.description,
      requirements: newJob.value.requirements,
      salaryRange: newJob.value.salaryRange
    };
    
    jobOpenings.value.push(job);
    dialogVisible.value = false;
    toast.add({ severity: 'success', summary: 'Success', detail: 'Job posted successfully', life: 3000 });
  }
};

const viewJob = (job: JobOpening) => {
  toast.add({ severity: 'info', summary: 'View Job', detail: `Viewing ${job.title}`, life: 3000 });
};

const editJob = (job: JobOpening) => {
  toast.add({ severity: 'info', summary: 'Edit Job', detail: `Editing ${job.title}`, life: 3000 });
};

const getStatusSeverity = (status: string) => {
  switch (status.toLowerCase()) {
    case 'active': return 'success';
    case 'closed': return 'danger';
    case 'draft': return 'warning';
    default: return 'info';
  }
};

onMounted(async () => {
  loading.value = true;
  try {
    await new Promise(resolve => setTimeout(resolve, 1000));
    jobOpenings.value = [
      { id: 1, title: 'Senior Software Engineer', department: 'IT', location: 'New York', type: 'Full-time', postedDate: '2024-01-15', applications: 25, status: 'Active', description: 'We are looking for a senior software engineer...', requirements: 'Bachelor\'s degree in Computer Science...', salaryRange: '$80,000 - $120,000' },
      { id: 2, title: 'HR Coordinator', department: 'HR', location: 'Remote', type: 'Full-time', postedDate: '2024-01-14', applications: 12, status: 'Active', description: 'Join our HR team as a coordinator...', requirements: 'Bachelor\'s degree in HR or related field...', salaryRange: '$45,000 - $60,000' },
      { id: 3, title: 'Marketing Intern', department: 'Marketing', location: 'Chicago', type: 'Internship', postedDate: '2024-01-13', applications: 8, status: 'Closed', description: 'Summer internship opportunity...', requirements: 'Currently enrolled in Marketing program...', salaryRange: '$15/hour' }
    ];
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.job-openings-view {
  padding: 0;
}

.field {
  margin-bottom: 1rem;
}
</style>