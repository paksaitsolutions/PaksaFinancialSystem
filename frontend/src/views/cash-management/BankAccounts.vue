<template>
  <div class="p-4">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold">Bank Accounts</h1>
      <div class="flex gap-2">
        <Button 
          label="Export" 
          icon="pi pi-download" 
          class="p-button-outlined p-button-success"
          @click="showExportDialog"
        />
        <Button 
          label="Print" 
          icon="pi pi-print" 
          class="p-button-outlined p-button-info"
          @click="printAccounts"
        />
        <Button 
          label="New Account" 
          icon="pi pi-plus" 
          @click="showAccountForm()" 
        />
      </div>
    </div>

    <Card>
      <template #content>
        <DataTable 
          :value="accounts" 
          :paginator="true" 
          :rows="10"
          :loading="loading"
          responsiveLayout="scroll"
          class="p-datatable-sm"
        >
          <Column field="name" header="Account Name" :sortable="true">
            <template #body="{ data }">
              <div class="flex items-center">
                <div class="mr-3">
                  <i class="pi pi-credit-card text-xl"></i>
                </div>
                <div>
                  <div class="font-medium">{{ data.name }}</div>
                  <div class="text-sm text-gray-500">{{ data.account_number }}</div>
                </div>
              </div>
            </template>
          </Column>
          
          <Column field="bank_name" header="Bank" :sortable="true" />
          
          <Column field="current_balance" header="Balance" :sortable="true">
            <template #body="{ data }">
              <div class="text-right">
                <div class="font-medium" :class="data.current_balance >= 0 ? 'text-green-600' : 'text-red-600'">
                  {{ formatCurrency(data.current_balance, data.currency?.code) }}
                </div>
                <div class="text-xs text-gray-500">
                  Available: {{ formatCurrency(data.available_balance, data.currency?.code) }}
                </div>
              </div>
            </template>
          </Column>
          
          <Column field="status" header="Status" :sortable="true">
            <template #body="{ data }">
              <Tag 
                :value="data.is_active ? 'Active' : 'Inactive'" 
                :severity="data.is_active ? 'success' : 'danger'" 
              />
            </template>
          </Column>
          
          <Column header="Actions" style="width: 120px">
            <template #body="{ data }">
              <div class="flex space-x-2">
                <Button 
                  icon="pi pi-pencil" 
                  class="p-button-text p-button-sm" 
                  @click="showAccountForm(data)" 
                />
                <Button 
                  icon="pi pi-trash" 
                  class="p-button-text p-button-sm p-button-danger" 
                  @click="confirmDeleteAccount(data)" 
                />
              </div>
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <!-- Account Form Dialog -->
    <Dialog 
      v-model:visible="displayAccountForm" 
      :header="editingAccount ? 'Edit Bank Account' : 'New Bank Account'" 
      :modal="true"
      :style="{ width: '600px' }"
    >
      <form @submit.prevent="saveAccount">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <!-- Left Column -->
          <div class="space-y-4">
            <div class="field">
              <label for="name">Account Name *</label>
              <InputText 
                id="name" 
                v-model="accountForm.name" 
                class="w-full" 
                :class="{ 'p-invalid': submitted && !accountForm.name }"
              />
              <small v-if="submitted && !accountForm.name" class="p-error">Name is required.</small>
            </div>

            <div class="field">
              <label for="account_number">Account Number *</label>
              <InputText 
                id="account_number" 
                v-model="accountForm.account_number" 
                class="w-full" 
                :class="{ 'p-invalid': submitted && !accountForm.account_number }"
              />
              <small v-if="submitted && !accountForm.account_number" class="p-error">Account number is required.</small>
            </div>

            <div class="field">
              <label for="bank_name">Bank Name *</label>
              <InputText 
                id="bank_name" 
                v-model="accountForm.bank_name" 
                class="w-full" 
                :class="{ 'p-invalid': submitted && !accountForm.bank_name }"
              />
              <small v-if="submitted && !accountForm.bank_name" class="p-error">Bank name is required.</small>
            </div>

            <div class="field">
              <label for="account_type">Account Type *</label>
              <Dropdown 
                id="account_type"
                v-model="accountForm.account_type"
                :options="accountTypes"
                optionLabel="label"
                optionValue="value"
                placeholder="Select a type"
                class="w-full"
                :class="{ 'p-invalid': submitted && !accountForm.account_type }"
              />
              <small v-if="submitted && !accountForm.account_type" class="p-error">Account type is required.</small>
            </div>
          </div>

          <!-- Right Column -->
          <div class="space-y-4">
            <div class="field">
              <label for="currency_id">Currency *</label>
              <Dropdown 
                id="currency_id"
                v-model="accountForm.currency_id"
                :options="currencies"
                optionLabel="code"
                optionValue="id"
                placeholder="Select currency"
                class="w-full"
                :class="{ 'p-invalid': submitted && !accountForm.currency_id }"
              />
              <small v-if="submitted && !accountForm.currency_id" class="p-error">Currency is required.</small>
            </div>

            <div class="field">
              <label for="opening_balance">Opening Balance</label>
              <InputNumber 
                id="opening_balance"
                v-model="accountForm.opening_balance"
                mode="currency"
                :currency="getCurrencyCode(accountForm.currency_id)"
                locale="en-US"
                class="w-full"
              />
            </div>

            <div class="field">
              <label for="opening_balance_date">Balance Date</label>
              <Calendar 
                id="opening_balance_date"
                v-model="accountForm.opening_balance_date"
                dateFormat="yy-mm-dd"
                showIcon
                class="w-full"
              />
            </div>

            <div class="field-checkbox">
              <Checkbox 
                id="is_active" 
                v-model="accountForm.is_active" 
                :binary="true"
              />
              <label for="is_active" class="ml-2">Active</label>
            </div>
          </div>
        </div>

        <div class="flex justify-end gap-2 mt-4">
          <Button 
            label="Cancel" 
            icon="pi pi-times" 
            class="p-button-text" 
            @click="displayAccountForm = false" 
          />
          <Button 
            type="submit" 
            :label="editingAccount ? 'Update' : 'Create'" 
            icon="pi pi-check" 
          />
        </div>
      </form>
    </Dialog>

    <!-- Delete Confirmation Dialog -->
    <Dialog 
      v-model:visible="displayDeleteDialog" 
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
          class="p-button-text" 
          @click="displayDeleteDialog = false" 
        />
        <Button 
          label="Yes" 
          icon="pi pi-check" 
          class="p-button-danger" 
          @click="deleteAccount" 
        />
      </template>
    </Dialog>
    
    <!-- Export Dialog -->
    <ReportExportDialog
      v-model:visible="displayExportDialog"
      :current-item-count="accounts.length"
      :total-items="accounts.length"
      :total-pages="1"
      :has-pagination="false"
      :export-formats="['pdf', 'excel', 'csv']"
      :export-callback="handleExport"
      @schedule="handleScheduleExport"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import ReportExportDialog from '@/components/reports/ReportExportDialog.vue';
import { useToast } from 'primevue/usetoast';
import { useCurrency } from '@/composables/useCurrency';
import BankAccountService from '@/services/BankAccountService';
import CurrencyService from '@/services/CurrencyService';

const router = useRouter();
const toast = useToast();
const { formatCurrency, getCurrencyCode } = useCurrency();

// Refs for template
const actionMenu = ref(null);
const displayExportDialog = ref(false);

// Show export dialog
const showExportDialog = () => {
  displayExportDialog.value = true;
};

// Handle export action
const handleExport = async (params) => {
  try {
    const { format, scope, options } = params;
    let exportData = [];
    
    // In this view, we don't have pagination, so we'll just use all accounts
    exportData = [...accounts.value];
    
    // Format data for export
    const formattedData = exportData.map(account => ({
      'Account Name': account.name,
      'Bank Name': account.bank_name,
      'Account Number': account.account_number,
      'Account Type': account.account_type,
      'Current Balance': formatCurrency(account.current_balance, account.currency?.code),
      'Available Balance': formatCurrency(account.available_balance, account.currency?.code),
      'Currency': account.currency?.code || 'USD',
      'Status': account.is_active ? 'Active' : 'Inactive',
      'Last Updated': formatDate(account.updated_at)
    }));
    
    // In a real app, you would use a library like xlsx, jsPDF, etc.
    console.log(`Exporting ${formattedData.length} accounts to ${format} format`, options);
    
    // Simulate export
    toast.add({
      severity: 'success',
      summary: 'Export Started',
      detail: `Preparing to export ${formattedData.length} accounts to ${format.toUpperCase()} format`,
      life: 3000
    });
    
    // In a real app, you would generate and download the file here
    return new Promise(resolve => {
      setTimeout(() => {
        console.log('Export complete:', { format, data: formattedData });
        resolve();
      }, 1000);
    });
    
  } catch (error) {
    console.error('Export error:', error);
    toast.add({
      severity: 'error',
      summary: 'Export Failed',
      detail: 'Failed to export bank accounts. Please try again.',
      life: 5000
    });
    throw error;
  }
};

// Handle scheduled export
const handleScheduleExport = (params) => {
  console.log('Scheduling export:', params);
  // In a real app, you would save this to a scheduled jobs/tasks system
  toast.add({
    severity: 'info',
    summary: 'Export Scheduled',
    detail: 'Your export has been scheduled and will be processed shortly.',
    life: 5000
  });
};

// Print accounts
const printAccounts = () => {
  const printWindow = window.open('', '_blank');
  
  // Create a print-friendly version
  const printContent = `
    <!DOCTYPE html>
    <html>
    <head>
      <title>Bank Accounts - ${new Date().toLocaleDateString()}</title>
      <style>
        body { font-family: Arial, sans-serif; font-size: 12px; margin: 20px; }
        h1 { color: #333; font-size: 18px; margin-bottom: 10px; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f5f5f5; font-weight: bold; }
        .text-right { text-align: right; }
        .footer { margin-top: 20px; font-size: 11px; color: #666; }
        @media print {
          @page { size: landscape; margin: 1cm; }
          .no-print { display: none; }
        }
      </style>
    </head>
    <body>
      <h1>Bank Accounts</h1>
      <div>Generated on: ${new Date().toLocaleString()}</div>
      
      <table>
        <thead>
          <tr>
            <th>Account Name</th>
            <th>Bank Name</th>
            <th>Account Number</th>
            <th>Type</th>
            <th class="text-right">Current Balance</th>
            <th class="text-right">Available Balance</th>
            <th>Currency</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          ${accounts.value.map(account => `
            <tr>
              <td>${account.name}</td>
              <td>${account.bank_name || 'N/A'}</td>
              <td>${account.account_number || 'N/A'}</td>
              <td>${account.account_type || 'N/A'}</td>
              <td class="text-right">${formatCurrency(account.current_balance, account.currency?.code)}</td>
              <td class="text-right">${formatCurrency(account.available_balance, account.currency?.code)}</td>
              <td>${account.currency?.code || 'USD'}</td>
              <td>${account.is_active ? 'Active' : 'Inactive'}</td>
            </tr>
          `).join('')}
        </tbody>
        <tfoot>
          <tr>
            <td colspan="4" class="text-right"><strong>Total:</strong></td>
            <td class="text-right">
              <strong>${formatCurrency(accounts.value.reduce((sum, acc) => sum + parseFloat(acc.current_balance || 0), 0))}</strong>
            </td>
            <td class="text-right">
              <strong>${formatCurrency(accounts.value.reduce((sum, acc) => sum + parseFloat(acc.available_balance || 0), 0))}</strong>
            </td>
            <td colspan="2"></td>
          </tr>
        </tfoot>
      </table>
      
      <div class="footer">
        <div>Generated by Paksa Financial System</div>
        <div>Page 1 of 1</div>
      </div>
      
      <div class="no-print" style="margin-top: 20px; text-align: center;">
        <button onclick="window.print()" style="padding: 8px 16px; background: #2196F3; color: white; border: none; border-radius: 4px; cursor: pointer;">
          Print Report
        </button>
        <button onclick="window.close()" style="margin-left: 10px; padding: 8px 16px; background: #f44336; color: white; border: none; border-radius: 4px; cursor: pointer;">
          Close
        </button>
      </div>
      
      <script>
        // Auto-print when the window loads
        window.onload = function() {
          setTimeout(function() {
            window.print();
            // Close the window after printing (or after a delay if print was cancelled)
            setTimeout(function() {
              // window.close();
            }, 1000);
          }, 500);
        };
      <\/script>
    </body>
    </html>
  `;
  
  // Write the content to the new window
  printWindow.document.open();
  printWindow.document.write(printContent);
  printWindow.document.close();
};

const loading = ref(false);
const displayAccountForm = ref(false);
const displayDeleteDialog = ref(false);
const submitted = ref(false);
const editingAccount = ref(false);
// ... existing code ...
const accountToDelete = ref(null);
const currencies = ref([]);

// Form data
const accountForm = ref({
  id: null,
  name: '',
  account_number: '',
  account_type: '',
  bank_name: '',
  bank_code: '',
  branch_name: '',
  iban: '',
  currency_id: null,
  is_active: true,
  include_in_cash_flow: true,
  allow_overdraft: false,
  overdraft_limit: 0,
  opening_balance: 0,
  opening_balance_date: new Date(),
});

// Constants
const accountTypes = [
  { label: 'Checking', value: 'checking' },
  { label: 'Savings', value: 'savings' },
  { label: 'Credit Card', value: 'credit_card' },
  { label: 'Loan', value: 'loan' },
  { label: 'Money Market', value: 'money_market' },
  { label: 'Other', value: 'other' },
];

// Lifecycle hooks
onMounted(async () => {
  await Promise.all([
    fetchAccounts(),
    fetchCurrencies(),
  ]);
});

// Methods
const fetchAccounts = async () => {
  try {
    loading.value = true;
    const response = await BankAccountService.getBankAccounts();
    accounts.value = response.data;
  } catch (error) {
    console.error('Error fetching bank accounts:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load bank accounts',
      life: 3000,
    });
  } finally {
    loading.value = false;
  }
};

const fetchCurrencies = async () => {
  try {
    const response = await CurrencyService.getCurrencies();
    currencies.value = response.data;
  } catch (error) {
    console.error('Error fetching currencies:', error);
  }
};

const showAccountForm = (account = null) => {
  editingAccount.value = !!account;
  submitted.value = false;
  
  if (account) {
    // Edit existing account
    const { current_balance, available_balance, ...accountData } = account;
    accountForm.value = {
      ...accountData,
      opening_balance: parseFloat(current_balance) || 0,
      opening_balance_date: new Date(),
    };
  } else {
    // New account
    accountForm.value = {
      id: null,
      name: '',
      account_number: '',
      account_type: '',
      bank_name: '',
      bank_code: '',
      branch_name: '',
      iban: '',
      currency_id: currencies.value[0]?.id || null,
      is_active: true,
      include_in_cash_flow: true,
      allow_overdraft: false,
      overdraft_limit: 0,
      opening_balance: 0,
      opening_balance_date: new Date(),
    };
  }
  
  displayAccountForm.value = true;
};

const saveAccount = async () => {
  submitted.value = true;
  
  // Validate form
  if (
    !accountForm.value.name ||
    !accountForm.value.account_number ||
    !accountForm.value.bank_name ||
    !accountForm.value.account_type ||
    !accountForm.value.currency_id
  ) {
    return;
  }
  
  try {
    const accountData = { ...accountForm.value };
    
    if (editingAccount.value) {
      // Update existing account
      await BankAccountService.updateBankAccount(accountForm.value.id, accountData);
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Bank account updated',
        life: 3000,
      });
    } else {
      // Create new account
      await BankAccountService.createBankAccount(accountData);
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Bank account created',
        life: 3000,
      });
    }
    
    // Refresh accounts and close form
    await fetchAccounts();
    displayAccountForm.value = false;
  } catch (error) {
    console.error('Error saving bank account:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to save bank account',
      life: 3000,
    });
  }
};

const confirmDeleteAccount = (account) => {
  accountToDelete.value = account;
  displayDeleteDialog.value = true;
};

const deleteAccount = async () => {
  if (!accountToDelete.value) return;
  
  try {
    await BankAccountService.deleteBankAccount(accountToDelete.value.id);
    
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Bank account deleted',
      life: 3000,
    });
    
    // Refresh accounts and close dialog
    await fetchAccounts();
    displayDeleteDialog.value = false;
    accountToDelete.value = null;
  } catch (error) {
    console.error('Error deleting bank account:', error);
    
    let errorMessage = 'Failed to delete bank account';
    if (error.response?.data?.detail) {
      errorMessage = error.response.data.detail;
    }
    
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: errorMessage,
      life: 5000,
    });
  }
};
</script>

<style scoped>
.p-card {
  box-shadow: none;
  border: 1px solid var(--surface-d);
}

.confirmation-content {
  display: flex;
  align-items: center;
  padding: 1rem 0;
}
</style>
