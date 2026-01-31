<template>
  <div class="tax-liability-report">
    <!-- Page Header -->
    <div class="page-header">
      <h1>Tax Liability Report</h1>
      <div class="actions">
        <Button 
          icon="pi pi-refresh" 
          label="Refresh" 
          @click="loadData" 
          :loading="isLoading"
          class="p-button-text"
        />
        <Button 
          icon="pi pi-file-export" 
          label="Export" 
          @click="showExportDialog = true" 
          :loading="isExporting"
          class="p-button-text"
        />
      </div>
    </div>

    <!-- Filters Card -->
    <TaxLiabilityFilters 
      v-model:dateRange="dateRange"
      v-model:selectedTaxTypes="selectedTaxTypes"
      v-model:selectedJurisdictions="selectedJurisdictions"
      v-model:groupBy="groupBy"
      :availableTaxTypes="availableTaxTypes"
      :availableJurisdictions="availableJurisdictions"
      :isLoading="isLoading"
      @apply-filters="applyFilters"
      @reset-filters="resetFilters"
    />

    <!-- Summary Cards -->
    <TaxLiabilitySummary :reportData="reportData" />

    <!-- Report Tabs -->
    <TabView class="mt-4">
      <!-- Periods Tab -->
      <TabPanel header="By Period">
        <TaxLiabilityPeriodsTable 
          :periods="reportData?.periods || []" 
          :isLoading="isLoading"
          :currency="reportData?.currency"
          @view-transactions="viewTransactions"
        />
      </TabPanel>
      
      <!-- Summary by Tax Type Tab -->
      <TabPanel header="By Tax Type">
        <TaxLiabilityTaxTypeTable 
          :items="reportData?.summary_by_tax_type || []"
          :isLoading="isLoading"
          :currency="reportData?.currency"
          @view-details="viewTaxTypeDetails"
        />
      </TabPanel>
      
      <!-- Summary by Jurisdiction Tab -->
      <TabPanel header="By Jurisdiction">
        <TaxLiabilityJurisdictionTable 
          :items="reportData?.summary_by_jurisdiction || []"
          :isLoading="isLoading"
          :currency="reportData?.currency"
          @view-details="viewJurisdictionDetails"
        />
      </TabPanel>
      
      <!-- Charts Tab -->
      <TabPanel header="Charts">
        <TaxLiabilityCharts 
          :periods="reportData?.periods || []"
          :summaryByTaxType="reportData?.summary_by_tax_type || []"
          :currency="reportData?.currency"
        />
      </TabPanel>
    </TabView>

    <!-- Export Dialog -->
    <TaxLiabilityExportDialog 
      v-model:visible="showExportDialog"
      v-model:format="exportFormat"
      v-model:content="exportContent"
      :isLoading="isExporting"
      @export="exportReport"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'primevue/usetoast';
import { useTaxReporting } from '@/composables/useTaxReporting';
import { formatDate } from '@/utils/formatters';

const router = useRouter();
const toast = useToast();

// Use the tax reporting composable
const {
  isLoading,
  error,
  liabilityReport: reportData,
  fetchTaxLiabilityReport,
  exportTaxReport
} = useTaxReporting();

// Local state
const isExporting = ref(false);
const showExportDialog = ref(false);
const exportFormat = ref('PDF');
const exportContent = ref('Current View');

// Default to current month
const today = new Date();
const firstDayOfMonth = new Date(today.getFullYear(), today.getMonth(), 1);
const dateRange = ref([firstDayOfMonth, today]);

// Filter options
const selectedTaxTypes = ref<string[]>([]);
const selectedJurisdictions = ref<string[]>([]);
const groupBy = ref('month');

// Mock data for demo - in a real app, these would come from the API
const availableTaxTypes = ref([
  { code: 'vat', name: 'VAT' },
  { code: 'sales_tax', name: 'Sales Tax' },
  { code: 'gst', name: 'GST' },
  { code: 'hst', name: 'HST' },
  { code: 'pst', name: 'PST' }
]);

const availableJurisdictions = ref([
  { code: 'US', name: 'United States' },
  { code: 'US-CA', name: 'California' },
  { code: 'US-NY', name: 'New York' },
  { code: 'US-TX', name: 'Texas' },
  { code: 'CA', name: 'Canada' },
  { code: 'CA-ON', name: 'Ontario' },
  { code: 'CA-BC', name: 'British Columbia' },
  { code: 'GB', name: 'United Kingdom' },
  { code: 'AU', name: 'Australia' },
  { code: 'EU', name: 'European Union' }
]);

// Computed
const hasData = computed(() => {
  return reportData.value !== null && 
         (reportData.value?.periods?.length > 0 || 
          reportData.value?.summary_by_tax_type?.length > 0 || 
          reportData.value?.summary_by_jurisdiction?.length > 0);
});

// Methods
const loadData = async () => {
  try {
    const [startDate, endDate] = dateRange.value || [];
    
    if (!startDate || !endDate) {
      toast.add({
        severity: 'warn',
        summary: 'Warning',
        detail: 'Please select a date range',
        life: 3000
      });
      return;
    }
    
    await fetchTaxLiabilityReport({
      start_date: formatDate(startDate, 'yyyy-MM-dd'),
      end_date: formatDate(endDate, 'yyyy-MM-dd'),
      tax_types: selectedTaxTypes.value,
      jurisdiction_codes: selectedJurisdictions.value,
      group_by: groupBy.value
    });
  } catch (error) {
    console.error('Error loading tax liability report:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load tax liability report',
      life: 5000
    });
  }
};

const resetFilters = () => {
  dateRange.value = [firstDayOfMonth, today];
  selectedTaxTypes.value = [];
  selectedJurisdictions.value = [];
  groupBy.value = 'month';
};

const applyFilters = () => {
  loadData();
};

const exportReport = async () => {
  if (!exportFormat.value) {
    toast.add({
      severity: 'warn',
      summary: 'Warning',
      detail: 'Please select a format',
      life: 3000
    });
    return;
  }
  
  isExporting.value = true;
  
  try {
    const [startDate, endDate] = dateRange.value || [];
    const format = exportFormat.value.toLowerCase() as 'pdf' | 'excel' | 'csv';
    
    const filter = {
      start_date: startDate ? formatDate(startDate, 'yyyy-MM-dd') : '',
      end_date: endDate ? formatDate(endDate, 'yyyy-MM-dd') : '',
      tax_types: selectedTaxTypes.value,
      jurisdiction_codes: selectedJurisdictions.value,
      group_by: groupBy.value,
      export_type: exportContent.value === 'Full Report' ? 'full' : 'current'
    };
    
    const blob = await exportTaxReport(format, filter);
    
    // Create download link
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `tax-liability-report-${formatDate(new Date(), 'yyyyMMdd')}.${format}`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
    
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Export started successfully',
      life: 3000
    });
    
    showExportDialog.value = false;
  } catch (error) {
    console.error('Error exporting report:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to export report',
      life: 5000
    });
  } finally {
    isExporting.value = false;
  }
};

const viewTransactions = (period: any) => {
  // Navigate to transactions page with filters applied
  const [startDate, endDate] = dateRange.value || [];
  
  router.push({
    name: 'transactions',
    query: {
      tax_type: period.tax_type,
      jurisdiction: period.jurisdiction_code,
      start_date: startDate ? formatDate(startDate, 'yyyy-MM-dd') : undefined,
      end_date: endDate ? formatDate(endDate, 'yyyy-MM-dd') : undefined,
      status: 'posted'
    }
  });
};

const viewTaxTypeDetails = (taxType: any) => {
  // Navigate to tax type details page
  router.push({
    name: 'tax-type-details',
    params: { taxType: taxType.tax_type },
    query: {
      jurisdiction: taxType.jurisdiction_code
    }
  });
};

const viewJurisdictionDetails = (jurisdiction: any) => {
  // Navigate to jurisdiction details page
  router.push({
    name: 'tax-jurisdiction-details',
    params: { code: jurisdiction.jurisdiction_code },
    query: {
      tax_type: jurisdiction.tax_type
    }
  });
};

// Lifecycle hooks
onMounted(() => {
  // Load initial data
  loadData();
});

// Watch for changes in the report data to update charts
watch(reportData, () => {
  // Charts will automatically update due to computed properties
});
</script>

<style scoped>
.tax-liability-report {
  padding: 1rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.page-header h1 {
  margin: 0;
  font-size: 1.75rem;
  font-weight: 600;
  color: var(--text-color);
}

.actions {
  display: flex;
  gap: 0.5rem;
}

/* Responsive adjustments */
@media (max-width: 960px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .actions {
    width: 100%;
    justify-content: flex-end;
  }
}

@media (max-width: 640px) {
  .actions {
    flex-direction: column;
    width: 100%;
  }
  
  .actions .p-button {
    width: 100%;
    justify-content: center;
  }
}
</style>
