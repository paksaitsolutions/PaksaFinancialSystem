<template>
  <div class="banking-fee-tracking">
    <Card>
      <template #title>Banking Fee Tracking</template>
      <template #content>
        <div class="grid">
          <div class="col-12 md:col-3">
            <Card class="h-full">
              <template #title>This Month</template>
              <template #content>
                <div class="text-3xl font-bold text-red-500 mb-2">
                  {{ formatCurrency(monthlyFees) }}
                </div>
                <div class="text-sm text-500">
                  Total fees paid
                </div>
              </template>
            </Card>
          </div>
          
          <div class="col-12 md:col-3">
            <Card class="h-full">
              <template #title>This Year</template>
              <template #content>
                <div class="text-3xl font-bold text-orange-500 mb-2">
                  {{ formatCurrency(yearlyFees) }}
                </div>
                <div class="text-sm text-500">
                  YTD fees
                </div>
              </template>
            </Card>
          </div>
          
          <div class="col-12 md:col-3">
            <Card class="h-full">
              <template #title>Average Monthly</template>
              <template #content>
                <div class="text-3xl font-bold text-blue-500 mb-2">
                  {{ formatCurrency(averageMonthlyFees) }}
                </div>
                <div class="text-sm text-500">
                  12-month average
                </div>
              </template>
            </Card>
          </div>
          
          <div class="col-12 md:col-3">
            <Card class="h-full">
              <template #title>Fee Categories</template>
              <template #content>
                <div class="text-3xl font-bold text-purple-500 mb-2">
                  {{ feeCategories.length }}
                </div>
                <div class="text-sm text-500">
                  Active categories
                </div>
              </template>
            </Card>
          </div>
        </div>
        
        <div class="mt-4">
          <h3>Recent Banking Fees</h3>
          <DataTable :value="recentFees" responsiveLayout="scroll">
            <Column field="date" header="Date" :sortable="true">
              <template #body="{ data }">
                {{ formatDate(data.date) }}
              </template>
            </Column>
            <Column field="description" header="Description" :sortable="true" />
            <Column field="category" header="Category" :sortable="true">
              <template #body="{ data }">
                <Tag :value="data.category" />
              </template>
            </Column>
            <Column field="amount" header="Amount" :sortable="true">
              <template #body="{ data }">
                <span class="text-red-500 font-bold">
                  {{ formatCurrency(data.amount) }}
                </span>
              </template>
            </Column>
            <Column field="account" header="Account" :sortable="true" />
          </DataTable>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const monthlyFees = ref(245.50)
const yearlyFees = ref(2890.75)
const averageMonthlyFees = ref(241.00)

const feeCategories = ref([
  'Transaction Fees',
  'Monthly Maintenance',
  'Wire Transfer',
  'Overdraft',
  'International'
])

const recentFees = ref([
  {
    date: new Date('2024-01-15'),
    description: 'Monthly Account Maintenance',
    category: 'Monthly Maintenance',
    amount: 25.00,
    account: 'Main Business Account'
  },
  {
    date: new Date('2024-01-12'),
    description: 'Wire Transfer Fee',
    category: 'Wire Transfer',
    amount: 15.00,
    account: 'Main Business Account'
  },
  {
    date: new Date('2024-01-10'),
    description: 'Transaction Fee',
    category: 'Transaction Fees',
    amount: 2.50,
    account: 'Savings Account'
  }
])

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(value)
}

const formatDate = (date: Date) => {
  return date.toLocaleDateString()
}
</script>

<style scoped>
/* Component styles */
</style>