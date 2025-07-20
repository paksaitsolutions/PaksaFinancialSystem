<script setup lang="ts">
import { ref, watch, defineProps, withDefaults, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useGlAccounts } from '../composables/useGlAccounts';
import { useToast } from 'primevue/usetoast';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import Dropdown from 'primevue/dropdown';
import type { AccountType, GlAccountFilters } from '../types/gl-account';

// Define props with TypeScript interface
interface Props {
  selection?: any[];
  filters?: Partial<GlAccountFilters> & {
    searchTerm?: string;
    page?: number;
    pageSize?: number;
    sortField?: string;
    sortOrder?: number;
  };
}

const props = withDefaults(defineProps<Props>(), {
  selection: () => [],
  filters: () => ({
    searchTerm: '',
    page: 1,
    pageSize: 10,
    sortField: 'code',
    sortOrder: 1
  })
});

const emit = defineEmits(['row-select']);

const router = useRouter();
const toast = useToast();

// Use our composable
const {
  accounts,
  currentAccount,
  isLoading,
  error,
  totalAccounts,
  currentFilters,
  fetchAccounts,
  deleteAccount,
  resetCurrentAccount
} = useGlAccounts();

// Initialize local filters from props
const localFilters = ref<GlAccountFilters & { searchTerm?: string; page?: number; pageSize?: number; sortField?: string; sortOrder?: number }>({ 
  ...props.filters,
  searchTerm: props.filters?.searchTerm || ''
});

// Watch for filter changes and fetch accounts
watch(() => localFilters.value, (newFilters) => {
  const { searchTerm, page, pageSize, sortField, sortOrder, ...rest } = newFilters;
  fetchAccounts({
    ...rest,
    searchTerm,
    page,
    pageSize,
    sortField,
    sortOrder
  });
}, { deep: true });

// Account types for filter dropdown
const accountTypes = [
  { label: 'Assets', value: 'ASSET' },
  { label: 'Liabilities', value: 'LIABILITY' },
  { label: 'Equity', value: 'EQUITY' },
  { label: 'Revenue', value: 'REVENUE' },
  { label: 'Expense', value: 'EXPENSE' },
];

// Status options for filter
const statusOptions = [
  { label: 'Active', value: true },
  { label: 'Inactive', value: false }
];

// Handle row click to view details
const onRowSelect = (event: any) => {
  if (event.data?.id) {
    router.push(`/gl/accounts/${event.data.id}`);
  }
};

// Handle account deletion
const confirmDelete = async (accountId: string | number) => {
  if (confirm('Are you sure you want to delete this account?')) {
    try {
      await deleteAccount(accountId);
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Account deleted successfully',
        life: 3000
      });
    } catch (err) {
      console.error('Failed to delete account:', err);
    }
  }
};

// Handle page change
const onPage = (event: any) => {
  localFilters.value.page = event.page + 1;
  localFilters.value.pageSize = event.rows;
};

// Handle sort change
const onSort = (event: any) => {
  localFilters.value.sortField = event.sortField;
  localFilters.value.sortOrder = event.sortOrder;
};

// Reset filters
const resetFilters = () => {
  localFilters.value = {
    searchTerm: '',
    page: 1,
    pageSize: 10,
    sortField: 'code',
    sortOrder: 1
  };
};

// Format account type for display
const formatAccountType = (type: string) => {
  const typeMap: Record<string, string> = {
    'ASSET': 'Asset',
    'LIABILITY': 'Liability',
    'EQUITY': 'Equity',
    'REVENUE': 'Revenue',
    'EXPENSE': 'Expense'
  };
  return typeMap[type] || type;
};

// Format status for display
const formatStatus = (isActive: boolean) => {
  return isActive ? 'Active' : 'Inactive';
};

// Get status severity for badge
const getStatusSeverity = (isActive: boolean) => {
  return isActive ? 'success' : 'danger';
};

// Format currency
const formatCurrency = (value: number, currency: string = 'USD') => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency
  }).format(value);
};
</script>

<template>
  <div class="card">
    <div class="flex justify-content-between align-items-center mb-4">
      <h2>GL Accounts</h2>
      <Button 
        icon="pi pi-plus" 
        label="New Account" 
        @click="router.push('/gl/accounts/new')"
      />
    </div>

    <!-- Filters -->
    <div class="grid p-fluid mb-4">
      <div class="col-12 md:col-4">
        <span class="p-float-label">
          <InputText 
            id="search" 
            v-model="localFilters.search" 
            type="text" 
            placeholder="Search by name or code..."
          />
          <label for="search">Search</label>
        </span>
      </div>
      
      <div class="col-12 md:col-3">
        <span class="p-float-label">
          <Dropdown 
            v-model="localFilters.type" 
            :options="accountTypes" 
            optionLabel="label" 
            optionValue="value"
            :showClear="true"
            placeholder="Select Type"
          />
          <label>Account Type</label>
        </span>
      </div>
      
      <div class="col-12 md:col-3">
        <span class="p-float-label">
          <Dropdown 
            v-model="localFilters.isActive" 
            :options="statusOptions" 
            optionLabel="label" 
            optionValue="value"
            :showClear="true"
            placeholder="Select Status"
          />
          <label>Status</label>
        </span>
      </div>
      
      <div class="col-12 md:col-2 flex align-items-end">
        <Button 
          label="Reset" 
          icon="pi pi-refresh" 
          class="p-button-outlined" 
          @click="resetFilters"
        />
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="text-center p-5">
      <i class="pi pi-spin pi-spinner text-4xl"></i>
      <p>Loading accounts...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="p-4 bg-red-100 text-red-700 rounded-md">
      <p>Error loading accounts: {{ error.message }}</p>
      <Button 
        label="Retry" 
        icon="pi pi-refresh" 
        class="p-button-text p-button-sm mt-2" 
        @click="fetchAccounts(filters)"
      />
    </div>

    <!-- Data Table -->
    <div v-else class="card">
      <DataTable
        :value="accounts"
        :paginator="true"
        :rows="filters.pageSize"
        :totalRecords="totalAccounts"
        :lazy="true"
        :loading="isLoading"
        :sortField="filters.sortField"
        :sortOrder="filters.sortOrder"
        @page="onPage"
        @sort="onSort"
        @rowSelect="onRowSelect"
        selectionMode="single"
        dataKey="id"
        responsiveLayout="scroll"
        :paginatorTemplate="'FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown'"
        :rowsPerPageOptions="[10, 25, 50]"
        currentPageReportTemplate="Showing {first} to {last} of {totalRecords} accounts"
      >
        <Column field="code" header="Code" sortable>
          <template #body="{ data }">
            <span class="font-medium">{{ data.code }}</span>
          </template>
        </Column>
        
        <Column field="name" header="Name" sortable />
        
        <Column field="type" header="Type" sortable>
          <template #body="{ data }">
            <Tag :value="formatAccountType(data.type)" />
          </template>
        </Column>
        
        <Column field="balance" header="Balance" sortable>
          <template #body="{ data }">
            {{ formatCurrency(data.balance, data.currency) }}
          </template>
        </Column>
        
        <Column field="isActive" header="Status" sortable>
          <template #body="{ data }">
            <Tag 
              :value="formatStatus(data.isActive)" 
              :severity="getStatusSeverity(data.isActive)"
            />
          </template>
        </Column>
        
        <Column header="Actions" :exportable="false" style="min-width: 8rem">
          <template #body="{ data }">
            <div class="flex gap-2">
              <Button 
                icon="pi pi-pencil" 
                class="p-button-rounded p-button-text p-button-sm"
                @click.stop="router.push(`/gl/accounts/${data.id}/edit`)"
              />
              <Button 
                icon="pi pi-trash" 
                class="p-button-rounded p-button-text p-button-sm p-button-danger"
                @click.stop="confirmDelete(data.id)"
              />
            </div>
          </template>
        </Column>
      </DataTable>
    </div>
  </div>
</template>

<style scoped>
.p-datatable .p-datatable-thead > tr > th {
  background-color: #f8f9fa;
}

.p-datatable .p-datatable-tbody > tr {
  cursor: pointer;
  transition: background-color 0.2s;
}

.p-datatable .p-datatable-tbody > tr:hover {
  background-color: #f8f9fa;
}
</style>
