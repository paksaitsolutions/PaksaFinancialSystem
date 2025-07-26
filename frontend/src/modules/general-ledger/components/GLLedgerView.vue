<template>
  <v-container fluid>
    <v-card>
      <v-card-title class="d-flex align-center">
        <v-icon class="mr-2">mdi-book-open-page-variant</v-icon>
        General Ledger
        <v-spacer />
        <v-btn color="primary" @click="exportLedger" :loading="exporting">
          <v-icon start>mdi-download</v-icon>
          Export
        </v-btn>
      </v-card-title>

      <v-card-text>
        <v-row class="mb-4">
          <v-col cols="12" md="3">
            <v-select
              v-model="selectedAccount"
              :items="accounts"
              item-title="name"
              item-value="id"
              label="Select Account"
              clearable
              @update:model-value="loadLedgerEntries"
            />
          </v-col>
          <v-col cols="12" md="3">
            <v-text-field
              v-model="dateFrom"
              type="date"
              label="From Date"
              @change="loadLedgerEntries"
            />
          </v-col>
          <v-col cols="12" md="3">
            <v-text-field
              v-model="dateTo"
              type="date"
              label="To Date"
              @change="loadLedgerEntries"
            />
          </v-col>
          <v-col cols="12" md="3">
            <v-btn color="primary" @click="loadLedgerEntries" :loading="loading" block>
              <v-icon start>mdi-refresh</v-icon>
              Refresh
            </v-btn>
          </v-col>
        </v-row>

        <v-data-table
          :items="ledgerEntries"
          :headers="headers"
          :loading="loading"
          class="elevation-1"
          items-per-page="25"
        >
          <template #item.entry_date="{ item }">
            {{ formatDate(item.entry_date) }}
          </template>
          <template #item.debit="{ item }">
            {{ item.debit ? formatCurrency(item.debit) : '' }}
          </template>
          <template #item.credit="{ item }">
            {{ item.credit ? formatCurrency(item.credit) : '' }}
          </template>
          <template #item.balance="{ item }">
            {{ formatCurrency(item.balance) }}
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const loading = ref(false)
const exporting = ref(false)
const selectedAccount = ref(null)
const dateFrom = ref('')
const dateTo = ref('')
const accounts = ref([])
const ledgerEntries = ref([])

const headers = [
  { title: 'Date', key: 'entry_date' },
  { title: 'Reference', key: 'reference' },
  { title: 'Description', key: 'description' },
  { title: 'Debit', key: 'debit', align: 'end' },
  { title: 'Credit', key: 'credit', align: 'end' },
  { title: 'Balance', key: 'balance', align: 'end' }
]

const formatDate = (date) => new Date(date).toLocaleDateString()
const formatCurrency = (amount) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount)

const loadLedgerEntries = async () => {
  if (!selectedAccount.value) return
  loading.value = true
  // Mock data - replace with API call
  ledgerEntries.value = [
    { id: 1, entry_date: '2024-01-01', reference: 'JE-001', description: 'Opening Balance', debit: 1000, credit: 0, balance: 1000 },
    { id: 2, entry_date: '2024-01-15', reference: 'JE-002', description: 'Payment received', debit: 500, credit: 0, balance: 1500 }
  ]
  loading.value = false
}

const exportLedger = () => {
  exporting.value = true
  setTimeout(() => { exporting.value = false }, 1000)
}

onMounted(() => {
  accounts.value = [
    { id: '1', name: '1000 - Cash' },
    { id: '2', name: '1100 - Accounts Receivable' }
  ]
})
</script>