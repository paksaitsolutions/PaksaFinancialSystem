<template>
  <div class="enhanced-reports-view">
    <div class="reports-header">
      <h1>Enhanced Reports</h1>
      <p>Generate comprehensive financial and operational reports with multi-tenant support</p>
    </div>

    <div class="reports-grid">
      <!-- Financial Reports Section -->
      <div class="report-section">
        <h2><i class="pi pi-chart-line"></i> Financial Reports</h2>
        <div class="report-cards">
          <div class="report-card" @click="generateIncomeStatement">
            <i class="pi pi-chart-line"></i>
            <h3>Income Statement</h3>
            <p>Profit & Loss statement showing revenue and expenses</p>
            <Button label="Generate" class="p-button-sm" />
          </div>
          
          <div class="report-card" @click="generateBalanceSheet">
            <i class="pi pi-balance-scale"></i>
            <h3>Balance Sheet</h3>
            <p>Financial position showing assets, liabilities, and equity</p>
            <Button label="Generate" class="p-button-sm" />
          </div>
          
          <div class="report-card" @click="generateCashFlow">
            <i class="pi pi-money-bill"></i>
            <h3>Cash Flow Statement</h3>
            <p>Cash inflows and outflows from operations</p>
            <Button label="Generate" class="p-button-sm" />
          </div>
        </div>
      </div>

      <!-- Operational Reports Section -->
      <div class="report-section">
        <h2><i class="pi pi-cog"></i> Operational Reports</h2>
        <div class="report-cards">
          <div class="report-card" @click="generateAgingReport('receivables')">
            <i class="pi pi-credit-card"></i>
            <h3>Receivables Aging</h3>
            <p>Outstanding customer invoices by age</p>
            <Button label="Generate" class="p-button-sm" />
          </div>
          
          <div class="report-card" @click="generateAgingReport('payables')">
            <i class="pi pi-shopping-cart"></i>
            <h3>Payables Aging</h3>
            <p>Outstanding vendor bills by age</p>
            <Button label="Generate" class="p-button-sm" />
          </div>
          
          <div class="report-card" @click="generateTaxSummary">
            <i class="pi pi-percentage"></i>
            <h3>Tax Summary</h3>
            <p>VAT, GST, and other tax obligations</p>
            <Button label="Generate" class="p-button-sm" />
          </div>
        </div>
      </div>

      <!-- Recent Reports -->
      <div class="recent-reports">
        <h2><i class="pi pi-history"></i> Recent Reports</h2>
        <DataTable :value="recentReports" :loading="loading">
          <Column field="report_name" header="Report Name" />
          <Column field="report_type" header="Type">
            <template #body="{ data }">
              {{ enhancedReportsService.utils.formatReportType(data.report_type) }}
            </template>
          </Column>
          <Column field="generated_at" header="Generated">
            <template #body="{ data }">
              {{ new Date(data.generated_at).toLocaleDateString() }}
            </template>
          </Column>
          <Column field="status" header="Status">
            <template #body="{ data }">
              <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
            </template>
          </Column>
          <Column header="Actions">
            <template #body="{ data }">
              <Button icon="pi pi-eye" class="p-button-text" @click="viewReport(data)" />
              <Button icon="pi pi-download" class="p-button-text" @click="exportReport(data)" />
            </template>
          </Column>
        </DataTable>
      </div>
    </div>

    <!-- Report Generation Dialog -->
    <Dialog v-model:visible="showReportDialog" :header="dialogTitle" modal>
      <div class="report-form">
        <div class="field">
          <label>Period Start</label>
          <Calendar v-model="reportParams.periodStart" />
        </div>
        <div class="field">
          <label>Period End</label>
          <Calendar v-model="reportParams.periodEnd" />
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" class="p-button-text" @click="showReportDialog = false" />
        <Button label="Generate" @click="executeReportGeneration" :loading="generating" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import enhancedReportsService from '@/services/enhancedReportsService';

const toast = useToast();
const loading = ref(false);
const generating = ref(false);
const showReportDialog = ref(false);
const dialogTitle = ref('');
const currentReportType = ref('');
const recentReports = ref([]);

const reportParams = ref({
  periodStart: new Date(),
  periodEnd: new Date()
});

const generateIncomeStatement = () => {
  dialogTitle.value = 'Generate Income Statement';
  currentReportType.value = 'income_statement';
  showReportDialog.value = true;
};

const generateBalanceSheet = () => {
  dialogTitle.value = 'Generate Balance Sheet';
  currentReportType.value = 'balance_sheet';
  showReportDialog.value = true;
};

const generateCashFlow = () => {
  dialogTitle.value = 'Generate Cash Flow Statement';
  currentReportType.value = 'cash_flow';
  showReportDialog.value = true;
};

const generateAgingReport = (type: string) => {
  dialogTitle.value = `Generate ${type} Aging Report`;
  currentReportType.value = 'aging_report';
  showReportDialog.value = true;
};

const generateTaxSummary = () => {
  dialogTitle.value = 'Generate Tax Summary';
  currentReportType.value = 'tax_summary';
  showReportDialog.value = true;
};

const executeReportGeneration = async () => {
  generating.value = true;
  try {
    const companyId = 'current-company-id'; // Get from store
    
    let result;
    switch (currentReportType.value) {
      case 'income_statement':
        result = await enhancedReportsService.generateIncomeStatement(
          companyId, 
          reportParams.value.periodStart, 
          reportParams.value.periodEnd
        );
        break;
      case 'balance_sheet':
        result = await enhancedReportsService.generateBalanceSheet(
          companyId, 
          reportParams.value.periodEnd
        );
        break;
      // Add other cases...
    }
    
    toast.add({
      severity: 'success',
      summary: 'Report Generated',
      detail: 'Report has been generated successfully',
      life: 3000
    });
    
    showReportDialog.value = false;
    loadRecentReports();
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Generation Failed',
      detail: 'Failed to generate report',
      life: 5000
    });
  } finally {
    generating.value = false;
  }
};

const loadRecentReports = async () => {
  loading.value = true;
  try {
    const companyId = 'current-company-id'; // Get from store
    const response = await enhancedReportsService.listCompanyReports(companyId);
    recentReports.value = response.data;
  } catch (error) {
    console.error('Failed to load reports:', error);
  } finally {
    loading.value = false;
  }
};

const getStatusSeverity = (status: string) => {
  const severityMap = {
    'completed': 'success',
    'pending': 'warning',
    'generating': 'info',
    'failed': 'danger'
  };
  return severityMap[status] || 'info';
};

const viewReport = (report: any) => {
  // Navigate to report view
  console.log('View report:', report);
};

const exportReport = async (report: any) => {
  try {
    await enhancedReportsService.exportReportToPDF(report.id);
    toast.add({
      severity: 'success',
      summary: 'Export Started',
      detail: 'Report export has been initiated',
      life: 3000
    });
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Export Failed',
      detail: 'Failed to export report',
      life: 5000
    });
  }
};

onMounted(() => {
  loadRecentReports();
});
</script>

<style scoped>
.enhanced-reports-view {
  padding: 2rem;
}

.reports-header {
  margin-bottom: 2rem;
  text-align: center;
}

.reports-grid {
  display: grid;
  gap: 2rem;
}

.report-section h2 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.report-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

.report-card {
  border: 1px solid var(--surface-border);
  border-radius: 8px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.report-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.report-card i {
  font-size: 2rem;
  color: var(--primary-color);
  margin-bottom: 1rem;
}

.report-card h3 {
  margin: 0 0 0.5rem 0;
}

.report-card p {
  color: var(--text-color-secondary);
  margin-bottom: 1rem;
}

.recent-reports {
  margin-top: 2rem;
}

.report-form {
  display: grid;
  gap: 1rem;
}

.field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}
</style>