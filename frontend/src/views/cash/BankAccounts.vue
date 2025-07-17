<template>
  <div class="bank-accounts">
    <div class="flex justify-content-between align-items-center mb-4">
      <h1>Bank Accounts</h1>
      <div class="flex">
        <Button 
          icon="pi pi-download" 
          label="Export"
          class="p-button-outlined p-button-secondary mr-2"
          @click="exportDialogVisible = true"
          :loading="exportLoading"
        />
        <Button 
          label="Add Bank Account" 
          icon="pi pi-plus" 
          @click="openNewAccountDialog"
        />
      </div>
    </div>

    <!-- Bank Accounts Summary Cards -->
    <div class="grid mb-4">
      <div class="col-12 md:col-6 lg:col-3">
        <Card class="h-full">
          <template #title>Total Balance</template>
          <template #content>
            <div class="text-4xl font-bold text-primary">
              {{ formatCurrency(totalBalance, 'USD') }}
            </div>
            <div class="text-sm text-500 mt-2">Across all accounts</div>
          </template>
        </Card>
      </div>
      <div class="col-12 md:col-6 lg:col-3">
        <Card class="h-full">
          <template #title>Active Accounts</template>
          <template #content>
            <div class="text-4xl font-bold text-primary">
              {{ activeAccountsCount }}
            </div>
            <div class="text-sm text-500 mt-2">Out of {{ bankAccounts.length }} total</div>
          </template>
        </Card>
      </div>
      <div class="col-12 md:col-6 lg:col-3">
        <Card class="h-full">
          <template #title>This Month</template>
          <template #content>
            <div class="flex align-items-center">
              <span class="text-4xl font-bold mr-2" :class="monthlyChange >= 0 ? 'text-green-500' : 'text-red-500'">
                {{ formatCurrency(monthlyChange, 'USD') }}
              </span>
              <span class="text-sm" :class="monthlyChange >= 0 ? 'text-green-500' : 'text-red-500'">
                <i :class="monthlyChange >= 0 ? 'pi pi-arrow-up' : 'pi pi-arrow-down'" class="mr-1"></i>
                {{ Math.abs(monthlyChangePercent) }}%
              </span>
            </div>
            <div class="text-sm text-500 mt-2">Net change this month</div>
          </template>
        </Card>
      </div>
      <div class="col-12 md:col-6 lg:col-3">
        <Card class="h-full">
          <template #title>Next 30 Days</template>
          <template #content>
            <div class="text-4xl font-bold" :class="projectedBalance >= 0 ? 'text-primary' : 'text-red-500'">
              {{ formatCurrency(projectedBalance, 'USD') }}
            </div>
            <div class="text-sm text-500 mt-2">Projected balance</div>
          </template>
        </Card>
      </div>
    </div>

    <!-- Bank Accounts Table -->
    <Card>
      <template #header>
        <div class="flex justify-content-between align-items-center">
          <h2>Bank Accounts</h2>
          <span class="p-input-icon-left">
            <i class="pi pi-search" />
            <InputText 
              v-model="filters['global'].value" 
              placeholder="Search accounts..." 
              class="p-inputtext-sm" 
            />
          </span>
        </div>
      </template>
      
      <template #content>
        <DataTable 
          :value="filteredAccounts" 
          :paginator="true" 
          :rows="10"
          :rowsPerPageOptions="[5, 10, 25, 50]"
          :loading="loading"
          :filters="filters"
          :globalFilterFields="['name', 'account_number', 'bank_name', 'account_type']"
          responsiveLayout="scroll"
          class="p-datatable-sm"
          currentPageReportTemplate="Showing {first} to {last} of {totalRecords} entries"
          paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
        >
          <Column field="name" header="Account Name" :sortable="true" style="min-width: 200px">
            <template #body="{ data }">
              <div class="flex align-items-center">
                <div class="mr-3" :class="getAccountStatusClass(data)">
                  <i :class="getAccountIcon(data.account_type)" class="text-xl"></i>
                </div>
                <div>
                  <div class="font-medium">{{ data.name }}</div>
                  <div class="text-500 text-sm">{{ data.account_number }}</div>
                </div>
              </div>
            </template>
          </Column>
          
          <Column field="bank_name" header="Bank" :sortable="true" style="min-width: 150px" />
          
          <Column field="account_type" header="Type" :sortable="true" style="min-width: 120px">
            <template #body="{ data }">
              <Tag :value="formatAccountType(data.account_type)" :severity="getAccountTypeSeverity(data.account_type)" />
            </template>
          </Column>
          
          <Column field="currency" header="Currency" :sortable="true" style="min-width: 100px" />
          
          <Column field="current_balance" header="Balance" :sortable="true" style="min-width: 150px" class="text-right">
            <template #body="{ data }">
              <div class="font-bold" :class="data.current_balance >= 0 ? 'text-green-500' : 'text-red-500'">
                {{ formatCurrency(data.current_balance, data.currency) }}
              </div>
              <div class="text-500 text-sm">
                {{ formatCurrency(data.available_balance || data.current_balance, data.currency) }} available
              </div>
            </template>
          </Column>
          
          <Column field="status" header="Status" :sortable="true" style="min-width: 120px">
            <template #body="{ data }">
              <Tag 
                :value="data.is_active ? 'Active' : 'Inactive'" 
                :severity="data.is_active ? 'success' : 'danger'" 
              />
            </template>
          </Column>
          
          <Column headerStyle="width: 120px; text-align: center" bodyStyle="text-align: center; overflow: visible">
            <template #body="{ data }">
              <div class="flex justify-content-center">
                <Button 
                  icon="pi pi-pencil" 
                  class="p-button-text p-button-sm p-button-rounded" 
                  @click="editAccount(data)"
                  v-tooltip.top="'Edit'"
                />
                <Button 
                  icon="pi pi-trash" 
                  class="p-button-text p-button-sm p-button-rounded p-button-danger" 
                  @click="confirmDeleteAccount(data)"
                  v-tooltip.top="'Delete'"
                />
              </div>
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <!-- Account Dialog -->
    <Dialog 
      v-model:visible="accountDialog" 
      :header="editing ? 'Edit Bank Account' : 'New Bank Account'" 
      :modal="true"
      :style="{ width: '600px' }"
      @hide="closeAccountDialog"
    >
      <form @submit.prevent="saveAccount">
        <div class="grid">
          <div class="col-12 md:col-6">
            <div class="field">
              <label for="name">Account Name <span class="text-red-500">*</span></label>
              <InputText 
                id="name" 
                v-model="account.name" 
                class="w-full" 
                :class="{ 'p-invalid': submitted && !account.name }"
              />
              <small v-if="submitted && !account.name" class="p-error">Account name is required.</small>
            </div>
            
            <div class="field">
              <label for="account_number">Account Number <span class="text-red-500">*</span></label>
              <InputText 
                id="account_number" 
                v-model="account.account_number" 
                class="w-full" 
                :class="{ 'p-invalid': submitted && !account.account_number }"
              />
              <small v-if="submitted && !account.account_number" class="p-error">Account number is required.</small>
            </div>
            
            <div class="field">
              <label for="routing_number">Routing Number</label>
              <InputText id="routing_number" v-model="account.routing_number" class="w-full" />
            </div>
          </div>
          
          <div class="col-12 md:col-6">
            <div class="field">
              <label for="bank_name">Bank Name <span class="text-red-500">*</span></label>
              <InputText 
                id="bank_name" 
                v-model="account.bank_name" 
                class="w-full" 
                :class="{ 'p-invalid': submitted && !account.bank_name }"
              />
              <small v-if="submitted && !account.bank_name" class="p-error">Bank name is required.</small>
            </div>
            
            <div class="field">
              <label for="account_type">Account Type <span class="text-red-500">*</span></label>
              <Dropdown 
                id="account_type"
                v-model="account.account_type"
                :options="accountTypes"
                optionLabel="label"
                optionValue="value"
                placeholder="Select a type"
                class="w-full"
                :class="{ 'p-invalid': submitted && !account.account_type }"
              />
              <small v-if="submitted && !account.account_type" class="p-error">Account type is required.</small>
            </div>
            
            <div class="field">
              <label for="currency">Currency <span class="text-red-500">*</span></label>
              <Dropdown 
                id="currency"
                v-model="account.currency"
                :options="currencies"
                optionLabel="code"
                optionValue="code"
                placeholder="Select currency"
                class="w-full"
                :class="{ 'p-invalid': submitted && !account.currency }"
              />
              <small v-if="submitted && !account.currency" class="p-error">Currency is required.</small>
            </div>
          </div>
          
          <div class="col-12">
            <div class="field">
              <label for="notes">Notes</label>
              <Textarea id="notes" v-model="account.notes" rows="2" class="w-full" />
            </div>
          </div>
        </div>
        
        <template #footer>
          <Button 
            label="Cancel" 
            icon="pi pi-times" 
            class="p-button-text"
            @click="closeAccountDialog"
          />
          <Button 
            :label="editing ? 'Update' : 'Create'" 
            icon="pi pi-check"
            type="submit"
            :loading="saving"
          />
        </template>
      </form>
    </Dialog>
    
    <!-- Delete Confirmation Dialog -->
    <Dialog 
      v-model:visible="deleteAccountDialog" 
      header="Confirm Delete" 
      :modal="true" 
      :style="{ width: '450px' }"
    >
      <div class="confirmation-content">
        <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
        <span v-if="account">
          Are you sure you want to delete <b>{{ account.name }}</b>? This action cannot be undone.
        </span>
      </div>
      <template #footer>
        <Button 
          label="No" 
          icon="pi pi-times" 
          class="p-button-text"
          @click="deleteAccountDialog = false"
        />
        <Button 
          label="Yes" 
          icon="pi pi-check" 
          class="p-button-danger"
          @click="deleteAccount"
          :loading="deleting"
        />
      </template>
    </Dialog>
    
    <!-- Export Dialog -->
    <ReportExportDialog
      v-model:visible="exportDialogVisible"
      :loading="exportLoading"
      title="Export Bank Accounts"
      @export="handleExport"
    />
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue';
import { useToast } from 'primevue/usetoast';
import { formatCurrency, formatDate } from '@/utils/formatters';
import BankAccountService from '@/services/BankAccountService';
import ReportExportDialog from '@/components/common/ReportExportDialog.vue';

export default {
  name: 'BankAccounts',
  
  setup() {
    const toast = useToast();
    
    // State
    const loading = ref(false);
    const saving = ref(false);
    const deleting = ref(false);
    const submitted = ref(false);
    const accountDialog = ref(false);
    const deleteAccountDialog = ref(false);
    const editing = ref(false);
    const bankAccounts = ref([]);
    const account = ref({});
    const filters = ref({
      'global': { value: null, matchMode: 'contains' },
    });
    
    // Constants
    const accountTypes = [
      { label: 'Checking', value: 'checking' },
      { label: 'Savings', value: 'savings' },
      { label: 'Credit Card', value: 'credit_card' },
      { label: 'Money Market', value: 'money_market' },
      { label: 'Investment', value: 'investment' },
      { label: 'Loan', value: 'loan' },
      { label: 'Other', value: 'other' },
    ];
    
    const currencies = [
      { code: 'USD', name: 'US Dollar' },
      { code: 'EUR', name: 'Euro' },
      { code: 'GBP', name: 'British Pound' },
      { code: 'JPY', name: 'Japanese Yen' },
      { code: 'AUD', name: 'Australian Dollar' },
      { code: 'CAD', name: 'Canadian Dollar' },
      { code: 'PKR', name: 'Pakistani Rupee' },
      { code: 'AED', name: 'UAE Dirham' },
      { code: 'SAR', name: 'Saudi Riyal' },
    ];
    
    // Computed
    const filteredAccounts = computed(() => {
      if (!filters.value.global.value) return bankAccounts.value;
      
      const search = filters.value.global.value.toLowerCase();
      return bankAccounts.value.filter(account => {
        return (
          (account.name && account.name.toLowerCase().includes(search)) ||
          (account.account_number && account.account_number.toLowerCase().includes(search)) ||
          (account.bank_name && account.bank_name.toLowerCase().includes(search)) ||
          (account.account_type && account.account_type.toLowerCase().includes(search))
        );
      });
    });
    
    const totalBalance = computed(() => {
      return bankAccounts.value.reduce((sum, acc) => sum + (acc.current_balance || 0), 0);
    });
    
    const activeAccountsCount = computed(() => {
      return bankAccounts.value.filter(acc => acc.is_active).length;
    });
    
    const monthlyChange = computed(() => 1250.75); // Mock data
    const monthlyChangePercent = computed(() => (monthlyChange.value / (totalBalance.value - monthlyChange.value) * 100).toFixed(2));
    const projectedBalance = computed(() => totalBalance.value * 1.02); // Simple 2% projection
    
    // Methods
    const loadBankAccounts = async () => {
      try {
        loading.value = true;
        const response = await BankAccountService.getBankAccounts();
        bankAccounts.value = response.data || [];
      } catch (error) {
        console.error('Error loading bank accounts:', error);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to load bank accounts',
          life: 5000
        });
      } finally {
        loading.value = false;
      }
    };
    
    const openNewAccountDialog = () => {
      account.value = {
        name: '',
        account_number: '',
        bank_name: '',
        account_type: 'checking',
        currency: 'USD',
        opening_balance: 0,
        is_active: true
      };
      editing.value = false;
      submitted.value = false;
      accountDialog.value = true;
    };
    
    const editAccount = (acc) => {
      account.value = { ...acc };
      editing.value = true;
      submitted.value = false;
      accountDialog.value = true;
    };
    
    const closeAccountDialog = () => {
      accountDialog.value = false;
      account.value = {};
      submitted.value = false;
    };
    
    const saveAccount = async () => {
      submitted.value = true;
      
      // Validate form
      if (!account.value.name || !account.value.account_number || 
          !account.value.bank_name || !account.value.account_type || 
          !account.value.currency) {
        return;
      }
      
      try {
        saving.value = true;
        
        if (editing.value) {
          await BankAccountService.updateBankAccount(account.value.id, account.value);
          toast.add({
            severity: 'success',
            summary: 'Success',
            detail: 'Account updated successfully',
            life: 3000
          });
        } else {
          await BankAccountService.createBankAccount(account.value);
          toast.add({
            severity: 'success',
            summary: 'Success',
            detail: 'Account created successfully',
            life: 3000
          });
        }
        
        await loadBankAccounts();
        accountDialog.value = false;
        account.value = {};
        
      } catch (error) {
        console.error('Error saving bank account:', error);
        
        let errorMessage = editing.value ? 'Failed to update account' : 'Failed to create account';
        if (error.response?.data?.detail) {
          errorMessage = error.response.data.detail;
        } else if (error.response?.data?.errors) {
          errorMessage = Object.values(error.response.data.errors).flat().join(' ');
        }
        
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: errorMessage,
          life: 5000
        });
      } finally {
        saving.value = false;
      }
    };
    
    const confirmDeleteAccount = (acc) => {
      account.value = { ...acc };
      deleteAccountDialog.value = true;
    };
    
    const deleteAccount = async () => {
      if (!account.value.id) {
        deleteAccountDialog.value = false;
        return;
      }
      
      try {
        deleting.value = true;
        
        await BankAccountService.deleteBankAccount(account.value.id);
        
        toast.add({
          severity: 'success',
          summary: 'Success',
          detail: 'Account deleted successfully',
          life: 3000
        });
        
        await loadBankAccounts();
        deleteAccountDialog.value = false;
        account.value = {};
        
      } catch (error) {
        console.error('Error deleting bank account:', error);
        
        let errorMessage = 'Failed to delete account';
        if (error.response?.data?.detail) {
          errorMessage = error.response.data.detail;
        }
        
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: errorMessage,
          life: 5000
        });
      } finally {
        deleting.value = false;
      }
    };
    
    const getAccountIcon = (type) => {
      switch (type) {
        case 'savings': return 'pi pi-wallet';
        case 'credit_card': return 'pi pi-credit-card';
        case 'investment': return 'pi pi-chart-line';
        case 'loan': return 'pi pi-money-bill';
        default: return 'pi pi-credit-card';
      }
    };
    
    const getAccountStatusClass = (account) => {
      if (!account.is_active) return 'text-400';
      const balance = account.current_balance || 0;
      return balance < 0 ? 'text-red-500' : balance === 0 ? 'text-500' : 'text-green-500';
    };
    
    const formatAccountType = (type) => {
      if (!type) return '';
      return type.split('_').map(word => 
        word.charAt(0).toUpperCase() + word.slice(1)
      ).join(' ');
    };
    
    const getAccountTypeSeverity = (type) => {
      switch (type) {
        case 'checking': return 'primary';
        case 'savings': return 'success';
        case 'credit_card': return 'danger';
        case 'investment': return 'info';
        case 'loan': return 'warning';
        default: return 'secondary';
      }
    };
    
    const exportDialogVisible = ref(false);
    const exportLoading = ref(false);

    const getExportData = () => {
      return bankAccounts.value.map(account => ({
        'Account Name': account.name,
        'Bank Name': account.bank_name,
        'Account Number': account.account_number,
        'Account Type': formatAccountType(account.account_type),
        'Currency': account.currency,
        'Current Balance': formatCurrency(account.current_balance, account.currency),
        'Status': account.is_active ? 'Active' : 'Inactive',
        'Opening Date': formatDate(account.opening_date),
        'Last Updated': formatDate(account.updated_at)
      }));
    };

    const handleExport = async (format, options = {}) => {
      exportLoading.value = true;
      
      try {
        const data = getExportData();
        const exportService = (await import('@/services/ExportService')).default;
        const title = 'Bank Accounts Report';
        
        switch (format) {
          case 'pdf':
            await exportService.exportToPDF(data, Object.keys(data[0] || {}), title, 'bank_accounts', options);
            break;
          case 'excel':
            await exportService.exportToExcel(data, 'bank_accounts', options);
            break;
          case 'csv':
            await exportService.exportToCSV(data, 'bank_accounts', options);
            break;
          case 'print':
            await exportService.printTable(data, Object.keys(data[0] || {}), title, options);
            break;
        }
        
        toast.add({
          severity: 'success',
          summary: 'Export Successful',
          detail: `Bank accounts exported to ${format.toUpperCase()} successfully`,
          life: 3000
        });
      } catch (error) {
        console.error('Export error:', error);
        toast.add({
          severity: 'error',
          summary: 'Export Failed',
          detail: error.message || 'Failed to export bank accounts',
          life: 5000
        });
        throw error;
      } finally {
        exportLoading.value = false;
      }
    };
    
    // Lifecycle hooks
    onMounted(() => {
      loadBankAccounts();
    });
    
    return {
      // State
      loading,
      saving,
      deleting,
      submitted,
      accountDialog,
      deleteAccountDialog,
      editing,
      bankAccounts,
      account,
      filters,
      
      // Computed
      filteredAccounts,
      totalBalance,
      activeAccountsCount,
      monthlyChange,
      monthlyChangePercent,
      projectedBalance,
      
      // Constants
      accountTypes,
      currencies,
      
      // Methods
      formatCurrency,
      exportDialogVisible,
      exportLoading,
      openNewAccountDialog,
      editAccount,
      closeAccountDialog,
      saveAccount,
      confirmDeleteAccount,
      deleteAccount,
      getAccountIcon,
      getAccountStatusClass,
      formatAccountType,
      getAccountTypeSeverity,
      handleExport
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
  font-size: 0.875rem;
}

:deep(.p-datatable .p-datatable-thead > tr > th) {
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.5px;
}

:deep(.p-datatable .p-datatable-tbody > tr > td) {
  padding: 0.5rem 1rem;
}

:deep(.p-datatable .p-datatable-tbody > tr.p-highlight) {
  background-color: #f0f9ff;
  color: #0369a1;
}

:deep(.p-datatable .p-datatable-tbody > tr:hover) {
  background-color: #f8fafc;
  cursor: pointer;
}

:deep(.p-datatable .p-paginator) {
  padding: 0.5rem 1rem;
  background: transparent;
  border: none;
}

:deep(.p-datatable .p-sortable-column:not(.p-highlight):hover) {
  background: #f1f5f9;
}

:deep(.p-datatable .p-sortable-column.p-highlight) {
  background: #e0f2fe;
  color: #0369a1;
}

:deep(.p-datatable .p-sortable-column.p-highlight:hover) {
  background: #e0f2fe;
  color: #0369a1;
}

:deep(.p-datatable .p-datatable-tbody > tr > td .p-button.p-button-text) {
  color: #64748b;
}

:deep(.p-datatable .p-datatable-tbody > tr > td .p-button.p-button-text:hover) {
  color: #0ea5e9;
  background: #f0f9ff;
}

:deep(.p-datatable .p-datatable-tbody > tr > td .p-button.p-button-text.p-button-danger) {
  color: #ef4444;
}

:deep(.p-datatable .p-datatable-tbody > tr > td .p-button.p-button-text.p-button-danger:hover) {
  color: #dc2626;
  background: #fef2f2;
}

:deep(.p-dialog .p-dialog-header) {
  border-bottom: 1px solid #e2e8f0;
  padding: 1.25rem 1.5rem;
}

:deep(.p-dialog .p-dialog-content) {
  padding: 1.5rem;
}

:deep(.p-dialog .p-dialog-footer) {
  border-top: 1px solid #e2e8f0;
  padding: 1.25rem 1.5rem;
}

.field {
  margin-bottom: 1.25rem;
}

.field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.field-checkbox {
  display: flex;
  align-items: center;
}

.field-checkbox label {
  margin-bottom: 0;
  margin-left: 0.5rem;
}
</style>
