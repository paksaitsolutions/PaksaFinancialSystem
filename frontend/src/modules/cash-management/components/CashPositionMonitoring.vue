<template>
  <div class="cash-position-monitoring">
    <div class="grid">
      <div class="col-12 md:col-4">
        <Card>
          <template #title>Current Cash Position</template>
          <template #content>
            <div class="text-4xl font-bold text-primary mb-2">
              {{ formatCurrency(totalCashPosition) }}
            </div>
            <div class="text-sm text-500">
              Across {{ bankAccounts.length }} accounts
            </div>
          </template>
        </Card>
      </div>
      
      <div class="col-12 md:col-4">
        <Card>
          <template #title>Available Balance</template>
          <template #content>
            <div class="text-4xl font-bold text-green-500 mb-2">
              {{ formatCurrency(availableBalance) }}
            </div>
            <div class="text-sm text-500">
              Ready for use
            </div>
          </template>
        </Card>
      </div>
      
      <div class="col-12 md:col-4">
        <Card>
          <template #title>Pending Transactions</template>
          <template #content>
            <div class="text-4xl font-bold text-orange-500 mb-2">
              {{ pendingTransactions }}
            </div>
            <div class="text-sm text-500">
              Awaiting clearance
            </div>
          </template>
        </Card>
      </div>
    </div>
    
    <Card class="mt-4">
      <template #title>Account Breakdown</template>
      <template #content>
        <DataTable :value="bankAccounts" responsiveLayout="scroll">
          <Column field="name" header="Account Name" :sortable="true" />
          <Column field="bank" header="Bank" :sortable="true" />
          <Column field="balance" header="Balance" :sortable="true">
            <template #body="{ data }">
              <span class="font-bold" :class="data.balance >= 0 ? 'text-green-500' : 'text-red-500'">
                {{ formatCurrency(data.balance) }}
              </span>
            </template>
          </Column>
          <Column field="available" header="Available" :sortable="true">
            <template #body="{ data }">
              {{ formatCurrency(data.available) }}
            </template>
          </Column>
          <Column field="status" header="Status" :sortable="true">
            <template #body="{ data }">
              <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const bankAccounts = ref([
  {
    id: 1,
    name: 'Main Business Account',
    bank: 'HBL',
    balance: 150000,
    available: 145000,
    status: 'Active'
  },
  {
    id: 2,
    name: 'Savings Account',
    bank: 'Meezan Bank',
    balance: 50000,
    available: 50000,
    status: 'Active'
  },
  {
    id: 3,
    name: 'USD Account',
    bank: 'HBL',
    balance: 5000,
    available: 4800,
    status: 'Active'
  }
])

const totalCashPosition = computed(() => {
  return bankAccounts.value.reduce((sum, account) => sum + account.balance, 0)
})

const availableBalance = computed(() => {
  return bankAccounts.value.reduce((sum, account) => sum + account.available, 0)
})

const pendingTransactions = computed(() => {
  return bankAccounts.value.reduce((sum, account) => sum + (account.balance - account.available), 0)
})

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(value)
}

const getStatusSeverity = (status: string) => {
  switch (status) {
    case 'Active': return 'success'
    case 'Inactive': return 'danger'
    case 'Pending': return 'warning'
    default: return 'info'
  }
}
</script>

<style scoped>
/* Component styles */
</style>