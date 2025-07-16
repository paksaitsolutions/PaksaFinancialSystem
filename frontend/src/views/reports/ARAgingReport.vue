<template>
  <div class="ar-aging-report">
    <ReportHeader 
      title="Accounts Receivable Aging Report"
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
            <label for="customer">Customer</label>
            <Dropdown
              id="customer"
              v-model="filters.customerId"
              :options="customerOptions"
              option-label="name"
              option-value="id"
              :filter="true"
              placeholder="All Customers"
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
          title="Total Receivables"
          :amount="summary.totalReceivables"
          :change="summary.totalChange"
          :is-positive="summary.totalChange >= 0"
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
              label="Send Statements" 
              icon="pi pi-envelope" 
              class="p-button-outlined p-button-sm mr-2"
              @click="sendStatements"
              :disabled="!selectedInvoices.length"
            />
          </div>
        </div>
        
        <DataTable 
          :value="agingData" 
          :paginator="true" 
          :rows="20"
          :rows-per-page-options="[10, 20, 50, 100]"
          :loading="loading"
          :scrollable="true"
          scroll-height="flex"
          class="p-datatable-sm"
          responsive-layout="scroll"
          v-model:selection="selectedInvoices"
          selection-mode="multiple"
          data-key="id"
        >
          <Column selection-mode="multiple" header-style="width: 3em"></Column>
          <Column field="customer" header="Customer" :sortable="true">
            <template #body="{ data }">
              <div class="customer-cell">
                <div class="customer-name">{{ data.customer }}</div>
                <div class="customer-email">{{ data.customerEmail }}</div>
              </div>
            </template>
          </Column>
          <Column field="invoiceNumber" header="Invoice #" :sortable="true" />
          <Column field="invoiceDate" header="Date" :sortable="true">
            <template #body="{ data }">
              {{ formatDate(data.invoiceDate) }}
            </template>
          </Column>
          <Column field="dueDate" header="Due Date" :sortable="true">
            <template #body="{ data }">
              <span :class="{ 'text-red-500': isOverdue(data.dueDate) }">
                {{ formatDate(data.dueDate) }}
              </span>
            </template>
          </Column>
          <Column field="daysOverdue" header="Days Overdue" :sortable="true">
            <template #body="{ data }">
              <span :class="getDaysOverdueClass(data.daysOverdue)">
                {{ data.daysOverdue > 0 ? data.daysOverdue : '-' }}
              </span>
            </template>
          </Column>
          <Column field="originalAmount" header="Original Amount" :sortable="true" class="text-right">
            <template #body="{ data }">
              {{ formatCurrency(data.originalAmount) }}
            </template>
          </Column>
          <Column field="paidAmount" header="Paid" :sortable="true" class="text-right">
            <template #body="{ data }">
              {{ formatCurrency(data.paidAmount) }}
            </template>
          </Column>
          <Column field="current" header="Current" :sortable="true" class="text-right">
            <template #body="{ data }">
              {{ formatCurrency(data.current) }}
            </template>
          </Column>
          <Column field="period1" header="31-60 days" :sortable="true" class="text-right">
            <template #body="{ data }">
              {{ formatCurrency(data.period1) }}
            </template>
          </Column>
          <Column field="period2" header="61-90 days" :sortable="true" class="text-right">
            <template #body="{ data }">
              {{ formatCurrency(data.period2) }}
            </template>
          </Column>
          <Column field="overdue" header="Over 90 days" :sortable="true" class="text-right">
            <template #body="{ data }">
              {{ formatCurrency(data.overdue) }}
            </template>
          </Column>
          <Column field="total" header="Balance" :sortable="true" class="text-right font-bold">
            <template #body="{ data }">
              {{ formatCurrency(data.total) }}
            </template>
          </Column>
        </DataTable>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import ReportHeader from '@/components/reports/ReportHeader.vue';
import SummaryCard from '@/components/reports/SummaryCard.vue';

// Types
interface FilterState {
  asOfDate: Date | null;
  currency: string;
  customerId: string | null;
}

interface AgingData {
  id: string;
  customer: string;
  customerEmail: string;
  invoiceNumber: string;
  invoiceDate: string;
  dueDate: string;
  daysOverdue: number;
  originalAmount: number;
  paidAmount: number;
  current: number;
  period1: number;
  period2: number;
  overdue: number;
  total: number;
}

interface SummaryData {
  totalReceivables: number;
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

// State
const loading = ref(false);
const exportLoading = ref(false);
const selectedInvoices = ref<any[]>([]);

// Filters
const filters = ref<FilterState>({
  asOfDate: new Date(),
  currency: 'USD',
  customerId: null,
});

// Options
const currencyOptions = [
  { name: 'US Dollar', code: 'USD', symbol: '$' },
  { name: 'Euro', code: 'EUR', symbol: '€' },
  { name: 'British Pound', code: 'GBP', symbol: '£' },
  { name: 'Pakistani Rupee', code: 'PKR', symbol: '₨' },
  { name: 'Saudi Riyal', code: 'SAR', symbol: '﷼' },
  { name: 'UAE Dirham', code: 'AED', symbol: 'د.إ' },
];

// Mock data
const customerOptions = ref([
  { id: '1', name: 'ABC Electronics', code: 'CUST001' },
  { id: '2', name: 'XYZ Corporation', code: 'CUST002' },
  { id: '3', name: 'Acme Inc.', code: 'CUST003' },
]);

// Summary data
const summary = ref<SummaryData>({
  totalReceivables: 0,
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

// Aging data
const agingData = ref<AgingData[]>([]);

// Computed
const selectedCurrency = computed(() => {
  return currencyOptions.find(c => c.code === filters.value.currency) || currencyOptions[0];
});

// Methods
const fetchAgingData = async () => {
  loading.value = true;
  
  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 800));
    
    // Generate mock data
    const mockData: AgingData[] = [];
    
    // Helper to generate random amounts
    const randomAmount = (min: number, max: number) => {
      return Math.floor(Math.random() * (max - min + 1) + min) * 10;
    };
    
    // Generate mock invoices
    customerOptions.value.forEach((customer, idx) => {
      if (filters.value.customerId && customer.id !== filters.value.customerId) return;
      
      const invoiceCount = Math.floor(Math.random() * 3) + 1; // 1-3 invoices per customer
      
      for (let i = 0; i < invoiceCount; i++) {
        const today = new Date();
        const invoiceDate = new Date();
        invoiceDate.setDate(today.getDate() - Math.floor(Math.random() * 180)); // Up to 6 months old
        
        const dueDate = new Date(invoiceDate);
        dueDate.setDate(invoiceDate.getDate() + 30); // Standard 30-day terms
        
        const daysOverdue = Math.max(0, Math.floor((today.getTime() - dueDate.getTime()) / (1000 * 60 * 60 * 24)));
        
        const originalAmount = randomAmount(500, 10000);
        const paidAmount = Math.random() > 0.7 ? randomAmount(0, originalAmount * 0.8) : 0;
        const remainingAmount = originalAmount - paidAmount;
        
        // Distribute amount across aging buckets
        let current = 0;
        let period1 = 0;
        let period2 = 0;
        let overdue = 0;
        
        if (daysOverdue <= 30) {
          current = remainingAmount;
        } else if (daysOverdue <= 60) {
          period1 = remainingAmount;
        } else if (daysOverdue <= 90) {
          period2 = remainingAmount;
        } else {
          overdue = remainingAmount;
        }
        
        mockData.push({
          id: `inv-${customer.id}-${i}`,
          customer: customer.name,
          customerEmail: `contact@${customer.name.toLowerCase().replace(/\s+/g, '')}.com`,
          invoiceNumber: `INV-${1000 + idx * 10 + i}`,
          invoiceDate: invoiceDate.toISOString().split('T')[0],
          dueDate: dueDate.toISOString().split('T')[0],
          daysOverdue,
          originalAmount,
          paidAmount,
          current,
          period1,
          period2,
          overdue,
          total: remainingAmount,
        });
      }
    });
    
    // Update reactive data
    agingData.value = mockData;
    
    // Calculate summary
    const totalReceivables = mockData.reduce((sum, item) => sum + item.total, 0);
    const currentAmount = mockData.reduce((sum, item) => sum + item.current, 0);
    const period1Amount = mockData.reduce((sum, item) => sum + item.period1, 0);
    const period2Amount = mockData.reduce((sum, item) => sum + item.period2, 0);
    const overdueAmount = mockData.reduce((sum, item) => sum + item.overdue, 0);
    
    // Mock some changes for demonstration
    const totalChange = (Math.random() * 20) - 5; // -5% to +15%
    
    summary.value = {
      totalReceivables,
      totalChange,
      currentAmount,
      currentPercentage: totalReceivables > 0 ? (currentAmount / totalReceivables) * 100 : 0,
      period1Amount,
      period1Percentage: totalReceivables > 0 ? (period1Amount / totalReceivables) * 100 : 0,
      period2Amount,
      period2Percentage: totalReceivables > 0 ? (period2Amount / totalReceivables) * 100 : 0,
      overdueAmount,
      overduePercentage: totalReceivables > 0 ? (overdueAmount / totalReceivables) * 100 : 0,
    };
    
  } catch (error) {
    console.error('Error fetching AR aging data:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load AR aging data. Please try again later.',
      life: 5000,
    });
  } finally {
    loading.value = false;
  }
};

const handleFilterChange = () => {
  fetchAgingData();
};

const exportToPdf = async () => {
  exportLoading.value = true;
  try {
    // Simulate PDF export
    await new Promise(resolve => setTimeout(resolve, 1500));
    toast.add({
      severity: 'success',
      summary: 'Export Successful',
      detail: 'AR Aging Report has been exported as PDF',
      life: 3000,
    });
  } catch (error) {
    console.error('Error exporting to PDF:', error);
    toast.add({
      severity: 'error',
      summary: 'Export Failed',
      detail: 'Failed to export report as PDF. Please try again.',
      life: 5000,
    });
  } finally {
    exportLoading.value = false;
  }
};

const exportToExcel = async () => {
  exportLoading.value = true;
  try {
    // Simulate Excel export
    await new Promise(resolve => setTimeout(resolve, 1500));
    toast.add({
      severity: 'success',
      summary: 'Export Successful',
      detail: 'AR Aging Report has been exported as Excel',
      life: 3000,
    });
  } catch (error) {
    console.error('Error exporting to Excel:', error);
    toast.add({
      severity: 'error',
      summary: 'Export Failed',
      detail: 'Failed to export report as Excel. Please try again.',
      life: 5000,
    });
  } finally {
    exportLoading.value = false;
  }
};

const printReport = () => {
  window.print();
};

const sendStatements = () => {
  const count = selectedInvoices.value.length || 'All';
  toast.add({
    severity: 'success',
    summary: 'Statements Sent',
    detail: `${count} statement(s) have been queued for sending`,
    life: 3000,
  });
};

const formatDate = (dateString: string): string => {
  if (!dateString) return '';
  const options: Intl.DateTimeFormatOptions = { year: 'numeric', month: 'short', day: 'numeric' };
  return new Date(dateString).toLocaleDateString(undefined, options);
};

const isOverdue = (dueDate: string): boolean => {
  if (!dueDate) return false;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return new Date(dueDate) < today;
};

const getDaysOverdueClass = (days: number): string => {
  if (days <= 0) return '';
  if (days <= 30) return 'text-yellow-600';
  if (days <= 90) return 'text-orange-600';
  return 'text-red-600 font-semibold';
};

const formatCurrency = (value: number): string => {
  return `${selectedCurrency.value.symbol}${Math.abs(value).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
};

// Lifecycle hooks
onMounted(() => {
  fetchAgingData();
});
</script>

<style scoped>
.ar-aging-report {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 1rem;
  background-color: var(--surface-ground);
}

.filters {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.section {
  background-color: var(--surface-card);
  border-radius: 6px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.section h3 {
  margin: 0;
  color: var(--text-color);
  font-size: 1.25rem;
  font-weight: 600;
}

.customer-cell {
  display: flex;
  flex-direction: column;
}

.customer-name {
  font-weight: 500;
}

.customer-email {
  font-size: 0.8rem;
  color: var(--text-color-secondary);
}

.text-red-500 {
  color: #ef4444;
}

.text-yellow-600 {
  color: #ca8a04;
}

.text-orange-600 {
  color: #ea580c;
}

.text-right {
  text-align: right;
}

.font-bold {
  font-weight: 700;
}

.font-semibold {
  font-weight: 600;
}

/* Print styles */
@media print {
  .p-datatable .p-datatable-thead > tr > th,
  .p-datatable .p-datatable-tbody > tr > td {
    padding: 0.5rem !important;
    font-size: 0.8rem !important;
  }
  
  .p-datatable .p-datatable-thead > tr > th {
    background-color: #f8f9fa !important;
    color: #495057 !important;
  }
  
  .p-datatable .p-datatable-tbody > tr:nth-child(even) {
    background-color: #f8f9fa !important;
  }
  
  .section {
    page-break-inside: avoid;
    break-inside: avoid;
  }
  
  .section h3 {
    page-break-after: avoid;
    break-after: avoid;
  }
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .filters {
    grid-template-columns: 1fr;
  }
  
  .summary-cards {
    grid-template-columns: 1fr;
  }
}
</style>
