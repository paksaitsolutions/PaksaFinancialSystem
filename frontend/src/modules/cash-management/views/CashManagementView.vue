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
import { ref } from 'vue'
import { useToast } from 'primevue/usetoast'

const toast = useToast()

const stats = ref({
  totalCash: '245,680',
  bankAccounts: 4,
  monthlyInflow: '156,890',
  monthlyOutflow: '89,240'
})

const recentTransactions = ref([
  { date: '2024-01-15', description: 'Customer Payment', account: 'Main Checking', type: 'inflow', amount: 5500 },
  { date: '2024-01-14', description: 'Office Rent', account: 'Main Checking', type: 'outflow', amount: 2500 },
  { date: '2024-01-13', description: 'Equipment Purchase', account: 'Business Savings', type: 'outflow', amount: 8500 },
  { date: '2024-01-12', description: 'Service Revenue', account: 'Main Checking', type: 'inflow', amount: 3200 },
  { date: '2024-01-11', description: 'Utility Payment', account: 'Main Checking', type: 'outflow', amount: 450 }
])

const bankAccounts = ref([
  { id: 1, name: 'Main Checking', number: '****1234', balance: 125680 },
  { id: 2, name: 'Business Savings', number: '****5678', balance: 85000 },
  { id: 3, name: 'Payroll Account', number: '****9012', balance: 25000 },
  { id: 4, name: 'Tax Reserve', number: '****3456', balance: 10000 }
])

const transactionDialog = ref(false)
const submitted = ref(false)

const transaction = ref({
  description: '',
  account: '',
  type: 'inflow',
  amount: 0,
  date: new Date()
})

const accountOptions = ref([
  { name: 'Main Checking' },
  { name: 'Business Savings' },
  { name: 'Payroll Account' },
  { name: 'Tax Reserve' }
])

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

const saveTransaction = () => {
  submitted.value = true
  if (transaction.value.description && transaction.value.account && transaction.value.amount > 0) {
    recentTransactions.value.unshift({
      date: transaction.value.date.toISOString().split('T')[0],
      description: transaction.value.description,
      account: transaction.value.account,
      type: transaction.value.type,
      amount: transaction.value.type === 'inflow' ? transaction.value.amount : -transaction.value.amount
    })
    transactionDialog.value = false
    toast.add({ severity: 'success', summary: 'Success', detail: 'Transaction recorded', life: 3000 })
  }
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}
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