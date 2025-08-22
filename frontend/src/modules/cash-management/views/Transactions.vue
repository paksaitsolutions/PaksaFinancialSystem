<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title>Cash Transactions</v-card-title>
          <v-card-text>
            <v-data-table
              :headers="headers"
              :items="transactions"
              :loading="loading"
              class="elevation-1"
            >
              <template v-slot:item.amount="{ item }">
                {{ formatCurrency(item.amount) }}
              </template>
              <template v-slot:item.actions="{ item }">
                <v-btn icon size="small" @click="editTransaction(item)">
                  <v-icon>mdi-pencil</v-icon>
                </v-btn>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';

interface Transaction {
  id: string;
  date: string;
  description: string;
  amount: number;
  type: string;
}

const loading = ref(false);
const transactions = ref<Transaction[]>([]);

const headers = [
  { title: 'Date', key: 'date' },
  { title: 'Description', key: 'description' },
  { title: 'Amount', key: 'amount' },
  { title: 'Type', key: 'type' },
  { title: 'Actions', key: 'actions', sortable: false }
];

const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount);
};

const editTransaction = (transaction: Transaction) => {
  console.log('Editing transaction:', transaction);
};

onMounted(() => {
  // Load transactions
});
</script>