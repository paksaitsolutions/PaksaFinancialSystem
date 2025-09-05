<template>
  <div class="email-templates-view">
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1>Email Templates</h1>
        <p class="text-color-secondary">Manage HR email templates for automated communications</p>
      </div>
      <Button label="New Template" icon="pi pi-plus" @click="showDialog" />
    </div>

    <Card>
      <template #content>
        <DataTable :value="templates" :loading="loading" paginator :rows="10">
          <Column field="name" header="Template Name" sortable />
          <Column field="category" header="Category" sortable />
          <Column field="subject" header="Subject" sortable />
          <Column field="lastModified" header="Last Modified" sortable />
          <Column field="status" header="Status" sortable>
            <template #body="{ data }">
              <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
            </template>
          </Column>
          <Column header="Actions">
            <template #body="{ data }">
              <Button icon="pi pi-pencil" class="p-button-text p-button-warning" @click="editTemplate(data)" />
              <Button icon="pi pi-eye" class="p-button-text" @click="previewTemplate(data)" />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <Dialog v-model:visible="dialogVisible" header="Email Template" :modal="true" :style="{width: '700px'}">
      <div class="field">
        <label>Template Name</label>
        <InputText v-model="newTemplate.name" class="w-full" />
      </div>
      <div class="field">
        <label>Category</label>
        <Dropdown v-model="newTemplate.category" :options="categories" placeholder="Select Category" class="w-full" />
      </div>
      <div class="field">
        <label>Subject</label>
        <InputText v-model="newTemplate.subject" class="w-full" />
      </div>
      <div class="field">
        <label>Email Content</label>
        <Editor v-model="newTemplate.content" editorStyle="height: 300px">
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
      <template #footer>
        <Button label="Cancel" class="p-button-text" @click="dialogVisible = false" />
        <Button label="Save" @click="saveTemplate" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';

interface EmailTemplate {
  id: number;
  name: string;
  category: string;
  subject: string;
  content: string;
  lastModified: string;
  status: string;
}

const toast = useToast();
const loading = ref(false);
const dialogVisible = ref(false);

const templates = ref<EmailTemplate[]>([]);
const categories = ref(['Welcome', 'Leave Approval', 'Performance Review', 'Training', 'Termination', 'General']);

const newTemplate = ref({
  name: '',
  category: '',
  subject: '',
  content: ''
});

const showDialog = () => {
  newTemplate.value = {
    name: '',
    category: '',
    subject: '',
    content: ''
  };
  dialogVisible.value = true;
};

const saveTemplate = () => {
  if (newTemplate.value.name && newTemplate.value.subject) {
    const template: EmailTemplate = {
      id: Date.now(),
      name: newTemplate.value.name,
      category: newTemplate.value.category,
      subject: newTemplate.value.subject,
      content: newTemplate.value.content,
      lastModified: new Date().toLocaleDateString(),
      status: 'Active'
    };
    
    templates.value.push(template);
    dialogVisible.value = false;
    toast.add({ severity: 'success', summary: 'Success', detail: 'Email template created', life: 3000 });
  }
};

const editTemplate = (template: EmailTemplate) => {
  toast.add({ severity: 'info', summary: 'Edit Template', detail: `Editing ${template.name}`, life: 3000 });
};

const previewTemplate = (template: EmailTemplate) => {
  toast.add({ severity: 'info', summary: 'Preview Template', detail: `Previewing ${template.name}`, life: 3000 });
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
    templates.value = [
      { id: 1, name: 'Welcome New Employee', category: 'Welcome', subject: 'Welcome to the Team!', content: '<p>Welcome to our company...</p>', lastModified: '2024-01-15', status: 'Active' },
      { id: 2, name: 'Leave Approved', category: 'Leave Approval', subject: 'Your Leave Request has been Approved', content: '<p>Your leave request has been approved...</p>', lastModified: '2024-01-14', status: 'Active' },
      { id: 3, name: 'Performance Review Reminder', category: 'Performance Review', subject: 'Performance Review Due', content: '<p>Your performance review is due...</p>', lastModified: '2024-01-13', status: 'Active' }
    ];
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.email-templates-view {
  padding: 0;
}

.field {
  margin-bottom: 1rem;
}
</style>