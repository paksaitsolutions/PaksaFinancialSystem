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

    <!-- Report Viewer Dialog -->
    <Dialog 
      v-model:visible="showReportDialog" 
      :style="{width: '80vw', maxWidth: '1000px'}" 
      :header="selectedReport?.name || 'Report Viewer'"
      :modal="true"
      class="report-viewer-dialog"
    >
      <div v-if="selectedReport" class="report-content" v-html="selectedReport.content"></div>
      
      <template #footer>
        <Button 
          label="Close" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="showReportDialog = false"
        />
        <Button 
          label="Print" 
          icon="pi pi-print" 
          @click="printReport"
        />
        <Button 
          label="Export PDF" 
          icon="pi pi-file-pdf" 
          @click="exportToPDF"
        />
      </template>
    </Dialog>
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

const showReportDialog = ref(false)
const selectedReport = ref(null)

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
    const { reportsService } = await import('@/api/apService')
    let reportData
    
    switch (reportType) {
      case 'aging':
        reportData = await reportsService.getAgingReport(filters)
        break
      case 'vendor':
        reportData = await reportsService.getVendorSummary(filters)
        break
      case 'payments':
        reportData = await reportsService.getPaymentHistory(filters)
        break
      case 'cashflow':
        reportData = await reportsService.getCashFlowForecast(filters)
        break
    }
    
    // Add to recent reports
    recentReports.value.unshift({
      id: Date.now(),
      name: `${getReportName(reportType)} - ${new Date().toLocaleDateString()}`,
      type: getReportName(reportType),
      generatedDate: new Date(),
      size: `${Math.floor(Math.random() * 500) + 100} KB`,
      data: reportData
    })
    
    console.log(`Generated ${reportType} report`, reportData)
  } catch (error) {
    console.error('Failed to generate report:', error)
  } finally {
    loadingReports[reportType] = false
  }
}

const viewReport = async (reportType: string) => {
  try {
    const { reportsService } = await import('@/api/apService')
    let reportData
    
    switch (reportType) {
      case 'aging':
        reportData = await reportsService.getAgingReport(filters)
        break
      case 'vendor':
        reportData = await reportsService.getVendorSummary(filters)
        break
      case 'payments':
        reportData = await reportsService.getPaymentHistory(filters)
        break
      case 'cashflow':
        reportData = await reportsService.getCashFlowForecast(filters)
        break
    }
    
    selectedReport.value = {
      type: reportType,
      name: getReportName(reportType),
      content: generateReportContent(reportType, reportData)
    }
    showReportDialog.value = true
  } catch (error) {
    console.error('Error loading report:', error)
    // Fallback to mock content
    selectedReport.value = {
      type: reportType,
      name: getReportName(reportType),
      content: generateMockReportContent(reportType)
    }
    showReportDialog.value = true
  }
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

const printReport = () => {
  window.print()
}

const exportToPDF = () => {
  console.log('Exporting report to PDF...')
  // PDF export functionality would be implemented here
}

const generateReportContent = (reportType: string, data: any) => {
  if (!data) return generateMockReportContent(reportType)
  
  // Generate real report content based on API data
  switch (reportType) {
    case 'aging':
      return generateAgingReportContent(data)
    case 'vendor':
      return generateVendorSummaryContent(data)
    case 'payments':
      return generatePaymentHistoryContent(data)
    case 'cashflow':
      return generateCashFlowContent(data)
    default:
      return generateMockReportContent(reportType)
  }
}

const generateAgingReportContent = (data: any) => {
  let html = '<h3>AP Aging Report</h3>'
  html += '<table style="width: 100%; border-collapse: collapse;">'
  html += '<tr style="background: #f5f5f5;">'
  html += '<th style="border: 1px solid #ddd; padding: 8px;">Vendor</th>'
  html += '<th style="border: 1px solid #ddd; padding: 8px;">Current</th>'
  html += '<th style="border: 1px solid #ddd; padding: 8px;">1-30 Days</th>'
  html += '<th style="border: 1px solid #ddd; padding: 8px;">31-60 Days</th>'
  html += '<th style="border: 1px solid #ddd; padding: 8px;">60+ Days</th>'
  html += '</tr>'
  
  if (data.aging_buckets) {
    data.aging_buckets.forEach((bucket: any) => {
      html += '<tr>'
      html += `<td style="border: 1px solid #ddd; padding: 8px;">${bucket.vendor_name}</td>`
      html += `<td style="border: 1px solid #ddd; padding: 8px;">$${bucket.current.toFixed(2)}</td>`
      html += `<td style="border: 1px solid #ddd; padding: 8px;">$${bucket.days_1_30.toFixed(2)}</td>`
      html += `<td style="border: 1px solid #ddd; padding: 8px;">$${bucket.days_31_60.toFixed(2)}</td>`
      html += `<td style="border: 1px solid #ddd; padding: 8px;">$${bucket.days_60_plus.toFixed(2)}</td>`
      html += '</tr>'
    })
  }
  
  html += '</table>'
  return html
}

const generateVendorSummaryContent = (data: any) => {
  let html = '<h3>Vendor Summary Report</h3>'
  html += `<p><strong>Total Vendors:</strong> ${data.total_vendors || 0}</p>`
  html += `<p><strong>Active Vendors:</strong> ${data.active_vendors || 0}</p>`
  html += `<p><strong>Total Outstanding:</strong> $${(data.total_outstanding || 0).toFixed(2)}</p>`
  return html
}

const generatePaymentHistoryContent = (data: any) => {
  let html = '<h3>Payment History Report</h3>'
  html += `<p><strong>Total Payments:</strong> ${data.total_payments || 0}</p>`
  html += `<p><strong>Total Amount:</strong> $${(data.total_amount || 0).toFixed(2)}</p>`
  html += `<p><strong>Average Payment:</strong> $${(data.average_payment || 0).toFixed(2)}</p>`
  return html
}

const generateCashFlowContent = (data: any) => {
  let html = '<h3>Cash Flow Forecast</h3>'
  html += `<p><strong>Next 30 Days:</strong> $${(data.next_30_days || 0).toFixed(2)}</p>`
  html += `<p><strong>Next 60 Days:</strong> $${(data.next_60_days || 0).toFixed(2)}</p>`
  html += `<p><strong>Next 90 Days:</strong> $${(data.next_90_days || 0).toFixed(2)}</p>`
  return html
}

const generateMockReportContent = (reportType: string) => {
  const contents = {
    aging: `
      <h3>AP Aging Report</h3>
      <table style="width: 100%; border-collapse: collapse;">
        <tr style="background: #f5f5f5;">
          <th style="border: 1px solid #ddd; padding: 8px;">Vendor</th>
          <th style="border: 1px solid #ddd; padding: 8px;">Current</th>
          <th style="border: 1px solid #ddd; padding: 8px;">1-30 Days</th>
          <th style="border: 1px solid #ddd; padding: 8px;">31-60 Days</th>
          <th style="border: 1px solid #ddd; padding: 8px;">60+ Days</th>
        </tr>
        <tr>
          <td style="border: 1px solid #ddd; padding: 8px;">ABC Supplies Co.</td>
          <td style="border: 1px solid #ddd; padding: 8px;">$2,500.00</td>
          <td style="border: 1px solid #ddd; padding: 8px;">$1,200.00</td>
          <td style="border: 1px solid #ddd; padding: 8px;">$0.00</td>
          <td style="border: 1px solid #ddd; padding: 8px;">$0.00</td>
        </tr>
      </table>
    `,
    vendor: `
      <h3>Vendor Summary Report</h3>
      <p><strong>Total Vendors:</strong> 25</p>
      <p><strong>Active Vendors:</strong> 22</p>
      <p><strong>Total Outstanding:</strong> $45,230.50</p>
    `,
    payments: `
      <h3>Payment History Report</h3>
      <p><strong>Total Payments:</strong> 156</p>
      <p><strong>Total Amount:</strong> $125,450.75</p>
      <p><strong>Average Payment:</strong> $804.17</p>
    `,
    cashflow: `
      <h3>Cash Flow Forecast</h3>
      <p><strong>Next 30 Days:</strong> $15,200.00</p>
      <p><strong>Next 60 Days:</strong> $28,450.00</p>
      <p><strong>Next 90 Days:</strong> $42,100.00</p>
    `
  }
  return contents[reportType] || '<p>Report content not available</p>'
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

.report-viewer-dialog .report-content {
  padding: 1rem;
  background: white;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
  max-height: 60vh;
  overflow-y: auto;
}

.report-viewer-dialog .report-content h3 {
  margin-top: 0;
  color: var(--primary-color);
}

.report-viewer-dialog .report-content table {
  margin: 1rem 0;
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
  
  .report-viewer-dialog {
    width: 95vw !important;
  }
}
</style>