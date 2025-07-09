<template>
  <div class="financial-statements">
    <div class="flex justify-content-between align-items-center mb-4">
      <h2>Financial Statements</h2>
      <div>
        <Button 
          label="Generate Report" 
          icon="pi pi-file-pdf" 
          @click="showReportDialog = true"
          class="p-button-success"
        />
      </div>
    </div>

    <div class="grid">
      <!-- Balance Sheet Card -->
      <div class="col-12 lg:col-6">
        <div class="card h-full">
          <div class="flex justify-content-between align-items-center mb-4">
            <h3>Balance Sheet</h3>
            <Button 
              icon="pi pi-download" 
              class="p-button-text" 
              @click="exportToPdf('balance-sheet')"
              v-tooltip.top="'Export to PDF'"
            />
          </div>
          
          <DataTable 
            :value="balanceSheetData" 
            :loading="loading"
            :rowHover="true"
            :stripedRows="true"
            class="p-datatable-sm"
            :scrollable="true"
            scrollHeight="400px"
          >
            <Column field="account" header="Account" style="min-width:200px">
              <template #body="{ data }">
                <span :class="{ 'font-bold': data.isHeader }">
                  {{ data.account }}
                </span>
              </template>
            </Column>
            <Column field="amount" header="Amount" style="width:150px">
              <template #body="{ data }">
                <span :class="{ 'font-bold': data.isHeader }">
                  {{ formatCurrency(data.amount) }}
                </span>
              </template>
            </Column>
            
            <template #footer>
              <div class="flex justify-content-between p-2 border-top-1 border-gray-300">
                <div class="font-bold">Total Assets</div>
                <div class="font-bold">{{ formatCurrency(totalAssets) }}</div>
              </div>
              <div class="flex justify-content-between p-2 border-top-1 border-gray-300">
                <div class="font-bold">Total Liabilities & Equity</div>
                <div class="font-bold">{{ formatCurrency(totalLiabilitiesEquity) }}</div>
              </div>
            </template>
          </DataTable>
          
          <div class="mt-4 text-sm text-gray-600">
            <i class="pi pi-info-circle mr-1"></i>
            As of {{ formatDate(new Date()) }}
          </div>
        </div>
      </div>
      
      <!-- Income Statement Card -->
      <div class="col-12 lg:col-6">
        <div class="card h-full">
          <div class="flex justify-content-between align-items-center mb-4">
            <h3>Income Statement</h3>
            <Button 
              icon="pi pi-download" 
              class="p-button-text" 
              @click="exportToPdf('income-statement')"
              v-tooltip.top="'Export to PDF'"
            />
          </div>
          
          <DataTable 
            :value="incomeStatementData" 
            :loading="loading"
            :rowHover="true"
            :stripedRows="true"
            class="p-datatable-sm"
            :scrollable="true"
            scrollHeight="400px"
          >
            <Column field="account" header="Account" style="min-width:200px">
              <template #body="{ data }">
                <span :class="{ 'font-bold': data.isHeader }">
                  {{ data.account }}
                </span>
              </template>
            </Column>
            <Column field="amount" header="Amount" style="width:150px">
              <template #body="{ data }">
                <span :class="{ 'font-bold': data.isHeader }">
                  {{ formatCurrency(data.amount) }}
                </span>
              </template>
            </Column>
            
            <template #footer>
              <div class="flex justify-content-between p-2 border-top-1 border-gray-300">
                <div class="font-bold">Net Income</div>
                <div class="font-bold" :class="{ 'text-green-600': netIncome >= 0, 'text-red-600': netIncome < 0 }">
                  {{ formatCurrency(netIncome) }}
                </div>
              </div>
            </template>
          </DataTable>
          
          <div class="mt-4 text-sm text-gray-600">
            <i class="pi pi-info-circle mr-1"></i>
            For the period {{ formatDateRange(reportParams.start_date, reportParams.end_date) }}
          </div>
        </div>
      </div>
      
      <!-- Cash Flow Card -->
      <div class="col-12">
        <div class="card mt-4">
          <div class="flex justify-content-between align-items-center mb-4">
            <h3>Cash Flow Statement</h3>
            <Button 
              icon="pi pi-download" 
              class="p-button-text" 
              @click="exportToPdf('cash-flow')"
              v-tooltip.top="'Export to PDF'"
            />
          </div>
          
          <DataTable 
            :value="cashFlowData" 
            :loading="loading"
            :rowHover="true"
            :stripedRows="true"
            class="p-datatable-sm"
            :scrollable="true"
            scrollHeight="300px"
          >
            <Column field="activity" header="Activity" style="min-width:200px">
              <template #body="{ data }">
                <span :class="{ 'font-bold': data.isHeader }">
                  {{ data.activity }}
                </span>
              </template>
            </Column>
            <Column field="amount" header="Amount" style="width:150px">
              <template #body="{ data }">
                <span :class="{ 'font-bold': data.isHeader }">
                  {{ formatCurrency(data.amount) }}
                </span>
              </template>
            </Column>
            
            <template #footer>
              <div class="flex justify-content-between p-2 border-top-1 border-gray-300">
                <div class="font-bold">Net Increase in Cash</div>
                <div class="font-bold" :class="{ 'text-green-600': netCashFlow >= 0, 'text-red-600': netCashFlow < 0 }">
                  {{ formatCurrency(netCashFlow) }}
                </div>
              </div>
              <div class="flex justify-content-between p-2 border-top-1 border-gray-300">
                <div class="font-bold">Cash at Beginning of Period</div>
                <div class="font-bold">{{ formatCurrency(cashBeginning) }}</div>
              </div>
              <div class="flex justify-content-between p-2 border-top-1 border-gray-300">
                <div class="font-bold">Cash at End of Period</div>
                <div class="font-bold">{{ formatCurrency(cashEnd) }}</div>
              </div>
            </template>
          </DataTable>
          
          <div class="mt-4 text-sm text-gray-600">
            <i class="pi pi-info-circle mr-1"></i>
            For the period {{ formatDateRange(reportParams.start_date, reportParams.end_date) }}
          </div>
        </div>
      </div>
    </div>
    
    <!-- Report Generation Dialog -->
    <Dialog 
      v-model:visible="showReportDialog" 
      header="Generate Financial Statements"
      :modal="true"
      :style="{ width: '500px' }"
    >
      <div class="field">
        <label>Report Type</label>
        <div class="flex flex-column gap-2 mt-2">
          <div class="flex align-items-center">
            <RadioButton 
              id="report-type-balance" 
              v-model="reportParams.report_type" 
              value="balance-sheet" 
              class="mr-2" 
            />
            <label for="report-type-balance">Balance Sheet</label>
          </div>
          <div class="flex align-items-center">
            <RadioButton 
              id="report-type-income" 
              v-model="reportParams.report_type" 
              value="income-statement" 
              class="mr-2" 
            />
            <label for="report-type-income">Income Statement</label>
          </div>
          <div class="flex align-items-center">
            <RadioButton 
              id="report-type-cash" 
              v-model="reportParams.report_type" 
              value="cash-flow" 
              class="mr-2" 
            />
            <label for="report-type-cash">Cash Flow Statement</label>
          </div>
          <div class="flex align-items-center">
            <RadioButton 
              id="report-type-all" 
              v-model="reportParams.report_type" 
              value="all" 
              class="mr-2" 
            />
            <label for="report-type-all">All Statements</label>
          </div>
        </div>
      </div>
      
      <div class="field mt-4">
        <label>Date Range</label>
        <div class="flex flex-column gap-2 mt-2">
          <div class="flex align-items-center">
            <RadioButton 
              id="period-month" 
              v-model="reportParams.period" 
              value="month" 
              class="mr-2" 
            />
            <label for="period-month">This Month</label>
          </div>
          <div class="flex align-items-center">
            <RadioButton 
              id="period-quarter" 
              v-model="reportParams.period" 
              value="quarter" 
              class="mr-2" 
            />
            <label for="period-quarter">This Quarter</label>
          </div>
          <div class="flex align-items-center">
            <RadioButton 
              id="period-year" 
              v-model="reportParams.period" 
              value="year" 
              class="mr-2" 
            />
            <label for="period-year">This Fiscal Year</label>
          </div>
          <div class="flex align-items-center">
            <RadioButton 
              id="period-custom" 
              v-model="reportParams.period" 
              value="custom" 
              class="mr-2" 
            />
            <label for="period-custom">Custom Range</label>
          </div>
          
          <div v-if="reportParams.period === 'custom'" class="grid mt-2">
            <div class="col-12 md:col-6">
              <div class="field">
                <label>Start Date</label>
                <Calendar 
                  v-model="reportParams.start_date" 
                  :showIcon="true" 
                  dateFormat="yy-mm-dd"
                  class="w-full"
                />
              </div>
            </div>
            <div class="col-12 md:col-6">
              <div class="field">
                <label>End Date</label>
                <Calendar 
                  v-model="reportParams.end_date" 
                  :showIcon="true" 
                  dateFormat="yy-mm-dd"
                  class="w-full"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="field mt-4">
        <label>Format</label>
        <div class="flex flex-column gap-2 mt-2">
          <div class="flex align-items-center">
            <RadioButton 
              id="format-pdf" 
              v-model="reportParams.format" 
              value="pdf" 
              class="mr-2" 
            />
            <label for="format-pdf">PDF Document</label>
          </div>
          <div class="flex align-items-center">
            <RadioButton 
              id="format-excel" 
              v-model="reportParams.format" 
              value="excel" 
              class="mr-2" 
            />
            <label for="format-excel">Excel Spreadsheet</label>
          </div>
        </div>
      </div>
      
      <template #footer>
        <Button 
          label="Cancel" 
          @click="showReportDialog = false"
          class="p-button-text"
        />
        <Button 
          label="Generate Report" 
          @click="generateReport"
          class="p-button-primary"
          :loading="generating"
        />
      </template>
    </Dialog>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';

export default {
  name: 'FinancialStatementsView',
  
  setup() {
    const toast = useToast();
    
    const loading = ref(false);
    const generating = ref(false);
    const showReportDialog = ref(false);
    
    const reportParams = ref({
      report_type: 'all',
      period: 'month',
      start_date: new Date(new Date().setDate(1)), // Start of current month
      end_date: new Date(), // Today
      format: 'pdf',
      currency: 'USD'
    });
    
    // Mock data - replace with actual API calls
    const balanceSheetData = ref([
      { account: 'ASSETS', amount: null, isHeader: true },
      { account: '  Current Assets', amount: null, isHeader: true },
      { account: '    Cash and Cash Equivalents', amount: 150000, isHeader: false },
      { account: '    Accounts Receivable', amount: 75000, isHeader: false },
      { account: '    Inventory', amount: 120000, isHeader: false },
      { account: '    Prepaid Expenses', amount: 15000, isHeader: false },
      { account: '  Total Current Assets', amount: 360000, isHeader: true },
      { account: '  Non-Current Assets', amount: null, isHeader: true },
      { account: '    Property, Plant & Equipment', amount: 450000, isHeader: false },
      { account: '    Less: Accumulated Depreciation', amount: -120000, isHeader: false },
      { account: '  Total Non-Current Assets', amount: 330000, isHeader: true },
      { account: 'TOTAL ASSETS', amount: 690000, isHeader: true },
      
      { account: 'LIABILITIES', amount: null, isHeader: true },
      { account: '  Current Liabilities', amount: null, isHeader: true },
      { account: '    Accounts Payable', amount: 65000, isHeader: false },
      { account: '    Short-term Loans', amount: 50000, isHeader: false },
      { account: '    Accrued Expenses', amount: 25000, isHeader: false },
      { account: '  Total Current Liabilities', amount: 140000, isHeader: true },
      { account: '  Long-term Liabilities', amount: null, isHeader: true },
      { account: '    Long-term Debt', amount: 200000, isHeader: false },
      { account: '    Deferred Tax Liabilities', amount: 35000, isHeader: false },
      { account: '  Total Long-term Liabilities', amount: 235000, isHeader: true },
      { account: 'TOTAL LIABILITIES', amount: 375000, isHeader: true },
      
      { account: 'EQUITY', amount: null, isHeader: true },
      { account: '  Common Stock', amount: 200000, isHeader: false },
      { account: '  Retained Earnings', amount: 115000, isHeader: false },
      { account: 'TOTAL EQUITY', amount: 315000, isHeader: true },
      { account: 'TOTAL LIABILITIES & EQUITY', amount: 690000, isHeader: true },
    ]);
    
    const incomeStatementData = ref([
      { account: 'REVENUE', amount: null, isHeader: true },
      { account: '  Product Sales', amount: 850000, isHeader: false },
      { account: '  Service Revenue', amount: 150000, isHeader: false },
      { account: '  Other Income', amount: 25000, isHeader: false },
      { account: 'TOTAL REVENUE', amount: 1025000, isHeader: true },
      
      { account: 'COST OF GOODS SOLD', amount: null, isHeader: true },
      { account: '  Direct Materials', amount: 320000, isHeader: false },
      { account: '  Direct Labor', amount: 180000, isHeader: false },
      { account: '  Manufacturing Overhead', amount: 120000, isHeader: false },
      { account: 'TOTAL COST OF GOODS SOLD', amount: 620000, isHeader: true },
      { account: 'GROSS PROFIT', amount: 405000, isHeader: true },
      
      { account: 'OPERATING EXPENSES', amount: null, isHeader: true },
      { account: '  Salaries and Wages', amount: 120000, isHeader: false },
      { account: '  Rent Expense', amount: 48000, isHeader: false },
      { account: '  Utilities', amount: 18000, isHeader: false },
      { account: '  Marketing', amount: 35000, isHeader: false },
      { account: '  Depreciation', amount: 25000, isHeader: false },
      { account: '  Other Expenses', amount: 15000, isHeader: false },
      { account: 'TOTAL OPERATING EXPENSES', amount: 261000, isHeader: true },
      
      { account: 'OPERATING INCOME', amount: 144000, isHeader: true },
      
      { account: 'OTHER INCOME/EXPENSES', amount: null, isHeader: true },
      { account: '  Interest Income', amount: 5000, isHeader: false },
      { account: '  Interest Expense', amount: -18000, isHeader: false },
      { account: 'TOTAL OTHER INCOME/EXPENSES', amount: -13000, isHeader: true },
      
      { account: 'INCOME BEFORE TAXES', amount: 131000, isHeader: true },
      { account: 'Income Tax Expense', amount: -32750, isHeader: false },
      { account: 'NET INCOME', amount: 98250, isHeader: true },
    ]);
    
    const cashFlowData = ref([
      { activity: 'CASH FLOWS FROM OPERATING ACTIVITIES', amount: null, isHeader: true },
      { activity: '  Net Income', amount: 98250, isHeader: false },
      { activity: '  Adjustments to Reconcile Net Income to Net Cash', amount: null, isHeader: true },
      { activity: '    Depreciation Expense', amount: 25000, isHeader: false },
      { activity: '    Changes in Working Capital', amount: null, isHeader: true },
      { activity: '      (Increase) in Accounts Receivable', amount: -15000, isHeader: false },
      { activity: '      (Increase) in Inventory', amount: -20000, isHeader: false },
      { activity: '      (Increase) in Prepaid Expenses', amount: -5000, isHeader: false },
      { activity: '      Increase in Accounts Payable', amount: 10000, isHeader: false },
      { activity: '      Increase in Accrued Expenses', amount: 5000, isHeader: false },
      { activity: '  Net Cash Provided by Operating Activities', amount: 94250, isHeader: true },
      
      { activity: 'CASH FLOWS FROM INVESTING ACTIVITIES', amount: null, isHeader: true },
      { activity: '  Purchase of Property, Plant & Equipment', amount: -75000, isHeader: false },
      { activity: '  Proceeds from Sale of Equipment', amount: 10000, isHeader: false },
      { activity: '  Net Cash Used in Investing Activities', amount: -65000, isHeader: true },
      
      { activity: 'CASH FLOWS FROM FINANCING ACTIVITIES', amount: null, isHeader: true },
      { activity: '  Proceeds from Long-term Debt', amount: 50000, isHeader: false },
      { activity: '  Repayment of Long-term Debt', amount: -25000, isHeader: false },
      { activity: '  Dividends Paid', amount: -30000, isHeader: false },
      { activity: '  Net Cash Used in Financing Activities', amount: -5000, isHeader: true },
      
      { activity: 'NET INCREASE IN CASH', amount: 24250, isHeader: true },
      { activity: 'CASH AT BEGINNING OF PERIOD', amount: 125750, isHeader: true },
      { activity: 'CASH AT END OF PERIOD', amount: 150000, isHeader: true },
    ]);
    
    // Computed properties
    const totalAssets = computed(() => {
      return balanceSheetData.value.find(item => item.account === 'TOTAL ASSETS')?.amount || 0;
    });
    
    const totalLiabilitiesEquity = computed(() => {
      return balanceSheetData.value.find(item => item.account === 'TOTAL LIABILITIES & EQUITY')?.amount || 0;
    });
    
    const netIncome = computed(() => {
      return incomeStatementData.value.find(item => item.account === 'NET INCOME')?.amount || 0;
    });
    
    const netCashFlow = computed(() => {
      return cashFlowData.value.find(item => item.activity === 'NET INCREASE IN CASH')?.amount || 0;
    });
    
    const cashBeginning = computed(() => {
      return cashFlowData.value.find(item => item.activity === 'CASH AT BEGINNING OF PERIOD')?.amount || 0;
    });
    
    const cashEnd = computed(() => {
      return cashFlowData.value.find(item => item.activity === 'CASH AT END OF PERIOD')?.amount || 0;
    });
    
    // Methods
    const formatDate = (date) => {
      if (!date) return '';
      const options = { year: 'numeric', month: 'long', day: 'numeric' };
      return new Date(date).toLocaleDateString('en-US', options);
    };
    
    const formatDateRange = (start, end) => {
      if (!start || !end) return '';
      return `${formatDate(start)} to ${formatDate(end)}`;
    };
    
    const formatCurrency = (value) => {
      if (value === null || value === undefined) return '$0.00';
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }).format(value);
    };
    
    const generateReport = async () => {
      generating.value = true;
      
      try {
        // TODO: Replace with actual API call to generate report
        console.log('Generating report with params:', reportParams.value);
        
        // Simulate API call delay
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        toast.add({
          severity: 'success',
          summary: 'Report Generated',
          detail: `Your ${reportParams.value.report_type} report is ready for download`,
          life: 3000
        });
        
        showReportDialog.value = false;
      } catch (error) {
        console.error('Error generating report:', error);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to generate report',
          life: 3000
        });
      } finally {
        generating.value = false;
      }
    };
    
    const exportToPdf = (reportType) => {
      console.log(`Exporting ${reportType} to PDF`);
      // TODO: Implement PDF export
      toast.add({
        severity: 'info',
        summary: 'Exporting',
        detail: `Exporting ${reportType.replace('-', ' ')} to PDF`,
        life: 2000
      });
    };
    
    // Initialize date range based on selected period
    const updateDateRange = () => {
      const today = new Date();
      const start = new Date();
      
      switch (reportParams.value.period) {
        case 'month':
          start.setDate(1); // Start of current month
          break;
        case 'quarter':
          start.setMonth(Math.floor(today.getMonth() / 3) * 3, 1); // Start of current quarter
          break;
        case 'year':
          start.setMonth(0, 1); // Start of current year
          break;
        // For 'custom', use the existing dates
      }
      
      reportParams.value.start_date = start;
      reportParams.value.end_date = today;
    };
    
    // Watch for period changes to update date range
    onMounted(() => {
      updateDateRange();
    });
    
    return {
      loading,
      generating,
      showReportDialog,
      reportParams,
      balanceSheetData,
      incomeStatementData,
      cashFlowData,
      totalAssets,
      totalLiabilitiesEquity,
      netIncome,
      netCashFlow,
      cashBeginning,
      cashEnd,
      formatDate,
      formatDateRange,
      formatCurrency,
      generateReport,
      exportToPdf,
      updateDateRange
    };
  }
};
</script>

<style scoped>
:deep(.p-datatable) {
  font-size: 0.9rem;
}

:deep(.p-datatable .p-datatable-thead > tr > th) {
  background-color: #f8f9fa;
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.5px;
}

:deep(.p-datatable .p-datatable-tbody > tr > td) {
  padding: 0.5rem 1rem;
}

:deep(.p-datatable .p-datatable-tbody > tr:hover) {
  background-color: #f8f9fa;
}

.border-top-1 {
  border-top: 1px solid #e5e7eb;
}

.border-gray-300 {
  border-color: #e5e7eb;
}

.text-green-600 {
  color: #059669;
}

.text-red-600 {
  color: #dc2626;
}

.text-gray-600 {
  color: #4b5563;
}

.h-full {
  height: 100%;
}
</style>
