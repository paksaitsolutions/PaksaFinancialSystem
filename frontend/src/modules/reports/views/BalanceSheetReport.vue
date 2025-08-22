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
      <Button icon="pi pi-print" label="Print" class="p-button-text" @click="printReport" />
      <Button icon="pi pi-download" label="Export PDF" class="p-button-text" @click="exportToPDF" />
      <Button icon="pi pi-file-excel" label="Export Excel" class="p-button-text" @click="exportToExcel" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useEnhancedReports } from '@/composables/useEnhancedReports';
import { formatCurrency } from '@/utils/formatters';
import ReportHeader from '@/components/reports/ReportHeader.vue';

const { loading, exportLoading, generateReport, exportReport } = useEnhancedReports();

const asOfDate = ref(new Date());
const currency = ref('USD');
const reportData = ref(null);

const currencies = [
  { name: 'US Dollar (USD)', code: 'USD' },
  { name: 'Euro (EUR)', code: 'EUR' },
  { name: 'British Pound (GBP)', code: 'GBP' }
];

const fetchReportData = async () => {
  const result = await generateReport('balance_sheet', {
    asOfDate: asOfDate.value
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

const printReport = () => window.print();
const exportToPDF = () => handleExport('pdf');
const exportToExcel = () => handleExport('excel');

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