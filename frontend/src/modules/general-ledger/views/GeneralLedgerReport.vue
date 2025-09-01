<template>
  <div class="general-ledger-report">
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <Button icon="pi pi-arrow-left" class="p-button-text" @click="$router.go(-1)" />
          <div>
            <h1>General Ledger Report</h1>
            <p class="subtitle">Detailed account transactions and running balances</p>
          </div>
        </div>
        <div class="header-actions">
          <Button label="Export PDF" icon="pi pi-file-pdf" class="p-button-outlined" />
          <Button label="Export Excel" icon="pi pi-file-excel" class="p-button-outlined" />
        </div>
      </div>
    </div>

    <div class="content-container">
      <Card>
        <template #title>
          <div class="flex justify-content-between align-items-center flex-wrap gap-3">
            <span>General Ledger Report</span>
            <div class="flex gap-2 flex-wrap">
              <Dropdown v-model="selectedAccount" :options="accounts" optionLabel="name" optionValue="id" placeholder="Select Account" showClear />
              <Calendar v-model="dateFrom" dateFormat="mm/dd/yy" showIcon placeholder="From Date" />
              <Calendar v-model="dateTo" dateFormat="mm/dd/yy" showIcon placeholder="To Date" />
              <Button label="Generate" icon="pi pi-refresh" @click="generateReport" :loading="loading" />
            </div>
          </div>
        </template>
        
        <template #content>
          <div v-if="selectedAccountData" class="account-header mb-4">
            <div class="grid">
              <div class="col-12 md:col-8">
                <h3 class="mb-2">{{ selectedAccountData.code }} - {{ selectedAccountData.name }}</h3>
                <p class="text-600 mb-0">Account Type: {{ selectedAccountData.type }}</p>
              </div>
              <div class="col-12 md:col-4 text-right">
                <div class="balance-info">
                  <div class="balance-label">Current Balance</div>
                  <div class="balance-amount" :class="selectedAccountData.balance >= 0 ? 'text-green-600' : 'text-red-600'">
                    {{ formatCurrency(selectedAccountData.balance) }}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <DataTable 
            :value="ledgerEntries" 
            :loading="loading"
            responsiveLayout="scroll"
            :paginator="true"
            :rows="20"
            class="ledger-table"
          >
            <Column field="date" header="Date" sortable style="width: 120px">
              <template #body="{ data }">
                <span class="font-medium">{{ formatDate(data.date) }}</span>
              </template>
            </Column>

            <Column field="reference" header="Reference" style="width: 120px">
              <template #body="{ data }">
                <span class="font-mono text-primary cursor-pointer" @click="viewJournalEntry(data.reference)">
                  {{ data.reference }}
                </span>
              </template>
            </Column>

            <Column field="description" header="Description">
              <template #body="{ data }">
                <div>
                  <div class="font-medium">{{ data.description }}</div>
                  <div v-if="data.memo" class="text-sm text-600">{{ data.memo }}</div>
                </div>
              </template>
            </Column>

            <Column field="debit" header="Debit" class="text-right" style="width: 120px">
              <template #body="{ data }">
                <span v-if="data.debit > 0" class="font-medium">
                  {{ formatCurrency(data.debit) }}
                </span>
                <span v-else class="text-400">-</span>
              </template>
            </Column>

            <Column field="credit" header="Credit" class="text-right" style="width: 120px">
              <template #body="{ data }">
                <span v-if="data.credit > 0" class="font-medium">
                  {{ formatCurrency(data.credit) }}
                </span>
                <span v-else class="text-400">-</span>
              </template>
            </Column>

            <Column field="balance" header="Running Balance" class="text-right" style="width: 140px">
              <template #body="{ data }">
                <span :class="data.balance >= 0 ? 'text-green-600' : 'text-red-600'" class="font-bold">
                  {{ formatCurrency(data.balance) }}
                </span>
              </template>
            </Column>

            <template #footer>
              <div class="ledger-summary">
                <div class="summary-row">
                  <div class="summary-label">
                    <strong>Period Totals ({{ formatDate(dateFrom) }} - {{ formatDate(dateTo) }})</strong>
                  </div>
                  <div class="summary-debit">
                    <strong>{{ formatCurrency(periodTotalDebits) }}</strong>
                  </div>
                  <div class="summary-credit">
                    <strong>{{ formatCurrency(periodTotalCredits) }}</strong>
                  </div>
                  <div class="summary-balance">
                    <strong>{{ formatCurrency(endingBalance) }}</strong>
                  </div>
                </div>
              </div>
            </template>
          </DataTable>

          <!-- Account Activity Summary -->
          <div v-if="ledgerEntries.length > 0" class="mt-4">
            <h4 class="mb-3">Period Summary</h4>
            <div class="grid">
              <div class="col-12 md:col-6">
                <div class="summary-card">
                  <div class="summary-item">
                    <span class="label">Beginning Balance:</span>
                    <span class="value">{{ formatCurrency(beginningBalance) }}</span>
                  </div>
                  <div class="summary-item">
                    <span class="label">Total Debits:</span>
                    <span class="value text-blue-600">{{ formatCurrency(periodTotalDebits) }}</span>
                  </div>
                  <div class="summary-item">
                    <span class="label">Total Credits:</span>
                    <span class="value text-red-600">{{ formatCurrency(periodTotalCredits) }}</span>
                  </div>
                  <div class="summary-item total">
                    <span class="label">Ending Balance:</span>
                    <span class="value" :class="endingBalance >= 0 ? 'text-green-600' : 'text-red-600'">
                      {{ formatCurrency(endingBalance) }}
                    </span>
                  </div>
                </div>
              </div>
              <div class="col-12 md:col-6">
                <div class="summary-card">
                  <div class="summary-item">
                    <span class="label">Number of Transactions:</span>
                    <span class="value">{{ ledgerEntries.length }}</span>
                  </div>
                  <div class="summary-item">
                    <span class="label">Average Transaction:</span>
                    <span class="value">{{ formatCurrency(averageTransaction) }}</span>
                  </div>
                  <div class="summary-item">
                    <span class="label">Net Change:</span>
                    <span class="value" :class="netChange >= 0 ? 'text-green-600' : 'text-red-600'">
                      {{ formatCurrency(netChange) }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const loading = ref(false)
const selectedAccount = ref(null)
const dateFrom = ref(new Date(new Date().getFullYear(), new Date().getMonth(), 1))
const dateTo = ref(new Date())

const accounts = ref([
  { id: 1, code: '1000', name: 'Cash', type: 'Asset', balance: 50000 },
  { id: 2, code: '1100', name: 'Accounts Receivable', type: 'Asset', balance: 25000 },
  { id: 3, code: '1200', name: 'Inventory', type: 'Asset', balance: 75000 },
  { id: 4, code: '2000', name: 'Accounts Payable', type: 'Liability', balance: 15000 },
  { id: 5, code: '4000', name: 'Sales Revenue', type: 'Revenue', balance: 45000 },
  { id: 6, code: '5000', name: 'Cost of Goods Sold', type: 'Expense', balance: 20000 }
])

const ledgerEntries = ref([])

const selectedAccountData = computed(() => {
  return accounts.value.find(acc => acc.id === selectedAccount.value)
})

const periodTotalDebits = computed(() => {
  return ledgerEntries.value.reduce((sum, entry) => sum + entry.debit, 0)
})

const periodTotalCredits = computed(() => {
  return ledgerEntries.value.reduce((sum, entry) => sum + entry.credit, 0)
})

const beginningBalance = computed(() => {
  if (ledgerEntries.value.length === 0) return 0
  const firstEntry = ledgerEntries.value[0]
  return firstEntry.balance - firstEntry.debit + firstEntry.credit
})

const endingBalance = computed(() => {
  if (ledgerEntries.value.length === 0) return 0
  return ledgerEntries.value[ledgerEntries.value.length - 1].balance
})

const netChange = computed(() => {
  return endingBalance.value - beginningBalance.value
})

const averageTransaction = computed(() => {
  if (ledgerEntries.value.length === 0) return 0
  const totalAmount = ledgerEntries.value.reduce((sum, entry) => sum + Math.abs(entry.debit - entry.credit), 0)
  return totalAmount / ledgerEntries.value.length
})

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value)
}

const formatDate = (date: Date) => {
  return new Intl.DateTimeFormat('en-US').format(date)
}

const generateMockEntries = (accountId: number) => {
  const entries = [
    { date: new Date('2024-01-15'), reference: 'JE-001', description: 'Opening Balance', memo: '', debit: 45000, credit: 0, balance: 45000 },
    { date: new Date('2024-01-20'), reference: 'JE-002', description: 'Client Payment', memo: 'Invoice #1001', debit: 2500, credit: 0, balance: 47500 },
    { date: new Date('2024-01-25'), reference: 'JE-003', description: 'Bank Transfer', memo: 'Transfer to savings', debit: 0, credit: 5000, balance: 42500 },
    { date: new Date('2024-02-01'), reference: 'JE-004', description: 'Service Revenue', memo: 'February services', debit: 3000, credit: 0, balance: 45500 },
    { date: new Date('2024-02-10'), reference: 'JE-005', description: 'Equipment Purchase', memo: 'New computer', debit: 0, credit: 1200, balance: 44300 },
    { date: new Date('2024-02-15'), reference: 'JE-006', description: 'Client Payment', memo: 'Invoice #1002', debit: 4500, credit: 0, balance: 48800 },
    { date: new Date('2024-02-20'), reference: 'JE-007', description: 'Office Rent', memo: 'February rent', debit: 0, credit: 1500, balance: 47300 }
  ]
  
  return entries.filter(entry => 
    entry.date >= dateFrom.value && entry.date <= dateTo.value
  )
}

const generateReport = async () => {
  if (!selectedAccount.value) return
  
  loading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 800))
    ledgerEntries.value = generateMockEntries(selectedAccount.value)
  } finally {
    loading.value = false
  }
}

const viewJournalEntry = (reference: string) => {
  router.push('/accounting/journal-entry')
}

watch([selectedAccount, dateFrom, dateTo], () => {
  if (selectedAccount.value) {
    generateReport()
  }
})

onMounted(() => {
  // Auto-select first account for demo
  selectedAccount.value = accounts.value[0].id
})
</script>

<style scoped>
.general-ledger-report {
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

.account-header {
  background: #f9fafb;
  padding: 1.5rem;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
}

.balance-info {
  text-align: right;
}

.balance-label {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 0.25rem;
}

.balance-amount {
  font-size: 1.5rem;
  font-weight: 700;
}

.ledger-summary {
  background: #f9fafb;
  padding: 1rem;
  border-radius: 0.5rem;
  margin-top: 1rem;
}

.summary-row {
  display: grid;
  grid-template-columns: 1fr 120px 120px 140px;
  gap: 1rem;
  align-items: center;
}

.summary-label {
  font-size: 1rem;
}

.summary-debit,
.summary-credit,
.summary-balance {
  text-align: right;
  font-size: 1rem;
}

.summary-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1.5rem;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid #f3f4f6;
}

.summary-item:last-child {
  border-bottom: none;
}

.summary-item.total {
  border-top: 2px solid #e5e7eb;
  margin-top: 0.5rem;
  padding-top: 1rem;
  font-weight: 600;
}

.summary-item .label {
  color: #6b7280;
  font-size: 0.875rem;
}

.summary-item .value {
  font-weight: 500;
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
  }
  
  .content-container {
    padding: 0 1rem 2rem;
  }
  
  .summary-row {
    grid-template-columns: 1fr;
    text-align: center;
    gap: 0.5rem;
  }
}
</style>