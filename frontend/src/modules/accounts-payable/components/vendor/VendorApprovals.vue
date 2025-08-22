<template>
  <v-card>
    <v-card-title>
      <v-icon left>mdi-check-circle</v-icon>
      Vendor Approvals
    </v-card-title>
    
    <v-card-text>
      <v-data-table
        :headers="headers"
        :items="pendingVendors"
        :loading="loading"
        class="elevation-1"
      >
        <template v-slot:item.status="{ item }">
          <v-chip :color="getStatusColor(item.status)" small>
            {{ item.status }}
          </v-chip>
        </template>
        
        <template v-slot:item.actions="{ item }">
          <v-btn
            icon
            small
            color="success"
            @click="approve(item)"
            :disabled="item.status !== 'pending_approval'"
          >
            <v-icon>mdi-check</v-icon>
          </v-btn>
          <v-btn
            icon
            small
            color="error"
            @click="reject(item)"
            :disabled="item.status !== 'pending_approval'"
          >
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </template>
      </v-data-table>
    </v-card-text>
    
    <!-- Approval Dialog -->
    <v-dialog v-model="showApprovalDialog" max-width="500">
      <v-card>
        <v-card-title>Approve Vendor</v-card-title>
        <v-card-text>
          <v-form ref="approvalForm">
            <v-textarea
              v-model="approvalNotes"
              label="Approval Notes"
              rows="3"
            />
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="showApprovalDialog = false">Cancel</v-btn>
          <v-btn color="success" @click="confirmApproval">Approve</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
    <!-- Rejection Dialog -->
    <v-dialog v-model="showRejectionDialog" max-width="500">
      <v-card>
        <v-card-title>Reject Vendor</v-card-title>
        <v-card-text>
          <v-form ref="rejectionForm">
            <v-textarea
              v-model="rejectionReason"
              label="Rejection Reason"
              rows="3"
              required
            />
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="showRejectionDialog = false">Cancel</v-btn>
          <v-btn color="error" @click="confirmRejection">Reject</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useVendorStore } from '../../store/vendors'

const emit = defineEmits(['approve', 'reject'])

const vendorStore = useVendorStore()
const loading = ref(false)
const pendingVendors = ref([])
const showApprovalDialog = ref(false)
const showRejectionDialog = ref(false)
const selectedVendor = ref(null)
const approvalNotes = ref('')
const rejectionReason = ref('')

const headers = [
  { title: 'Vendor ID', key: 'vendor_id' },
  { title: 'Name', key: 'name' },
  { title: 'Email', key: 'email' },
  { title: 'Category', key: 'category' },
  { title: 'Status', key: 'status' },
  { title: 'Actions', key: 'actions', sortable: false }
]

const getStatusColor = (status) => {
  switch (status) {
    case 'pending_approval': return 'warning'
    case 'approved': return 'success'
    case 'rejected': return 'error'
    default: return 'grey'
  }
}

const approve = (vendor) => {
  selectedVendor.value = vendor
  showApprovalDialog.value = true
}

const reject = (vendor) => {
  selectedVendor.value = vendor
  showRejectionDialog.value = true
}

const confirmApproval = () => {
  emit('approve', selectedVendor.value.id, {
    approved_by: 'current_user',
    notes: approvalNotes.value
  })
  showApprovalDialog.value = false
  approvalNotes.value = ''
  loadPendingVendors()
}

const confirmRejection = () => {
  emit('reject', selectedVendor.value.id, {
    rejected_by: 'current_user',
    reason: rejectionReason.value
  })
  showRejectionDialog.value = false
  rejectionReason.value = ''
  loadPendingVendors()
}

const loadPendingVendors = async () => {
  loading.value = true
  try {
    const vendors = await vendorStore.getVendors({ status: 'pending_approval' })
    pendingVendors.value = vendors
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadPendingVendors()
})
</script>