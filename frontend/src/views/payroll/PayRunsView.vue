<template>
  <div class="p-4">
    <Card>
      <template #title>Pay Runs</template>
      <template #content>
        <Message severity="info" :closable="false" class="mb-4">
          <p>Manage and process payroll runs for your organization.</p>
        </Message>
        
        <div class="flex justify-content-between mb-4">
          <Button 
            label="New Pay Run" 
            icon="pi pi-plus" 
            class="p-button-primary"
            @click="startNewPayRun"
          />
          <span class="p-input-icon-left">
            <i class="pi pi-search" />
            <InputText v-model="filters['global'].value" placeholder="Search pay runs..." />
          </span>
        </div>
        
        <DataTable 
          :value="payRuns" 
          :paginator="true" 
          :rows="10"
          :loading="loading"
          :filters="filters"
          responsiveLayout="scroll"
          class="p-datatable-sm"
        >
          <Column field="payPeriod" header="Pay Period" :sortable="true">
            <template #body="{ data }">
              {{ formatDateRange(data.payPeriodStart, data.payPeriodEnd) }}
            </template>
          </Column>
          
          <Column field="payDate" header="Pay Date" :sortable="true">
            <template #body="{ data }">
              {{ formatDate(data.payDate) }}
            </template>
          </Column>
          
          <Column field="status" header="Status" :sortable="true">
            <template #body="{ data }">
              <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
            </template>
          </Column>
          
          <Column field="employeeCount" header="Employees" :sortable="true" />
          
          <Column field="totalAmount" header="Total Amount" :sortable="true">
            <template #body="{ data }">
              {{ formatCurrency(data.totalAmount) }}
            </template>
          </Column>
          
          <Column headerStyle="width: 10rem; text-align: center">
            <template #body="{ data }">
              <Button 
                icon="pi pi-eye" 
                class="p-button-text p-button-rounded"
                @click="viewPayRun(data)"
                v-tooltip.top="'View Details'"
              />
              <Button 
                icon="pi pi-file-pdf" 
                class="p-button-text p-button-rounded p-button-help"
                @click="exportPdf(data)"
                v-tooltip.top="'Export PDF'"
              />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import { FilterMatchMode } from 'primevue/api';

// Components
import Card from 'primevue/card';
import Button from 'primevue/button';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import InputText from 'primevue/inputtext';
import Message from 'primevue/message';
import Tag from 'primevue/tag';

type PayRunStatus = 'Draft' | 'Pending' | 'Processing' | 'Completed' | 'Failed';

interface PayRun {
  id: string;
  payPeriodStart: string;
  payPeriodEnd: string;
  payDate: string;
  status: PayRunStatus;
  employeeCount: number;
  totalAmount: number;
  processedBy: string;
  processedAt: string | null;
}

const toast = useToast();
const loading = ref(false);

// Mock data
const payRuns = ref<PayRun[]>([
  {
    id: 'PR-2023-001',
    payPeriodStart: '2023-01-01',
    payPeriodEnd: '2023-01-15',
    payDate: '2023-01-20',
    status: 'Completed',
    employeeCount: 24,
    totalAmount: 12456.78,
    processedBy: 'admin',
    processedAt: '2023-01-19T14:30:00Z',
  },
  {
    id: 'PR-2023-002',
    payPeriodStart: '2023-01-16',
    payPeriodEnd: '2023-01-31',
    payDate: '2023-02-05',
    status: 'Completed',
    employeeCount: 24,
    totalAmount: 12890.45,
    processedBy: 'admin',
    processedAt: '2023-02-04T10:15:00Z',
  },
  {
    id: 'PR-2023-003',
    payPeriodStart: '2023-02-01',
    payPeriodEnd: '2023-02-15',
    payDate: '2023-02-20',
    status: 'Pending',
    employeeCount: 24,
    totalAmount: 0,
    processedBy: '',
    processedAt: null,
  },
]);

// Filters
const filters = ref({
  'global': { value: null, matchMode: FilterMatchMode.CONTAINS },
});

// Format date to YYYY-MM-DD
const formatDate = (dateString: string) => {
  if (!dateString) return '-';
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

// Format date range
const formatDateRange = (startDate: string, endDate: string) => {
  if (!startDate || !endDate) return '-';
  const start = new Date(startDate);
  const end = new Date(endDate);
  return `${start.getDate()} ${start.toLocaleString('default', { month: 'short' })} - ${end.getDate()} ${end.toLocaleString('default', { month: 'short' })} ${end.getFullYear()}`;
};

// Format currency
const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(value);
};

// Get severity for status tag
const getStatusSeverity = (status: PayRunStatus) => {
  switch (status) {
    case 'Completed': return 'success';
    case 'Processing': return 'info';
    case 'Pending': return 'warning';
    case 'Failed': return 'danger';
    default: return 'info';
  }
};

// Start new pay run
const startNewPayRun = () => {
  toast.add({
    severity: 'info',
    summary: 'New Pay Run',
    detail: 'Starting new pay run...',
    life: 3000,
  });
};

// View pay run details
const viewPayRun = (payRun: PayRun) => {
  toast.add({
    severity: 'info',
    summary: 'View Pay Run',
    detail: `Viewing pay run ${payRun.id}`,
    life: 3000,
  });
};

// Export to PDF
const exportPdf = (payRun: PayRun) => {
  toast.add({
    severity: 'success',
    summary: 'Export PDF',
    detail: `Exporting pay run ${payRun.id} to PDF...`,
    life: 3000,
  });
};

// Initialize component
onMounted(() => {
  loading.value = true;
  setTimeout(() => loading.value = false, 500);
});
</script>

<style scoped>
.p-card {
  margin-bottom: 1rem;
}

:deep(.p-card-title) {
  font-size: 1.25rem;
  font-weight: 600;
}

:deep(.p-datatable) {
  font-size: 0.9rem;
}

:deep(.p-datatable .p-datatable-thead > tr > th) {
  background-color: #f8f9fa;
  font-weight: 600;
}
</style>
