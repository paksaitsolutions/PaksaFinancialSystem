<template>
  <UnifiedDashboard
    title="Financial Statements"
    subtitle="Generate and view key financial reports"
    :show-back="true"
    @back="goBack"
  >
    <template #actions>
      <Button label="Export All" icon="pi pi-download" class="p-button-outlined" @click="exportAll" />
      <Button label="Generate Reports" icon="pi pi-refresh" class="p-button-success" @click="generateReports" :loading="generating" />
    </template>

    <template #content>
      <!-- Report Selection -->
      <Card class="parameters-card">
        <template #title>Report Parameters</template>
        <template #content>
          <div class="grid parameters-grid">
            <div class="col-12 md:col-3">
              <label class="compact-label">Period</label>
              <Dropdown v-model="selectedPeriod" :options="periods" optionLabel="label" optionValue="value" class="w-full compact-input" @change="onParameterChange" />
            </div>
            <div class="col-12 md:col-3">
              <label class="compact-label">Year</label>
              <Dropdown v-model="selectedYear" :options="years" class="w-full compact-input" @change="onParameterChange" />
            </div>
            <div class="col-12 md:col-3">
              <label class="compact-label">Currency</label>
              <Dropdown v-model="selectedCurrency" :options="currencies" optionLabel="name" optionValue="code" class="w-full compact-input" @change="onParameterChange" />
            </div>
            <div class="col-12 md:col-3">
              <label class="compact-label">Format</label>
              <Dropdown v-model="selectedFormat" :options="formats" optionLabel="label" optionValue="value" class="w-full compact-input" @change="onParameterChange" />
            </div>
          </div>
        </template>
      </Card>

      <!-- Financial Reports Grid -->
      <div class="grid compact-grid">
        <!-- Balance Sheet -->
        <div class="col-12 lg:col-4">
          <Card class="report-card compact-card h-full">
            <template #title>
              <div class="flex align-items-center justify-content-between compact-title">
                <span>Balance Sheet</span>
                <Button icon="pi pi-external-link" class="p-button-text p-button-sm" @click="viewReport('balance-sheet')" />
              </div>
            </template>
            <template #content>
              <div class="report-summary compact-summary">
                <div class="summary-item">
                  <span class="label">Total Assets</span>
                  <span class="value text-blue-600">{{ formatCurrency(balanceSheet.totalAssets) }}</span>
                </div>
                <div class="summary-item">
                  <span class="label">Total Liabilities</span>
                  <span class="value text-red-600">{{ formatCurrency(balanceSheet.totalLiabilities) }}</span>
                </div>
                <div class="summary-item">
                  <span class="label">Total Equity</span>
                  <span class="value text-green-600">{{ formatCurrency(balanceSheet.totalEquity) }}</span>
                </div>
              </div>
              <div class="compact-actions">
                <Button label="View Details" class="w-full" @click="viewReport('balance-sheet')" />
              </div>
            </template>
          </Card>
        </div>

        <!-- Income Statement -->
        <div class="col-12 lg:col-4">
          <Card class="report-card compact-card h-full">
            <template #title>
              <div class="flex align-items-center justify-content-between compact-title">
                <span>Income Statement</span>
                <Button icon="pi pi-external-link" class="p-button-text p-button-sm" @click="viewReport('income-statement')" />
              </div>
            </template>
            <template #content>
              <div class="report-summary compact-summary">
                <div class="summary-item">
                  <span class="label">Total Revenue</span>
                  <span class="value text-green-600">{{ formatCurrency(incomeStatement.totalRevenue) }}</span>
                </div>
                <div class="summary-item">
                  <span class="label">Total Expenses</span>
                  <span class="value text-red-600">{{ formatCurrency(incomeStatement.totalExpenses) }}</span>
                </div>
                <div class="summary-item">
                  <span class="label">Net Income</span>
                  <span class="value" :class="incomeStatement.netIncome >= 0 ? 'text-green-600' : 'text-red-600'">{{ formatCurrency(incomeStatement.netIncome) }}</span>
                </div>
              </div>
              <div class="compact-actions">
                <Button label="View Details" class="w-full" @click="viewReport('income-statement')" />
              </div>
            </template>
          </Card>
        </div>

        <!-- Cash Flow Statement -->
        <div class="col-12 lg:col-4">
          <Card class="report-card compact-card h-full">
            <template #title>
              <div class="flex align-items-center justify-content-between compact-title">
                <span>Cash Flow Statement</span>
                <Button icon="pi pi-external-link" class="p-button-text p-button-sm" @click="viewReport('cash-flow')" />
              </div>
            </template>
            <template #content>
              <div class="report-summary compact-summary">
                <div class="summary-item">
                  <span class="label">Operating Cash Flow</span>
                  <span class="value text-blue-600">{{ formatCurrency(cashFlow.operating) }}</span>
                </div>
                <div class="summary-item">
                  <span class="label">Investing Cash Flow</span>
                  <span class="value text-purple-600">{{ formatCurrency(cashFlow.investing) }}</span>
                </div>
                <div class="summary-item">
                  <span class="label">Financing Cash Flow</span>
                  <span class="value text-orange-600">{{ formatCurrency(cashFlow.financing) }}</span>
                </div>
              </div>
              <div class="compact-actions">
                <Button label="View Details" class="w-full" @click="viewReport('cash-flow')" />
              </div>
            </template>
          </Card>
        </div>
      </div>

      <!-- Additional Reports -->
      <Card class="additional-reports-card">
        <template #title>Additional Financial Reports</template>
        <template #content>
          <div class="grid compact-grid">
            <div class="col-12 md:col-6 lg:col-3" v-for="report in additionalReports" :key="report.id">
              <div class="report-item compact-item" @click="viewReport(report.id)">
                <div class="flex align-items-center gap-2">
                  <i :class="report.icon" class="text-lg text-primary"></i>
                  <div>
                    <div class="font-medium text-sm">{{ report.name }}</div>
                    <div class="text-xs text-500">{{ report.description }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </template>
      </Card>
    </template>

    <!-- Report Modal -->
    <Dialog v-model:visible="showReportModal" modal :header="currentReport?.name || 'Report'" :style="{width: '90vw', maxWidth: '1200px'}" class="report-modal">
      <div v-if="currentReport" class="report-content">
        <div class="report-header mb-4">
          <div class="flex justify-content-between align-items-center">
            <div>
              <h3 class="m-0">{{ currentReport.name }}</h3>
              <p class="text-500 m-0">Generated: {{ currentReport.generatedAt }}</p>
            </div>
            <div class="flex gap-2">
              <Button icon="pi pi-file-pdf" label="PDF" class="p-button-outlined" @click="() => exportReportAs('pdf')" />
              <Button icon="pi pi-file-excel" label="Excel" class="p-button-outlined" @click="() => exportReportAs('excel')" />
              <Button icon="pi pi-file" label="CSV" class="p-button-outlined" @click="() => exportReportAs('csv')" />
              <Button icon="pi pi-print" class="p-button-outlined" @click="printCurrentReport" />
            </div>
          </div>
        </div>

        <!-- Balance Sheet Report -->
        <div v-if="currentReport.id === 'balance-sheet'" class="balance-sheet-report">
          <div class="grid">
            <div class="col-12 md:col-6">
              <h4>Assets</h4>
              <DataTable :value="reportData.assets" class="mb-4">
                <Column field="account" header="Account"></Column>
                <Column field="amount" header="Amount">
                  <template #body="{data}">
                    {{ formatCurrency(data.amount) }}
                  </template>
                </Column>
              </DataTable>
            </div>
            <div class="col-12 md:col-6">
              <h4>Liabilities</h4>
              <DataTable :value="reportData.liabilities" class="mb-4">
                <Column field="account" header="Account"></Column>
                <Column field="amount" header="Amount">
                  <template #body="{data}">
                    {{ formatCurrency(data.amount) }}
                  </template>
                </Column>
              </DataTable>
              
              <h4>Equity</h4>
              <DataTable :value="reportData.equity">
                <Column field="account" header="Account"></Column>
                <Column field="amount" header="Amount">
                  <template #body="{data}">
                    {{ formatCurrency(data.amount) }}
                  </template>
                </Column>
              </DataTable>
            </div>
          </div>
        </div>

        <!-- Income Statement Report -->
        <div v-else-if="currentReport.id === 'income-statement'" class="income-statement-report">
          <div class="grid">
            <div class="col-12 md:col-6">
              <h4>Revenue</h4>
              <DataTable :value="reportData.revenue" class="mb-4">
                <Column field="account" header="Account"></Column>
                <Column field="amount" header="Amount">
                  <template #body="{data}">
                    {{ formatCurrency(data.amount) }}
                  </template>
                </Column>
              </DataTable>
            </div>
            <div class="col-12 md:col-6">
              <h4>Expenses</h4>
              <DataTable :value="reportData.expenses">
                <Column field="account" header="Account"></Column>
                <Column field="amount" header="Amount">
                  <template #body="{data}">
                    {{ formatCurrency(data.amount) }}
                  </template>
                </Column>
              </DataTable>
            </div>
          </div>
        </div>

        <!-- Cash Flow Report -->
        <div v-else-if="currentReport.id === 'cash-flow'" class="cash-flow-report">
          <div class="grid">
            <div class="col-12 md:col-4">
              <h4>Operating Activities</h4>
              <DataTable :value="reportData.operating" class="mb-4">
                <Column field="activity" header="Activity"></Column>
                <Column field="amount" header="Amount">
                  <template #body="{data}">
                    {{ formatCurrency(data.amount) }}
                  </template>
                </Column>
              </DataTable>
            </div>
            <div class="col-12 md:col-4">
              <h4>Investing Activities</h4>
              <DataTable :value="reportData.investing" class="mb-4">
                <Column field="activity" header="Activity"></Column>
                <Column field="amount" header="Amount">
                  <template #body="{data}">
                    {{ formatCurrency(data.amount) }}
                  </template>
                </Column>
              </DataTable>
            </div>
            <div class="col-12 md:col-4">
              <h4>Financing Activities</h4>
              <DataTable :value="reportData.financing">
                <Column field="activity" header="Activity"></Column>
                <Column field="amount" header="Amount">
                  <template #body="{data}">
                    {{ formatCurrency(data.amount) }}
                  </template>
                </Column>
              </DataTable>
            </div>
          </div>
        </div>

        <!-- Generic Report -->
        <div v-else class="generic-report">
          <p class="mb-4">{{ reportData.summary }}</p>
          <DataTable :value="reportData.items">
            <Column field="description" header="Description"></Column>
            <Column field="value" header="Value">
              <template #body="{data}">
                {{ formatCurrency(data.value) }}
              </template>
            </Column>
          </DataTable>
        </div>
      </div>
      
      <template #footer>
        <Button label="Close" class="p-button-text" @click="closeReportModal" />
      </template>
    </Dialog>
  </UnifiedDashboard>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useSnackbar } from '@/composables/useSnackbar'
import UnifiedDashboard from '@/components/ui/UnifiedDashboard.vue'
import Dialog from 'primevue/dialog'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'

const { showSuccess, showInfo, showError } = useSnackbar()
const generating = ref(false)

// Form data
const selectedPeriod = ref('current-year')
const selectedYear = ref(2024)
const selectedCurrency = ref('USD')
const selectedFormat = ref('detailed')

// Options
const periods = [
  { label: 'Current Year', value: 'current-year' },
  { label: 'Last Year', value: 'last-year' },
  { label: 'Quarter', value: 'quarter' },
  { label: 'Month', value: 'month' },
  { label: 'Custom Range', value: 'custom' }
]

const years = [2024, 2023, 2022, 2021, 2020]

const currencies = [
  { code: 'USD', name: 'US Dollar' },
  { code: 'EUR', name: 'Euro' },
  { code: 'GBP', name: 'British Pound' },
  { code: 'PKR', name: 'Pakistani Rupee' }
]

const formats = [
  { label: 'Detailed', value: 'detailed' },
  { label: 'Summary', value: 'summary' },
  { label: 'Comparative', value: 'comparative' }
]

// Mock financial data
const balanceSheet = reactive({
  totalAssets: 2500000,
  totalLiabilities: 800000,
  totalEquity: 1700000
})

const incomeStatement = reactive({
  totalRevenue: 1200000,
  totalExpenses: 950000,
  netIncome: 250000
})

const cashFlow = reactive({
  operating: 180000,
  investing: -50000,
  financing: -30000
})

const additionalReports = [
  {
    id: 'trial-balance',
    name: 'Trial Balance',
    description: 'Account balances verification',
    icon: 'pi pi-list'
  },
  {
    id: 'general-ledger',
    name: 'General Ledger',
    description: 'Detailed transaction history',
    icon: 'pi pi-book'
  },
  {
    id: 'aged-receivables',
    name: 'Aged Receivables',
    description: 'Customer payment analysis',
    icon: 'pi pi-clock'
  },
  {
    id: 'aged-payables',
    name: 'Aged Payables',
    description: 'Vendor payment analysis',
    icon: 'pi pi-calendar'
  },
  {
    id: 'budget-variance',
    name: 'Budget Variance',
    description: 'Budget vs actual comparison',
    icon: 'pi pi-chart-bar'
  },
  {
    id: 'tax-summary',
    name: 'Tax Summary',
    description: 'Tax liability overview',
    icon: 'pi pi-percentage'
  }
]

// Methods
const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: selectedCurrency.value
  }).format(amount)
}

const generateReports = async () => {
  generating.value = true
  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // Update mock data to show changes
    balanceSheet.totalAssets += Math.floor(Math.random() * 100000)
    incomeStatement.totalRevenue += Math.floor(Math.random() * 50000)
    cashFlow.operating += Math.floor(Math.random() * 25000)
    
    showSuccess('Financial statements have been updated successfully')
  } catch (error) {
    showError('Failed to generate financial reports')
    console.error('Generation error:', error)
  } finally {
    generating.value = false
  }
}

// Report modal state
const showReportModal = ref(false)
const currentReport = ref(null)
const reportData = ref(null)

const viewReport = async (reportId: string) => {
  showInfo(`Loading ${reportId} report...`)
  
  try {
    // Simulate loading report data
    await new Promise(resolve => setTimeout(resolve, 800))
    
    const reportNames = {
      'balance-sheet': 'Balance Sheet',
      'income-statement': 'Income Statement', 
      'cash-flow': 'Cash Flow Statement',
      'trial-balance': 'Trial Balance',
      'general-ledger': 'General Ledger',
      'aged-receivables': 'Aged Receivables',
      'aged-payables': 'Aged Payables',
      'budget-variance': 'Budget Variance',
      'tax-summary': 'Tax Summary'
    }
    
    const reportName = reportNames[reportId as keyof typeof reportNames] || reportId
    
    // Generate mock report data based on report type
    const mockData = generateMockReportData(reportId)
    
    currentReport.value = {
      id: reportId,
      name: reportName,
      data: mockData,
      generatedAt: new Date().toLocaleString()
    }
    
    reportData.value = mockData
    showReportModal.value = true
    
    showSuccess(`${reportName} report loaded successfully`)
  } catch (error) {
    showError(`Failed to load ${reportId} report`)
    console.error('Report loading error:', error)
  }
}

const generateMockReportData = (reportId: string) => {
  switch (reportId) {
    case 'balance-sheet':
      return {
        assets: [
          { account: 'Cash and Cash Equivalents', amount: 500000 },
          { account: 'Accounts Receivable', amount: 350000 },
          { account: 'Inventory', amount: 280000 },
          { account: 'Property, Plant & Equipment', amount: 1370000 }
        ],
        liabilities: [
          { account: 'Accounts Payable', amount: 180000 },
          { account: 'Short-term Debt', amount: 120000 },
          { account: 'Long-term Debt', amount: 500000 }
        ],
        equity: [
          { account: 'Share Capital', amount: 1000000 },
          { account: 'Retained Earnings', amount: 700000 }
        ]
      }
    case 'income-statement':
      return {
        revenue: [
          { account: 'Sales Revenue', amount: 1200000 },
          { account: 'Service Revenue', amount: 180000 }
        ],
        expenses: [
          { account: 'Cost of Goods Sold', amount: 720000 },
          { account: 'Operating Expenses', amount: 230000 },
          { account: 'Interest Expense', amount: 25000 }
        ]
      }
    case 'cash-flow':
      return {
        operating: [
          { activity: 'Net Income', amount: 250000 },
          { activity: 'Depreciation', amount: 80000 },
          { activity: 'Changes in Working Capital', amount: -50000 }
        ],
        investing: [
          { activity: 'Equipment Purchase', amount: -120000 },
          { activity: 'Investment Sales', amount: 70000 }
        ],
        financing: [
          { activity: 'Loan Proceeds', amount: 200000 },
          { activity: 'Dividend Payments', amount: -80000 }
        ]
      }
    default:
      return {
        summary: `This is a detailed ${reportId} report with comprehensive financial data and analysis.`,
        items: [
          { description: 'Sample Data Item 1', value: 125000 },
          { description: 'Sample Data Item 2', value: 89000 },
          { description: 'Sample Data Item 3', value: 156000 }
        ]
      }
  }
}

const closeReportModal = () => {
  showReportModal.value = false
  currentReport.value = null
  reportData.value = null
}

const exportCurrentReport = () => {
  if (currentReport.value) {
    showInfo(`Preparing ${currentReport.value.name} for download...`)
    
    // Create downloadable content
    const reportContent = generateReportContent(currentReport.value)
    const blob = new Blob([reportContent], { type: 'text/html' })
    const url = URL.createObjectURL(blob)
    
    // Create download link
    const link = document.createElement('a')
    link.href = url
    link.download = `${currentReport.value.name.replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.html`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    
    showSuccess(`${currentReport.value.name} downloaded successfully`)
  }
}

const printCurrentReport = () => {
  if (currentReport.value) {
    showInfo(`Preparing ${currentReport.value.name} for printing...`)
    
    // Create printable content
    const reportContent = generatePrintableContent(currentReport.value)
    
    // Open print window
    const printWindow = window.open('', '_blank')
    if (printWindow) {
      printWindow.document.write(reportContent)
      printWindow.document.close()
      
      // Wait for content to load then print
      printWindow.onload = () => {
        printWindow.print()
        printWindow.close()
      }
      
      showSuccess(`${currentReport.value.name} sent to printer`)
    } else {
      showError('Unable to open print window. Please check popup blocker settings.')
    }
  }
}

const generateReportContent = (report: any) => {
  const data = report.data
  let html = `
    <!DOCTYPE html>
    <html>
    <head>
      <title>${report.name}</title>
      <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
        h2 { color: #555; margin-top: 30px; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f8f9fa; font-weight: bold; }
        .amount { text-align: right; }
        .total { font-weight: bold; background-color: #e9ecef; }
        .generated { color: #666; font-size: 12px; margin-top: 20px; }
      </style>
    </head>
    <body>
      <h1>${report.name}</h1>
      <p class="generated">Generated: ${report.generatedAt}</p>
  `
  
  if (report.id === 'balance-sheet') {
    html += `
      <h2>Assets</h2>
      <table>
        <tr><th>Account</th><th class="amount">Amount</th></tr>
        ${data.assets.map(item => `<tr><td>${item.account}</td><td class="amount">${formatCurrency(item.amount)}</td></tr>`).join('')}
      </table>
      
      <h2>Liabilities</h2>
      <table>
        <tr><th>Account</th><th class="amount">Amount</th></tr>
        ${data.liabilities.map(item => `<tr><td>${item.account}</td><td class="amount">${formatCurrency(item.amount)}</td></tr>`).join('')}
      </table>
      
      <h2>Equity</h2>
      <table>
        <tr><th>Account</th><th class="amount">Amount</th></tr>
        ${data.equity.map(item => `<tr><td>${item.account}</td><td class="amount">${formatCurrency(item.amount)}</td></tr>`).join('')}
      </table>
    `
  } else if (report.id === 'income-statement') {
    html += `
      <h2>Revenue</h2>
      <table>
        <tr><th>Account</th><th class="amount">Amount</th></tr>
        ${data.revenue.map(item => `<tr><td>${item.account}</td><td class="amount">${formatCurrency(item.amount)}</td></tr>`).join('')}
      </table>
      
      <h2>Expenses</h2>
      <table>
        <tr><th>Account</th><th class="amount">Amount</th></tr>
        ${data.expenses.map(item => `<tr><td>${item.account}</td><td class="amount">${formatCurrency(item.amount)}</td></tr>`).join('')}
      </table>
    `
  } else if (report.id === 'cash-flow') {
    html += `
      <h2>Operating Activities</h2>
      <table>
        <tr><th>Activity</th><th class="amount">Amount</th></tr>
        ${data.operating.map(item => `<tr><td>${item.activity}</td><td class="amount">${formatCurrency(item.amount)}</td></tr>`).join('')}
      </table>
      
      <h2>Investing Activities</h2>
      <table>
        <tr><th>Activity</th><th class="amount">Amount</th></tr>
        ${data.investing.map(item => `<tr><td>${item.activity}</td><td class="amount">${formatCurrency(item.amount)}</td></tr>`).join('')}
      </table>
      
      <h2>Financing Activities</h2>
      <table>
        <tr><th>Activity</th><th class="amount">Amount</th></tr>
        ${data.financing.map(item => `<tr><td>${item.activity}</td><td class="amount">${formatCurrency(item.amount)}</td></tr>`).join('')}
      </table>
    `
  } else {
    html += `
      <p>${data.summary}</p>
      <table>
        <tr><th>Description</th><th class="amount">Value</th></tr>
        ${data.items.map(item => `<tr><td>${item.description}</td><td class="amount">${formatCurrency(item.value)}</td></tr>`).join('')}
      </table>
    `
  }
  
  html += `
    </body>
    </html>
  `
  
  return html
}

const generatePrintableContent = (report: any) => {
  return generateReportContent(report)
}

const exportReportAs = (format: 'pdf' | 'excel' | 'csv') => {
  if (!currentReport.value) return
  
  showInfo(`Exporting ${currentReport.value.name} as ${format.toUpperCase()}...`)
  
  setTimeout(() => {
    const report = currentReport.value
    const data = report.data
    const timestamp = new Date().toISOString().split('T')[0]
    const filename = `${report.name.replace(/\s+/g, '_')}_${timestamp}`
    
    if (format === 'csv') {
      exportAsCSV(data, filename, report.id)
    } else if (format === 'excel') {
      exportAsExcel(data, filename, report.id)
    } else if (format === 'pdf') {
      exportAsPDF(report, filename)
    }
    
    showSuccess(`${report.name} exported as ${format.toUpperCase()} successfully`)
  }, 800)
}

const exportAsCSV = (data: any, filename: string, reportType: string) => {
  let csvContent = ''
  
  if (reportType === 'balance-sheet') {
    csvContent = 'Section,Account,Amount\n'
    csvContent += data.assets.map((item: any) => `Assets,"${item.account}",${item.amount}`).join('\n') + '\n'
    csvContent += data.liabilities.map((item: any) => `Liabilities,"${item.account}",${item.amount}`).join('\n') + '\n'
    csvContent += data.equity.map((item: any) => `Equity,"${item.account}",${item.amount}`).join('\n')
  } else if (reportType === 'income-statement') {
    csvContent = 'Section,Account,Amount\n'
    csvContent += data.revenue.map((item: any) => `Revenue,"${item.account}",${item.amount}`).join('\n') + '\n'
    csvContent += data.expenses.map((item: any) => `Expenses,"${item.account}",${item.amount}`).join('\n')
  } else if (reportType === 'cash-flow') {
    csvContent = 'Section,Activity,Amount\n'
    csvContent += data.operating.map((item: any) => `Operating,"${item.activity}",${item.amount}`).join('\n') + '\n'
    csvContent += data.investing.map((item: any) => `Investing,"${item.activity}",${item.amount}`).join('\n') + '\n'
    csvContent += data.financing.map((item: any) => `Financing,"${item.activity}",${item.amount}`).join('\n')
  } else {
    csvContent = 'Description,Value\n'
    csvContent += data.items.map((item: any) => `"${item.description}",${item.value}`).join('\n')
  }
  
  downloadFile(csvContent, `${filename}.csv`, 'text/csv')
}

const exportAsExcel = (data: any, filename: string, reportType: string) => {
  // Simulate Excel export with HTML table format that Excel can open
  let htmlContent = `
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #000; padding: 8px; text-align: left; }
        th { background-color: #f0f0f0; font-weight: bold; }
        .amount { text-align: right; }
      </style>
    </head>
    <body>
  `
  
  if (reportType === 'balance-sheet') {
    htmlContent += `
      <h2>Assets</h2>
      <table>
        <tr><th>Account</th><th>Amount</th></tr>
        ${data.assets.map((item: any) => `<tr><td>${item.account}</td><td class="amount">${item.amount}</td></tr>`).join('')}
      </table>
      <h2>Liabilities</h2>
      <table>
        <tr><th>Account</th><th>Amount</th></tr>
        ${data.liabilities.map((item: any) => `<tr><td>${item.account}</td><td class="amount">${item.amount}</td></tr>`).join('')}
      </table>
      <h2>Equity</h2>
      <table>
        <tr><th>Account</th><th>Amount</th></tr>
        ${data.equity.map((item: any) => `<tr><td>${item.account}</td><td class="amount">${item.amount}</td></tr>`).join('')}
      </table>
    `
  }
  
  htmlContent += '</body></html>'
  downloadFile(htmlContent, `${filename}.xls`, 'application/vnd.ms-excel')
}

const exportAsPDF = (report: any, filename: string) => {
  // Create a simplified PDF-like HTML that browsers can save as PDF
  const pdfContent = generateReportContent(report)
  const printWindow = window.open('', '_blank')
  
  if (printWindow) {
    printWindow.document.write(pdfContent)
    printWindow.document.close()
    printWindow.focus()
    
    // Suggest user to save as PDF
    setTimeout(() => {
      showInfo('Use Ctrl+P (Cmd+P on Mac) and select "Save as PDF" to download as PDF')
    }, 500)
  }
}

const downloadFile = (content: string, filename: string, mimeType: string) => {
  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

const exportAll = async () => {
  showInfo('Preparing financial statements for export...')
  
  try {
    // Generate comprehensive financial statements export
    const exportData = {
      companyName: 'Paksa Financial System',
      reportDate: new Date().toLocaleDateString(),
      period: selectedPeriod.value,
      year: selectedYear.value,
      currency: selectedCurrency.value,
      format: selectedFormat.value,
      balanceSheet: {
        assets: [
          { account: 'Cash and Cash Equivalents', amount: 500000 },
          { account: 'Accounts Receivable', amount: 350000 },
          { account: 'Inventory', amount: 280000 },
          { account: 'Property, Plant & Equipment', amount: 1370000 }
        ],
        liabilities: [
          { account: 'Accounts Payable', amount: 180000 },
          { account: 'Short-term Debt', amount: 120000 },
          { account: 'Long-term Debt', amount: 500000 }
        ],
        equity: [
          { account: 'Share Capital', amount: 1000000 },
          { account: 'Retained Earnings', amount: 700000 }
        ]
      },
      incomeStatement: {
        revenue: [
          { account: 'Sales Revenue', amount: 1200000 },
          { account: 'Service Revenue', amount: 180000 }
        ],
        expenses: [
          { account: 'Cost of Goods Sold', amount: 720000 },
          { account: 'Operating Expenses', amount: 230000 },
          { account: 'Interest Expense', amount: 25000 }
        ]
      },
      cashFlow: {
        operating: [
          { activity: 'Net Income', amount: 250000 },
          { activity: 'Depreciation', amount: 80000 },
          { activity: 'Changes in Working Capital', amount: -50000 }
        ],
        investing: [
          { activity: 'Equipment Purchase', amount: -120000 },
          { activity: 'Investment Sales', amount: 70000 }
        ],
        financing: [
          { activity: 'Loan Proceeds', amount: 200000 },
          { activity: 'Dividend Payments', amount: -80000 }
        ]
      }
    }
    
    // Create CSV content for all financial statements
    let csvContent = `Financial Statements Export\n`
    csvContent += `Company: ${exportData.companyName}\n`
    csvContent += `Report Date: ${exportData.reportDate}\n`
    csvContent += `Period: ${exportData.period}\n`
    csvContent += `Year: ${exportData.year}\n`
    csvContent += `Currency: ${exportData.currency}\n\n`
    
    // Balance Sheet
    csvContent += `BALANCE SHEET\n`
    csvContent += `Section,Account,Amount\n`
    exportData.balanceSheet.assets.forEach(item => {
      csvContent += `Assets,"${item.account}",${item.amount}\n`
    })
    exportData.balanceSheet.liabilities.forEach(item => {
      csvContent += `Liabilities,"${item.account}",${item.amount}\n`
    })
    exportData.balanceSheet.equity.forEach(item => {
      csvContent += `Equity,"${item.account}",${item.amount}\n`
    })
    
    csvContent += `\nINCOME STATEMENT\n`
    csvContent += `Section,Account,Amount\n`
    exportData.incomeStatement.revenue.forEach(item => {
      csvContent += `Revenue,"${item.account}",${item.amount}\n`
    })
    exportData.incomeStatement.expenses.forEach(item => {
      csvContent += `Expenses,"${item.account}",${item.amount}\n`
    })
    
    csvContent += `\nCASH FLOW STATEMENT\n`
    csvContent += `Section,Activity,Amount\n`
    exportData.cashFlow.operating.forEach(item => {
      csvContent += `Operating,"${item.activity}",${item.amount}\n`
    })
    exportData.cashFlow.investing.forEach(item => {
      csvContent += `Investing,"${item.activity}",${item.amount}\n`
    })
    exportData.cashFlow.financing.forEach(item => {
      csvContent += `Financing,"${item.activity}",${item.amount}\n`
    })
    
    // Download the file
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `Financial_Statements_${exportData.year}_${new Date().toISOString().split('T')[0]}.csv`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    
    showSuccess('Financial statements exported successfully')
  } catch (error) {
    showError('Failed to export financial statements')
    console.error('Export error:', error)
  }
}

const goBack = () => {
  if (window.history.length > 1) {
    window.history.back()
  } else {
    // Fallback navigation
    window.location.href = '/gl'
  }
}

// Watch for parameter changes to regenerate reports
const onParameterChange = () => {
  showInfo('Report parameters updated. Click "Generate Reports" to refresh data.')
}

onMounted(() => {
  // Initialize with current data
  showInfo('Financial statements loaded successfully')
})
</script>

<style scoped>
/* Unified System Styles */
.parameters-card {
  margin-bottom: var(--spacing-md);
}

.parameters-card :deep(.p-card-body) {
  padding: var(--spacing-md);
}

.parameters-card :deep(.p-card-title) {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  margin-bottom: var(--spacing-sm);
}

.parameters-grid {
  gap: var(--spacing-sm);
}

.additional-reports-card {
  margin-top: var(--spacing-md);
}

.additional-reports-card :deep(.p-card-body) {
  padding: var(--spacing-md);
}

.additional-reports-card :deep(.p-card-title) {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  margin-bottom: var(--spacing-sm);
}

.compact-card {
  margin-bottom: 0;
}

.compact-card :deep(.p-card-body) {
  padding: var(--spacing-md);
}

.compact-card :deep(.p-card-title) {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  margin-bottom: var(--spacing-sm);
}

.compact-grid {
  gap: var(--spacing-sm);
  margin-bottom: 0;
}

.compact-label {
  display: block;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  margin-bottom: var(--spacing-xs);
  color: var(--text-color-secondary);
}

.compact-input {
  height: var(--input-height-sm);
}

.compact-title {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
}

.compact-summary {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.compact-actions {
  margin-top: var(--spacing-sm);
}

.compact-item {
  padding: var(--spacing-sm);
  border: 1px solid var(--surface-border);
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: all var(--transition-duration) ease;
  background: var(--surface-card);
}

.compact-item:hover {
  background: var(--surface-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.report-card {
  transition: transform 0.2s ease;
}

.report-card:hover {
  transform: translateY(-2px);
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-sm) 0;
  border-bottom: 1px solid var(--surface-border);
}

.summary-item:last-child {
  border-bottom: none;
}

.label {
  font-size: var(--font-size-sm);
  color: var(--text-color-secondary);
}

.value {
  font-weight: var(--font-weight-semibold);
  font-size: var(--font-size-base);
}

.report-modal :deep(.p-dialog-content) {
  padding: var(--spacing-lg);
}

.report-content {
  min-height: 400px;
}

.report-header {
  border-bottom: 1px solid var(--surface-border);
  padding-bottom: var(--spacing-sm);
  margin-bottom: var(--spacing-lg);
}

.balance-sheet-report h4,
.income-statement-report h4,
.cash-flow-report h4 {
  color: var(--text-color);
  margin-bottom: var(--spacing-sm);
  font-weight: var(--font-weight-semibold);
  font-size: var(--font-size-lg);
}

.generic-report {
  padding: var(--spacing-md) 0;
}

:deep(.p-datatable) {
  font-size: 0.875rem;
}

:deep(.p-datatable .p-datatable-thead > tr > th) {
  background: var(--surface-section);
  font-weight: var(--font-weight-semibold);
  color: var(--text-color);
  padding: var(--spacing-sm) var(--spacing-md);
}

:deep(.p-datatable .p-datatable-tbody > tr > td) {
  padding: var(--spacing-sm) var(--spacing-md);
}

@media (max-width: 768px) {
  .report-modal :deep(.p-dialog) {
    width: 95vw !important;
    margin: var(--spacing-sm);
  }
  
  .parameters-card :deep(.p-card-body),
  .additional-reports-card :deep(.p-card-body),
  .compact-card :deep(.p-card-body) {
    padding: var(--spacing-sm);
  }
}
</style>