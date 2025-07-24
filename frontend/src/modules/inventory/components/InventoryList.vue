<template>
  <div class="inventory-list">
    <v-card>
      <v-card-title class="d-flex align-center justify-space-between">
        <h2>Inventory Items</h2>
        <div>
          <v-btn color="info" class="mr-2" prepend-icon="mdi-barcode-scan" @click="showBarcodeScanner = true">
            Scan Barcode
          </v-btn>
          <v-btn color="primary" prepend-icon="mdi-plus" @click="openCreateDialog">
            Add Item
          </v-btn>
        </div>
      </v-card-title>
      
      <v-card-text>
        <!-- Search and filters -->
        <v-row>
          <v-col cols="12" sm="3">
            <v-text-field
              v-model="filters.name"
              label="Search by name"
              prepend-inner-icon="mdi-magnify"
              density="compact"
              hide-details
              @update:model-value="debouncedFetchItems"
            ></v-text-field>
          </v-col>
          <v-col cols="12" sm="3">
            <v-text-field
              v-model="filters.sku"
              label="Search by SKU"
              prepend-inner-icon="mdi-barcode"
              density="compact"
              hide-details
              @update:model-value="debouncedFetchItems"
            ></v-text-field>
          </v-col>
          <v-col cols="12" sm="3">
            <v-select
              v-model="filters.status"
              label="Status"
              :items="statusOptions"
              density="compact"
              hide-details
              clearable
              @update:model-value="fetchItems"
            ></v-select>
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
        :items="items"
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
        
        <!-- Quantity columns -->
        <template v-slot:item.quantity_on_hand="{ item }">
          {{ formatQuantity(item.quantity_on_hand) }}
        </template>
        
        <template v-slot:item.unit_cost="{ item }">
          {{ formatCurrency(item.unit_cost) }}
        </template>
        
        <!-- Actions column -->
        <template v-slot:item.actions="{ item }">
          <v-btn
            icon
            variant="text"
            size="small"
            color="primary"
            @click="viewItem(item)"
          >
            <v-icon>mdi-eye</v-icon>
          </v-btn>
          <v-btn
            icon
            variant="text"
            size="small"
            color="warning"
            @click="editItem(item)"
          >
            <v-icon>mdi-pencil</v-icon>
          </v-btn>
          <v-btn
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
        <v-card-title>Delete Inventory Item</v-card-title>
        <v-card-text>
          Are you sure you want to delete item "{{ deleteDialog.item?.name }}"?
          This action cannot be undone.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" variant="text" @click="deleteDialog.show = false">Cancel</v-btn>
          <v-btn color="error" @click="deleteItem">Delete</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
    <!-- Barcode Scanner Dialog -->
    <v-dialog v-model="showBarcodeScanner" max-width="700px">
      <barcode-scanner
        @close="showBarcodeScanner = false"
        @item-selected="handleItemSelected"
      />
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { useSnackbar } from '@/composables/useSnackbar';
import { debounce } from '@/utils/debounce';
import { formatCurrency } from '@/utils/formatters';
import { apiClient } from '@/utils/apiClient';
import BarcodeScanner from './BarcodeScanner.vue';

// Emits
const emit = defineEmits(['view', 'create']);

// Composables
const { showSnackbar } = useSnackbar();

// Data
const items = ref([]);
const loading = ref(false);
const showBarcodeScanner = ref(false);

// Pagination
const pagination = reactive({
  page: 1,
  itemsPerPage: 10,
  totalItems: 0,
  sortBy: 'name',
  sortDesc: false,
});

// Filters
const filters = reactive({
  name: '',
  sku: '',
  status: null,
});

// Dialogs
const deleteDialog = reactive({
  show: false,
  item: null,
});

// Table headers
const headers = [
  { title: 'SKU', key: 'sku', sortable: true },
  { title: 'Barcode', key: 'barcode', sortable: true },
  { title: 'Name', key: 'name', sortable: true },
  { title: 'Status', key: 'status', sortable: true },
  { title: 'On Hand', key: 'quantity_on_hand', sortable: true, align: 'end' },
  { title: 'Unit Cost', key: 'unit_cost', sortable: true, align: 'end' },
  { title: 'UOM', key: 'unit_of_measure', sortable: false },
  { title: 'Actions', key: 'actions', sortable: false, align: 'center' },
];

// Options
const statusOptions = [
  { title: 'Active', value: 'active' },
  { title: 'Inactive', value: 'inactive' },
  { title: 'Discontinued', value: 'discontinued' },
];

// Methods
const fetchItems = async () => {
  loading.value = true;
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.itemsPerPage,
      sort_by: pagination.sortBy,
      sort_order: pagination.sortDesc ? 'desc' : 'asc',
    };
    
    // Add filters
    if (filters.name) params.name = filters.name;
    if (filters.sku) params.sku = filters.sku;
    if (filters.status) params.status = filters.status;
    
    const response = await apiClient.get('/api/v1/inventory/items', { params });
    items.value = response.data;
    pagination.totalItems = response.meta.pagination.total;
  } catch (error) {
    showSnackbar('Failed to load inventory items', 'error');
    console.error('Error fetching inventory items:', error);
  } finally {
    loading.value = false;
  }
};

const debouncedFetchItems = debounce(fetchItems, 300);

const handleTableUpdate = (options) => {
  pagination.page = options.page;
  pagination.itemsPerPage = options.itemsPerPage;
  
  if (options.sortBy.length > 0) {
    pagination.sortBy = options.sortBy[0].key;
    pagination.sortDesc = options.sortBy[0].order === 'desc';
  } else {
    pagination.sortBy = 'name';
    pagination.sortDesc = false;
  }
  
  fetchItems();
};

const clearFilters = () => {
  filters.name = '';
  filters.sku = '';
  filters.status = null;
  fetchItems();
};

const openCreateDialog = () => {
  emit('create');
};

const viewItem = (item) => {
  emit('view', item);
};

const editItem = (item) => {
  // Navigate to item edit page
  // router.push({ name: 'inventory-edit', params: { id: item.id } });
};

const confirmDelete = (item) => {
  deleteDialog.item = item;
  deleteDialog.show = true;
};

const deleteItem = async () => {
  if (!deleteDialog.item) return;
  
  try {
    await apiClient.delete(`/api/v1/inventory/items/${deleteDialog.item.id}`);
    showSnackbar('Inventory item deleted successfully', 'success');
    fetchItems();
  } catch (error) {
    showSnackbar('Failed to delete inventory item', 'error');
    console.error('Error deleting inventory item:', error);
  } finally {
    deleteDialog.show = false;
    deleteDialog.item = null;
  }
};

// Helper methods
const getStatusColor = (status) => {
  const colors = {
    active: 'success',
    inactive: 'grey',
    discontinued: 'error',
  };
  return colors[status] || 'grey';
};

const formatStatus = (status) => {
  return status.charAt(0).toUpperCase() + status.slice(1);
};

const formatQuantity = (quantity) => {
  return Number(quantity).toLocaleString();
};

const handleItemSelected = (item) => {
  showSnackbar(`Item found: ${item.name}`, 'success');
  viewItem(item);
};

// Lifecycle hooks
onMounted(() => {
  fetchItems();
});
</script>

<style scoped>
.inventory-list {
  padding: 16px;
}
</style>