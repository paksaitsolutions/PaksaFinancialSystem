<template>
  <div class="cash-transactions">
    <div class="flex justify-content-between align-items-center mb-4">
      <h1>Cash Transactions</h1>
      <Button label="New Transaction" icon="pi pi-plus" @click="openTransactionDialog" />
    </div>

    <Card>
      <template #content>
        <div class="flex justify-content-between align-items-center mb-3">
          <div class="flex gap-2">
            <Dropdown v-model="selectedAccount" :options="bankAccounts" optionLabel="name" optionValue="id" placeholder="All Accounts" @change="loadTransactions" />
            <Calendar v-model="dateRange" selectionMode="range" placeholder="Date Range" @date-select="loadTransactions" />
          </div>
          <Button icon="pi pi-refresh" class="p-button-text" @click="loadTransactions" :loading="loading" />
        </div>
        
        <DataTable :value="transactions" :loading="loading" responsiveLayout="scroll" :paginator="true" :rows="20">
          <Column field="transaction_date" header="Date" :sortable="true">
            <template #body="{ data }">
              {{ formatDate(data.transaction_date) }}
            </template>
          </Column>
          <Column field="payee" header="Payee" :sortable="true" />
          <Column field="memo" header="Description" :sortable="true" />
          <Column field="transaction_type" header="Type" :sortable="true">
            <template #body="{ data }">
              <Tag :value="formatTransactionType(data.transaction_type)" :severity="getTypeSeverity(data.transaction_type)" />
            </template>
          </Column>
          <Column field="amount" header="Amount" :sortable="true">
            <template #body="{ data }">
              <span :class="data.transaction_type === 'deposit' ? 'text-green-500' : 'text-red-500'" class="font-bold">
                {{ data.transaction_type === 'deposit' ? '+' : '-' }}{{ formatCurrency(data.amount) }}
              </span>
            </template>
          </Column>
          <Column field="status" header="Status" :sortable="true">
            <template #body="{ data }">
              <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
            </template>
          </Column>
          <Column>
            <template #body="{ data }">
              <Button icon="pi pi-pencil" class="p-button-text p-button-sm" @click="editTransaction(data)" />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <Dialog v-model:visible="transactionDialog" header="New Transaction" :modal="true" :style="{width: '600px'}">
      <div class="grid">
        <div class="col-12">
          <div class="field">
            <label>Bank Account</label>
            <Dropdown v-model="transaction.account_id" :options="bankAccounts" optionLabel="name" optionValue="id" placeholder="Select Account" class="w-full" />
          </div>
        </div>
        <div class="col-6">
          <div class="field">
            <label>Date</label>
            <Calendar v-model="transaction.transaction_date" class="w-full" />
          </div>
        </div>
        <div class="col-6">
          <div class="field">
            <label>Type</label>
            <Dropdown v-model="transaction.transaction_type" :options="transactionTypes" optionLabel="label" optionValue="value" class="w-full" />
          </div>
        </div>
        <div class="col-6">
          <div class="field">
            <label>Amount</label>
            <InputNumber v-model="transaction.amount" mode="currency" currency="USD" class="w-full" />
          </div>
        </div>
        <div class="col-6">
          <div class="field">
            <label>Payment Method</label>
            <InputText v-model="transaction.payment_method" class="w-full" />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label>Payee</label>
            <InputText v-model="transaction.payee" class="w-full" />
          </div>
        </div>
        <div class="col-12">
          <div class="field">
            <label>Memo</label>
            <Textarea v-model="transaction.memo" rows="3" class="w-full" />
          </div>
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" class="p-button-text" @click="transactionDialog = false" />
        <Button label="Save" @click="saveTransaction" :loading="saving" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { cashService, type Transaction, type BankAccount } from '@/api/cashService'

const toast = useToast()
const loading = ref(false)
const saving = ref(false)
const transactions = ref<Transaction[]>([])
const bankAccounts = ref<BankAccount[]>([])
const selectedAccount = ref(null)
const dateRange = ref(null)
const transactionDialog = ref(false)

const transaction = ref({
  account_id: '',
  transaction_date: new Date(),
  transaction_type: 'deposit',
  amount: 0,
  memo: '',
  payee: '',
  payment_method: ''
})

const transactionTypes = [
  { label: 'Deposit', value: 'deposit' },
  { label: 'Withdrawal', value: 'withdrawal' },
  { label: 'Transfer In', value: 'transfer_in' },
  { label: 'Transfer Out', value: 'transfer_out' },
  { label: 'Payment', value: 'payment' },
  { label: 'Fee', value: 'fee' }
]

const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}

const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const formatTransactionType = (type: string): string => {
  return type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const getTypeSeverity = (type: string) => {
  switch (type) {
    case 'deposit': return 'success'
    case 'withdrawal': return 'danger'
    case 'transfer_in': return 'info'
    case 'transfer_out': return 'warning'
    default: return 'secondary'
  }
}

const getStatusSeverity = (status: string) => {
  switch (status) {
    case 'posted': return 'success'
    case 'pending': return 'warning'
    case 'cleared': return 'info'
    case 'void': return 'danger'
    default: return 'secondary'
  }
}

const loadTransactions = async () => {
  loading.value = true
  try {
    const params: any = { limit: 100 }
    if (selectedAccount.value) params.account_id = selectedAccount.value
    if (dateRange.value && dateRange.value[0]) {
      params.start_date = dateRange.value[0].toISOString().split('T')[0]
      if (dateRange.value[1]) {
        params.end_date = dateRange.value[1].toISOString().split('T')[0]
      }
    }
    
    const response = await cashService.getTransactions(params)
    transactions.value = response.items || []
  } catch (error) {
    console.error('Error loading transactions:', error)
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load transactions', life: 5000 })
  } finally {
    loading.value = false
  }
}

const loadBankAccounts = async () => {
  try {
    const response = await cashService.getBankAccounts()
    bankAccounts.value = response.items || []
  } catch (error) {
    console.error('Error loading bank accounts:', error)
  }
}

const openTransactionDialog = () => {
  transaction.value = {
    account_id: '',
    transaction_date: new Date(),
    transaction_type: 'deposit',
    amount: 0,
    memo: '',
    payee: '',
    payment_method: ''
  }
  transactionDialog.value = true
}

const saveTransaction = async () => {
  saving.value = true
  try {
    await cashService.createTransaction({
      ...transaction.value,
      transaction_date: transaction.value.transaction_date.toISOString().split('T')[0]
    })
    transactionDialog.value = false
    toast.add({ severity: 'success', summary: 'Success', detail: 'Transaction created successfully', life: 3000 })
    await loadTransactions()
  } catch (error) {
    console.error('Error saving transaction:', error)
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to save transaction', life: 5000 })
  } finally {
    saving.value = false
  }
}

const editTransaction = (trans: Transaction) => {
  console.log('Editing transaction:', trans)
  toast.add({ severity: 'info', summary: 'Info', detail: 'Edit functionality coming soon', life: 3000 })
}

onMounted(() => {
  loadBankAccounts()
  loadTransactions()
})
</script>

<style scoped>
.cash-transactions {
  padding: 0;
}

.field {
  margin-bottom: 1rem;
}
</style>