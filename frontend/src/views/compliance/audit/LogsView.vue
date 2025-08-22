<template>
  <div class="audit-logs-view">
    <div class="flex justify-content-between align-items-center mb-4">
      <h1 class="text-2xl font-bold">Audit Logs</h1>
      <div class="flex gap-2">
        <Button
          icon="pi pi-sync"
          class="p-button-rounded p-button-text"
          :loading="loading"
          @click="fetchLogs"
          v-tooltip.top="'Refresh logs'"
        />
        <Button
          label="Export"
          icon="pi pi-download"
          class="p-button-outlined"
          @click="exportLogs"
          :disabled="!logs || logs.length === 0"
        />
      </div>
    </div>

    <!-- Filters -->
    <Card class="mb-6">
      <template #content>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div class="field">
            <label class="block text-sm font-medium text-gray-700 mb-1">Action Type</label>
            <Dropdown 
              v-model="filters.actionType" 
              :options="actionTypes" 
              optionLabel="label" 
              optionValue="value"
              placeholder="All Actions"
              class="w-full"
              :showClear="true"
            />
          </div>
          <div class="field">
            <label class="block text-sm font-medium text-gray-700 mb-1">User</label>
            <Dropdown 
              v-model="filters.userId" 
              :options="users" 
              optionLabel="name" 
              optionValue="id"
              placeholder="All Users"
              class="w-full"
              :showClear="true"
              :filter="true"
            />
          </div>
          <div class="field">
            <label class="block text-sm font-medium text-gray-700 mb-1">Date Range</label>
            <Calendar 
              v-model="dateRange" 
              selectionMode="range" 
              :manualInput="false"
              class="w-full"
              :showIcon="true"
              dateFormat="yy-mm-dd"
              :showButtonBar="true"
            />
          </div>
          <div class="field flex items-end">
            <Button 
              icon="pi pi-search" 
              label="Search" 
              class="w-full"
              @click="fetchLogs"
              :loading="loading"
            />
          </div>
        </div>
      </template>
    </Card>

    <!-- Logs Table -->
    <Card>
      <template #content>
        <div class="relative overflow-x-auto">
          <DataTable
            :value="logs"
            :paginator="true"
            :rows="pagination.rows"
            :totalRecords="pagination.total"
            :loading="loading"
            :lazy="true"
            :scrollable="true"
            scrollHeight="flex"
            :resizableColumns="true"
            columnResizeMode="expand"
            :rowHover="true"
            :autoLayout="true"
            :rowsPerPageOptions="[10, 25, 50, 100]"
            @page="onPageChange"
            class="p-datatable-sm"
            data-key="id"
          >
            <Column field="timestamp" header="Date/Time" :sortable="true">
              <template #body="{ data }">
                {{ formatDateTime(data.timestamp) }}
              </template>
            </Column>
            <Column field="user.name" header="User" :sortable="true">
              <template #body="{ data }">
                <div class="flex items-center">
                  <Avatar 
                    :label="getInitials(data.user?.name || 'SYSTEM')" 
                    :style="{
                      backgroundColor: stringToColor(data.user?.name || 'SYSTEM'),
                      color: 'white'
                    }"
                    shape="circle"
                    size="normal"
                    class="mr-2"
                  />
                  {{ data.user?.name || 'System' }}
                </div>
              </template>
            </Column>
            <Column field="action" header="Action" :sortable="true" style="min-width: 120px">
              <template #body="{ data }">
                <Tag
                  :value="data.action"
                  :severity="getActionSeverity(data.action)"
                  :style="{
                    textTransform: 'capitalize',
                    minWidth: '80px',
                    textAlign: 'center',
                    padding: '0.25rem 0.5rem',
                    borderRadius: '4px',
                    fontWeight: 'bold',
                    fontSize: '0.8rem',
                    letterSpacing: '0.5px'
                  }"
                />
              </template>
            </Column>
            <Column field="entityType" header="Entity" :sortable="true">
              <template #body="{ data }">
                {{ formatEntityType(data.entityType) }}
              </template>
            </Column>
            <Column field="entityId" header="Entity ID" :sortable="true">
              <template #body="{ data }">
                <Button 
                  v-if="data.entityId"
                  :label="data.entityId" 
                  class="p-button-text p-button-sm"
                  @click="viewEntityDetails(data)"
                />
                <span v-else>-</span>
              </template>
            </Column>
            <Column field="ipAddress" header="IP Address" :sortable="true" />
            <Column header="Details" style="width: 150px">
              <template #body="{ data }">
                <Button 
                  icon="pi pi-eye" 
                  class="p-button-text p-button-sm"
                  @click="viewDetails(data)"
                  v-tooltip.top="'View Details'"
                />
              </template>
            </Column>
          </DataTable>
        </div>
      </template>
    </Card>

    <!-- Log Details Dialog -->
    <Dialog 
      v-model:visible="showDetailsDialog" 
      :style="{ width: '600px' }" 
      header="Audit Log Details"
      :modal="true"
      :dismissableMask="true"
    >
      <div v-if="selectedLog" class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <p class="text-sm font-medium text-gray-500">Timestamp</p>
            <p class="text-sm">{{ formatDateTime(selectedLog.timestamp) }}</p>
          </div>
          <div>
            <p class="text-sm font-medium text-gray-500">Action</p>
            <p class="text-sm">
              <Tag 
                :value="formatAction(selectedLog.action)" 
                :severity="getActionSeverity(selectedLog.action)"
                class="capitalize"
              />
            </p>
          </div>
          <div>
            <p class="text-sm font-medium text-gray-500">User</p>
            <p class="text-sm">{{ selectedLog.user?.name || 'System' }}</p>
          </div>
          <div>
            <p class="text-sm font-medium text-gray-500">IP Address</p>
            <p class="text-sm">{{ selectedLog.ipAddress || '-' }}</p>
          </div>
          <div>
            <p class="text-sm font-medium text-gray-500">Entity Type</p>
            <p class="text-sm">{{ formatEntityType(selectedLog.entityType) || '-' }}</p>
          </div>
          <div>
            <p class="text-sm font-medium text-gray-500">Entity ID</p>
            <p class="text-sm">{{ selectedLog.entityId || '-' }}</p>
          </div>
        </div>
        
        <Divider />
        
        <div>
          <p class="text-sm font-medium text-gray-500 mb-2">Changes</p>
          <div v-if="selectedLog.changes && selectedLog.changes.length > 0">
            <div v-for="(change, index) in selectedLog.changes" :key="index" class="mb-3">
              <p class="text-sm font-medium">{{ change.field }}</p>
              <div class="flex items-center gap-2 text-sm">
                <div class="flex-1 p-2 bg-red-50 rounded">
                  <p class="text-xs text-gray-500">Old Value</p>
                  <p class="break-all">{{ formatChangeValue(change.oldValue) }}</p>
                </div>
                <i class="pi pi-arrow-right text-gray-400"></i>
                <div class="flex-1 p-2 bg-green-50 rounded">
                  <p class="text-xs text-gray-500">New Value</p>
                  <p class="break-all">{{ formatChangeValue(change.newValue) }}</p>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="text-sm text-gray-500 italic">
            No detailed changes recorded
          </div>
        </div>
      </div>
      <template #footer>
        <Button 
          label="Close" 
          icon="pi pi-times" 
          class="p-button-text"
          @click="showDetailsDialog = false"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import type { RouteLocationNormalizedLoaded, Router } from 'vue-router';
import { useToast } from 'vue/usetoast';
import { format, parseISO } from 'date-fns';

// Types and Interfaces
interface User {
  id: string;
  name: string;
  email?: string;
  role?: string;
}

interface AuditLog {
  id: string;
  timestamp: string;
  action: string;
  user: User | null;
  entityType: string;
  entityId: string | null;
  ipAddress: string | null;
  userAgent?: string;
  changes?: Array<{
    field: string;
    oldValue: any;
    newValue: any;
  }>;
  status?: 'success' | 'failed' | 'pending';
  details?: Record<string, any>;
}

interface ActionType {
  label: string;
  value: string;
}

interface PaginationState {
  first: number;
  rows: number;
  total: number;
  sortField: string;
  sortOrder: 1 | -1;
}

interface Filters {
  actionType: string | null;
  userId: string | null;
  startDate: Date | null;
  endDate: Date | null;
  search: string;
}

// Initialize composables with proper type safety
// i18n is available but not used in this component yet
const toast = useToast?.() || { add: console.log }; // Fallback for toast

// Router and route - properly typed and marked as unused
// @ts-ignore - Router types are available at runtime
const _route = useRoute?.() as RouteLocationNormalizedLoaded | undefined;
// @ts-ignore - Router types are available at runtime
const _router = useRouter?.() as Router | undefined;

// State
const loading = ref<boolean>(false);
const exporting = ref<boolean>(false);
const showDetailsDialog = ref<boolean>(false);
const selectedLog = ref<AuditLog | null>(null);

// Data
const logs = ref<AuditLog[]>([]);
const users = ref<User[]>([]);
const actionTypes: ActionType[] = [
  { label: 'Create', value: 'CREATE' },
  { label: 'Update', value: 'UPDATE' },
  { label: 'Delete', value: 'DELETE' },
  { label: 'Login', value: 'LOGIN' },
  { label: 'Logout', value: 'LOGOUT' },
  { label: 'Export', value: 'EXPORT' },
  { label: 'Import', value: 'IMPORT' },
  { label: 'Access Denied', value: 'ACCESS_DENIED' },
];

// Filters with proper typing
const filters = ref<Filters>({
  actionType: null,
  userId: null,
  startDate: null,
  endDate: null,
  search: ''
});

const dateRange = ref<[Date, Date] | null>(null);

// Pagination with proper typing
const pagination = ref<PaginationState>({
  first: 0,
  rows: 10,
  total: 0,
  sortField: 'timestamp',
  sortOrder: -1
});

// Methods
const fetchLogs = async (): Promise<void> => {
  try {
    loading.value = true;
    
    // Update date range from the date picker
    if (dateRange.value && dateRange.value.length === 2) {
      filters.value.startDate = dateRange.value[0];
      filters.value.endDate = dateRange.value[1];
    } else {
      filters.value.startDate = null;
      filters.value.endDate = null;
    }
    
    // Simulate API call with mock data
    await new Promise(resolve => setTimeout(resolve, 800));
    
    // Mock data - in a real app, this would be an API call
    const mockLogs = generateMockLogs(100);
    
    // Apply filters
    let filteredLogs = [...mockLogs];
    
    if (filters.value.actionType) {
      filteredLogs = filteredLogs.filter(log => log.action === filters.value.actionType);
    }
    
    if (filters.value.userId) {
      filteredLogs = filteredLogs.filter(log => log.user?.id === filters.value.userId);
    }
    
    if (filters.value.startDate) {
      const start = new Date(filters.value.startDate);
      start.setHours(0, 0, 0, 0);
      filteredLogs = filteredLogs.filter(log => new Date(log.timestamp) >= start);
    }
    
    if (filters.value.endDate) {
      const end = new Date(filters.value.endDate);
      end.setHours(23, 59, 59, 999);
      filteredLogs = filteredLogs.filter(log => new Date(log.timestamp) <= end);
    }
    
    if (filters.value.search) {
      const searchLower = filters.value.search.toLowerCase();
      filteredLogs = filteredLogs.filter(log => 
        (log.user?.name?.toLowerCase().includes(searchLower)) ||
        (log.entityType?.toLowerCase().includes(searchLower)) ||
        (log.entityId?.toLowerCase().includes(searchLower)) ||
        (log.ipAddress?.toLowerCase().includes(searchLower)) ||
        (log.action?.toLowerCase().includes(searchLower))
      );
    }
    
    // Sort
    filteredLogs.sort((a, b) => {
      if (pagination.value.sortOrder === 1) {
        return a[pagination.value.sortField] > b[pagination.value.sortField] ? 1 : -1;
      } else {
        return a[pagination.value.sortField] < b[pagination.value.sortField] ? 1 : -1;
      }
    });
    
    // Apply pagination
    const start = pagination.value.first;
    const end = start + pagination.value.rows;
    
    logs.value = filteredLogs.slice(start, end);
    pagination.value.total = filteredLogs.length;
    
  } catch (error) {
    console.error('Failed to fetch audit logs:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load audit logs. Please try again.',
      life: 5000
    });
  } finally {
    loading.value = false;
  }
};

const fetchUsers = async () => {
  // In a real app, this would be an API call to get users with audit access
  users.value = [
    { id: '1', name: 'John Doe' },
    { id: '2', name: 'Jane Smith' },
    { id: '3', name: 'Admin User' },
    { id: '4', name: 'System' },
  ];
};

const exportLogs = async () => {
  try {
    exporting.value = true;
    // Simulate export
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // In a real app, this would generate and download a CSV/Excel file
    toast.add({
      severity: 'success',
      summary: 'Export Started',
      detail: 'Your export has been queued. You will receive an email when ready.',
      life: 5000
    });
  } catch (error) {
    console.error('Export failed:', error);
    toast.add({
      severity: 'error',
      summary: 'Export Failed',
      detail: 'Failed to export audit logs. Please try again.',
      life: 5000
    });
  } finally {
    exporting.value = false;
  }
};

const viewDetails = (log: AuditLog): void => {
  selectedLog.value = log;
  showDetailsDialog.value = true;
};

const viewEntityDetails = (log: AuditLog): void => {
  if (!log.entityType || !log.entityId) return;
  
  // This would navigate to the entity details page in a real app
  console.log(`Viewing ${log.entityType} with ID: ${log.entityId}`);
  
  // Show a toast notification with proper type checking
  const toastInstance = toast as { add: (options: { severity: string; summary: string; detail: string; life: number }) => void };
  toastInstance.add({
    severity: 'info',
    summary: 'Viewing Entity',
    detail: `Would navigate to ${log.entityType} with ID: ${log.entityId}`,
    life: 3000
  });
};

interface PageEvent {
  first: number;
  rows: number;
  page: number;
  pageCount: number;
}

const onPageChange = (event: PageEvent): void => {
  if (event) {
    pagination.value.first = event.first;
    pagination.value.rows = event.rows;
    fetchLogs();
  }
};

// Formatting helpers
const formatDateTime = (dateString: string): string => {
  try {
    return format(parseISO(dateString), 'PPpp');
  } catch (e) {
    console.error('Error formatting date:', e);
    return dateString;
  }
};

const formatAction = (action: string): string => {
  return action.toLowerCase()
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

const formatEntityType = (type: string): string => {
  if (!type) return '-';
  return type
    .replace(/([a-z])([A-Z])/g, '$1 $2')
    .replace(/\b\w/g, char => char.toUpperCase());
};

type Severity = 'success' | 'info' | 'warning' | 'danger' | 'contrast' | 'secondary';

const getActionSeverity = (action: string): Severity => {
  const severityMap: Record<string, Severity> = {
    'CREATE': 'success',
    'UPDATE': 'info',
    'DELETE': 'danger',
    'LOGIN': 'success',
    'LOGOUT': 'info',
    'ACCESS_DENIED': 'warning',
    'EXPORT': 'secondary',
    'IMPORT': 'secondary'
  };
  
  return severityMap[action] ?? 'contrast';
};

const getInitials = (name: string): string => {
  if (!name || typeof name !== 'string') return '??';
  const parts = name.trim().split(/\s+/);
  if (parts.length === 0) return '??';
  return parts
    .slice(0, 2)
    .map(part => part[0]?.toUpperCase() ?? '')
    .join('');
};

const stringToColor = (str: string): string => {
  if (!str) return '#6c757d'; // Default gray color
  
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }
  
  // Use HSL for better color distribution
  const hue = Math.abs(hash % 360);
  // Use a fixed saturation and lightness for better contrast
  return `hsl(${hue}, 70%, 45%)`;
};

const formatChangeValue = (value: unknown): string => {
  if (value === null) return 'null';
  if (value === undefined) return 'undefined';
  if (typeof value === 'object') {
    try {
      return JSON.stringify(value, null, 2);
    } catch (e) {
      return '[Complex Object]';
    }
  }
  return String(value);
};

// Mock data generator
const generateMockLogs = (count: number): AuditLog[] => {
  const actions = ['CREATE', 'UPDATE', 'DELETE', 'LOGIN', 'LOGOUT', 'EXPORT', 'IMPORT', 'ACCESS_DENIED'] as const;
  const entities = ['USER', 'ROLE', 'DOCUMENT', 'INVOICE', 'PAYMENT', 'SETTING', 'POLICY'] as const;
  const mockUsers: User[] = [
    { id: '1', name: 'John Doe', email: 'john@example.com', role: 'Admin' },
    { id: '2', name: 'Jane Smith', email: 'jane@example.com', role: 'Manager' },
    { id: '3', name: 'Admin User', email: 'admin@example.com', role: 'Admin' },
    { id: '4', name: 'System', role: 'System' },
  ];

  const mockLogs: AuditLog[] = [];
  const now = new Date();
  
  for (let i = 0; i < count; i++) {
    const action = actions[Math.floor(Math.random() * actions.length)];
    const user = Math.random() > 0.1 ? mockUsers[Math.floor(Math.random() * mockUsers.length)] : null;
    const entityType = Math.random() > 0.3 ? entities[Math.floor(Math.random() * entities.length)] : 'SYSTEM';
    
    const log: AuditLog = {
      id: `log-${i + 1}`,
      timestamp: new Date(now.getTime() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
      action,
      user,
      entityType,
      entityId: entityType !== 'SYSTEM' ? `id-${Math.floor(Math.random() * 1000)}` : null,
      ipAddress: Math.random() > 0.2 ? `${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}` : null,
      userAgent: Math.random() > 0.3 ? 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36' : undefined,
      status: Math.random() > 0.1 ? 'success' : 'failed',
      changes: []
    };

    if (Math.random() > 0.5) {
      log.changes = [
        { field: 'status', oldValue: 'inactive', newValue: 'active' },
        { field: 'lastUpdated', oldValue: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(), newValue: new Date().toISOString() }
      ];
    }

    mockLogs.push(log);
  }

  // Sort by timestamp descending
  return mockLogs.sort((a: AuditLog, b: AuditLog) => 
    new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  );
};

// Lifecycle hooks
onMounted(async () => {
  try {
    await Promise.all([
      fetchUsers(),
      fetchLogs()
    ]);
  } catch (error) {
    console.error('Error initializing component:', error);
    const toastInstance = toast as { add: (options: { severity: string; summary: string; detail: string; life: number }) => void };
    toastInstance.add({
      severity: 'error',
      summary: 'Initialization Error',
      detail: 'Failed to initialize component data',
      life: 5000
    });
  }
});

// Watch for filter changes
watch(
  [
    () => filters.value.actionType,
    () => filters.value.userId,
    () => filters.value.startDate,
    () => filters.value.endDate,
    () => filters.value.search
  ],
  () => {
    // Reset to first page when filters change
    pagination.value.first = 0;
    fetchLogs();
  },
  { deep: true }
);

// Watch for filter changes
watch([() => filters.value, () => pagination.value], () => {
  fetchLogs();
}, { deep: true });
</script>

<style scoped>
.audit-logs-view {
  padding: 1rem;
}

:deep(.p-datatable) {
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
}

:deep(.p-datatable-thead > tr > th) {
  background-color: #f9fafb;
  color: #4b5563;
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.05em;
}

:deep(.p-datatable-tbody > tr) {
  border-bottom: 1px solid #f3f4f6;
  transition: background-color 150ms ease-in-out;
}

:deep(.p-datatable-tbody > tr:hover) {
  background-color: #f9fafb;
}

:deep(.p-paginator) {
  border-top: 1px solid #e5e7eb;
  background-color: white;
  border-bottom-left-radius: 0.5rem;
  border-bottom-right-radius: 0.5rem;
}

:deep(.p-paginator .p-paginator-pages .p-paginator-page.p-highlight) {
  background-color: #3b82f6;
  color: white;
}

:deep(.p-datatable .p-sortable-column:not(.p-highlight):hover) {
  background-color: #f3f4f6;
  color: #374151;
}

:deep(.p-datatable .p-sortable-column.p-highlight) {
  background-color: #f3f4f6;
  color: #111827;
}
</style>
