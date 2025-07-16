<template>
  <div class="ap-aging-report">
    <ReportHeader 
      title="Accounts Payable Aging Report"
      :filters="filters"
      :loading="loading"
      :export-loading="exportLoading"
      @filter-changed="handleFilterChange"
      @export-pdf="exportToPdf"
      @export-excel="exportToExcel"
      @print="printReport"
    >
      <template #filters>
        <div class="filters">
          <div class="p-field">
            <label for="asOfDate">As Of Date</label>
            <Calendar
              id="asOfDate"
              v-model="filters.asOfDate"
              :show-icon="true"
              date-format="yy-mm-dd"
              class="w-full"
            />
          </div>
          <div class="p-field">
            <label for="currency">Currency</label>
            <Dropdown
              id="currency"
              v-model="filters.currency"
              :options="currencyOptions"
              option-label="name"
              option-value="code"
              class="w-full"
            />
          </div>
          <div class="p-field">
            <label for="vendor">Vendor</label>
            <Dropdown
              id="vendor"
              v-model="filters.vendorId"
              :options="vendorOptions"
              option-label="name"
              option-value="id"
              :filter="true"
              placeholder="All Vendors"
              :show-clear="true"
              class="w-full"
            />
          </div>
        </div>
      </template>
    </ReportHeader>

    <!-- Loading State -->
    <ProgressBar v-if="loading" mode="indeterminate" class="mb-4" />

    <div v-else class="report-content">
      <!-- Summary Cards -->
      <div class="summary-cards">
        <SummaryCard
          title="Total Payables"
          :amount="summary.totalPayables"
          :change="summary.totalChange"
          :is-positive="summary.totalChange <= 0"
          icon="pi pi-money-bill"
        />
        <SummaryCard
          title="Current (0-30 days)"
          :amount="summary.currentAmount"
          :percentage="summary.currentPercentage"
          :is-percentage-positive="true"
          icon="pi pi-calendar"
        />
        <SummaryCard
          title="31-60 days"
          :amount="summary.period1Amount"
          :percentage="summary.period1Percentage"
          :is-percentage-positive="false"
          icon="pi pi-clock"
          warning
        />
        <SummaryCard
          title="61-90 days"
          :amount="summary.period2Amount"
          :percentage="summary.period2Percentage"
          :is-percentage-positive="false"
          icon="pi pi-exclamation-triangle"
          warning
        />
        <SummaryCard
          title="Over 90 days"
          :amount="summary.overdueAmount"
          :percentage="summary.overduePercentage"
          :is-percentage-positive="false"
          icon="pi pi-exclamation-circle"
          danger
        />
      </div>

      <!-- Aging Details -->
      <div class="section">
        <div class="section-header">
          <h3>Aging Details</h3>
          <div class="section-actions">
            <Button 
              icon="pi pi-send" 
              label="Send Reminders" 
              class="p-button-text p-button-sm" 
              @click="sendReminders"
              :disabled="!selectedVendors.length"
            />
            <Button 
              icon="pi pi-download" 
              label="Export" 
              class="p-button-text p-button-sm" 
              @click="exportDialogVisible = true"
            />
          </div>
        </div>

        <DataTable 
          :value="agingData" 
          :loading="loading"
          :scrollable="true"
          scroll-height="flex"
          :resizable-columns="true"
          column-resize-mode="expand"
          :paginator="true"
          :rows="20"
          :rows-per-page-options="[10, 20, 50, 100]"
          :selection.sync="selectedVendors"
          selection-mode="multiple"
          data-key="vendorId"
          class="p-datatable-sm"
        >
          <Column selection-mode="multiple" header-style="width: 3rem"></Column>
          <Column field="vendorName" header="Vendor" sortable>
            <template #body="{ data }">
              <span class="font-medium">{{ data.vendorName }}</span>
            </template>
          </Column>
          <Column field="invoiceNumber" header="Invoice #" sortable>
            <template #body="{ data }">
              <span class="font-medium">{{ data.invoiceNumber }}</span>
            </template>
          </Column>
          <Column field="invoiceDate" header="Invoice Date" sortable>
            <template #body="{ data }">
              {{ formatDate(data.invoiceDate) }}
            </template>
          </Column>
          <Column field="dueDate" header="Due Date" sortable>
            <template #body="{ data }">
              <span :class="{ 'text-red-500 font-medium': isOverdue(data.dueDate) }">
                {{ formatDate(data.dueDate) }}
              </span>
            </template>
          </Column>
          <Column field="daysOverdue" header="Days Overdue" sortable>
            <template #body="{ data }">
              <span :class="getDaysOverdueClass(data.daysOverdue)">
                {{ data.daysOverdue > 0 ? data.daysOverdue : '' }}
              </span>
            </template>
          </Column>
          <Column field="current" header="Current" sortable>
            <template #body="{ data }">
              {{ formatCurrency(data.current) }}
            </template>
          </Column>
          <Column field="period1" header="1-30 Days" sortable>
            <template #body="{ data }">
              {{ formatCurrency(data.period1) }}
            </template>
          </Column>
          <Column field="period2" header="31-60 Days" sortable>
            <template #body="{ data }">
              {{ formatCurrency(data.period2) }}
            </template>
          </Column>
          <Column field="period3" header="61-90 Days" sortable>
            <template #body="{ data }">
              {{ formatCurrency(data.period3) }}
            </template>
          </Column>
          <Column field="over90" header="90+ Days" sortable>
            <template #body="{ data }">
              {{ formatCurrency(data.over90) }}
            </template>
          </Column>
          <Column field="total" header="Total" sortable>
            <template #body="{ data }">
              <strong>{{ formatCurrency(data.total) }}</strong>
            </template>
          </Column>
          <Column header="Actions" :exportable="false" style="min-width: 10rem">
            <template #body="{ data }">
              <Button 
                icon="pi pi-eye" 
                class="p-button-text p-button-sm" 
                @click="viewVendor(data.vendorId)" 
                v-tooltip.top="'View Vendor'"
              />
              <Button 
                icon="pi pi-file-pdf" 
                class="p-button-text p-button-sm p-button-success" 
                @click="viewInvoice(data.invoiceId)" 
                v-tooltip.top="'View Invoice'"
              />
              <Button 
                icon="pi pi-send" 
                class="p-button-text p-button-sm p-button-info" 
                @click="sendReminder(data.vendorId, data.invoiceId)" 
                v-tooltip.top="'Send Reminder'"
              />
            </template>
          </Column>
        </DataTable>
      </div>
    </div>

    <!-- Export Dialog -->
    <Dialog 
      v-model:visible="exportDialogVisible" 
      header="Export Report" 
      :modal="true" 
      :style="{ width: '450px' }"
      :closable="false"
    >
      <div class="p-fluid">
        <div class="p-field">
          <label for="exportFormat">Format</label>
          <Dropdown
            id="exportFormat"
            v-model="exportFormat"
            :options="exportFormats"
            option-label="name"
            option-value="value"
            placeholder="Select Format"
          />
        </div>
      </div>
      <template #footer>
        <Button 
          label="Cancel" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="exportDialogVisible = false" 
        />
        <Button 
          label="Export" 
          icon="pi pi-download" 
          class="p-button-primary" 
          @click="handleExport" 
          :loading="exportLoading"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useRouter } from 'vue-router';
import { format, parseISO, differenceInDays } from 'date-fns';
import ReportHeader from '@/components/reports/ReportHeader.vue';
import SummaryCard from '@/components/reports/SummaryCard.vue';
import Button from 'primevue/button';
import Calendar from 'primevue/calendar';
import Dropdown from 'primevue/dropdown';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Dialog from 'primevue/dialog';
import ProgressBar from 'primevue/progressbar';
import { useReport } from '@/composables/useReport';

// Types
interface FilterState {
  asOfDate: Date | null;
  currency: string;
  vendorId: string | null;
}

interface AgingData {
  vendorId: string;
  vendorName: string;
  invoiceId: string;
  invoiceNumber: string;
  invoiceDate: string;
  dueDate: string;
  daysOverdue: number;
  current: number;
  period1: number;
  period2: number;
  period3: number;
  over90: number;
  total: number;
}

interface SummaryData {
  totalPayables: number;
  totalChange: number;
  currentAmount: number;
  currentPercentage: number;
  period1Amount: number;
  period1Percentage: number;
  period2Amount: number;
  period2Percentage: number;
  overdueAmount: number;
  overduePercentage: number;
}

// Toast
const toast = useToast();
const router = useRouter();

// State
const loading = ref(false);
const exportLoading = ref(false);
const exportDialogVisible = ref(false);
const exportFormat = ref('pdf');
const selectedVendors = ref<any[]>([]);

// Filters
const filters = ref<FilterState>({
  asOfDate: new Date(),
  currency: 'USD',
  vendorId: null,
});

// Mock data - Replace with actual API calls
const vendorOptions = ref([
  { id: '1', name: 'ABC Suppliers' },
  { id: '2', name: 'XYZ Manufacturing' },
  { id: '3', name: 'Global Parts Inc.' },
]);

const currencyOptions = ref([
  { name: 'US Dollar', code: 'USD' },
  { name: 'Euro', code: 'EUR' },
  { name: 'British Pound', code: 'GBP' },
]);

const exportFormats = ref([
  { name: 'PDF', value: 'pdf' },
  { name: 'Excel', value: 'excel' },
  { name: 'CSV', value: 'csv' },
]);

// Mock data - Replace with actual API calls
const agingData = ref<AgingData[]>([]);
const summary = ref<SummaryData>({
  totalPayables: 0,
  totalChange: 0,
  currentAmount: 0,
  currentPercentage: 0,
  period1Amount: 0,
  period1Percentage: 0,
  period2Amount: 0,
  period2Percentage: 0,
  overdueAmount: 0,
  overduePercentage: 0,
});

// Methods
const fetchAgingData = async () => {
  try {
    loading.value = true;
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Mock data - Replace with actual API response
    agingData.value = [
      {
        vendorId: '1',
        vendorName: 'ABC Suppliers',
        invoiceId: 'INV-2023-001',
        invoiceNumber: 'INV-2023-001',
        invoiceDate: '2023-11-01',
        dueDate: '2023-12-01',
        daysOverdue: 45,
        current: 0,
        period1: 2500.00,
        period2: 0,
        period3: 0,
        over90: 0,
        total: 2500.00
      },
      {
        vendorId: '2',
        vendorName: 'XYZ Manufacturing',
        invoiceId: 'INV-2023-002',
        invoiceNumber: 'INV-2023-002',
        invoiceDate: '2023-10-15',
        dueDate: '2023-11-15',
        daysOverdue: 75,
        current: 0,
        period1: 0,
        period2: 3500.00,
        period3: 0,
        over90: 0,
        total: 3500.00
      },
      // Add more mock data as needed
    ];
    
    // Calculate summary
    updateSummary();
    
  } catch (error) {
    console.error('Error fetching AP aging data:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to fetch AP aging data',
      life: 5000
    });
  } finally {
    loading.value = false;
  }
};

const updateSummary = () => {
  // Calculate summary from aging data
  const currentDate = new Date();
  let totalPayables = 0;
  let currentTotal = 0;
  let period1Total = 0;
  let period2Total = 0;
  let overdueTotal = 0;
  
  agingData.value.forEach(item => {
    totalPayables += item.total;
    currentTotal += item.current;
    period1Total += item.period1;
    period2Total += item.period2;
    overdueTotal += item.period3 + item.over90;
  });
  
  summary.value = {
    totalPayables,
    totalChange: 0, // Would be calculated based on previous period
    currentAmount: currentTotal,
    currentPercentage: totalPayables > 0 ? (currentTotal / totalPayables) * 100 : 0,
    period1Amount: period1Total,
    period1Percentage: totalPayables > 0 ? (period1Total / totalPayables) * 100 : 0,
    period2Amount: period2Total,
    period2Percentage: totalPayables > 0 ? (period2Total / totalPayables) * 100 : 0,
    overdueAmount: overdueTotal,
    overduePercentage: totalPayables > 0 ? (overdueTotal / totalPayables) * 100 : 0,
  };
};

const handleFilterChange = () => {
  fetchAgingData();
};

const handleExport = async () => {
  try {
    exportLoading.value = true;
    
    // Simulate export
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    toast.add({
      severity: 'success',
      summary: 'Export Successful',
      detail: `Report exported as ${exportFormat.value.toUpperCase()}`,
      life: 3000
    });
    
    exportDialogVisible.value = false;
    
  } catch (error) {
    console.error('Export error:', error);
    toast.add({
      severity: 'error',
      summary: 'Export Failed',
      detail: 'Failed to export report',
      life: 5000
    });
  } finally {
    exportLoading.value = false;
  }
};

const exportToPdf = () => {
  exportFormat.value = 'pdf';
  handleExport();
};

const exportToExcel = () => {
  exportFormat.value = 'excel';
  handleExport();
};

const printReport = () => {
  window.print();
};

const sendReminders = async (vendorId?: string, invoiceId?: string) => {
  try {
    loading.value = true;
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const message = vendorId && invoiceId 
      ? `Reminder sent for invoice ${invoiceId}`
      : `Reminders sent to ${selectedVendors.value.length} vendors`;
    
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: message,
      life: 3000
    });
    
    // Clear selection
    if (!vendorId) {
      selectedVendors.value = [];
    }
    
  } catch (error) {
    console.error('Error sending reminders:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to send reminders',
      life: 5000
    });
  } finally {
    loading.value = false;
  }
};

const viewVendor = (vendorId: string) => {
  router.push({ name: 'VendorDetails', params: { id: vendorId } });
};

const viewInvoice = (invoiceId: string) => {
  // Implement view invoice logic
  console.log('View invoice:', invoiceId);
};

const formatDate = (dateString: string): string => {
  if (!dateString) return '';
  try {
    return format(parseISO(dateString), 'MMM dd, yyyy');
  } catch (error) {
    return dateString;
  }
};

const isOverdue = (dueDate: string): boolean => {
  if (!dueDate) return false;
  try {
    const due = parseISO(dueDate);
    const today = new Date();
    return due < today;
  } catch (error) {
    return false;
  }
};

const getDaysOverdueClass = (days: number): string => {
  if (days <= 0) return '';
  if (days <= 30) return 'text-yellow-600';
  if (days <= 60) return 'text-orange-600';
  return 'text-red-600 font-medium';
};

const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: filters.value.currency || 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value || 0);
};

// Lifecycle hooks
onMounted(() => {
  fetchAgingData();
});
</script>

<style scoped>
.ap-aging-report {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.report-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 1rem 0;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.section {
  background: #ffffff;
  border-radius: 6px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.section-actions {
  display: flex;
  gap: 0.5rem;
}

/* Responsive adjustments */
@media (max-width: 960px) {
  .summary-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .summary-cards {
    grid-template-columns: 1fr;
  }
  
  .section {
    padding: 1rem;
  }
}

/* Print styles */
@media print {
  .p-datatable-tbody {
    display: table-row-group;
  }
  
  .p-datatable-tbody > tr {
    page-break-inside: avoid;
  }
  
  .section-actions {
    display: none;
  }
  
  .p-paginator {
    display: none;
  }
}
</style>
