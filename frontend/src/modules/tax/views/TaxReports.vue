<template>
  <div class="p-4">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold">Tax Reports</h1>
      <div class="flex space-x-2">
        <Button 
          label="Export" 
          icon="pi pi-download" 
          class="p-button-outlined"
          @click="exportReport"
          :loading="exporting"
          :disabled="!selectedReport"
        />
      </div>
    </div>

    <Card>
      <template #content>
        <div class="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-6">
          <!-- Report Type Selection -->
          <div class="lg:col-span-1">
            <div class="sticky top-4">
              <h2 class="text-lg font-semibold mb-4">Report Types</h2>
              <div class="space-y-2">
                <div 
                  v-for="report in reportTypes" 
                  :key="report.id"
                  @click="selectReport(report)"
                  :class="[
                    'p-4 border rounded-md cursor-pointer transition-colors',
                    selectedReport?.id === report.id 
                      ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20' 
                      : 'border-gray-200 hover:border-primary-300 hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800'
                  ]"
                >
                  <div class="flex items-center">
                    <div class="p-2 rounded-full mr-3" :class="report.iconBgClass">
                      <i :class="[report.icon, 'text-white"]"></i>
                    </div>
                    <div>
                      <h3 class="font-medium">{{ report.name }}</h3>
                      <p class="text-sm text-gray-500 dark:text-gray-400">{{ report.description }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Report Content -->
          <div class="lg:col-span-3">
            <div v-if="!selectedReport" class="flex flex-col items-center justify-center h-64">
              <i class="pi pi-file-pdf text-5xl text-gray-300 mb-4"></i>
              <p class="text-gray-500">Select a report type to view details</p>
            </div>

            <div v-else>
              <!-- Report Header -->
              <div class="flex justify-between items-center mb-6">
                <div>
                  <h2 class="text-xl font-bold">{{ selectedReport.name }}</h2>
                  <p class="text-gray-600 dark:text-gray-400">{{ selectedReport.description }}</p>
                </div>
                <div class="flex space-x-2">
                  <Dropdown 
                    v-model="selectedPeriod" 
                    :options="periodOptions" 
                    optionLabel="name" 
                    placeholder="Select Period"
                    class="w-48"
                  />
                  <Calendar 
                    v-model="dateRange" 
                    selectionMode="range" 
                    :manualInput="false" 
                    dateFormat="yy-mm-dd"
                    placeholder="Select Date Range"
                    class="w-64"
                  />
                </div>
              </div>

              <!-- Report Content -->
              <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
                <!-- Loading State -->
                <div v-if="loading" class="p-8 text-center">
                  <ProgressSpinner style="width: 50px; height: 50px" strokeWidth="4" />
                  <p class="mt-2 text-gray-500">Generating report...</p>
                </div>
                
                <!-- Export Progress -->
                <div v-if="exporting" class="p-4">
                  <div class="flex items-center mb-2">
                    <i class="pi pi-spin pi-spinner text-primary-500 mr-2"></i>
                    <span>Exporting report ({{ Math.round(exportProgress) }}%)</span>
                  </div>
                  <ProgressBar :value="exportProgress" :show-value="false" style="height: 4px" />
                </div>

                <!-- Report Data -->
                <div v-else>
                  <!-- Summary Cards -->
                  <div class="grid grid-cols-1 md:grid-cols-4 gap-4 p-4 border-b dark:border-gray-700">
                    <div v-for="(stat, index) in reportStats" :key="index" class="p-4 rounded-lg" :class="stat.bgClass">
                      <div class="flex items-center">
                        <div class="p-3 rounded-full mr-4" :class="stat.iconBgClass">
                          <i :class="[stat.icon, 'text-white"]"></i>
                        </div>
                        <div>
                          <p class="text-sm text-gray-500 dark:text-gray-300">{{ stat.label }}</p>
                          <p class="text-xl font-semibold">{{ stat.value }}</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Data Table -->
                  <div class="overflow-x-auto">
                    <DataTable 
                      :value="reportData" 
                      :paginator="true" 
                      :rows="10"
                      :rowsPerPageOptions="[10, 25, 50]"
                      paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
                      currentPageReportTemplate="Showing {first} to {last} of {totalRecords} entries"
                      responsiveLayout="scroll"
                      class="p-datatable-sm"
                      :scrollable="true"
                      scrollHeight="400px"
                    >
                      <Column 
                        v-for="col in reportColumns" 
                        :key="col.field" 
                        :field="col.field" 
                        :header="col.header" 
                        :sortable="true"
                        :style="col.style"
                      >
                        <template #body="{ data }">
                          <template v-if="col.isAmount">
                            {{ formatCurrency(data[col.field]) }}
                          </template>
                          <template v-else-if="col.isDate">
                            {{ formatDate(data[col.field]) }}
                          </template>
                          <template v-else>
                            {{ data[col.field] }}
                          </template>
                        </template>
                      </Column>
                    </DataTable>
                  </div>

                  <!-- Chart Section -->
                  <div class="p-4 border-t dark:border-gray-700">
                    <h3 class="text-lg font-semibold mb-4">Tax Overview</h3>
                    <div class="h-80">
                      <Chart 
                        type="bar" 
                        :data="chartData" 
                        :options="chartOptions"
                        class="w-full h-full"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </Card>
    
    <!-- Export Dialog -->
    <ExportDialog
      v-model:visible="exportDialogVisible"
      :title="exportOptions?.title || 'Export Report'"
      :file-name="exportOptions?.fileName || 'tax-report'"
      :columns="exportOptions?.columns || []"
      :data="exportOptions?.data || []"
      :table-ref="exportOptions?.tableRef"
      :meta="{
        title: selectedReport?.name || 'Tax Report',
        description: selectedReport?.description || '',
        generatedOn: new Date().toLocaleString(),
        generatedBy: authStore.user?.name || 'System',
        includeSummary: true,
        filters: {
          Period: selectedPeriod?.name || 'Custom',
          'Date Range': dateRange && dateRange[0] && dateRange[1] 
            ? `${new Date(dateRange[0]).toLocaleDateString()} - ${new Date(dateRange[1]).toLocaleDateString()}`
            : 'All Dates'
        }
      }"
      @export="handleExport"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import ExportDialog from '@/components/common/ExportDialog.vue';
import { useExport } from '@/composables/useExport';
import { formatDate, formatCurrency } from '@/utils/formatters';

// UI Components
import Button from 'primevue/button';
import Card from 'primevue/card';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import Dropdown from 'primevue/dropdown';
import Calendar from 'primevue/calendar';
import Chart from 'primevue/chart';
import ProgressSpinner from 'primevue/progressspinner';

// Types
interface ReportType {
  id: string;
  name: string;
  description: string;
  icon: string;
  iconBgClass: string;
  permission: string;
}

interface ReportStat {
  label: string;
  value: string | number;
  icon: string;
  iconBgClass: string;
  bgClass: string;
}

// State
const authStore = useAuthStore();
const loading = ref(false);
const tableRef = ref();

// Initialize export functionality
const { 
  isExporting: exporting,
  exportProgress,
  exportDialogVisible,
  exportOptions,
  showExportDialog,
  handleExport 
} = useExport();
const selectedReport = ref<ReportType | null>(null);
const selectedPeriod = ref({ name: 'This Month', value: 'current_month' });
const dateRange = ref<Date[]>([]);

// Report Types
const reportTypes = ref<ReportType[]>([
  {
    id: 'tax_summary',
    name: 'Tax Summary',
    description: 'Overview of tax liabilities and payments',
    icon: 'pi pi-chart-bar',
    iconBgClass: 'bg-blue-500',
    permission: 'view_tax_summary'
  },
  {
    id: 'vat_report',
    name: 'VAT Report',
    description: 'Detailed VAT calculations and declarations',
    icon: 'pi pi-file-pdf',
    iconBgClass: 'bg-green-500',
    permission: 'view_vat_report'
  },
  {
    id: 'sales_tax',
    name: 'Sales Tax Report',
    description: 'Sales tax collected and payable',
    icon: 'pi pi-shopping-cart',
    iconBgClass: 'bg-purple-500',
    permission: 'view_sales_tax_report'
  },
  {
    id: 'tax_liability',
    name: 'Tax Liability',
    description: 'Current and projected tax liabilities',
    icon: 'pi pi-money-bill',
    iconBgClass: 'bg-orange-500',
    permission: 'view_tax_liability'
  },
  {
    id: 'tax_audit',
    name: 'Tax Audit',
    description: 'Detailed transaction history for audit purposes',
    icon: 'pi pi-search',
    iconBgClass: 'bg-red-500',
    permission: 'view_tax_audit'
  }
]);

// Period Options
const periodOptions = [
  { name: 'Today', value: 'today' },
  { name: 'Yesterday', value: 'yesterday' },
  { name: 'This Week', value: 'current_week' },
  { name: 'Last Week', value: 'last_week' },
  { name: 'This Month', value: 'current_month' },
  { name: 'Last Month', value: 'last_month' },
  { name: 'This Quarter', value: 'current_quarter' },
  { name: 'Last Quarter', value: 'last_quarter' },
  { name: 'This Year', value: 'current_year' },
  { name: 'Last Year', value: 'last_year' },
  { name: 'Custom Range', value: 'custom' }
];

// Mock Data
const reportData = ref([
  { id: 1, date: '2025-07-01', description: 'VAT on Sales', amount: 1500, taxCode: 'VAT-20', status: 'Paid' },
  { id: 2, date: '2025-07-05', description: 'VAT on Services', amount: 875, taxCode: 'VAT-20', status: 'Paid' },
  { id: 3, date: '2025-07-10', description: 'Sales Tax - Retail', amount: 1200, taxCode: 'ST-15', status: 'Pending' },
  { id: 4, date: '2025-07-15', description: 'VAT on Exports', amount: 0, taxCode: 'VAT-0', status: 'Exempt' },
  { id: 5, date: '2025-07-20', description: 'Withholding Tax', amount: 320, taxCode: 'WHT-10', status: 'Pending' },
  { id: 6, date: '2025-07-25', description: 'VAT on Purchases', amount: -450, taxCode: 'VAT-20', status: 'Credit' },
  { id: 7, date: '2025-07-28', description: 'Sales Tax - Wholesale', amount: 980, taxCode: 'ST-10', status: 'Paid' },
]);

const reportColumns = ref([
  { field: 'date', header: 'Date', isDate: true },
  { field: 'description', header: 'Description' },
  { field: 'taxCode', header: 'Tax Code' },
  { field: 'amount', header: 'Amount', isAmount: true, style: 'text-right' },
  { field: 'status', header: 'Status' }
]);

const reportStats = computed<ReportStat[]>(() => [
  {
    label: 'Total Tax Payable',
    value: formatCurrency(3895),
    icon: 'pi pi-arrow-up',
    iconBgClass: 'bg-blue-100 dark:bg-blue-900/50',
    bgClass: 'bg-blue-50 dark:bg-blue-900/20'
  },
  {
    label: 'Tax Paid',
    value: formatCurrency(2375),
    icon: 'pi pi-check-circle',
    iconBgClass: 'bg-green-100 dark:bg-green-900/50',
    bgClass: 'bg-green-50 dark:bg-green-900/20'
  },
  {
    label: 'Pending Payment',
    value: formatCurrency(1520),
    icon: 'pi pi-clock',
    iconBgClass: 'bg-yellow-100 dark:bg-yellow-900/50',
    bgClass: 'bg-yellow-50 dark:bg-yellow-900/20'
  },
  {
    label: 'Tax Credits',
    value: formatCurrency(450),
    icon: 'pi pi-arrow-down',
    iconBgClass: 'bg-purple-100 dark:bg-purple-900/50',
    bgClass: 'bg-purple-50 dark:bg-purple-900/20'
  }
]);

// Chart Data
const chartData = ref({
  labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
  datasets: [
    {
      label: 'Tax Payable',
      backgroundColor: '#3B82F6',
      data: [1200, 1900, 1500, 2100, 1800, 2300, 2500]
    },
    {
      label: 'Tax Paid',
      backgroundColor: '#10B981',
      data: [1000, 1600, 1300, 1900, 1500, 2100, 2300]
    },
    {
      label: 'Tax Credits',
      backgroundColor: '#8B5CF6',
      data: [200, 300, 200, 200, 300, 200, 300]
    }
  ]
});

const chartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top'
    },
    title: {
      display: false
    }
  },
  scales: {
    x: {
      grid: {
        display: false
      }
    },
    y: {
      beginAtZero: true,
      ticks: {
        callback: (value: number) => `$${value.toLocaleString()}`
      }
    }
  }
});

// Methods
const hasPermission = (permission: string) => {
  return authStore.hasPermission(permission);
};

const selectReport = (report: ReportType) => {
  if (!hasPermission(report.permission)) {
    // Show error toast or disable the selection
    return;
  }
  
  selectedReport.value = report;
  loading.value = true;
  
  // Simulate API call
  setTimeout(() => {
    loading.value = false;
  }, 800);
};

const exportReport = () => {
  if (!selectedReport.value) {
    return;
  }
  
  // Get the current report data
  const reportData = getReportData();
  
  // Prepare export options
  showExportDialog({
    title: selectedReport.value.name,
    fileName: `tax-report-${selectedReport.value.id.toLowerCase().replace(/\s+/g, '-')}`,
    columns: getExportColumns(),
    data: reportData,
    tableRef: tableRef.value,
    meta: {
      title: selectedReport.value.name,
      description: selectedReport.value.description || '',
      includeSummary: true
    }
  });
};

// Helper methods for export
const getExportColumns = () => {
  // Define columns based on the selected report type
  const commonColumns = [
    { field: 'id', header: 'ID', width: 80 },
    { field: 'date', header: 'Date', format: 'date', width: 100 },
    { field: 'reference', header: 'Reference', width: 120 },
    { field: 'description', header: 'Description', width: 200 },
    { field: 'taxCode', header: 'Tax Code', width: 120 },
    { field: 'taxRate', header: 'Rate', format: 'percent', width: 80 },
    { field: 'taxableAmount', header: 'Taxable Amount', format: 'currency', total: 'sum', width: 120 },
    { field: 'taxAmount', header: 'Tax Amount', format: 'currency', total: 'sum', width: 120 }
  ];

  // Add report-specific columns
  if (selectedReport.value?.id === 'tax-liability') {
    commonColumns.push(
      { field: 'dueDate', header: 'Due Date', format: 'date', width: 100 },
      { field: 'status', header: 'Status', width: 100 }
    );
  } else if (selectedReport.value?.id === 'vat-return') {
    commonColumns.push(
      { field: 'period', header: 'Period', width: 100 },
      { field: 'boxNumber', header: 'Box', width: 80 }
    );
  }

  return commonColumns;
};

const getReportData = () => {
  // In a real app, this would fetch the actual report data
  // For now, we'll return sample data
  const sampleData = [
    {
      id: 'TX001',
      date: new Date('2023-01-15'),
      reference: 'INV-2023-001',
      description: 'Consulting Services',
      taxCode: 'SRV-001',
      taxRate: 0.15,
      taxableAmount: 1000.00,
      taxAmount: 150.00,
      dueDate: new Date('2023-02-15'),
      status: 'Paid',
      period: 'Jan 2023',
      boxNumber: 'A1'
    },
    // Add more sample data as needed
  ];

  return sampleData;
};

// Lifecycle Hooks
onMounted(() => {
  // Set default date range to current month
  const today = new Date();
  const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
  dateRange.value = [firstDay, today];
});
</script>

<style scoped>
.p-datatable :deep(.p-datatable-thead > tr > th) {
  background-color: #f9fafb;
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.05em;
  color: #6b7280;
}

.p-datatable :deep(.p-datatable-tbody > tr) {
  transition: background-color 0.2s;
}

.p-datatable :deep(.p-datatable-tbody > tr:hover) {
  background-color: #f9fafb;
}

/* Print styles */
@media print {
  .no-print {
    display: none !important;
  }
  
  body * {
    visibility: hidden;
  }
  
  #report-content, #report-content * {
    visibility: visible;
  }
  
  #report-content {
    position: absolute;
    left: 0;
    top: 0;
    width: 100%;
  }
}
</style>
