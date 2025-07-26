<template>
  <div class="data-subject-requests">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center md:justify-between mb-6 gap-4">
      <div>
        <h1 class="text-2xl font-semibold text-gray-900">Data Subject Requests</h1>
        <p class="text-gray-600">Manage GDPR/CCPA data subject requests</p>
      </div>
      <Button 
        icon="pi pi-plus" 
        label="New Request" 
        @click="showNewRequestDialog = true"
      />
    </div>

    <!-- Filters -->
    <Card class="mb-6">
      <template #content>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="field">
            <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <MultiSelect 
              v-model="filters.statuses" 
              :options="requestStatuses"
              optionLabel="label" 
              optionValue="value"
              placeholder="All Statuses"
              class="w-full"
              display="chip"
            />
          </div>
          <div class="field">
            <label class="block text-sm font-medium text-gray-700 mb-1">Request Type</label>
            <MultiSelect 
              v-model="filters.types" 
              :options="requestTypes"
              optionLabel="label" 
              optionValue="value"
              placeholder="All Types"
              class="w-full"
              display="chip"
            />
          </div>
          <div class="field flex items-end">
            <Button 
              icon="pi pi-filter" 
              label="Apply Filters" 
              class="w-full"
              @click="fetchRequests"
              :loading="loading"
            />
          </div>
        </div>
      </template>
    </Card>

    <!-- Requests Table -->
    <Card>
      <template #content>
        <DataTable 
          :value="requests" 
          :paginator="true" 
          :rows="10"
          :totalRecords="totalRecords"
          :loading="loading"
          v-model:first="first"
          @page="onPageChange($event)"
          :scrollable="true"
          scrollHeight="flex"
          class="p-datatable-sm"
          :selection.sync="selectedRequests"
          dataKey="id"
        >
          <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>
          
          <Column field="id" header="ID" :sortable="true">
            <template #body="{ data }">
              <Button 
                :label="data.id" 
                class="p-button-text p-0"
                @click="viewRequestDetails(data)"
              />
            </template>
          </Column>
          
          <Column field="type" header="Type" :sortable="true">
            <template #body="{ data }">
              <Tag 
                :value="formatRequestType(data.type)" 
                :severity="getRequestTypeSeverity(data.type)"
                class="capitalize"
              />
            </template>
          </Column>
          
          <Column field="status" header="Status" :sortable="true">
            <template #body="{ data }">
              <Tag 
                :value="formatStatus(data.status)" 
                :severity="getStatusSeverity(data.status)"
                class="capitalize"
              />
            </template>
          </Column>
          
          <Column field="subjectName" header="Subject" :sortable="true" />
          <Column field="subjectEmail" header="Email" :sortable="true" />
          
          <Column field="createdAt" header="Requested" :sortable="true">
            <template #body="{ data }">
              {{ formatDate(data.createdAt) }}
            </template>
          </Column>
          
          <Column field="dueDate" header="Due Date" :sortable="true">
            <template #body="{ data }">
              <span :class="{ 'text-red-600 font-medium': isOverdue(data) }">
                {{ formatDate(data.dueDate) }}
              </span>
            </template>
          </Column>
          
          <Column headerStyle="width: 5rem; text-align: center">
            <template #body="{ data }">
              <Button 
                icon="pi pi-ellipsis-v" 
                class="p-button-text p-button-sm"
                @click="toggleActionMenu($event, data)"
                v-tooltip.top="'Actions'"
                aria-haspopup="true"
                :aria-controls="'menu-' + data.id"
              />
              <Menu 
                :id="'menu-' + data.id"
                :ref="'menu' + data.id"
                :model="getActionMenuItems(data)" 
                :popup="true"
              />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <!-- New Request Dialog -->
    <Dialog 
      v-model:visible="showNewRequestDialog" 
      header="New Data Subject Request"
      :style="{ width: '600px' }"
      :modal="true"
    >
      <div class="p-fluid">
        <div class="field">
          <label for="requestType" class="font-medium">Request Type <span class="text-red-500">*</span></label>
          <Dropdown 
            id="requestType"
            v-model="newRequest.type" 
            :options="requestTypes"
            optionLabel="label" 
            optionValue="value"
            placeholder="Select request type"
            class="w-full"
            :class="{ 'p-invalid': submitted && !newRequest.type }"
          />
          <small v-if="submitted && !newRequest.type" class="p-error">Request type is required</small>
        </div>
        
        <div class="field">
          <label for="subjectName" class="font-medium">Subject Name <span class="text-red-500">*</span></label>
          <InputText 
            id="subjectName"
            v-model.trim="newRequest.subjectName" 
            placeholder="Enter subject name"
            class="w-full"
            :class="{ 'p-invalid': submitted && !newRequest.subjectName }"
          />
        </div>
        
        <div class="field">
          <label for="subjectEmail" class="font-medium">Email Address <span class="text-red-500">*</span></label>
          <InputText 
            id="subjectEmail"
            v-model.trim="newRequest.subjectEmail" 
            placeholder="Enter email address"
            class="w-full"
            :class="{ 'p-invalid': submitted && !isValidEmail(newRequest.subjectEmail) }"
          />
        </div>
        
        <div class="field">
          <label for="description" class="font-medium">Description</label>
          <Textarea 
            id="description"
            v-model="newRequest.description" 
            rows="3" 
            placeholder="Provide additional details about this request"
            class="w-full"
          />
        </div>
      </div>
      
      <template #footer>
        <Button 
          label="Cancel" 
          icon="pi pi-times" 
          class="p-button-text"
          @click="closeNewRequestDialog"
        />
        <Button 
          label="Create Request" 
          icon="pi pi-check" 
          class="p-button-primary"
          @click="createRequest"
          :loading="submitting"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useToast } from 'vue/usetoast';
import { format } from 'date-fns';

// Types
interface Document {
  id: string;
  name: string;
  url: string;
  uploadedAt: string;
}

interface DataSubjectRequest {
  id: string;
  type: 'access' | 'erasure' | 'rectification' | 'restriction' | 'portability' | 'objection' | 'other';
  status: 'pending' | 'in_progress' | 'completed' | 'rejected' | 'cancelled';
  requesterName: string;
  requesterEmail: string;
  requesterPhone?: string;
  description: string;
  submittedAt: string;
  updatedAt: string;
  dueDate: string;
  assignedTo?: string;
  notes?: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  verificationStatus: 'pending' | 'verified' | 'failed';
  documents?: Document[];
}

type RequestType = DataSubjectRequest['type'];
type RequestStatus = DataSubjectRequest['status'];
type RequestPriority = DataSubjectRequest['priority'];

interface RequestFilter {
  statuses: RequestStatus[];
  types: RequestType[];
  searchQuery: string;
  dateRange: [Date | null, Date | null];
  priority: RequestPriority | '';
}

// Component state
// State
const loading = ref<boolean>(false);
const requests = ref<DataSubjectRequest[]>([]);
const selectedRequest = ref<DataSubjectRequest | null>(null);
const showNewRequestDialog = ref<boolean>(false);
const showRequestDetailsDialog = ref<boolean>(false);
const actionMenuItems = ref<Array<{label: string; icon: string; command?: () => void; separator?: boolean}>>([]);
const actionMenuTarget = ref<EventTarget | null>(null);
const actionMenuVisible = ref<boolean>(false);
const actionMenuRequest = ref<DataSubjectRequest | null>(null);
const totalRecords = ref<number>(0);
const selectedRequests = ref<DataSubjectRequest[]>([]);
const submitted = ref<boolean>(false);
const submitting = ref<boolean>(false);

// Lazy params for data table
const lazyParams = ref({
  first: 0,
  rows: 10,
  sortField: 'submittedAt',
  sortOrder: -1 as 1 | -1,
  filters: {} as Record<string, any>
});

// Form data
const newRequest = ref<Omit<DataSubjectRequest, 'id' | 'submittedAt' | 'updatedAt'>>({
  type: 'access',
  priority: 'medium',
  status: 'pending',
  verificationStatus: 'pending',
  requesterName: '',
  requesterEmail: '',
  description: '',
  dueDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString()
});

// Filters
const filters = ref<RequestFilter>({
  statuses: [],
  types: [],
  searchQuery: '',
  dateRange: [null, null],
  priority: ''
});

// Constants
const requestTypes = [
  { label: 'Access', value: 'access' },
  { label: 'Erasure', value: 'erasure' },
  { label: 'Rectification', value: 'rectification' },
  { label: 'Restriction', value: 'restriction' },
  { label: 'Data Portability', value: 'portability' },
  { label: 'Objection', value: 'objection' },
  { label: 'Other', value: 'other' }
];

const requestStatuses = [
  { label: 'Pending', value: 'pending' },
  { label: 'In Progress', value: 'in_progress' },
  { label: 'Completed', value: 'completed' },
  { label: 'Rejected', value: 'rejected' },
  { label: 'Cancelled', value: 'cancelled' }
];

const priorityOptions = [
  { label: 'Low', value: 'low' },
  { label: 'Medium', value: 'medium' },
  { label: 'High', value: 'high' },
  { label: 'Critical', value: 'critical' }
];

// Toast
const toast = useToast();

// Computed
const filteredRequests = computed<DataSubjectRequest[]>(() => {
  return requests.value.filter(request => {
    const matchesStatus = filters.value.statuses.length === 0 || 
                         filters.value.statuses.includes(request.status);
    const matchesType = filters.value.types.length === 0 || 
                       filters.value.types.includes(request.type);
    const matchesSearch = !filters.value.searchQuery || 
                         request.requesterName.toLowerCase().includes(filters.value.searchQuery.toLowerCase()) ||
                         request.requesterEmail.toLowerCase().includes(filters.value.searchQuery.toLowerCase()) ||
                         request.description.toLowerCase().includes(filters.value.searchQuery.toLowerCase());
    const matchesPriority = !filters.value.priority || 
                           request.priority === filters.value.priority;
    
    return matchesStatus && matchesType && matchesSearch && matchesPriority;
  });
});

// Methods
const fetchRequests = async (): Promise<void> => {
  loading.value = true;
  try {
    // In a real app, you would call an API here
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Mock data
    requests.value = [
      {
        id: 'DSR-001',
        type: 'access',
        status: 'pending',
        requesterName: 'John Doe',
        requesterEmail: 'john@example.com',
        description: 'Requesting a copy of all personal data',
        submittedAt: '2025-07-01T10:30:00Z',
        updatedAt: '2025-07-01T10:30:00Z',
        dueDate: '2025-07-15T23:59:59Z',
        priority: 'high',
        verificationStatus: 'pending'
      },
      {
        id: 'DSR-002',
        type: 'erasure',
        status: 'in_progress',
        requesterName: 'Jane Smith',
        requesterEmail: 'jane@example.com',
        description: 'Request to be forgotten',
        submittedAt: '2025-06-28T14:15:00Z',
        updatedAt: '2025-06-29T09:45:00Z',
        dueDate: '2025-07-12T23:59:59Z',
        priority: 'critical',
        verificationStatus: 'verified',
        assignedTo: 'admin@example.com'
      }
    ];
    
    totalRecords.value = requests.value.length;
  } catch (error) {
    console.error('Error fetching requests:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to fetch data subject requests',
      life: 5000
    });
  } finally {
    loading.value = false;
  }
};

const createRequest = async (): Promise<void> => {
  const submitting = ref<boolean>(false);
  const submitted = ref<boolean>(false);
  
  submitted.value = true;
  
  // Validate form
  if (!newRequest.value.type || !newRequest.value.requesterName || !isValidEmail(newRequest.value.requesterEmail)) {
    return;
  }
  
  submitting.value = true;
  
  try {
    // In a real app, you would call an API here
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Reset form
    closeNewRequestDialog();
    
    // Refresh requests
    await fetchRequests();
    
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Data subject request created successfully',
      life: 5000
    });
  } catch (error) {
    console.error('Error creating request:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to create data subject request',
      life: 5000
    });
  } finally {
    submitting.value = false;
  }
};

const closeNewRequestDialog = (): void => {
  showNewRequestDialog.value = false;
  // Reset form
  newRequest.value = {
    type: 'access',
    priority: 'medium',
    status: 'pending',
    verificationStatus: 'pending'
  };
};

const viewRequestDetails = (request: DataSubjectRequest): void => {
  selectedRequest.value = request;
  showRequestDetailsDialog.value = true;
};

const toggleActionMenu = (event: Event, request: DataSubjectRequest): void => {
  actionMenuTarget.value = event.currentTarget;
  actionMenuRequest.value = request;
  actionMenuItems.value = getActionMenuItems(request);
  actionMenuVisible.value = true;
};

const getActionMenuItems = (request: DataSubjectRequest): any[] => {
  const items = [
    {
      label: 'View Details',
      icon: 'pi pi-eye',
      command: () => viewRequestDetails(request)
    }
  ];
  
  if (request.status === 'pending' || request.status === 'in_progress') {
    items.push(
      {
        label: 'Mark as In Progress',
        icon: 'pi pi-spin pi-cog',
        command: () => updateRequestStatus(request, 'in_progress')
      },
      {
        label: 'Mark as Completed',
        icon: 'pi pi-check',
        command: () => updateRequestStatus(request, 'completed')
      },
      {
        label: 'Reject Request',
        icon: 'pi pi-times',
        command: () => updateRequestStatus(request, 'rejected')
      }
    );
  }
  
  return items;
};

const updateRequestStatus = async (request: DataSubjectRequest, status: RequestStatus): Promise<void> => {
  try {
    // In a real app, you would call an API here
    await new Promise(resolve => setTimeout(resolve, 500));
    
    const index = requests.value.findIndex(r => r.id === request.id);
    if (index !== -1) {
      requests.value[index] = {
        ...requests.value[index],
        status,
        updatedAt: new Date().toISOString()
      };
      
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: `Request marked as ${status.replace('_', ' ')}`,
        life: 3000
      });
    }
  } catch (error) {
    console.error('Error updating request status:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to update request status',
      life: 5000
    });
  }
};

// Utility functions
const formatDate = (dateString: string, formatStr = 'PP'): string => {
  if (!dateString) return 'N/A';
  try {
    return format(new Date(dateString), formatStr);
  } catch (e) {
    console.error('Error formatting date:', e);
    return 'Invalid date';
  }
};

const formatRequestType = (type: RequestType): string => {
  const typeMap: Record<RequestType, string> = {
    access: 'Access',
    erasure: 'Erasure',
    rectification: 'Rectification',
    restriction: 'Restriction',
    portability: 'Data Portability',
    objection: 'Objection',
    other: 'Other'
  };
  return typeMap[type] || type;
};

const formatStatus = (status: RequestStatus): string => {
  const statusMap: Record<RequestStatus, string> = {
    pending: 'Pending',
    in_progress: 'In Progress',
    completed: 'Completed',
    rejected: 'Rejected',
    cancelled: 'Cancelled'
  };
  return statusMap[status] || status;
};

const getRequestTypeSeverity = (type: RequestType): 'info' | 'danger' | 'warning' | 'secondary' => {
  const severityMap: Record<RequestType, 'info' | 'danger' | 'warning' | 'secondary'> = {
    access: 'info',
    erasure: 'danger',
    rectification: 'warning',
    restriction: 'warning',
    portability: 'info',
    objection: 'warning',
    other: 'secondary'
  };
  return severityMap[type] || 'info';
};

const getStatusSeverity = (status: RequestStatus): 'info' | 'primary' | 'success' | 'danger' | 'secondary' => {
  const severityMap: Record<RequestStatus, 'info' | 'primary' | 'success' | 'danger' | 'secondary'> = {
    pending: 'info',
    in_progress: 'primary',
    completed: 'success',
    rejected: 'danger',
    cancelled: 'secondary'
  };
  return severityMap[status] || 'info';
};

const isOverdue = (request: DataSubjectRequest): boolean => {
  if (!request.dueDate) return false;
  const dueDate = new Date(request.dueDate);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return dueDate < today && 
         request.status !== 'completed' && 
         request.status !== 'rejected' && 
         request.status !== 'cancelled';
};

const isValidEmail = (email: string): boolean => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
};

const onPageChange = (event: any): void => {
  lazyParams.value = event;
  fetchRequests();
};

// Lifecycle hooks
onMounted(() => {
  fetchRequests();
});

// Expose methods and state to template if needed
const exposeToTemplate = {
  fetchRequests,
  createRequest,
  viewRequestDetails,
  toggleActionMenu,
  formatDate,
  formatRequestType,
  formatStatus,
  getRequestTypeSeverity,
  getStatusSeverity,
  isOverdue,
  isValidEmail
};

// Only expose in development
if (import.meta.env.DEV) {
  defineExpose(exposeToTemplate);
}
</script>

<style scoped>
.data-subject-requests {
  @apply p-4 md:p-6;
}

:deep(.p-datatable) {
  @apply border border-gray-200 rounded-lg overflow-hidden;
}

:deep(.p-datatable thead th) {
  @apply bg-gray-50 text-gray-700 font-semibold text-xs uppercase tracking-wider;
}

:deep(.p-datatable-tbody > tr) {
  @apply border-b border-gray-200;
}

:deep(.p-datatable-tbody > tr:last-child) {
  @apply border-b-0;
}

:deep(.p-paginator) {
  @apply border-t border-gray-200 bg-white;
}

:deep(.p-datatable .p-sortable-column.p-highlight) {
  @apply text-blue-600 bg-blue-50;
}

:deep(.p-datatable .p-sortable-column:not(.p-highlight):hover) {
  @apply bg-gray-100;
}
</style>
