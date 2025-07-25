<template>
  <AppLayout title="Journal Entries">
    <v-card>
      <v-card-title class="d-flex align-center">
        <v-icon class="mr-2">mdi-book-edit</v-icon>
        Journal Entries
        <v-spacer></v-spacer>
        <v-btn color="primary" @click="openJournalDialog">
          <v-icon class="mr-2">mdi-plus</v-icon>
          New Entry
        </v-btn>
      </v-card-title>

      <v-card-text>
        <v-data-table
          :headers="headers"
          :items="journalEntries"
          :loading="loading"
          class="elevation-1"
        >
          <template v-slot:item.date="{ item }">
            {{ formatDate(item.date) }}
          </template>
          
          <template v-slot:item.total_amount="{ item }">
            {{ formatCurrency(item.total_amount) }}
          </template>
          
          <template v-slot:item.status="{ item }">
            <v-chip :color="getStatusColor(item.status)" size="small">
              {{ item.status }}
            </v-chip>
          </template>
          
          <template v-slot:item.actions="{ item }">
            <v-btn icon size="small" @click="viewEntry(item)" class="mr-2">
              <v-icon>mdi-eye</v-icon>
            </v-btn>
            <v-btn icon size="small" @click="editEntry(item)" class="mr-2" :disabled="item.status === 'Posted'">
              <v-icon>mdi-pencil</v-icon>
            </v-btn>
            <v-btn icon size="small" @click="postEntry(item)" color="success" :disabled="item.status === 'Posted'">
              <v-icon>mdi-check</v-icon>
            </v-btn>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>

    <!-- Journal Entry Dialog -->
    <v-dialog v-model="journalDialog" max-width="900px">
      <v-card>
        <v-card-title>{{ editingEntry ? 'Edit Journal Entry' : 'New Journal Entry' }}</v-card-title>
        <v-card-text>
          <v-form ref="form" v-model="valid">
            <v-row>
              <v-col cols="12" md="4">
                <v-text-field
                  v-model="editedEntry.reference"
                  label="Reference"
                  :rules="[rules.required]"
                  variant="outlined"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="4">
                <v-text-field
                  v-model="editedEntry.date"
                  label="Date"
                  type="date"
                  :rules="[rules.required]"
                  variant="outlined"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="4">
                <v-select
                  v-model="editedEntry.currency"
                  :items="currencies"
                  label="Currency"
                  variant="outlined"
                ></v-select>
              </v-col>
              <v-col cols="12">
                <v-textarea
                  v-model="editedEntry.description"
                  label="Description"
                  rows="2"
                  variant="outlined"
                ></v-textarea>
              </v-col>
            </v-row>

            <v-divider class="my-4"></v-divider>
            
            <div class="d-flex align-center mb-4">
              <h3>Journal Lines</h3>
              <v-spacer></v-spacer>
              <v-btn color="primary" size="small" @click="addLine">
                <v-icon class="mr-1">mdi-plus</v-icon>
                Add Line
              </v-btn>
            </div>

            <v-data-table
              :headers="lineHeaders"
              :items="editedEntry.lines"
              hide-default-footer
              class="elevation-1 mb-4"
            >
              <template v-slot:item.account="{ item, index }">
                <v-select
                  v-model="item.account_id"
                  :items="accounts"
                  item-title="account_name"
                  item-value="id"
                  variant="outlined"
                  density="compact"
                ></v-select>
              </template>
              
              <template v-slot:item.debit="{ item }">
                <v-text-field
                  v-model="item.debit"
                  type="number"
                  step="0.01"
                  variant="outlined"
                  density="compact"
                  @input="updateCredit(item)"
                ></v-text-field>
              </template>
              
              <template v-slot:item.credit="{ item }">
                <v-text-field
                  v-model="item.credit"
                  type="number"
                  step="0.01"
                  variant="outlined"
                  density="compact"
                  @input="updateDebit(item)"
                ></v-text-field>
              </template>
              
              <template v-slot:item.actions="{ item, index }">
                <v-btn icon size="small" @click="removeLine(index)" color="error">
                  <v-icon>mdi-delete</v-icon>
                </v-btn>
              </template>
            </v-data-table>

            <v-row>
              <v-col cols="12" md="6">
                <v-card color="blue-lighten-5" class="pa-3">
                  <div class="text-subtitle-1">Total Debits: {{ formatCurrency(totalDebits) }}</div>
                </v-card>
              </v-col>
              <v-col cols="12" md="6">
                <v-card color="green-lighten-5" class="pa-3">
                  <div class="text-subtitle-1">Total Credits: {{ formatCurrency(totalCredits) }}</div>
                </v-card>
              </v-col>
            </v-row>
            
            <v-alert v-if="!isBalanced" type="warning" class="mt-4">
              Journal entry is not balanced. Debits must equal credits.
            </v-alert>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="journalDialog = false">Cancel</v-btn>
          <v-btn color="primary" @click="saveEntry" :disabled="!valid || !isBalanced" :loading="saving">
            Save
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import AppLayout from '@/layouts/AppLayout.vue'

const loading = ref(false)
const saving = ref(false)
const journalDialog = ref(false)
const editingEntry = ref(false)
const valid = ref(false)

const currencies = ['USD', 'EUR', 'GBP', 'CAD']

const headers = [
  { title: 'Reference', key: 'reference', sortable: true },
  { title: 'Date', key: 'date', sortable: true },
  { title: 'Description', key: 'description', sortable: false },
  { title: 'Amount', key: 'total_amount', sortable: true },
  { title: 'Status', key: 'status', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false }
]

const lineHeaders = [
  { title: 'Account', key: 'account', sortable: false },
  { title: 'Debit', key: 'debit', sortable: false },
  { title: 'Credit', key: 'credit', sortable: false },
  { title: 'Actions', key: 'actions', sortable: false }
]

const journalEntries = ref([
  { id: 1, reference: 'JE-001', date: '2024-01-15', description: 'Opening balance', total_amount: 10000, status: 'Posted' },
  { id: 2, reference: 'JE-002', date: '2024-01-16', description: 'Sales transaction', total_amount: 5000, status: 'Draft' },
  { id: 3, reference: 'JE-003', date: '2024-01-17', description: 'Expense payment', total_amount: 2500, status: 'Posted' }
])

const accounts = ref([
  { id: 1, account_name: 'Cash', account_code: '1000' },
  { id: 2, account_name: 'Accounts Receivable', account_code: '1100' },
  { id: 3, account_name: 'Accounts Payable', account_code: '2000' },
  { id: 4, account_name: 'Sales Revenue', account_code: '4000' },
  { id: 5, account_name: 'Operating Expenses', account_code: '6000' }
])

const editedEntry = ref({
  reference: '',
  date: new Date().toISOString().substr(0, 10),
  description: '',
  currency: 'USD',
  lines: []
})

const rules = {
  required: (value: string) => !!value || 'Required'
}

const totalDebits = computed(() => {
  return editedEntry.value.lines.reduce((sum, line) => sum + (parseFloat(line.debit) || 0), 0)
})

const totalCredits = computed(() => {
  return editedEntry.value.lines.reduce((sum, line) => sum + (parseFloat(line.credit) || 0), 0)
})

const isBalanced = computed(() => {
  return Math.abs(totalDebits.value - totalCredits.value) < 0.01
})

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString()
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}

const getStatusColor = (status: string) => {
  return status === 'Posted' ? 'success' : 'warning'
}

const openJournalDialog = () => {
  editingEntry.value = false
  editedEntry.value = {
    reference: `JE-${String(journalEntries.value.length + 1).padStart(3, '0')}`,
    date: new Date().toISOString().substr(0, 10),
    description: '',
    currency: 'USD',
    lines: [{ account_id: null, debit: 0, credit: 0 }]
  }
  journalDialog.value = true
}

const addLine = () => {
  editedEntry.value.lines.push({ account_id: null, debit: 0, credit: 0 })
}

const removeLine = (index: number) => {
  editedEntry.value.lines.splice(index, 1)
}

const updateCredit = (item: any) => {
  if (parseFloat(item.debit) > 0) {
    item.credit = 0
  }
}

const updateDebit = (item: any) => {
  if (parseFloat(item.credit) > 0) {
    item.debit = 0
  }
}

const saveEntry = async () => {
  saving.value = true
  
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    const newEntry = {
      ...editedEntry.value,
      id: Date.now(),
      total_amount: totalDebits.value,
      status: 'Draft'
    }
    
    journalEntries.value.push(newEntry)
    journalDialog.value = false
  } catch (error) {
    console.error('Error saving entry:', error)
  } finally {
    saving.value = false
  }
}

const editEntry = (entry: any) => {
  editingEntry.value = true
  editedEntry.value = { ...entry }
  journalDialog.value = true
}

const viewEntry = (entry: any) => {
  console.log('View entry:', entry)
}

const postEntry = async (entry: any) => {
  entry.status = 'Posted'
}

onMounted(() => {
  // Load data
})
</script>