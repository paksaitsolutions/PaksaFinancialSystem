<template>
  <div class="gl-account-list">
    <!-- Page Header -->
    <div class="flex justify-content-between align-items-center mb-4">
      <div>
        <h1 class="text-2xl font-bold">Chart of Accounts</h1>
        <p class="text-color-secondary text-sm mt-1">
          Manage your organization's chart of accounts and financial structure
        </p>
      </div>
      <div class="flex gap-2">
        <Button 
          icon="pi pi-refresh" 
          class="p-button-text" 
          :loading="isLoading"
          @click="refreshAccounts"
          v-tooltip="'Refresh accounts'"
        />
        <Button 
          label="New Account" 
          icon="pi pi-plus" 
          class="p-button-success"
          @click="openAccountForm()"
        />
      </div>
    </div>

    <!-- Filters and Actions -->
    <Card class="mb-4">
      <template #content>
        <div class="grid">
          <div class="col-12 md:col-4">
            <span class="p-input-icon-left w-full">
              <i class="pi pi-search" />
              <InputText 
                v-model="filters.search" 
                placeholder="Search accounts..." 
                class="w-full"
                @keyup.enter="applyFilters"
              />
            </span>
          </div>
          <div class="col-12 md:col-2">
            <Dropdown 
              v-model="filters.accountType" 
              :options="accountTypes" 
              optionLabel="label"
              optionValue="value"
              placeholder="Account Type"
              class="w-full"
              :showClear="true"
              @change="applyFilters"
            />
          </div>
          <div class="col-12 md:col-2">
            <Dropdown 
              v-model="filters.status" 
              :options="statusOptions" 
              optionLabel="label"
              optionValue="value"
              placeholder="Status"
              class="w-full"
              :showClear="true"
              @change="applyFilters"
            />
          </div>
          <div class="col-12 md:col-2">
            <Button 
              label="Filter" 
              icon="pi pi-filter" 
              class="p-button-outlined w-full"
              @click="applyFilters"
            />
          </div>
          <div class="col-12 md:col-2">
            <Button 
              label="Clear" 
              icon="pi pi-times" 
              class="p-button-text w-full"
              @click="resetFilters"
            />
          </div>
        </div>
      </template>
    </Card>

    <!-- Accounts Table -->
    <Card>
      <template #content>
        <DataTable 
          :value="accounts" 
          :loading="isLoading"
          :paginator="true"
          :rows="pagination.limit"
          :totalRecords="totalRecords"
          :first="pagination.offset"
          :rowsPerPageOptions="[10, 25, 50, 100]"
          :globalFilterFields="['accountNumber', 'name', 'accountType']"
          @page="onPageChange($event)"
          @sort="onSort($event)"
          :sortField="sort.field"
          :sortOrder="sort.order"
          responsiveLayout="scroll"
          class="p-datatable-sm"
        >
          <template #empty>
            <div class="text-center p-4">
              <i class="pi pi-inbox text-4xl text-400 mb-2" />
              <p class="text-600">No accounts found</p>
              <Button 
                label="Create Account" 
                icon="pi pi-plus" 
                class="p-button-text mt-2"
                @click="openAccountForm()"
              />
            </div>
          </template>

          <Column field="accountNumber" header="Account #" :sortable="true">
            <template #body="{ data }">
              <span class="font-medium">{{ data.accountNumber }}</span>
            </template>
          </Column>
          
          <Column field="name" header="Account Name" :sortable="true">
            <template #body="{ data }">
              <div class="flex align-items-center">
                <span 
                  class="mr-2"
                  :style="{ 'margin-left': `${(data.level || 0) * 1}rem` }"
                >
                  <i v-if="data.children && data.children.length > 0" 
                     :class="data.expanded ? 'pi pi-folder-open' : 'pi pi-folder'"
                     class="mr-2"
                     @click="toggleExpand(data)"
                     style="cursor: pointer"
                  />
                  <i v-else class="pi pi-file mr-2 text-400" />
                </span>
                <router-link 
                  :to="{ name: 'gl-account-detail', params: { id: data.id } }"
                  class="text-primary hover:underline"
                >
                  {{ data.name }}
                </router-link>
              </div>
            </template>
          </Column>
          
          <Column field="accountType" header="Type" :sortable="true">
            <template #body="{ data }">
              <Tag :value="formatAccountType(data.accountType)" :severity="getAccountTypeSeverity(data.accountType)" />
            </template>
          </Column>
          
          <Column field="currentBalance" header="Balance" :sortable="true" class="text-right">
            <template #body="{ data }">
              <span class="font-medium">{{ formatCurrency(data.currentBalance, data.currency) }}</span>
            </template>
          </Column>
          
          <Column field="status" header="Status" :sortable="true">
            <template #body="{ data }">
              <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
            </template>
          </Column>
          
          <Column header="Actions" style="width: 150px">
            <template #body="{ data }">
              <div class="flex gap-1">
                <Button 
                  icon="pi pi-pencil" 
                  class="p-button-text p-button-sm"
                  @click="openAccountForm(data)"
                  v-tooltip="'Edit account'"
                />
                <Button 
                  icon="pi pi-trash" 
                  class="p-button-text p-button-sm p-button-danger"
                  @click="confirmDelete(data)"
                  v-tooltip="'Delete account'"
                  :disabled="data.isSystemAccount"
                />
              </div>
            </template>
          </Column>
          
          <template #footer>
            <div class="flex justify-content-between align-items-center">
              <div class="text-sm text-500">
                Showing {{ Math.min(pagination.offset + 1, totalRecords) }} to 
                {{ Math.min(pagination.offset + accounts.length, totalRecords) }} of {{ totalRecords }} accounts
              </div>
              <div>
                <Button 
                  icon="pi pi-download" 
                  label="Export" 
                  class="p-button-outlined p-button-sm"
                  @click="showExportDialog"
                  :loading="exportLoading"
                />
              </div>
            </div>
          </template>
        </DataTable>
      </template>
    </Card>

    <!-- Account Form Dialog -->
    <Dialog 
      v-model:visible="showAccountForm" 
      :header="formMode === 'create' ? 'New Account' : 'Edit Account'"
      :modal="true"
      :style="{ width: '600px' }"
      :closable="!formSubmitting"
      :closeOnEscape="!formSubmitting"
    >
      <GlAccountForm 
        v-if="showAccountForm"
        :account="selectedAccount"
        :mode="formMode"
        @submit="handleFormSubmit"
        @cancel="showAccountForm = false"
        :loading="formSubmitting"
      />
    </Dialog>

    <!-- Delete Confirmation -->
    <ConfirmDialog />
    
    <!-- Export Dialog -->
    <ExportDialog 
      v-model:visible="showExportDialog"
      :loading="exportLoading"
      @export="handleExport"
      @cancel="showExportDialog = false"
    />
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, reactive, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import { useGlAccountStore } from '@/modules/general-ledger/store/gl-account';
import { GlAccount, AccountType, AccountStatus } from '@/modules/general-ledger/types/gl-account';
import GlAccountForm from './GlAccountForm.vue';
import ExportDialog from '@/components/common/ExportDialog.vue';
import { formatCurrency } from '@/shared/utils/formatters';

export default defineComponent({
  name: 'GlAccountListView',
  
  components: {
    GlAccountForm,
    ExportDialog
  },
  
  setup() {
    const router = useRouter();
    const toast = useToast();
    const confirm = useConfirm();
    const accountStore = useGlAccountStore();
    
    // State
    const isLoading = ref(false);
    const showAccountForm = ref(false);
    const formMode = ref<'create' | 'edit'>('create');
    const selectedAccount = ref<Partial<GlAccount> | null>(null);
    const formSubmitting = ref(false);
    const showExportDialog = ref(false);
    const exportLoading = ref(false);
    
    // Filters
    const filters = reactive({
      search: '',
      accountType: null as string | null,
      status: AccountStatus.ACTIVE,
    });
    
    // Pagination
    const pagination = reactive({
      page: 1,
      limit: 10,
      get offset() {
        return (this.page - 1) * this.limit;
      }
    });
    
    // Sorting
    const sort = reactive({
      field: 'accountNumber',
      order: 1 as 1 | -1
    });
    
    // Options for filters
    const accountTypes = [
      { label: 'Assets', value: AccountType.ASSET },
      { label: 'Liabilities', value: AccountType.LIABILITY },
      { label: 'Equity', value: AccountType.EQUITY },
      { label: 'Revenue', value: AccountType.REVENUE },
      { label: 'Expense', value: AccountType.EXPENSE },
      { label: 'Gain', value: AccountType.GAIN },
      { label: 'Loss', value: AccountType.LOSS },
    ];
    
    const statusOptions = [
      { label: 'Active', value: AccountStatus.ACTIVE },
      { label: 'Inactive', value: AccountStatus.INACTIVE },
      { label: 'All', value: null },
    ];
    
    // Computed
    const accounts = computed(() => accountStore.accounts);
    const totalRecords = computed(() => accountStore.totalAccounts || 0);
    
    // Methods
    const loadAccounts = async () => {
      try {
        isLoading.value = true;
        await accountStore.fetchAccounts({
          search: filters.search,
          accountType: filters.accountType as any,
          status: filters.status as any,
          page: pagination.page,
          limit: pagination.limit,
          sortBy: sort.field,
          sortOrder: sort.order === 1 ? 'asc' : 'desc',
        });
      } catch (error) {
        console.error('Error loading accounts:', error);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to load accounts. Please try again.',
          life: 5000,
        });
      } finally {
        isLoading.value = false;
      }
    };
    
    const applyFilters = () => {
      pagination.page = 1; // Reset to first page when filters change
      loadAccounts();
    };
    
    const resetFilters = () => {
      filters.search = '';
      filters.accountType = null;
      filters.status = AccountStatus.ACTIVE;
      pagination.page = 1;
      loadAccounts();
    };
    
    const onPageChange = (event: any) => {
      pagination.page = event.page + 1;
      pagination.limit = event.rows;
      loadAccounts();
    };
    
    const onSort = (event: any) => {
      sort.field = event.sortField;
      sort.order = event.sortOrder > 0 ? 1 : -1;
      loadAccounts();
    };
    
    const refreshAccounts = () => {
      loadAccounts();
    };
    
    const openAccountForm = (account: Partial<GlAccount> | null = null) => {
      if (account) {
        selectedAccount.value = { ...account };
        formMode.value = 'edit';
      } else {
        selectedAccount.value = {
          accountType: AccountType.EXPENSE,
          status: AccountStatus.ACTIVE,
          currency: 'USD', // Default currency
        };
        formMode.value = 'create';
      }
      showAccountForm.value = true;
    };
    
    const handleFormSubmit = async (formData: any) => {
      try {
        formSubmitting.value = true;
        
        if (formMode.value === 'create') {
          await accountStore.createAccount(formData);
          toast.add({
            severity: 'success',
            summary: 'Success',
            detail: 'Account created successfully',
            life: 3000,
          });
        } else {
          if (!selectedAccount.value?.id) return;
          
          await accountStore.updateAccount(selectedAccount.value.id, formData);
          toast.add({
            severity: 'success',
            summary: 'Success',
            detail: 'Account updated successfully',
            life: 3000,
          });
        }
        
        showAccountForm.value = false;
        loadAccounts();
      } catch (error) {
        console.error('Error saving account:', error);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to save account. Please try again.',
          life: 5000,
        });
      } finally {
        formSubmitting.value = false;
      }
    };
    
    const confirmDelete = (account: GlAccount) => {
      if (account.isSystemAccount) {
        toast.add({
          severity: 'warn',
          summary: 'Cannot Delete',
          detail: 'System accounts cannot be deleted.',
          life: 5000,
        });
        return;
      }
      
      confirm.require({
        message: `Are you sure you want to delete account ${account.accountNumber} - ${account.name}?`,
        header: 'Confirm Deletion',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'p-button-danger',
        accept: () => deleteAccount(account.id),
      });
    };
    
    const deleteAccount = async (id: string) => {
      try {
        await accountStore.deleteAccount(id);
        toast.add({
          severity: 'success',
          summary: 'Success',
          detail: 'Account deleted successfully',
          life: 3000,
        });
        loadAccounts();
      } catch (error) {
        console.error('Error deleting account:', error);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to delete account. Please try again.',
          life: 5000,
        });
      }
    };
    
    const toggleExpand = (account: any) => {
      // Toggle expanded state
      account.expanded = !account.expanded;
      
      // If expanding and children not loaded, fetch them
      if (account.expanded && (!account.children || account.children.length === 0)) {
        loadChildAccounts(account.id);
      }
    };
    
    const loadChildAccounts = async (parentId: string) => {
      try {
        await accountStore.fetchAccountHierarchy(parentId);
      } catch (error) {
        console.error('Error loading child accounts:', error);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to load child accounts',
          life: 5000,
        });
      }
    };
    
    const handleExport = async (options: any) => {
      try {
        exportLoading.value = true;
        // Implement export logic here
        // This would call the export method from the store
        console.log('Exporting with options:', options);
        
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        toast.add({
          severity: 'success',
          summary: 'Export Complete',
          detail: 'Your export has been generated and will be downloaded shortly.',
          life: 3000,
        });
        
        showExportDialog.value = false;
      } catch (error) {
        console.error('Export error:', error);
        toast.add({
          severity: 'error',
          summary: 'Export Failed',
          detail: 'An error occurred while generating the export. Please try again.',
          life: 5000,
        });
      } finally {
        exportLoading.value = false;
      }
    };
    
    const formatAccountType = (type: AccountType) => {
      return type.charAt(0).toUpperCase() + type.slice(1).toLowerCase();
    };
    
    const getAccountTypeSeverity = (type: AccountType) => {
      switch (type) {
        case AccountType.ASSET: return 'success';
        case AccountType.LIABILITY: return 'danger';
        case AccountType.EQUITY: return 'info';
        case AccountType.REVENUE: return 'primary';
        case AccountType.EXPENSE: return 'warning';
        case AccountType.GAIN: return 'help';
        case AccountType.LOSS: return 'danger';
        default: return null;
      }
    };
    
    const getStatusSeverity = (status: string) => {
      switch (status) {
        case AccountStatus.ACTIVE: return 'success';
        case AccountStatus.INACTIVE: return 'danger';
        default: return 'info';
      }
    };
    
    // Lifecycle hooks
    onMounted(() => {
      loadAccounts();
    });
    
    return {
      // State
      isLoading,
      showAccountForm,
      formMode,
      selectedAccount,
      formSubmitting,
      showExportDialog,
      exportLoading,
      
      // Filters & Pagination
      filters,
      pagination,
      sort,
      
      // Options
      accountTypes,
      statusOptions,
      
      // Computed
      accounts,
      totalRecords,
      
      // Methods
      applyFilters,
      resetFilters,
      onPageChange,
      onSort,
      refreshAccounts,
      openAccountForm,
      handleFormSubmit,
      confirmDelete,
      toggleExpand,
      handleExport,
      formatAccountType,
      getAccountTypeSeverity,
      getStatusSeverity,
      formatCurrency,
    };
  },
});
</script>

<style scoped>
.gl-account-list {
  padding: 1rem;
}

:deep(.p-datatable .p-datatable-tbody > tr > td) {
  padding: 0.5rem 1rem;
}

:deep(.p-datatable .p-datatable-thead > tr > th) {
  padding: 0.5rem 1rem;
}

:deep(.p-datatable .p-sortable-column) {
  padding: 0.5rem 1rem;
}
</style>
