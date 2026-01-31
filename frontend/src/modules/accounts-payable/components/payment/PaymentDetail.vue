<template>
  <div class="payment-detail">
    <v-card>
      <v-card-title class="d-flex align-center justify-space-between">
        <h2>Payment Details</h2>
        <div>
          <v-btn
            v-if="canVoid"
            color="error"
            class="mr-2"
            prepend-icon="mdi-cancel"
            @click="voidPayment"
          >
            Void
          </v-btn>
          <v-btn
            color="primary"
            prepend-icon="mdi-printer"
            @click="printPayment"
          >
            Print
          </v-btn>
        </div>
      </v-card-title>
      
      <v-card-text>
        <v-row>
          <!-- Payment Header -->
          <v-col cols="12" md="6">
            <v-card variant="outlined" class="mb-4">
              <v-card-title>Payment Information</v-card-title>
              <v-card-text>
                <v-row>
                  <v-col cols="12" md="6">
                    <div class="text-caption">Payment Number</div>
                    <div class="text-body-1 font-weight-medium">{{ payment.payment_number }}</div>
                  </v-col>
                  <v-col cols="12" md="6">
                    <div class="text-caption">Status</div>
                    <v-chip
                      :color="getStatusColor(payment.status)"
                      size="small"
                      text-color="white"
                    >
                      {{ formatStatus(payment.status) }}
                    </v-chip>
                  </v-col>
                  <v-col cols="12" md="6">
                    <div class="text-caption">Payment Date</div>
                    <div class="text-body-1">{{ formatDate(payment.payment_date) }}</div>
                  </v-col>
                  <v-col cols="12" md="6">
                    <div class="text-caption">Payment Method</div>
                    <div class="text-body-1">{{ formatPaymentMethod(payment.payment_method) }}</div>
                  </v-col>
                  <v-col cols="12" md="6">
                    <div class="text-caption">Amount</div>
                    <div class="text-body-1 font-weight-bold">{{ formatCurrency(payment.amount) }}</div>
                  </v-col>
                  <v-col cols="12" md="6">
                    <div class="text-caption">Reference</div>
                    <div class="text-body-1">{{ payment.reference || 'N/A' }}</div>
                  </v-col>
                </v-row>
              </v-card-text>
            </v-card>
          </v-col>
          
          <!-- Vendor Information -->
          <v-col cols="12" md="6">
            <v-card variant="outlined" class="mb-4">
              <v-card-title>Vendor Information</v-card-title>
              <v-card-text v-if="payment.vendor">
                <v-row>
                  <v-col cols="12">
                    <div class="text-caption">Vendor Name</div>
                    <div class="text-body-1 font-weight-medium">{{ payment.vendor.name }}</div>
                  </v-col>
                  <v-col cols="12" md="6">
                    <div class="text-caption">Email</div>
                    <div class="text-body-1">{{ payment.vendor.email || 'N/A' }}</div>
                  </v-col>
                  <v-col cols="12" md="6">
                    <div class="text-caption">Phone</div>
                    <div class="text-body-1">{{ payment.vendor.phone || 'N/A' }}</div>
                  </v-col>
                </v-row>
              </v-card-text>
            </v-card>
          </v-col>
          
          <!-- Memo -->
          <v-col cols="12">
            <v-card variant="outlined" class="mb-4">
              <v-card-title>Memo</v-card-title>
              <v-card-text>
                <div class="text-body-1">{{ payment.memo || 'No memo provided.' }}</div>
              </v-card-text>
            </v-card>
          </v-col>
          
          <!-- Invoices -->
          <v-col cols="12">
            <v-card variant="outlined" class="mb-4">
              <v-card-title>Invoices Paid</v-card-title>
              <v-card-text>
                <v-data-table
                  :headers="invoiceHeaders"
                  :items="payment.invoices || []"
                  class="elevation-0"
                >
                  <template v-slot:item.invoice_number="{ item }">
                    <a href="#" @click.prevent="viewInvoice(item.invoice_id)">{{ item.invoice_number }}</a>
                  </template>
                  
                  <template v-slot:item.amount="{ item }">
                    {{ formatCurrency(item.amount) }}
                  </template>
                  
                  <template v-slot:item.invoice_total="{ item }">
                    {{ formatCurrency(item.invoice_total) }}
                  </template>
                  
                  <template v-slot:item.invoice_balance_before="{ item }">
                    {{ formatCurrency(item.invoice_balance_before) }}
                  </template>
                  
                  <template v-slot:item.invoice_balance_after="{ item }">
                    {{ formatCurrency(item.invoice_balance_after) }}
                  </template>
                </v-data-table>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
    
    <!-- Void Dialog -->
    <v-dialog v-model="voidDialog.show" max-width="500px">
      <v-card>
        <v-card-title>Void Payment</v-card-title>
        <v-card-text>
          <p>Are you sure you want to void this payment?</p>
          <p class="text-warning">This will reverse all invoice payments and cannot be undone.</p>
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
            color="error"
            :disabled="!voidDialog.reason"
            @click="submitVoidAction"
          >
            Void Payment
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
  paymentId: {
    type: String,
    required: true,
  },
});

// Emits
const emit = defineEmits(['updated']);

// Composables
const { showSnackbar } = useSnackbar();

// Data
const payment = ref({
  id: '',
  payment_number: '',
  vendor_id: '',
  vendor: null,
  payment_date: '',
  amount: 0,
  payment_method: '',
  reference: '',
  memo: '',
  status: '',
  invoices: [],
});

const loading = ref(false);

// Invoice headers
const invoiceHeaders = [
  { title: 'Invoice #', key: 'invoice_number', sortable: true },
  { title: 'Invoice Total', key: 'invoice_total', sortable: true, align: 'end' },
  { title: 'Previous Balance', key: 'invoice_balance_before', sortable: true, align: 'end' },
  { title: 'Payment Amount', key: 'amount', sortable: true, align: 'end' },
  { title: 'Remaining Balance', key: 'invoice_balance_after', sortable: true, align: 'end' },
];

// Dialogs
const voidDialog = reactive({
  show: false,
  reason: '',
});

// Computed
const canVoid = computed(() => {
  return payment.value.status === 'completed';
});

// Methods
const fetchPayment = async () => {
  loading.value = true;
  try {
    const response = await apiClient.get(`/api/v1/accounts-payable/payments/${props.paymentId}`);
    payment.value = response.data;
  } catch (error) {
    showSnackbar('Failed to load payment', 'error');
    console.error('Error fetching payment:', error);
  } finally {
    loading.value = false;
  }
};

const viewInvoice = (invoiceId) => {
  // Navigate to invoice detail page
  // router.push({ name: 'invoice-detail', params: { id: invoiceId } });
};

const voidPayment = () => {
  voidDialog.reason = '';
  voidDialog.show = true;
};

const submitVoidAction = async () => {
  if (!voidDialog.reason) return;
  
  try {
    await apiClient.post(`/api/v1/accounts-payable/payments/${props.paymentId}/void`, {
      reason: voidDialog.reason
    });
    showSnackbar('Payment voided successfully', 'success');
    fetchPayment();
    emit('updated');
  } catch (error) {
    showSnackbar('Failed to void payment', 'error');
    console.error('Error voiding payment:', error);
  } finally {
    voidDialog.show = false;
  }
};

const printPayment = () => {
  window.print();
};

// Helper methods
const getStatusColor = (status) => {
  const colors = {
    pending: 'warning',
    completed: 'success',
    voided: 'error',
  };
  return colors[status] || 'grey';
};

const formatStatus = (status) => {
  return status.charAt(0).toUpperCase() + status.slice(1);
};

const formatPaymentMethod = (method) => {
  const methodMap = {
    check: 'Check',
    ach: 'ACH',
    wire: 'Wire Transfer',
    credit_card: 'Credit Card',
    cash: 'Cash',
    other: 'Other',
  };
  return methodMap[method] || method;
};

// Lifecycle hooks
onMounted(() => {
  fetchPayment();
});
</script>

<style scoped>
.payment-detail {
  padding: 16px;
}

@media print {
  .v-btn {
    display: none !important;
  }
}
</style>