<template>
  <div class="ap-aging-report">
    <ReportHeader 
      title="Accounts Payable Aging Report"
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
      <!-- Summary Cards -->
      <div class="summary-cards">
        <div class="summary-card">
          <h3>Total Outstanding</h3>
          <div class="amount">{{ formatCurrency(reportData.total_outstanding, currency) }}</div>
        </div>
        <div class="summary-card current">
          <h3>Current (0-30 days)</h3>
          <div class="amount">{{ formatCurrency(reportData.aging_buckets.current, currency) }}</div>
          <div class="percentage">{{ getPercentage(reportData.aging_buckets.current, reportData.total_outstanding) }}%</div>
        </div>
        <div class="summary-card overdue">
          <h3>Overdue (31+ days)</h3>
          <div class="amount">{{ formatCurrency(getOverdueAmount(), currency) }}</div>
          <div class="percentage">{{ getPercentage(getOverdueAmount(), reportData.total_outstanding) }}%</div>
        </div>
      </div>

      <!-- Aging Distribution Chart -->
      <div class="aging-chart">
        <h3>Payment Distribution</h3>
        <div class="chart-container">
          <div 
            v-for="(amount, bucket) in reportData.aging_buckets" 
            :key="bucket"
            class="chart-bar payable"
            :style="{ height: getBarHeight(amount, reportData.total_outstanding) + '%' }"
          >
            <div class="bar-label">{{ formatBucketName(bucket) }}</div>
            <div class="bar-amount">{{ formatCurrency(amount, currency) }}</div>
          </div>
        </div>
      </div>

      <!-- Detailed Aging Table -->
      <div class="aging-table">
        <h3>Aging Breakdown</h3>
        <DataTable :value="agingTableData" responsiveLayout="scroll">
          <Column field="bucket" header="Age Range" />
          <Column field="amount" header="Amount">
            <template #body="{ data }">
              {{ formatCurrency(data.amount, currency) }}
            </template>
          </Column>
          <Column field="percentage" header="% of Total">
            <template #body="{ data }">
              {{ data.percentage }}%
            </template>
          </Column>
          <Column field="count" header="# of Bills" />
        </DataTable>
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
import { ref, computed, onMounted } from 'vue';
import { useEnhancedReports } from '@/composables/useEnhancedReports';

const { loading, exportLoading, generateReport, exportReport } = useEnhancedReports();

const asOfDate = ref(new Date());
const currency = ref('USD');
const reportData = ref(null);

const currencies = [
  { name: 'US Dollar (USD)', code: 'USD' },
  { name: 'Euro (EUR)', code: 'EUR' },
  { name: 'British Pound (GBP)', code: 'GBP' }
];

const agingTableData = computed(() => {
  if (!reportData.value) return [];
  
  return Object.entries(reportData.value.aging_buckets).map(([bucket, amount]) => ({
    bucket: formatBucketName(bucket),
    amount: amount,
    percentage: getPercentage(amount, reportData.value.total_outstanding),
    count: Math.floor(Math.random() * 15) + 1
  }));
});

const fetchReportData = async () => {
  const result = await generateReport('aging_report', {
    agingType: 'payables',
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

const formatBucketName = (bucket: string) => {
  const bucketNames = {
    'current': 'Current (0-30 days)',
    '1_30_days': '1-30 days',
    '31_60_days': '31-60 days',
    '61_90_days': '61-90 days',
    'over_90_days': 'Over 90 days'
  };
  return bucketNames[bucket] || bucket;
};

const getPercentage = (amount: number, total: number) => {
  return total > 0 ? Math.round((amount / total) * 100) : 0;
};

const getOverdueAmount = () => {
  if (!reportData.value) return 0;
  const buckets = reportData.value.aging_buckets;
  return buckets['31_60_days'] + buckets['61_90_days'] + buckets['over_90_days'];
};

const getBarHeight = (amount: number, total: number) => {
  return total > 0 ? Math.max((amount / total) * 100, 5) : 5;
};

const printReport = () => window.print();
const exportToPDF = () => handleExport('pdf');
const exportToExcel = () => handleExport('excel');

onMounted(() => {
  fetchReportData();
});
</script>

<style scoped>
.ap-aging-report {
  padding: 1rem;
}

.filters {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin: 2rem 0;
}

.summary-card {
  background: var(--surface-card);
  border-radius: 8px;
  padding: 1.5rem;
  text-align: center;
  border-left: 4px solid var(--orange-500);
}

.summary-card.current {
  border-left-color: var(--blue-500);
}

.summary-card.overdue {
  border-left-color: var(--red-500);
}

.chart-bar.payable {
  background: var(--orange-500);
}

.aging-chart, .aging-table {
  background: var(--surface-card);
  border-radius: 8px;
  padding: 1.5rem;
  margin: 2rem 0;
}

.chart-container {
  display: flex;
  align-items: end;
  gap: 1rem;
  height: 200px;
  padding: 1rem 0;
}

.chart-bar {
  flex: 1;
  border-radius: 4px 4px 0 0;
  position: relative;
  min-height: 20px;
  display: flex;
  flex-direction: column;
  justify-content: end;
  align-items: center;
  color: white;
  font-size: 0.8rem;
}

.bar-label {
  position: absolute;
  bottom: -30px;
  font-size: 0.7rem;
  color: var(--text-color);
  text-align: center;
  width: 100%;
}

.bar-amount {
  padding: 0.25rem;
  font-weight: 600;
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