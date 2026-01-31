<template>
  <div class="invoice-detail">
    <v-card>
      <v-card-title class="d-flex align-center justify-space-between">
        <h2>Invoice Details</h2>
        <div>
          <v-btn
            v-if="canEdit"
            color="warning"
            class="mr-2"
            prepend-icon="mdi-pencil"
            @click="editInvoice"
          >
            Edit
          </v-btn>
          <v-btn
            v-if="canSubmit"
            color="info"
            class="mr-2"
            prepend-icon="mdi-send"
            @click="submitInvoice"
          >
            Submit
          </v-btn>
          <v-btn
            v-if="canApprove"
            color="success"
            class="mr-2"
            prepend-icon="mdi-check"
            @click="approveInvoice"
          >
            Approve
          </v-btn>
          <v-btn
            v-if="canReject"
            color="error"
            class="mr-2"
            prepend-icon="mdi-close"
            @click="rejectInvoice"
          >
            Reject
          </v-btn>
          <v-btn
            v-if="canVoid"
            color="grey-darken-1"
            class="mr-2"
            prepend-icon="mdi-cancel"
            @click="voidInvoice"
          >
            Void
          </v-btn>
          <v-btn
            color="primary"
            prepend-icon="mdi-printer"
            @click="printInvoice"
          >
            Print
          </v-btn>
        </div>
      </v-card-title>
      
      <v-card-text>
        <v-row>
          <!-- Invoice Header -->
          <v-col cols="12" md="6">
            <v-card variant="outlined" class="mb-4">
              <v-card-title>Invoice Information</v-card-title>
              <v-card-text>
                <v-row>
                  <v-col cols="12" md="6">
                    <div class="text-caption">Invoice Number</div>
                    <div class="text-body-1 font-weight-medium">{{ invoice.invoice_number }}</div>
                  </v-col>
                  <v-col cols="12" md="6">
                    <div class="text-caption">Status</div>
                    <v-chip
                      :color="getStatusColor(invoice.status)"
                      size="small"
                      text-color="white"
                    >
                      {{ formatStatus(invoice.status) }}
                    </v-chip>
                  </v-col>
                  <v-col cols="12" md="6">
                    <div class="text-caption">Invoice Date</div>
                    <div class="text-body-1">{{ formatDate(invoice.invoice_date) }}</div>
                  </v-col>
                  <v-col cols="12" md="6">
                    <div class="text-caption">Due Date</div>
                    <div class="text-body-1">{{ formatDate(invoice.due_date) }}</div>
                  </v-col>
                  <v-col cols="12" md="6">
                    <div class="text-caption">Payment Terms</div>
                    <div class="text-body-1">{{ formatPaymentTerms(invoice.payment_terms) }}</div>
                  </v-col>
                  <v-col cols="12" md="6">
                    <div class="text-caption">Reference</div>
                    <div class="text-body-1">{{ invoice.reference || 'N/A' }}</div>
                  </v-col>
                </v-row>
              </v-card-text>
            </v-card>
          </v-col>
          
          <!-- Vendor Information -->
          <v-col cols="12" md="6">
            <v-card variant="outlined" class="mb-4">
              <v-card-title>Vendor Information</v-card-title>
              <v-card-text v-if="invoice.vendor">
                <v-row>
                  <v-col cols="12">
                    <div class="text-caption">Vendor Name</div>
                    <div class="text-body-1 font-weight-medium">{{ invoice.vendor.name }}</div>
                  </v-col>
                  <v-col cols="12" md="6">
                    <div class="text-caption">Email</div>
                    <div class="text-body-1">{{ invoice.vendor.email || 'N/A' }}</div>
                  </v-col>
                  <v-col cols="12" md="6">
                    <div class="text-caption">Phone</div>
                    <div class="text-body-1">{{ invoice.vendor.phone || 'N/A' }}</div>
                  </v-col>
                  <v-col cols="12">
                    <div class="text-caption">Address</div>
                    <div class="text-body-1">
                      <template v-if="invoice.vendor.address_line1">
                        {{ invoice.vendor.address_line1 }}<br>
                        <template v-if="invoice.vendor.address_line2">
                          {{ invoice.vendor.address_line2 }}<br>
                        </template>
                        {{ [invoice.vendor.city, invoice.vendor.state, invoice.vendor.postal_code].filter(Boolean).join(', ') }}<br>
                        {{ invoice.vendor.country }}
                      </template>
                      <template v-else>
                        N/A
                      </template>
                    </div>
                  </v-col>
                </v-row>
              </v-card-text>
            </v-card>
          </v-col>
          
          <!-- Description -->
          <v-col cols="12">
            <v-card variant="outlined" class="mb-4">
              <v-card-title>Description</v-card-title>
              <v-card-text>
                <div class="text-body-1">{{ invoice.description || 'No description provided.' }}</div>
              </v-card-text>
            </v-card>
          </v-col>
          
          <!-- Line Items -->
          <v-col cols="12">
            <v-card variant="outlined" class="mb-4">
              <v-card-title>Line Items</v-card-title>
              <v-card-text>
                <v-data-table
                  :headers="lineItemHeaders"
                  :items="invoice.line_items || []"
                  class="elevation-0"
                >
                  <template v-slot:item.amount="{ item }">
                    {{ formatCurrency(item.amount) }}
                  </template>
                </v-data-table>
              </v-card-text>
            </v-card>
          </v-col>
          
          <!-- Totals -->
          <v-col cols="12" md="6" offset-md="6">
            <v-card variant="outlined" class="mb-4">
              <v-card-title>Totals</v-card-title>
              <v-card-text>
                <v-list>
                  <v-list-item>
                    <template v-slot:prepend>
                      <div class="font-weight-medium">Subtotal:</div>
                    </template>
                    <v-list-item-title class="text-right">
                      {{ formatCurrency(invoice.subtotal) }}
                    </v-list-item-title>
                  </v-list-item>
                  
                  <v-list-item>
                    <template v-slot:prepend>
                      <div class="font-weight-medium">Tax:</div>
                    </template>
                    <v-list-item-title class="text-right">
                      {{ formatCurrency(invoice.tax_amount) }}
                    </v-list-item-title>
                  </v-list-item>
                  
                  <v-list-item v-if="invoice.discount_amount > 0">
                    <template v-slot:prepend>
                      <div class="font-weight-medium">Discount:</div>
                    </template>
                    <v-list-item-title class="text-right">
                      {{ formatCurrency(invoice.discount_amount) }}
                    </v-list-item-title>
                  </v-list-item>
                  
                  <v-list-item>
                    <template v-slot:prepend>
                      <div class="font-weight-bold">Total:</div>
                    </template>
                    <v-list-item-title class="text-right font-weight-bold">
                      {{ formatCurrency(invoice.total_amount) }}
                    </v-list-item-title>
                  </v-list-item>
                  
                  <v-list-item v-if="invoice.paid_amount > 0">
                    <template v-slot:prepend>
                      <div class="font-weight-medium">Paid:</div>
                    </template>
                    <v-list-item-title class="text-right">
                      {{ formatCurrency(invoice.paid_amount) }}
                    </v-list-item-title>
                  </v-list-item>
                  
                  <v-list-item v-if="invoice.paid_amount > 0">
                    <template v-slot:prepend>
                      <div class="font-weight-bold">Balance Due:</div>
                    </template>
                    <v-list-item-title class="text-right font-weight-bold">
                      {{ formatCurrency(invoice.balance_due) }}
                    </v-list-item-title>
                  </v-list-item>
                </v-list>
              </v-card-text>
            </v-card>
          </v-col>
          
          <!-- Approval Information -->
          <v-col cols="12" v-if="invoice.approved_by_id">
            <v-card variant="outlined" class="mb-4">
              <v-card-title>Approval Information</v-card-title>
              <v-card-text>
                <v-row>
                  <v-col cols="12" md="6">
                    <div class="text-caption">Approved By</div>
                    <div class="text-body-1">{{ invoice.approved_by?.full_name || invoice.approved_by_id }}</div>
                  </v-col>
                  <v-col cols="12" md="6">
                    <div class="text-caption">Approved At</div>
                    <div class="text-body-1">{{ formatDateTime(invoice.approved_at) }}</div>
                  </v-col>
                </v-row>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
    
    <!-- Approval Dialog -->
    <v-dialog v-model="approvalDialog.show" max-width="500px">
      <v-card>
        <v-card-title>{{ approvalDialog.action === 'approve' ? 'Approve' : 'Reject' }} Invoice</v-card-title>
        <v-card-text>
          <p>{{ approvalDialog.action === 'approve' ? 'Approve' : 'Reject' }} invoice "{{ invoice.invoice_number }}"?</p>
          <v-textarea
            v-model="approvalDialog.notes"
            label="Notes"
            rows="3"
            auto-grow
          ></v-textarea>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" variant="text" @click="approvalDialog.show = false">Cancel</v-btn>
          <v-btn 
            :color="approvalDialog.action === 'approve' ? 'success' : 'error'"
            @click="submitApprovalAction"
          >
            {{ approvalDialog.action === 'approve' ? 'Approve' : 'Reject' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
    <!-- Void Dialog -->
    <v-dialog v-model="voidDialog.show" max-width="500px">
      <v-card>
        <v-card-title>Void Invoice</v-card-title>
        <v-card-text>
          <p>Void invoice "{{ invoice.invoice_number }}"?</p>
          <v-textarea
            v-model="voidDialog.reason"
            label="Reason"
            rows="3"
            auto-grow
            :rules="[v => !!v || 'Reason is required']"
          ></v-textarea>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" variant="text" @click="voidDialog.show = false">Cancel</v-btn>
          <v-btn 
            color="grey-darken-1"
            :disabled="!voidDialog.reason"
            @click="submitVoidAction"
          >
            Void
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { useSnackbar } from '@/composables/useSnackbar';
import { apiClient } from '@/utils/apiClient';

// Props
const props = defineProps({
  invoiceId: {
    type: String,
    required: true,
  },
});

// Emits
const emit = defineEmits(['updated']);

// Composables
const { showSnackbar } = useSnackbar();

// Data
const invoice = ref({
  id: '',
  invoice_number: '',
  vendor_id: '',
  vendor: null,
  invoice_date: '',
  due_date: '',
  description: '',
  reference: '',
  payment_terms: '',
  currency_id: null,
  requires_approval: false,
  status: '',
  subtotal: 0,
  tax_amount: 0,
  discount_amount: 0,
  total_amount: 0,
  paid_amount: 0,
  balance_due: 0,
  line_items: [],
  approved_by_id: null,
  approved_by: null,
  approved_at: null,
});

const loading = ref(false);

// Line item headers
const lineItemHeaders = [
  { title: 'Description', key: 'description', sortable: true },
  { title: 'Quantity', key: 'quantity', sortable: true },
  { title: 'Unit Price', key: 'unit_price', sortable: true },
  { title: 'Amount', key: 'amount', sortable: true, align: 'end' },
];

// Dialogs
const approvalDialog = reactive({
  show: false,
  action: 'approve', // 'approve' or 'reject'
  notes: '',
});

const voidDialog = reactive({
  show: false,
  reason: '',
});

// Computed
const canEdit = computed(() => {
  return ['draft', 'rejected'].includes(invoice.value.status);
});

const canSubmit = computed(() => {
  return invoice.value.status === 'draft';
});

const canApprove = computed(() => {
  return invoice.value.status === 'pending';
});

const canReject = computed(() => {
  return invoice.value.status === 'pending';
});

const canVoid = computed(() => {
  return ['draft', 'pending', 'approved', 'rejected'].includes(invoice.value.status);
});

// Methods
const fetchInvoice = async () => {
  loading.value = true;
  try {
    const response = await apiClient.get(`/api/v1/accounts-payable/invoices/${props.invoiceId}`);
    invoice.value = response.data;
  } catch (error) {
    showSnackbar('Failed to load invoice', 'error');
    console.error('Error fetching invoice:', error);
  } finally {
    loading.value = false;
  }
};

const editInvoice = () => {
  // Navigate to invoice edit page
  // router.push({ name: 'invoice-edit', params: { id: props.invoiceId } });
};

const submitInvoice = async () => {
  try {
    await apiClient.post(`/api/v1/accounts-payable/invoices/${props.invoiceId}/submit`);
    showSnackbar('Invoice submitted for approval', 'success');
    fetchInvoice();
    emit('updated');
  } catch (error) {
    showSnackbar('Failed to submit invoice', 'error');
    console.error('Error submitting invoice:', error);
  }
};

const approveInvoice = () => {
  approvalDialog.action = 'approve';
  approvalDialog.notes = '';
  approvalDialog.show = true;
};

const rejectInvoice = () => {
  approvalDialog.action = 'reject';
  approvalDialog.notes = '';
  approvalDialog.show = true;
};

const submitApprovalAction = async () => {
  try {
    const endpoint = `/api/v1/accounts-payable/invoices/${props.invoiceId}/${approvalDialog.action}`;
    const payload = {
      approved_by_id: '00000000-0000-0000-0000-000000000000', // Replace with actual user ID
      notes: approvalDialog.notes
    };
    
    await apiClient.post(endpoint, payload);
    showSnackbar(`Invoice ${approvalDialog.action === 'approve' ? 'approved' : 'rejected'} successfully`, 'success');
    fetchInvoice();
    emit('updated');
  } catch (error) {
    showSnackbar(`Failed to ${approvalDialog.action} invoice`, 'error');
    console.error(`Error ${approvalDialog.action}ing invoice:`, error);
  } finally {
    approvalDialog.show = false;
  }
};

const voidInvoice = () => {
  voidDialog.reason = '';
  voidDialog.show = true;
};

const submitVoidAction = async () => {
  if (!voidDialog.reason) return;
  
  try {
    await apiClient.post(`/api/v1/accounts-payable/invoices/${props.invoiceId}/void`, {
      reason: voidDialog.reason
    });
    showSnackbar('Invoice voided successfully', 'success');
    fetchInvoice();
    emit('updated');
  } catch (error) {
    showSnackbar('Failed to void invoice', 'error');
    console.error('Error voiding invoice:', error);
  } finally {
    voidDialog.show = false;
  }
};

const printInvoice = () => {
  window.print();
};

// Helper methods
const getStatusColor = (status) => {
  const colors = {
    draft: 'grey',
    pending: 'warning',
    approved: 'info',
    paid: 'success',
    partially_paid: 'success-lighten-1',
    rejected: 'error',
    voided: 'grey-darken-1',
    cancelled: 'grey-darken-2',
  };
  return colors[status] || 'grey';
};

const formatStatus = (status) => {
  return status.charAt(0).toUpperCase() + status.slice(1).replace('_', ' ');
};

const formatPaymentTerms = (terms) => {
  const termMap = {
    net_15: 'Net 15',
    net_30: 'Net 30',
    net_45: 'Net 45',
    net_60: 'Net 60',
    due_on_receipt: 'Due on Receipt',
    prepaid: 'Prepaid',
    cod: 'Cash on Delivery',
    custom: 'Custom',
  };
  return termMap[terms] || terms;
};

// Lifecycle hooks
onMounted(() => {
  fetchInvoice();
});
</script>

<style scoped>
.invoice-detail {
  padding: 16px;
}

@media print {
  .v-btn {
    display: none !important;
  }
}
</style>