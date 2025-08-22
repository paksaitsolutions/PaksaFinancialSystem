<template>
  <div class="security-events p-4">
    <Toast />
    <Card>
      <template #title>
        <div class="flex justify-between items-center">
          <h2 class="text-2xl font-bold">Security Events Log</h2>
          <Button icon="pi pi-refresh" class="p-button-text" @click="fetchEvents" :loading="loading" />
        </div>
      </template>
      <template #content>
        <Toolbar class="mb-4">
          <template #start>
            <div class="flex items-center gap-2">
              <InputText placeholder="Search..." v-model="filters['global'].value" style="width: 250px;" />
              <Button label="Export" icon="pi pi-upload" class="p-button-help" @click="exportEvents" :loading="exportLoading" />
            </div>
          </template>
        </Toolbar>

        <DataTable :value="events" :loading="loading" :paginator="true" :rows="10" :filters="filters"
          dataKey="id" rowHover responsiveLayout="scroll"
          paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
          :rowsPerPageOptions="[10, 25, 50]" currentPageReportTemplate="Showing {first} to {last} of {totalRecords} events">
          
          <Column field="severity" header="Severity" :sortable="true" style="min-width: 8rem">
            <template #body="{ data }">
              <Tag :value="data.severity" :class="getSeverityInfo(data.severity).class" class="px-2 py-1 text-xs font-semibold rounded-full" />
            </template>
          </Column>

          <Column field="event_type" header="Event Type" :sortable="true" style="min-width: 12rem"></Column>

          <Column field="timestamp" header="Timestamp" :sortable="true" style="min-width: 12rem">
            <template #body="{ data }">
              {{ formatTime(data.timestamp) }}
            </template>
          </Column>

          <Column field="source_ip" header="Source IP" :sortable="true" style="min-width: 10rem"></Column>

          <Column field="user.name" header="User" :sortable="true" style="min-width: 10rem">
            <template #body="{ data }">
              {{ data.user?.name || 'N/A' }}
            </template>
          </Column>

          <Column field="resolved" header="Status" :sortable="true" style="min-width: 8rem">
            <template #body="{ data }">
              <Tag :value="getStatusInfo(data.resolved).text" :severity="getStatusInfo(data.resolved).severity" />
            </template>
          </Column>

          <Column header="Actions" style="min-width: 10rem">
            <template #body="{ data }">
              <Button icon="pi pi-eye" class="p-button-rounded p-button-info mr-2" @click="viewEventDetails(data)" />
              <Button icon="pi pi-check" class="p-button-rounded p-button-success" @click="resolveEvent(data)" :disabled="data.resolved" />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <!-- Event Details Dialog -->
    <Dialog header="Event Details" v-model:visible="dialogVisible" :modal="true" :style="{ width: '50vw' }">
      <div v-if="selectedEvent" class="event-details-grid">
        <div class="detail-item">
          <span class="detail-label">Event ID</span>
          <span class="detail-value">{{ selectedEvent.id }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Timestamp</span>
          <span class="detail-value">{{ formatTime(selectedEvent.timestamp) }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Severity</span>
          <Tag :value="selectedEvent.severity" :class="getSeverityInfo(selectedEvent.severity).class" />
        </div>
        <div class="detail-item">
          <span class="detail-label">Status</span>
          <Tag :value="getStatusInfo(selectedEvent.resolved).text" :severity="getStatusInfo(selectedEvent.resolved).severity" />
        </div>
        <div class="detail-item col-span-2">
          <span class="detail-label">Description</span>
          <span class="detail-value">{{ selectedEvent.description }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">Source IP</span>
          <span class="detail-value">{{ selectedEvent.source_ip }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">User</span>
          <span class="detail-value">{{ selectedEvent.user?.name || 'N/A' }} ({{ selectedEvent.user?.id || 'System' }})</span>
        </div>
        <div class="detail-item col-span-2">
          <span class="detail-label">Additional Data</span>
          <pre class="bg-gray-100 p-2 rounded">{{ JSON.stringify(selectedEvent.additional_data, null, 2) }}</pre>
        </div>
      </div>
      <template #footer>
        <Button label="Close" icon="pi pi-times" class="p-button-text" @click="dialogVisible = false" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useToast } from 'vue/usetoast';
import { FilterMatchMode } from 'vue/api';
import DataTable from 'vue/datatable';
import Column from 'vue/column';
import Button from 'vue/button';
import InputText from 'vue/inputtext';
import Dialog from 'vue/dialog';
import Card from 'vue/card';
import Toolbar from 'vue/toolbar';
import Tag from 'vue/tag';
import Toast from 'vue/toast';
import { format } from 'date-fns';
import apiClient from '@/services/api';

// --- INTERFACES & TYPES ---
type Severity = 'low' | 'medium' | 'high' | 'critical';
type TagSeverity = 'success' | 'info' | 'warning' | 'danger';

interface SecurityEvent {
  id: string;
  event_type: string;
  timestamp: string;
  severity: Severity;
  description: string;
  source_ip: string;
  user: { id: string; name: string } | null;
  additional_data: Record<string, any>;
  resolved: boolean;
}

// --- STATE MANAGEMENT ---
const toast = useToast();
const events = ref<SecurityEvent[]>([]);
const loading = ref(false);
const exportLoading = ref(false);
const selectedEvent = ref<SecurityEvent | null>(null);
const dialogVisible = ref(false);

const filters = ref({
  global: { value: null, matchMode: FilterMatchMode.CONTAINS },
});

// --- API & DATA HANDLING ---
onMounted(() => {
  fetchEvents();
});

const fetchEvents = async () => {
  loading.value = true;
  try {
    const response = await apiClient.get('/compliance/security/events');
    events.value = response.data.events; // Assuming API returns { events: [], total: number }
    toast.add({ severity: 'success', summary: 'Success', detail: 'Events loaded successfully.', life: 3000 });
  } catch (err) {
    console.error('Failed to load security events:', err);
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load security events.', life: 3000 });
    // Load mock data as a fallback for demonstration
    events.value = []; 
  } finally {
    loading.value = false;
  }
};

const resolveEvent = async (event: SecurityEvent) => {
  try {
    toast.add({ severity: 'info', summary: 'Processing', detail: `Resolving event ${event.id}...`, life: 2000 });
    await apiClient.post(`/compliance/security/events/${event.id}/resolve`);

    const eventToResolve = events.value.find(e => e.id === event.id);
    if (eventToResolve) {
      eventToResolve.resolved = true;
    }
    toast.add({ severity: 'success', summary: 'Success', detail: 'Event marked as resolved.', life: 3000 });
  } catch (err) {
    console.error('Failed to resolve event:', err);
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to resolve event.', life: 3000 });
  }
};

const exportEvents = () => {
  exportLoading.value = true;
  try {
    toast.add({ severity: 'info', summary: 'Exporting', detail: 'Preparing data for export...', life: 2000 });
    setTimeout(() => {
      const data = JSON.stringify(events.value, null, 2);
      const blob = new Blob([data], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'security-events.json';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      exportLoading.value = false;
    }, 1000);
  } catch (error) {
    console.error('Error exporting events:', error);
    toast.add({
      severity: 'error',
      summary: 'Export Failed',
      detail: 'There was an error exporting the events.',
      life: 5000
    });
    exportLoading.value = false;
  }
};

const viewEventDetails = (event: SecurityEvent) => {
  selectedEvent.value = event;
  dialogVisible.value = true;
};

// --- FORMATTING & DISPLAY HELPERS ---
const formatTime = (timestamp: string) => {
  return format(new Date(timestamp), "yyyy-MM-dd HH:mm:ss");
};

const getSeverityInfo = (severity: Severity): { class: string } => {
  const mapping: Record<Severity, string> = {
    low: 'bg-blue-100 text-blue-800',
    medium: 'bg-yellow-100 text-yellow-800',
    high: 'bg-orange-100 text-orange-800',
    critical: 'bg-red-100 text-red-800',
  };
  return { class: mapping[severity] ?? 'bg-gray-100 text-gray-800' };
};

const getStatusInfo = (resolved: boolean): { severity: TagSeverity, text: string } => {
  return resolved
    ? { severity: 'success', text: 'Resolved' }
    : { severity: 'warning', text: 'Unresolved' };
};

</script>

<style scoped>
.security-events {
  max-width: 1200px;
  margin: auto;
}

.event-details-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem 2rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
}

.detail-label {
  font-weight: 600;
  color: #4b5563; /* text-gray-600 */
  margin-bottom: 0.25rem;
}

.detail-value {
  color: #1f2937; /* text-gray-800 */
}

.col-span-2 {
  grid-column: span 2;
}
</style>
