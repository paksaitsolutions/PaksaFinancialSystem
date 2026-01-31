<template>
  <div class="payment-list">
    <v-card>
      <v-card-title class="d-flex align-center justify-space-between">
        <h2>Payments</h2>
        <v-btn color="primary" prepend-icon="mdi-plus" @click="openCreateDialog">
          New Payment
        </v-btn>
      </v-card-title>
      
      <v-card-text>
        <!-- Search and filters -->
        <v-row>
          <v-col cols="12" sm="3">
            <v-select
              v-model="filters.status"
              label="Status"
              :items="statusOptions"
              density="compact"
              hide-details
              clearable
              @update:model-value="fetchPayments"
            ></v-select>
          </v-col>
          <v-col cols="12" sm="3">
            <v-select
              v-model="filters.vendorId"
              label="Vendor"
              :items="vendors"
              item-title="name"
              item-value="id"
              density="compact"
              hide-details
              clearable
              @update:model-value="fetchPayments"
            ></v-select>
          </v-col>
          <v-col cols="12" sm="3">
            <v-text-field
              v-model="filters.paymentNumber"
              label="Payment Number"
              prepend-inner-icon="mdi-pound"
              density="compact"
              hide-details
              @update:model-value="debouncedFetchPayments"
            ></v-text-field>
          </v-col>
          <v-col cols="12" sm="3">
            <v-btn
              color="secondary"
              variant="outlined"
              prepend-icon="mdi-filter-remove"
              @click="clearFilters"
            >
              Clear
            </v-btn>
          </v-col>
        </v-row>
        
        <v-row class="mt-2">
          <v-col cols="12" sm="3">
            <v-menu
              ref="fromDateMenu"
              v-model="fromDateMenu"
              :close-on-content-click="false"
              transition="scale-transition"
              offset-y
              min-width="auto"
            >
              <template v-slot:activator="{ props }">
                <v-text-field
                  v-model="filters.fromDate"
                  label="From Date"
                  prepend-inner-icon="mdi-calendar"
                  readonly
                  v-bind="props"
                  density="compact"
                  hide-details
                ></v-text-field>
              </template>
              <v-date-picker
                v-model="filters.fromDate"
                @update:model-value="fromDateMenu = false; fetchPayments()"
              ></v-date-picker>
            </v-menu>
          </v-col>
          <v-col cols="12" sm="3">
            <v-menu
              ref="toDateMenu"
              v-model="toDateMenu"
              :close-on-content-click="false"
              transition="scale-transition"
              offset-y
              min-width="auto"
            >
              <template v-slot:activator="{ props }">
                <v-text-field
                  v-model="filters.toDate"
                  label="To Date"
                  prepend-inner-icon="mdi-calendar"
                  readonly
                  v-bind="props"
                  density="compact"
                  hide-details
                ></v-text-field>
              </template>
              <v-date-picker
                v-model="filters.toDate"
                @update:model-value="toDateMenu = false; fetchPayments()"
              ></v-date-picker>
            </v-menu>
          </v-col>
        </v-row>
      </v-card-text>
      
      <!-- Data table -->
      <v-data-table
        v-model:items-per-page="pagination.itemsPerPage"
        :headers="headers"
        :items="payments"
        :loading="loading"
        :server-items-length="pagination.totalItems"
        class="elevation-1"
        @update:options="handleTableUpdate"
      >
        <!-- Status column -->
        <template v-slot:item.status="{ item }">
          <v-chip
            :color="getStatusColor(item.status)"
            size="small"
            text-color="white"
          >
            {{ formatStatus(item.status) }}
          </v-chip>
        </template>
        
        <!-- Amount column -->
        <template v-slot:item.amount="{ item }">
          {{ formatCurrency(item.amount) }}
        </template>
        
        <!-- Date column -->
        <template v-slot:item.payment_date="{ item }">
          {{ formatDate(item.payment_date) }}
        </template>
        
        <!-- Payment method column -->
        <template v-slot:item.payment_method="{ item }">
          {{ formatPaymentMethod(item.payment_method) }}
        </template>
        
        <!-- Actions column -->
        <template v-slot:item.actions="{ item }">
          <v-btn
            icon
            variant="text"
            size="small"
            color="primary"
            @click="viewPayment(item)"
          >
            <v-icon>mdi-eye</v-icon>
          </v-btn>
          <v-btn
            v-if="canEdit(item)"
            icon
            variant="text"
            size="small"
            color="warning"
            @click="editPayment(item)"
          >
            <v-icon>mdi-pencil</v-icon>
          </v-btn>
          <v-btn
            v-if="canVoid(item)"
            icon
            variant="text"
            size="small"
            color="error"
            @click="voidPayment(item)"
          >
            <v-icon>mdi-cancel</v-icon>
          </v-btn>
        </template>
      </v-data-table>
    </v-card>
    
    <!-- Void Dialog -->
    <v-dialog v-model="voidDialog.show" max-width="500px">
      <v-card>
        <v-card-title>Void Payment</v-card-title>
        <v-card-text>
          <p>Are you sure you want to void payment "{{ voidDialog.payment?.payment_number }}"?</p>
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
import { ref, reactive, onMounted, computed } from 'vue';
import { useSnackbar } from '@/composables/useSnackbar';
import { debounce } from '@/utils/debounce';
import { apiClient } from '@/utils/apiClient';

// Props
const props = defineProps({
  defaultFilters: {
    type: Object,
    default: () => ({})
  }
});

// Emits
const emit = defineEmits(['view', 'create']);

// Composables
const { showSnackbar } = useSnackbar();

// Data
const payments = ref([]);
const vendors = ref([]);
const loading = ref(false);
const fromDateMenu = ref(false);
const toDateMenu = ref(false);

// Pagination
const pagination = reactive({
  page: 1,
  itemsPerPage: 10,
  totalItems: 0,
  sortBy: 'payment_date',
  sortDesc: true,
});

// Filters
const filters = reactive({
  status: props.defaultFilters.status || null,
  vendorId: props.defaultFilters.vendorId || null,
  paymentNumber: props.defaultFilters.paymentNumber || '',
  fromDate: props.defaultFilters.fromDate || null,
  toDate: props.defaultFilters.toDate || null,
});

// Dialogs
const voidDialog = reactive({
  show: false,
  payment: null,
  reason: '',
});

// Table headers
const headers = [
  { title: 'Payment #', key: 'payment_number', sortable: true },
  { title: 'Vendor', key: 'vendor.name', sortable: true },
  { title: 'Date', key: 'payment_date', sortable: true },
  { title: 'Method', key: 'payment_method', sortable: true },
  { title: 'Amount', key: 'amount', sortable: true, align: 'end' },
  { title: 'Status', key: 'status', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false, align: 'center' },
];

// Options
const statusOptions = [
  { title: 'Pending', value: 'pending' },
  { title: 'Completed', value: 'completed' },
  { title: 'Voided', value: 'voided' },
];

// Methods
const fetchPayments = async () => {
  loading.value = true;
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.itemsPerPage,
      sort_by: pagination.sortBy,
      sort_order: pagination.sortDesc ? 'desc' : 'asc',
    };
    
    // Add filters
    if (filters.status) params.status = filters.status;
    if (filters.vendorId) params.vendor_id = filters.vendorId;
    if (filters.paymentNumber) params.payment_number = filters.paymentNumber;
    if (filters.fromDate) params.from_date = filters.fromDate;
    if (filters.toDate) params.to_date = filters.toDate;
    
    const response = await apiClient.get('/api/v1/accounts-payable/payments', { params });
    payments.value = response.data;
    pagination.totalItems = response.meta.pagination.total;
  } catch (error) {
    showSnackbar('Failed to load payments', 'error');
    console.error('Error fetching payments:', error);
  } finally {
    loading.value = false;
  }
};

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

const debouncedFetchPayments = debounce(fetchPayments, 300);

const handleTableUpdate = (options) => {
  pagination.page = options.page;
  pagination.itemsPerPage = options.itemsPerPage;
  
  if (options.sortBy.length > 0) {
    pagination.sortBy = options.sortBy[0].key;
    pagination.sortDesc = options.sortBy[0].order === 'desc';
  } else {
    pagination.sortBy = 'payment_date';
    pagination.sortDesc = true;
  }
  
  fetchPayments();
};

const clearFilters = () => {
  filters.status = null;
  filters.vendorId = null;
  filters.paymentNumber = '';
  filters.fromDate = null;
  filters.toDate = null;
  fetchPayments();
};

const openCreateDialog = () => {
  emit('create');
};

const viewPayment = (payment) => {
  emit('view', payment);
};

const editPayment = (payment) => {
  // Navigate to payment edit page
  // router.push({ name: 'payment-edit', params: { id: payment.id } });
};

const voidPayment = (payment) => {
  voidDialog.payment = payment;
  voidDialog.reason = '';
  voidDialog.show = true;
};

const submitVoidAction = async () => {
  if (!voidDialog.payment || !voidDialog.reason) return;
  
  try {
    await apiClient.post(`/api/v1/accounts-payable/payments/${voidDialog.payment.id}/void`, {
      reason: voidDialog.reason
    });
    showSnackbar('Payment voided successfully', 'success');
    fetchPayments();
  } catch (error) {
    showSnackbar('Failed to void payment', 'error');
    console.error('Error voiding payment:', error);
  } finally {
    voidDialog.show = false;
    voidDialog.payment = null;
  }
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

// Permission checks
const canEdit = (payment) => {
  return payment.status === 'pending';
};

const canVoid = (payment) => {
  return payment.status === 'completed';
};

// Lifecycle hooks
onMounted(() => {
  fetchVendors();
  fetchPayments();
});
</script>

<style scoped>
.payment-list {
  padding: 16px;
}
</style>