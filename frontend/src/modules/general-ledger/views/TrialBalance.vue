<template>
  <div class="trial-balance">
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <Button icon="pi pi-arrow-left" class="p-button-text" @click="$router.go(-1)" />
          <div>
            <h1>Trial Balance</h1>
            <p class="subtitle">View account balances and verify debits equal credits</p>
          </div>
        </div>
        <div class="header-actions">
          <Button label="Export PDF" icon="pi pi-file-pdf" class="p-button-outlined" @click="exportToPDF" :loading="exportingPDF" />
          <Button label="Export CSV" icon="pi pi-file" class="p-button-outlined" @click="exportToExcel" :loading="exportingExcel" />
          <Button label="Print" icon="pi pi-print" class="p-button-outlined" @click="printReport" />
        </div>
      </div>
    </div>

    <div class="content-container">
      <Card>
        <template #title>
          <div class="flex justify-content-between align-items-center">
            <span>Trial Balance Report</span>
            <div class="flex gap-2">
              <Calendar v-model="asOfDate" dateFormat="mm/dd/yy" showIcon placeholder="As of Date" />
              <Button label="Generate" icon="pi pi-refresh" @click="generateReport" :loading="loading" />
            </div>
          </div>
        </template>
        
        <template #content>
          <div class="report-header mb-4">
            <div class="text-center">
              <h2 class="text-2xl font-bold mb-1">Paksa Financial System</h2>
              <h3 class="text-xl mb-1">Trial Balance</h3>
              <p class="text-600">As of {{ formatDate(asOfDate) }}</p>
            </div>
          </div>

          <DataTable 
            :value="trialBalanceData" 
            :loading="loading"
            responsiveLayout="scroll"
            class="trial-balance-table"
          >
            <Column field="accountCode" header="Account Code" style="width: 120px">
              <template #body="{ data }">
                <span class="font-mono">{{ data.accountCode }}</span>
              </template>
            </Column>

            <Column field="accountName" header="Account Name">
              <template #body="{ data }">
                <div class="flex align-items-center gap-2">
                  <div class="account-type-indicator" :class="getTypeColor(data.accountType)"></div>
                  <span>{{ data.accountName }}</span>
                </div>
              </template>
            </Column>

            <Column field="debit" header="Debit" class="text-right" style="width: 150px">
              <template #body="{ data }">
                <span v-if="data.debit > 0" class="font-medium">
                  {{ formatCurrency(data.debit) }}
                </span>
                <span v-else class="text-400">-</span>
              </template>
            </Column>

            <Column field="credit" header="Credit" class="text-right" style="width: 150px">
              <template #body="{ data }">
                <span v-if="data.credit > 0" class="font-medium">
                  {{ formatCurrency(data.credit) }}
                </span>
                <span v-else class="text-400">-</span>
              </template>
            </Column>

            <template #footer>
              <div class="trial-balance-totals">
                <div class="totals-row">
                  <div class="totals-label">
                    <strong>TOTALS</strong>
                  </div>
                  <div class="totals-debit">
                    <strong>{{ formatCurrency(totalDebits) }}</strong>
                  </div>
                  <div class="totals-credit">
                    <strong>{{ formatCurrency(totalCredits) }}</strong>
                  </div>
                </div>
                <div class="balance-check" :class="{ 'balanced': isBalanced, 'unbalanced': !isBalanced }">
                  <i :class="isBalanced ? 'pi pi-check-circle' : 'pi pi-exclamation-triangle'"></i>
                  <span>{{ isBalanced ? 'Trial Balance is Balanced' : 'Trial Balance is NOT Balanced' }}</span>
                  <span v-if="!isBalanced" class="difference">
                    (Difference: {{ formatCurrency(Math.abs(totalDebits - totalCredits)) }})
                  </span>
                </div>
              </div>
            </template>
          </DataTable>

          <!-- Summary by Account Type -->
          <div class="mt-4">
            <h4 class="mb-3">Summary by Account Type</h4>
            <div class="grid">
              <div class="col-12 md:col-6">
                <DataTable :value="accountTypeSummary" class="p-datatable-sm">
                  <Column field="type" header="Account Type">
                    <template #body="{ data }">
                      <div class="flex align-items-center gap-2">
                        <div class="account-type-indicator" :class="getTypeColor(data.type)"></div>
                        <span>{{ data.type }}</span>
                      </div>
                    </template>
                  </Column>
                  <Column field="balance" header="Total Balance" class="text-right">
                    <template #body="{ data }">
                      <span :class="data.balance >= 0 ? 'text-green-600' : 'text-red-600'" class="font-medium">
                        {{ formatCurrency(Math.abs(data.balance)) }}
                      </span>
                    </template>
                  </Column>
                </DataTable>
              </div>
            </div>
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

const loading = ref(false)
const exportingPDF = ref(false)
const exportingExcel = ref(false)
const asOfDate = ref(new Date())

const trialBalanceData = ref([
  { accountCode: '1000', accountName: 'Cash', accountType: 'Asset', debit: 50000, credit: 0 },
  { accountCode: '1100', accountName: 'Accounts Receivable', accountType: 'Asset', debit: 25000, credit: 0 },
  { accountCode: '1200', accountName: 'Inventory', accountType: 'Asset', debit: 75000, credit: 0 },
  { accountCode: '1500', accountName: 'Equipment', accountType: 'Asset', debit: 100000, credit: 0 },
  { accountCode: '2000', accountName: 'Accounts Payable', accountType: 'Liability', debit: 0, credit: 15000 },
  { accountCode: '2100', accountName: 'Notes Payable', accountType: 'Liability', debit: 0, credit: 50000 },
  { accountCode: '3000', accountName: 'Owner Equity', accountType: 'Equity', debit: 0, credit: 100000 },
  { accountCode: '4000', accountName: 'Sales Revenue', accountType: 'Revenue', debit: 0, credit: 45000 },
  { accountCode: '5000', accountName: 'Cost of Goods Sold', accountType: 'Expense', debit: 20000, credit: 0 },
  { accountCode: '6000', accountName: 'Office Expenses', accountType: 'Expense', debit: 8000, credit: 0 },
  { accountCode: '6100', accountName: 'Rent Expense', accountType: 'Expense', debit: 12000, credit: 0 }
])

const totalDebits = computed(() => {
  return trialBalanceData.value.reduce((sum, item) => sum + item.debit, 0)
})

const totalCredits = computed(() => {
  return trialBalanceData.value.reduce((sum, item) => sum + item.credit, 0)
})

const isBalanced = computed(() => {
  return Math.abs(totalDebits.value - totalCredits.value) < 0.01
})

const accountTypeSummary = computed(() => {
  const summary = {}
  
  trialBalanceData.value.forEach(item => {
    if (!summary[item.accountType]) {
      summary[item.accountType] = { type: item.accountType, balance: 0 }
    }
    
    // For assets and expenses, debit increases balance
    // For liabilities, equity, and revenue, credit increases balance
    if (['Asset', 'Expense'].includes(item.accountType)) {
      summary[item.accountType].balance += item.debit - item.credit
    } else {
      summary[item.accountType].balance += item.credit - item.debit
    }
  })
  
  return Object.values(summary)
})

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value)
}

const formatDate = (date: Date) => {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  }).format(date)
}

const getTypeColor = (type: string) => {
  const colors = {
    Asset: 'bg-blue-500',
    Liability: 'bg-red-500',
    Equity: 'bg-green-500',
    Revenue: 'bg-teal-500',
    Expense: 'bg-amber-500'
  }
  return colors[type] || 'bg-gray-500'
}

const generateReport = async () => {
  loading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    // Mock data refresh
  } finally {
    loading.value = false
  }
}

const exportToPDF = async () => {
  exportingPDF.value = true
  try {
    console.log('Starting PDF export...')
    const response = await fetch('http://localhost:8000/api/v1/gl/reports/trial-balance/export/pdf', {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Accept': 'application/pdf,text/html'
      },
      body: JSON.stringify({ asOfDate: asOfDate.value, data: trialBalanceData.value })
    })
    
    console.log('PDF export response:', response.status, response.headers.get('content-type'))
    
    if (response.ok) {
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      
      // Check content type to determine file extension
      const contentType = response.headers.get('content-type')
      if (contentType?.includes('text/html')) {
        a.download = `trial-balance-${formatDate(asOfDate.value)}.html`
      } else {
        a.download = `trial-balance-${formatDate(asOfDate.value)}.pdf`
      }
      
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      console.log('PDF export successful')
    } else {
      const errorText = await response.text()
      console.error('PDF export failed:', response.status, response.statusText, errorText)
      alert(`PDF export failed: ${response.status} ${response.statusText}`)
    }
  } catch (error) {
    console.error('PDF export failed:', error)
    alert('PDF export failed. Please check your connection and try again.')
  } finally {
    exportingPDF.value = false
  }
}

const exportToExcel = async () => {
  exportingExcel.value = true
  try {
    console.log('Starting Excel export...')
    const response = await fetch('http://localhost:8000/api/v1/gl/reports/trial-balance/export/excel', {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      },
      body: JSON.stringify({ asOfDate: asOfDate.value, data: trialBalanceData.value })
    })
    
    console.log('Excel export response:', response.status, response.headers.get('content-type'))
    
    if (response.ok) {
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `trial-balance-${formatDate(asOfDate.value)}.csv`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      console.log('CSV export successful')
    } else {
      const errorText = await response.text()
      console.error('Excel export failed:', response.status, response.statusText, errorText)
      alert(`CSV export failed: ${response.status} ${response.statusText}`)
    }
  } catch (error) {
    console.error('Excel export failed:', error)
    alert('CSV export failed. Please check your connection and try again.')
  } finally {
    exportingExcel.value = false
  }
}

const printReport = () => {
  const printContent = document.querySelector('.trial-balance')
  const printWindow = window.open('', '_blank')
  
  printWindow.document.write(`
    <html>
      <head>
        <title>Trial Balance Report</title>
        <style>
          body { font-family: Arial, sans-serif; margin: 20px; }
          .page-header { border-bottom: 2px solid #000; padding-bottom: 10px; margin-bottom: 20px; }
          .report-header { text-align: center; margin-bottom: 20px; }
          table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
          th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
          th { background-color: #f5f5f5; font-weight: bold; }
          .text-right { text-align: right; }
          .totals-row { border-top: 2px solid #000; font-weight: bold; }
          @media print { .header-actions { display: none; } }
        </style>
      </head>
      <body>
        <div class="report-header">
          <h1>Paksa Financial System</h1>
          <h2>Trial Balance</h2>
          <p>As of ${formatDate(asOfDate.value)}</p>
        </div>
        <table>
          <thead>
            <tr>
              <th>Account Code</th>
              <th>Account Name</th>
              <th class="text-right">Debit</th>
              <th class="text-right">Credit</th>
            </tr>
          </thead>
          <tbody>
            ${trialBalanceData.value.map(item => `
              <tr>
                <td>${item.accountCode}</td>
                <td>${item.accountName}</td>
                <td class="text-right">${item.debit > 0 ? formatCurrency(item.debit) : '-'}</td>
                <td class="text-right">${item.credit > 0 ? formatCurrency(item.credit) : '-'}</td>
              </tr>
            `).join('')}
            <tr class="totals-row">
              <td colspan="2"><strong>TOTALS</strong></td>
              <td class="text-right"><strong>${formatCurrency(totalDebits.value)}</strong></td>
              <td class="text-right"><strong>${formatCurrency(totalCredits.value)}</strong></td>
            </tr>
          </tbody>
        </table>
        <p><strong>${isBalanced.value ? 'Trial Balance is Balanced' : 'Trial Balance is NOT Balanced'}</strong></p>
      </body>
    </html>
  `)
  
  printWindow.document.close()
  printWindow.print()
}

onMounted(() => {
  generateReport()
})
</script>

<style scoped>
.trial-balance {
  padding: 0;
}

.page-header {
  background: white;
  border-bottom: 1px solid #e5e7eb;
  padding: 1.5rem 2rem;
  margin-bottom: 2rem;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-left h1 {
  margin: 0;
  font-size: 1.75rem;
  font-weight: 600;
  color: #1f2937;
}

.subtitle {
  margin: 0.25rem 0 0 0;
  color: #6b7280;
  font-size: 0.875rem;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

.content-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem 2rem;
}

.report-header {
  border-bottom: 2px solid #e5e7eb;
  padding-bottom: 1rem;
}

.account-type-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.trial-balance-totals {
  background: #f9fafb;
  padding: 1rem;
  border-radius: 0.5rem;
  margin-top: 1rem;
}

.totals-row {
  display: grid;
  grid-template-columns: 1fr 150px 150px;
  gap: 1rem;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid #e5e7eb;
  margin-bottom: 0.75rem;
}

.totals-label {
  font-size: 1.1rem;
}

.totals-debit,
.totals-credit {
  text-align: right;
  font-size: 1.1rem;
}

.balance-check {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
}

.balance-check.balanced {
  color: #059669;
}

.balance-check.unbalanced {
  color: #dc2626;
}

.difference {
  font-weight: normal;
  font-size: 0.875rem;
}

:deep(.trial-balance-table .p-datatable-tbody > tr:last-child) {
  border-bottom: 2px solid #374151;
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .header-actions {
    width: 100%;
    justify-content: flex-end;
    flex-wrap: wrap;
  }
  
  .content-container {
    padding: 0 1rem 2rem;
  }
  
  .totals-row {
    grid-template-columns: 1fr;
    text-align: center;
  }
}
</style>