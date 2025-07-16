<template>
  <div class="cash-flow-report">
    <ReportHeader 
      title="Cash Flow Report"
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
            <label for="period">Period</label>
            <Dropdown
              id="period"
              v-model="filters.period"
              :options="periodOptions"
              option-label="label"
              option-value="value"
              placeholder="Select Period"
              class="w-full"
            />
          </div>
          <div class="p-field">
            <label for="startDate">Start Date</label>
            <Calendar
              id="startDate"
              v-model="filters.startDate"
              :show-icon="true"
              date-format="yy-mm-dd"
              class="w-full"
              :disabled="filters.period !== 'custom'"
            />
          </div>
          <div class="p-field">
            <label for="endDate">End Date</label>
            <Calendar
              id="endDate"
              v-model="filters.endDate"
              :show-icon="true"
              date-format="yy-mm-dd"
              class="w-full"
              :disabled="filters.period !== 'custom'"
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
              placeholder="Select Currency"
              class="w-full"
            />
          </div>
          <div class="p-field">
            <label for="format">Format</label>
            <Dropdown
              id="format"
              v-model="filters.format"
              :options="formatOptions"
              option-label="label"
              option-value="value"
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
          title="Net Cash Flow"
          :amount="summary.netCashFlow"
          :change="summary.netCashFlowChange"
          :is-positive="summary.netCashFlow >= 0"
          icon="pi pi-arrow-right-arrow-left"
        />
        <SummaryCard
          title="Operating Activities"
          :amount="summary.operatingCashFlow"
          :change="summary.operatingCashFlowChange"
          :is-positive="summary.operatingCashFlow >= 0"
          icon="pi pi-briefcase"
        />
        <SummaryCard
          title="Investing Activities"
          :amount="summary.investingCashFlow"
          :change="summary.investingCashFlowChange"
          :is-positive="summary.investingCashFlow >= 0"
          icon="pi pi-chart-line"
        />
        <SummaryCard
          title="Financing Activities"
          :amount="summary.financingCashFlow"
          :change="summary.financingCashFlowChange"
          :is-positive="summary.financingCashFlow >= 0"
          icon="pi pi-money-bill"
        />
        <SummaryCard
          title="Beginning Cash"
          :amount="summary.beginningCash"
          icon="pi pi-wallet"
          is-static
        />
        <SummaryCard
          title="Ending Cash"
          :amount="summary.endingCash"
          icon="pi pi-credit-card"
          is-static
        />
      </div>

      <!-- Cash Flow Statement -->
      <div class="section">
        <h3>Cash Flow Statement</h3>
        
        <!-- Operating Activities -->
        <div class="mb-5">
          <h4>Cash Flows from Operating Activities</h4>
          <DataTable :value="operatingActivities" class="p-datatable-sm" responsive-layout="scroll">
            <Column field="item" header="Item" />
            <Column field="amount" header="Amount" class="text-right">
              <template #body="{ data }">
                <span :class="getAmountClass(data.amount)">
                  {{ formatCurrency(data.amount) }}
                </span>
              </template>
            </Column>
            <Column field="lastYear" header="Last Year" class="text-right">
              <template #body="{ data }">
                {{ formatCurrency(data.lastYear) }}
              </template>
            </Column>
            <Column field="change" header="Change" class="text-right">
              <template #body="{ data }">
                <span :class="getChangeClass(data.change)">
                  {{ formatPercentage(data.change) }}
                </span>
              </template>
            </Column>
          </DataTable>
          <div class="section-total">
            <span>Net Cash Provided by Operating Activities</span>
            <span class="total-amount">{{ formatCurrency(summary.operatingCashFlow) }}</span>
          </div>
        </div>

        <!-- Investing Activities -->
        <div class="mb-5">
          <h4>Cash Flows from Investing Activities</h4>
          <DataTable :value="investingActivities" class="p-datatable-sm" responsive-layout="scroll">
            <Column field="item" header="Item" />
            <Column field="amount" header="Amount" class="text-right">
              <template #body="{ data }">
                <span :class="getAmountClass(data.amount)">
                  {{ formatCurrency(data.amount) }}
                </span>
              </template>
            </Column>
            <Column field="lastYear" header="Last Year" class="text-right">
              <template #body="{ data }">
                {{ formatCurrency(data.lastYear) }}
              </template>
            </Column>
            <Column field="change" header="Change" class="text-right">
              <template #body="{ data }">
                <span :class="getChangeClass(data.change)">
                  {{ formatPercentage(data.change) }}
                </span>
              </template>
            </Column>
          </DataTable>
          <div class="section-total">
            <span>Net Cash Used in Investing Activities</span>
            <span class="total-amount">{{ formatCurrency(summary.investingCashFlow) }}</span>
          </div>
        </div>

        <!-- Financing Activities -->
        <div class="mb-5">
          <h4>Cash Flows from Financing Activities</h4>
          <DataTable :value="financingActivities" class="p-datatable-sm" responsive-layout="scroll">
            <Column field="item" header="Item" />
            <Column field="amount" header="Amount" class="text-right">
              <template #body="{ data }">
                <span :class="getAmountClass(data.amount)">
                  {{ formatCurrency(data.amount) }}
                </span>
              </template>
            </Column>
            <Column field="lastYear" header="Last Year" class="text-right">
              <template #body="{ data }">
                {{ formatCurrency(data.lastYear) }}
              </template>
            </Column>
            <Column field="change" header="Change" class="text-right">
              <template #body="{ data }">
                <span :class="getChangeClass(data.change)">
                  {{ formatPercentage(data.change) }}
                </span>
              </template>
            </Column>
          </DataTable>
          <div class="section-total">
            <span>Net Cash Used in Financing Activities</span>
            <span class="total-amount">{{ formatCurrency(summary.financingCashFlow) }}</span>
          </div>
        </div>

        <!-- Summary -->
        <div class="summary-section">
          <div class="summary-row">
            <span>Net Increase (Decrease) in Cash and Cash Equivalents</span>
            <span class="summary-amount">{{ formatCurrency(summary.netCashFlow) }}</span>
          </div>
          <div class="summary-row">
            <span>Cash and Cash Equivalents at Beginning of Period</span>
            <span class="summary-amount">{{ formatCurrency(summary.beginningCash) }}</span>
          </div>
          <div class="summary-row total">
            <span>Cash and Cash Equivalents at End of Period</span>
            <span class="summary-amount">{{ formatCurrency(summary.endingCash) }}</span>
          </div>
        </div>
      </div>

      <!-- Cash Flow Analysis -->
      <div class="section">
        <h3>Cash Flow Analysis</h3>
        <div class="analysis-grid">
          <div class="analysis-card">
            <h4>Operating Cash Flow Ratio</h4>
            <div class="metric-value">
              {{ (summary.operatingCashFlow / Math.abs(summary.netCashFlow) || 0).toFixed(2) }}
              <span class="metric-change positive">
                <i class="pi pi-arrow-up"></i>
                {{ (Math.random() * 15 + 5).toFixed(1) }}%
              </span>
            </div>
            <div class="metric-description">
              Measures cash generated from operations relative to net cash flow
            </div>
          </div>
          <div class="analysis-card">
            <h4>Free Cash Flow</h4>
            <div class="metric-value">
              {{ formatCurrency(summary.operatingCashFlow + summary.investingCashFlow) }}
              <span class="metric-change positive">
                <i class="pi pi-arrow-up"></i>
                {{ (Math.random() * 10 + 5).toFixed(1) }}%
              </span>
            </div>
            <div class="metric-description">
              Operating cash flow minus capital expenditures
            </div>
          </div>
          <div class="analysis-card">
            <h4>Cash Conversion Cycle</h4>
            <div class="metric-value">
              {{ Math.floor(Math.random() * 30) + 20 }} days
              <span class="metric-change negative">
                <i class="pi pi-arrow-down"></i>
                {{ (Math.random() * 5 + 1).toFixed(1) }}%
              </span>
            </div>
            <div class="metric-description">
              Days to convert inventory and resources into cash flows
            </div>
          </div>
        </div>
      </div>

      <!-- Cash Flow Trends -->
      <div class="section">
        <h3>12-Month Cash Flow Trend</h3>
        <div class="trend-chart">
          <!-- Placeholder for chart -->
          <div class="chart-placeholder">
            <i class="pi pi-chart-line" style="font-size: 2rem; color: var(--primary-color);"></i>
            <p>Cash flow trend chart will be displayed here</p>
          </div>
        </div>
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
  period: string;
  startDate: Date | null;
  endDate: Date | null;
  currency: string;
  format: string;
  comparison: string;
}

interface CashFlowItem {
  item: string;
  amount: number;
  lastYear: number;
  change: number;
}

interface SummaryData {
  netCashFlow: number;
  netCashFlowChange: number;
  operatingCashFlow: number;
  operatingCashFlowChange: number;
  investingCashFlow: number;
  investingCashFlowChange: number;
  financingCashFlow: number;
  financingCashFlowChange: number;
  beginningCash: number;
  endingCash: number;
}

// Toast
const toast = useToast();

// State
const loading = ref(false);
const exportLoading = ref(false);

// Filters
const filters = ref<FilterState>({
  period: 'thisMonth',
  startDate: new Date(new Date().getFullYear(), new Date().getMonth(), 1),
  endDate: new Date(),
  currency: 'USD',
  format: 'indirect',
  comparison: 'previousPeriod',
});

// Options
const periodOptions = [
  { label: 'This Month', value: 'thisMonth' },
  { label: 'Last Month', value: 'lastMonth' },
  { label: 'This Quarter', value: 'thisQuarter' },
  { label: 'Last Quarter', value: 'lastQuarter' },
  { label: 'This Year', value: 'thisYear' },
  { label: 'Last Year', value: 'lastYear' },
  { label: 'Custom', value: 'custom' },
];

const currencyOptions = [
  { name: 'US Dollar', code: 'USD', symbol: '$' },
  { name: 'Euro', code: 'EUR', symbol: '€' },
  { name: 'British Pound', code: 'GBP', symbol: '£' },
  { name: 'Japanese Yen', code: 'JPY', symbol: '¥' },
  { name: 'Pakistani Rupee', code: 'PKR', symbol: '₨' },
  { name: 'Saudi Riyal', code: 'SAR', symbol: '﷼' },
  { name: 'UAE Dirham', code: 'AED', symbol: 'د.إ' },
];

const formatOptions = [
  { label: 'Indirect Method', value: 'indirect' },
  { label: 'Direct Method', value: 'direct' },
];

const comparisonOptions = [
  { label: 'Previous Period', value: 'previousPeriod' },
  { label: 'Previous Year', value: 'previousYear' },
  { label: 'Budget', value: 'budget' },
  { label: 'Forecast', value: 'forecast' },
];

// Mock data - Replace with API calls
const operatingActivities = ref<CashFlowItem[]>([
  { item: 'Net Income', amount: 1250000, lastYear: 980000, change: 27.55 },
  { item: 'Depreciation & Amortization', amount: 320000, lastYear: 280000, change: 14.29 },
  { item: 'Accounts Receivable', amount: -185000, lastYear: -150000, change: -23.33 },
  { item: 'Inventory', amount: -225000, lastYear: -180000, change: -25.00 },
  { item: 'Accounts Payable', amount: 167000, lastYear: 145000, change: 15.17 },
  { item: 'Income Taxes Paid', amount: -285000, lastYear: -230000, change: -23.91 },
  { item: 'Other Operating Activities', amount: -42000, lastYear: -35000, change: -20.00 },
]);

const investingActivities = ref<CashFlowItem[]>([
  { item: 'Purchase of Property & Equipment', amount: -450000, lastYear: -320000, change: -40.63 },
  { item: 'Proceeds from Sale of Equipment', amount: 85000, lastYear: 60000, change: 41.67 },
  { item: 'Purchase of Investments', amount: -200000, lastYear: -150000, change: -33.33 },
  { item: 'Proceeds from Maturities of Investments', amount: 120000, lastYear: 90000, change: 33.33 },
  { item: 'Acquisitions, Net of Cash Acquired', amount: -150000, lastYear: 0, change: 0 },
]);

const financingActivities = ref<CashFlowItem[]>([
  { item: 'Proceeds from Issuance of Common Stock', amount: 250000, lastYear: 180000, change: 38.89 },
  { item: 'Dividends Paid', amount: -300000, lastYear: -275000, change: -9.09 },
  { item: 'Repayment of Long-term Debt', amount: -200000, lastYear: -150000, change: -33.33 },
  { item: 'Proceeds from Long-term Debt', amount: 400000, lastYear: 300000, change: 33.33 },
  { item: 'Repurchase of Common Stock', amount: -100000, lastYear: -80000, change: -25.00 },
]);

const summary = ref<SummaryData>({
  netCashFlow: 0,
  netCashFlowChange: 0,
  operatingCashFlow: 0,
  operatingCashFlowChange: 0,
  investingCashFlow: 0,
  investingCashFlowChange: 0,
  financingCashFlow: 0,
  financingCashFlowChange: 0,
  beginningCash: 2500000,
  endingCash: 0,
});

// Computed
const selectedCurrency = computed(() => {
  return currencyOptions.find(c => c.code === filters.value.currency) || currencyOptions[0];
});

// Methods
const fetchCashFlowData = async () => {
  loading.value = true;
  
  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 800));
    
    // Calculate summary data from mock data
    const operatingTotal = operatingActivities.value.reduce((sum, item) => sum + item.amount, 0);
    const investingTotal = investingActivities.value.reduce((sum, item) => sum + item.amount, 0);
    const financingTotal = financingActivities.value.reduce((sum, item) => sum + item.amount, 0);
    const netCashFlow = operatingTotal + investingTotal + financingTotal;
    
    // Update summary
    summary.value = {
      operatingCashFlow: operatingTotal,
      operatingCashFlowChange: 12.5, // Mocked change percentage
      investingCashFlow: investingTotal,
      investingCashFlowChange: -8.3, // Mocked change percentage
      financingCashFlow: financingTotal,
      financingCashFlowChange: 5.7, // Mocked change percentage
      netCashFlow,
      netCashFlowChange: 15.2, // Mocked change percentage
      beginningCash: summary.value.beginningCash,
      endingCash: summary.value.beginningCash + netCashFlow,
    };
    
  } catch (error) {
    console.error('Error fetching cash flow data:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load cash flow data. Please try again later.',
      life: 5000,
    });
  } finally {
    loading.value = false;
  }
};

const handleFilterChange = () => {
  fetchCashFlowData();
};

const exportToPdf = async () => {
  exportLoading.value = true;
  try {
    // Simulate PDF export
    await new Promise(resolve => setTimeout(resolve, 1500));
    toast.add({
      severity: 'success',
      summary: 'Export Successful',
      detail: 'Cash Flow Report has been exported as PDF',
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
      detail: 'Cash Flow Report has been exported as Excel',
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

const formatCurrency = (value: number): string => {
  if (value >= 0) {
    return `${selectedCurrency.value.symbol}${Math.abs(value).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  } else {
    return `(${selectedCurrency.value.symbol}${Math.abs(value).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })})`;
  }
};

const formatPercentage = (value: number): string => {
  if (value > 0) {
    return `+${value.toFixed(2)}%`;
  } else if (value < 0) {
    return `${value.toFixed(2)}%`;
  } else {
    return '0.00%';
  }
};

const getAmountClass = (amount: number): string => {
  return amount >= 0 ? 'positive-amount' : 'negative-amount';
};

const getChangeClass = (change: number): string => {
  if (change > 0) return 'positive-change';
  if (change < 0) return 'negative-change';
  return 'no-change';
};

// Lifecycle hooks
onMounted(() => {
  fetchCashFlowData();
});
</script>

<style scoped>
.cash-flow-report {
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
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
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

.section h3 {
  margin-top: 0;
  margin-bottom: 1.25rem;
  color: var(--text-color);
  font-size: 1.25rem;
  font-weight: 600;
  border-bottom: 1px solid var(--surface-border);
  padding-bottom: 0.5rem;
}

.section h4 {
  margin: 1.5rem 0 1rem;
  color: var(--text-color-secondary);
  font-size: 1rem;
  font-weight: 600;
}

.section-total {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background-color: var(--surface-50);
  border-radius: 4px;
  font-weight: 600;
  margin-top: 0.5rem;
}

.total-amount {
  font-weight: 700;
  color: var(--primary-color);
}

.positive-amount {
  color: var(--green-600);
  font-weight: 500;
}

.negative-amount {
  color: var(--red-600);
  font-weight: 500;
}

.positive-change {
  color: var(--green-600);
  font-weight: 600;
}

.negative-change {
  color: var(--red-600);
  font-weight: 600;
}

.no-change {
  color: var(--text-color-secondary);
}

.summary-section {
  margin-top: 2rem;
  border-top: 1px solid var(--surface-border);
  padding-top: 1rem;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--surface-border);
}

.summary-row.total {
  font-weight: 700;
  font-size: 1.1rem;
  border-bottom: none;
  padding-top: 1rem;
  margin-top: 0.5rem;
  border-top: 2px solid var(--surface-border);
}

.summary-amount {
  font-family: 'Roboto Mono', monospace;
  font-weight: 500;
}

.analysis-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-top: 1rem;
}

.analysis-card {
  background-color: var(--surface-50);
  border-radius: 6px;
  padding: 1.25rem;
  border-left: 4px solid var(--primary-color);
}

.analysis-card h4 {
  margin: 0 0 0.75rem;
  font-size: 0.95rem;
  color: var(--text-color);
}

.metric-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--primary-color);
  margin-bottom: 0.5rem;
}

.metric-change {
  font-size: 0.85rem;
  font-weight: 500;
  margin-left: 0.5rem;
}

.metric-change.positive {
  color: var(--green-600);
}

.metric-change.negative {
  color: var(--red-600);
}

.metric-description {
  font-size: 0.85rem;
  color: var(--text-color-secondary);
  line-height: 1.5;
}

.trend-chart {
  height: 350px;
  background-color: var(--surface-card);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px dashed var(--surface-border);
  margin-top: 1rem;
}

.chart-placeholder {
  text-align: center;
  color: var(--text-color-secondary);
}

.chart-placeholder i {
  font-size: 2.5rem;
  margin-bottom: 1rem;
  opacity: 0.7;
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
@media (max-width: 992px) {
  .summary-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .analysis-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .filters {
    grid-template-columns: 1fr;
  }
  
  .summary-cards {
    grid-template-columns: 1fr;
  }
}
</style>
