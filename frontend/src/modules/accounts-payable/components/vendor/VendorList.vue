<template>
  <div class="vendor-list">
    <v-card>
      <v-card-title class="d-flex align-center justify-space-between">
        <h2>Vendors</h2>
        <v-btn color="primary" prepend-icon="mdi-plus" @click="openCreateDialog">
          Add Vendor
        </v-btn>
      </v-card-title>
      
      <v-card-text>
        <!-- Search and filters -->
        <v-row>
          <v-col cols="12" sm="4">
            <v-text-field
              v-model="filters.name"
              label="Search by name"
              prepend-inner-icon="mdi-magnify"
              density="compact"
              hide-details
              @update:model-value="debouncedFetchVendors"
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
              @update:model-value="fetchVendors"
            ></v-select>
          </v-col>
          <v-col cols="12" sm="3">
            <v-select
              v-model="filters.is1099"
              label="1099 Status"
              :items="is1099Options"
              density="compact"
              hide-details
              clearable
              @update:model-value="fetchVendors"
            ></v-select>
          </v-col>
          <v-col cols="12" sm="2">
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
        :items="vendors"
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
            {{ item.status }}
          </v-chip>
        </template>
        
        <!-- 1099 column -->
        <template v-slot:item.is_1099="{ item }">
          <v-icon v-if="item.is_1099" color="success">mdi-check</v-icon>
          <v-icon v-else color="error">mdi-close</v-icon>
        </template>
        
        <!-- Actions column -->
        <template v-slot:item.actions="{ item }">
          <v-btn
            icon
            variant="text"
            size="small"
            color="primary"
            @click="viewVendor(item)"
          >
            <v-icon>mdi-eye</v-icon>
          </v-btn>
          <v-btn
            icon
            variant="text"
            size="small"
            color="warning"
            @click="editVendor(item)"
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
    
    <!-- Create/Edit Dialog -->
    <vendor-form-dialog
      v-model="dialog.show"
      :vendor="selectedVendor"
      :is-edit="dialog.isEdit"
      @saved="handleSaved"
      @closed="dialog.show = false"
    />
    
    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="deleteDialog.show" max-width="500px">
      <v-card>
        <v-card-title>Delete Vendor</v-card-title>
        <v-card-text>
          Are you sure you want to delete vendor "{{ deleteDialog.vendor?.name }}"?
          This action cannot be undone.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" variant="text" @click="deleteDialog.show = false">Cancel</v-btn>
          <v-btn color="error" @click="deleteVendor">Delete</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue';
import { useSnackbar } from '@/composables/useSnackbar';
import { debounce } from '@/utils/debounce';
import VendorFormDialog from './VendorFormDialog.vue';
import vendorService from '@/services/vendorService';
import { useAuthStore } from '@/stores/auth';

// Composables
const { showSnackbar } = useSnackbar();
const authStore = useAuthStore();
const currentCompany = computed(() => authStore.currentCompany);

// Data
const vendors = ref([]);
const loading = ref(false);
const selectedVendor = ref(null);

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
  status: null,
  is1099: null,
});

// Dialogs
const dialog = reactive({
  show: false,
  isEdit: false,
});

const deleteDialog = reactive({
  show: false,
  vendor: null,
});

// Table headers
const headers = [
  { title: 'Code', key: 'code', sortable: true },
  { title: 'Name', key: 'name', sortable: true },
  { title: 'Status', key: 'status', sortable: true },
  { title: '1099', key: 'is_1099', sortable: true },
  { title: 'Phone', key: 'phone', sortable: false },
  { title: 'Email', key: 'email', sortable: false },
  { title: 'Actions', key: 'actions', sortable: false },
];

// Options
const statusOptions = [
  { title: 'Active', value: 'active' },
  { title: 'Inactive', value: 'inactive' },
  { title: 'Hold', value: 'hold' },
  { title: 'Pending Approval', value: 'pending_approval' },
  { title: 'Blocked', value: 'blocked' },
];

const is1099Options = [
  { title: 'Yes', value: true },
  { title: 'No', value: false },
];

// Methods
const fetchVendors = async () => {
  if (!currentCompany.value?.id) return;
  
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
    if (filters.status) params.status = filters.status;
    if (filters.is1099 !== null) params.is_1099 = filters.is1099;
    
    const response = await vendorService.getVendors(currentCompany.value.id, params);
    vendors.value = response.data;
    pagination.totalItems = response.meta?.pagination?.total || response.data.length;
  } catch (error) {
    showSnackbar('Failed to load vendors', 'error');
    console.error('Error fetching vendors:', error);
  } finally {
    loading.value = false;
  }
};

const debouncedFetchVendors = debounce(fetchVendors, 300);

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
  
  fetchVendors();
};

const clearFilters = () => {
  filters.name = '';
  filters.status = null;
  filters.is1099 = null;
  fetchVendors();
};

const openCreateDialog = () => {
  selectedVendor.value = null;
  dialog.isEdit = false;
  dialog.show = true;
};

const viewVendor = (vendor) => {
  // Navigate to vendor detail page
  // router.push({ name: 'vendor-detail', params: { id: vendor.id } });
};

const editVendor = (vendor) => {
  selectedVendor.value = vendor;
  dialog.isEdit = true;
  dialog.show = true;
};

const confirmDelete = (vendor) => {
  deleteDialog.vendor = vendor;
  deleteDialog.show = true;
};

const deleteVendor = async () => {
  if (!deleteDialog.vendor) return;
  
  try {
    await vendorService.deleteVendor(deleteDialog.vendor.id);
    showSnackbar('Vendor deleted successfully', 'success');
    fetchVendors();
  } catch (error) {
    showSnackbar('Failed to delete vendor', 'error');
    console.error('Error deleting vendor:', error);
  } finally {
    deleteDialog.show = false;
    deleteDialog.vendor = null;
  }
};

const handleSaved = () => {
  fetchVendors();
  dialog.show = false;
};

const getStatusColor = (status) => {
  const colors = {
    active: 'success',
    inactive: 'grey',
    hold: 'warning',
    pending_approval: 'info',
    blocked: 'error',
  };
  return colors[status] || 'grey';
};

// Lifecycle hooks
onMounted(() => {
  fetchVendors();
});
</script>

<style scoped>
.vendor-list {
  padding: 16px;
}
</style>