<template>
  <div class="invoice-list">
    <v-card>
      <v-card-title class="d-flex align-center justify-space-between">
        <h2>Invoices</h2>
        <v-btn color="primary" prepend-icon="mdi-plus" @click="openCreateDialog">
          New Invoice
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
              @update:model-value="fetchInvoices"
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
              @update:model-value="fetchInvoices"
            ></v-select>
          </v-col>
          <v-col cols="12" sm="3">
            <v-text-field
              v-model="filters.invoiceNumber"
              label="Invoice Number"
              prepend-inner-icon="mdi-pound"
              density="compact"
              hide-details
              @update:model-value="debouncedFetchInvoices"
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
                @update:model-value="fromDateMenu = false; fetchInvoices()"
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
                @update:model-value="toDateMenu = false; fetchInvoices()"
              ></v-date-picker>
            </v-menu>
          </v-col>
        </v-row>
      </v-card-text>
      
      <!-- Data table -->
      <v-data-table
        v-model:items-per-page="pagination.itemsPerPage"
        :headers="headers"
        :items="invoices"
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
        
        <!-- Amount columns -->
        <template v-slot:item.total_amount="{ item }">
          {{ formatCurrency(item.total_amount) }}
        </template>
        
        <template v-slot:item.balance_due="{ item }">
          {{ formatCurrency(item.balance_due) }}
        </template>
        
        <!-- Date columns -->
        <template v-slot:item.invoice_date="{ item }">
          {{ formatDate(item.invoice_date) }}
        </template>
        
        <template v-slot:item.due_date="{ item }">
          {{ formatDate(item.due_date) }}
        </template>
        
        <!-- Actions column -->
        <template v-slot:item.actions="{ item }">
          <v-btn
            icon
            variant="text"
            size="small"
            color="primary"
            @click="viewInvoice(item)"
          >
            <v-icon>mdi-eye</v-icon>
          </v-btn>
          <v-btn
            v-if="canEdit(item)"
            icon
            variant="text"
            size="small"
            color="warning"
            @click="editInvoice(item)"
          >
            <v-icon>mdi-pencil</v-icon>
          </v-btn>
          <v-btn
            v-if="canSubmit(item)"
            icon
            variant="text"
            size="small"
            color="info"
            @click="submitInvoice(item)"
          >
            <v-icon>mdi-send</v-icon>
          </v-btn>
          <v-btn
            v-if="canApprove(item)"
            icon
            variant="text"
            size="small"
            color="success"
            @click="approveInvoice(item)"
          >
            <v-icon>mdi-check</v-icon>
          </v-btn>
          <v-btn
            v-if="canReject(item)"
            icon
            variant="text"
            size="small"
            color="error"
            @click="rejectInvoice(item)"
          >
            <v-icon>mdi-close</v-icon>
          </v-btn>
          <v-btn
            v-if="canVoid(item)"
            icon
            variant="text"
            size="small"
            color="grey"
            @click="voidInvoice(item)"
          >
            <v-icon>mdi-cancel</v-icon>
          </v-btn>
          <v-btn
            v-if="canDelete(item)"
            icon
            variant="text"
            size="small"
            color="error"
            @click="confirmDelete(item)"
          >
            <v-icon>mdi-delete</v-icon>
          </v-btn>
        </template>
      </v-data-table>
    </v-card>
    
    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="deleteDialog.show" max-width="500px">
      <v-card>
        <v-card-title>Delete Invoice</v-card-title>
        <v-card-text>
          Are you sure you want to delete invoice "{{ deleteDialog.invoice?.invoice_number }}"?
          This action cannot be undone.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" variant="text" @click="deleteDialog.show = false">Cancel</v-btn>
          <v-btn color="error" @click="deleteInvoice">Delete</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
    <!-- Approval Dialog -->
    <v-dialog v-model="approvalDialog.show" max-width="500px">
      <v-card>
        <v-card-title>{{ approvalDialog.action === 'approve' ? 'Approve' : 'Reject' }} Invoice</v-card-title>
        <v-card-text>
          <p>{{ approvalDialog.action === 'approve' ? 'Approve' : 'Reject' }} invoice "{{ approvalDialog.invoice?.invoice_number }}"?</p>
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
          <p>Void invoice "{{ voidDialog.invoice?.invoice_number }}"?</p>
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
import { ref, reactive, onMounted, computed } from 'vue';
import { useSnackbar } from '@/composables/useSnackbar';
import { debounce } from '@/utils/debounce';
import { apiClient } from '@/utils/apiClient';

// Composables
const { showSnackbar } = useSnackbar();

// Data
const invoices = ref([]);
const vendors = ref([]);
const loading = ref(false);
const fromDateMenu = ref(false);
const toDateMenu = ref(false);

// Pagination
const pagination = reactive({
  page: 1,
  itemsPerPage: 10,
  totalItems: 0,
  sortBy: 'invoice_date',
  sortDesc: true,
});

// Filters
const filters = reactive({
  status: null,
  vendorId: null,
  invoiceNumber: '',
  fromDate: null,
  toDate: null,
});

// Dialogs
const deleteDialog = reactive({
  show: false,
  invoice: null,
});

const approvalDialog = reactive({
  show: false,
  invoice: null,
  action: 'approve', // 'approve' or 'reject'
  notes: '',
});

const voidDialog = reactive({
  show: false,
  invoice: null,
  reason: '',
});

// Table headers
const headers = [
  { title: 'Invoice #', key: 'invoice_number', sortable: true },
  { title: 'Vendor', key: 'vendor.name', sortable: true },
  { title: 'Date', key: 'invoice_date', sortable: true },
  { title: 'Due Date', key: 'due_date', sortable: true },
  { title: 'Status', key: 'status', sortable: true },
  { title: 'Total', key: 'total_amount', sortable: true, align: 'end' },
  { title: 'Balance', key: 'balance_due', sortable: true, align: 'end' },
  { title: 'Actions', key: 'actions', sortable: false, align: 'center' },
];

// Options
const statusOptions = [
  { title: 'Draft', value: 'draft' },
  { title: 'Pending', value: 'pending' },
  { title: 'Approved', value: 'approved' },
  { title: 'Paid', value: 'paid' },
  { title: 'Partially Paid', value: 'partially_paid' },
  { title: 'Rejected', value: 'rejected' },
  { title: 'Voided', value: 'voided' },
  { title: 'Cancelled', value: 'cancelled' },
];

// Methods
const fetchInvoices = async () => {
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
    if (filters.invoiceNumber) params.invoice_number = filters.invoiceNumber;
    if (filters.fromDate) params.from_date = filters.fromDate;
    if (filters.toDate) params.to_date = filters.toDate;
    
    const response = await apiClient.get('/api/v1/accounts-payable/invoices', { params });
    invoices.value = response.data;
    pagination.totalItems = response.meta.pagination.total;
  } catch (error) {
    showSnackbar('Failed to load invoices', 'error');
    console.error('Error fetching invoices:', error);
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

const debouncedFetchInvoices = debounce(fetchInvoices, 300);

const handleTableUpdate = (options) => {
  pagination.page = options.page;
  pagination.itemsPerPage = options.itemsPerPage;
  
  if (options.sortBy.length > 0) {
    pagination.sortBy = options.sortBy[0].key;
    pagination.sortDesc = options.sortBy[0].order === 'desc';
  } else {
    pagination.sortBy = 'invoice_date';
    pagination.sortDesc = true;
  }
  
  fetchInvoices();
};

const clearFilters = () => {
  filters.status = null;
  filters.vendorId = null;
  filters.invoiceNumber = '';
  filters.fromDate = null;
  filters.toDate = null;
  fetchInvoices();
};

const openCreateDialog = () => {
  // Navigate to invoice creation page
  // router.push({ name: 'invoice-create' });
};

const viewInvoice = (invoice) => {
  // Navigate to invoice detail page
  // router.push({ name: 'invoice-detail', params: { id: invoice.id } });
};

const editInvoice = (invoice) => {
  // Navigate to invoice edit page
  // router.push({ name: 'invoice-edit', params: { id: invoice.id } });
};

const confirmDelete = (invoice) => {
  deleteDialog.invoice = invoice;
  deleteDialog.show = true;
};

const deleteInvoice = async () => {
  if (!deleteDialog.invoice) return;
  
  try {
    await apiClient.delete(`/api/v1/accounts-payable/invoices/${deleteDialog.invoice.id}`);
    showSnackbar('Invoice deleted successfully', 'success');
    fetchInvoices();
  } catch (error) {
    showSnackbar('Failed to delete invoice', 'error');
    console.error('Error deleting invoice:', error);
  } finally {
    deleteDialog.show = false;
    deleteDialog.invoice = null;
  }
};

const submitInvoice = async (invoice) => {
  try {
    await apiClient.post(`/api/v1/accounts-payable/invoices/${invoice.id}/submit`);
    showSnackbar('Invoice submitted for approval', 'success');
    fetchInvoices();
  } catch (error) {
    showSnackbar('Failed to submit invoice', 'error');
    console.error('Error submitting invoice:', error);
  }
};

const approveInvoice = (invoice) => {
  approvalDialog.invoice = invoice;
  approvalDialog.action = 'approve';
  approvalDialog.notes = '';
  approvalDialog.show = true;
};

const rejectInvoice = (invoice) => {
  approvalDialog.invoice = invoice;
  approvalDialog.action = 'reject';
  approvalDialog.notes = '';
  approvalDialog.show = true;
};

const submitApprovalAction = async () => {
  if (!approvalDialog.invoice) return;
  
  try {
    const endpoint = `/api/v1/accounts-payable/invoices/${approvalDialog.invoice.id}/${approvalDialog.action}`;
    const payload = {
      approved_by_id: '00000000-0000-0000-0000-000000000000', // Replace with actual user ID
      notes: approvalDialog.notes
    };
    
    await apiClient.post(endpoint, payload);
    showSnackbar(`Invoice ${approvalDialog.action === 'approve' ? 'approved' : 'rejected'} successfully`, 'success');
    fetchInvoices();
  } catch (error) {
    showSnackbar(`Failed to ${approvalDialog.action} invoice`, 'error');
    console.error(`Error ${approvalDialog.action}ing invoice:`, error);
  } finally {
    approvalDialog.show = false;
    approvalDialog.invoice = null;
  }
};

const voidInvoice = (invoice) => {
  voidDialog.invoice = invoice;
  voidDialog.reason = '';
  voidDialog.show = true;
};

const submitVoidAction = async () => {
  if (!voidDialog.invoice || !voidDialog.reason) return;
  
  try {
    await apiClient.post(`/api/v1/accounts-payable/invoices/${voidDialog.invoice.id}/void`, {
      reason: voidDialog.reason
    });
    showSnackbar('Invoice voided successfully', 'success');
    fetchInvoices();
  } catch (error) {
    showSnackbar('Failed to void invoice', 'error');
    console.error('Error voiding invoice:', error);
  } finally {
    voidDialog.show = false;
    voidDialog.invoice = null;
  }
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

// Permission checks
const canEdit = (invoice) => {
  return ['draft', 'rejected'].includes(invoice.status);
};

const canSubmit = (invoice) => {
  return invoice.status === 'draft';
};

const canApprove = (invoice) => {
  return invoice.status === 'pending';
};

const canReject = (invoice) => {
  return invoice.status === 'pending';
};

const canVoid = (invoice) => {
  return ['draft', 'pending', 'approved', 'rejected'].includes(invoice.status);
};

const canDelete = (invoice) => {
  return invoice.status === 'draft';
};

// Lifecycle hooks
onMounted(() => {
  fetchVendors();
  fetchInvoices();
});
</script>

<style scoped>
.invoice-list {
  padding: 16px;
}
</style>