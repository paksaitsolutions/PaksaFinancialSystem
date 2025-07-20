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

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { formatCurrency, formatDate } from '@/utils/formatters';

// Toast implementation
interface ToastMessage {
  severity: 'success' | 'info' | 'warn' | 'error';
  summary: string;
  detail: string;
  life?: number;
}

const useToast = () => {
  const add = (message: ToastMessage) => {
    console.log('Toast:', message);
  };
  
  return { add };
};

const toast = useToast();

interface BankAccount {
  id: string | number;
  name: string;
  account_number: string;
  bank_name: string;
  account_type: string;
  currency: string;
  current_balance: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  last_reconciled: string;
  opening_balance: number;
  opening_date: string;
  notes?: string;
}

interface Filter {
  [key: string]: {
    value: any;
    matchMode: string;
  };
}

interface ExportData {
  [key: string]: string | number | undefined;
}

interface ExportOptions {
  [key: string]: any;
}

const bankAccounts = ref<BankAccount[]>([]);
const account = ref<Partial<BankAccount>>({});
const accountDialog = ref(false);
const deleteAccountDialog = ref(false);
const editing = ref(false);
const loading = ref(true);
const submitted = ref(false);
const exportLoading = ref(false);
const exportDialogVisible = ref(false);
const toast = useToast() as ToastServiceMethods;

const filters = ref<Filter>({
  global: { value: null, matchMode: 'contains' },
  name: { value: null, matchMode: 'contains' },
  bank_name: { value: null, matchMode: 'contains' },
  account_number: { value: null, matchMode: 'contains' },
  current_balance: { value: null, matchMode: 'equals' },
  is_active: { value: null, matchMode: 'equals' }
});

const accountTypes = [
  { label: 'Checking', value: 'checking' },
  { label: 'Savings', value: 'savings' },
  { label: 'Credit Card', value: 'credit_card' },
  { label: 'Investment', value: 'investment' },
  { label: 'Loan', value: 'loan' },
  { label: 'Other', value: 'other' }
] as const;

type AccountType = typeof accountTypes[number]['value'];

const currencies = [
  { label: 'PKR - Pakistani Rupee', value: 'PKR' },
  { label: 'USD - US Dollar', value: 'USD' },
  { label: 'EUR - Euro', value: 'EUR' },
  { label: 'GBP - British Pound', value: 'GBP' },
  { label: 'AED - UAE Dirham', value: 'AED' },
  { label: 'SAR - Saudi Riyal', value: 'SAR' }
] as const;

type Currency = typeof currencies[number]['value'];

// Computed properties
const filteredAccounts = computed(() => {
  const search = filters.value.global.value ? String(filters.value.global.value).toLowerCase() : '';
  if (!search) return bankAccounts.value;
  
  return bankAccounts.value.filter((account) => {
    const nameMatch = account.name.toLowerCase().includes(search);
    const numberMatch = account.account_number.toLowerCase().includes(search);
    const bankMatch = account.bank_name.toLowerCase().includes(search);
    return nameMatch || numberMatch || bankMatch;
  });
});

const activeAccountsCount = computed(() => {
  return bankAccounts.value.filter(acc => acc.is_active).length;
});

const monthlyChangePercent = computed(() => {
  // Mock data - in a real app, this would calculate the actual change
  return 2.5;
});

const projectedBalance = computed(() => {
  // Mock data - in a real app, this would calculate the projected balance
  return bankAccounts.value.reduce((sum, acc) => sum + (acc.current_balance || 0), 0) * 1.1;
});

const totalBalance = computed(() => {
  return bankAccounts.value.reduce((sum, acc) => sum + (acc.current_balance || 0), 0);
});

const activeAccountsCount = computed(() => {
  return bankAccounts.value.filter(acc => acc.is_active).length;
});

const monthlyChange = computed(() => 1250.75); // Mock data
const monthlyChangePercent = computed(() => {
  const change = monthlyChange.value;
  const balance = totalBalance.value - change;
  return balance !== 0 ? ((change / balance) * 100).toFixed(2) : '0.00';
});
const projectedBalance = computed(() => totalBalance.value * 1.02); // Simple 2% projection

// Methods
const loadBankAccounts = async () => {
  loading.value = true;
  try {
    // In a real app, this would be an API call
    await new Promise(resolve => setTimeout(resolve, 500));
    
    const mockBankAccounts: BankAccount[] = [
      {
        id: 1,
        name: 'Main Business Account',
        account_number: '1234567890',
        bank_name: 'HBL',
        account_type: 'checking',
        currency: 'PKR',
        current_balance: 1500000,
        is_active: true,
        created_at: '2023-01-15',
        updated_at: '2023-11-30',
        last_reconciled: '2023-11-30',
        opening_balance: 1000000,
        opening_date: '2023-01-15',
        notes: ''
      },
      {
        id: 2,
        name: 'Savings Account',
        account_number: '9876543210',
        bank_name: 'Meezan Bank',
        account_type: 'savings',
        currency: 'PKR',
        current_balance: 500000,
        is_active: true,
        created_at: '2023-02-20',
        updated_at: '2023-11-30',
        last_reconciled: '2023-11-30',
        opening_balance: 200000,
        opening_date: '2023-02-20',
        notes: ''
      },
      {
        id: 3,
        name: 'USD Account',
        account_number: '1122334455',
        bank_name: 'HBL',
        account_type: 'checking',
        currency: 'USD',
        current_balance: 5000,
        is_active: true,
        created_at: '2023-03-10',
        updated_at: '2023-11-30',
        last_reconciled: '2023-11-30',
        opening_balance: 3000,
        opening_date: '2023-03-10',
        notes: ''
      }
    ];
    
    bankAccounts.value = mockBankAccounts;
  } catch (error) {
    console.error('Failed to load bank accounts:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load bank accounts',
      life: 3000
    });
  } finally {
    loading.value = false;
  }
};

const openNewAccountDialog = () => {
  account.value = {
    id: Math.floor(Math.random() * 10000) + 1000, // Generate a random ID for demo
    name: '',
    account_number: '',
    bank_name: '',
    account_type: 'checking',
    currency: 'PKR',
    current_balance: 0,
    is_active: true,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    last_reconciled: new Date().toISOString(),
    opening_balance: 0,
    opening_date: new Date().toISOString(),
    notes: ''
  };
  editing.value = false;
  submitted.value = false;
  accountDialog.value = true;
};

const editAccount = (acc: BankAccount) => {
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
  
  if (!account.value?.name || !account.value?.account_number || !account.value?.bank_name) {
    return;
  }
  
  loading.value = true;
  
  try {
    if (editing.value && account.value.id) {
      // Update existing account
      const index = bankAccounts.value.findIndex(acc => acc.id === account.value?.id);
      if (index !== -1) {
        const updatedAccount: BankAccount = {
          ...bankAccounts.value[index],
          ...account.value,
          updated_at: new Date().toISOString(),
          // Ensure required fields are not undefined
          name: account.value.name || bankAccounts.value[index].name,
          account_number: account.value.account_number || bankAccounts.value[index].account_number,
          bank_name: account.value.bank_name || bankAccounts.value[index].bank_name,
          account_type: account.value.account_type || bankAccounts.value[index].account_type || 'checking',
          currency: account.value.currency || bankAccounts.value[index].currency || 'PKR',
          current_balance: account.value.current_balance || 0,
          is_active: account.value.is_active ?? true,
          opening_balance: account.value.opening_balance || 0,
          opening_date: account.value.opening_date || new Date().toISOString(),
          last_reconciled: account.value.last_reconciled || new Date().toISOString(),
          notes: account.value.notes || ''
        };
        
        bankAccounts.value[index] = updatedAccount;
      }
      
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Bank account updated successfully',
        life: 3000
      });
    } else {
      // Add new account
      const newAccount: BankAccount = {
        id: Math.max(0, ...bankAccounts.value.map(acc => Number(acc.id) || 0)) + 1,
        name: account.value.name || '',
        account_number: account.value.account_number || '',
        bank_name: account.value.bank_name || '',
        account_type: account.value.account_type || 'checking',
        currency: account.value.currency || 'PKR',
        current_balance: account.value.current_balance || 0,
        is_active: true,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        last_reconciled: new Date().toISOString(),
        opening_balance: account.value.opening_balance || 0,
        opening_date: account.value.opening_date || new Date().toISOString(),
        notes: account.value.notes || ''
      };
      
      bankAccounts.value = [...bankAccounts.value, newAccount];
      
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Bank account created successfully',
        life: 3000
      });
    }
    
    // Reset form
    accountDialog.value = false;
    account.value = {
      id: 0,
      name: '',
      account_number: '',
      bank_name: '',
      account_type: 'checking',
      currency: 'PKR',
      current_balance: 0,
      is_active: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      last_reconciled: new Date().toISOString(),
      opening_balance: 0,
      opening_date: new Date().toISOString(),
      notes: ''
    };
  } catch (error) {
    console.error('Error saving bank account:', error);
    const errorMessage = error instanceof Error ? error.message : 'Failed to save bank account';
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: errorMessage,
      life: 5000
    });
  } finally {
    loading.value = false;
  }
};

const confirmDeleteAccount = (acc: BankAccount) => {
  account.value = { ...acc };
  deleteAccountDialog.value = true;
};

const deleteAccount = async () => {
  if (!account.value.id) {
    deleteAccountDialog.value = false;
    return;
  }

  try {
    loading.value = true;
    
    // Mock delete - filter out the account with the given ID
    bankAccounts.value = bankAccounts.value.filter(acc => acc.id !== account.value.id);
    
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Bank account deleted successfully',
      life: 3000
    });
  } catch (error: unknown) {
    console.error('Error deleting bank account:', error);
    const errorMessage = error instanceof Error ? error.message : 'Failed to delete bank account. Please try again.';
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: errorMessage,
      life: 5000
    });
  } finally {
    loading.value = false;
    deleteAccountDialog.value = false;
  }
};

const getAccountIcon = (type: string = ''): string => {
  switch (type) {
    case 'savings': return 'pi pi-wallet';
    case 'credit_card': return 'pi pi-credit-card';
    case 'checking': return 'pi pi-credit-card';
    case 'investment': return 'pi pi-chart-line';
    case 'loan': return 'pi pi-credit-card';
    default: return 'pi pi-money-bill';
  }
};

const getAccountStatusClass = (account: Partial<BankAccount>): string => {
  if (!account.is_active) return 'text-400';
  const balance = account.current_balance ?? 0;
  if (balance < 0) return 'text-red-500';
  if (balance === 0) return 'text-500';
  return 'text-green-500';
};

const formatAccountType = (type: string = ''): string => {
  if (!type) return '';
  return type
    .split('_')
    .map((word: string) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

const getAccountTypeSeverity = (type: string = ''): string => {
  switch (type) {
    case 'checking': return 'primary';
    case 'savings': return 'success';
    case 'credit_card': return 'danger';
    case 'investment': return 'warning';
    case 'loan': return 'danger';
    default: return 'info';
  }
};

interface ExportData {
  [key: string]: string | number | undefined;
}

const getExportData = (): ExportData[] => {
  return bankAccounts.value.map((account: BankAccount) => ({
    'Account Name': account.name ?? '',
    'Bank Name': account.bank_name ?? '',
    'Account Number': account.account_number ?? '',
    'Type': formatAccountType(account.account_type),
    'Currency': account.currency ?? '',
    'Balance': account.current_balance ?? 0,
    'Status': account.is_active ? 'Active' : 'Inactive',
    'Last Reconciled': account.last_reconciled ?? 'Never',
    'Opening Balance': account.opening_balance ?? 0,
    'Opening Date': account.opening_date ?? 'N/A',
    'Created At': account.created_at ?? 'N/A',
    'Updated At': account.updated_at ?? 'N/A'
  }));
};

interface ExportOptions {
  [key: string]: any;
}

const handleExport = async (format: 'pdf' | 'excel' | 'csv' | 'print', options: ExportOptions = {}) => {
  exportLoading.value = true;
  
  try {
    const data = getExportData();
    const fileName = `bank-accounts-${new Date().toISOString().split('T')[0]}`;
    
    console.log(`Exporting ${data.length} accounts to ${format}`, { options });
    
    // Show export started message
    toast.add({
      severity: 'info',
      summary: 'Export Started',
      detail: `Preparing to export ${data.length} accounts to ${format.toUpperCase()} format`,
      life: 3000
    });
    
    // Simulate export delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Create a blob and download link for the export
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${fileName}.${format}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    // Show success message
    toast.add({
      severity: 'success',
      summary: 'Export Complete',
      detail: `Successfully exported ${data.length} accounts to ${fileName}.${format}`,
      life: 5000
    });
    
  } catch (error: unknown) {
    console.error('Error exporting data:', error);
    const errorMessage = error instanceof Error ? error.message : 'Failed to export bank accounts. Please try again.';
    toast.add({
      severity: 'error',
      summary: 'Export Failed',
      detail: errorMessage,
      life: 5000
    });
  } finally {
    exportLoading.value = false;
    exportDialogVisible.value = false;
  }
};

// Lifecycle hooks
// Lifecycle hooks
onMounted(() => {
  loadBankAccounts();
});

// Expose methods to template
const exposedMethods = {
  openNewAccountDialog,
  editAccount,
  saveAccount,
  confirmDeleteAccount,
  deleteAccount,
  getAccountIcon,
  getAccountStatusClass,
  getAccountTypeSeverity,
  handleExport,
  formatAccountType,
  formatCurrency,
  formatDate
};

// Expose computed properties to template
const exposedComputed = {
  filteredAccounts,
  activeAccountsCount,
  monthlyChangePercent,
  projectedBalance
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
