<template>
  <div class="reconciliation-list">
    <v-card class="mb-6">
      <v-card-title class="d-flex align-center">
        <span class="text-h5">Account Reconciliations</span>
        <v-spacer></v-spacer>
        <v-btn
          color="primary"
          prepend-icon="mdi-plus"
          @click="createReconciliation"
        >
          New Reconciliation
        </v-btn>
      </v-card-title>

      <v-card-text>
        <v-row class="mb-4">
          <v-col cols="12" md="4">
            <v-select
              v-model="filters.status"
              :items="statusOptions"
              label="Status"
              clearable
              hide-details
              @update:modelValue="fetchReconciliations"
            ></v-select>
          </v-col>
          <v-col cols="12" md="4">
            <v-select
              v-model="filters.accountId"
              :items="accounts"
              item-title="name"
              item-value="id"
              label="Account"
              clearable
              hide-details
              @update:modelValue="fetchReconciliations"
            ></v-select>
          </v-col>
          <v-col cols="12" md="4">
            <v-text-field
              v-model="search"
              label="Search"
              prepend-inner-icon="mdi-magnify"
              clearable
              hide-details
              @update:modelValue="handleSearch"
            ></v-text-field>
          </v-col>
        </v-row>

        <v-data-table
          :headers="headers"
          :items="reconciliations"
          :loading="loading"
          :items-per-page="pagination.itemsPerPage"
          :page="pagination.page"
          :items-length="pagination.total"
          :items-per-page-options="[10, 25, 50, 100]"
          @update:options="handleOptionsChange"
          class="elevation-1"
        >
          <template v-slot:item.status="{ item }">
            <v-chip :color="getStatusColor(item.status)" size="small">
              {{ formatStatus(item.status) }}
            </v-chip>
          </template>

          <template v-slot:item.startDate="{ item }">
            {{ formatDate(item.startDate) }}
          </template>

          <template v-slot:item.endDate="{ item }">
            {{ formatDate(item.endDate) }}
          </template>

          <template v-slot:item.statementBalance="{ item }">
            {{ formatCurrency(item.statementBalance, item.statementCurrency) }}
          </template>

          <template v-slot:item.calculatedBalance="{ item }">
            {{ formatCurrency(item.calculatedBalance, item.statementCurrency) }}
          </template>

          <template v-slot:item.difference="{ item }">
            <span :class="getDifferenceClass(item.difference)">
              {{ formatCurrency(item.difference, item.statementCurrency) }}
            </span>
          </template>

          <template v-slot:item.actions="{ item }">
            <v-tooltip location="top">
              <template v-slot:activator="{ props }">
                <v-btn
                  v-bind="props"
                  icon
                  size="small"
                  variant="text"
                  color="primary"
                  @click="viewReconciliation(item.id)"
                >
                  <v-icon>mdi-eye</v-icon>
                </v-btn>
              </template>
              <span>View Details</span>
            </v-tooltip>

            <v-tooltip location="top" v-if="item.status === 'DRAFT' || item.status === 'IN_PROGRESS'">
              <template v-slot:activator="{ props }">
                <v-btn
                  v-bind="props"
                  icon
                  size="small"
                  variant="text"
                  color="warning"
                  @click="editReconciliation(item.id)"
                >
                  <v-icon>mdi-pencil</v-icon>
                </v-btn>
              </template>
              <span>Edit</span>
            </v-tooltip>

            <v-tooltip location="top" v-if="item.status === 'COMPLETED'">
              <template v-slot:activator="{ props }">
                <v-btn
                  v-bind="props"
                  icon
                  size="small"
                  variant="text"
                  color="success"
                  @click="exportReconciliation(item.id)"
                >
                  <v-icon>mdi-file-export</v-icon>
                </v-btn>
              </template>
              <span>Export</span>
            </v-tooltip>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>

    <!-- Create/Edit Dialog -->
    <v-dialog v-model="showDialog" max-width="600px">
      <v-card>
        <v-card-title>
          <span class="text-h5">{{ isEdit ? 'Edit' : 'New' }} Reconciliation</span>
        </v-card-title>
        <v-card-text>
          <v-form ref="form" v-model="valid" @submit.prevent="saveReconciliation">
            <v-row>
              <v-col cols="12" md="6">
                <v-select
                  v-model="formData.accountId"
                  :items="accounts"
                  item-title="name"
                  item-value="id"
                  label="Account"
                  :rules="[v => !!v || 'Account is required']"
                  required
                ></v-select>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="formData.reference"
                  label="Reference"
                  :rules="[v => !!v || 'Reference is required']"
                  required
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-menu
                  v-model="startDateMenu"
                  :close-on-content-click="false"
                  transition="scale-transition"
                  offset-y
                  min-width="auto"
                >
                  <template v-slot:activator="{ props }">
                    <v-text-field
                      v-model="formData.startDate"
                      label="Start Date"
                      readonly
                      v-bind="props"
                      :rules="[v => !!v || 'Start date is required']"
                      required
                    ></v-text-field>
                  </template>
                  <v-date-picker
                    v-model="formData.startDate"
                    @input="startDateMenu = false"
                  ></v-date-picker>
                </v-menu>
              </v-col>
              <v-col cols="12" md="6">
                <v-menu
                  v-model="endDateMenu"
                  :close-on-content-click="false"
                  transition="scale-transition"
                  offset-y
                  min-width="auto"
                >
                  <template v-slot:activator="{ props }">
                    <v-text-field
                      v-model="formData.endDate"
                      label="End Date"
                      readonly
                      v-bind="props"
                      :rules="[v => !!v || 'End date is required', v => !v || v >= formData.startDate || 'End date must be after start date']"
                      required
                    ></v-text-field>
                  </template>
                  <v-date-picker
                    v-model="formData.endDate"
                    :min="formData.startDate"
                    @input="endDateMenu = false"
                  ></v-date-picker>
                </v-menu>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model.number="formData.statementBalance"
                  label="Statement Balance"
                  type="number"
                  step="0.01"
                  :rules="[v => !!v || 'Statement balance is required', v => !isNaN(v) || 'Must be a valid number']"
                  required
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="formData.statementReference"
                  label="Statement Reference"
                ></v-text-field>
              </v-col>
              <v-col cols="12">
                <v-textarea
                  v-model="formData.notes"
                  label="Notes"
                  rows="2"
                ></v-textarea>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="error" text @click="showDialog = false">Cancel</v-btn>
          <v-btn color="primary" @click="saveReconciliation" :loading="saving">
            Save
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'vue-toastification';
import { format, parseISO } from 'date-fns';
import reconciliationService from '@/services/accounting/reconciliationService';
import accountService from '@/services/accounting/accountService';

const router = useRouter();
const toast = useToast();

// Data
const loading = ref(false);
const saving = ref(false);
const reconciliations = ref([]);
const accounts = ref([]);
const search = ref('');
const showDialog = ref(false);
const isEdit = ref(false);
const currentId = ref(null);
const startDateMenu = ref(false);
const endDateMenu = ref(false);
const valid = ref(false);

// Form data
const formData = ref({
  accountId: null,
  reference: '',
  startDate: format(new Date(), 'yyyy-MM-dd'),
  endDate: format(new Date(), 'yyyy-MM-dd'),
  statementBalance: 0,
  statementCurrency: 'USD',
  statementReference: '',
  notes: ''
});

// Filters
const filters = ref({
  status: null,
  accountId: null
});

// Pagination
const pagination = ref({
  page: 1,
  itemsPerPage: 10,
  total: 0,
  sortBy: 'endDate',
  sortDesc: true
});

// Table headers
const headers = [
  { title: 'Reference', key: 'reference', sortable: true },
  { title: 'Account', key: 'account.name', sortable: true },
  { title: 'Status', key: 'status', sortable: true },
  { title: 'Start Date', key: 'startDate', sortable: true },
  { title: 'End Date', key: 'endDate', sortable: true },
  { title: 'Statement Balance', key: 'statementBalance', align: 'end', sortable: true },
  { title: 'Calculated Balance', key: 'calculatedBalance', align: 'end', sortable: true },
  { title: 'Difference', key: 'difference', align: 'end', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false, align: 'end' }
];

// Status options for filter
const statusOptions = [
  { title: 'Draft', value: 'DRAFT' },
  { title: 'In Progress', value: 'IN_PROGRESS' },
  { title: 'Completed', value: 'COMPLETED' },
  { title: 'Voided', value: 'VOIDED' }
];

// Methods
const fetchReconciliations = async () => {
  try {
    loading.value = true;
    const params = {
      page: pagination.value.page,
      limit: pagination.value.itemsPerPage,
      sortBy: pagination.value.sortBy,
      sortOrder: pagination.value.sortDesc ? 'desc' : 'asc',
      ...filters.value,
      search: search.value
    };

    const response = await reconciliationService.getReconciliations(params);
    reconciliations.value = response.items;
    pagination.value.total = response.total;
  } catch (error) {
    console.error('Error fetching reconciliations:', error);
    toast.error('Failed to load reconciliations');
  } finally {
    loading.value = false;
  }
};

const fetchAccounts = async () => {
  try {
    const response = await accountService.getAccounts({
      type: 'BANK',
      isActive: true,
      limit: 1000
    });
    accounts.value = response.items;
  } catch (error) {
    console.error('Error fetching accounts:', error);
    toast.error('Failed to load accounts');
  }
};

const handleOptionsChange = (options) => {
  pagination.value.page = options.page;
  pagination.value.itemsPerPage = options.itemsPerPage;
  if (options.sortBy && options.sortBy.length > 0) {
    pagination.value.sortBy = options.sortBy[0];
    pagination.value.sortDesc = options.sortDesc[0];
  }
  fetchReconciliations();
};

const handleSearch = () => {
  // Add a small delay to prevent too many API calls while typing
  clearTimeout(window.searchTimeout);
  window.searchTimeout = setTimeout(() => {
    fetchReconciliations();
  }, 500);
};

const createReconciliation = () => {
  isEdit.value = false;
  currentId.value = null;
  formData.value = {
    accountId: null,
    reference: '',
    startDate: format(new Date(), 'yyyy-MM-dd'),
    endDate: format(new Date(), 'yyyy-MM-dd'),
    statementBalance: 0,
    statementCurrency: 'USD',
    statementReference: '',
    notes: ''
  };
  showDialog.value = true;
};

const editReconciliation = async (id) => {
  try {
    const reconciliation = await reconciliationService.getReconciliation(id);
    currentId.value = id;
    isEdit.value = true;
    
    formData.value = {
      accountId: reconciliation.accountId,
      reference: reconciliation.reference,
      startDate: format(new Date(reconciliation.startDate), 'yyyy-MM-dd'),
      endDate: format(new Date(reconciliation.endDate), 'yyyy-MM-dd'),
      statementBalance: parseFloat(reconciliation.statementBalance),
      statementCurrency: reconciliation.statementCurrency,
      statementReference: reconciliation.statementReference || '',
      notes: reconciliation.notes || ''
    };
    
    showDialog.value = true;
  } catch (error) {
    console.error('Error loading reconciliation:', error);
    toast.error('Failed to load reconciliation');
  }
};

const saveReconciliation = async () => {
  if (!valid.value) return;
  
  try {
    saving.value = true;
    const data = {
      ...formData.value,
      startDate: new Date(formData.value.startDate).toISOString(),
      endDate: new Date(formData.value.endDate).toISOString()
    };

    if (isEdit.value && currentId.value) {
      await reconciliationService.updateReconciliation(currentId.value, data);
      toast.success('Reconciliation updated successfully');
    } else {
      await reconciliationService.createReconciliation(data);
      toast.success('Reconciliation created successfully');
    }
    
    showDialog.value = false;
    fetchReconciliations();
  } catch (error) {
    console.error('Error saving reconciliation:', error);
    toast.error(error.response?.data?.message || 'Failed to save reconciliation');
  } finally {
    saving.value = false;
  }
};

const viewReconciliation = (id) => {
  router.push(`/accounting/reconciliations/${id}`);
};

const exportReconciliation = async (id) => {
  try {
    const response = await reconciliationService.exportReconciliation(id, 'pdf');
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `reconciliation-${id}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    toast.success('Export started successfully');
  } catch (error) {
    console.error('Error exporting reconciliation:', error);
    toast.error('Failed to export reconciliation');
  }
};

// Formatting helpers
const formatDate = (date) => {
  return date ? format(parseISO(date), 'MMM d, yyyy') : '';
};

const formatCurrency = (amount, currency = 'USD') => {
  if (amount === null || amount === undefined) return '';
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency || 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount);
};

const formatStatus = (status) => {
  const statusMap = {
    DRAFT: 'Draft',
    IN_PROGRESS: 'In Progress',
    COMPLETED: 'Completed',
    VOIDED: 'Voided'
  };
  return statusMap[status] || status;
};

const getStatusColor = (status) => {
  const colors = {
    DRAFT: 'grey',
    IN_PROGRESS: 'blue',
    COMPLETED: 'success',
    VOIDED: 'error'
  };
  return colors[status] || 'default';
};

const getDifferenceClass = (difference) => {
  if (difference > 0) return 'text-success';
  if (difference < 0) return 'text-error';
  return '';
};

// Lifecycle hooks
onMounted(() => {
  fetchReconciliations();
  fetchAccounts();
});
</script>

<style scoped>
.reconciliation-list {
  padding: 20px;
}

.text-success {
  color: #4CAF50;
  font-weight: 500;
}

.text-error {
  color: #F44336;
  font-weight: 500;
}

.v-data-table {
  margin-top: 20px;
}

.v-card {
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.v-card-title {
  padding: 16px 24px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.12);
}

.v-card-text {
  padding: 16px 24px;
}

.v-dialog .v-card {
  border-radius: 8px;
}

.v-dialog .v-card-title {
  background-color: #f5f5f5;
  border-bottom: 1px solid #e0e0e0;
}

.v-dialog .v-card-actions {
  padding: 16px 24px;
  border-top: 1px solid rgba(0, 0, 0, 0.12);
}
</style>
