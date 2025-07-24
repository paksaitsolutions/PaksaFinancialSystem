<template>
  <div class="credit-memo-list">
    <v-card>
      <v-card-title class="d-flex align-center justify-space-between">
        <h2>Credit Memos</h2>
        <v-btn color="primary" prepend-icon="mdi-plus" @click="openCreateDialog">
          New Credit Memo
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
              @update:model-value="fetchCreditMemos"
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
              @update:model-value="fetchCreditMemos"
            ></v-select>
          </v-col>
          <v-col cols="12" sm="3">
            <v-text-field
              v-model="filters.creditMemoNumber"
              label="Credit Memo Number"
              prepend-inner-icon="mdi-pound"
              density="compact"
              hide-details
              @update:model-value="debouncedFetchCreditMemos"
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
      </v-card-text>
      
      <!-- Data table -->
      <v-data-table
        v-model:items-per-page="pagination.itemsPerPage"
        :headers="headers"
        :items="creditMemos"
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
        <template v-slot:item.amount="{ item }">
          {{ formatCurrency(item.amount) }}
        </template>
        
        <template v-slot:item.applied_amount="{ item }">
          {{ formatCurrency(item.applied_amount) }}
        </template>
        
        <template v-slot:item.remaining_amount="{ item }">
          {{ formatCurrency(item.remaining_amount) }}
        </template>
        
        <!-- Date column -->
        <template v-slot:item.credit_date="{ item }">
          {{ formatDate(item.credit_date) }}
        </template>
        
        <!-- Actions column -->
        <template v-slot:item.actions="{ item }">
          <v-btn
            icon
            variant="text"
            size="small"
            color="primary"
            @click="viewCreditMemo(item)"
          >
            <v-icon>mdi-eye</v-icon>
          </v-btn>
          <v-btn
            v-if="canEdit(item)"
            icon
            variant="text"
            size="small"
            color="warning"
            @click="editCreditMemo(item)"
          >
            <v-icon>mdi-pencil</v-icon>
          </v-btn>
          <v-btn
            v-if="canApply(item)"
            icon
            variant="text"
            size="small"
            color="success"
            @click="applyCreditMemo(item)"
          >
            <v-icon>mdi-check-circle</v-icon>
          </v-btn>
          <v-btn
            v-if="canVoid(item)"
            icon
            variant="text"
            size="small"
            color="error"
            @click="voidCreditMemo(item)"
          >
            <v-icon>mdi-cancel</v-icon>
          </v-btn>
        </template>
      </v-data-table>
    </v-card>
    
    <!-- Void Dialog -->
    <v-dialog v-model="voidDialog.show" max-width="500px">
      <v-card>
        <v-card-title>Void Credit Memo</v-card-title>
        <v-card-text>
          <p>Are you sure you want to void credit memo "{{ voidDialog.creditMemo?.credit_memo_number }}"?</p>
          <p class="text-warning">This will reverse all applications and cannot be undone.</p>
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
            Void Credit Memo
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
import { formatCurrency, formatDate } from '@/utils/formatters';
import { apiClient } from '@/utils/apiClient';

// Props
const props = defineProps({
  defaultFilters: {
    type: Object,
    default: () => ({})
  }
});

// Emits
const emit = defineEmits(['view', 'create', 'apply']);

// Composables
const { showSnackbar } = useSnackbar();

// Data
const creditMemos = ref([]);
const vendors = ref([]);
const loading = ref(false);

// Pagination
const pagination = reactive({
  page: 1,
  itemsPerPage: 10,
  totalItems: 0,
  sortBy: 'credit_date',
  sortDesc: true,
});

// Filters
const filters = reactive({
  status: props.defaultFilters.status || null,
  vendorId: props.defaultFilters.vendorId || null,
  creditMemoNumber: props.defaultFilters.creditMemoNumber || '',
});

// Dialogs
const voidDialog = reactive({
  show: false,
  creditMemo: null,
  reason: '',
});

// Table headers
const headers = [
  { title: 'Credit Memo #', key: 'credit_memo_number', sortable: true },
  { title: 'Vendor', key: 'vendor.name', sortable: true },
  { title: 'Date', key: 'credit_date', sortable: true },
  { title: 'Amount', key: 'amount', sortable: true, align: 'end' },
  { title: 'Applied', key: 'applied_amount', sortable: true, align: 'end' },
  { title: 'Remaining', key: 'remaining_amount', sortable: true, align: 'end' },
  { title: 'Status', key: 'status', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false, align: 'center' },
];

// Options
const statusOptions = [
  { title: 'Active', value: 'active' },
  { title: 'Fully Applied', value: 'fully_applied' },
  { title: 'Expired', value: 'expired' },
  { title: 'Voided', value: 'voided' },
];

// Methods
const fetchCreditMemos = async () => {
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
    if (filters.creditMemoNumber) params.credit_memo_number = filters.creditMemoNumber;
    
    const response = await apiClient.get('/api/v1/accounts-payable/credit-memos', { params });
    creditMemos.value = response.data;
    pagination.totalItems = response.meta.pagination.total;
  } catch (error) {
    showSnackbar('Failed to load credit memos', 'error');
    console.error('Error fetching credit memos:', error);
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

const debouncedFetchCreditMemos = debounce(fetchCreditMemos, 300);

const handleTableUpdate = (options) => {
  pagination.page = options.page;
  pagination.itemsPerPage = options.itemsPerPage;
  
  if (options.sortBy.length > 0) {
    pagination.sortBy = options.sortBy[0].key;
    pagination.sortDesc = options.sortBy[0].order === 'desc';
  } else {
    pagination.sortBy = 'credit_date';
    pagination.sortDesc = true;
  }
  
  fetchCreditMemos();
};

const clearFilters = () => {
  filters.status = null;
  filters.vendorId = null;
  filters.creditMemoNumber = '';
  fetchCreditMemos();
};

const openCreateDialog = () => {
  emit('create');
};

const viewCreditMemo = (creditMemo) => {
  emit('view', creditMemo);
};

const editCreditMemo = (creditMemo) => {
  // Navigate to credit memo edit page
  // router.push({ name: 'credit-memo-edit', params: { id: creditMemo.id } });
};

const applyCreditMemo = (creditMemo) => {
  emit('apply', creditMemo);
};

const voidCreditMemo = (creditMemo) => {
  voidDialog.creditMemo = creditMemo;
  voidDialog.reason = '';
  voidDialog.show = true;
};

const submitVoidAction = async () => {
  if (!voidDialog.creditMemo || !voidDialog.reason) return;
  
  try {
    await apiClient.post(`/api/v1/accounts-payable/credit-memos/${voidDialog.creditMemo.id}/void`, {
      reason: voidDialog.reason
    });
    showSnackbar('Credit memo voided successfully', 'success');
    fetchCreditMemos();
  } catch (error) {
    showSnackbar('Failed to void credit memo', 'error');
    console.error('Error voiding credit memo:', error);
  } finally {
    voidDialog.show = false;
    voidDialog.creditMemo = null;
  }
};

// Helper methods
const getStatusColor = (status) => {
  const colors = {
    active: 'success',
    fully_applied: 'info',
    expired: 'warning',
    voided: 'error',
  };
  return colors[status] || 'grey';
};

const formatStatus = (status) => {
  return status.charAt(0).toUpperCase() + status.slice(1).replace('_', ' ');
};

// Permission checks
const canEdit = (creditMemo) => {
  return creditMemo.status === 'active';
};

const canApply = (creditMemo) => {
  return creditMemo.status === 'active' && creditMemo.remaining_amount > 0;
};

const canVoid = (creditMemo) => {
  return ['active', 'fully_applied'].includes(creditMemo.status);
};

// Lifecycle hooks
onMounted(() => {
  fetchVendors();
  fetchCreditMemos();
});
</script>

<style scoped>
.credit-memo-list {
  padding: 16px;
}
</style>