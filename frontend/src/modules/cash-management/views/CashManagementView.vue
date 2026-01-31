<template>
  <UnifiedDashboard 
    title="Cash Management" 
    subtitle="Monitor cash flow and bank account balances"
  >
    <template #actions>
      <Button label="Add Transaction" icon="pi pi-plus" class="btn-primary" @click="openNew" />
    </template>
    
    <template #metrics>
      <UnifiedMetrics :metrics="dashboardMetrics" />
    </template>
    
    <template #content>

      <div class="content-grid">
        <Card>
          <template #header>
            <h3 class="card-title">Recent Transactions</h3>
          </template>
          <template #content>
            <DataTable :value="recentTransactions" :rows="10" class="compact-table">
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
                  <span :class="data.type === 'inflow' ? 'text-success' : 'text-error'">
                    {{ formatCurrency(data.amount) }}
                  </span>
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
        <Card>
          <template #header>
            <h3 class="card-title">Bank Accounts</h3>
          </template>
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

    </template>
  </UnifiedDashboard>

  <Dialog v-model:visible="transactionDialog" header="Cash Transaction" :modal="true" :style="{width: '500px'}">
    <div class="form-group">
      <label class="form-label">Description</label>
      <InputText v-model="transaction.description" class="form-input" :class="{'p-invalid': submitted && !transaction.description}" />
      <small class="p-error" v-if="submitted && !transaction.description">Description is required.</small>
    </div>
    <div class="form-group">
      <label class="form-label">Account</label>
      <Dropdown v-model="transaction.account" :options="accountOptions" optionLabel="name" optionValue="name" placeholder="Select Account" class="form-input" />
    </div>
    <div class="form-group">
      <label class="form-label">Type</label>
      <Dropdown v-model="transaction.type" :options="typeOptions" optionLabel="label" optionValue="value" placeholder="Select Type" class="form-input" />
    </div>
    <div class="form-group">
      <label class="form-label">Amount</label>
      <InputNumber v-model="transaction.amount" mode="currency" currency="USD" class="form-input" :min="0" />
    </div>
    <div class="form-group">
      <label class="form-label">Date</label>
      <Calendar v-model="transaction.date" class="form-input" />
    </div>
    <template #footer>
      <Button label="Cancel" class="btn-secondary" @click="hideDialog" />
      <Button label="Save" class="btn-primary" @click="saveTransaction" />
    </template>
  </Dialog>
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

const dashboardMetrics = computed(() => [
  {
    id: 'cash',
    icon: 'pi pi-wallet',
    value: `$${stats.value.totalCash}`,
    label: 'Total Cash',
    color: 'var(--success-500)'
  },
  {
    id: 'accounts',
    icon: 'pi pi-bank',
    value: stats.value.bankAccounts,
    label: 'Bank Accounts',
    color: 'var(--primary-500)'
  },
  {
    id: 'inflow',
    icon: 'pi pi-arrow-up',
    value: `$${stats.value.monthlyInflow}`,
    label: 'Monthly Inflow',
    color: 'var(--info-500)'
  },
  {
    id: 'outflow',
    icon: 'pi pi-arrow-down',
    value: `$${stats.value.monthlyOutflow}`,
    label: 'Monthly Outflow',
    color: 'var(--warning-500)'
  }
])

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
.content-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: var(--spacing-lg);
}

.card-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--text-color);
  margin: 0;
}

.bank-accounts {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.bank-account-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-lg);
  border: 1px solid var(--surface-200);
  border-radius: var(--border-radius);
  background: var(--surface-50);
  transition: all var(--transition-fast);
}

.bank-account-item:hover {
  background: var(--surface-100);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.account-info {
  flex: 1;
}

.account-name {
  font-weight: var(--font-weight-semibold);
  color: var(--text-color);
  font-size: var(--font-size-base);
  margin-bottom: var(--spacing-xs);
}

.account-number {
  font-size: var(--font-size-sm);
  color: var(--text-color-secondary);
}

.account-balance {
  font-weight: var(--font-weight-bold);
  color: var(--primary-600);
  font-size: var(--font-size-lg);
}

:deep(.compact-table .p-datatable-tbody td) {
  padding: var(--spacing-sm) var(--spacing-md);
}

:deep(.compact-table .p-datatable-thead th) {
  padding: var(--spacing-sm) var(--spacing-md);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
}

@media (max-width: 768px) {
  .content-grid {
    grid-template-columns: 1fr;
    gap: var(--spacing-md);
  }
}
</style>