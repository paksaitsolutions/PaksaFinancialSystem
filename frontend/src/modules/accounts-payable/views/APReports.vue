<template>
  <div class="ap-reports">
    <div class="reports-header">
      <h2>Accounts Payable Reports</h2>
      <p>Generate and view various AP reports</p>
    </div>

    <div class="reports-grid">
      <!-- Aging Report -->
      <Card class="report-card">
        <template #title>
          <div class="report-title">
            <i class="pi pi-clock"></i>
            <span>Aging Report</span>
          </div>
        </template>
        <template #content>
          <p>View outstanding bills by age categories</p>
          <div class="report-actions">
            <Button 
              label="Generate" 
              icon="pi pi-file-pdf"
              @click="generateReport('aging')"
              :loading="loadingReports.aging"
            />
            <Button 
              label="View" 
              icon="pi pi-eye"
              class="p-button-outlined"
              @click="viewReport('aging')"
            />
          </div>
        </template>
      </Card>

      <!-- Vendor Summary -->
      <Card class="report-card">
        <template #title>
          <div class="report-title">
            <i class="pi pi-users"></i>
            <span>Vendor Summary</span>
          </div>
        </template>
        <template #content>
          <p>Summary of all vendor transactions</p>
          <div class="report-actions">
            <Button 
              label="Generate" 
              icon="pi pi-file-pdf"
              @click="generateReport('vendor')"
              :loading="loadingReports.vendor"
            />
            <Button 
              label="View" 
              icon="pi pi-eye"
              class="p-button-outlined"
              @click="viewReport('vendor')"
            />
          </div>
        </template>
      </Card>

      <!-- Payment History -->
      <Card class="report-card">
        <template #title>
          <div class="report-title">
            <i class="pi pi-history"></i>
            <span>Payment History</span>
          </div>
        </template>
        <template #content>
          <p>Detailed payment transaction history</p>
          <div class="report-actions">
            <Button 
              label="Generate" 
              icon="pi pi-file-pdf"
              @click="generateReport('payments')"
              :loading="loadingReports.payments"
            />
            <Button 
              label="View" 
              icon="pi pi-eye"
              class="p-button-outlined"
              @click="viewReport('payments')"
            />
          </div>
        </template>
      </Card>

      <!-- Cash Flow Forecast -->
      <Card class="report-card">
        <template #title>
          <div class="report-title">
            <i class="pi pi-chart-line"></i>
            <span>Cash Flow Forecast</span>
          </div>
        </template>
        <template #content>
          <p>Projected cash outflows based on due dates</p>
          <div class="report-actions">
            <Button 
              label="Generate" 
              icon="pi pi-file-pdf"
              @click="generateReport('cashflow')"
              :loading="loadingReports.cashflow"
            />
            <Button 
              label="View" 
              icon="pi pi-eye"
              class="p-button-outlined"
              @click="viewReport('cashflow')"
            />
          </div>
        </template>
      </Card>
    </div>

    <!-- Report Filters -->
    <Card class="filters-card">
      <template #title>Report Filters</template>
      <template #content>
        <div class="filters-grid">
          <div class="field">
            <label for="dateRange">Date Range</label>
            <Calendar 
              id="dateRange"
              v-model="filters.dateRange" 
              selectionMode="range"
              dateFormat="mm/dd/yy"
            />
          </div>
          
          <div class="field">
            <label for="vendor">Vendor</label>
            <MultiSelect 
              id="vendor"
              v-model="filters.vendors" 
              :options="vendorOptions" 
              optionLabel="name"
              optionValue="id"
              placeholder="Select vendors"
            />
          </div>
          
          <div class="field">
            <label for="status">Status</label>
            <MultiSelect 
              id="status"
              v-model="filters.statuses" 
              :options="statusOptions" 
              optionLabel="label"
              optionValue="value"
              placeholder="Select statuses"
            />
          </div>
          
          <div class="field">
            <label for="amountRange">Amount Range</label>
            <div class="amount-inputs">
              <InputNumber 
                v-model="filters.minAmount" 
                mode="currency" 
                currency="USD"
                placeholder="Min"
              />
              <InputNumber 
                v-model="filters.maxAmount" 
                mode="currency" 
                currency="USD"
                placeholder="Max"
              />
            </div>
          </div>
        </div>
      </template>
    </Card>

    <!-- Recent Reports -->
    <Card class="recent-reports">
      <template #title>Recent Reports</template>
      <template #content>
        <DataTable :value="recentReports" responsiveLayout="scroll">
          <Column field="name" header="Report Name"></Column>
          <Column field="type" header="Type"></Column>
          <Column field="generatedDate" header="Generated">
            <template #body="slotProps">
              {{ formatDate(slotProps.data.generatedDate) }}
            </template>
          </Column>
          <Column field="size" header="Size"></Column>
          <Column header="Actions">
            <template #body="slotProps">
              <div class="action-buttons">
                <Button 
                  icon="pi pi-download" 
                  class="p-button-text p-button-sm"
                  @click="downloadReport(slotProps.data)"
                />
                <Button 
                  icon="pi pi-eye" 
                  class="p-button-text p-button-sm"
                  @click="viewStoredReport(slotProps.data)"
                />
                <Button 
                  icon="pi pi-trash" 
                  class="p-button-text p-button-sm p-button-danger"
                  @click="deleteReport(slotProps.data)"
                />
              </div>
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'

const loadingReports = reactive({
  aging: false,
  vendor: false,
  payments: false,
  cashflow: false
})

const filters = reactive({
  dateRange: null,
  vendors: [],
  statuses: [],
  minAmount: null,
  maxAmount: null
})

const vendorOptions = ref([
  { id: 1, name: 'ABC Supplies Co.' },
  { id: 2, name: 'XYZ Services Ltd.' },
  { id: 3, name: 'Tech Solutions Inc.' }
])

const statusOptions = ref([
  { label: 'Pending', value: 'pending' },
  { label: 'Approved', value: 'approved' },
  { label: 'Paid', value: 'paid' },
  { label: 'Overdue', value: 'overdue' }
])

const recentReports = ref([
  {
    id: 1,
    name: 'AP Aging Report - January 2024',
    type: 'Aging',
    generatedDate: new Date('2024-01-15'),
    size: '245 KB'
  },
  {
    id: 2,
    name: 'Vendor Summary - Q4 2023',
    type: 'Vendor Summary',
    generatedDate: new Date('2024-01-10'),
    size: '189 KB'
  },
  {
    id: 3,
    name: 'Payment History - December 2023',
    type: 'Payment History',
    generatedDate: new Date('2024-01-05'),
    size: '312 KB'
  }
])

const generateReport = async (reportType: string) => {
  loadingReports[reportType] = true
  
  try {
    // Mock report generation
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // Add to recent reports
    recentReports.value.unshift({
      id: Date.now(),
      name: `${getReportName(reportType)} - ${new Date().toLocaleDateString()}`,
      type: getReportName(reportType),
      generatedDate: new Date(),
      size: `${Math.floor(Math.random() * 500) + 100} KB`
    })
    
    console.log(`Generated ${reportType} report`)
  } catch (error) {
    console.error('Failed to generate report:', error)
  } finally {
    loadingReports[reportType] = false
  }
}

const viewReport = (reportType: string) => {
  console.log(`Viewing ${reportType} report`)
  // Open report in new tab/modal
}

const downloadReport = (report: any) => {
  console.log('Downloading report:', report.name)
  // Trigger download
}

const viewStoredReport = (report: any) => {
  console.log('Viewing stored report:', report.name)
  // Open stored report
}

const deleteReport = (report: any) => {
  const index = recentReports.value.findIndex(r => r.id === report.id)
  if (index > -1) {
    recentReports.value.splice(index, 1)
  }
}

const getReportName = (type: string) => {
  const names = {
    aging: 'AP Aging Report',
    vendor: 'Vendor Summary',
    payments: 'Payment History',
    cashflow: 'Cash Flow Forecast'
  }
  return names[type] || type
}

const formatDate = (date: Date) => {
  return new Date(date).toLocaleDateString()
}
</script>

<style scoped>
.ap-reports {
  padding: 0;
}

.reports-header {
  margin-bottom: 2rem;
}

.reports-header h2 {
  margin: 0 0 0.5rem 0;
  color: var(--text-color);
}

.reports-header p {
  margin: 0;
  color: var(--text-color-secondary);
}

.reports-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.report-card {
  height: fit-content;
}

.report-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.report-title i {
  color: var(--primary-color);
}

.report-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
}

.filters-card {
  margin-bottom: 2rem;
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.amount-inputs {
  display: flex;
  gap: 0.5rem;
}

.recent-reports {
  margin-top: 2rem;
}

.action-buttons {
  display: flex;
  gap: 0.25rem;
}

@media (max-width: 768px) {
  .reports-grid {
    grid-template-columns: 1fr;
  }
  
  .filters-grid {
    grid-template-columns: 1fr;
  }
  
  .amount-inputs {
    flex-direction: column;
  }
}
</style>