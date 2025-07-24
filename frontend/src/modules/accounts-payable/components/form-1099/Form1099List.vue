<template>
  <div class="form-1099-list">
    <v-card>
      <v-card-title class="d-flex align-center justify-space-between">
        <h2>1099 Forms</h2>
        <div>
          <v-btn color="info" class="mr-2" prepend-icon="mdi-auto-fix" @click="openGenerateDialog">
            Generate Forms
          </v-btn>
          <v-btn color="primary" prepend-icon="mdi-plus" @click="openCreateDialog">
            New 1099 Form
          </v-btn>
        </div>
      </v-card-title>
      
      <v-card-text>
        <!-- Search and filters -->
        <v-row>
          <v-col cols="12" sm="3">
            <v-select
              v-model="filters.taxYear"
              label="Tax Year"
              :items="taxYearOptions"
              density="compact"
              hide-details
              clearable
              @update:model-value="fetchForms"
            ></v-select>
          </v-col>
          <v-col cols="12" sm="3">
            <v-select
              v-model="filters.status"
              label="Status"
              :items="statusOptions"
              density="compact"
              hide-details
              clearable
              @update:model-value="fetchForms"
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
              @update:model-value="fetchForms"
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
        :items="forms"
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
        
        <!-- Form type column -->
        <template v-slot:item.form_type="{ item }">
          <v-chip size="small" variant="outlined">
            {{ item.form_type }}
          </v-chip>
        </template>
        
        <!-- Amount column -->
        <template v-slot:item.total_amount="{ item }">
          {{ formatCurrency(item.total_amount) }}
        </template>
        
        <!-- Filed date column -->
        <template v-slot:item.filed_date="{ item }">
          {{ item.filed_date ? formatDate(item.filed_date) : 'Not Filed' }}
        </template>
        
        <!-- Actions column -->
        <template v-slot:item.actions="{ item }">
          <v-btn
            icon
            variant="text"
            size="small"
            color="primary"
            @click="viewForm(item)"
          >
            <v-icon>mdi-eye</v-icon>
          </v-btn>
          <v-btn
            v-if="canEdit(item)"
            icon
            variant="text"
            size="small"
            color="warning"
            @click="editForm(item)"
          >
            <v-icon>mdi-pencil</v-icon>
          </v-btn>
          <v-btn
            v-if="canFile(item)"
            icon
            variant="text"
            size="small"
            color="success"
            @click="fileForm(item)"
          >
            <v-icon>mdi-file-send</v-icon>
          </v-btn>
          <v-btn
            v-if="canVoid(item)"
            icon
            variant="text"
            size="small"
            color="error"
            @click="voidForm(item)"
          >
            <v-icon>mdi-cancel</v-icon>
          </v-btn>
          <v-btn
            icon
            variant="text"
            size="small"
            color="info"
            @click="printForm(item)"
          >
            <v-icon>mdi-printer</v-icon>
          </v-btn>
        </template>
      </v-data-table>
    </v-card>
    
    <!-- Generate Dialog -->
    <v-dialog v-model="generateDialog.show" max-width="600px">
      <v-card>
        <v-card-title>Generate 1099 Forms</v-card-title>
        <v-card-text>
          <v-form ref="generateForm" v-model="generateDialog.valid">
            <v-row>
              <v-col cols="12" md="6">
                <v-select
                  v-model="generateDialog.taxYear"
                  label="Tax Year*"
                  :items="taxYearOptions"
                  :rules="[v => !!v || 'Tax year is required']"
                  required
                ></v-select>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="generateDialog.minimumAmount"
                  label="Minimum Amount"
                  type="number"
                  step="0.01"
                  min="0"
                  hint="Only generate forms for vendors with payments above this amount"
                ></v-text-field>
              </v-col>
              <v-col cols="12">
                <v-select
                  v-model="generateDialog.vendorIds"
                  label="Vendors (Optional)"
                  :items="vendors"
                  item-title="name"
                  item-value="id"
                  multiple
                  chips
                  hint="Leave empty to generate for all 1099 vendors"
                ></v-select>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" variant="text" @click="generateDialog.show = false">Cancel</v-btn>
          <v-btn
            color="primary"
            :loading="generateDialog.loading"
            :disabled="!generateDialog.valid"
            @click="generateForms"
          >
            Generate Forms
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
    <!-- Void Dialog -->
    <v-dialog v-model="voidDialog.show" max-width="500px">
      <v-card>
        <v-card-title>Void 1099 Form</v-card-title>
        <v-card-text>
          <p>Are you sure you want to void this 1099 form?</p>
          <p class="text-warning">This action cannot be undone.</p>
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
            Void Form
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue';
import { useSnackbar } from '@/composables/useSnackbar';
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
const emit = defineEmits(['view', 'create']);

// Composables
const { showSnackbar } = useSnackbar();

// Data
const forms = ref([]);
const vendors = ref([]);
const loading = ref(false);

// Pagination
const pagination = reactive({
  page: 1,
  itemsPerPage: 10,
  totalItems: 0,
  sortBy: 'tax_year',
  sortDesc: true,
});

// Filters
const filters = reactive({
  taxYear: props.defaultFilters.taxYear || new Date().getFullYear(),
  status: props.defaultFilters.status || null,
  vendorId: props.defaultFilters.vendorId || null,
});

// Dialogs
const generateDialog = reactive({
  show: false,
  valid: false,
  loading: false,
  taxYear: new Date().getFullYear(),
  minimumAmount: 600,
  vendorIds: [],
});

const voidDialog = reactive({
  show: false,
  form: null,
  reason: '',
});

// Table headers
const headers = [
  { title: 'Tax Year', key: 'tax_year', sortable: true },
  { title: 'Vendor', key: 'vendor.name', sortable: true },
  { title: 'Form Type', key: 'form_type', sortable: true },
  { title: 'Total Amount', key: 'total_amount', sortable: true, align: 'end' },
  { title: 'Status', key: 'status', sortable: true },
  { title: 'Filed Date', key: 'filed_date', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false, align: 'center' },
];

// Options
const currentYear = new Date().getFullYear();
const taxYearOptions = Array.from({ length: 10 }, (_, i) => currentYear - i);

const statusOptions = [
  { title: 'Draft', value: 'draft' },
  { title: 'Ready', value: 'ready' },
  { title: 'Filed', value: 'filed' },
  { title: 'Corrected', value: 'corrected' },
  { title: 'Voided', value: 'voided' },
];

// Methods
const fetchForms = async () => {
  loading.value = true;
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.itemsPerPage,
      sort_by: pagination.sortBy,
      sort_order: pagination.sortDesc ? 'desc' : 'asc',
    };
    
    // Add filters
    if (filters.taxYear) params.tax_year = filters.taxYear;
    if (filters.status) params.status = filters.status;
    if (filters.vendorId) params.vendor_id = filters.vendorId;
    
    const response = await apiClient.get('/api/v1/accounts-payable/1099', { params });
    forms.value = response.data;
    pagination.totalItems = response.meta.pagination.total;
  } catch (error) {
    showSnackbar('Failed to load 1099 forms', 'error');
    console.error('Error fetching 1099 forms:', error);
  } finally {
    loading.value = false;
  }
};

const fetchVendors = async () => {
  try {
    const response = await apiClient.get('/api/v1/accounts-payable/vendors', { 
      params: { page_size: 100, is_1099: true } 
    });
    vendors.value = response.data;
  } catch (error) {
    console.error('Error fetching vendors:', error);
  }
};

const handleTableUpdate = (options) => {
  pagination.page = options.page;
  pagination.itemsPerPage = options.itemsPerPage;
  
  if (options.sortBy.length > 0) {
    pagination.sortBy = options.sortBy[0].key;
    pagination.sortDesc = options.sortBy[0].order === 'desc';
  } else {
    pagination.sortBy = 'tax_year';
    pagination.sortDesc = true;
  }
  
  fetchForms();
};

const clearFilters = () => {
  filters.taxYear = new Date().getFullYear();
  filters.status = null;
  filters.vendorId = null;
  fetchForms();
};

const openCreateDialog = () => {
  emit('create');
};

const openGenerateDialog = () => {
  generateDialog.taxYear = new Date().getFullYear();
  generateDialog.minimumAmount = 600;
  generateDialog.vendorIds = [];
  generateDialog.show = true;
};

const generateForms = async () => {
  if (!generateDialog.valid) return;
  
  generateDialog.loading = true;
  try {
    const payload = {
      tax_year: generateDialog.taxYear,
      minimum_amount: Number(generateDialog.minimumAmount),
      vendor_ids: generateDialog.vendorIds.length > 0 ? generateDialog.vendorIds : null,
    };
    
    const response = await apiClient.post('/api/v1/accounts-payable/1099/generate', payload);
    showSnackbar(`Generated ${response.data.length} 1099 forms`, 'success');
    fetchForms();
  } catch (error) {
    showSnackbar('Failed to generate 1099 forms', 'error');
    console.error('Error generating 1099 forms:', error);
  } finally {
    generateDialog.loading = false;
    generateDialog.show = false;
  }
};

const viewForm = (form) => {
  emit('view', form);
};

const editForm = (form) => {
  // Navigate to form edit page
  // router.push({ name: '1099-edit', params: { id: form.id } });
};

const fileForm = async (form) => {
  try {
    await apiClient.post(`/api/v1/accounts-payable/1099/${form.id}/file`);
    showSnackbar('1099 form filed successfully', 'success');
    fetchForms();
  } catch (error) {
    showSnackbar('Failed to file 1099 form', 'error');
    console.error('Error filing 1099 form:', error);
  }
};

const voidForm = (form) => {
  voidDialog.form = form;
  voidDialog.reason = '';
  voidDialog.show = true;
};

const submitVoidAction = async () => {
  if (!voidDialog.form || !voidDialog.reason) return;
  
  try {
    await apiClient.post(`/api/v1/accounts-payable/1099/${voidDialog.form.id}/void`, {
      reason: voidDialog.reason
    });
    showSnackbar('1099 form voided successfully', 'success');
    fetchForms();
  } catch (error) {
    showSnackbar('Failed to void 1099 form', 'error');
    console.error('Error voiding 1099 form:', error);
  } finally {
    voidDialog.show = false;
    voidDialog.form = null;
  }
};

const printForm = (form) => {
  // Implement print functionality
  window.print();
};

// Helper methods
const getStatusColor = (status) => {
  const colors = {
    draft: 'grey',
    ready: 'info',
    filed: 'success',
    corrected: 'warning',
    voided: 'error',
  };
  return colors[status] || 'grey';
};

const formatStatus = (status) => {
  return status.charAt(0).toUpperCase() + status.slice(1);
};

// Permission checks
const canEdit = (form) => {
  return ['draft', 'ready'].includes(form.status);
};

const canFile = (form) => {
  return form.status === 'ready';
};

const canVoid = (form) => {
  return ['draft', 'ready', 'filed'].includes(form.status);
};

// Lifecycle hooks
onMounted(() => {
  fetchVendors();
  fetchForms();
});
</script>

<style scoped>
.form-1099-list {
  padding: 16px;
}
</style>