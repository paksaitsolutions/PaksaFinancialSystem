<template>
  <div class="p-4">
    <Card>
      <template #title>Payroll Reports</template>
      <template #content>
        <div class="grid">
          <div class="col-12">
            <Message severity="info" :closable="false">
              <p>Generate and manage payroll reports.</p>
              <p class="mt-2">Select a report type and date range to generate detailed payroll reports.</p>
            </Message>
          </div>
          
          <!-- Report Type Selection -->
          <div class="col-12 md:col-4">
            <Card class="h-full">
              <template #title>Report Type</template>
              <template #content>
                <div class="field">
                  <label for="reportType" class="block text-500 mb-2">Select Report</label>
                  <Dropdown 
                    v-model="selectedReport" 
                    :options="reportTypes" 
                    optionLabel="name" 
                    placeholder="Select a report"
                    class="w-full"
                  />
                </div>
                
                <div class="field mt-4">
                  <label for="dateRange" class="block text-500 mb-2">Date Range</label>
                  <Calendar 
                    v-model="dateRange" 
                    selectionMode="range" 
                    :showIcon="true" 
                    dateFormat="yy-mm-dd"
                    class="w-full"
                    :manualInput="false"
                  />
                </div>
                
                <div class="mt-4">
                  <Button 
                    label="Generate Report" 
                    icon="pi pi-file-pdf" 
                    class="p-button-primary w-full"
                    :disabled="!selectedReport || !dateRange"
                    @click="generateReport"
                  />
                </div>
              </template>
            </Card>
          </div>

          <!-- Report Preview -->
          <div class="col-12 md:col-8">
            <Card>
              <template #title>Report Preview</template>
              <template #content>
                <div v-if="reportData" class="report-preview">
                  <DataTable 
                    :value="reportData" 
                    :paginator="true" 
                    :rows="10"
                    :rowsPerPageOptions="[5, 10, 25, 50]"
                    :loading="loading"
                    scrollable
                    scrollHeight="flex"
                    class="p-datatable-sm"
                  >
                    <Column field="employeeId" header="Employee ID" :sortable="true"></Column>
                    <Column field="employeeName" header="Name" :sortable="true"></Column>
                    <Column field="department" header="Department" :sortable="true"></Column>
                    <Column field="grossPay" header="Gross Pay" :sortable="true">
                      <template #body="{ data }">
                        {{ formatCurrency(data.grossPay) }}
                      </template>
                    </Column>
                    <Column field="deductions" header="Deductions" :sortable="true">
                      <template #body="{ data }">
                        {{ formatCurrency(data.deductions) }}
                      </template>
                    </Column>
                    <Column field="netPay" header="Net Pay" :sortable="true">
                      <template #body="{ data }">
                        <strong>{{ formatCurrency(data.netPay) }}</strong>
                      </template>
                    </Column>
                  </DataTable>
                  
                  <div class="flex justify-content-end mt-4">
                    <Button 
                      label="Export to Excel" 
                      icon="pi pi-file-excel" 
                      class="p-button-success mr-2"
                      @click="exportToExcel"
                    />
                    <Button 
                      label="Print" 
                      icon="pi pi-print" 
                      class="p-button-secondary"
                      @click="printReport"
                    />
                  </div>
                </div>
                <div v-else class="flex align-items-center justify-content-center" style="min-height: 300px;">
                  <div class="text-center">
                    <i class="pi pi-search" style="font-size: 3rem; color: var(--primary-color)"></i>
                    <p class="mt-3 text-600">Select a report type and date range to generate a report</p>
                  </div>
                </div>
              </template>
            </Card>
          </div>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import Card from 'primevue/card';
import Button from 'primevue/button';
import Message from 'primevue/message';
import Dropdown from 'primevue/dropdown';
import Calendar from 'primevue/calendar';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import { useToast } from 'primevue/usetoast';

const toast = useToast();

// Report types
const reportTypes = ref([
  { name: 'Payroll Summary', value: 'summary' },
  { name: 'Employee Earnings', value: 'earnings' },
  { name: 'Tax Deductions', value: 'tax' },
  { name: 'Benefits Summary', value: 'benefits' },
  { name: 'Department Summary', value: 'department' },
  { name: 'Year-to-Date Summary', value: 'ytd' },
]);

const selectedReport = ref();
const dateRange = ref();
const loading = ref(false);

// Mock data for demonstration
interface ReportItem {
  employeeId: string;
  employeeName: string;
  department: string | undefined;
  grossPay: number;
  deductions: number;
  netPay: number;
}

const reportData = ref<ReportItem[]>([]);

// Format currency
const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(value);
};

// Generate report
const generateReport = () => {
  if (!selectedReport.value || !dateRange.value) return;
  
  loading.value = true;
  
  // Simulate API call
  setTimeout(() => {
    // Mock data - in a real app, this would come from an API
    reportData.value = Array.from({ length: 10 }, (_, i) => ({
      employeeId: `EMP${1000 + i}`,
      employeeName: `Employee ${i + 1}`,
      department: ['HR', 'IT', 'Finance', 'Operations', 'Sales'][Math.floor(Math.random() * 5)],
      grossPay: 3000 + Math.random() * 7000,
      deductions: 500 + Math.random() * 1000,
      netPay: 0
    }));
    
    // Calculate net pay
    reportData.value = reportData.value.map((item: ReportItem) => ({
      ...item,
      netPay: item.grossPay - item.deductions
    }));
    
    loading.value = false;
    
    toast.add({
      severity: 'success',
      summary: 'Report Generated',
      detail: `${selectedReport.value.name} report has been generated successfully.`,
      life: 3000
    });
  }, 1000);
};

// Export to Excel
const exportToExcel = () => {
  toast.add({
    severity: 'info',
    summary: 'Export Started',
    detail: 'Preparing Excel export...',
    life: 3000
  });
  
  // In a real app, this would generate and download an Excel file
  setTimeout(() => {
    toast.add({
      severity: 'success',
      summary: 'Export Complete',
      detail: 'Report has been exported to Excel.',
      life: 3000
    });
  }, 1500);
};

// Print report
const printReport = () => {
  window.print();
};
</script>

<style scoped>
.p-card {
  margin-bottom: 1rem;
}

:deep(.p-card-title) {
  font-size: 1.25rem;
  font-weight: 600;
}

:deep(.p-card-content) {
  padding: 1.25rem 1.5rem;
}

.report-preview {
  min-height: 400px;
}

@media print {
  .p-datatable {
    width: 100% !important;
  }
  
  .p-datatable-thead > tr > th {
    background-color: #f8f9fa !important;
    color: #343a40 !important;
  }
  
  .p-datatable-tbody > tr:nth-child(even) {
    background-color: #f8f9fa !important;
  }
}
</style>
