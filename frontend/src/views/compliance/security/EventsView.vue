<template>
  <div class="security-events">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center md:justify-between mb-6 gap-4">
      <div>
        <h1 class="text-2xl font-semibold text-gray-900">Security Events</h1>
        <p class="text-gray-600">Monitor and investigate security-related events</p>
      </div>
      <div class="flex gap-3">
        <Button 
          icon="pi pi-filter" 
          :label="`Filters ${activeFiltersCount > 0 ? `(${activeFiltersCount})` : ''}" 
          class="p-button-outlined p-button-sm"
          :class="{ 'p-button-primary': activeFiltersCount > 0 }"
          @click="showFilters = !showFilters"
        />
        <Button 
          icon="pi pi-download" 
          label="Export" 
          class="p-button-outlined p-button-sm"
          @click="showExportDialog = true"
          :loading="exportLoading"
        />
      </div>
    </div>

    <!-- Filters Panel -->
    <Card v-if="showFilters" class="mb-6">
      <template #title>
        <div class="flex justify-between items-center">
          <span>Filters</span>
          <Button 
            icon="pi pi-times" 
            class="p-button-text p-button-rounded p-button-sm" 
            @click="showFilters = false"
          />
        </div>
      </template>
      <template #content>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
          <!-- Event Type Filter -->
          <div class="field">
            <label for="eventType" class="block text-sm font-medium text-gray-700 mb-1">Event Type</label>
            <Dropdown 
              id="eventType"
              v-model="filters.eventType" 
              :options="eventTypes" 
              optionLabel="name" 
              optionValue="value"
              placeholder="Select event type"
              class="w-full"
              showClear
            />
          </div>
          
          <!-- Severity Filter -->
          <div class="field">
            <label for="severity" class="block text-sm font-medium text-gray-700 mb-1">Severity</label>
            <Dropdown 
              id="severity"
              v-model="filters.severity" 
              :options="severityLevels" 
              optionLabel="name" 
              optionValue="value"
              placeholder="Select severity"
              class="w-full"
              showClear
            />
          </div>
          
          <!-- Status Filter -->
          <div class="field">
            <label for="status" class="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <Dropdown 
              id="status"
              v-model="filters.status" 
              :options="eventStatuses" 
              optionLabel="name" 
              optionValue="value"
              placeholder="Select status"
              class="w-full"
              showClear
            />
          </div>
          
          <!-- Date Range Filter -->
          <div class="field">
            <label for="dateRange" class="block text-sm font-medium text-gray-700 mb-1">Date Range</label>
            <Calendar 
              id="dateRange"
              v-model="filters.dateRange" 
              selectionMode="range" 
              :manualInput="false"
              class="w-full"
              placeholder="Select date range"
              :showIcon="true"
              dateFormat="yy-mm-dd"
              :showButtonBar="true"
            />
          </div>
          
          <!-- Source Filter -->
          <div class="field">
            <label for="source" class="block text-sm font-medium text-gray-700 mb-1">Source</label>
            <Dropdown 
              id="source"
              v-model="filters.source" 
              :options="sources" 
              optionLabel="name" 
              optionValue="value"
              placeholder="Select source"
              class="w-full"
              showClear
            />
          </div>
          
          <!-- Search Query -->
          <div class="field">
            <label for="searchQuery" class="block text-sm font-medium text-gray-700 mb-1">Search</label>
            <span class="p-input-icon-left w-full">
              <i class="pi pi-search" />
              <InputText 
                id="searchQuery"
                v-model="filters.searchQuery" 
                placeholder="Search events..."
                class="w-full"
                @keyup.enter="onFilter"
              />
            </span>
          </div>
        </div>
        
        <!-- Filter Actions -->
        <div class="flex justify-end gap-2 mt-4">
          <Button 
            label="Clear All" 
            icon="pi pi-times"
            class="p-button-text"
            @click="clearFilters"
            :disabled="!isFiltered"
          />
          <Button 
            label="Apply Filters" 
            icon="pi pi-check"
            class="p-button-primary"
            @click="onFilter"
            :loading="loading"
          />
        </div>
      </template>
    </Card>

    <!-- Events Table -->
    <Card>
      <template #content>
        <DataTable 
          :value="events" 
          :loading="loading"
          :paginator="true"
          :rows="pagination.rows"
          :first="pagination.first"
          :totalRecords="pagination.totalRecords"
          :rowsPerPageOptions="[10, 25, 50, 100]"
          paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
          currentPageReportTemplate="Showing {first} to {last} of {totalRecords} events"
          responsiveLayout="scroll"
          @page="onPage($event)"
          @sort="onSort($event)"
          :sortField="sortState.sortField"
          :sortOrder="sortState.sortOrder"
          :scrollable="true"
          scrollHeight="flex"
          :scrollDirection="'both'"
          :resizableColumns="true"
          columnResizeMode="expand"
          showGridlines
          stripedRows
          class="p-datatable-sm"
          data-key="id"
        >
          <!-- Timestamp Column -->
          <Column 
            field="timestamp" 
            header="Timestamp" 
            :sortable="true"
            :style="{ minWidth: '160px' }"
          >
            <template #body="{ data }">
              <div class="flex flex-col">
                <span class="font-medium">{{ formatDate(data.timestamp) }}</span>
                <span class="text-xs text-gray-500">{{ formatTime(data.timestamp) }}</span>
              </div>
            </template>
          </Column>
          
          <!-- Event Type Column -->
          <Column 
            field="eventType" 
            header="Event Type" 
            :sortable="true"
            :style="{ minWidth: '180px' }"
          >
            <template #body="{ data }">
              <div class="flex items-center gap-2">
                <i :class="getEventTypeIcon(data.eventType) + ' text-sm'" />
                <span>{{ formatEventType(data.eventType) }}</span>
              </div>
            </template>
          </Column>
          
          <!-- Severity Column -->
          <Column 
            field="severity" 
            header="Severity" 
            :sortable="true"
            :style="{ minWidth: '120px' }"
          >
            <template #body="{ data }">
              <Tag 
                :value="formatSeverity(data.severity)" 
                :severity="getSeverityColor(data.severity)" 
                :icon="getSeverityIcon(data.severity)"
                :style="{ 
                  backgroundColor: getSeverityBackground(data.severity),
                  color: getSeverityTextColor(data.severity),
                  borderColor: getSeverityBorderColor(data.severity)
                }"
              />
            </template>
          </Column>
          
          <!-- Status Column -->
          <Column 
            field="status" 
            header="Status" 
            :sortable="true"
            :style="{ minWidth: '140px' }"
          >
            <template #body="{ data }">
              <Tag 
                :value="formatStatus(data.status)"
                :severity="getStatusSeverity(data.status)"
                :icon="getStatusIcon(data.status)"
              />
            </template>
          </Column>
          
          <!-- Source Column -->
          <Column 
            field="source" 
            header="Source" 
            :sortable="true"
            :style="{ minWidth: '140px' }"
          >
            <template #body="{ data }">
              <div class="flex items-center gap-2">
                <i :class="getSourceIcon(data.source) + ' text-sm'" />
                <span>{{ formatSource(data.source) }}</span>
              </div>
            </template>
          </Column>
          
          <!-- User Column -->
          <Column 
            field="user" 
            header="User" 
            :sortable="true"
            :style="{ minWidth: '200px' }"
          >
            <template #body="{ data }">
              <div v-if="data.user" class="flex items-center gap-2">
                <Avatar 
                  :label="data.user.name ? data.user.name.charAt(0).toUpperCase() : 'U'" 
                  :style="getUserAvatarStyle(data.user)"
                  shape="circle"
                  size="small"
                />
                <div class="flex flex-col">
                  <span class="font-medium">{{ data.user.name || 'Unknown User' }}</span>
                  <span class="text-xs text-gray-500">{{ data.user.email || 'No email' }}</span>
                </div>
              </div>
              <div v-else class="flex items-center gap-2 text-gray-500">
                <i class="pi pi-server text-sm" />
                <span>System</span>
              </div>
            </template>
          </Column>
          
          <!-- Details Column -->
          <Column 
            :exportable="false"
            :style="{ width: '80px', textAlign: 'center' }"
          >
            <template #body="{ data }">
              <Button 
                icon="pi pi-eye" 
                class="p-button-text p-button-sm p-button-rounded"
                @click="viewEventDetails(data)"
                v-tooltip.top="'View Details'"
              />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <!-- Event Details Dialog -->
    <Dialog 
      v-model:visible="showEventDialog" 
      :style="{ width: '700px' }" 
      header="Event Details" 
      :modal="true"
      :dismissableMask="true"
      :closable="true"
      @hide="selectedEvent = null"
    >
      <div v-if="selectedEvent" class="event-details">
        <div class="grid">
          <div class="col-12 md:col-6">
            <div class="field">
              <label>Event Type</label>
              <div class="flex align-items-center">
                <i :class="['mr-2', getEventTypeIcon(selectedEvent.eventType)]"></i>
                <span>{{ formatEventType(selectedEvent.eventType) }}</span>
              </div>
            </div>
            <div class="field">
              <label>Severity</label>
              <div class="flex align-items-center">
                <Tag 
                  :value="formatSeverity(selectedEvent.severity)" 
                  :severity="getSeverityColor(selectedEvent.severity)" 
                />
              </div>
            </div>
            <div class="field">
              <label>Status</label>
              <div class="flex align-items-center">
                <Tag 
                  :value="formatStatus(selectedEvent.status)" 
                  :severity="getStatusSeverity(selectedEvent.status)" 
                />
              </div>
            </div>
            <div class="field">
              <label>Source</label>
              <div class="flex align-items-center">
                <i :class="['mr-2', getSourceIcon(selectedEvent.source)]"></i>
                <span>{{ formatSource(selectedEvent.source) }}</span>
              </div>
            </div>
          </div>
          <div class="col-12 md:col-6">
            <div class="field">
              <label>Date & Time</label>
              <div>{{ formatDate(selectedEvent.timestamp) }}</div>
              <div class="text-500">{{ formatTime(selectedEvent.timestamp) }}</div>
            </div>
            <div class="field" v-if="selectedEvent.user">
              <label>User</label>
              <div class="flex align-items-center">
                <Avatar 
                  :label="selectedEvent.user.name.charAt(0)" 
                  :style="getUserAvatarStyle(selectedEvent.user)"
                  shape="circle" 
                  class="mr-2"
                />
                <span>{{ selectedEvent.user.name }}</span>
              </div>
            </div>
            <div class="field" v-if="selectedEvent.sourceIp">
              <label>IP Address</label>
              <div>{{ selectedEvent.sourceIp }}</div>
            </div>
          </div>
        </div>
        <Divider />
        <div class="field">
          <label>Description</label>
          <div class="p-3 border-round" :class="getSeverityBackground(selectedEvent.severity)">
            {{ selectedEvent.description }}
          </div>
        </div>
        <div class="field" v-if="selectedEvent.details">
          <label>Details</label>
          <pre class="p-3 border-round surface-100 overflow-auto" style="max-height: 200px">
            {{ formatEventDetails(selectedEvent.details) }}
          </pre>
        </div>
        <template #footer>
          <Button 
            label="Close" 
            icon="pi pi-times" 
            @click="showEventDialog = false" 
            class="p-button-text"
          />
          <Button 
            v-if="selectedEvent.status !== 'resolved'"
            label="Mark as Resolved" 
            icon="pi pi-check" 
            @click="resolveEvent(selectedEvent)" 
            class="p-button-success"
            :loading="loading"
          />
        </template>
      </div>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, watch, onUnmounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import type { DataTablePageEvent, DataTableSortEvent } from 'primevue/datatable';
import type { ToastMessageOptions } from 'primevue/toast';
import { format, parseISO } from 'date-fns';
import axios from 'axios';

// Import the security event service
import SecurityEventService from '@/services/securityEventService';

// Types
type SecurityEventSeverity = 'info' | 'low' | 'medium' | 'high' | 'critical';
type SecurityEventStatus = 'open' | 'in_progress' | 'resolved' | 'dismissed';

interface User {
  id: string;
  name: string;
  email: string;
  role: string;
  avatar?: string;
  lastLogin?: string;
  status: 'active' | 'inactive' | 'suspended';
}

interface SecurityEvent {
  id: string;
  timestamp: string;
  eventType: string;
  severity: SecurityEventSeverity;
  status: SecurityEventStatus;
  source: string;
  sourceIp?: string;
  userAgent?: string;
  userId?: string;
  user?: User;
  description: string;
  details?: Record<string, any>;
  metadata?: Record<string, any>;
  resolvedAt?: string;
  resolvedBy?: string;
  createdAt: string;
  updatedAt: string;
  location?: string;
  relatedEvents?: SecurityEvent[];
}

interface EventType {
  name: string;
  value: string;
  icon: string;
  description: string;
}

interface SeverityLevel {
  name: string;
  value: SecurityEventSeverity | '';
  color: string;
  icon: string;
}

interface EventSource {
  name: string;
  value: string;
  icon: string;
}

interface EventFilter {
  eventType?: string;
  severity?: SecurityEventSeverity | '';
  status?: SecurityEventStatus | '';
  source?: string;
  searchQuery?: string;
  dateRange?: Date[];
  startDate?: string;
  endDate?: string;
  userId?: string;
}

interface PaginationState {
  first: number;
  rows: number;
  page: number;
  pageCount: number;
  totalRecords: number;
  sortField: string;
  sortOrder: 1 | -1 | null;
}

interface SortState {
  sortField: string;
  sortOrder: 1 | -1 | null;
}

interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

// API client with proper typing
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': `Bearer ${localStorage.getItem('token')}`
  }
});

// Initialize services
const securityEventService = new SecurityEventService(apiClient);

// Initialize toast
const toast = useToast?.() || { 
  add: (options: ToastMessageOptions) => console.log('Toast:', options) 
};

// State
const events = ref<SecurityEvent[]>([]);
const loading = ref(false);
const exportLoading = ref(false);
const error = ref<string | null>(null);
const showFilters = ref(false);
const showExportDialog = ref(false);
const showEventDialog = ref(false);
const selectedEvent = ref<SecurityEvent | null>(null);

// Pagination
const pagination = reactive<PaginationState>({
  first: 0,
  rows: 10,
  page: 1,
  pageCount: 0,
  totalRecords: 0,
  sortField: 'timestamp',
  sortOrder: -1 // -1 for desc, 1 for asc
});

// Filters
const filters = reactive<EventFilter>({
  eventType: '',
  severity: '',
  status: '',
  source: '',
  searchQuery: '',
  dateRange: undefined,
  startDate: undefined,
  endDate: undefined
});

// Sort state
const sortState = reactive<SortState>({
  sortField: 'timestamp',
  sortOrder: -1
});

// Computed
const activeFiltersCount = computed(() => {
  return Object.values(filters).filter(v => 
    v !== null && 
    v !== '' && 
    !(Array.isArray(v) && v.length === 0) &&
    v !== undefined
  ).length;
});

const isFiltered = computed(() => activeFiltersCount.value > 0);

// Event types with icons and descriptions
const eventTypes: EventType[] = [
  { 
    name: 'All Types', 
    value: '',
    icon: 'pi pi-filter',
    description: 'All event types'
  },
  { 
    name: 'Authentication', 
    value: 'AUTH',
    icon: 'pi pi-key',
    description: 'User authentication related events'
  },
  { 
    name: 'Authorization', 
    value: 'AUTHZ',
    icon: 'pi pi-shield',
    description: 'Authorization and permission events'
  },
  {
    name: 'User Management',
    value: 'USER_MGMT',
    icon: 'pi pi-users',
    description: 'User account management events'
  },
  {
    name: 'Data Access',
    value: 'DATA_ACCESS',
    icon: 'pi pi-database',
    description: 'Data access and retrieval events'
  },
  {
    name: 'Configuration',
    value: 'CONFIG_CHANGE',
    icon: 'pi pi-cog',
    description: 'System configuration changes'
  },
  {
    name: 'Security',
    value: 'SECURITY',
    icon: 'pi pi-lock',
    description: 'Security-related events'
  },
  {
    name: 'System',
    value: 'SYSTEM',
    icon: 'pi pi-server',
    description: 'System-level events'
  }
];

// Severity levels with colors and icons
const severityLevels: SeverityLevel[] = [
  { 
    name: 'All Levels', 
    value: '', 
    color: 'var(--surface-500)',
    icon: 'pi pi-filter'
  },
  { 
    name: 'Info', 
    value: 'info', 
    color: 'var(--primary-color)',
    icon: 'pi pi-info-circle'
  },
  { 
    name: 'Low', 
    value: 'low', 
    color: 'var(--blue-500)',
    icon: 'pi pi-arrow-down'
  },
  { 
    name: 'Medium', 
    value: 'medium', 
    color: 'var(--yellow-500)',
    icon: 'pi pi-exclamation-triangle'
  },
  { 
    name: 'High', 
    value: 'high', 
    color: 'var(--orange-500)',
    icon: 'pi pi-exclamation-circle'
  },
  { 
    name: 'Critical', 
    value: 'critical', 
    color: 'var(--red-500)',
    icon: 'pi pi-times-circle'
  }
];

// Event sources with icons
const sources: EventSource[] = [
  { 
    name: 'All Sources', 
    value: '',
    icon: 'pi pi-filter'
  },
  { 
    name: 'Web Application', 
    value: 'web',
    icon: 'pi pi-globe'
  },
  { 
    name: 'API', 
    value: 'api',
    icon: 'pi pi-code'
  },
  { 
    name: 'Database', 
    value: 'database',
    icon: 'pi pi-database'
  },
  { 
    name: 'Authentication', 
    value: 'auth',
    icon: 'pi pi-key'
  },
  { 
    name: 'Scheduler', 
    value: 'scheduler',
    icon: 'pi pi-clock'
  },
  { 
    name: 'Background Job', 
    value: 'background_job',
    icon: 'pi pi-cog'
  },
  { 
    name: 'System', 
    value: 'system',
    icon: 'pi pi-server'
  }
];

// Table columns
interface TableColumn {
  field: string;
  header: string;
  sortable: boolean;
}

const columns: TableColumn[] = [
  { field: 'timestamp', header: 'Timestamp', sortable: true },
  { field: 'eventType', header: 'Event Type', sortable: true },
  { field: 'severity', header: 'Severity', sortable: true },
  { field: 'status', header: 'Status', sortable: true },
  { field: 'source', header: 'Source', sortable: true },
  { field: 'description', header: 'Description', sortable: false },
  { field: 'actions', header: 'Actions', sortable: false }
];

// Status options for resolution
const eventStatuses = [
  { name: 'Open', value: 'open' },
  { name: 'In Progress', value: 'in_progress' },
  { name: 'Resolved', value: 'resolved' },
  { name: 'Dismissed', value: 'dismissed' }
] as const;

// Resolved statuses for filtering
const resolvedStatuses = ['resolved', 'dismissed'] as const;

// Methods
const loadEvents = async () => {
  try {
    loading.value = true;
    error.value = null;
    
    // Prepare query params
    const params: Record<string, any> = {
      page: Math.floor(pagination.first / pagination.rows) + 1,
      limit: pagination.rows,
      sortBy: pagination.sortField,
      sortOrder: pagination.sortOrder === 1 ? 'asc' : 'desc'
    };
    
    // Add filters if they exist
    if (filters.eventType) params.eventType = filters.eventType;
    if (filters.severity) params.severity = filters.severity;
    if (filters.status) params.status = filters.status;
    if (filters.source) params.source = filters.source;
    if (filters.searchQuery) params.search = filters.searchQuery;
    
    // Handle date range
    if (filters.dateRange && filters.dateRange.length === 2) {
      params.startDate = format(filters.dateRange[0], 'yyyy-MM-dd');
      params.endDate = format(filters.dateRange[1], 'yyyy-MM-dd');
    }
    
    // Call API
    const response = await securityEventService.getEvents(params);
    
    // Update state
    events.value = response.data;
    pagination.totalRecords = response.total || 0;
    pagination.pageCount = Math.ceil(response.total / pagination.rows);
    
  } catch (err: any) {
    console.error('Error loading security events:', err);
    error.value = 'Failed to load security events. Please try again.';
    
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load security events. Please try again later.',
      life: 5000
    });
  } finally {
    loading.value = false;
  }
};

const onPage = (event: DataTablePageEvent) => {
  pagination.first = event.first || 0;
  pagination.rows = event.rows || 10;
  loadEvents();
};

const onSort = (event: DataTableSortEvent) => {
  if (event.sortField) {
    pagination.sortField = event.sortField as string;
    pagination.sortOrder = event.sortOrder as 1 | -1 | null;
    loadEvents();
  }
};

const onFilter = () => {
  pagination.first = 0;
  loadEvents();
};

const clearFilters = () => {
  Object.assign(filters, {
    eventType: '',
    severity: '',
    status: '',
    source: '',
    searchQuery: '',
    dateRange: undefined,
    startDate: undefined,
    endDate: undefined
  });
  onFilter();
};

const viewEventDetails = (event: SecurityEvent) => {
  selectedEvent.value = event;
  showEventDialog.value = true;
};

const resolveEvent = async (event: SecurityEvent) => {
  try {
    await securityEventService.updateEventStatus(event.id, 'resolved');
    
    // Update local state
    const eventIndex = events.value.findIndex(e => e.id === event.id);
    if (eventIndex !== -1) {
      events.value[eventIndex].status = 'resolved';
      events.value[eventIndex].resolvedAt = new Date().toISOString();
    }
    
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: `Event marked as resolved.`,
      life: 3000
    });
    
  } catch (err) {
    console.error('Error updating event status:', err);
    
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to update event status. Please try again.',
      life: 5000
    });
  }
};

const exportEvents = async () => {
  try {
    exportLoading.value = true;
    
    // Prepare query params
    const params: Record<string, any> = {
      format: 'csv'
    };
    
    // Add filters if they exist
    if (filters.eventType) params.eventType = filters.eventType;
    if (filters.severity) params.severity = filters.severity;
    if (filters.status) params.status = filters.status;
    if (filters.source) params.source = filters.source;
    if (filters.searchQuery) params.search = filters.searchQuery;
    
    // Handle date range
    if (filters.dateRange && filters.dateRange.length === 2) {
      params.startDate = format(filters.dateRange[0], 'yyyy-MM-dd');
      params.endDate = format(filters.dateRange[1], 'yyyy-MM-dd');
    }
    
    // Call export API
    const response = await securityEventService.exportEvents(params);
    
    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `security-events-${format(new Date(), 'yyyy-MM-dd')}.csv`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    
    toast.add({
      severity: 'success',
      summary: 'Export Successful',
      detail: 'Security events have been exported successfully',
      life: 3000
    });
    
  } catch (err) {
    console.error('Error exporting events:', err);
    
    toast.add({
      severity: 'error',
      summary: 'Export Failed',
      detail: 'Failed to export security events. Please try again.',
      life: 5000
    });
  } finally {
    exportLoading.value = false;
  }
};

// Formatting helpers
const formatTimestamp = (timestamp: string) => {
  if (!timestamp) return '';
  try {
    return format(parseISO(timestamp), 'MMM d, yyyy HH:mm:ss');
  } catch (e) {
    return timestamp;
  }
};

const formatDateTime = (timestamp: string, formatStr: string = 'PPpp'): string => {
  if (!timestamp) return '';
  try {
    return format(parseISO(timestamp), formatStr);
  } catch (e) {
    return timestamp;
  }
};

const formatEventType = (eventType: string): string => {
  const type = eventTypes.find(t => t.value === eventType);
  return type ? type.name : eventType;
};

const formatSeverity = (severity: SecurityEventSeverity): string => {
  return severity.charAt(0).toUpperCase() + severity.slice(1);
};

const getSeverityIcon = (severity: SecurityEventSeverity): string => {
  switch (severity) {
    case 'critical': return 'pi pi-exclamation-triangle';
    case 'high': return 'pi pi-exclamation-circle';
    case 'medium': return 'pi pi-info-circle';
    case 'low': return 'pi pi-flag';
    default: return 'pi pi-info';
  }
};

const getSeverityBackground = (severity: SecurityEventSeverity): string => {
  switch (severity) {
    case 'critical': return 'bg-red-50';
    case 'high': return 'bg-orange-50';
    case 'medium': return 'bg-yellow-50';
    case 'low': return 'bg-blue-50';
    default: return 'bg-gray-50';
  }
};

const getSeverityTextColor = (severity: SecurityEventSeverity): string => {
  switch (severity) {
    case 'critical': return 'text-red-700';
    case 'high': return 'text-orange-700';
    case 'medium': return 'text-yellow-700';
    case 'low': return 'text-blue-700';
    default: return 'text-gray-700';
  }
};

const getSeverityBorderColor = (severity: SecurityEventSeverity): string => {
  switch (severity) {
    case 'critical': return 'border-red-200';
    case 'high': return 'border-orange-200';
    case 'medium': return 'border-yellow-200';
    case 'low': return 'border-blue-200';
    default: return 'border-gray-200';
  }
};

const formatStatus = (status: SecurityEventStatus): string => {
  return status.split('_').map(word => 
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ');
};

const getStatusSeverity = (status: SecurityEventStatus): string => {
  switch (status) {
    case 'resolved': return 'success';
    case 'in_progress': return 'info';
    case 'dismissed': return 'warning';
    case 'open':
    default: return 'danger';
  }
};

const getStatusIcon = (status: SecurityEventStatus): string => {
  switch (status) {
    case 'resolved': return 'pi pi-check';
    case 'in_progress': return 'pi pi-spin pi-spinner';
    case 'dismissed': return 'pi pi-times';
    case 'open':
    default: return 'pi pi-exclamation-circle';
  }
};

const getSourceIcon = (source: string): string => {
  const sourceMap: Record<string, string> = {
    'web': 'pi pi-globe',
    'api': 'pi pi-code',
    'mobile': 'pi pi-mobile',
    'desktop': 'pi pi-desktop',
    'server': 'pi pi-server',
    'database': 'pi pi-database',
    'cron': 'pi pi-clock',
    'system': 'pi pi-cog',
    'user': 'pi pi-user',
    'admin': 'pi pi-shield',
  };
  return sourceMap[source.toLowerCase()] || 'pi pi-question-circle';
};

const formatSource = (source: string): string => {
  return source.split('_').map(word => 
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ');
};

const getUserAvatarStyle = (user?: User): Record<string, string> => {
  if (!user) return {};
  return {
    backgroundColor: `#${Math.floor(Math.random()*16777215).toString(16)}`,
    color: '#fff',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontWeight: 'bold'
  };
};

const formatEventDetails = (details: any): string => {
  if (!details) return 'No details available';
  if (typeof details === 'string') return details;
  return JSON.stringify(details, null, 2);
};

    const response = await apiClient.get('/events/export', {
      params: filters.value
    });
    const blob = new Blob([response.data], { type: 'application/csv' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'security_events.csv';
    link.click();
    toast.add({
      severity: 'success',
      summary: 'Events Exported',
      detail: 'Security events have been exported successfully.',
      life: 5000
    });
  } catch (error) {
    console.error(error);
    toast.add({
      severity: 'error',
      summary: 'Export Failed',
      detail: 'Failed to export security events. Please try again.',
      life: 5000
    });
  } finally {
    exportLoading.value = false;
  }
};

const getEventTypeSeverity = (eventType: string) => {
  const typeMap: Record<string, string> = {
    'LOGIN_ATTEMPT': 'info',
    'LOGIN_SUCCESS': 'success',
    'LOGIN_FAILED': 'warning',
    'PASSWORD_CHANGE': 'info',
    'PASSWORD_RESET': 'warning',
    'PERMISSION_CHANGE': 'warning',
    'ROLE_ASSIGNMENT': 'info',
    'ROLE_REMOVAL': 'warning',
    'DATA_ACCESS': 'info',
    'DATA_MODIFICATION': 'warning',
    'DATA_DELETION': 'danger',
    'CONFIG_CHANGE': 'warning',
    'SYSTEM_ALERT': 'warning',
    'SECURITY_ALERT': 'danger',
    'API_ACCESS': 'info',
    'FILE_UPLOAD': 'info',
    'FILE_DOWNLOAD': 'info',
    'EXPORT_DATA': 'warning',
    'IMPORT_DATA': 'warning'
  };
  return typeMap[eventType] || 'info';
};

const getSeverityColor = (severity: string) => {
  const severityMap: Record<string, string> = {
    'info': 'info',
    'low': 'success',
    'medium': 'warning',
    'high': 'danger',
    'critical': 'danger'
  };
  return severityMap[severity] || 'info';
};

const formatTimestamp = (timestamp: string) => {
  return new Date(timestamp).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
};

// Lifecycle hooks
onMounted(async () => {
  // Load initial data
  await loadEvents();
  
  // Set up auto-refresh every 30 seconds
  const refreshInterval = setInterval(() => {
    if (!showEventDialog.value) { // Don't refresh if viewing event details
      loadEvents();
    }
  }, 30000);
  
  // Clean up interval on component unmount
  onUnmounted(() => {
    clearInterval(refreshInterval);
  });
});
</script>

<style scoped>
.event-details {
  max-height: 70vh;
  overflow-y: auto;
  padding-right: 0.5rem;
}

/* Custom scrollbar for event details */
.event-details::-webkit-scrollbar {
  width: 6px;
}

.event-details::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.event-details::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 3px;
}

.event-details::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .event-details {
    max-height: 60vh;
  }
}
</style>
