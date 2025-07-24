<template>
  <div class="transaction-history">
    <v-card>
      <v-card-title class="d-flex align-center justify-space-between">
        <h3>Transaction History</h3>
        <v-btn
          color="secondary"
          prepend-icon="mdi-download"
          @click="exportTransactions"
        >
          Export
        </v-btn>
      </v-card-title>
      
      <v-card-text>
        <!-- Filters -->
        <v-row>
          <v-col cols="12" md="3">
            <v-select
              v-model="filters.item_id"
              label="Item"
              :items="items"
              item-title="name"
              item-value="id"
              clearable
              @update:model-value="fetchTransactions"
            ></v-select>
          </v-col>
          
          <v-col cols="12" md="3">
            <v-select
              v-model="filters.location_id"
              label="Location"
              :items="locations"
              item-title="name"
              item-value="id"
              clearable
              @update:model-value="fetchTransactions"
            ></v-select>
          </v-col>
          
          <v-col cols="12" md="3">
            <v-select
              v-model="filters.transaction_type"
              label="Transaction Type"
              :items="transactionTypes"
              clearable
              @update:model-value="fetchTransactions"
            ></v-select>
          </v-col>
          
          <v-col cols="12" md="3">
            <v-btn
              color="secondary"
              variant="outlined"
              prepend-icon="mdi-filter-remove"
              @click="clearFilters"
            >
              Clear Filters
            </v-btn>
          </v-col>
        </v-row>
        
        <v-row>
          <v-col cols="12" md="4">
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
                  v-model="filters.from_date"
                  label="From Date"
                  prepend-inner-icon="mdi-calendar"
                  readonly
                  v-bind="props"
                  clearable
                  @click:clear="filters.from_date = null; fetchTransactions()"
                ></v-text-field>
              </template>
              <v-date-picker
                v-model="filters.from_date"
                @update:model-value="fromDateMenu = false; fetchTransactions()"
              ></v-date-picker>
            </v-menu>
          </v-col>
          
          <v-col cols="12" md="4">
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
                  v-model="filters.to_date"
                  label="To Date"
                  prepend-inner-icon="mdi-calendar"
                  readonly
                  v-bind="props"
                  clearable
                  @click:clear="filters.to_date = null; fetchTransactions()"
                ></v-text-field>
              </template>
              <v-date-picker
                v-model="filters.to_date"
                @update:model-value="toDateMenu = false; fetchTransactions()"
              ></v-date-picker>
            </v-menu>
          </v-col>
          
          <v-col cols="12" md="4">
            <v-btn
              color="primary"
              prepend-icon="mdi-refresh"
              @click="fetchTransactions"
              :loading="loading"
            >
              Refresh
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
      
      <!-- Data table -->
      <v-data-table
        v-model:items-per-page="pagination.itemsPerPage"
        :headers="headers"
        :items="transactions"
        :loading="loading"
        :server-items-length="pagination.totalItems"
        class="elevation-1"
        @update:options="handleTableUpdate"
      >
        <template v-slot:item.transaction_type="{ item }">
          <v-chip
            :color="getTransactionColor(item.transaction_type)"
            size="small"
            text-color="white"
          >
            {{ formatTransactionType(item.transaction_type) }}
          </v-chip>
        </template>
        
        <template v-slot:item.transaction_date="{ item }">
          {{ formatDate(item.transaction_date) }}
        </template>
        
        <template v-slot:item.quantity="{ item }">
          <span :class="getQuantityColor(item.quantity)">
            {{ formatQuantity(item.quantity) }}
          </span>
        </template>
        
        <template v-slot:item.unit_cost="{ item }">
          {{ formatCurrency(item.unit_cost) }}
        </template>
        
        <template v-slot:item.total_cost="{ item }">
          {{ formatCurrency(item.total_cost) }}
        </template>
        
        <template v-slot:item.quantity_before="{ item }">
          {{ formatQuantity(item.quantity_before) }}
        </template>
        
        <template v-slot:item.quantity_after="{ item }">
          {{ formatQuantity(item.quantity_after) }}
        </template>
        
        <template v-slot:item.actions="{ item }">
          <v-btn
            icon
            variant="text"
            size="small"
            color="primary"
            @click="viewTransaction(item)"
          >
            <v-icon>mdi-eye</v-icon>
          </v-btn>
        </template>
      </v-data-table>
    </v-card>
    
    <!-- Transaction Detail Dialog -->
    <v-dialog v-model="detailDialog.show" max-width="600px">
      <v-card v-if="detailDialog.transaction">
        <v-card-title>Transaction Details</v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="12" md="6">
              <div class="mb-2">
                <strong>Transaction Type:</strong>
                <v-chip
                  :color="getTransactionColor(detailDialog.transaction.transaction_type)"
                  size="small"
                  text-color="white"
                  class="ml-2"
                >
                  {{ formatTransactionType(detailDialog.transaction.transaction_type) }}
                </v-chip>
              </div>
              <div class="mb-2"><strong>Date:</strong> {{ formatDate(detailDialog.transaction.transaction_date) }}</div>
              <div class="mb-2"><strong>Reference:</strong> {{ detailDialog.transaction.reference || 'N/A' }}</div>
            </v-col>
            <v-col cols="12" md="6">
              <div class="mb-2"><strong>Item:</strong> {{ detailDialog.transaction.item_name }} ({{ detailDialog.transaction.item_sku }})</div>
              <div class="mb-2"><strong>Location:</strong> {{ detailDialog.transaction.location_name }}</div>
            </v-col>
          </v-row>
          
          <v-divider class="my-4"></v-divider>
          
          <v-row>
            <v-col cols="12" md="4">
              <div class="text-center">
                <div class="text-h6">{{ formatQuantity(detailDialog.transaction.quantity) }}</div>
                <div class="text-caption">Quantity</div>
              </div>
            </v-col>
            <v-col cols="12" md="4">
              <div class="text-center">
                <div class="text-h6">{{ formatCurrency(detailDialog.transaction.unit_cost) }}</div>
                <div class="text-caption">Unit Cost</div>
              </div>
            </v-col>
            <v-col cols="12" md="4">
              <div class="text-center">
                <div class="text-h6">{{ formatCurrency(detailDialog.transaction.total_cost) }}</div>
                <div class="text-caption">Total Cost</div>
              </div>
            </v-col>
          </v-row>
          
          <v-divider class="my-4"></v-divider>
          
          <v-row>
            <v-col cols="12" md="6">
              <div class="text-center">
                <div class="text-h6">{{ formatQuantity(detailDialog.transaction.quantity_before) }}</div>
                <div class="text-caption">Quantity Before</div>
              </div>
            </v-col>
            <v-col cols="12" md="6">
              <div class="text-center">
                <div class="text-h6">{{ formatQuantity(detailDialog.transaction.quantity_after) }}</div>
                <div class="text-caption">Quantity After</div>
              </div>
            </v-col>
          </v-row>
          
          <div v-if="detailDialog.transaction.notes" class="mt-4">
            <strong>Notes:</strong>
            <div class="mt-2 pa-3 bg-grey-lighten-4 rounded">
              {{ detailDialog.transaction.notes }}
            </div>
          </div>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" @click="detailDialog.show = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { useSnackbar } from '@/composables/useSnackbar';
import { formatCurrency, formatDate } from '@/utils/formatters';
import { apiClient } from '@/utils/apiClient';

// Composables
const { showSnackbar } = useSnackbar();

// Data
const transactions = ref([]);
const items = ref([]);
const locations = ref([]);
const loading = ref(false);
const fromDateMenu = ref(false);
const toDateMenu = ref(false);

// Pagination
const pagination = reactive({
  page: 1,
  itemsPerPage: 20,
  totalItems: 0,
  sortBy: 'transaction_date',
  sortDesc: true,
});

// Filters
const filters = reactive({
  item_id: null,
  location_id: null,
  transaction_type: null,
  from_date: null,
  to_date: null,
});

// Dialog
const detailDialog = reactive({
  show: false,
  transaction: null,
});

// Table headers
const headers = [
  { title: 'Date', key: 'transaction_date', sortable: true },
  { title: 'Type', key: 'transaction_type', sortable: true },
  { title: 'Item', key: 'item_name', sortable: false },
  { title: 'Location', key: 'location_name', sortable: false },
  { title: 'Quantity', key: 'quantity', sortable: true, align: 'end' },
  { title: 'Unit Cost', key: 'unit_cost', sortable: true, align: 'end' },
  { title: 'Total Cost', key: 'total_cost', sortable: true, align: 'end' },
  { title: 'Before', key: 'quantity_before', sortable: false, align: 'end' },
  { title: 'After', key: 'quantity_after', sortable: false, align: 'end' },
  { title: 'Reference', key: 'reference', sortable: false },
  { title: 'Actions', key: 'actions', sortable: false, align: 'center' },
];

// Transaction types
const transactionTypes = [
  { title: 'Receipt', value: 'receipt' },
  { title: 'Issue', value: 'issue' },
  { title: 'Adjustment', value: 'adjustment' },
  { title: 'Transfer', value: 'transfer' },
];

// Methods
const fetchTransactions = async () => {
  loading.value = true;
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.itemsPerPage,
      sort_by: pagination.sortBy,
      sort_order: pagination.sortDesc ? 'desc' : 'asc',
    };
    
    // Add filters
    Object.keys(filters).forEach(key => {
      if (filters[key] !== null && filters[key] !== '') {
        params[key] = filters[key];
      }
    });
    
    const response = await apiClient.get('/api/v1/inventory/transactions', { params });
    transactions.value = response.data;
    pagination.totalItems = response.meta.pagination.total;
  } catch (error) {
    showSnackbar('Failed to load transactions', 'error');
    console.error('Error fetching transactions:', error);
  } finally {
    loading.value = false;
  }
};

const fetchItems = async () => {
  try {
    const response = await apiClient.get('/api/v1/inventory/items');
    items.value = response.data;
  } catch (error) {
    console.error('Error fetching items:', error);
  }
};

const fetchLocations = async () => {
  try {
    const response = await apiClient.get('/api/v1/inventory/locations');
    locations.value = response.data;
  } catch (error) {
    console.error('Error fetching locations:', error);
  }
};

const handleTableUpdate = (options) => {
  pagination.page = options.page;
  pagination.itemsPerPage = options.itemsPerPage;
  
  if (options.sortBy.length > 0) {
    pagination.sortBy = options.sortBy[0].key;
    pagination.sortDesc = options.sortBy[0].order === 'desc';
  } else {
    pagination.sortBy = 'transaction_date';
    pagination.sortDesc = true;
  }
  
  fetchTransactions();
};

const clearFilters = () => {
  Object.keys(filters).forEach(key => {
    filters[key] = null;
  });
  fetchTransactions();
};

const viewTransaction = (transaction) => {
  detailDialog.transaction = transaction;
  detailDialog.show = true;
};

const exportTransactions = () => {
  showSnackbar('Export functionality coming soon', 'info');
};

// Helper methods
const formatQuantity = (quantity) => {
  return Number(quantity || 0).toLocaleString();
};

const formatTransactionType = (type) => {
  const types = {
    receipt: 'Receipt',
    issue: 'Issue',
    adjustment: 'Adjustment',
    transfer: 'Transfer',
  };
  return types[type] || type;
};

const getTransactionColor = (type) => {
  const colors = {
    receipt: 'success',
    issue: 'error',
    adjustment: 'warning',
    transfer: 'info',
  };
  return colors[type] || 'grey';
};

const getQuantityColor = (quantity) => {
  const num = Number(quantity || 0);
  if (num > 0) return 'text-success';
  if (num < 0) return 'text-error';
  return '';
};

// Lifecycle hooks
onMounted(() => {
  fetchTransactions();
  fetchItems();
  fetchLocations();
});
</script>

<style scoped>
.transaction-history {
  padding: 16px;
}
</style>