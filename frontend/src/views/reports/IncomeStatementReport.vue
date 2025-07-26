<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useStore } from 'vuex';
import { useToast } from 'vue/usetoast';
import enhancedReportsService from '@/services/enhancedReportsService';
import { formatCurrency, formatPercentage, formatDate } from '@/utils/formatters';
import ReportHeader from '@/components/reports/ReportHeader.vue';
import SummaryCard from '@/components/reports/SummaryCard.vue';
import DataTable from 'vue/datatable';
import Column from 'vue/column';
import Dropdown from 'vue/dropdown';
import Button from 'vue/button';

// Initialize necessary hooks and store
const router = useRouter();
const route = useRoute();
const store = useStore();
const toast = useToast();
const loading = ref(false);
const exportLoading = ref(false);
const dateRange = ref({ start: new Date(), end: new Date() });

// Component state
const reportingPeriod = ref('this_month');
const compareWith = ref('previous_period');
const displayFormat = ref('standard');
const currency = ref('USD');

// Computed properties
const currentUser = computed(() => store.state.auth.user);
const showComparison = computed(() => compareWith.value !== 'none');

// Mock data - Replace with actual API calls
const summary = ref({
  // Revenue
  totalRevenue: 1250000,
  previousTotalRevenue: 1100000,
  revenueChange: 13.6,
  revenueTrend: 'up',
  
  // Expenses
  totalExpenses: 1050000,
  previousTotalExpenses: 1002000,
  expensesChange: 4.8,
  expensesTrend: 'up',
  
  // COGS
  totalCogs: 750000,
  previousTotalCogs: 700000,
  cogsChange: 7.1,
  
  // Gross Profit
  grossProfit: 500000,
  previousGrossProfit: 400000,
  grossProfitChange: 25.0,
  grossMargin: 40.0,
  previousGrossMargin: 36.4,
  grossMarginChange: 3.6,
  
  // Operating Expenses
  totalOperatingExpenses: 300000,
  previousTotalOperatingExpenses: 280000,
  operatingExpensesChange: 7.1,
  operatingExpenseRatio: 24.0,
  operatingExpenseRatioChange: -1.5,
  
  // Operating Income
  operatingIncome: 200000,
  previousOperatingIncome: 120000,
  operatingIncomeChange: 66.7,
  operatingMargin: 16.0,
  previousOperatingMargin: 10.9,
  operatingMarginChange: 5.1,
  
  // Other Income/Expenses
  otherIncome: 50000,
  otherExpenses: 30000,
  
  // Tax & Net Income
  incomeBeforeTax: 220000,
  previousIncomeBeforeTax: 140000,
  incomeBeforeTaxChange: 57.1,
  
  incomeTaxExpense: 66000, // 30% tax rate for example
  previousIncomeTaxExpense: 42000,
  incomeTaxExpenseChange: 57.1,
  
  netIncome: 154000,
  previousNetIncome: 98000,
  netIncomeChange: 57.1,
  
  // Profitability Metrics
  profitMargin: 12.3,
  previousProfitMargin: 8.9,
  profitMarginChange: 3.4,
  
  ebitda: 275000,
  previousEbitda: 185000,
  ebitdaChange: 48.6,
  
  ebitdaMargin: 22.0,
  previousEbitdaMargin: 16.8,
  ebitdaMarginChange: 5.2,
});

// Mock data for report items
const revenueItems = ref([
  { 
    account: 'Product Sales', 
    current: 1000000, 
    previous: 850000, 
    change: 17.6, 
    percentage: 80.0,
    type: 'revenue'
  },
  { 
    account: 'Service Revenue', 
    current: 200000, 
    previous: 200000, 
    change: 0, 
    percentage: 16.0,
    type: 'revenue'
  },
  { 
    account: 'Subscription Revenue', 
    current: 50000, 
    previous: 50000, 
    change: 0, 
    percentage: 4.0,
    type: 'revenue'
  },
]);

const cogsItems = ref([
  { 
    account: 'Cost of Goods Sold', 
    current: 600000, 
    previous: 550000, 
    change: 9.1, 
    percentage: 48.0,
    type: 'cogs'
  },
  { 
    account: 'Direct Labor', 
    current: 100000, 
    previous: 100000, 
    change: 0, 
    percentage: 8.0,
    type: 'cogs'
  },
  { 
    account: 'Freight & Shipping', 
    current: 50000, 
    previous: 50000, 
    change: 0, 
    percentage: 4.0,
    type: 'cogs'
  },
]);

const expenseItems = ref([
  { 
    account: 'Salaries & Wages', 
    current: 150000, 
    previous: 140000, 
    change: 7.1, 
    percentage: 12.0,
    type: 'expense'
  },
  { 
    account: 'Rent & Utilities', 
    current: 50000, 
    previous: 50000, 
    change: 0, 
    percentage: 4.0,
    type: 'expense'
  },
  { 
    account: 'Marketing & Advertising', 
    current: 40000, 
    previous: 45000, 
    change: -11.1, 
    percentage: 3.2,
    type: 'expense'
  },
  { 
    account: 'Office Expenses', 
    current: 20000, 
    previous: 18000, 
    change: 11.1, 
    percentage: 1.6,
    type: 'expense'
  },
  { 
    account: 'Depreciation & Amortization', 
    current: 25000, 
    previous: 22000, 
    change: 13.6, 
    percentage: 2.0,
    type: 'expense'
  },
  { 
    account: 'Professional Fees', 
    current: 15000, 
    previous: 15000, 
    change: 0, 
    percentage: 1.2,
    type: 'expense'
  },
]);

const otherItems = ref([
  { 
    account: 'Interest Income', 
    current: 10000, 
    previous: 8000, 
    change: 25.0, 
    percentage: 0.8,
    type: 'income'
  },
  { 
    account: 'Interest Expense', 
    current: -15000, 
    previous: -12000, 
    change: -25.0, 
    percentage: -1.2,
    type: 'expense'
  },
  { 
    account: 'Gain/Loss on Asset Sales', 
    current: 5000, 
    previous: 0, 
    change: 0, 
    percentage: 0.4,
    type: 'income'
  },
]);

// Dropdown options
const reportingPeriods = ref([
  { name: 'This Month', value: 'this_month' },
  { name: 'Last Month', value: 'last_month' },
  { name: 'This Quarter', value: 'this_quarter' },
  { name: 'Last Quarter', value: 'last_quarter' },
  { name: 'This Year', value: 'this_year' },
  { name: 'Last Year', value: 'last_year' },
  { name: 'Custom', value: 'custom' },
]);

const compareOptions = ref([
  { name: 'Previous Period', value: 'previous_period' },
  { name: 'Previous Year', value: 'previous_year' },
  { name: 'Budget', value: 'budget' },
  { name: 'Forecast', value: 'forecast' },
  { name: 'None', value: 'none' },
]);

const displayFormats = ref([
  { name: 'Standard', value: 'standard' },
  { name: 'Detailed', value: 'detailed' },
  { name: 'Summary', value: 'summary' },
]);

const currencies = ref([
  { name: 'US Dollar (USD)', code: 'USD' },
  { name: 'Euro (EUR)', code: 'EUR' },
  { name: 'British Pound (GBP)', code: 'GBP' },
  { name: 'Japanese Yen (JPY)', code: 'JPY' },
  { name: 'Saudi Riyal (SAR)', code: 'SAR' },
  { name: 'UAE Dirham (AED)', code: 'AED' },
  { name: 'Pakistani Rupee (PKR)', code: 'PKR' },
]);

// Methods
const getChangeClass = (change: number) => {
  if (change > 0) return 'positive-change';
  if (change < 0) return 'negative-change';
  return 'no-change';
};

const getMarginClass = (margin: number, change: number) => {
  if (margin > 0) return 'positive-margin';
  if (margin < 0) return 'negative-margin';
  return 'neutral-margin';
};

const getRowClass = (data: any) => {
  return data.type || '';
};

const getPercentageColor = (value: number, section: string) => {
  if (section === 'revenue') return 'var(--primary-color)';
  if (section === 'cogs') return 'var(--red-500)';
  if (section === 'expenses') return 'var(--orange-500)';
  if (section === 'other') return value >= 0 ? 'var(--green-500)' : 'var(--pink-500)';
  return 'var(--primary-color)';
};

const fetchReportData = async () => {
  try {
    loading.value = true;
    const companyId = store.state.auth.currentCompany?.id || 'default-company';
    
    const report = await enhancedReportsService.generateIncomeStatement(
      companyId,
      dateRange.value.start,
      dateRange.value.end
    );
    
    if (report.data?.report_data) {
      updateSummaryFromReportData(report.data.report_data);
    }
  } catch (error) {
    console.error('Error fetching income statement data:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load income statement data',
      life: 5000
    });
  } finally {
    loading.value = false;
  }
};

const updateSummaryFromReportData = (reportData: any) => {
  if (reportData.revenue) {
    summary.value.totalRevenue = reportData.revenue.total_revenue;
  }
  if (reportData.expenses) {
    summary.value.totalExpenses = reportData.expenses.total_expenses;
  }
  summary.value.netIncome = reportData.net_income || 0;
};

const handleExport = async (format: string) => {
  try {
    exportLoading.value = true;
    const companyId = store.state.auth.currentCompany?.id || 'default-company';
    
    const report = await enhancedReportsService.generateIncomeStatement(
      companyId,
      dateRange.value.start,
      dateRange.value.end
    );
    
    if (report.data?.id) {
      if (format === 'pdf') {
        await enhancedReportsService.exportReportToPDF(report.data.id);
      } else if (format === 'excel') {
        await enhancedReportsService.exportReportToExcel(report.data.id);
      } else if (format === 'csv') {
        await enhancedReportsService.exportReportToCSV(report.data.id);
      }
    }
    
    toast.add({
      severity: 'success',
      summary: 'Export Started',
      detail: `Exporting income statement to ${format.toUpperCase()}...`,
      life: 3000
    });
  } catch (error) {
    console.error('Export error:', error);
    toast.add({
      severity: 'error',
      summary: 'Export Failed',
      detail: 'Failed to export income statement',
      life: 5000
    });
  } finally {
    exportLoading.value = false;
  }
};

const exportToPDF = () => {
  handleExport('pdf');
};

const exportToExcel = () => {
  handleExport('excel');
};

const printReport = () => {
  window.print();
};

// Lifecycle hooks
onMounted(() => {
  fetchReportData();
});
</script>

<template>
  <div class="income-statement-report">
    <ReportHeader 
      title="Income Statement"
      :loading="loading"
      :date-range="dateRange"
      :export-loading="exportLoading"
      @date-range-update="handleDateRangeUpdate"
      @export="handleExport"
    >
      <template #filters>
        <div class="filters">
          <div class="p-field">
            <label for="reportingPeriod">Reporting Period</label>
            <Dropdown
              id="reportingPeriod"
              v-model="reportingPeriod"
              :options="reportingPeriods"
              optionLabel="name"
              optionValue="value"
              placeholder="Select period"
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
          
          <div class="p-field">
            <label for="currency">Currency</label>
            <Dropdown
              id="currency"
              v-model="currency"
              :options="currencies"
              optionLabel="name"
              optionValue="code"
            />
          </div>
        </div>
      </template>
    </ReportHeader>

    <div class="report-content">
      <div class="summary-cards">
        <SummaryCard 
          title="Total Revenue" 
          :value="formatCurrency(summary.totalRevenue, currency)" 
          icon="pi pi-arrow-up-circle"
          :trend="summary.revenueTrend"
          :trend-percentage="summary.revenueChange"
          class="revenue-card"
        />
        <SummaryCard 
          title="Total Expenses" 
          :value="formatCurrency(summary.totalExpenses, currency)" 
          icon="pi pi-arrow-down-circle"
          :trend="summary.expensesTrend"
          :trend-percentage="summary.expensesChange"
          class="expenses-card"
        />
        <SummaryCard 
          title="Net Income" 
          :value="formatCurrency(summary.netIncome, currency)" 
          :icon="summary.netIncome >= 0 ? 'pi pi-arrow-up-circle' : 'pi pi-arrow-down-circle'"
          :trend="summary.netIncome >= 0 ? 'up' : 'down'"
          :trend-percentage="Math.abs(summary.netIncomeChange)"
          :class="{ 'profit': summary.netIncome >= 0, 'loss': summary.netIncome < 0 }"
        />
      </div>

      <!-- Revenue Section -->
      <div class="section revenue-section">
        <h3>Revenue</h3>
        <DataTable 
          :value="revenueItems" 
          :loading="loading"
          :scrollable="true"
          scrollHeight="flex"
          class="p-datatable-sm"
          responsiveLayout="scroll"
          :rowClass="getRowClass"
        >
          <Column field="account" header="Account" :sortable="true" />
          <Column field="current" header="Current" :sortable="true">
            <template #body="{ data }">
              {{ formatCurrency(data.current, currency) }}
            </template>
          </Column>
          <Column v-if="showComparison" field="previous" header="Previous" :sortable="true">
            <template #body="{ data }">
              {{ formatCurrency(data.previous, currency) }}
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
                  :style="{ 
                    width: Math.min(data.percentage, 100) + '%',
                    backgroundColor: getPercentageColor(data.percentage, 'revenue')
                  }"
                ></div>
                <span class="percentage-text">{{ formatPercentage(data.percentage, 1) }}</span>
              </div>
            </template>
          </Column>
          <template #footer v-if="revenueItems.length > 0">
            <tr class="p-datatable-emptymessage">
              <td>Total Revenue</td>
              <td>{{ formatCurrency(summary.totalRevenue, currency) }}</td>
              <td v-if="showComparison">{{ formatCurrency(summary.previousTotalRevenue, currency) }}</td>
              <td :class="getChangeClass(summary.revenueChange)">
                {{ formatPercentage(summary.revenueChange) }}
              </td>
              <td></td>
            </tr>
          </template>
        </DataTable>
      </div>

      <!-- COGS Section -->
      <div class="section cogs-section">
        <h3>Cost of Goods Sold</h3>
        <DataTable 
          :value="cogsItems" 
          :loading="loading"
          :scrollable="true"
          scrollHeight="flex"
          class="p-datatable-sm"
          responsiveLayout="scroll"
          :rowClass="getRowClass"
        >
          <Column field="account" header="Account" :sortable="true" />
          <Column field="current" header="Current" :sortable="true">
            <template #body="{ data }">
              {{ formatCurrency(data.current, currency) }}
            </template>
          </Column>
          <Column v-if="showComparison" field="previous" header="Previous" :sortable="true">
            <template #body="{ data }">
              {{ formatCurrency(data.previous, currency) }}
            </template>
          </Column>
          <Column field="change" header="Change" :sortable="true">
            <template #body="{ data }">
              <span :class="getChangeClass(data.change)">
                {{ formatPercentage(data.change) }}
              </span>
            </template>
          </Column>
          <Column field="percentage" header="% of Revenue" :sortable="true">
            <template #body="{ data }">
              <div class="percentage-bar">
                <div 
                  class="percentage-fill" 
                  :style="{ 
                    width: Math.min(data.percentage, 100) + '%',
                    backgroundColor: getPercentageColor(data.percentage, 'cogs')
                  }"
                ></div>
                <span class="percentage-text">{{ formatPercentage(data.percentage, 1) }}</span>
              </div>
            </template>
          </Column>
          <template #footer v-if="cogsItems.length > 0">
            <tr class="p-datatable-emptymessage">
              <td>Total COGS</td>
              <td>{{ formatCurrency(summary.totalCogs, currency) }}</td>
              <td v-if="showComparison">{{ formatCurrency(summary.previousTotalCogs, currency) }}</td>
              <td :class="getChangeClass(summary.cogsChange)">
                {{ formatPercentage(summary.cogsChange) }}
              </td>
              <td></td>
            </tr>
            <tr class="gross-profit-row">
              <td><strong>Gross Profit</strong></td>
              <td><strong>{{ formatCurrency(summary.grossProfit, currency) }}</strong></td>
              <td v-if="showComparison"><strong>{{ formatCurrency(summary.previousGrossProfit, currency) }}</strong></td>
              <td :class="getChangeClass(summary.grossProfitChange)">
                <strong>{{ formatPercentage(summary.grossProfitChange) }}</strong>
              </td>
              <td>
                <div class="gross-margin">
                  <strong>Gross Margin: {{ formatPercentage(summary.grossMargin, 1) }}</strong>
                  <span 
                    class="margin-change" 
                    :class="getChangeClass(summary.grossMarginChange)"
                  >
                    ({{ formatPercentage(summary.grossMarginChange, 1) }})
                  </span>
                </div>
              </td>
            </tr>
          </template>
        </DataTable>
      </div>

      <!-- Operating Expenses Section -->
      <div class="section expenses-section">
        <h3>Operating Expenses</h3>
        <DataTable 
          :value="expenseItems" 
          :loading="loading"
          :scrollable="true"
          scrollHeight="flex"
          class="p-datatable-sm"
          responsiveLayout="scroll"
          :rowClass="getRowClass"
        >
          <Column field="account" header="Account" :sortable="true" />
          <Column field="current" header="Current" :sortable="true">
            <template #body="{ data }">
              {{ formatCurrency(data.current, currency) }}
            </template>
          </Column>
          <Column v-if="showComparison" field="previous" header="Previous" :sortable="true">
            <template #body="{ data }">
              {{ formatCurrency(data.previous, currency) }}
            </template>
          </Column>
          <Column field="change" header="Change" :sortable="true">
            <template #body="{ data }">
              <span :class="getChangeClass(data.change)">
                {{ formatPercentage(data.change) }}
              </span>
            </template>
          </Column>
          <Column field="percentage" header="% of Revenue" :sortable="true">
            <template #body="{ data }">
              <div class="percentage-bar">
                <div 
                  class="percentage-fill" 
                  :style="{ 
                    width: Math.min(data.percentage, 100) + '%',
                    backgroundColor: getPercentageColor(data.percentage, 'expenses')
                  }"
                ></div>
                <span class="percentage-text">{{ formatPercentage(data.percentage, 1) }}</span>
              </div>
            </template>
          </Column>
          <template #footer v-if="expenseItems.length > 0">
            <tr class="p-datatable-emptymessage">
              <td>Total Operating Expenses</td>
              <td>{{ formatCurrency(summary.totalOperatingExpenses, currency) }}</td>
              <td v-if="showComparison">{{ formatCurrency(summary.previousTotalOperatingExpenses, currency) }}</td>
              <td :class="getChangeClass(summary.operatingExpensesChange)">
                {{ formatPercentage(summary.operatingExpensesChange) }}
              </td>
              <td>
                <div class="expense-ratio">
                  {{ formatPercentage(summary.operatingExpenseRatio, 1) }} of Revenue
                  <span 
                    class="ratio-change" 
                    :class="getChangeClass(-summary.operatingExpenseRatioChange)"
                  >
                    ({{ formatPercentage(summary.operatingExpenseRatioChange, 1) }})
                  </span>
                </div>
              </td>
            </tr>
            <tr class="operating-income-row">
              <td><strong>Operating Income</strong></td>
              <td><strong>{{ formatCurrency(summary.operatingIncome, currency) }}</strong></td>
              <td v-if="showComparison"><strong>{{ formatCurrency(summary.previousOperatingIncome, currency) }}</strong></td>
              <td :class="getChangeClass(summary.operatingIncomeChange)">
                <strong>{{ formatPercentage(summary.operatingIncomeChange) }}</strong>
              </td>
              <td>
                <div class="operating-margin">
                  <strong>Operating Margin: {{ formatPercentage(summary.operatingMargin, 1) }}</strong>
                  <span 
                    class="margin-change" 
                    :class="getChangeClass(summary.operatingMarginChange)"
                  >
                    ({{ formatPercentage(summary.operatingMarginChange, 1) }})
                  </span>
                </div>
              </td>
            </tr>
          </template>
        </DataTable>
      </div>

      <!-- Other Income/Expenses Section -->
      <div class="section other-section">
        <h3>Other Income & Expenses</h3>
        <DataTable 
          :value="otherItems" 
          :loading="loading"
          :scrollable="true"
          scrollHeight="flex"
          class="p-datatable-sm"
          responsiveLayout="scroll"
          :rowClass="getRowClass"
        >
          <Column field="account" header="Account" :sortable="true" />
          <Column field="current" header="Current" :sortable="true">
            <template #body="{ data }">
              {{ formatCurrency(data.current, currency) }}
            </template>
          </Column>
          <Column v-if="showComparison" field="previous" header="Previous" :sortable="true">
            <template #body="{ data }">
              {{ formatCurrency(data.previous, currency) }}
            </template>
          </Column>
          <Column field="change" header="Change" :sortable="true">
            <template #body="{ data }">
              <span :class="getChangeClass(data.change)">
                {{ formatPercentage(data.change) }}
              </span>
            </template>
          </Column>
          <Column field="percentage" header="% of Revenue" :sortable="true">
            <template #body="{ data }">
              <div class="percentage-bar">
                <div 
                  class="percentage-fill" 
                  :style="{ 
                    width: Math.min(Math.abs(data.percentage), 100) + '%',
                    backgroundColor: getPercentageColor(data.percentage, 'other')
                  }"
                ></div>
                <span class="percentage-text">{{ formatPercentage(data.percentage, 1) }}</span>
              </div>
            </template>
          </Column>
        </DataTable>
      </div>

      <!-- Tax & Net Income Section -->
      <div class="section summary-section">
        <div class="summary-grid">
          <div class="summary-row">
            <div class="summary-label">Income Before Tax</div>
            <div class="summary-amount">{{ formatCurrency(summary.incomeBeforeTax, currency) }}</div>
            <div v-if="showComparison" class="summary-previous">
              {{ formatCurrency(summary.previousIncomeBeforeTax, currency) }}
            </div>
            <div class="summary-change" :class="getChangeClass(summary.incomeBeforeTaxChange)">
              {{ formatPercentage(summary.incomeBeforeTaxChange) }}
            </div>
          </div>
          
          <div class="summary-row">
            <div class="summary-label">Income Tax Expense</div>
            <div class="summary-amount">{{ formatCurrency(summary.incomeTaxExpense, currency) }}</div>
            <div v-if="showComparison" class="summary-previous">
              {{ formatCurrency(summary.previousIncomeTaxExpense, currency) }}
            </div>
            <div class="summary-change" :class="getChangeClass(summary.incomeTaxExpenseChange)">
              {{ formatPercentage(summary.incomeTaxExpenseChange) }}
            </div>
          </div>
          
          <div class="summary-row total">
            <div class="summary-label">Net Income</div>
            <div class="summary-amount">{{ formatCurrency(summary.netIncome, currency) }}</div>
            <div v-if="showComparison" class="summary-previous">
              {{ formatCurrency(summary.previousNetIncome, currency) }}
            </div>
            <div class="summary-change" :class="getChangeClass(summary.netIncomeChange)">
              {{ formatPercentage(summary.netIncomeChange) }}
            </div>
          </div>
          
          <div class="profitability-metrics">
            <div class="metric">
              <div class="metric-label">Profit Margin</div>
              <div class="metric-value" :class="getMarginClass(summary.profitMargin, summary.profitMarginChange)">
                {{ formatPercentage(summary.profitMargin, 1) }}
                <span 
                  v-if="showComparison" 
                  class="metric-change"
                  :class="getChangeClass(summary.profitMarginChange)"
                >
                  ({{ formatPercentage(summary.profitMarginChange, 1) }})
                </span>
              </div>
            </div>
            
            <div class="metric">
              <div class="metric-label">EBITDA</div>
              <div class="metric-value" :class="getMarginClass(summary.ebitdaMargin, summary.ebitdaMarginChange)">
                {{ formatCurrency(summary.ebitda, currency) }}
                <span 
                  v-if="showComparison" 
                  class="metric-change"
                  :class="getChangeClass(summary.ebitdaChange)"
                >
                  ({{ formatPercentage(summary.ebitdaChange) }})
                </span>
              </div>
            </div>
            
            <div class="metric">
              <div class="metric-label">EBITDA Margin</div>
              <div class="metric-value" :class="getMarginClass(summary.ebitdaMargin, summary.ebitdaMarginChange)">
                {{ formatPercentage(summary.ebitdaMargin, 1) }}
                <span 
                  v-if="showComparison" 
                  class="metric-change"
                  :class="getChangeClass(summary.ebitdaMarginChange)"
                >
                  ({{ formatPercentage(summary.ebitdaMarginChange, 1) }})
                </span>
              </div>
            </div>
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
        <Button 
          icon="pi pi-file-excel" 
          label="Export to Excel" 
          class="p-button-text"
          @click="exportToExcel"
        />
      </div>
      <div class="report-info">
        Generated on {{ formatDate(new Date(), 'PPpp') }} by {{ currentUser?.name || 'System' }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.income-statement-report {
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

.section {
  background-color: var(--surface-card);
  border-radius: 6px;
  padding: 1.25rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.section h3 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: var(--text-color);
  font-weight: 600;
  border-bottom: 1px solid var(--surface-border);
  padding-bottom: 0.5rem;
}

.p-datatable {
  font-size: 0.9rem;
}

.p-datatable .p-datatable-thead > tr > th {
  background-color: var(--surface-50);
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.5px;
}

.percentage-bar {
  position: relative;
  width: 100%;
  height: 1.5rem;
  background-color: var(--surface-100);
  border-radius: 3px;
  overflow: hidden;
}

.percentage-fill {
  height: 100%;
  min-width: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 0.5rem;
  font-size: 0.7rem;
  color: white;
  font-weight: 600;
}

.percentage-text {
  position: absolute;
  left: 0.5rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-color);
  font-weight: 500;
  font-size: 0.8rem;
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

.summary-grid {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 1rem;
  margin-top: 1.5rem;
}

.summary-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr auto;
  gap: 1rem;
  padding: 0.75rem 0;
  border-bottom: 1px solid var(--surface-border);
  align-items: center;
}

.summary-row.total {
  font-weight: 700;
  font-size: 1.1rem;
  border-top: 2px solid var(--surface-border);
  border-bottom: none;
  padding-top: 1rem;
  margin-top: 0.5rem;
}

.summary-label {
  font-weight: 500;
}

.summary-amount {
  text-align: right;
  font-family: 'Roboto Mono', monospace;
}

.summary-previous {
  text-align: right;
  font-family: 'Roboto Mono', monospace;
  color: var(--text-color-secondary);
  font-size: 0.9em;
}

.summary-change {
  min-width: 5rem;
  text-align: right;
  font-weight: 500;
}

.profitability-metrics {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-top: 1rem;
}

.metric {
  background-color: var(--surface-50);
  border-radius: 6px;
  padding: 1rem;
  text-align: center;
}

.metric-label {
  font-size: 0.8rem;
  color: var(--text-color-secondary);
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.metric-value {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--primary-color);
}

.metric-value.positive-margin {
  color: var(--green-500);
}

.metric-value.negative-margin {
  color: var(--red-500);
}

.metric-change {
  font-size: 0.8rem;
  margin-left: 0.25rem;
}

.report-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid var(--surface-border);
  font-size: 0.85rem;
  color: var(--text-color-secondary);
}

.print-options {
  display: flex;
  gap: 1rem;
}

/* Responsive adjustments */
@media (max-width: 1200px) {
  .summary-cards {
    grid-template-columns: 1fr;
  }
  
  .profitability-metrics {
    grid-template-columns: 1fr;
  }
  
  .summary-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .filters {
    grid-template-columns: 1fr;
  }
  
  .summary-row {
    grid-template-columns: 1fr 1fr;
  }
  
  .summary-row > div:nth-child(3),
  .summary-row > div:nth-child(4) {
    grid-column: span 1;
    text-align: right;
  }
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
  
  .report-footer {
    display: none;
  }
  
  .summary-cards {
    display: none;
  }
  
  .section {
    page-break-inside: avoid;
    break-inside: avoid;
  }
}
</style>
