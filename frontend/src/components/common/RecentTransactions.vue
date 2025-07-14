<template>
  <div class="recent-transactions">
    <v-list>
      <v-list-item
        v-for="transaction in transactions"
        :key="transaction.id"
        class="transaction-item"
      >
        <template #prepend>
          <v-avatar
            :color="transaction.amount >= 0 ? 'success' : 'error'"
            size="40"
          >
            <v-icon color="white">
              {{ transaction.amount >= 0 ? 'mdi-plus' : 'mdi-minus' }}
            </v-icon>
          </v-avatar>
        </template>

        <v-list-item-title>{{ transaction.description }}</v-list-item-title>
        <v-list-item-subtitle>
          {{ transaction.account }} • {{ formatDate(transaction.date) }}
        </v-list-item-subtitle>

        <template #append>
          <div class="transaction-amount">
            <span
              :class="transaction.amount >= 0 ? 'text-success' : 'text-error'"
              class="font-weight-bold"
            >
              {{ formatCurrency(transaction.amount) }}
            </span>
          </div>
        </template>
      </v-list-item>
    </v-list>

    <div v-if="transactions.length === 0" class="text-center py-4">
      <v-icon size="48" color="grey-lighten-2">mdi-receipt</v-icon>
      <p class="text-grey-600 mt-2">No recent transactions</p>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Transaction {
  id: number
  date: string
  description: string
  amount: number
  account: string
}

interface Props {
  transactions: Transaction[]
}

defineProps<Props>()

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(Math.abs(amount))
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric'
  })
}
</script>

<style scoped>
.recent-transactions {
  max-height: 400px;
  overflow-y: auto;
}

.transaction-item {
  border-bottom: 1px solid #f0f0f0;
}

.transaction-item:last-child {
  border-bottom: none;
}

.transaction-amount {
  text-align: right;
}
</style>