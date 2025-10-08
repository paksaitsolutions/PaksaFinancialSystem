<template>
  <div class="credit-memo-list">
    <Card>
      <template #title>
        <div class="flex align-items-center justify-content-between">
          <h2>Credit Memos</h2>
          <Button 
            label="New Credit Memo" 
            icon="pi pi-plus" 
            @click="openCreateDialog"
          />
        </div>
      </template>
      
      <template #content>
        <!-- Search and filters -->
        <div class="grid mb-4">
          <div class="col-12 sm:col-3">
            <Dropdown
              v-model="filters.status"
              :options="statusOptions"
              optionLabel="title"
              optionValue="value"
              placeholder="Status"
              :showClear="true"
              @change="fetchCreditMemos"
            />
          </div>
          <div class="col-12 sm:col-3">
            <Dropdown
              v-model="filters.vendorId"
              :options="vendors"
              optionLabel="name"
              optionValue="id"
              placeholder="Vendor"
              :showClear="true"
              @change="fetchCreditMemos"
            />
          </div>
          <div class="col-12 sm:col-3">
            <InputText
              v-model="filters.creditMemoNumber"
              placeholder="Credit Memo Number"
              @input="debouncedFetchCreditMemos"
            />
          </div>
          <div class="col-12 sm:col-3">
            <Button
              label="Clear"
              icon="pi pi-filter-slash"
              severity="secondary"
              outlined
              @click="clearFilters"
            />
          </div>
        </div>
        
        <!-- Data table -->
        <DataTable
          :value="creditMemos"
          :loading="loading"
          :paginator="true"
          :rows="pagination.itemsPerPage"
          :totalRecords="pagination.totalItems"
          :lazy="true"
          @page="onPage"
          @sort="onSort"
        >
          <Column field="credit_memo_number" header="Credit Memo #" :sortable="true" />
          <Column field="vendor.name" header="Vendor" :sortable="true" />
          <Column field="credit_date" header="Date" :sortable="true">
            <template #body="{ data }">
              {{ formatDate(data.credit_date) }}
            </template>
          </Column>
          <Column field="amount" header="Amount" :sortable="true">
            <template #body="{ data }">
              {{ formatCurrency(data.amount) }}
            </template>
          </Column>
          <Column field="applied_amount" header="Applied" :sortable="true">
            <template #body="{ data }">
              {{ formatCurrency(data.applied_amount) }}
            </template>
          </Column>
          <Column field="remaining_amount" header="Remaining" :sortable="true">
            <template #body="{ data }">
              {{ formatCurrency(data.remaining_amount) }}
            </template>
          </Column>
          <Column field="status" header="Status" :sortable="true">
            <template #body="{ data }">
              <Tag :value="formatStatus(data.status)" :severity="getStatusSeverity(data.status)" />
            </template>
          </Column>
          <Column header="Actions">
            <template #body="{ data }">
              <div class="flex gap-2">
                <Button
                  icon="pi pi-eye"
                  class="p-button-rounded p-button-text"
                  @click="viewCreditMemo(data)"
                  v-tooltip.top="'View'"
                />
                <Button
                  v-if="canEdit(data)"
                  icon="pi pi-pencil"
                  class="p-button-rounded p-button-text p-button-warning"
                  @click="editCreditMemo(data)"
                  v-tooltip.top="'Edit'"
                />
                <Button
                  v-if="canApply(data)"
                  icon="pi pi-check-circle"
                  class="p-button-rounded p-button-text p-button-success"
                  @click="applyCreditMemo(data)"
                  v-tooltip.top="'Apply'"
                />
                <Button
                  v-if="canVoid(data)"
                  icon="pi pi-times"
                  class="p-button-rounded p-button-text p-button-danger"
                  @click="voidCreditMemo(data)"
                  v-tooltip.top="'Void'"
                />
              </div>
            </template>
          </Column>
        </DataTable>
    </template>
    </Card>
    
    <!-- Void Dialog -->
    <Dialog 
      v-model:visible="voidDialog.show" 
      :style="{width: '500px'}" 
      header="Void Credit Memo" 
      :modal="true"
    >
      <p>Are you sure you want to void credit memo "{{ voidDialog.creditMemo?.credit_memo_number }}"?</p>
      <p class="text-orange-500">This will reverse all applications and cannot be undone.</p>
      <div class="field">
        <label for="reason">Reason</label>
        <Textarea
          id="reason"
          v-model="voidDialog.reason"
          rows="3"
          class="w-full"
        />
      </div>
      
      <template #footer>
        <Button 
          label="Cancel" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="voidDialog.show = false"
        />
        <Button 
          label="Void Credit Memo" 
          icon="pi pi-check" 
          class="p-button-danger" 
          :disabled="!voidDialog.reason"
          @click="submitVoidAction"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';

type CreditMemo = {
  id: string;
  credit_memo_number: string;
  vendor: { name: string };
  credit_date: string;
  amount: number;
  applied_amount: number;
  remaining_amount: number;
  status: string;
};

type Vendor = {
  id: string;
  name: string;
};

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
const toast = useToast();

// Data
const creditMemos = ref<CreditMemo[]>([]);
const vendors = ref<Vendor[]>([]);
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
    const { creditMemoService } = await import('@/api/apService');
    const params = {
      page: pagination.page,
      limit: pagination.itemsPerPage,
      ...filters
    };
    const response = await creditMemoService.getCreditMemos(params);
    creditMemos.value = response.credit_memos || response.data || [];
    pagination.totalItems = response.total || creditMemos.value.length;
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load credit memos',
      life: 5000
    });
    console.error('Error fetching credit memos:', error);
  } finally {
    loading.value = false;
  }
};

const fetchVendors = async () => {
  try {
    const { vendorService } = await import('@/api/apService');
    const response = await vendorService.getVendors();
    vendors.value = response.vendors || response.data || [];
  } catch (error) {
    console.error('Error fetching vendors:', error);
  }
};

const debouncedFetchCreditMemos = () => {
  setTimeout(fetchCreditMemos, 300);
};

const onPage = (event: any) => {
  pagination.page = event.page + 1;
  fetchCreditMemos();
};

const onSort = (event: any) => {
  pagination.sortBy = event.sortField;
  pagination.sortDesc = event.sortOrder === -1;
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
    const { creditMemoService } = await import('@/api/apService');
    await creditMemoService.voidCreditMemo(voidDialog.creditMemo.id, voidDialog.reason);
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Credit memo voided successfully',
      life: 3000
    });
    fetchCreditMemos();
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to void credit memo',
      life: 5000
    });
    console.error('Error voiding credit memo:', error);
  } finally {
    voidDialog.show = false;
    voidDialog.creditMemo = null;
  }
};

// Helper methods
const getStatusSeverity = (status: string) => {
  const severities: Record<string, string> = {
    active: 'success',
    fully_applied: 'info',
    expired: 'warning',
    voided: 'danger',
  };
  return severities[status] || 'info';
};

const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount || 0);
};

const formatDate = (dateString: string): string => {
  if (!dateString) return '';
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
};

const formatStatus = (status: string) => {
  return status.charAt(0).toUpperCase() + status.slice(1).replace('_', ' ');
};

// Permission checks
const canEdit = (creditMemo: CreditMemo) => {
  return creditMemo.status === 'active';
};

const canApply = (creditMemo: CreditMemo) => {
  return creditMemo.status === 'active' && creditMemo.remaining_amount > 0;
};

const canVoid = (creditMemo: CreditMemo) => {
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
  padding: 1rem;
}
</style>