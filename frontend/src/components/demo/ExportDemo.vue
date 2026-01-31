<template>
  <div class="export-demo">
    <div class="card">
      <div class="flex justify-content-between align-items-center mb-4">
        <h2>Export Demo</h2>
        <div class="flex gap-2">
          <Button 
            label="Export Data" 
            icon="pi pi-download" 
            @click="openExportDialog"
            :loading="isExporting"
          />
        </div>
      </div>

      <DataTable 
        :value="demoData" 
        :loading="loading" 
        :paginator="true"
        :rows="10"
        :rowsPerPageOptions="[5, 10, 20, 50]"
        v-model:first="first"
        v-model:sortField="sortField"
        v-model:sortOrder="sortOrder"
        @sort="onSort($event)"
        ref="dt"
      >
        <Column field="id" header="ID" :sortable="true"></Column>
        <Column field="name" header="Name" :sortable="true"></Column>
        <Column field="email" header="Email" :sortable="true"></Column>
        <Column field="status" header="Status" :sortable="true">
          <template #body="{ data }">
            <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
          </template>
        </Column>
        <Column field="date" header="Date" :sortable="true">
          <template #body="{ data }">
            {{ formatDate(data.date) }}
          </template>
        </Column>
        <Column field="amount" header="Amount" :sortable="true">
          <template #body="{ data }">
            {{ formatCurrency(data.amount) }}
          </template>
        </Column>
      </DataTable>
    </div>

    <!-- Export Dialog -->
    <ExportDialog 
      ref="exportDialogRef" 
      @export="handleExport"
      @success="onExportSuccess"
      @error="onExportError"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useToast } from 'primevue/usetoast';
import { useReportExport } from '@/composables/useReportExport';

const { t } = useI18n();
const toast = useToast();

// Table state
const loading = ref(false);
const first = ref(0);
const sortField = ref('id');
const sortOrder = ref(1); // 1 for asc, -1 for desc
const dt = ref();

// Sample data for demo
const demoData = ref([
  { id: 1, name: 'John Doe', email: 'john@example.com', status: 'active', date: '2023-06-15', amount: 1250.75 },
  { id: 2, name: 'Jane Smith', email: 'jane@example.com', status: 'inactive', date: '2023-06-14', amount: 850.50 },
  { id: 3, name: 'Bob Johnson', email: 'bob@example.com', status: 'pending', date: '2023-06-13', amount: 2200.00 },
  { id: 4, name: 'Alice Brown', email: 'alice@example.com', status: 'active', date: '2023-06-12', amount: 1750.25 },
  { id: 5, name: 'Charlie Wilson', email: 'charlie@example.com', status: 'inactive', date: '2023-06-11', amount: 950.00 },
]);

// Use the report export composable
const {
  exportDialogRef,
  isExporting,
  exportProgress,
  openExportDialog,
  handleExport,
  onExportSuccess,
  onExportError,
  prepareExportData
} = useReportExport();

// Format date for display
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString();
};

// Format currency for display
const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(value);
};

// Get severity for status tag
const getStatusSeverity = (status: string) => {
  switch (status) {
    case 'active':
      return 'success';
    case 'inactive':
      return 'danger';
    case 'pending':
      return 'warning';
    default:
      return null;
  }
};

// Handle sort
const onSort = (event: any) => {
  sortField.value = event.sortField;
  sortOrder.value = event.sortOrder;
  // In a real app, you would fetch sorted data from the server here
};

// Handle export with custom options
const handleExportWithOptions = async (options: any) => {
  try {
    // In a real app, you would fetch data from the server with the given options
    // For this demo, we'll use the local data
    
    // Prepare columns for export
    const columns = [
      { field: 'id', header: 'ID', type: 'number' },
      { field: 'name', header: 'Name', type: 'text' },
      { field: 'email', header: 'Email', type: 'text' },
      { field: 'status', header: 'Status', type: 'text' },
      { field: 'date', header: 'Date', type: 'date' },
      { field: 'amount', header: 'Amount', type: 'currency' },
    ];
    
    // Prepare the data for export
    const exportData = prepareExportData(demoData.value, columns);
    
    // Call the handleExport function with the prepared data
    return await handleExport(exportData, {
      ...options,
      fileName: options.fileName || 'export-demo',
    });
  } catch (error) {
    onExportError(error);
    throw error;
  }
};

// Handle export dialog submit
const handleExport = async (options: any) => {
  return await handleExportWithOptions(options);
};

// Handle successful export
const onExportSuccess = (result: any) => {
  toast.add({
    severity: 'success',
    summary: t('export.success.title'),
    detail: t('export.success.message', { format: result.format.toUpperCase() }),
    life: 3000,
  });
};

// Handle export error
const onExportError = (error: any) => {
  console.error('Export error:', error);
  toast.add({
    severity: 'error',
    summary: t('export.error.title'),
    detail: error.message || t('export.error.message'),
    life: 5000,
  });
};

// Open export dialog with default options
const openExportDialog = () => {
  if (exportDialogRef.value) {
    exportDialogRef.value.open({
      fileName: 'export-demo',
      format: 'excel',
    });
  }
};

// Fetch data on component mount
onMounted(() => {
  // In a real app, you would fetch data from an API here
  loading.value = true;
  setTimeout(() => {
    loading.value = false;
  }, 500);
});
</script>

<style scoped>
.export-demo {
  padding: 1rem;
}

.card {
  background: var(--surface-card);
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 2px 1px -1px rgba(0, 0, 0, 0.2), 0 1px 1px 0 rgba(0, 0, 0, 0.14), 0 1px 3px 0 rgba(0, 0, 0, 0.12);
}

:deep(.p-datatable) {
  .p-datatable-thead > tr > th {
    background: var(--surface-50);
    font-weight: 600;
  }
  
  .p-datatable-tbody > tr {
    transition: background-color 0.2s;
    
    &:hover {
      background: var(--surface-50) !important;
    }
  }
}

.export-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-bottom: 1rem;
}
</style>
