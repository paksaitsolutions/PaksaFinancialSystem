<template>
  <div class="reports-view">
    <div class="grid">
      <div class="col-12">
        <div class="flex flex-column md:flex-row justify-content-between align-items-start md:align-items-center mb-4 gap-3">
          <div>
            <h1>Payroll Reports</h1>
            <Breadcrumb :home="home" :model="breadcrumbItems" class="mb-4" />
          </div>
        </div>
      </div>

      <!-- Report Categories -->
      <div class="col-12 md:col-6 lg:col-4" v-for="category in reportCategories" :key="category.name">
        <Card class="h-full">
          <template #header>
            <div class="flex align-items-center p-3">
              <i :class="category.icon" class="text-2xl mr-3" :style="{color: category.color}"></i>
              <h3 class="m-0">{{ category.name }}</h3>
            </div>
          </template>
          <template #content>
            <div class="flex flex-column gap-2">
              <Button 
                v-for="report in category.reports" 
                :key="report.name"
                :label="report.name" 
                class="p-button-text justify-content-start" 
                @click="generateReport(report)"
                :loading="loadingReports[report.key]"
              />
            </div>
          </template>
        </Card>
      </div>

      <!-- Report Viewer -->
      <div class="col-12" v-if="currentReport">
        <Card>
          <template #header>
            <div class="flex justify-content-between align-items-center">
              <h3>{{ currentReport.title }}</h3>
              <div class="flex gap-2">
                <Button 
                  label="Export PDF" 
                  icon="pi pi-file-pdf" 
                  class="p-button-danger p-button-sm" 
                  @click="exportPDF"
                />
                <Button 
                  label="Export Excel" 
                  icon="pi pi-file-excel" 
                  class="p-button-success p-button-sm" 
                  @click="exportExcel"
                />
                <Button 
                  icon="pi pi-times" 
                  class="p-button-text p-button-sm" 
                  @click="closeReport"
                />
              </div>
            </div>
          </template>
          <template #content>
            <div class="report-filters mb-4" v-if="showFilters">
              <div class="grid">
                <div class="col-12 md:col-3">
                  <label>Date Range</label>
                  <Calendar 
                    v-model="filters.dateRange" 
                    selectionMode="range" 
                    :showIcon="true"
                    dateFormat="yy-mm-dd"
                  />
                </div>
                <div class="col-12 md:col-3">
                  <label>Department</label>
                  <Dropdown 
                    v-model="filters.department" 
                    :options="departments" 
                    optionLabel="name" 
                    optionValue="value"
                    placeholder="All Departments"
                  />
                </div>
                <div class="col-12 md:col-3">
                  <label>Employee</label>
                  <Dropdown 
                    v-model="filters.employee" 
                    :options="employees" 
                    optionLabel="name" 
                    optionValue="id"
                    placeholder="All Employees"
                    filter
                  />
                </div>
                <div class="col-12 md:col-3 flex align-items-end">
                  <Button 
                    label="Apply Filters" 
                    icon="pi pi-filter" 
                    @click="applyFilters"
                    :loading="loadingReport"
                  />
                </div>
              </div>
            </div>

            <DataTable 
              :value="reportData" 
              :loading="loadingReport"
              :paginator="true" 
              :rows="25"
              :rowsPerPageOptions="[10,25,50,100]"
              class="p-datatable-sm"
              responsiveLayout="scroll"
            >
              <template #empty>No data available for this report.</template>
              <Column 
                v-for="column in reportColumns" 
                :key="column.field"
                :field="column.field" 
                :header="column.header" 
                :sortable="column.sortable"
              >
                <template #body="{ data }" v-if="column.type === 'currency'">
                  ${{ formatCurrency(data[column.field]) }}
                </template>
                <template #body="{ data }" v-else-if="column.type === 'date'">
                  {{ formatDate(data[column.field]) }}
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import { payrollService } from '@/services/payrollService';

const toast = useToast();

// Data
const currentReport = ref(null);
const reportData = ref([]);
const reportColumns = ref([]);
const employees = ref([]);
const departments = ref([]);
const loadingReport = ref(false);
const loadingReports = ref({});
const showFilters = ref(false);

// Filters
const filters = ref({
  dateRange: null,
  department: null,
  employee: null
});

// Breadcrumb
const home = ref({ icon: 'pi pi-home', to: '/' });
const breadcrumbItems = ref([
  { label: 'Payroll', to: '/payroll' },
  { label: 'Reports' }
]);

// Report Categories
const reportCategories = ref([
  {
    name: 'Payroll Summary',
    icon: 'pi pi-chart-bar',
    color: '#3B82F6',
    reports: [
      { name: 'Payroll Summary Report', key: 'payroll_summary' },
      { name: 'Department Payroll', key: 'department_payroll' },
      { name: 'Pay Period Summary', key: 'pay_period_summary' }
    ]
  },
  {
    name: 'Employee Reports',
    icon: 'pi pi-users',
    color: '#10B981',
    reports: [
      { name: 'Employee Earnings', key: 'employee_earnings' },
      { name: 'Employee Deductions', key: 'employee_deductions' },
      { name: 'Employee Tax Summary', key: 'employee_tax_summary' }
    ]
  },
  {
    name: 'Tax Reports',
    icon: 'pi pi-calculator',
    color: '#F59E0B',
    reports: [
      { name: 'Tax Liability Report', key: 'tax_liability' },
      { name: 'Quarterly Tax Report', key: 'quarterly_tax' },
      { name: 'Annual Tax Summary', key: 'annual_tax_summary' }
    ]
  },
  {
    name: 'Compliance',
    icon: 'pi pi-shield',
    color: '#EF4444',
    reports: [
      { name: 'Audit Trail', key: 'audit_trail' },
      { name: 'Compliance Report', key: 'compliance' },
      { name: 'Year-End Report', key: 'year_end' }
    ]
  }
]);

// Methods
const generateReport = async (report: any) => {
  loadingReports.value[report.key] = true;
  showFilters.value = true;
  
  try {
    const reportConfig = getReportConfig(report.key);
    currentReport.value = {
      title: report.name,
      key: report.key
    };
    
    reportColumns.value = reportConfig.columns;
    await loadReportData(report.key);
    
  } catch (error) {
    console.error('Error generating report:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to generate report',
      life: 3000
    });
  } finally {
    loadingReports.value[report.key] = false;
  }
};

const loadReportData = async (reportKey: string) => {
  loadingReport.value = true;
  try {
    // Mock data based on report type
    reportData.value = getMockReportData(reportKey);
    
    toast.add({
      severity: 'info',
      summary: 'Info',
      detail: 'Showing sample report data',
      life: 3000
    });
  } catch (error) {
    console.error('Error loading report data:', error);
  } finally {
    loadingReport.value = false;
  }
};

const getReportConfig = (reportKey: string) => {
  const configs = {
    payroll_summary: {
      columns: [
        { field: 'period', header: 'Pay Period', sortable: true },
        { field: 'employees', header: 'Employees', sortable: true },
        { field: 'gross_pay', header: 'Gross Pay', sortable: true, type: 'currency' },
        { field: 'deductions', header: 'Deductions', sortable: true, type: 'currency' },
        { field: 'taxes', header: 'Taxes', sortable: true, type: 'currency' },
        { field: 'net_pay', header: 'Net Pay', sortable: true, type: 'currency' }
      ]
    },
    employee_earnings: {
      columns: [
        { field: 'employee_name', header: 'Employee', sortable: true },
        { field: 'department', header: 'Department', sortable: true },
        { field: 'regular_hours', header: 'Regular Hours', sortable: true },
        { field: 'overtime_hours', header: 'Overtime Hours', sortable: true },
        { field: 'gross_pay', header: 'Gross Pay', sortable: true, type: 'currency' }
      ]
    },
    tax_liability: {
      columns: [
        { field: 'tax_type', header: 'Tax Type', sortable: true },
        { field: 'jurisdiction', header: 'Jurisdiction', sortable: true },
        { field: 'employee_portion', header: 'Employee Portion', sortable: true, type: 'currency' },
        { field: 'employer_portion', header: 'Employer Portion', sortable: true, type: 'currency' },
        { field: 'total', header: 'Total', sortable: true, type: 'currency' }
      ]
    }
  };
  
  return configs[reportKey] || configs.payroll_summary;
};

const getMockReportData = (reportKey: string) => {
  const mockData = {
    payroll_summary: [
      { period: '2024-01', employees: 25, gross_pay: 125000, deductions: 15000, taxes: 25000, net_pay: 85000 },
      { period: '2024-02', employees: 26, gross_pay: 130000, deductions: 15600, taxes: 26000, net_pay: 88400 }
    ],
    employee_earnings: [
      { employee_name: 'John Doe', department: 'Engineering', regular_hours: 160, overtime_hours: 8, gross_pay: 8500 },
      { employee_name: 'Jane Smith', department: 'Marketing', regular_hours: 160, overtime_hours: 0, gross_pay: 6000 }
    ],
    tax_liability: [
      { tax_type: 'Federal Income', jurisdiction: 'Federal', employee_portion: 15000, employer_portion: 0, total: 15000 },
      { tax_type: 'Social Security', jurisdiction: 'Federal', employee_portion: 7500, employer_portion: 7500, total: 15000 }
    ]
  };
  
  return mockData[reportKey] || mockData.payroll_summary;
};

const applyFilters = () => {
  loadReportData(currentReport.value.key);
};

const closeReport = () => {
  currentReport.value = null;
  reportData.value = [];
  reportColumns.value = [];
  showFilters.value = false;
};

const exportPDF = () => {
  toast.add({
    severity: 'info',
    summary: 'Export',
    detail: 'PDF export functionality would be implemented here',
    life: 3000
  });
};

const exportExcel = () => {
  toast.add({
    severity: 'info',
    summary: 'Export',
    detail: 'Excel export functionality would be implemented here',
    life: 3000
  });
};

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value);
};

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString();
};

const loadEmployees = async () => {
  try {
    const response = await payrollService.getEmployees();
    employees.value = response.data || [];
  } catch (error) {
    employees.value = [
      { id: '1', name: 'John Doe' },
      { id: '2', name: 'Jane Smith' }
    ];
  }
};

const loadDepartments = async () => {
  try {
    const response = await payrollService.getDepartments();
    departments.value = response.map(dept => ({ name: dept, value: dept }));
  } catch (error) {
    departments.value = [
      { name: 'Engineering', value: 'engineering' },
      { name: 'Marketing', value: 'marketing' },
      { name: 'Sales', value: 'sales' }
    ];
  }
};

// Lifecycle
onMounted(() => {
  loadEmployees();
  loadDepartments();
});
</script>

<style scoped>
.reports-view {
  padding: 1rem;
}

.report-filters {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 6px;
  border: 1px solid #e9ecef;
}
</style>