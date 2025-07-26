<template>
  <AppLayout title="Trial Balance">
    <v-container>
      <v-card>
        <v-card-title>Trial Balance</v-card-title>
        <v-card-text>
          <v-data-table
            :headers="headers"
            :items="trialBalance"
            class="elevation-1"
          >
            <template v-slot:item.debit="{ item }">
              {{ item.debit ? formatCurrency(item.debit) : '-' }}
            </template>
            <template v-slot:item.credit="{ item }">
              {{ item.credit ? formatCurrency(item.credit) : '-' }}
            </template>
          </v-data-table>
          
          <v-row class="mt-4">
            <v-col cols="6">
              <v-card color="blue-lighten-5">
                <v-card-text>
                  <div class="text-h6">Total Debits: {{ formatCurrency(totalDebits) }}</div>
                </v-card-text>
              </v-card>
            </v-col>
            <v-col cols="6">
              <v-card color="green-lighten-5">
                <v-card-text>
                  <div class="text-h6">Total Credits: {{ formatCurrency(totalCredits) }}</div>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
    </v-container>
  </AppLayout>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import AppLayout from '@/layouts/AppLayout.vue'

const headers = [
  { title: 'Account', key: 'account' },
  { title: 'Debit', key: 'debit' },
  { title: 'Credit', key: 'credit' }
]

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