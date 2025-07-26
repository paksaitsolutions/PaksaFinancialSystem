<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-4">Cash Management</h1>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12" md="4">
        <v-card>
          <v-card-title>Cash Balance</v-card-title>
          <v-card-text>
            <div class="text-h3 text-primary">{{ formatCurrency(cashBalance) }}</div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-card>
          <v-card-title>Pending Receipts</v-card-title>
          <v-card-text>
            <div class="text-h3 text-success">{{ formatCurrency(pendingReceipts) }}</div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-card>
          <v-card-title>Pending Payments</v-card-title>
          <v-card-text>
            <div class="text-h3 text-error">{{ formatCurrency(pendingPayments) }}</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-row class="mt-4">
      <v-col cols="12">
        <v-card>
          <v-card-title>Recent Transactions</v-card-title>
          <v-card-text>
            <v-data-table
              :items="transactions"
              :headers="headers"
              class="elevation-1"
            >
              <template #item.amount="{ item }">
                <span :class="item.type === 'receipt' ? 'text-success' : 'text-error'">
                  {{ formatCurrency(item.amount) }}
                </span>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref } from 'vue'

const cashBalance = ref(125000)
const pendingReceipts = ref(25000)
const pendingPayments = ref(15000)

const headers = [
  { title: 'Date', key: 'date' },
  { title: 'Description', key: 'description' },
  { title: 'Type', key: 'type' },
  { title: 'Amount', key: 'amount' }
]

const transactions = ref([
  { date: '2024-01-15', description: 'Customer Payment', type: 'receipt', amount: 5000 },
  { date: '2024-01-14', description: 'Vendor Payment', type: 'payment', amount: 3000 }
])

const formatCurrency = (amount) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount)
</script>