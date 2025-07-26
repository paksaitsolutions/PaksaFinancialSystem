<template>
  <v-container fluid>
    <v-card>
      <v-card-title class="d-flex align-center">
        <v-icon class="mr-2">mdi-check-circle</v-icon>
        Journal Entry Approvals
        <v-spacer />
        <v-chip :color="pendingCount > 0 ? 'warning' : 'success'" size="small">
          {{ pendingCount }} Pending
        </v-chip>
      </v-card-title>

      <v-card-text>
        <v-data-table
          :items="pendingApprovals"
          :headers="headers"
          :loading="loading"
          class="elevation-1"
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
          <template #item.actions="{ item }">
            <v-btn
              color="success"
              size="small"
              @click="approveEntry(item)"
              :loading="item.approving"
              class="mr-2"
            >
              Approve
            </v-btn>
            <v-btn
              color="error"
              size="small"
              @click="rejectEntry(item)"
              :loading="item.rejecting"
            >
              Reject
            </v-btn>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>

    <!-- Approval Dialog -->
    <v-dialog v-model="showApprovalDialog" max-width="600px">
      <v-card>
        <v-card-title>{{ approvalAction }} Journal Entry</v-card-title>
        <v-card-text>
          <v-textarea
            v-model="approvalComments"
            label="Comments"
            rows="3"
            placeholder="Enter approval comments..."
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="showApprovalDialog = false">Cancel</v-btn>
          <v-btn
            :color="approvalAction === 'Approve' ? 'success' : 'error'"
            @click="confirmApproval"
            :loading="processing"
          >
            {{ approvalAction }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const loading = ref(false)
const processing = ref(false)
const showApprovalDialog = ref(false)
const approvalAction = ref('')
const approvalComments = ref('')
const selectedEntry = ref(null)

const pendingApprovals = ref([
  {
    id: '1',
    entry_number: 'JE-2024-001',
    entry_date: '2024-01-15',
    description: 'Monthly accrual entries',
    total_debit: 15000,
    status: 'pending_approval',
    submitted_by: 'John Doe',
    approving: false,
    rejecting: false
  }
])

const headers = [
  { title: 'Entry #', key: 'entry_number' },
  { title: 'Date', key: 'entry_date' },
  { title: 'Description', key: 'description' },
  { title: 'Amount', key: 'amount', align: 'end' },
  { title: 'Status', key: 'status' },
  { title: 'Submitted By', key: 'submitted_by' },
  { title: 'Actions', key: 'actions', sortable: false }
]

const pendingCount = computed(() => pendingApprovals.value.length)

const formatDate = (date) => new Date(date).toLocaleDateString()
const formatCurrency = (amount) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount)

const getStatusColor = (status) => {
  switch (status) {
    case 'pending_approval': return 'warning'
    case 'approved': return 'success'
    case 'rejected': return 'error'
    default: return 'grey'
  }
}

const approveEntry = (entry) => {
  selectedEntry.value = entry
  approvalAction.value = 'Approve'
  showApprovalDialog.value = true
}

const rejectEntry = (entry) => {
  selectedEntry.value = entry
  approvalAction.value = 'Reject'
  showApprovalDialog.value = true
}

const confirmApproval = async () => {
  processing.value = true
  // Mock API call
  setTimeout(() => {
    const index = pendingApprovals.value.findIndex(e => e.id === selectedEntry.value.id)
    if (index !== -1) {
      pendingApprovals.value[index].status = approvalAction.value === 'Approve' ? 'approved' : 'rejected'
    }
    processing.value = false
    showApprovalDialog.value = false
    approvalComments.value = ''
  }, 1000)
}

onMounted(() => {
  // Load pending approvals
})
</script>