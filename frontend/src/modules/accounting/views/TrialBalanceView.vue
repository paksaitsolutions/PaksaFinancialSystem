<template>
  <div class="trial-balance p-4">
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1>Trial Balance</h1>
        <Breadcrumb :home="home" :model="breadcrumbItems" />
      </div>
    </div>
    <Card>
      <template #content>
        <DataTable :value="trialBalance" class="p-datatable-sm">
          <Column field="account" header="Account" />
          <Column field="debit" header="Debit">
            <template #body="{ data }">
              {{ data.debit ? formatCurrency(data.debit) : '-' }}
            </template>
          </Column>
          <Column field="credit" header="Credit">
            <template #body="{ data }">
              {{ data.credit ? formatCurrency(data.credit) : '-' }}
            </template>
          </Column>
        </DataTable>
        
        <div class="grid mt-4">
          <div class="col-6">
            <Card class="bg-blue-50">
              <template #content>
                <div class="text-xl font-semibold">Total Debits: {{ formatCurrency(totalDebits) }}</div>
              </template>
            </Card>
          </div>
          <div class="col-6">
            <Card class="bg-green-50">
              <template #content>
                <div class="text-xl font-semibold">Total Credits: {{ formatCurrency(totalCredits) }}</div>
              </template>
            </Card>
          </div>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

const home = ref({ icon: 'pi pi-home', to: '/' })
const breadcrumbItems = ref([
  { label: 'Accounting', to: '/accounting' },
  { label: 'Trial Balance' }
])

const trialBalance = [
  { account: 'Cash', debit: 50000, credit: 0 },
  { account: 'Accounts Receivable', debit: 25000, credit: 0 },
  { account: 'Accounts Payable', debit: 0, credit: 15000 },
  { account: 'Owner Equity', debit: 0, credit: 60000 }
]

const totalDebits = computed(() => trialBalance.reduce((sum, item) => sum + item.debit, 0))
const totalCredits = computed(() => trialBalance.reduce((sum, item) => sum + item.credit, 0))

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount)
}
</script>