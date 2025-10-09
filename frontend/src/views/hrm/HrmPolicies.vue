<template>
  <div class="policies-view">
    <div class="grid">
      <div class="col-12">
        <div class="flex flex-column md:flex-row justify-content-between align-items-start md:align-items-center mb-4 gap-3">
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
              <h3>Policies ({{ policies.length }})</h3>
              <div class="flex gap-2">
                <InputText 
                  v-model="filters['global'].value" 
                  placeholder="Search policies..." 
                  class="p-inputtext-sm"
                />
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
              responsiveLayout="scroll"
              :scrollable="true"
              scrollHeight="400px"
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
              <Column header="Actions" style="min-width: 10rem">
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
      :style="{width: '650px', maxWidth: '95vw'}" 
      :header="editing ? 'Edit Policy' : 'New Policy'" 
      :modal="true"
      :closable="!submitting"
      :closeOnEscape="!submitting"
      class="p-fluid"
      :breakpoints="{'960px': '75vw', '640px': '95vw'}"
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
        <InputText 
          id="effectiveDate" 
          v-model="policy.effectiveDate" 
          type="date"
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
import { FilterMatchMode } from 'primevue/api';
import { useToast } from 'primevue/usetoast';
import { hrmService, type Policy } from '@/services/hrmService';

interface LocalPolicy {
  id?: string | null;
  title: string;
  description: string;
  content: string;
  category: string;
  effectiveDate: string;
  status: string;
}

const toast = useToast();

// Data
const policies = ref<LocalPolicy[]>([]);
const policy = ref<LocalPolicy>({
  title: '',
  category: '',
  description: '',
  content: '',
  effectiveDate: new Date().toISOString().split('T')[0],
  status: 'ACTIVE'
});
const viewingPolicy = ref<LocalPolicy | null>(null);

// UI State
const loading = ref(false);
const submitting = ref(false);
const deleting = ref(false);
const policyDialog = ref(false);
const deletePolicyDialog = ref(false);
const viewerDialog = ref(false);
const editing = ref(false);
const submitted = ref(false);

// Filters
const filters = ref({
  global: { value: null, matchMode: FilterMatchMode.CONTAINS }
});

// Options
const categories = ref([
  { name: 'HR Policies', code: 'HR' },
  { name: 'IT Policies', code: 'IT' },
  { name: 'Finance Policies', code: 'FINANCE' },
  { name: 'Security Policies', code: 'SECURITY' },
  { name: 'Compliance', code: 'COMPLIANCE' }
]);

const statuses = ref([
  { label: 'Active', value: 'ACTIVE' },
  { label: 'Draft', value: 'DRAFT' },
  { label: 'Inactive', value: 'INACTIVE' },
  { label: 'Expired', value: 'EXPIRED' }
]);

// Breadcrumb
const home = ref({ icon: 'pi pi-home', to: '/' });
const breadcrumbItems = ref([
  { label: 'HRM', to: '/hrm' },
  { label: 'Policies' }
]);

// Methods
const loadPolicies = async () => {
  loading.value = true;
  try {
    const response = await hrmService.getPolicies();
    policies.value = response.data?.map((p: Policy) => ({
      id: p.id,
      title: p.title,
      description: p.description || '',
      content: p.content,
      category: p.category,
      effectiveDate: p.effective_date,
      status: p.status
    })) || [];
  } catch (error) {
    console.error('Error loading policies:', error);
    // Fallback data
    policies.value = [
      {
        id: '1',
        title: 'Leave Policy',
        description: 'Annual leave and sick leave policy',
        content: '<p>This policy outlines...</p>',
        category: 'HR',
        effectiveDate: '2024-01-01',
        status: 'ACTIVE'
      }
    ];
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
    title: '',
    category: '',
    description: '',
    content: '',
    effectiveDate: new Date().toISOString().split('T')[0],
    status: 'ACTIVE'
  };
  editing.value = false;
  submitted.value = false;
  policyDialog.value = true;
};

const editPolicy = (data: LocalPolicy) => {
  policy.value = { ...data };
  editing.value = true;
  submitted.value = false;
  policyDialog.value = true;
};

const viewPolicy = (data: LocalPolicy) => {
  viewingPolicy.value = data;
  viewerDialog.value = true;
};

const hideDialog = () => {
  policyDialog.value = false;
  submitted.value = false;
};

const savePolicy = async () => {
  submitted.value = true;
  
  if (!policy.value.title || !policy.value.content) {
    return;
  }

  submitting.value = true;
  try {
    const policyData = {
      title: policy.value.title,
      category: policy.value.category,
      description: policy.value.description,
      content: policy.value.content,
      effective_date: policy.value.effectiveDate,
      status: policy.value.status,
      approval_required: false
    };

    if (editing.value && policy.value.id) {
      await hrmService.updatePolicy(policy.value.id, policyData);
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Policy updated successfully',
        life: 3000
      });
    } else {
      await hrmService.createPolicy(policyData);
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Policy created successfully',
        life: 3000
      });
    }
    
    hideDialog();
    await loadPolicies();
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
};

const confirmDeletePolicy = (data: LocalPolicy) => {
  policy.value = data;
  deletePolicyDialog.value = true;
};

const deletePolicy = async () => {
  if (!policy.value.id) return;
  
  deleting.value = true;
  try {
    await hrmService.deletePolicy(policy.value.id);
    deletePolicyDialog.value = false;
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Policy deleted successfully',
      life: 3000
    });
    await loadPolicies();
  } catch (error) {
    console.error('Error deleting policy:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to delete policy',
      life: 3000
    });
  } finally {
    deleting.value = false;
  }
};

const printPolicy = () => {
  window.print();
};

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString();
};

const getStatusSeverity = (status: string) => {
  const severityMap: { [key: string]: string } = {
    ACTIVE: 'success',
    DRAFT: 'info',
    INACTIVE: 'secondary',
    EXPIRED: 'danger'
  };
  return severityMap[status] || 'secondary';
};

// Lifecycle
onMounted(() => {
  loadPolicies();
});
</script>

<style scoped>
.policies-view {
  padding: 1rem;
}

.policy-viewer .policy-content {
  max-height: 60vh;
  overflow-y: auto;
}

.policy-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.policy-body {
  line-height: 1.6;
}
</style>