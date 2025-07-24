<template>
  <div class="payment-form">
    <v-form ref="form" v-model="valid" @submit.prevent="savePayment">
      <v-card>
        <v-card-title>
          <h2>New Payment</h2>
        </v-card-title>
        
        <v-card-text>
          <v-row>
            <!-- Payment Header -->
            <v-col cols="12">
              <h3 class="text-subtitle-1 font-weight-bold">Payment Information</h3>
            </v-col>
            
            <v-col cols="12" md="6">
              <v-select
                v-model="formData.vendor_id"
                label="Vendor*"
                :items="vendors"
                item-title="name"
                item-value="id"
                :rules="[v => !!v || 'Vendor is required']"
                required
                @update:model-value="handleVendorChange"
              ></v-select>
            </v-col>
            
            <v-col cols="12" md="6">
              <v-menu
                ref="paymentDateMenu"
                v-model="paymentDateMenu"
                :close-on-content-click="false"
                transition="scale-transition"
                offset-y
                min-width="auto"
              >
                <template v-slot:activator="{ props }">
                  <v-text-field
                    v-model="formData.payment_date"
                    label="Payment Date*"
                    prepend-inner-icon="mdi-calendar"
                    readonly
                    v-bind="props"
                    :rules="[v => !!v || 'Payment date is required']"
                    required
                  ></v-text-field>
                </template>
                <v-date-picker
                  v-model="formData.payment_date"
                  @update:model-value="paymentDateMenu = false"
                ></v-date-picker>
              </v-menu>
            </v-col>
            
            <v-col cols="12" md="6">
              <v-select
                v-model="formData.payment_method"
                label="Payment Method*"
                :items="paymentMethodOptions"
                :rules="[v => !!v || 'Payment method is required']"
                required
              ></v-select>
            </v-col>
            
            <v-col cols="12" md="6">
              <v-text-field
                v-model="formData.reference"
                label="Reference"
                placeholder="Check number, transaction ID, etc."
              ></v-text-field>
            </v-col>
            
            <v-col cols="12">
              <v-textarea
                v-model="formData.memo"
                label="Memo"
                rows="2"
                auto-grow
              ></v-textarea>
            </v-col>
            
            <!-- Invoice Selection -->
            <v-col cols="12" class="mt-4">
              <h3 class="text-subtitle-1 font-weight-bold">Select Invoices to Pay</h3>
              
              <v-data-table
                v-model="selectedInvoices"
                :headers="invoiceHeaders"
                :items="availableInvoices"
                :loading="loadingInvoices"
                item-value="id"
                show-select
                class="elevation-1 mt-2"
                @update:model-value="handleInvoiceSelection"
              >
                <template v-slot:item.invoice_date="{ item }">
                  {{ formatDate(item.invoice_date) }}
                </template>
                
                <template v-slot:item.due_date="{ item }">
                  {{ formatDate(item.due_date) }}
                </template>
                
                <template v-slot:item.total_amount="{ item }">
                  {{ formatCurrency(item.total_amount) }}
                </template>
                
                <template v-slot:item.balance_due="{ item }">
                  {{ formatCurrency(item.balance_due) }}
                </template>
                
                <template v-slot:item.payment_amount="{ item }">
                  <v-text-field
                    v-model="invoicePayments[item.id]"
                    type="number"
                    density="compact"
                    hide-details
                    :disabled="!isInvoiceSelected(item.id)"
                    :rules="[
                      v => !isInvoiceSelected(item.id) || !!v || 'Amount is required',
                      v => !isInvoiceSelected(item.id) || v > 0 || 'Amount must be greater than 0',
                      v => !isInvoiceSelected(item.id) || v <= item.balance_due || 'Amount cannot exceed balance due'
                    ]"
                    @input="updateTotalAmount"
                  ></v-text-field>
                </template>
              </v-data-table>
            </v-col>
            
            <!-- Totals -->
            <v-col cols="12" md="6" offset-md="6" class="mt-4">
              <v-list>
                <v-list-item>
                  <template v-slot:prepend>
                    <div class="font-weight-bold">Total Payment Amount:</div>
                  </template>
                  <v-list-item-title class="text-right font-weight-bold">
                    {{ formatCurrency(totalPaymentAmount) }}
                  </v-list-item-title>
                </v-list-item>
              </v-list>
            </v-col>
          </v-row>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" variant="text" @click="cancel">Cancel</v-btn>
          <v-btn
            color="primary"
            type="submit"
            :loading="saving"
            :disabled="!valid || saving || !hasSelectedInvoices || totalPaymentAmount <= 0"
          >
            Create Payment
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-form>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue';
import { useSnackbar } from '@/composables/useSnackbar';
import { formatCurrency, formatDate } from '@/utils/formatters';
import { apiClient } from '@/utils/apiClient';

// Emits
const emit = defineEmits(['saved', 'cancelled']);

// Composables
const { showSnackbar } = useSnackbar();

// Refs
const form = ref(null);
const valid = ref(false);
const saving = ref(false);
const paymentDateMenu = ref(false);

// Data
const vendors = ref([]);
const availableInvoices = ref([]);
const selectedInvoices = ref([]);
const invoicePayments = reactive({});
const loadingInvoices = ref(false);

// Form data
const formData = reactive({
  vendor_id: null,
  payment_date: new Date().toISOString().substr(0, 10),
  payment_method: 'check',
  reference: '',
  memo: '',
  invoices: [],
  amount: 0,
});

// Invoice headers
const invoiceHeaders = [
  { title: 'Invoice #', key: 'invoice_number', sortable: true },
  { title: 'Date', key: 'invoice_date', sortable: true },
  { title: 'Due Date', key: 'due_date', sortable: true },
  { title: 'Total', key: 'total_amount', sortable: true, align: 'end' },
  { title: 'Balance Due', key: 'balance_due', sortable: true, align: 'end' },
  { title: 'Payment Amount', key: 'payment_amount', sortable: false, align: 'end' },
];

// Payment method options
const paymentMethodOptions = [
  { title: 'Check', value: 'check' },
  { title: 'ACH', value: 'ach' },
  { title: 'Wire Transfer', value: 'wire' },
  { title: 'Credit Card', value: 'credit_card' },
  { title: 'Cash', value: 'cash' },
  { title: 'Other', value: 'other' },
];

// Computed
const totalPaymentAmount = computed(() => {
  let total = 0;
  for (const invoiceId of selectedInvoices.value) {
    total += Number(invoicePayments[invoiceId] || 0);
  }
  return total;
});

const hasSelectedInvoices = computed(() => {
  return selectedInvoices.value.length > 0;
});

// Methods
const fetchVendors = async () => {
  try {
    const response = await apiClient.get('/api/v1/accounts-payable/vendors', { 
      params: { page_size: 100 } 
    });
    vendors.value = response.data;
  } catch (error) {
    console.error('Error fetching vendors:', error);
  }
};

const fetchVendorInvoices = async (vendorId) => {
  if (!vendorId) {
    availableInvoices.value = [];
    return;
  }
  
  loadingInvoices.value = true;
  try {
    const response = await apiClient.get('/api/v1/accounts-payable/invoices', {
      params: {
        vendor_id: vendorId,
        status: 'approved',
        page_size: 100,
      }
    });
    
    // Filter invoices with balance due > 0
    availableInvoices.value = response.data.filter(invoice => invoice.balance_due > 0);
    
    // Initialize payment amounts to balance due
    for (const invoice of availableInvoices.value) {
      invoicePayments[invoice.id] = invoice.balance_due;
    }
  } catch (error) {
    showSnackbar('Failed to load invoices', 'error');
    console.error('Error fetching invoices:', error);
  } finally {
    loadingInvoices.value = false;
  }
};

const handleVendorChange = (vendorId) => {
  // Reset selected invoices and payments
  selectedInvoices.value = [];
  Object.keys(invoicePayments).forEach(key => delete invoicePayments[key]);
  
  // Fetch invoices for the selected vendor
  fetchVendorInvoices(vendorId);
};

const handleInvoiceSelection = (selected) => {
  // Update payment amounts based on selection
  for (const invoiceId of Object.keys(invoicePayments)) {
    if (!selected.includes(invoiceId)) {
      invoicePayments[invoiceId] = 0;
    } else if (invoicePayments[invoiceId] === 0) {
      // If newly selected, set to balance due
      const invoice = availableInvoices.value.find(inv => inv.id === invoiceId);
      if (invoice) {
        invoicePayments[invoiceId] = invoice.balance_due;
      }
    }
  }
  
  updateTotalAmount();
};

const isInvoiceSelected = (invoiceId) => {
  return selectedInvoices.value.includes(invoiceId);
};

const updateTotalAmount = () => {
  formData.amount = totalPaymentAmount.value;
};

const savePayment = async () => {
  if (!valid.value || !hasSelectedInvoices.value || totalPaymentAmount.value <= 0) return;
  
  saving.value = true;
  try {
    // Prepare invoice payments
    const invoicePaymentsList = selectedInvoices.value.map(invoiceId => ({
      invoice_id: invoiceId,
      amount: Number(invoicePayments[invoiceId])
    })).filter(item => item.amount > 0);
    
    const payload = {
      vendor_id: formData.vendor_id,
      payment_date: formData.payment_date,
      payment_method: formData.payment_method,
      reference: formData.reference,
      memo: formData.memo,
      amount: totalPaymentAmount.value,
      invoices: invoicePaymentsList
    };
    
    await apiClient.post('/api/v1/accounts-payable/payments', payload);
    showSnackbar('Payment created successfully', 'success');
    emit('saved');
  } catch (error) {
    showSnackbar(error.response?.data?.message || 'Failed to create payment', 'error');
    console.error('Error creating payment:', error);
  } finally {
    saving.value = false;
  }
};

const cancel = () => {
  emit('cancelled');
};

// Lifecycle hooks
onMounted(() => {
  fetchVendors();
});
</script>

<style scoped>
.payment-form {
  padding: 16px;
}
</style>