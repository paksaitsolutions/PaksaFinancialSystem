<template>
  <div class="reconciliation">
    <div class="flex justify-content-between align-items-center mb-4">
      <h1>Bank Reconciliation</h1>
      <Button label="New Reconciliation" icon="pi pi-plus" @click="startNewReconciliation" />
    </div>

    <Card v-if="!activeReconciliation">
      <template #content>
        <div class="text-center p-4">
          <i class="pi pi-info-circle text-4xl text-blue-500 mb-3"></i>
          <h3>No Active Reconciliation</h3>
          <p class="text-color-secondary mb-4">Start a new reconciliation to begin matching transactions with your bank statement.</p>
          <Button label="Start Reconciliation" icon="pi pi-plus" @click="startNewReconciliation" />
        </div>
      </template>
    </Card>

    <div v-if="activeReconciliation" class="grid">
      <div class="col-12">
        <Card>
          <template #title>Active Reconciliation</template>
          <template #content>
            <div class="grid">
              <div class="col-4">
                <div class="text-500 font-medium mb-1">Account</div>
                <div class="text-900">{{ activeReconciliation.account_name }}</div>
              </div>
              <div class="col-4">
                <div class="text-500 font-medium mb-1">Statement Date</div>
                <div class="text-900">{{ formatDate(activeReconciliation.statement_date) }}</div>
              </div>
              <div class="col-4">
                <div class="text-500 font-medium mb-1">Ending Balance</div>
                <div class="text-900">{{ formatCurrency(activeReconciliation.closing_balance) }}</div>
              </div>
            </div>
          </template>
        </Card>
      </div>

      <div class="col-6">
        <Card>
          <template #title>Unreconciled Transactions</template>
          <template #content>
            <DataTable :value="unreconciledTransactions" :loading="loading">
              <Column field="transaction_date" header="Date">
                <template #body="{ data }">
                  {{ formatDate(data.transaction_date) }}
                </template>
              </Column>
              <Column field="description" header="Description" />
              <Column field="amount" header="Amount">
                <template #body="{ data }">
                  <span :class="data.amount >= 0 ? 'text-green-500' : 'text-red-500'">
                    {{ formatCurrency(data.amount) }}
                  </span>
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </div>

      <div class="col-6">
        <Card>
          <template #title>Statement Items</template>
          <template #content>
            <DataTable :value="statementItems" :loading="loadingStatement">
              <Column field="date" header="Date">
                <template #body="{ data }">
                  {{ formatDate(data.date) }}
                </template>
              </Column>
              <Column field="description" header="Description" />
              <Column field="amount" header="Amount">
                <template #body="{ data }">
                  <span :class="data.amount >= 0 ? 'text-green-500' : 'text-red-500'">
                    {{ formatCurrency(data.amount) }}
                  </span>
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </div>
    </div>

    <Dialog v-model:visible="showNewReconciliationDialog" header="New Reconciliation" :modal="true" :style="{width: '500px'}">
      <div class="field">
        <label>Bank Account</label>
        <Dropdown v-model="newReconciliation.account_id" :options="bankAccounts" optionLabel="name" optionValue="id" placeholder="Select account" class="w-full" />
      </div>
      <div class="field">
        <label>Statement Date</label>
        <Calendar v-model="newReconciliation.statement_date" class="w-full" />
      </div>
      <div class="field">
        <label>Closing Balance</label>
        <InputNumber v-model="newReconciliation.closing_balance" mode="currency" currency="USD" class="w-full" />
      </div>
      <template #footer>
        <Button label="Cancel" class="p-button-text" @click="showNewReconciliationDialog = false" />
        <Button label="Start" @click="createReconciliation" :loading="loading" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'

const toast = useToast()

const loading = ref(false)
const loadingStatement = ref(false)
const activeReconciliation = ref(null)
const unreconciledTransactions = ref([])
const statementItems = ref([])
const showNewReconciliationDialog = ref(false)
const bankAccounts = ref([
  { id: '1', name: 'Main Checking Account' },
  { id: '2', name: 'Savings Account' }
])

const newReconciliation = ref({
  account_id: null,
  statement_date: new Date(),
  closing_balance: null
})

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}

const startNewReconciliation = () => {
  newReconciliation.value = {
    account_id: null,
    statement_date: new Date(),
    closing_balance: null
  }
  showNewReconciliationDialog.value = true
}

const createReconciliation = async () => {
  if (!newReconciliation.value.account_id || !newReconciliation.value.closing_balance) {
    toast.add({ severity: 'warn', summary: 'Warning', detail: 'Please fill all required fields', life: 3000 })
    return
  }

  loading.value = true
  try {
    const account = bankAccounts.value.find(acc => acc.id === newReconciliation.value.account_id)
    
    activeReconciliation.value = {
      id: '1',
      account_id: newReconciliation.value.account_id,
      account_name: account?.name || 'Unknown Account',
      statement_date: newReconciliation.value.statement_date.toISOString().split('T')[0],
      closing_balance: newReconciliation.value.closing_balance,
      status: 'in_progress'
    }

    unreconciledTransactions.value = [
      {
        id: '1',
        transaction_date: '2024-01-15',
        description: 'Office supplies payment',
        amount: -250.00
      },
      {
        id: '2',
        transaction_date: '2024-01-16',
        description: 'Customer payment',
        amount: 1500.00
      }
    ]

    statementItems.value = [
      {
        id: 'stmt1',
        date: '2024-01-15',
        description: 'Deposit',
        amount: 1000.00
      },
      {
        id: 'stmt2',
        date: '2024-01-16',
        description: 'Check payment',
        amount: -1200.00
      }
    ]

    showNewReconciliationDialog.value = false
    toast.add({ severity: 'success', summary: 'Success', detail: 'Reconciliation started successfully', life: 3000 })
  } catch (error) {
    console.error('Error creating reconciliation:', error)
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to start reconciliation', life: 5000 })
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  // Component mounted
})
</script>

<style scoped>
.field {
  margin-bottom: 1rem;
}
</style>