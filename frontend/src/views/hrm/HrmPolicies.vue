<template>
  <div class="policies-view">
    <div class="grid">
      <div class="col-12">
        <div class="flex justify-content-between align-items-center mb-4">
          <div>
            <h1>HR Policies</h1>
            <Breadcrumb :home="home" :model="breadcrumbItems" class="mb-4" />
          </div>
          <div>
            <Button 
              label="New Policy" 
              icon="pi pi-plus" 
              class="p-button-success" 
              @click="showNewPolicyDialog" 
            />
          </div>
        </div>
      </div>

      <!-- Policy List -->
      <div class="col-12">
        <Card>
          <template #header>
            <div class="flex justify-content-between align-items-center">
              <h3>Policies</h3>
              <div>
                <Button 
                  icon="pi pi-refresh" 
                  class="p-button-text" 
                  @click="loadPolicies" 
                  :loading="loading"
                />
              </div>
            </div>
          </template>
          <template #content>
            <DataTable 
              :value="policies" 
              :paginator="true" 
              :rows="10"
              :loading="loading"
              :filters="filters"
              :globalFilterFields="['title', 'category', 'status']"
              :rowsPerPageOptions="[5,10,25,50]"
              class="p-datatable-sm"
            >
              <template #empty>No policies found.</template>
              <Column field="title" header="Title" :sortable="true">
                <template #body="{ data }">
                  <span class="font-medium">{{ data.title }}</span>
                </template>
              </Column>
              <Column field="category" header="Category" :sortable="true" />
              <Column field="effectiveDate" header="Effective Date" :sortable="true">
                <template #body="{ data }">
                  {{ formatDate(data.effectiveDate) }}
                </template>
              </Column>
              <Column field="status" header="Status" :sortable="true">
                <template #body="{ data }">
                  <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
                </template>
              </Column>
              <Column header="Actions" style="width: 10rem">
                <template #body="{ data }">
                  <div class="flex gap-2">
                    <Button 
                      icon="pi pi-eye" 
                      class="p-button-text p-button-sm" 
                      @click="viewPolicy(data)" 
                      v-tooltip.top="'View Policy'"
                    />
                    <Button 
                      icon="pi pi-pencil" 
                      class="p-button-text p-button-sm p-button-warning" 
                      @click="editPolicy(data)" 
                      v-tooltip.top="'Edit Policy'"
                    />
                    <Button 
                      icon="pi pi-trash" 
                      class="p-button-text p-button-sm p-button-danger" 
                      @click="confirmDeletePolicy(data)" 
                      v-tooltip.top="'Delete Policy'"
                    />
                  </div>
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </div>
    </div>

    <!-- Policy Dialog -->
    <Dialog 
      v-model:visible="policyDialog" 
      :style="{width: '650px'}" 
      :header="editing ? 'Edit Policy' : 'New Policy'" 
      :modal="true"
      :closable="!submitting"
      :closeOnEscape="!submitting"
      class="p-fluid"
    >
      <div class="field">
        <label for="title">Title <span class="text-red-500">*</span></label>
        <InputText 
          id="title" 
          v-model.trim="policy.title" 
          required="true" 
          autofocus 
          :class="{'p-invalid': submitted && !policy.title}" 
        />
        <small class="p-error" v-if="submitted && !policy.title">Title is required.</small>
      </div>

      <div class="field">
        <label for="category">Category</label>
        <Dropdown 
          id="category" 
          v-model="policy.category" 
          :options="categories" 
          optionLabel="name" 
          optionValue="code" 
          placeholder="Select a category"
        />
      </div>

      <div class="field">
        <label for="effectiveDate">Effective Date</label>
        <Calendar 
          id="effectiveDate" 
          v-model="policy.effectiveDate" 
          dateFormat="yy-mm-dd" 
          :showIcon="true" 
          :showButtonBar="true"
        />
      </div>

      <div class="field">
        <label for="description">Description</label>
        <Textarea id="description" v-model="policy.description" rows="3" />
      </div>

      <div class="field">
        <label for="content">Policy Content <span class="text-red-500">*</span></label>
        <Editor 
          v-model="policy.content" 
          editorStyle="height: 200px"
          :class="{'p-invalid': submitted && !policy.content}"
        >
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
        <small class="p-error" v-if="submitted && !policy.content">Content is required.</small>
      </div>

      <div class="field">
        <label for="status">Status</label>
        <Dropdown 
          id="status" 
          v-model="policy.status" 
          :options="statuses" 
          optionLabel="label" 
          optionValue="value"
        />
      </div>

      <template #footer>
        <Button 
          label="Cancel" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="hideDialog" 
          :disabled="submitting"
        />
        <Button 
          :label="editing ? 'Update' : 'Save'" 
          icon="pi pi-check" 
          class="p-button-text" 
          @click="savePolicy" 
          :loading="submitting"
        />
      </template>
    </Dialog>

    <!-- Delete Confirmation Dialog -->
    <Dialog 
      v-model:visible="deletePolicyDialog" 
      :style="{width: '450px'}" 
      header="Confirm" 
      :modal="true"
    >
      <div class="flex align-items-center justify-content-center">
        <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
        <span v-if="policy">Are you sure you want to delete <b>{{ policy.title }}</b>?</span>
      </div>
      <template #footer>
        <Button 
          label="No" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="deletePolicyDialog = false"
        />
        <Button 
          label="Yes" 
          icon="pi pi-check" 
          class="p-button-danger" 
          @click="deletePolicy"
          :loading="deleting"
        />
      </template>
    </Dialog>

    <!-- Policy Viewer Dialog -->
    <Dialog 
      v-model:visible="viewerDialog" 
      :style="{width: '800px', maxWidth: '90vw'}" 
      :header="viewingPolicy?.title || 'Policy'"
      :modal="true"
      class="policy-viewer"
    >
      <div v-if="viewingPolicy" class="policy-content">
        <div class="policy-meta mb-4">
          <div class="text-500">
            <span class="mr-3">
              <i class="pi pi-tag mr-1"></i>
              {{ viewingPolicy.category }}
            </span>
            <span>
              <i class="pi pi-calendar mr-1"></i>
              Effective: {{ formatDate(viewingPolicy.effectiveDate) }}
            </span>
          </div>
          <Tag :value="viewingPolicy.status" :severity="getStatusSeverity(viewingPolicy.status)" />
        </div>
        
        <div class="policy-description mb-4">
          <p class="text-700">{{ viewingPolicy.description }}</p>
        </div>
        
        <Divider />
        
        <div class="policy-body" v-html="viewingPolicy.content"></div>
      </div>
      
      <template #footer>
        <Button 
          label="Close" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="viewerDialog = false"
        />
        <Button 
          label="Print" 
          icon="pi pi-print" 
          class="p-button-primary" 
          @click="printPolicy"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';

// Types
interface Policy {
  id: string | null;
  title: string;
  description: string;
  content: string;
  category: string;
  effectiveDate: string | Date;
  status: string;
  createdAt?: Date;
  updatedAt?: Date;
}

interface Category {
  name: string;
  code: string;
}

interface StatusOption {
  label: string;
  value: string;
}

const toast = useToast();

// State
const loading = ref(false);
const submitting = ref(false);
const deleting = ref(false);
const policyDialog = ref(false);
const deletePolicyDialog = ref(false);
const viewerDialog = ref(false);
const editing = ref(false);
const submitted = ref(false);

const policies = ref<Policy[]>([]);
const viewingPolicy = ref<Policy | null>(null);
const policy = ref<Policy>({
  id: null,
  title: '',
  description: '',
  content: '',
  category: '',
  effectiveDate: new Date(),
  status: 'draft'
});

const categories = ref<Category[]>([
  { name: 'Attendance', code: 'attendance' },
  { name: 'Leave', code: 'leave' },
  { name: 'Code of Conduct', code: 'conduct' },
  { name: 'Health & Safety', code: 'safety' },
  { name: 'Diversity & Inclusion', code: 'diversity' },
  { name: 'Remote Work', code: 'remote' },
  { name: 'Benefits', code: 'benefits' },
  { name: 'Other', code: 'other' }
]);

const statuses = ref<StatusOption[]>([
  { label: 'Draft', value: 'draft' },
  { label: 'Active', value: 'active' },
  { label: 'Inactive', value: 'inactive' },
  { label: 'Archived', value: 'archived' }
]);

const filters = ref({
  global: { value: null, matchMode: 'contains' },
  title: { value: null, matchMode: 'contains' },
  category: { value: null, matchMode: 'equals' },
  status: { value: null, matchMode: 'equals' }
});

const home = ref({
  icon: 'pi pi-home',
  to: '/'
});

const breadcrumbItems = ref([
  { label: 'HRM', to: '/hrm' },
  { label: 'Policies', to: '/hrm/policies' }
]);

// Methods
const loadPolicies = async () => {
  loading.value = true;
  try {
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    policies.value = [
      {
        id: '1',
        title: 'Remote Work Policy',
        description: 'Guidelines and expectations for remote work arrangements',
        content: '<h2>1. Purpose</h2><p>This policy outlines the guidelines for remote work arrangements...</p>',
        category: 'remote',
        effectiveDate: '2023-01-15',
        status: 'active',
        createdAt: new Date('2023-01-10'),
        updatedAt: new Date('2023-01-10')
      },
      {
        id: '2',
        title: 'Code of Conduct',
        description: 'Expected behavior and professional standards for all employees',
        content: '<h2>1. Introduction</h2><p>Our company is committed to maintaining a workplace that is free from discrimination and harassment...</p>',
        category: 'conduct',
        effectiveDate: '2022-06-01',
        status: 'active',
        createdAt: new Date('2022-05-15'),
        updatedAt: new Date('2022-11-20')
      },
      {
        id: '3',
        title: 'Paid Time Off Policy',
        description: 'Guidelines for requesting and using paid time off',
        content: '<h2>1. Eligibility</h2><p>All full-time employees are eligible for paid time off...</p>',
        category: 'leave',
        effectiveDate: '2023-03-01',
        status: 'draft',
        createdAt: new Date('2023-02-15'),
        updatedAt: new Date('2023-02-28')
      }
    ];
  } catch (error) {
    console.error('Error loading policies:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load policies',
      life: 3000
    });
  } finally {
    loading.value = false;
  }
};

const showNewPolicyDialog = () => {
  policy.value = {
    id: null,
    title: '',
    description: '',
    content: '',
    category: '',
    effectiveDate: new Date(),
    status: 'draft'
  };
  editing.value = false;
  submitted.value = false;
  policyDialog.value = true;
};

const editPolicy = (pol: Policy) => {
  policy.value = { ...pol };
  editing.value = true;
  policyDialog.value = true;
};

const viewPolicy = (pol: Policy) => {
  viewingPolicy.value = { ...pol };
  viewerDialog.value = true;
};

const hideDialog = () => {
  policyDialog.value = false;
  submitted.value = false;
};

const savePolicy = async () => {
  submitted.value = true;
  
  if (policy.value.title && policy.value.content) {
    submitting.value = true;
    
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      if (editing.value) {
        const index = policies.value.findIndex(p => p.id === policy.value.id);
        if (index !== -1) {
          policies.value[index] = { 
            ...policy.value,
            updatedAt: new Date()
          };
        }
        toast.add({
          severity: 'success',
          summary: 'Success',
          detail: 'Policy updated',
          life: 3000
        });
      } else {
        const newPolicy: Policy = {
          ...policy.value,
          id: Date.now().toString(),
          createdAt: new Date(),
          updatedAt: new Date()
        };
        policies.value.push(newPolicy);
        toast.add({
          severity: 'success',
          summary: 'Success',
          detail: 'Policy created',
          life: 3000
        });
      }
      
      policyDialog.value = false;
      policy.value = {
        id: null,
        title: '',
        description: '',
        content: '',
        category: '',
        effectiveDate: new Date(),
        status: 'draft'
      };
    } catch (error) {
      console.error('Error saving policy:', error);
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to save policy',
        life: 3000
      });
    } finally {
      submitting.value = false;
    }
  }
};

const confirmDeletePolicy = (pol: Policy) => {
  policy.value = { ...pol };
  deletePolicyDialog.value = true;
};

const deletePolicy = async () => {
  if (policy.value.id) {
    deleting.value = true;
    
    try {
      await new Promise(resolve => setTimeout(resolve, 500));
      
      policies.value = policies.value.filter(p => p.id !== policy.value.id);
      
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Policy deleted',
        life: 3000
      });
    } catch (error) {
      console.error('Error deleting policy:', error);
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: 'Failed to delete policy',
        life: 3000
      });
    } finally {
      deletePolicyDialog.value = false;
      deleting.value = false;
    }
  }
};

const printPolicy = () => {
  window.print();
};

const formatDate = (date: string | Date): string => {
  if (!date) return '';
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  return dateObj.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric' 
  });
};

const getStatusSeverity = (status: string): string => {
  switch (status) {
    case 'active':
      return 'success';
    case 'draft':
      return 'info';
    case 'inactive':
      return 'warning';
    case 'archived':
      return 'danger';
    default:
      return 'info';
  }
};

// Lifecycle hooks
onMounted(() => {
  loadPolicies();
});
</script>

<style scoped>
.policies-view {
  padding: 1rem;
}

:deep(.p-card) {
  margin-bottom: 1rem;
}

:deep(.p-card .p-card-title) {
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

:deep(.p-datatable) {
  font-size: 0.9rem;
}

:deep(.p-datatable .p-datatable-thead > tr > th) {
  background-color: #f5f5f5;
  font-weight: 600;
}

:deep(.p-datatable .p-datatable-tbody > tr > td) {
  padding: 0.5rem 1rem;
}

:deep(.p-dialog .p-dialog-header) {
  padding: 1.5rem 1.5rem 0.5rem;
}

:deep(.p-dialog .p-dialog-content) {
  padding: 1.5rem;
}

:deep(.p-dialog .p-dialog-footer) {
  padding: 0.5rem 1.5rem 1.5rem;
}

.field {
  margin-bottom: 1.5rem;
}

/* Policy Viewer Styles */
.policy-viewer :deep(.p-dialog-content) {
  padding: 2rem;
}

.policy-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.policy-content :deep(h1),
.policy-content :deep(h2),
.policy-content :deep(h3) {
  margin: 1.5rem 0 1rem;
  color: var(--primary-color);
}

.policy-content :deep(p) {
  margin-bottom: 1rem;
  line-height: 1.6;
}

.policy-content :deep(ul),
.policy-content :deep(ol) {
  margin: 1rem 0 1rem 1.5rem;
  padding: 0;
}

.policy-content :deep(li) {
  margin-bottom: 0.5rem;
}

/* Print styles */
@media print {
  body * {
    visibility: hidden;
  }
  
  .policy-viewer,
  .policy-viewer * {
    visibility: visible;
  }
  
  .policy-viewer {
    position: absolute;
    left: 0;
    top: 0;
    width: 100%;
    margin: 0;
    padding: 0;
  }
  
  .policy-viewer :deep(.p-dialog-header),
  .policy-viewer :deep(.p-dialog-footer) {
    display: none;
  }
  
  .policy-viewer :deep(.p-dialog-content) {
    padding: 0;
    overflow: visible;
  }
}
</style>