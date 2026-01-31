<template>
  <div class="policy-management-view">
    <Toast />
    <div class="card">
      <Toolbar class="mb-4">
        <template #start>
          <Button label="New Policy" icon="pi pi-plus" class="p-button-success mr-2" @click="openNew" />
        </template>
      </Toolbar>

      <DataTable :value="policies" :loading="loading" responsiveLayout="scroll">
        <Column field="name" header="Name" :sortable="true"></Column>
        <Column field="category" header="Category" :sortable="true"></Column>
        <Column field="version" header="Version"></Column>
        <Column field="is_active" header="Status">
          <template #body="{ data }">
            <Tag :value="data.is_active ? 'Active' : 'Inactive'" :severity="data.is_active ? 'success' : 'danger'" />
          </template>
        </Column>
        <Column field="updated_at" header="Last Updated">
            <template #body="{ data }">
                {{ format(new Date(data.updated_at), 'PPpp') }}
            </template>
        </Column>
        <Column :exportable="false" style="min-width:8rem">
          <template #body="{ data }">
            <Button icon="pi pi-pencil" class="p-button-rounded p-button-success mr-2" @click="editPolicy(data)" />
            <Button icon="pi pi-trash" class="p-button-rounded p-button-warning" @click="confirmDeletePolicy(data)" />
          </template>
        </Column>
      </DataTable>
    </div>

    <Dialog v-model:visible="policyDialog" :style="{width: '450px'}" header="Policy Details" :modal="true" class="p-fluid">
        <div class="field">
            <label for="name">Name</label>
            <InputText id="name" v-model.trim="policy.name" required="true" autofocus :class="{'p-invalid': submitted && !policy.name}" />
            <small class="p-error" v-if="submitted && !policy.name">Name is required.</small>
        </div>
        <div class="field">
            <label for="description">Description</label>
            <Textarea id="description" v-model="policy.description" required="true" rows="3" cols="20" />
        </div>
        <div class="field">
            <label for="category">Category</label>
            <InputText id="category" v-model.trim="policy.category" required="true" />
        </div>
        <div class="field">
            <label for="version">Version</label>
            <InputText id="version" v-model.trim="policy.version" required="true" />
        </div>
        <div class="field">
            <label for="content">Content</label>
            <Textarea id="content" v-model="policy.content" required="true" rows="5" cols="20" />
        </div>
        <div class="field-checkbox">
            <Checkbox id="is_active" v-model="policy.is_active" :binary="true" />
            <label for="is_active">Active</label>
        </div>

        <template #footer>
            <Button label="Cancel" icon="pi pi-times" class="p-button-text" @click="hideDialog"/>
            <Button label="Save" icon="pi pi-check" class="p-button-text" @click="savePolicy" />
        </template>
    </Dialog>

    <Dialog v-model:visible="deletePolicyDialog" :style="{width: '450px'}" header="Confirm" :modal="true">
      <div class="confirmation-content">
        <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
        <span v-if="policy">Are you sure you want to delete <b>{{policy.name}}</b>?</span>
      </div>
      <template #footer>
        <Button label="No" icon="pi pi-times" class="p-button-text" @click="deletePolicyDialog = false"/>
        <Button label="Yes" icon="pi pi-check" class="p-button-text" @click="deletePolicy" />
      </template>
    </Dialog>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Textarea from 'primevue/textarea';
import Tag from 'primevue/tag';
import { format } from 'date-fns';

// MOCK DATA AND API
// TODO: Replace with real API calls once the api.ts corruption is resolved.

interface SecurityPolicy {
    id: number;
    name: string;
    description: string;
    category: string;
    content: string;
    version: string;
    is_active: boolean;
    created_at: string;
    updated_at: string;
}

const mockPolicies: SecurityPolicy[] = [
    {
        id: 1,
        name: 'Password Complexity Policy',
        description: 'Requires strong passwords for all user accounts.',
        category: 'Access Control',
        content: 'Passwords must be at least 12 characters long, include uppercase, lowercase, numbers, and symbols.',
        version: '1.2',
        is_active: true,
        created_at: '2023-01-15T10:00:00Z',
        updated_at: '2023-05-20T14:30:00Z',
    },
    {
        id: 2,
        name: 'Data Encryption Policy',
        description: 'Ensures all sensitive data is encrypted at rest and in transit.',
        category: 'Data Protection',
        content: 'All databases containing PII must use AES-256 encryption. All network traffic must use TLS 1.2 or higher.',
        version: '2.0',
        is_active: true,
        created_at: '2023-02-01T09:00:00Z',
        updated_at: '2023-06-01T11:00:00Z',
    },
    {
        id: 3,
        name: 'Incident Response Plan',
        description: 'Defines procedures for handling security incidents.',
        category: 'Security Operations',
        content: 'In case of a breach, the security team must be notified within 1 hour. The incident must be documented and resolved within 24 hours.',
        version: '1.5',
        is_active: false,
        created_at: '2023-03-10T16:00:00Z',
        updated_at: '2023-04-10T18:00:00Z',
    },
];

const mockApi = {
    getSecurityPolicies: async (): Promise<SecurityPolicy[]> => {
        console.log('Mock API: Fetching policies...');
        return new Promise(resolve => setTimeout(() => resolve(JSON.parse(JSON.stringify(mockPolicies))), 500));
    },
    createSecurityPolicy: async (policy: Omit<SecurityPolicy, 'id' | 'created_at' | 'updated_at'>): Promise<SecurityPolicy> => {
        console.log('Mock API: Creating policy...', policy);
        const newPolicy: SecurityPolicy = {
            ...policy,
            id: Math.floor(Math.random() * 1000) + 10,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
        };
        mockPolicies.push(newPolicy);
        return new Promise(resolve => setTimeout(() => resolve(newPolicy), 500));
    },
    updateSecurityPolicy: async (id: number, policyUpdate: Partial<SecurityPolicy>): Promise<SecurityPolicy> => {
        console.log(`Mock API: Updating policy ${id}...`, policyUpdate);
        const index = mockPolicies.findIndex(p => p.id === id);
        if (index !== -1) {
            const originalPolicy = mockPolicies[index];
            const updatedPolicy: SecurityPolicy = {
                ...originalPolicy,
                ...policyUpdate,
                id: originalPolicy.id, // Ensure ID is not changed and is not undefined
                updated_at: new Date().toISOString(),
            };
            mockPolicies[index] = updatedPolicy;
            return new Promise(resolve => setTimeout(() => resolve(updatedPolicy), 500));
        }
        throw new Error('Policy not found');
    },
    deleteSecurityPolicy: async (id: number): Promise<{}> => {
        console.log(`Mock API: Deleting policy ${id}...`);
        const index = mockPolicies.findIndex(p => p.id === id);
        if (index !== -1) {
            mockPolicies.splice(index, 1);
            return new Promise(resolve => setTimeout(() => resolve({}), 500));
        }
        throw new Error('Policy not found');
    },
};

// COMPONENT LOGIC
const toast = useToast();
const policies = ref<SecurityPolicy[]>([]);
const policyDialog = ref(false);
const deletePolicyDialog = ref(false);
const policy = ref<Partial<SecurityPolicy>>({});
const submitted = ref(false);
const loading = ref(true);

onMounted(() => {
    loadPolicies();
});

const loadPolicies = async () => {
    loading.value = true;
    try {
        // TODO: Replace with: policies.value = await api.getSecurityPolicies();
        policies.value = await mockApi.getSecurityPolicies();
    } catch (error) {
        console.error('Failed to load policies:', error);
        toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load policies', life: 3000 });
    } finally {
        loading.value = false;
    }
};

const openNew = () => {
    policy.value = { is_active: true, version: '1.0' };
    submitted.value = false;
    policyDialog.value = true;
};

const hideDialog = () => {
    policyDialog.value = false;
    submitted.value = false;
};

const savePolicy = async () => {
    submitted.value = true;

    if (!policy.value.name?.trim()) {
        return;
    }

    try {
        if (policy.value.id) {
            // TODO: Replace with: await api.updateSecurityPolicy(policy.value.id, policy.value);
            await mockApi.updateSecurityPolicy(policy.value.id, policy.value);
            toast.add({ severity: 'success', summary: 'Successful', detail: 'Policy Updated', life: 3000 });
        } else {
            // TODO: Replace with: await api.createSecurityPolicy(policy.value as any);
            await mockApi.createSecurityPolicy(policy.value as any);
            toast.add({ severity: 'success', summary: 'Successful', detail: 'Policy Created', life: 3000 });
        }
        policyDialog.value = false;
        policy.value = {};
        loadPolicies(); // Refresh list
    } catch (error) {
        console.error('Failed to save policy:', error);
        toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to save policy', life: 3000 });
    }
};

const editPolicy = (prod: SecurityPolicy) => {
    policy.value = { ...prod };
    policyDialog.value = true;
};

const confirmDeletePolicy = (prod: SecurityPolicy) => {
    policy.value = prod;
    deletePolicyDialog.value = true;
};

const deletePolicy = async () => {
    if (!policy.value.id) return;

    try {
        // TODO: Replace with: await api.deleteSecurityPolicy(policy.value.id);
        await mockApi.deleteSecurityPolicy(policy.value.id);
        deletePolicyDialog.value = false;
        toast.add({ severity: 'success', summary: 'Successful', detail: 'Policy Deleted', life: 3000 });
        policy.value = {};
        loadPolicies(); // Refresh list
    } catch (error) {
        console.error('Failed to delete policy:', error);
        toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to delete policy', life: 3000 });
    }
};

</script>

<style scoped>
.policy-management-view {
    padding: 1rem;
}
</style>
  <div class="security-policies">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center md:justify-between mb-6 gap-4">
      <div>
        <h1 class="text-2xl font-semibold text-gray-900">Security Policies</h1>
        <p class="text-gray-600">Manage and configure system security policies</p>
      </div>
      <div class="flex gap-3">
        <Button 
          icon="pi pi-plus" 
          label="Add Policy" 
          class="p-button-primary p-button-sm"
          @click="showPolicyDialog = true"
        />
      </div>
    </div>

    <!-- Policies List -->
    <Card>
      <template #content>
        <DataTable 
          :value="policies" 
          :loading="loading"
          :paginator="true"
          :rows="10"
          :rowsPerPageOptions="[5, 10, 25, 50]"
          paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
          currentPageReportTemplate="Showing {first} to {last} of {totalRecords} policies"
          responsiveLayout="scroll"
        >
          <Column field="name" header="Policy Name" :sortable="true">
            <template #body="{ data }">
              <span class="font-medium">{{ data.name }}</span>
            </template>
          </Column>
          <Column field="status" header="Status" :sortable="true">
            <template #body="{ data }">
              <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
            </template>
          </Column>
          <Column field="lastUpdated" header="Last Updated" :sortable="true">
            <template #body="{ data }">
              {{ formatDateTime(data.lastUpdated) }}
            </template>
          </Column>
          <Column header="Actions" style="width: 15%; min-width: 10rem">
            <template #body="{ data }">
              <div class="flex gap-2">
                <Button 
                  icon="pi pi-pencil" 
                  class="p-button-text p-button-rounded p-button-sm"
                  @click="editPolicy(data)"
                />
                <Button 
                  icon="pi pi-trash" 
                  class="p-button-text p-button-rounded p-button-sm p-button-danger"
                  @click="confirmDeletePolicy(data)"
                />
              </div>
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <!-- Policy Dialog -->
    <Dialog 
      v-model:visible="showPolicyDialog" 
      :header="editingPolicy ? 'Edit Policy' : 'Add New Policy'" 
      :modal="true"
      :style="{ width: '600px' }"
      :closable="false"
    >
      <div class="grid grid-cols-1 gap-4">
        <div class="field">
          <label for="policyName" class="block text-sm font-medium text-gray-700 mb-1">Policy Name</label>
          <InputText 
            id="policyName" 
            v-model="policyForm.name" 
            class="w-full" 
            :class="{ 'p-invalid': submitted && !policyForm.name }"
          />
          <small v-if="submitted && !policyForm.name" class="p-error">Policy name is required.</small>
        </div>
        <div class="field">
          <label for="policyDescription" class="block text-sm font-medium text-gray-700 mb-1">Description</label>
          <Textarea 
            id="policyDescription" 
            v-model="policyForm.description" 
            rows="3" 
            class="w-full"
            :class="{ 'p-invalid': submitted && !policyForm.description }"
          />
          <small v-if="submitted && !policyForm.description" class="p-error">Description is required.</small>
        </div>
        <div class="field">
          <label for="policyStatus" class="block text-sm font-medium text-gray-700 mb-1">Status</label>
          <Dropdown 
            id="policyStatus" 
            v-model="policyForm.status" 
            :options="statusOptions" 
            optionLabel="label" 
            optionValue="value"
            class="w-full"
            :class="{ 'p-invalid': submitted && !policyForm.status }"
          />
          <small v-if="submitted && !policyForm.status" class="p-error">Status is required.</small>
        </div>
        <div class="field">
          <label for="policyContent" class="block text-sm font-medium text-gray-700 mb-1">Policy Content</label>
          <Editor 
            v-model="policyForm.content" 
            editorStyle="height: 200px"
            :class="{ 'p-invalid': submitted && !policyForm.content }"
          />
          <small v-if="submitted && !policyForm.content" class="p-error">Policy content is required.</small>
        </div>
      </div>
      <template #footer>
        <Button 
          label="Cancel" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="closeDialog"
        />
        <Button 
          :label="editingPolicy ? 'Update' : 'Save'" 
          icon="pi pi-check" 
          class="p-button-primary" 
          @click="savePolicy"
        />
      </template>
    </Dialog>

    <!-- Delete Confirmation Dialog -->
    <Dialog 
      v-model:visible="showDeleteDialog" 
      header="Confirm Deletion" 
      :modal="true" 
      :style="{ width: '450px' }"
    >
      <div class="confirmation-content">
        <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
        <span>Are you sure you want to delete <b>{{ selectedPolicy?.name }}</b>?</span>
      </div>
      <template #footer>
        <Button 
          label="No" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="showDeleteDialog = false"
        />
        <Button 
          label="Yes" 
          icon="pi pi-check" 
          class="p-button-danger" 
          @click="deletePolicy"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import { format } from 'date-fns';

type PolicyStatus = 'active' | 'inactive' | 'draft';
type Severity = 'success' | 'danger' | 'warning' | 'info' | 'contrast' | 'secondary' | undefined;

interface Policy {
  id: number;
  name: string;
  description: string;
  status: PolicyStatus;
  content: string;
  lastUpdated: string;
}

interface PolicyForm {
  id: number | null;
  name: string;
  description: string;
  status: PolicyStatus;
  content: string;
}

interface StatusOption {
  label: string;
  value: PolicyStatus;
}

// Initialize toast with proper type
const toast = useToast?.() || { add: (message: any) => console.log(message) };

// State with proper typing
const loading = ref<boolean>(false);
const policies = ref<Policy[]>([
  {
    id: 1,
    name: 'Password Policy',
    description: 'Rules for password complexity and expiration',
    status: 'active',
    content: JSON.stringify({
      minLength: 12,
      requireUppercase: true,
      requireLowercase: true,
      requireNumbers: true,
      requireSpecialChars: true,
      expirationDays: 90,
      historySize: 5
    }, null, 2),
    lastUpdated: '2025-07-01T10:30:00Z'
  },
  {
    id: 2,
    name: 'Session Timeout',
    description: 'User session timeout settings',
    status: 'active',
    content: JSON.stringify({
      timeoutMinutes: 30,
      showWarning: true,
      warningBeforeMinutes: 5
    }, null, 2),
    lastUpdated: '2025-06-15T14:20:00Z'
  },
  {
    id: 3,
    name: 'MFA Requirements',
    description: 'Multi-factor authentication settings',
    status: 'draft',
    content: JSON.stringify({
      enabled: true,
      methods: ["authenticator", "sms", "email"],
      enforceForAdmins: true,
      enforceForAllUsers: false,
      rememberDeviceDays: 30
    }, null, 2),
    lastUpdated: '2025-06-28T09:15:00Z'
  }
]);

// Form state with proper typing
const showPolicyDialog = ref<boolean>(false);
const showDeleteDialog = ref<boolean>(false);
const submitted = ref<boolean>(false);
const editingPolicy = ref<boolean>(false);
const selectedPolicy = ref<Policy | null>(null);

const policyForm = ref<PolicyForm>({
  id: null,
  name: '',
  description: '',
  status: 'draft',
  content: ''
});

const statusOptions: StatusOption[] = [
  { label: 'Active', value: 'active' },
  { label: 'Inactive', value: 'inactive' },
  { label: 'Draft', value: 'draft' }
];

// Methods
const getStatusSeverity = (status: string): Severity => {
  switch (status) {
    case 'active':
      return 'success';
    case 'inactive':
      return 'danger';
    case 'draft':
      return 'warning';
    default:
      return undefined; // Return undefined instead of null for better type safety
  }
};

const formatDateTime = (dateString: string): string => {
  if (!dateString) return '';
  return format(new Date(dateString), 'PPpp');
};

const openNew = (): void => {
  policyForm.value = {
    id: null,
    name: '',
    description: '',
    status: 'draft',
    content: ''
  };
  editingPolicy.value = false;
  submitted.value = false;
  showPolicyDialog.value = true;
};

const editPolicy = (policy: Policy): void => {
  // Create a new object that matches the PolicyForm type
  const { id, name, description, status, content } = policy;
  policyForm.value = {
    id,
    name,
    description,
    status,
    content
  } as PolicyForm;
  editingPolicy.value = true;
  submitted.value = false;
  showPolicyDialog.value = true;
};

const savePolicy = (): void => {
  submitted.value = true;
  
  if (!policyForm.value.name || !policyForm.value.description || 
      !policyForm.value.status || !policyForm.value.content) {
    return;
  }

  if (editingPolicy.value) {
    // Update existing policy
    const index = policies.value.findIndex(p => p.id === policyForm.value.id);
    if (index !== -1) {
      policies.value[index] = {
        ...policyForm.value,
        lastUpdated: new Date().toISOString()
      };
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Policy updated successfully',
        life: 3000
      });
    }
  } else {
    // Add new policy
    const newPolicy = {
      ...policyForm.value,
      id: Math.max(...policies.value.map(p => p.id), 0) + 1,
      lastUpdated: new Date().toISOString()
    };
    policies.value.push(newPolicy);
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Policy created successfully',
      life: 3000
    });
  }

  showPolicyDialog.value = false;
};

const confirmDeletePolicy = (policy: Policy): void => {
  selectedPolicy.value = policy;
  showDeleteDialog.value = true;
};

const deletePolicy = (): void => {
  if (selectedPolicy.value) {
    const policyId = selectedPolicy.value.id;
    policies.value = policies.value.filter(p => p.id !== policyId);
    showDeleteDialog.value = false;
    selectedPolicy.value = null;
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Policy deleted successfully',
      life: 3000
    });
  }
};

const closeDialog = (): void => {
  showPolicyDialog.value = false;
  submitted.value = false;
};

// Lifecycle hooks
onMounted(() => {
  // In a real app, you would fetch policies from an API here
  loading.value = true;
  setTimeout(() => {
    loading.value = false;
  }, 500);
});
</script>

<style scoped>
.confirmation-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 1rem 0;
}

:deep(.p-editor-content) {
  border: 1px solid #e2e8f0;
  border-radius: 6px;
}

:deep(.p-editor-content.ql-container) {
  border-top: 1px solid #e2e8f0 !important;
}

:deep(.p-invalid) {
  border-color: #f87171 !important;
}
</style>
