<template>
  <div class="financial-statements">
    <div class="flex justify-content-between align-items-center mb-4">
      <h2>Financial Statements</h2>
      <div class="flex gap-2">
        <Button 
          icon="pi pi-download" 
          label="Export" 
          @click="showExportDialog = true"
          class="p-button-outlined"
          :loading="exportInProgress"
          :disabled="!exportData?.length"
          v-tooltip="exportData?.length ? 'Export financial statements' : 'No data to export'"
        />
        <Button 
          label="Generate Report" 
          icon="pi pi-file-pdf" 
          @click="showReportDialog = true"
          class="p-button-success"
          v-tooltip="'Generate custom report'"
        />
      </div>
    </div>

    <div class="grid">
      <!-- Balance Sheet Card -->
      <div class="col-12 lg:col-6">
        <div class="card h-full">
          <!-- ... -->
        </div>
      </div>

      <!-- ... -->

      <!-- Export Dialog -->
      <ExportDialog
        v-model:visible="showExportDialog"
        title="Export Financial Statements"
        :file-name="exportFileName"
        :columns="exportColumns"
        :data="exportData"
        :meta="{
          title: activeTab === 'balance-sheet' ? 'Balance Sheet' : 
                 activeTab === 'income-statement' ? 'Income Statement' : 'Cash Flow Statement',
          description: activeTab === 'balance-sheet' ? 'Snapshot of assets, liabilities, and equity' :
                      activeTab === 'income-statement' ? 'Revenue, expenses, and profitability' : 'Cash inflows and outflows',
          generatedOn: new Date().toLocaleString(),
          generatedBy: 'System',
          includeSummary: true,
          filters: {
            'Date Range': formatDateRange(dateRange.start, dateRange.end),
            'Report Type': activeTab.value === 'balance-sheet' ? 'Balance Sheet' : 
                          activeTab.value === 'income-statement' ? 'Income Statement' : 'Cash Flow Statement'
          }
        }"
        @export="handleExport"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { useToast } from 'primevue/usetoast';
import Button from 'primevue/button';
import ExportDialog from '@/components/common/ExportDialog.vue';
import { useExport } from '@/composables/useExport';
import { useGLStore } from '@/modules/general-ledger/store';

// Initialize composables
const { t } = useI18n();
const toast = useToast();
const glStore = useGLStore();

// Refs
const loading = ref(false);
const showReportDialog = ref(false);
const showExportDialog = ref(false);
const activeTab = ref('balance-sheet');
const startDateMenu = ref(false);
const endDateMenu = ref(false);

// Export configuration
const exportFileName = computed(() => `financial-statements-${activeTab.value}-${new Date().toISOString().split('T')[0]}`);

// Date range for reports
const dateRange = ref({
  start: new Date(new Date().getFullYear(), 0, 1), // Start of current year
  end: new Date() // Today
});

// Format date for display
const formatDate = (date, includeTime = false) => {
  if (!date) return '';
  const options = {
    year: 'numeric',
    month: 'short',
    day: '2-digit'
  };
  
  if (includeTime) {
    options.hour = '2-digit';
    options.minute = '2-digit';
  }
  
  return new Intl.DateTimeFormat('en-US', options).format(new Date(date));
};

// Format date range for display
const formatDateRange = (start, end) => {
  if (!start || !end) return 'All dates';
  return `${formatDate(start)} - ${formatDate(end)}`;
};

// Format currency
const formatCurrency = (value, returnRaw = false) => {
  if (value === null || value === undefined) return returnRaw ? 0 : '-';
  
  const numValue = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(numValue)) return returnRaw ? 0 : '-';
  
  return returnRaw ? numValue : new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(numValue);
};

// Export columns configuration
const exportColumns = computed(() => {
  if (activeTab.value === 'balance-sheet') {
    return [
      { field: 'account', header: 'Account' },
      { field: 'balance', header: 'Balance', format: (val) => formatCurrency(val, true) },
      { field: 'previousBalance', header: 'Previous Balance', format: (val) => formatCurrency(val, true) },
      { field: 'change', header: 'Change', format: (val) => formatCurrency(val, true) }
    ];
  } else if (activeTab.value === 'income-statement') {
    return [
      { field: 'account', header: 'Account' },
      { field: 'amount', header: 'Amount', format: (val) => formatCurrency(val, true) },
      { field: 'budget', header: 'Budget', format: (val) => formatCurrency(val, true) },
      { field: 'variance', header: 'Variance', format: (val) => formatCurrency(val, true) }
    ];
  } else {
    // Cash flow
    return [
      { field: 'category', header: 'Category' },
      { field: 'amount', header: 'Amount', format: (val) => formatCurrency(val, true) },
      { field: 'previousAmount', header: 'Previous Period', format: (val) => formatCurrency(val, true) },
      { field: 'change', header: 'Change', format: (val) => formatCurrency(val, true) }
    ];
  }
});

// Prepare data for export
const exportData = computed(() => {
  // This would be replaced with actual data from your store/API
  if (activeTab.value === 'balance-sheet') {
    return glStore.balanceSheet?.map(item => ({
      account: item.account,
      balance: item.balance,
      previousBalance: item.previousBalance || 0,
      change: (item.balance - (item.previousBalance || 0))
    })) || [];
  } else if (activeTab.value === 'income-statement') {
    return glStore.incomeStatement?.map(item => ({
      account: item.account,
      amount: item.amount,
      budget: item.budget || 0,
      variance: (item.amount - (item.budget || 0))
    })) || [];
  } else {
    return glStore.cashFlow?.map(item => ({
      category: item.category,
      amount: item.amount,
      previousAmount: item.previousAmount || 0,
      change: (item.amount - (item.previousAmount || 0))
    })) || [];
  }
});

// Initialize export functionality
const { exportData: exportHandler, exportProgress, exportInProgress } = useExport({
  data: exportData,
  columns: exportColumns,
  fileName: exportFileName,
  meta: {
    title: activeTab.value === 'balance-sheet' ? 'Balance Sheet' : 
           activeTab.value === 'income-statement' ? 'Income Statement' : 'Cash Flow Statement',
    description: activeTab.value === 'balance-sheet' ? 'Snapshot of assets, liabilities, and equity' :
                activeTab.value === 'income-statement' ? 'Revenue, expenses, and profitability' : 'Cash inflows and outflows',
    generatedOn: new Date().toLocaleString(),
    generatedBy: 'System',
    filters: {
      'Date Range': formatDateRange(dateRange.start, dateRange.end),
      'Report Type': activeTab.value === 'balance-sheet' ? 'Balance Sheet' : 
                    activeTab.value === 'income-statement' ? 'Income Statement' : 'Cash Flow Statement'
    }
  }
});

// Handle export
const handleExport = async ({ format, options }) => {
  try {
    await exportHandler(format, options);
    toast.add({
      severity: 'success',
      summary: 'Export Successful',
      detail: 'Financial statements exported successfully',
      life: 3000
    });
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
