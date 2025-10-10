<template>
  <div class="cash-management">
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1>Cash Management</h1>
        <p class="text-color-secondary">Monitor cash flow and bank account balances</p>
      </div>
      <Button label="Add Transaction" icon="pi pi-plus" @click="openNew" />
    </div>

    <div class="grid">
      <div class="col-12 lg:col-3">
        <Card>
          <template #content>
            <div class="metric-card">
              <i class="pi pi-wallet text-4xl text-green-500 mb-3"></i>
              <div class="text-2xl font-bold">${{ stats.totalCash }}</div>
              <div class="text-color-secondary">Total Cash</div>
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 lg:col-3">
        <Card>
          <template #content>
            <div class="metric-card">
              <i class="pi pi-bank text-4xl text-blue-500 mb-3"></i>
              <div class="text-2xl font-bold">{{ stats.bankAccounts }}</div>
              <div class="text-color-secondary">Bank Accounts</div>
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 lg:col-3">
        <Card>
          <template #content>
            <div class="metric-card">
              <i class="pi pi-arrow-up text-4xl text-purple-500 mb-3"></i>
              <div class="text-2xl font-bold">${{ stats.monthlyInflow }}</div>
              <div class="text-color-secondary">Monthly Inflow</div>
            </div>
          </template>
        </Card>
      </div>
      <div class="col-12 lg:col-3">
        <Card>
          <template #content>
            <div class="metric-card">
              <i class="pi pi-arrow-down text-4xl text-orange-500 mb-3"></i>
              <div class="text-2xl font-bold">${{ stats.monthlyOutflow }}</div>
              <div class="text-color-secondary">Monthly Outflow</div>
            </div>
          </template>
        </Card>
      </div>
    </div>

    <div class="grid">
      <div class="col-12 lg:col-8">
        <Card>
          <template #title>Recent Transactions</template>
          <template #content>
            <DataTable :value="recentTransactions" :rows="10">
              <Column field="date" header="Date" />
              <Column field="description" header="Description" />
              <Column field="account" header="Account" />
              <Column field="type" header="Type">
                <template #body="{ data }">
                  <Tag :value="data.type" :severity="data.type === 'inflow' ? 'success' : 'danger'" />
                </template>
              </Column>
              <Column field="amount" header="Amount">
                <template #body="{ data }">
                  <span :class="data.type === 'inflow' ? 'text-green-600' : 'text-red-600'">
                    {{ formatCurrency(data.amount) }}
                  </span>
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </div>
      <div class="col-12 lg:col-4">
        <Card>
          <template #title>Bank Accounts</template>
          <template #content>
            <div class="bank-accounts">
              <div v-for="account in bankAccounts" :key="account.id" class="bank-account-item">
                <div class="account-info">
                  <div class="account-name">{{ account.name }}</div>
                  <div class="account-number">{{ account.number }}</div>
                </div>
                <div class="account-balance">{{ formatCurrency(account.balance) }}</div>
              </div>
            </div>
          </template>
        </Card>
      </div>
    </div>

    <Dialog v-model:visible="transactionDialog" header="Cash Transaction" :modal="true" :style="{width: '500px'}">
      <div class="field">
        <label>Description</label>
        <InputText v-model="transaction.description" class="w-full" :class="{'p-invalid': submitted && !transaction.description}" />
        <small class="p-error" v-if="submitted && !transaction.description">Description is required.</small>
      </div>
      <div class="field">
        <label>Account</label>
        <Dropdown v-model="transaction.account" :options="accountOptions" optionLabel="name" optionValue="name" placeholder="Select Account" class="w-full" />
      </div>
      <div class="field">
        <label>Type</label>
        <Dropdown v-model="transaction.type" :options="typeOptions" optionLabel="label" optionValue="value" placeholder="Select Type" class="w-full" />
      </div>
      <div class="field">
        <label>Amount</label>
        <InputNumber v-model="transaction.amount" mode="currency" currency="USD" class="w-full" :min="0" />
      </div>
      <div class="field">
        <label>Date</label>
        <Calendar v-model="transaction.date" class="w-full" />
      </div>
      <template #footer>
        <Button label="Cancel" class="p-button-text" @click="hideDialog" />
        <Button label="Save" @click="saveTransaction" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useToast } from 'primevue/usetoast'
import { cashService } from '@/api/cashService'

const toast = useToast()
const loading = ref(false)
const dashboardData = ref(null)
const recentTransactionsData = ref([])
const bankAccountsData = ref([])

const stats = computed(() => {
  if (!dashboardData.value) {
    return {
      totalCash: '0',
      bankAccounts: 0,
      monthlyInflow: '0',
      monthlyOutflow: '0'
    }
  }
  return {
    totalCash: formatCurrency(dashboardData.value.total_balance).replace('$', ''),
    bankAccounts: dashboardData.value.account_count,
    monthlyInflow: '0',
    monthlyOutflow: '0'
  }
})

const recentTransactions = computed(() => {
  return recentTransactionsData.value.map(transaction => ({
    date: formatDate(transaction.transaction_date),
    description: transaction.memo || 'Transaction',
    account: transaction.account?.name || 'Unknown Account',
    type: ['deposit', 'transfer_in'].includes(transaction.transaction_type) ? 'inflow' : 'outflow',
    amount: parseFloat(transaction.amount)
  }))
})

const bankAccounts = computed(() => {
  return bankAccountsData.value.map(account => ({
    id: account.id,
    name: account.name,
    number: account.account_number,
    balance: parseFloat(account.current_balance)
  }))
})

const transactionDialog = ref(false)
const submitted = ref(false)

const transaction = ref({
  description: '',
  account: '',
  type: 'inflow',
  amount: 0,
  date: new Date()
})

const accountOptions = ref([])

const typeOptions = ref([
  { label: 'Inflow', value: 'inflow' },
  { label: 'Outflow', value: 'outflow' }
])

const openNew = () => {
  transaction.value = {
    description: '',
    account: '',
    type: 'inflow',
    amount: 0,
    date: new Date()
  }
  submitted.value = false
  transactionDialog.value = true
}

const hideDialog = () => {
  transactionDialog.value = false
  submitted.value = false
}

const loadDashboardData = async () => {
  loading.value = true
  try {
    const [dashboard, accounts, transactions] = await Promise.all([
      cashService.getDashboard(),
      cashService.getBankAccounts(),
      cashService.getTransactions({ limit: 10 })
    ])
    
    dashboardData.value = dashboard
    bankAccountsData.value = accounts
    recentTransactionsData.value = transactions
    accountOptions.value = accounts.map(acc => ({ name: acc.name, id: acc.id }))
  } catch (error) {
    console.error('Error loading dashboard data:', error)
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load data', life: 5000 })
  } finally {
    loading.value = false
  }
}

const saveTransaction = async () => {
  submitted.value = true
  if (transaction.value.description && transaction.value.account && transaction.value.amount > 0) {
    try {
      const account = bankAccountsData.value.find(acc => acc.name === transaction.value.account)
      if (!account) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'Account not found', life: 3000 })
        return
      }
      
      await cashService.createTransaction({
        account_id: account.id,
        transaction_date: transaction.value.date.toISOString(),
        transaction_type: transaction.value.type === 'inflow' ? 'deposit' : 'withdrawal',
        amount: transaction.value.amount,
        memo: transaction.value.description
      })
      
      transactionDialog.value = false
      toast.add({ severity: 'success', summary: 'Success', detail: 'Transaction recorded', life: 3000 })
      await loadDashboardData()
    } catch (error) {
      console.error('Error saving transaction:', error)
      toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to save transaction', life: 5000 })
    }
  }
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

onMounted(() => {
  loadDashboardData()
})
</script>

<style scoped>
.cash-management {
  padding: 0;
}

.metric-card {
  text-align: center;
}

.bank-accounts {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.bank-account-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border: 1px solid var(--surface-border);
  border-radius: 8px;
  background: var(--surface-50);
}

.account-info {
  flex: 1;
}

.account-name {
  font-weight: 600;
  color: var(--text-color);
}

.account-number {
  font-size: 0.875rem;
  color: var(--text-color-secondary);
}

.account-balance {
  font-weight: 600;
  color: var(--primary-color);
}
</style>