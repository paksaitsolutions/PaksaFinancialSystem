<template>
  <div class="balance-sheet-report">
    <ReportHeader 
      title="Balance Sheet"
      :loading="loading"
      :export-loading="exportLoading"
      @export="handleExport"
    >
      <template #filters>
        <div class="filters">
          <div class="field">
            <label>As of Date</label>
            <Calendar v-model="asOfDate" />
          </div>
          <div class="field">
            <label>Currency</label>
            <Dropdown v-model="currency" :options="currencies" optionLabel="name" optionValue="code" />
          </div>
        </div>
      </template>
    </ReportHeader>

    <div class="report-content" v-if="reportData">
      <div class="balance-sheet-grid">
        <!-- Assets Section -->
        <div class="section assets-section">
          <h2>Assets</h2>
          
          <div class="subsection">
            <h3>Current Assets</h3>
            <div class="line-item" v-for="(value, key) in reportData.assets.current_assets" :key="key">
              <span class="account-name">{{ formatAccountName(key) }}</span>
              <span class="amount">{{ formatCurrency(value, currency) }}</span>
            </div>
            <div class="subtotal">
              <span>Total Current Assets</span>
              <span>{{ formatCurrency(reportData.assets.current_assets.total_current, currency) }}</span>
            </div>
          </div>
          
          <div class="subsection">
            <h3>Fixed Assets</h3>
            <div class="line-item" v-for="(value, key) in reportData.assets.fixed_assets" :key="key">
              <span class="account-name">{{ formatAccountName(key) }}</span>
              <span class="amount">{{ formatCurrency(value, currency) }}</span>
            </div>
            <div class="subtotal">
              <span>Total Fixed Assets</span>
              <span>{{ formatCurrency(reportData.assets.fixed_assets.total_fixed, currency) }}</span>
            </div>
          </div>
          
          <div class="total">
            <span>Total Assets</span>
            <span>{{ formatCurrency(reportData.assets.total_assets, currency) }}</span>
          </div>
        </div>

        <!-- Liabilities & Equity Section -->
        <div class="section liabilities-section">
          <h2>Liabilities & Equity</h2>
          
          <div class="subsection">
            <h3>Current Liabilities</h3>
            <div class="line-item" v-for="(value, key) in reportData.liabilities.current_liabilities" :key="key">
              <span class="account-name">{{ formatAccountName(key) }}</span>
              <span class="amount">{{ formatCurrency(value, currency) }}</span>
            </div>
            <div class="subtotal">
              <span>Total Current Liabilities</span>
              <span>{{ formatCurrency(reportData.liabilities.current_liabilities.total_current, currency) }}</span>
            </div>
          </div>
          
          <div class="subsection">
            <h3>Long-term Liabilities</h3>
            <div class="line-item" v-for="(value, key) in reportData.liabilities.long_term_liabilities" :key="key">
              <span class="account-name">{{ formatAccountName(key) }}</span>
              <span class="amount">{{ formatCurrency(value, currency) }}</span>
            </div>
            <div class="subtotal">
              <span>Total Long-term Liabilities</span>
              <span>{{ formatCurrency(reportData.liabilities.long_term_liabilities.total_long_term, currency) }}</span>
            </div>
          </div>
          
          <div class="subtotal">
            <span>Total Liabilities</span>
            <span>{{ formatCurrency(reportData.liabilities.total_liabilities, currency) }}</span>
          </div>
          
          <div class="subsection">
            <h3>Equity</h3>
            <div class="line-item" v-for="(value, key) in reportData.equity" :key="key">
              <span class="account-name">{{ formatAccountName(key) }}</span>
              <span class="amount">{{ formatCurrency(value, currency) }}</span>
            </div>
          </div>
          
          <div class="total">
            <span>Total Liabilities & Equity</span>
            <span>{{ formatCurrency(reportData.liabilities.total_liabilities + reportData.equity.total_equity, currency) }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="report-footer">
      <Button icon="pi pi-print" label="Print" @click="printBalanceSheet" />
      <SplitButton label="Export" icon="pi pi-download" @click="exportBalanceSheetToPDF" :model="exportOptions" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import Calendar from 'primevue/calendar';
import Dropdown from 'primevue/dropdown';
import Button from 'primevue/button';
import SplitButton from 'primevue/splitbutton';
import ReportHeader from '@/components/reports/ReportHeader.vue';
import { useReportExport } from '@/composables/useReportExport';
import { formatCurrency } from '@/utils/formatters';
import { reportsService } from '@/api/reportsService';

const { exportToCSV, exportToPDF, printReport } = useReportExport();
const loading = ref(false);

const asOfDate = ref(new Date());
const currency = ref('USD');
const reportData = ref(null);

const currencies = [
  { name: 'US Dollar (USD)', code: 'USD' },
  { name: 'Euro (EUR)', code: 'EUR' },
  { name: 'British Pound (GBP)', code: 'GBP' }
];

const fetchReportData = async () => {
  loading.value = true;
  try {
    // Mock data for now - replace with actual API call
    reportData.value = {
      assets: {
        current_assets: {
          cash: 50000,
          accounts_receivable: 25000,
          inventory: 15000,
          total_current: 90000
        },
        fixed_assets: {
          equipment: 100000,
          accumulated_depreciation: -20000,
          total_fixed: 80000
        },
        total_assets: 170000
      },
      liabilities: {
        current_liabilities: {
          accounts_payable: 15000,
          accrued_expenses: 5000,
          total_current: 20000
        },
        long_term_liabilities: {
          long_term_debt: 30000,
          total_long_term: 30000
        },
        total_liabilities: 50000
      },
      equity: {
        retained_earnings: 70000,
        capital_stock: 50000,
        total_equity: 120000
      }
    };
  } catch (error) {
    console.error('Error fetching balance sheet data:', error);
  } finally {
    loading.value = false;
  }
};

const exportLoading = ref(false);

const handleExport = async (format: string) => {
  exportLoading.value = true;
  try {
    if (format === 'pdf') {
      exportBalanceSheetToPDF();
    } else if (format === 'excel') {
      exportBalanceSheetToExcel();
    }
  } finally {
    exportLoading.value = false;
  }
};

const formatAccountName = (key: string) => {
  return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
};

const printBalanceSheet = () => {
  if (reportData.value) {
    const data = formatDataForExport()
    printReport('Balance Sheet Report', data)
  }
}

const exportBalanceSheetToPDF = () => {
  if (reportData.value) {
    const data = formatDataForExport()
    exportToPDF('Balance Sheet Report', data, 'Balance_Sheet_Report')
  }
}

const exportBalanceSheetToExcel = () => {
  if (reportData.value) {
    const data = formatDataForExport()
    exportToCSV(data, 'Balance_Sheet_Report')
  }
}

const formatDataForExport = () => {
  const data = []
  
  // Assets Section
  data.push({ Section: 'ASSETS', Account: '', Amount: '' })
  data.push({ Section: '', Account: '', Amount: '' }) // Empty row
  
  // Current Assets
  data.push({ Section: 'Current Assets:', Account: '', Amount: '' })
  Object.entries(reportData.value.assets.current_assets).forEach(([key, value]) => {
    if (key !== 'total_current') {
      data.push({ Section: '', Account: `  ${formatAccountName(key)}`, Amount: formatCurrency(value, currency.value) })
    }
  })
  data.push({ Section: '', Account: 'Total Current Assets', Amount: formatCurrency(reportData.value.assets.current_assets.total_current, currency.value) })
  data.push({ Section: '', Account: '', Amount: '' }) // Empty row
  
  // Fixed Assets
  data.push({ Section: 'Fixed Assets:', Account: '', Amount: '' })
  Object.entries(reportData.value.assets.fixed_assets).forEach(([key, value]) => {
    if (key !== 'total_fixed') {
      data.push({ Section: '', Account: `  ${formatAccountName(key)}`, Amount: formatCurrency(value, currency.value) })
    }
  })
  data.push({ Section: '', Account: 'Total Fixed Assets', Amount: formatCurrency(reportData.value.assets.fixed_assets.total_fixed, currency.value) })
  data.push({ Section: '', Account: '', Amount: '' }) // Empty row
  data.push({ Section: '', Account: 'TOTAL ASSETS', Amount: formatCurrency(reportData.value.assets.total_assets, currency.value) })
  
  data.push({ Section: '', Account: '', Amount: '' }) // Empty row
  data.push({ Section: '', Account: '', Amount: '' }) // Empty row
  
  // Liabilities & Equity Section
  data.push({ Section: 'LIABILITIES & EQUITY', Account: '', Amount: '' })
  data.push({ Section: '', Account: '', Amount: '' }) // Empty row
  
  // Current Liabilities
  data.push({ Section: 'Current Liabilities:', Account: '', Amount: '' })
  Object.entries(reportData.value.liabilities.current_liabilities).forEach(([key, value]) => {
    if (key !== 'total_current') {
      data.push({ Section: '', Account: `  ${formatAccountName(key)}`, Amount: formatCurrency(value, currency.value) })
    }
  })
  data.push({ Section: '', Account: 'Total Current Liabilities', Amount: formatCurrency(reportData.value.liabilities.current_liabilities.total_current, currency.value) })
  data.push({ Section: '', Account: '', Amount: '' }) // Empty row
  
  // Long-term Liabilities
  data.push({ Section: 'Long-term Liabilities:', Account: '', Amount: '' })
  Object.entries(reportData.value.liabilities.long_term_liabilities).forEach(([key, value]) => {
    if (key !== 'total_long_term') {
      data.push({ Section: '', Account: `  ${formatAccountName(key)}`, Amount: formatCurrency(value, currency.value) })
    }
  })
  data.push({ Section: '', Account: 'Total Long-term Liabilities', Amount: formatCurrency(reportData.value.liabilities.long_term_liabilities.total_long_term, currency.value) })
  data.push({ Section: '', Account: 'Total Liabilities', Amount: formatCurrency(reportData.value.liabilities.total_liabilities, currency.value) })
  data.push({ Section: '', Account: '', Amount: '' }) // Empty row
  
  // Equity
  data.push({ Section: 'Equity:', Account: '', Amount: '' })
  Object.entries(reportData.value.equity).forEach(([key, value]) => {
    if (key !== 'total_equity') {
      data.push({ Section: '', Account: `  ${formatAccountName(key)}`, Amount: formatCurrency(value, currency.value) })
    }
  })
  data.push({ Section: '', Account: 'Total Equity', Amount: formatCurrency(reportData.value.equity.total_equity, currency.value) })
  data.push({ Section: '', Account: '', Amount: '' }) // Empty row
  data.push({ Section: '', Account: 'TOTAL LIABILITIES & EQUITY', Amount: formatCurrency(reportData.value.liabilities.total_liabilities + reportData.value.equity.total_equity, currency.value) })
  
  return data
}

const exportOptions = [
  {
    label: 'Export to PDF',
    icon: 'pi pi-file-pdf',
    command: () => exportBalanceSheetToPDF()
  },
  {
    label: 'Export to Excel',
    icon: 'pi pi-file-excel',
    command: () => exportBalanceSheetToExcel()
  }
]

onMounted(() => {
  fetchReportData();
});
</script>

<style scoped>
.balance-sheet-report {
  padding: 1rem;
}

.filters {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.balance-sheet-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin: 2rem 0;
}

.section {
  background: var(--surface-card);
  border-radius: 8px;
  padding: 1.5rem;
}

.section h2 {
  margin: 0 0 1rem 0;
  color: var(--primary-color);
  border-bottom: 2px solid var(--primary-color);
  padding-bottom: 0.5rem;
}

.subsection {
  margin-bottom: 1.5rem;
}

.subsection h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
  color: var(--text-color);
}

.line-item {
  display: flex;
  justify-content: space-between;
  padding: 0.25rem 0;
  border-bottom: 1px solid var(--surface-border);
}

.subtotal {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  font-weight: 600;
  border-top: 1px solid var(--surface-border);
  margin-top: 0.5rem;
}

.total {
  display: flex;
  justify-content: space-between;
  padding: 1rem 0;
  font-weight: 700;
  font-size: 1.1rem;
  border-top: 2px solid var(--surface-border);
  margin-top: 1rem;
}

.report-footer {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid var(--surface-border);
}

@media (max-width: 768px) {
  .balance-sheet-grid {
    grid-template-columns: 1fr;
  }
}
</style>