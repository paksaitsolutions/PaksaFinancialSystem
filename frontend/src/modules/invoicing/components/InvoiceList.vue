<template>
  <div class="invoice-list">
    <v-card>
      <v-card-title class="d-flex align-center justify-space-between">
        <h3>Invoices</h3>
        <v-btn color="primary" prepend-icon="mdi-plus" @click="createInvoice">
          Create Invoice
        </v-btn>
      </v-card-title>
      
      <v-card-text>
        <!-- Filters -->
        <v-row class="mb-4">
          <v-col cols="12" md="3">
            <v-select
              v-model="filters.status"
              label="Status"
              :items="statusOptions"
              clearable
              @update:model-value="fetchInvoices"
            ></v-select>
          </v-col>
          
          <v-col cols="12" md="3">
            <v-select
              v-model="filters.payment_status"
              label="Payment Status"
              :items="paymentStatusOptions"
              clearable
              @update:model-value="fetchInvoices"
            ></v-select>
          </v-col>
          
          <v-col cols="12" md="6" class="d-flex align-center justify-end">
            <v-btn
              prepend-icon="mdi-refresh"
              @click="fetchInvoices"
              :loading="loading"
            >
              Refresh
            </v-btn>
          </v-col>
        </v-row>
        
        <!-- Data Table -->
        <v-data-table
          :headers="headers"
          :items="invoices"
          :loading="loading"
          class="elevation-1"
        >
          <template v-slot:item.invoice_number="{ item }">
            <v-btn
              variant="text"
              color="primary"
              @click="viewInvoice(item)"
            >
              {{ item.invoice_number }}
            </v-btn>
          </template>
          
          <template v-slot:item.status="{ item }">
            <v-chip :color="getStatusColor(item.status)" size="small">
              {{ item.status.toUpperCase() }}
            </v-chip>
          </template>
          
          <template v-slot:item.payment_status="{ item }">
            <v-chip :color="getPaymentStatusColor(item.payment_status)" size="small">
              {{ item.payment_status.toUpperCase() }}
            </v-chip>
          </template>
          
          <template v-slot:item.total_amount="{ item }">
            {{ formatCurrency(item.total_amount) }}
          </template>
          
          <template v-slot:item.issue_date="{ item }">
            {{ formatDate(item.issue_date) }}
          </template>
          
          <template v-slot:item.due_date="{ item }">
            {{ formatDate(item.due_date) }}
          </template>
          
          <template v-slot:item.actions="{ item }">
            <v-menu>
              <template v-slot:activator="{ props }">
                <v-btn icon size="small" v-bind="props">
                  <v-icon>mdi-dots-vertical</v-icon>
                </v-btn>
              </template>
              
              <v-list>
                <v-list-item @click="viewInvoice(item)">
                  <v-list-item-title>View</v-list-item-title>
                </v-list-item>
                
                <v-list-item @click="editInvoice(item)" v-if="item.status === 'draft'">
                  <v-list-item-title>Edit</v-list-item-title>
                </v-list-item>
                
                <v-list-item @click="sendInvoice(item)" v-if="item.status === 'draft'">
                  <v-list-item-title>Send</v-list-item-title>
                </v-list-item>
                
                <v-list-item @click="addPayment(item)" v-if="item.payment_status !== 'paid'">
                  <v-list-item-title>Add Payment</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>
    
    <!-- Invoice Form Dialog -->
    <v-dialog v-model="showForm" max-width="1200px" persistent>
      <invoice-form
        :invoice-data="selectedInvoice"
        @saved="onInvoiceSaved"
        @cancel="showForm = false"
      />
    </v-dialog>
    
    <!-- Payment Dialog -->
    <v-dialog v-model="showPaymentDialog" max-width="500px">
      <v-card>
        <v-card-title>Add Payment</v-card-title>
        <v-card-text>
          <v-form ref="paymentForm" v-model="paymentValid">
            <v-text-field
              v-model="payment.payment_date"
              label="Payment Date*"
              type="date"
              :rules="[v => !!v || 'Payment date is required']"
              required
            ></v-text-field>
            
            <v-text-field
              v-model.number="payment.amount"
              label="Amount*"
              type="number"
              step="0.01"
              :rules="[v => !!v || 'Amount is required']"
              required
            ></v-text-field>
            
            <v-select
              v-model="payment.payment_method"
              label="Payment Method*"
              :items="paymentMethods"
              :rules="[v => !!v || 'Payment method is required']"
              required
            ></v-select>
            
            <v-text-field
              v-model="payment.reference"
              label="Reference"
            ></v-text-field>
            
            <v-textarea
              v-model="payment.notes"
              label="Notes"
              rows="2"
            ></v-textarea>
          </v-form>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="showPaymentDialog = false">Cancel</v-btn>
          <v-btn
            color="primary"
            :loading="paymentLoading"
            :disabled="!paymentValid"
            @click="savePayment"
          >
            Add Payment
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { useSnackbar } from '@/composables/useSnackbar';
import { apiClient } from '@/utils/apiClient';

const { showSnackbar } = useSnackbar();

// Data
const loading = ref(false);
const invoices = ref([]);
const showForm = ref(false);
const selectedInvoice = ref(null);
const showPaymentDialog = ref(false);
const paymentValid = ref(false);
const paymentLoading = ref(false);

const filters = reactive({
  status: null,
  payment_status: null
});

const payment = reactive({
  payment_date: new Date().toISOString().split('T')[0],
  amount: 0,
  payment_method: '',
  reference: '',
  notes: ''
});

// Options
const statusOptions = [
  { title: 'Draft', value: 'draft' },
  { title: 'Sent', value: 'sent' },
  { title: 'Paid', value: 'paid' },
  { title: 'Overdue', value: 'overdue' },
  { title: 'Cancelled', value: 'cancelled' }
];

const paymentStatusOptions = [
  { title: 'Unpaid', value: 'unpaid' },
  { title: 'Partial', value: 'partial' },
  { title: 'Paid', value: 'paid' }
];

const paymentMethods = [
  'Cash', 'Check', 'Bank Transfer', 'Credit Card', 'PayPal', 'Other'
];

const headers = [
  { title: 'Invoice #', key: 'invoice_number', sortable: true },
  { title: 'Customer', key: 'customer_name', sortable: true },
  { title: 'Issue Date', key: 'issue_date', sortable: true },
  { title: 'Due Date', key: 'due_date', sortable: true },
  { title: 'Amount', key: 'total_amount', sortable: true },
  { title: 'Status', key: 'status', sortable: true },
  { title: 'Payment', key: 'payment_status', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false }
];

// Methods
const fetchInvoices = async () => {
  loading.value = true;
  try {
    const params = new URLSearchParams();
    if (filters.status) params.append('status', filters.status);
    if (filters.payment_status) params.append('payment_status', filters.payment_status);
    
    const response = await apiClient.get(`/api/v1/invoicing/?${params}`);
    invoices.value = response.data;
  } catch (error) {
    showSnackbar('Failed to load invoices', 'error');
    console.error('Error fetching invoices:', error);
  } finally {
    loading.value = false;
  }
};

const createInvoice = () => {
  selectedInvoice.value = null;
  showForm.value = true;
};

const editInvoice = (invoice) => {
  selectedInvoice.value = invoice;
  showForm.value = true;
};

const viewInvoice = (invoice) => {
  // Navigate to invoice detail view
  console.log('View invoice:', invoice);
};

const sendInvoice = async (invoice) => {
  try {
    await apiClient.post(`/api/v1/invoicing/${invoice.id}/send`);
    showSnackbar('Invoice sent successfully', 'success');
    fetchInvoices();
  } catch (error) {
    showSnackbar('Failed to send invoice', 'error');
    console.error('Error sending invoice:', error);
  }
};

const addPayment = (invoice) => {
  selectedInvoice.value = invoice;
  payment.amount = invoice.total_amount;
  showPaymentDialog.value = true;
};

const savePayment = async () => {
  paymentLoading.value = true;
  try {
    await apiClient.post(`/api/v1/invoicing/${selectedInvoice.value.id}/payments`, payment);
    showSnackbar('Payment added successfully', 'success');
    showPaymentDialog.value = false;
    fetchInvoices();
  } catch (error) {
    showSnackbar('Failed to add payment', 'error');
    console.error('Error adding payment:', error);
  } finally {
    paymentLoading.value = false;
  }
};

const onInvoiceSaved = () => {
  showForm.value = false;
  fetchInvoices();
};

const getStatusColor = (status) => {
  const colors = {
    draft: 'grey',
    sent: 'blue',
    paid: 'success',
    overdue: 'error',
    cancelled: 'warning'
  };
  return colors[status] || 'grey';
};

const getPaymentStatusColor = (status) => {
  const colors = {
    unpaid: 'error',
    partial: 'warning',
    paid: 'success'
  };
  return colors[status] || 'grey';
};

// Lifecycle
onMounted(() => {
  fetchInvoices();
});
</script>

<style scoped>
.invoice-list {
  padding: 16px;
}
</style>