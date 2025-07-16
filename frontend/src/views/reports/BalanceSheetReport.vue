<template>
  <div class="balance-sheet-report">
    <ReportHeader 
      title="Balance Sheet"
      :loading="loading"
      :date-range="dateRange"
      :export-loading="exportLoading"
      @date-range-update="handleDateRangeUpdate"
      @export="handleExport"
    >
      <template #filters>
        <div class="filters">
          <div class="p-field">
            <label for="asOfDate">As of Date</label>
            <Calendar 
              id="asOfDate"
              v-model="asOfDate" 
              :showIcon="true"
              dateFormat="yy-mm-dd"
              :maxDate="new Date()"
            />
          </div>
          
          <div class="p-field">
            <label for="compareWith">Compare With</label>
            <Dropdown
              id="compareWith"
              v-model="compareWith"
              :options="compareOptions"
              optionLabel="name"
              optionValue="value"
              placeholder="Select comparison"
            />
          </div>
          
          <div class="p-field">
            <label for="displayFormat">Display Format</label>
            <Dropdown
              id="displayFormat"
              v-model="displayFormat"
              :options="displayFormats"
              optionLabel="name"
              optionValue="value"
            />
          </div>
        </div>
      </template>
    </ReportHeader>

    <div class="report-content">
      <div class="summary-cards">
        <SummaryCard 
          title="Total Assets" 
          :value="formatCurrency(summary.totalAssets)" 
          icon="pi pi-wallet"
          :trend="summary.assetsTrend"
          :trend-percentage="summary.assetsChange"
        />
        <SummaryCard 
          title="Total Liabilities" 
          :value="formatCurrency(summary.totalLiabilities)" 
          icon="pi pi-credit-card"
          :trend="summary.liabilitiesTrend"
          :trend-percentage="summary.liabilitiesChange"
        />
        <SummaryCard 
          title="Total Equity" 
          :value="formatCurrency(summary.totalEquity)" 
          icon="pi pi-chart-line"
          :trend="summary.equityTrend"
          :trend-percentage="summary.equityChange"
        />
      </div>

      <div class="report-sections">
        <div class="section">
          <h3>Assets</h3>
          <DataTable 
            :value="assets" 
            :loading="loading"
            :scrollable="true"
            scrollHeight="flex"
            class="p-datatable-sm"
            responsiveLayout="scroll"
          >
            <Column field="account" header="Account" :sortable="true" />
            <Column field="current" header="Current" :sortable="true">
              <template #body="{ data }">
                {{ formatCurrency(data.current) }}
              </template>
            </Column>
            <Column v-if="showComparison" field="previous" header="Previous" :sortable="true">
              <template #body="{ data }">
                {{ formatCurrency(data.previous) }}
              </template>
            </Column>
            <Column field="change" header="Change" :sortable="true">
              <template #body="{ data }">
                <span :class="getChangeClass(data.change)">
                  {{ formatPercentage(data.change) }}
                </span>
              </template>
            </Column>
            <Column field="percentage" header="% of Total" :sortable="true">
              <template #body="{ data }">
                <div class="percentage-bar">
                  <div 
                    class="percentage-fill" 
                    :style="{ width: Math.min(data.percentage, 100) + '%' }"
                  ></div>
                  <span class="percentage-text">{{ formatPercentage(data.percentage, 1) }}</span>
                </div>
              </template>
            </Column>
          </DataTable>
        </div>

        <div class="section">
          <h3>Liabilities & Equity</h3>
          <DataTable 
            :value="liabilitiesAndEquity" 
            :loading="loading"
            :scrollable="true"
            scrollHeight="flex"
            class="p-datatable-sm"
            responsiveLayout="scroll"
          >
            <Column field="account" header="Account" :sortable="true" />
            <Column field="current" header="Current" :sortable="true">
              <template #body="{ data }">
                {{ formatCurrency(data.current) }}
              </template>
            </Column>
            <Column v-if="showComparison" field="previous" header="Previous" :sortable="true">
              <template #body="{ data }">
                {{ formatCurrency(data.previous) }}
              </template>
            </Column>
            <Column field="change" header="Change" :sortable="true">
              <template #body="{ data }">
                <span :class="getChangeClass(data.change)">
                  {{ formatPercentage(data.change) }}
                </span>
              </template>
            </Column>
            <Column field="percentage" header="% of Total" :sortable="true">
              <template #body="{ data }">
                <div class="percentage-bar">
                  <div 
                    class="percentage-fill" 
                    :style="{ width: Math.min(data.percentage, 100) + '%' }"
                  ></div>
                  <span class="percentage-text">{{ formatPercentage(data.percentage, 1) }}</span>
                </div>
              </template>
            </Column>
          </DataTable>
        </div>
      </div>

      <div class="ratios-section">
        <h3>Financial Ratios</h3>
        <div class="ratios-grid">
          <div class="ratio-card" v-for="ratio in financialRatios" :key="ratio.name">
            <div class="ratio-name">{{ ratio.name }}</div>
            <div class="ratio-value">{{ ratio.value }}</div>
            <div class="ratio-description">{{ ratio.description }}</div>
          </div>
        </div>
      </div>
    </div>

    <div class="report-footer">
      <div class="print-options">
        <Button 
          icon="pi pi-print" 
          label="Print Report" 
          class="p-button-text"
          @click="printReport"
        />
        <Button 
          icon="pi pi-download" 
          label="Export to PDF" 
          class="p-button-text"
          @click="exportToPDF"
        />
      </div>
      <div class="report-info">
        Generated on {{ formatDate(new Date(), 'PPpp') }} by {{ currentUser?.name || 'System' }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useStore } from 'vuex';
import { format } from 'date-fns';
import { useToast } from 'primevue/usetoast';
import { useReport } from '@/composables/useReport';
import { formatCurrency, formatPercentage, formatDate } from '@/utils/formatters';
import ReportHeader from '@/components/reports/ReportHeader.vue';
import SummaryCard from '@/components/reports/SummaryCard.vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Calendar from 'primevue/calendar';
import Dropdown from 'primevue/dropdown';
import Button from 'primevue/button';

// Initialize necessary hooks and store
const router = useRouter();
const route = useRoute();
const store = useStore();
const toast = useToast();
const { dateRange, loading, exportLoading, handleDateRangeUpdate } = useReport();

// Component state
const asOfDate = ref(new Date());
const compareWith = ref('previous_period');
const displayFormat = ref('standard');

// Computed properties
const currentUser = computed(() => store.state.auth.user);
const showComparison = computed(() => compareWith.value !== 'none');

// Mock data - Replace with actual API calls
const summary = ref({
  totalAssets: 1250000,
  totalLiabilities: 750000,
  totalEquity: 500000,
  assetsTrend: 'up',
  liabilitiesTrend: 'down',
  equityTrend: 'up',
  assetsChange: 12.5,
  liabilitiesChange: -5.2,
  equityChange: 8.3
});

const assets = ref([
  { account: 'Current Assets', current: 500000, previous: 450000, change: 11.1, percentage: 40 },
  { account: 'Cash and Cash Equivalents', current: 200000, previous: 180000, change: 11.1, percentage: 16 },
  { account: 'Accounts Receivable', current: 150000, previous: 140000, change: 7.1, percentage: 12 },
  { account: 'Inventory', current: 100000, previous: 90000, change: 11.1, percentage: 8 },
  { account: 'Prepaid Expenses', current: 50000, previous: 40000, change: 25, percentage: 4 },
  { account: 'Non-Current Assets', current: 750000, previous: 700000, change: 7.1, percentage: 60 },
  { account: 'Property, Plant & Equipment', current: 700000, previous: 670000, change: 4.5, percentage: 56 },
  { account: 'Accumulated Depreciation', current: -150000, previous: -130000, change: -15.4, percentage: 12 },
  { account: 'Intangible Assets', current: 200000, previous: 160000, change: 25, percentage: 16 }
]);

const liabilitiesAndEquity = ref([
  { account: 'Current Liabilities', current: 300000, previous: 280000, change: 7.1, percentage: 24 },
  { account: 'Accounts Payable', current: 150000, previous: 140000, change: 7.1, percentage: 12 },
  { account: 'Short-term Debt', current: 100000, previous: 90000, change: 11.1, percentage: 8 },
  { account: 'Accrued Expenses', current: 50000, previous: 50000, change: 0, percentage: 4 },
  { account: 'Long-term Liabilities', current: 450000, previous: 420000, change: 7.1, percentage: 36 },
  { account: 'Long-term Debt', current: 400000, previous: 380000, change: 5.3, percentage: 32 },
  { account: 'Deferred Tax Liabilities', current: 50000, previous: 40000, change: 25, percentage: 4 },
  { account: 'Equity', current: 500000, previous: 460000, change: 8.7, percentage: 40 },
  { account: 'Common Stock', current: 300000, previous: 300000, change: 0, percentage: 24 },
  { account: 'Retained Earnings', current: 200000, previous: 160000, change: 25, percentage: 16 }
]);

const financialRatios = ref([
  { 
    name: 'Current Ratio', 
    value: '1.67', 
    description: 'Measures the ability to pay short-term obligations' 
  },
  { 
    name: 'Debt-to-Equity', 
    value: '1.50', 
    description: 'Indicates the relative proportion of equity and debt used' 
  },
  { 
    name: 'Return on Assets', 
    value: '8.0%', 
    description: 'Shows how profitable a company is relative to its total assets' 
  },
  { 
    name: 'Return on Equity', 
    value: '20.0%', 
    description: 'Measures the profitability of a business in relation to equity' 
  }
]);

const compareOptions = ref([
  { name: 'Previous Period', value: 'previous_period' },
  { name: 'Previous Year', value: 'previous_year' },
  { name: 'Budget', value: 'budget' },
  { name: 'None', value: 'none' }
]);

const displayFormats = ref([
  { name: 'Standard', value: 'standard' },
  { name: 'Detailed', value: 'detailed' },
  { name: 'Summary', value: 'summary' }
]);

// Methods
const getChangeClass = (change: number) => ({
  'positive-change': change > 0,
  'negative-change': change < 0,
  'no-change': change === 0
});

const fetchReportData = async () => {
  try {
    loading.value = true;
    // TODO: Replace with actual API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    console.log('Fetching balance sheet data...');
  } catch (error) {
    console.error('Error fetching balance sheet data:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load balance sheet data',
      life: 5000
    });
  } finally {
    loading.value = false;
  }
};

const handleExport = async (format: string) => {
  try {
    exportLoading.value = true;
    // TODO: Implement export functionality
    console.log(`Exporting to ${format}...`);
    toast.add({
      severity: 'success',
      summary: 'Export Started',
      detail: `Exporting balance sheet to ${format.toUpperCase()}...`,
      life: 3000
    });
  } catch (error) {
    console.error('Export error:', error);
    toast.add({
      severity: 'error',
      summary: 'Export Failed',
      detail: 'Failed to export balance sheet',
      life: 5000
    });
  } finally {
    exportLoading.value = false;
  }
};

const exportToPDF = () => {
  handleExport('pdf');
};

const printReport = () => {
  window.print();
};

// Lifecycle hooks
onMounted(() => {
  fetchReportData();
});
</script>

<style scoped>
.balance-sheet-report {
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
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.report-sections {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.section {
  background: var(--surface-card);
  border-radius: 6px;
  padding: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.section h3 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: var(--text-color);
  font-size: 1.1rem;
  border-bottom: 1px solid var(--surface-border);
  padding-bottom: 0.5rem;
}

.ratios-section {
  background: var(--surface-card);
  border-radius: 6px;
  padding: 1rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.ratios-section h3 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: var(--text-color);
  font-size: 1.1rem;
  border-bottom: 1px solid var(--surface-border);
  padding-bottom: 0.5rem;
}

.ratios-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1rem;
}

.ratio-card {
  background: var(--surface-50);
  border-radius: 4px;
  padding: 1rem;
  border-left: 4px solid var(--primary-color);
}

.ratio-name {
  font-weight: 600;
  color: var(--text-color);
  margin-bottom: 0.25rem;
}

.ratio-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--primary-color);
  margin: 0.5rem 0;
}

.ratio-description {
  font-size: 0.8rem;
  color: var(--text-color-secondary);
}

.percentage-bar {
  position: relative;
  width: 100%;
  height: 20px;
  background-color: var(--surface-200);
  border-radius: 3px;
  overflow: hidden;
}

.percentage-fill {
  height: 100%;
  background-color: var(--primary-color);
  opacity: 0.5;
  transition: width 0.3s ease;
}

.percentage-text {
  position: absolute;
  top: 50%;
  left: 8px;
  transform: translateY(-50%);
  font-size: 0.75rem;
  color: var(--text-color);
  text-shadow: 0 0 2px rgba(255, 255, 255, 0.8);
}

.positive-change {
  color: var(--green-500);
  font-weight: 600;
}

.negative-change {
  color: var(--red-500);
  font-weight: 600;
}

.no-change {
  color: var(--text-color-secondary);
}

.report-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
  padding: 1rem 0;
  border-top: 1px solid var(--surface-border);
  font-size: 0.875rem;
  color: var(--text-color-secondary);
}

.print-options {
  display: flex;
  gap: 0.5rem;
}

/* Print styles */
@media print {
  .p-datatable .p-datatable-thead > tr > th,
  .p-datatable .p-datatable-tbody > tr > td {
    padding: 0.5rem;
    font-size: 0.75rem;
  }
  
  .p-datatable .p-datatable-thead > tr > th {
    background-color: #f5f5f5 !important;
  }
  
  .p-datatable .p-datatable-tbody > tr:nth-child(even) {
    background-color: #f9f9f9 !important;
  }
  
  .p-datatable .p-datatable-tbody > tr > td {
    border: 1px solid #e0e0e0 !important;
  }
  
  .summary-cards,
  .ratios-grid {
    page-break-inside: avoid;
  }
  
  .report-sections {
    display: block;
  }
  
  .section {
    margin-bottom: 1.5rem;
    page-break-inside: avoid;
  }
  
  .print-options {
    display: none;
  }
}

/* Responsive adjustments */
@media (max-width: 1200px) {
  .report-sections {
    grid-template-columns: 1fr;
  }
  
  .summary-cards {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .summary-cards {
    grid-template-columns: 1fr;
  }
  
  .filters {
    grid-template-columns: 1fr;
  }
  
  .ratios-grid {
    grid-template-columns: 1fr;
  }
}
</style>
