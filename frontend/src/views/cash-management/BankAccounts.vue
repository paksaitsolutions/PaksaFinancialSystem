<template>
  <div class="p-4">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold">Bank Accounts</h1>
      <Button 
        label="New Account" 
        icon="pi pi-plus" 
        @click="showAccountForm()" 
      />
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'primevue/usetoast';
import { useCurrency } from '@/composables/useCurrency';
import BankAccountService from '@/services/BankAccountService';
import CurrencyService from '@/services/CurrencyService';

const router = useRouter();
const toast = useToast();
const { formatCurrency, getCurrencyCode } = useCurrency();

// State
const accounts = ref([]);
const loading = ref(false);
const displayAccountForm = ref(false);
const displayDeleteDialog = ref(false);
const submitted = ref(false);
const editingAccount = ref(false);
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
