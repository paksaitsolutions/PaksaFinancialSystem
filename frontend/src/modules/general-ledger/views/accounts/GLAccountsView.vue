<template>
  <div class="gl-accounts">
    <div class="flex justify-content-between align-items-center mb-4">
      <h2>Chart of Accounts</h2>
      <div>
        <Button 
          label="New Account" 
          icon="pi pi-plus" 
          @click="showNewAccountDialog = true"
          class="p-button-success"
        />
      </div>
    </div>

    <div class="card">
      <DataTable 
        :value="accounts" 
        :loading="loading"
        :paginator="true" 
        :rows="10"
        :filters="filters"
        :globalFilterFields="['code', 'name', 'type']"
        responsiveLayout="scroll"
      >
        <template #header>
          <div class="flex justify-content-between align-items-center">
            <span class="p-input-icon-left">
              <i class="pi pi-search" />
              <InputText 
                v-model="filters['global'].value" 
                placeholder="Search accounts..." 
              />
            </span>
            <div>
              <Button 
                icon="pi pi-refresh" 
                class="p-button-text" 
                @click="loadAccounts"
                :loading="loading"
                v-tooltip="'Refresh data'"
              />
              <Button 
                icon="pi pi-download" 
                class="p-button-text" 
                label="Export" 
                @click="showExportDialog"
                v-tooltip="'Export data'"
              />
            </div>
          </div>
        </template>

        <Column field="code" header="Code" :sortable="true" style="min-width:120px">
          <template #body="{ data }">
            <span class="font-medium">{{ data.code }}</span>
          </template>
        </Column>
        
        <Column field="name" header="Account Name" :sortable="true" style="min-width:250px">
          <template #body="{ data }">
            <router-link 
              :to="{ name: 'account-detail', params: { id: data.id } }"
              class="text-primary hover:underline"
            >
              {{ data.name }}
            </router-link>
          </template>
        </Column>
        
        <Column field="type" header="Type" :sortable="true" style="min-width:150px">
          <template #body="{ data }">
            <Tag :value="formatAccountType(data.type)" :severity="getAccountTypeSeverity(data.type)" />
          </template>
        </Column>
        
        <Column field="balance" header="Balance" :sortable="true" style="min-width:150px">
          <template #body="{ data }">
            {{ formatCurrency(data.balance) }}
          </template>
        </Column>
        
        <Column field="status" header="Status" :sortable="true" style="min-width:120px">
          <template #body="{ data }">
            <Tag 
              :value="data.is_active ? 'Active' : 'Inactive'" 
              :severity="data.is_active ? 'success' : 'danger'" 
            />
          </template>
        </Column>
        
        <Column style="min-width:150px">
          <template #body="{ data }">
            <div class="flex gap-2">
              <Button 
                icon="pi pi-pencil" 
                class="p-button-rounded p-button-text p-button-sm"
                @click="editAccount(data)"
              />
              <Button 
                icon="pi pi-trash" 
                class="p-button-rounded p-button-text p-button-sm p-button-danger"
                @click="confirmDeleteAccount(data)"
              />
            </div>
          </template>
        </Column>
      </DataTable>
    </div>

    <!-- New/Edit Account Dialog -->
    <Dialog 
      v-model:visible="showAccountDialog" 
      :header="editingAccount ? 'Edit Account' : 'New Account'"
      :modal="true"
      :style="{ width: '600px' }"
    >
      <div class="p-fluid">
        <div class="field">
          <label for="code">Account Code</label>
          <InputText 
            id="code" 
            v-model="accountForm.code" 
            required 
            :class="{ 'p-invalid': submitted && !accountForm.code }"
          />
          <small class="p-error" v-if="submitted && !accountForm.code">Account code is required.</small>
        </div>
        
        <div class="field">
          <label for="name">Account Name</label>
          <InputText 
            id="name" 
            v-model="accountForm.name" 
            required 
            :class="{ 'p-invalid': submitted && !accountForm.name }"
          />
          <small class="p-error" v-if="submitted && !accountForm.name">Account name is required.</small>
        </div>
        
        <div class="field">
          <label for="type">Account Type</label>
          <Dropdown
            id="type"
            v-model="accountForm.type"
            :options="accountTypes"
            optionLabel="label"
            optionValue="value"
            placeholder="Select Account Type"
            :class="{ 'p-invalid': submitted && !accountForm.type }"
          />
          <small class="p-error" v-if="submitted && !accountForm.type">Account type is required.</small>
        </div>
        
        <div class="field">
          <label for="parent">Parent Account</label>
          <TreeSelect
            v-model="accountForm.parent_id"
            :options="accountTree"
            placeholder="Select Parent Account"
            :showClear="true"
            selectionMode="single"
            :metaKeySelection="false"
            class="w-full"
          />
        </div>
        
        <div class="field">
          <label for="description">Description</label>
          <Textarea id="description" v-model="accountForm.description" rows="3" />
        </div>
        
        <div class="field-checkbox">
          <Checkbox id="is_active" v-model="accountForm.is_active" :binary="true" />
          <label for="is_active">Active</label>
        </div>
      </div>
      
      <template #footer>
        <Button 
          label="Cancel" 
          icon="pi pi-times" 
          @click="hideDialog"
          class="p-button-text"
        />
        <Button 
          label="Save" 
          icon="pi pi-check" 
          @click="saveAccount" 
          class="p-button-success"
          :loading="saving"
        />
      </template>
    </Dialog>
    
    <!-- Delete Confirmation Dialog -->
    <Dialog 
      v-model:visible="showDeleteDialog" 
      header="Confirm Delete" 
      :modal="true"
      :style="{ width: '450px' }"
    >
      <div class="confirmation-content">
        <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
        <span v-if="accountToDelete">
          Are you sure you want to delete <b>{{ accountToDelete.name }}</b>?
        </span>
      </div>
      
      <template #footer>
        <Button 
          label="No" 
          icon="pi pi-times" 
          @click="showDeleteDialog = false"
          class="p-button-text"
        />
        <Button 
          label="Yes" 
          icon="pi pi-check" 
          @click="deleteAccount"
          class="p-button-danger"
          :loading="deleting"
        />
      </template>
    </Dialog>
    <!-- Export Dialog -->
    <ExportDialog
      v-model:visible="exportDialogVisible"
      title="Export Chart of Accounts"
      :file-name="'gl-accounts-export'"
      :columns="exportColumns"
      :data="filteredAccounts"
      :meta="{
        title: 'Chart of Accounts',
        description: 'General Ledger Accounts',
        generatedOn: new Date().toLocaleString(),
        generatedBy: 'System',
        includeSummary: true,
        filters: {
          'Search Term': filters['global'].value || 'None',
          'Total Accounts': accounts.length,
          'Active Accounts': activeAccountsCount
        }
      }"
      @export="handleExport"
    />
  </div>
</template>

<script lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'primevue/usetoast';
import { FilterMatchMode } from 'primevue/api';
import { useGlAccountsStore, type GlAccount } from '@/modules/general-ledger/store/gl-accounts';
import ExportDialog from '@/components/common/ExportDialog.vue';

// Define local types for the view
interface AccountFormData {
  id: string | null;
  code: string;
  name: string;
  type: GlAccount['accountType'] | null;
  parent_id: string | null;
  description: string;
  is_active: boolean;
}

export default {
  name: 'GLAccountsView',
  components: {
    ExportDialog
  },
  setup() {
    const router = useRouter();
    const toast = useToast();
    const glAccountsStore = useGlAccountsStore();
    
    // Reactive state
    const loading = ref(false);
    const showNewAccountDialog = ref(false);
    const exportDialogVisible = ref(false);
    const exporting = ref(false);
    const exportProgress = ref(0);
    const deleting = ref(false);
    const submitted = ref(false);
    const showAccountDialog = ref(false);
    const showDeleteDialog = ref(false);
    const editingAccount = ref(false);
    const accountToDelete = ref<GlAccount | null>(null);
    
    // Filtering
    const filters = ref({
      'global': { value: null, matchMode: FilterMatchMode.CONTAINS },
    });
    
    // Export configuration
    const exportColumns = [
      { field: 'accountNumber', header: 'Account Number' },
      { field: 'name', header: 'Account Name' },
      { field: 'accountType', header: 'Type' },
      { field: 'balance', header: 'Balance' },
      { field: 'isActive', header: 'Status', format: (val: boolean) => val ? 'Active' : 'Inactive' }
    ] as const;

    // Computed properties
    const accounts = computed(() => glAccountsStore.state.accounts);
    
    const filteredAccounts = computed(() => {
      return accounts.value.map(account => ({
        ...account,
        balance: formatCurrency(account.balance, true),
        type: account.accountType // For backward compatibility with template
      }));
    });

    const activeAccountsCount = computed(() => {
      return accounts.value.filter(acc => acc.isActive).length;
    });

    // Form state
    const accountForm = ref<AccountFormData>({
      id: null,
      code: '',
      name: '',
      type: null,
      parent_id: null,
      description: '',
      is_active: true
    });
    
    const accountTypes = [
      { label: 'Asset', value: 'asset' },
      { label: 'Liability', value: 'liability' },
      { label: 'Equity', value: 'equity' },
      { label: 'Revenue', value: 'revenue' },
      { label: 'Expense', value: 'expense' },
      { label: 'Gain', value: 'gain' },
      { label: 'Loss', value: 'loss' },
      { label: 'Temporary', value: 'temporary' }
    ];
    
    // Load accounts from store
    const loadAccounts = async () => {
      loading.value = true;
      try {
        await glAccountsStore.fetchAccounts();
      } catch (error) {
        console.error('Error loading accounts:', error);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to load accounts',
          life: 3000
        });
      } finally {
        loading.value = false;
      }
    };
    
    // Format account type for display
    const formatAccountType = (type) => {
      if (!type) return '';
      return type.charAt(0).toUpperCase() + type.slice(1);
    };
    
    // Get severity for account type tag
    const getAccountTypeSeverity = (type) => {
      switch (type) {
        case 'asset': return 'primary';
        case 'liability': return 'warning';
        case 'equity': return 'success';
        case 'revenue': return 'info';
        case 'expense': return 'danger';
        default: return 'secondary';
      }
    };
    
    // Format currency
    const formatCurrency = (value) => {
      if (value === null || value === undefined) return '$0.00';
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(value);
    };
    
    // Export to CSV
    const showExportDialog = () => {
      exportDialogVisible.value = true;
    };

    const handleExport = async (format, options) => {
      exporting.value = true;
      exportProgress.value = 0;
      
      try {
        // Simulate export progress
        const interval = setInterval(() => {
          exportProgress.value = Math.min(exportProgress.value + 10, 90);
        }, 100);

        // Here you would typically make an API call to export the data
        // For now, we'll just simulate a delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        clearInterval(interval);
        exportProgress.value = 100;
        
        toast.add({
          severity: 'success',
          summary: 'Export Complete',
          detail: `Exported ${filteredAccounts.value.length} accounts to ${format.toUpperCase()}`,
          life: 3000
        });
      } catch (error) {
        console.error('Export failed:', error);
        toast.add({
          severity: 'error',
          summary: 'Export Failed',
          detail: 'An error occurred while exporting the data',
          life: 5000
        });
      } finally {
        setTimeout(() => {
          exporting.value = false;
          exportProgress.value = 0;
        }, 500);
      }
    };
    
    const saveAsExcelFile = (buffer, fileName) => {
      import('file-saver').then(module => {
        const { saveAs } = module;
        const data = new Blob([buffer], { type: 'application/octet-stream' });
        saveAs(data, `${fileName}_export_${new Date().getTime()}.xlsx`);
      });
    };
    
    // Open new account dialog
    const openNewAccount = () => {
      accountForm.value = {
        id: null,
        code: '',
        name: '',
        type: null,
        parent_id: null,
        description: '',
        is_active: true
      };
      submitted.value = false;
      showAccountDialog.value = true;
      editingAccount.value = false;
    };
    
    // Edit account
    const editAccount = (account: GlAccount) => {
      editingAccount.value = true;
      accountForm.value = {
        id: account.id,
        code: account.accountNumber,
        name: account.name,
        type: account.accountType,
        parent_id: account.parentAccountId || null,
        description: account.description || '',
        is_active: account.isActive
      };
      showAccountDialog.value = true;
    };
    
    // Hide dialog
    const hideDialog = () => {
      showAccountDialog.value = false;
      submitted.value = false;
    };
    
    // Save account (create or update)
    const saveAccount = async () => {
      submitted.value = true;
      
      // Validate form
      if (!accountForm.value.code || !accountForm.value.name || !accountForm.value.type) {
        toast.add({
          severity: 'warn',
          summary: 'Validation Error',
          detail: 'Please fill in all required fields',
          life: 3000
        });
        return;
      }
      
      loading.value = true;
      
      try {
        const accountData = {
          accountNumber: accountForm.value.code,
          name: accountForm.value.name,
          accountType: accountForm.value.type,
          parentAccountId: accountForm.value.parent_id || undefined,
          description: accountForm.value.description || undefined,
          isActive: accountForm.value.is_active,
          balance: 0, // New accounts start with 0 balance
          isSystemAccount: false,
          currency: 'USD' // Default currency, should be configurable
        };
        
        if (editingAccount.value && accountForm.value.id) {
          // Update existing account
          await glAccountsStore.updateAccount({
            id: accountForm.value.id,
            data: accountData
          });
          
          toast.add({
            severity: 'success',
            summary: 'Success',
            detail: 'Account updated successfully',
            life: 3000
          });
        } else {
          // Create new account
          await glAccountsStore.createAccount(accountData);
          
          toast.add({
            severity: 'success',
            summary: 'Success',
            detail: 'Account created successfully',
            life: 3000
          });
        }
        
        // Reset form and close dialog
        resetForm();
        showAccountDialog.value = false;
        
      } catch (error) {
        console.error('Error saving account:', error);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to save account',
          life: 3000
        });
      } finally {
        loading.value = false;
      }
    };
    
    // Confirm account deletion
    const confirmDeleteAccount = (account: GlAccount) => {
      accountToDelete.value = account;
      showDeleteDialog.value = true;
    };
    
    // Delete account
    const deleteAccount = async () => {
      if (!accountToDelete.value) return;
      
      deleting.value = true;
      
      try {
        await glAccountsStore.deleteAccount(accountToDelete.value.id);
        
        toast.add({
          severity: 'success',
          summary: 'Success',
          detail: 'Account deleted successfully',
          life: 3000
        });
        
        showDeleteDialog.value = false;
        accountToDelete.value = null;
        
      } catch (error) {
        console.error('Error deleting account:', error);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to delete account',
          life: 3000
        });
      } finally {
        deleting.value = false;
      }
    };
    
    // Generate account tree for parent selection
    const accountTree = computed(() => {
      const buildTree = (accounts, parentId = null) => {
        return accounts
          .filter(account => account.parent_id === parentId)
          .map(account => ({
            key: account.id,
            label: `${account.code} - ${account.name}`,
            data: account,
            children: buildTree(accounts, account.id)
          }));
      };
      
      return buildTree(accounts.value);
    });
    
    // Load accounts on component mount
    onMounted(() => {
      loadAccounts();
    });
    
    return {
      accounts,
      loading,
      saving,
      deleting,
      submitted,
      showAccountDialog,
      showDeleteDialog,
      editingAccount,
      accountToDelete,
      filters,
      accountForm,
      accountTypes,
      accountTree,
      loadAccounts,
      formatAccountType,
      getAccountTypeSeverity,
      formatCurrency,
      exportToCSV,
      openNewAccount,
      editAccount,
      hideDialog,
      saveAccount,
      confirmDeleteAccount,
      deleteAccount
    };
  }
};
</script>

<style scoped>
.confirmation-content {
  display: flex;
  align-items: center;
  justify-content: center;
}

:deep(.p-datatable) {
  font-size: 0.9rem;
}

:deep(.p-datatable .p-datatable-thead > tr > th) {
  background-color: #f8f9fa;
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.5px;
}

:deep(.p-datatable .p-datatable-tbody > tr > td) {
  padding: 0.75rem 1rem;
}

:deep(.p-datatable .p-datatable-tbody > tr:hover) {
  background-color: #f8f9fa;
  cursor: pointer;
}
</style>
