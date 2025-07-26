<template>
  <v-card>
    <v-card-title class="d-flex align-center">
      <v-icon class="mr-2">mdi-format-list-bulleted-square</v-icon>
      Bulk Operations
      <v-spacer />
      <v-chip v-if="selectedItems.length > 0" color="primary" size="small">
        {{ selectedItems.length }} Selected
      </v-chip>
    </v-card-title>

    <v-card-text>
      <!-- Bulk Actions -->
      <v-row class="mb-4">
        <v-col cols="12">
          <v-btn-group>
            <v-btn
              color="success"
              @click="bulkPost"
              :disabled="selectedItems.length === 0"
              :loading="posting"
            >
              <v-icon start>mdi-check</v-icon>
              Bulk Post
            </v-btn>
            <v-btn
              color="warning"
              @click="bulkUnpost"
              :disabled="selectedItems.length === 0"
              :loading="unposting"
            >
              <v-icon start>mdi-undo</v-icon>
              Bulk Unpost
            </v-btn>
            <v-btn
              color="error"
              @click="bulkDelete"
              :disabled="selectedItems.length === 0"
              :loading="deleting"
            >
              <v-icon start>mdi-delete</v-icon>
              Bulk Delete
            </v-btn>
            <v-btn
              color="info"
              @click="bulkExport"
              :disabled="selectedItems.length === 0"
              :loading="exporting"
            >
              <v-icon start>mdi-download</v-icon>
              Bulk Export
            </v-btn>
          </v-btn-group>
        </v-col>
      </v-row>

      <!-- Items Table -->
      <v-data-table
        v-model="selectedItems"
        :items="items"
        :headers="headers"
        show-select
        class="elevation-1"
        :loading="loading"
      >
        <template #item.entry_date="{ item }">
          {{ formatDate(item.entry_date) }}
        </template>
        <template #item.amount="{ item }">
          {{ formatCurrency(item.total_debit) }}
        </template>
        <template #item.status="{ item }">
          <v-chip :color="getStatusColor(item.status)" size="small">
            {{ item.status }}
          </v-chip>
        </template>
      </v-data-table>

      <!-- Progress Dialog -->
      <v-dialog v-model="showProgress" persistent max-width="400px">
        <v-card>
          <v-card-title>{{ progressTitle }}</v-card-title>
          <v-card-text>
            <v-progress-linear
              :model-value="progressValue"
              height="20"
              color="primary"
            >
              <template #default="{ value }">
                <strong>{{ Math.ceil(value) }}%</strong>
              </template>
            </v-progress-linear>
            <div class="mt-2 text-center">
              {{ progressText }}
            </div>
          </v-card-text>
        </v-card>
      </v-dialog>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const loading = ref(false)
const posting = ref(false)
const unposting = ref(false)
const deleting = ref(false)
const exporting = ref(false)
const showProgress = ref(false)
const progressValue = ref(0)
const progressTitle = ref('')
const progressText = ref('')

const selectedItems = ref([])
const items = ref([
  {
    id: '1',
    entry_number: 'JE-2024-001',
    entry_date: '2024-01-15',
    description: 'Monthly accrual',
    total_debit: 5000,
    status: 'draft'
  },
  {
    id: '2',
    entry_number: 'JE-2024-002',
    entry_date: '2024-01-16',
    description: 'Depreciation',
    total_debit: 2500,
    status: 'posted'
  }
])

const headers = [
  { title: 'Entry #', key: 'entry_number' },
  { title: 'Date', key: 'entry_date' },
  { title: 'Description', key: 'description' },
  { title: 'Amount', key: 'amount', align: 'end' },
  { title: 'Status', key: 'status' }
]

const formatDate = (date) => new Date(date).toLocaleDateString()
const formatCurrency = (amount) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount)

const getStatusColor = (status) => {
  switch (status) {
    case 'draft': return 'warning'
    case 'posted': return 'success'
    case 'reversed': return 'error'
    default: return 'grey'
  }
}

const performBulkOperation = async (operation, title) => {
  showProgress.value = true
  progressTitle.value = title
  progressValue.value = 0
  
  for (let i = 0; i < selectedItems.value.length; i++) {
    progressValue.value = ((i + 1) / selectedItems.value.length) * 100
    progressText.value = `Processing ${i + 1} of ${selectedItems.value.length}`
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 500))
  }
  
  showProgress.value = false
  selectedItems.value = []
}

const bulkPost = async () => {
  posting.value = true
  await performBulkOperation('post', 'Posting Journal Entries')
  posting.value = false
}

const bulkUnpost = async () => {
  unposting.value = true
  await performBulkOperation('unpost', 'Unposting Journal Entries')
  unposting.value = false
}

const bulkDelete = async () => {
  if (confirm(`Delete ${selectedItems.value.length} selected items?`)) {
    deleting.value = true
    await performBulkOperation('delete', 'Deleting Journal Entries')
    deleting.value = false
  }
}

const bulkExport = async () => {
  exporting.value = true
  await performBulkOperation('export', 'Exporting Journal Entries')
  exporting.value = false
}

onMounted(() => {
  // Load items
})
</script>