<template>
  <div class="cash-flow-report">
    <ReportHeader 
      title="Cash Flow Statement"
      :loading="loading"
      :export-loading="exportLoading"
      @export="handleExport"
    >
      <template #filters>
        <div class="filters">
          <div class="field">
            <label>Period Start</label>
            <Calendar v-model="periodStart" />
          </div>
          <div class="field">
            <label>Period End</label>
            <Calendar v-model="periodEnd" />
          </div>
          <div class="field">
            <label>Currency</label>
            <Dropdown v-model="currency" :options="currencies" optionLabel="name" optionValue="code" />
          </div>
        </div>
      </template>
    </ReportHeader>

    <div class="report-content" v-if="reportData">
      <!-- Operating Activities -->
      <div class="section">
        <h2>Cash Flow from Operating Activities</h2>
        <div class="line-item" v-for="(value, key) in reportData.operating_activities" :key="key">
          <span class="account-name">{{ formatAccountName(key) }}</span>
          <span class="amount" :class="{ negative: value < 0 }">{{ formatCurrency(value, currency) }}</span>
        </div>
        <div class="subtotal">
          <span>Net Cash from Operating Activities</span>
          <span :class="{ negative: reportData.operating_activities.net_operating_cash < 0 }">
            {{ formatCurrency(reportData.operating_activities.net_operating_cash, currency) }}
          </span>
        </div>
      </div>

      <!-- Investing Activities -->
      <div class="section">
        <h2>Cash Flow from Investing Activities</h2>
        <div class="line-item" v-for="(value, key) in reportData.investing_activities" :key="key">
          <span class="account-name">{{ formatAccountName(key) }}</span>
          <span class="amount" :class="{ negative: value < 0 }">{{ formatCurrency(value, currency) }}</span>
        </div>
        <div class="subtotal">
          <span>Net Cash from Investing Activities</span>
          <span :class="{ negative: reportData.investing_activities.net_investing_cash < 0 }">
            {{ formatCurrency(reportData.investing_activities.net_investing_cash, currency) }}
          </span>
        </div>
      </div>

      <!-- Financing Activities -->
      <div class="section">
        <h2>Cash Flow from Financing Activities</h2>
        <div class="line-item" v-for="(value, key) in reportData.financing_activities" :key="key">
          <span class="account-name">{{ formatAccountName(key) }}</span>
          <span class="amount" :class="{ negative: value < 0 }">{{ formatCurrency(value, currency) }}</span>
        </div>
        <div class="subtotal">
          <span>Net Cash from Financing Activities</span>
          <span :class="{ negative: reportData.financing_activities.net_financing_cash < 0 }">
            {{ formatCurrency(reportData.financing_activities.net_financing_cash, currency) }}
          </span>
        </div>
      </div>

      <!-- Net Change in Cash -->
      <div class="section total-section">
        <div class="total">
          <span>Net Change in Cash</span>
          <span :class="{ negative: reportData.net_cash_change < 0 }">
            {{ formatCurrency(reportData.net_cash_change, currency) }}
          </span>
        </div>
      </div>
    </div>

    <div class="report-footer">
      <Button icon="pi pi-print" label="Print" @click="printCashFlow" />
      <SplitButton label="Export" icon="pi pi-download" @click="exportCashFlowToPDF" :model="exportOptions" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useReportExport } from '@/composables/useReportExport';
import { formatCurrency } from '@/utils/formatters';

const { exportToCSV, exportToPDF, printReport } = useReportExport();
const loading = ref(false);

const periodStart = ref(new Date(new Date().getFullYear(), 0, 1));
const periodEnd = ref(new Date());
const currency = ref('USD');
const reportData = ref(null);

const currencies = [
  { name: 'US Dollar (USD)', code: 'USD' },
  { name: 'Euro (EUR)', code: 'EUR' },
  { name: 'British Pound (GBP)', code: 'GBP' }
];

const fetchReportData = async () => {
  const result = await generateReport('cash_flow', {
    periodStart: periodStart.value,
    periodEnd: periodEnd.value
  });
  
  if (result?.report_data) {
    reportData.value = result.report_data;
  }
};

const handleExport = async (format: string) => {
  if (reportData.value) {
    await exportReport(reportData.value.id, format);
  }
};

const formatAccountName = (key: string) => {
  return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
};

const printCashFlow = () => {
  if (reportData.value) {
    const data = formatDataForExport()
    printReport('Cash Flow Statement', data)
  }
}

const exportCashFlowToPDF = () => {
  if (reportData.value) {
    const data = formatDataForExport()
    exportToPDF('Cash Flow Statement', data, 'Cash_Flow_Statement')
  }
}

const exportCashFlowToExcel = () => {
  if (reportData.value) {
    const data = formatDataForExport()
    exportToCSV(data, 'Cash_Flow_Statement')
  }
}

const formatDataForExport = () => {
  const data = []
  
  // Operating Activities
  data.push({ Section: 'OPERATING ACTIVITIES', Account: '', Amount: '' })
  Object.entries(reportData.value.operating_activities).forEach(([key, value]) => {
    if (key !== 'net_operating_cash') {
      data.push({ Section: '', Account: formatAccountName(key), Amount: formatCurrency(value, currency.value) })
    }
  })
  data.push({ Section: '', Account: 'Net Cash from Operating Activities', Amount: formatCurrency(reportData.value.operating_activities.net_operating_cash, currency.value) })
  
  // Investing Activities
  data.push({ Section: 'INVESTING ACTIVITIES', Account: '', Amount: '' })
  Object.entries(reportData.value.investing_activities).forEach(([key, value]) => {
    if (key !== 'net_investing_cash') {
      data.push({ Section: '', Account: formatAccountName(key), Amount: formatCurrency(value, currency.value) })
    }
  })
  data.push({ Section: '', Account: 'Net Cash from Investing Activities', Amount: formatCurrency(reportData.value.investing_activities.net_investing_cash, currency.value) })
  
  // Financing Activities
  data.push({ Section: 'FINANCING ACTIVITIES', Account: '', Amount: '' })
  Object.entries(reportData.value.financing_activities).forEach(([key, value]) => {
    if (key !== 'net_financing_cash') {
      data.push({ Section: '', Account: formatAccountName(key), Amount: formatCurrency(value, currency.value) })
    }
  })
  data.push({ Section: '', Account: 'Net Cash from Financing Activities', Amount: formatCurrency(reportData.value.financing_activities.net_financing_cash, currency.value) })
  
  data.push({ Section: '', Account: 'NET CHANGE IN CASH', Amount: formatCurrency(reportData.value.net_cash_change, currency.value) })
  
  return data
}

const exportOptions = [
  {
    label: 'Export to PDF',
    icon: 'pi pi-file-pdf',
    command: () => exportCashFlowToPDF()
  },
  {
    label: 'Export to Excel',
    icon: 'pi pi-file-excel',
    command: () => exportCashFlowToExcel()
  }
]

onMounted(() => {
  fetchReportData();
});
</script>

<style scoped>
.cash-flow-report {
  padding: 1rem;
}

.filters {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.section {
  background: var(--surface-card);
  border-radius: 8px;
  padding: 1.5rem;
  margin: 1rem 0;
}

.section h2 {
  margin: 0 0 1rem 0;
  color: var(--primary-color);
  border-bottom: 2px solid var(--primary-color);
  padding-bottom: 0.5rem;
}

.line-item {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--surface-border);
}

.subtotal {
  display: flex;
  justify-content: space-between;
  padding: 1rem 0;
  font-weight: 600;
  border-top: 1px solid var(--surface-border);
  margin-top: 0.5rem;
}

.total {
  display: flex;
  justify-content: space-between;
  padding: 1rem 0;
  font-weight: 700;
  font-size: 1.2rem;
  border-top: 2px solid var(--surface-border);
}

.negative {
  color: var(--red-500);
}

.total-section {
  background: var(--surface-50);
  border: 2px solid var(--primary-color);
}

.report-footer {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid var(--surface-border);
}
</style>