<template>
  <div class="cash-management">
    <!-- Header -->
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="text-2xl font-semibold text-900 m-0">Cash Management</h2>
        <p class="text-600 mt-1 mb-0">Monitor cash flow, bank accounts, and financial positions</p>
      </div>
      <div class="flex gap-2">
        <Button label="Bank Reconciliation" icon="pi pi-check-circle" severity="secondary" outlined />
        <Button label="New Transaction" icon="pi pi-plus" @click="showTransactionDialog = true" />
      </div>
    </div>

    <!-- Cash Overview Cards -->
    <div class="flex flex-wrap gap-3 mb-4">
      <div class="cash-card flex-1 min-w-15rem p-4 border-round bg-blue-50 border-1 border-blue-200">
        <div class="flex align-items-center gap-3">
          <div class="w-3rem h-3rem border-circle bg-blue-500 flex align-items-center justify-content-center">
            <i class="pi pi-wallet text-white text-xl"></i>
          </div>
          <div>
            <div class="text-2xl font-bold text-900">{{ formatCurrency(cashBalance) }}</div>
            <div class="text-600 text-sm">Total Cash Balance</div>
          </div>
        </div>
      </div>
      <div class="cash-card flex-1 min-w-15rem p-4 border-round bg-green-50 border-1 border-green-200">
        <div class="flex align-items-center gap-3">
          <div class="w-3rem h-3rem border-circle bg-green-500 flex align-items-center justify-content-center">
            <i class="pi pi-arrow-down text-white text-xl"></i>
          </div>
          <div>
            <div class="text-2xl font-bold text-900">{{ formatCurrency(pendingReceipts) }}</div>
            <div class="text-600 text-sm">Pending Receipts</div>
          </div>
        </div>
      </div>
      <div class="cash-card flex-1 min-w-15rem p-4 border-round bg-orange-50 border-1 border-orange-200">
        <div class="flex align-items-center gap-3">
          <div class="w-3rem h-3rem border-circle bg-orange-500 flex align-items-center justify-content-center">
            <i class="pi pi-arrow-up text-white text-xl"></i>
          </div>
          <div>
            <div class="text-2xl font-bold text-900">{{ formatCurrency(pendingPayments) }}</div>
            <div class="text-600 text-sm">Pending Payments</div>
          </div>
        </div>
      </div>
      <div class="cash-card flex-1 min-w-15rem p-4 border-round bg-purple-50 border-1 border-purple-200">
        <div class="flex align-items-center gap-3">
          <div class="w-3rem h-3rem border-circle bg-purple-500 flex align-items-center justify-content-center">
            <i class="pi pi-chart-line text-white text-xl"></i>
          </div>
          <div>
            <div class="text-2xl font-bold text-900">{{ formatCurrency(netCashFlow) }}</div>
            <div class="text-600 text-sm">Net Cash Flow</div>
          </div>
        </div>
      </div>
    </div>

    <div class="grid">
      <!-- Bank Accounts -->
      <div class="col-12 lg:col-8">
        <Card class="mb-4">
          <template #title>
            <div class="flex justify-content-between align-items-center">
              <span>Bank Accounts</span>
              <Button label="Add Account" icon="pi pi-plus" size="small" @click="showAccountDialog = true" />
            </div>
          </template>
          <template #content>
            <DataTable :value="bankAccounts" responsiveLayout="scroll">
              <Column field="name" header="Account Name">
                <template #body="{ data }">
                  <div class="flex align-items-center gap-2">
                    <i class="pi pi-building text-primary"></i>
                    <div>
                      <div class="font-semibold">{{ data.name }}</div>
                      <div class="text-sm text-600">{{ data.accountNumber }}</div>
                    </div>
                  </div>
                </template>
              </Column>
              <Column field="type" header="Type">
                <template #body="{ data }">
                  <Tag :value="data.type" :severity="getAccountTypeSeverity(data.type)" />
                </template>
              </Column>
              <Column field="balance" header="Balance">
                <template #body="{ data }">
                  <span :class="data.balance >= 0 ? 'text-green-600' : 'text-red-600'" class="font-semibold">
                    {{ formatCurrency(data.balance) }}
                  </span>
                </template>
              </Column>
              <Column field="lastReconciled" header="Last Reconciled" />
              <Column header="Actions">
                <template #body="{ data }">
                  <div class="flex gap-1">
                    <Button icon="pi pi-eye" class="p-button-text p-button-sm" v-tooltip="'View Details'" />
                    <Button icon="pi pi-check-circle" class="p-button-text p-button-sm" v-tooltip="'Reconcile'" />
                    <Button icon="pi pi-pencil" class="p-button-text p-button-sm" v-tooltip="'Edit'" />
                  </div>
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </div>

      <!-- Cash Flow Chart -->
      <div class="col-12 lg:col-4">
        <Card class="mb-4">
          <template #title>Cash Flow Trend</template>
          <template #content>
            <div class="cash-flow-chart p-4 text-center">
              <div class="text-6xl text-primary mb-3">
                <i class="pi pi-chart-line"></i>
              </div>
              <div class="text-lg font-semibold mb-2">7-Day Trend</div>
              <div class="text-sm text-600">Cash flow visualization will be displayed here</div>
            </div>
          </template>
        </Card>
      </div>
    </div>

    <!-- Recent Transactions -->
    <Card>
      <template #title>
        <div class="flex justify-content-between align-items-center">
          <span>Recent Transactions</span>
          <div class="flex gap-2">
            <InputText v-model="searchTerm" placeholder="Search transactions..." class="w-15rem" />
            <Button label="Export" icon="pi pi-download" severity="secondary" outlined />
          </div>
        </div>
      </template>
      <template #content>
        <DataTable 
          :value="filteredTransactions" 
          :paginator="true" 
          :rows="10" 
          responsiveLayout="scroll"
          :loading="loading"
        >
          <Column field="date" header="Date" sortable>
            <template #body="{ data }">
              {{ formatDate(data.date) }}
            </template>
          </Column>
          <Column field="reference" header="Reference" sortable />
          <Column field="description" header="Description" sortable />
          <Column field="account" header="Account" sortable>
            <template #body="{ data }">
              <div class="flex align-items-center gap-2">
                <i class="pi pi-building text-primary text-sm"></i>
                <span>{{ data.account }}</span>
              </div>
            </template>
          </Column>
          <Column field="type" header="Type" sortable>
            <template #body="{ data }">
              <Tag :value="data.type" :severity="getTransactionTypeSeverity(data.type)" />
            </template>
          </Column>
          <Column field="amount" header="Amount" sortable>
            <template #body="{ data }">
              <span :class="data.type === 'Receipt' ? 'text-green-600' : 'text-red-600'" class="font-semibold">
                {{ data.type === 'Receipt' ? '+' : '-' }}{{ formatCurrency(Math.abs(data.amount)) }}
              </span>
            </template>
          </Column>
          <Column field="status" header="Status" sortable>
            <template #body="{ data }">
              <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
            </template>
          </Column>
          <Column header="Actions">
            <template #body="{ data }">
              <div class="flex gap-1">
                <Button icon="pi pi-eye" class="p-button-text p-button-sm" v-tooltip="'View Details'" />
                <Button icon="pi pi-pencil" class="p-button-text p-button-sm" v-tooltip="'Edit'" />
                <Button icon="pi pi-trash" class="p-button-text p-button-sm p-button-danger" v-tooltip="'Delete'" />
              </div>
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <!-- New Transaction Dialog -->
    <Dialog v-model:visible="showTransactionDialog" header="New Transaction" :style="{ width: '600px' }" :modal="true">
      <div class="grid">
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="transactionType" class="font-semibold">Transaction Type *</label>
            <Dropdown 
              id="transactionType" 
              v-model="newTransaction.type" 
              :options="transactionTypes" 
              optionLabel="label" 
              optionValue="value"
              class="w-full" 
              placeholder="Select type"
            />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="transactionAccount" class="font-semibold">Bank Account *</label>
            <Dropdown 
              id="transactionAccount" 
              v-model="newTransaction.account" 
              :options="bankAccounts" 
              optionLabel="name" 
              optionValue="name"
              class="w-full" 
              placeholder="Select account"
            />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="transactionAmount" class="font-semibold">Amount *</label>
            <InputNumber 
              id="transactionAmount" 
              v-model="newTransaction.amount" 
              class="w-full" 
              mode="currency" 
              currency="USD" 
              placeholder="0.00"
            />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="transactionDate" class="font-semibold">Date *</label>
            <Calendar 
              id="transactionDate" 
              v-model="newTransaction.date" 
              class="w-full" 
              dateFormat="mm/dd/yy"
            />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label for="transactionDescription" class="font-semibold">Description</label>
            <Textarea 
              id="transactionDescription" 
              v-model="newTransaction.description" 
              class="w-full" 
              rows="3" 
              placeholder="Enter transaction description"
            />
          </div>
        </div>
      </div>
      
      <template #footer>
        <Button label="Cancel" @click="showTransactionDialog = false" class="p-button-text" />
        <Button label="Save Transaction" @click="saveTransaction" icon="pi pi-save" />
      </template>
    </Dialog>

    <!-- Add Bank Account Dialog -->
    <Dialog v-model:visible="showAccountDialog" header="Add Bank Account" :style="{ width: '500px' }" :modal="true">
      <div class="grid">
        <div class="col-12">
          <div class="field">
            <label for="accountName" class="font-semibold">Account Name *</label>
            <InputText 
              id="accountName" 
              v-model="newAccount.name" 
              class="w-full" 
              placeholder="Enter account name"
            />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="accountNumber" class="font-semibold">Account Number *</label>
            <InputText 
              id="accountNumber" 
              v-model="newAccount.accountNumber" 
              class="w-full" 
              placeholder="Enter account number"
            />
          </div>
        </div>
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="accountType" class="font-semibold">Account Type *</label>
            <Dropdown 
              id="accountType" 
              v-model="newAccount.type" 
              :options="accountTypes" 
              optionLabel="label" 
              optionValue="value"
              class="w-full" 
              placeholder="Select type"
            />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label for="initialBalance" class="font-semibold">Initial Balance</label>
            <InputNumber 
              id="initialBalance" 
              v-model="newAccount.balance" 
              class="w-full" 
              mode="currency" 
              currency="USD" 
              placeholder="0.00"
            />
          </div>
        </div>
      </div>
      
      <template #footer>
        <Button label="Cancel" @click="showAccountDialog = false" class="p-button-text" />
        <Button label="Add Account" @click="saveAccount" icon="pi pi-save" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useToast } from 'primevue/usetoast'

const toast = useToast()

const loading = ref(false)
const showTransactionDialog = ref(false)
const showAccountDialog = ref(false)
const searchTerm = ref('')

const cashBalance = ref(125000)
const pendingReceipts = ref(25000)
const pendingPayments = ref(15000)

const netCashFlow = computed(() => pendingReceipts.value - pendingPayments.value)

const bankAccounts = ref([
  { name: 'Main Checking', accountNumber: '****1234', type: 'Checking', balance: 85000, lastReconciled: '2024-01-15' },
  { name: 'Savings Account', accountNumber: '****5678', type: 'Savings', balance: 40000, lastReconciled: '2024-01-10' },
  { name: 'Petty Cash', accountNumber: '****9012', type: 'Cash', balance: 500, lastReconciled: '2024-01-12' }
])

const transactions = ref([
  { date: '2024-01-15', reference: 'TXN-001', description: 'Customer Payment - ABC Corp', account: 'Main Checking', type: 'Receipt', amount: 5000, status: 'Cleared' },
  { date: '2024-01-14', reference: 'TXN-002', description: 'Vendor Payment - XYZ Supplies', account: 'Main Checking', type: 'Payment', amount: 3000, status: 'Pending' },
  { date: '2024-01-13', reference: 'TXN-003', description: 'Office Rent Payment', account: 'Main Checking', type: 'Payment', amount: 2500, status: 'Cleared' },
  { date: '2024-01-12', reference: 'TXN-004', description: 'Sales Revenue', account: 'Main Checking', type: 'Receipt', amount: 7500, status: 'Cleared' }
])

const newTransaction = ref({
  type: '',
  account: '',
  amount: 0,
  date: new Date(),
  description: ''
})

const newAccount = ref({
  name: '',
  accountNumber: '',
  type: '',
  balance: 0
})

const transactionTypes = [
  { label: 'Receipt', value: 'Receipt' },
  { label: 'Payment', value: 'Payment' },
  { label: 'Transfer', value: 'Transfer' },
  { label: 'Adjustment', value: 'Adjustment' }
]

const accountTypes = [
  { label: 'Checking', value: 'Checking' },
  { label: 'Savings', value: 'Savings' },
  { label: 'Cash', value: 'Cash' },
  { label: 'Credit Card', value: 'Credit Card' }
]

const filteredTransactions = computed(() => {
  if (!searchTerm.value) return transactions.value
  return transactions.value.filter(t => 
    t.description.toLowerCase().includes(searchTerm.value.toLowerCase()) ||
    t.reference.toLowerCase().includes(searchTerm.value.toLowerCase())
  )
})

const getAccountTypeSeverity = (type: string) => {
  switch (type) {
    case 'Checking': return 'info'
    case 'Savings': return 'success'
    case 'Cash': return 'warning'
    case 'Credit Card': return 'danger'
    default: return 'secondary'
  }
}

const getTransactionTypeSeverity = (type: string) => {
  switch (type) {
    case 'Receipt': return 'success'
    case 'Payment': return 'danger'
    case 'Transfer': return 'info'
    case 'Adjustment': return 'warning'
    default: return 'secondary'
  }
}

const getStatusSeverity = (status: string) => {
  switch (status) {
    case 'Cleared': return 'success'
    case 'Pending': return 'warning'
    case 'Failed': return 'danger'
    default: return 'secondary'
  }
}

const saveTransaction = () => {
  if (!newTransaction.value.type || !newTransaction.value.account || !newTransaction.value.amount) {
    toast.add({ severity: 'warn', summary: 'Validation Error', detail: 'Please fill all required fields', life: 3000 })
    return
  }
  
  transactions.value.unshift({
    date: newTransaction.value.date.toISOString().split('T')[0],
    reference: `TXN-${String(transactions.value.length + 1).padStart(3, '0')}`,
    description: newTransaction.value.description,
    account: newTransaction.value.account,
    type: newTransaction.value.type,
    amount: newTransaction.value.amount,
    status: 'Pending'
  })
  
  toast.add({ severity: 'success', summary: 'Success', detail: 'Transaction saved successfully', life: 3000 })
  showTransactionDialog.value = false
  resetTransactionForm()
}

const saveAccount = () => {
  if (!newAccount.value.name || !newAccount.value.accountNumber || !newAccount.value.type) {
    toast.add({ severity: 'warn', summary: 'Validation Error', detail: 'Please fill all required fields', life: 3000 })
    return
  }
  
  bankAccounts.value.push({
    name: newAccount.value.name,
    accountNumber: `****${newAccount.value.accountNumber.slice(-4)}`,
    type: newAccount.value.type,
    balance: newAccount.value.balance,
    lastReconciled: new Date().toISOString().split('T')[0]
  })
  
  toast.add({ severity: 'success', summary: 'Success', detail: 'Bank account added successfully', life: 3000 })
  showAccountDialog.value = false
  resetAccountForm()
}

const resetTransactionForm = () => {
  newTransaction.value = {
    type: '',
    account: '',
    amount: 0,
    date: new Date(),
    description: ''
  }
}

const resetAccountForm = () => {
  newAccount.value = {
    name: '',
    accountNumber: '',
    type: '',
    balance: 0
  }
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount)
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString()
}
</script>

<style scoped>
.cash-management {
  max-width: 1400px;
  margin: 0 auto;
}

.cash-card {
  transition: all 0.2s ease;
}

.cash-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.cash-flow-chart {
  min-height: 200px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

@media (max-width: 768px) {
  .cash-management {
    padding: 0 1rem;
  }
  
  .flex.gap-2 {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>