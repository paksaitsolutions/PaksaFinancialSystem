<template>
  <AppLayout title="Chart of Accounts">
    <v-container>
      <v-card>
        <v-card-title class="d-flex align-center">
          Chart of Accounts
          <v-spacer></v-spacer>
          <v-btn color="primary">
            <v-icon class="mr-2">mdi-plus</v-icon>
            Add Account
          </v-btn>
        </v-card-title>
        <v-card-text>
          <v-data-table
            :headers="headers"
            :items="accounts"
            class="elevation-1"
          >
            <template v-slot:item.balance="{ item }">
              {{ formatCurrency(item.balance) }}
            </template>
            <template v-slot:item.actions="{ item }">
              <v-btn icon size="small">
                <v-icon>mdi-pencil</v-icon>
              </v-btn>
            </template>
          </v-data-table>
        </v-card-text>
      </v-card>
    </v-container>
  </AppLayout>
</template>

<script setup lang="ts">
import AppLayout from '@/layouts/AppLayout.vue'

const headers = [
  { title: 'Code', key: 'code' },
  { title: 'Name', key: 'name' },
  { title: 'Type', key: 'type' },
  { title: 'Balance', key: 'balance' },
  { title: 'Actions', key: 'actions', sortable: false }
]

const accounts = [
  { code: '1000', name: 'Cash', type: 'Asset', balance: 50000 },
  { code: '1100', name: 'Accounts Receivable', type: 'Asset', balance: 25000 },
  { code: '2000', name: 'Accounts Payable', type: 'Liability', balance: 15000 }
]

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount)
}
</script>