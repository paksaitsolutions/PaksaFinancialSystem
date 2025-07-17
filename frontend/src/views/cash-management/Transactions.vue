<template>
  <div class="p-4">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold">Bank Transactions</h1>
      <div class="flex space-x-2">
        <Button 
          label="Import" 
          icon="pi pi-upload" 
          class="p-button-outlined"
          @click="showImportDialog"
        />
        <Button 
          label="New Transaction" 
          icon="pi pi-plus" 
          @click="showTransactionForm()" 
        />
      </div>
    </div>

    <Card>
      <template #content>
        <!-- Summary Cards -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
          <div class="p-3 border-round border-1 border-200">
            <div class="text-500 font-medium mb-1">Total Balance</div>
            <div class="text-2xl font-bold text-primary">{{ formatCurrency(summary.total_balance) }}</div>
          </div>
          <div class="p-3 border-round border-1 border-200">
            <div class="text-500 font-medium mb-1">This Month</div>
            <div class="text-2xl font-bold" :class="summary.monthly_net >= 0 ? 'text-green-600' : 'text-red-600'">
              {{ formatCurrency(summary.monthly_net) }}
            </div>
            <div class="text-sm">
              <span :class="summary.monthly_income >= 0 ? 'text-green-500' : 'text-red-500'">
                <i class="pi pi-arrow-up" v-if="summary.monthly_income >= 0"></i>
                <i class="pi pi-arrow-down" v-else></i>
                {{ formatCurrency(summary.monthly_income) }} income
              </span>
              <span class="mx-2">•</span>
              <span :class="summary.monthly_expense <= 0 ? 'text-green-500' : 'text-red-500'">
                <i class="pi pi-arrow-down" v-if="summary.monthly_expense <= 0"></i>
                <i class="pi pi-arrow-up" v-else></i>
                {{ formatCurrency(Math.abs(summary.monthly_expense)) }} expense
              </span>
            </div>
          </div>
          <div class="p-3 border-round border-1 border-200">
            <div class="text-500 font-medium mb-1">Unreconciled</div>
            <div class="text-2xl font-bold text-orange-600">{{ formatCurrency(summary.unreconciled) }}</div>
            <div class="text-sm">{{ summary.unreconciled_count }} transactions</div>
          </div>
          <div class="p-3 border-round border-1 border-200">
            <div class="text-500 font-medium mb-1">Upcoming</div>
            <div class="text-2xl font-bold text-blue-600">{{ formatCurrency(summary.upcoming) }}</div>
            <div class="text-sm">{{ summary.upcoming_count }} transactions</div>
          </div>
        </div>

        <!-- Filters -->
        <div class="flex flex-wrap gap-2 mb-4">
          <MultiSelect
            v-model="filters.accounts"
            :options="bankAccounts"
            optionLabel="name"
            optionValue="id"
            placeholder="All Accounts"
            display="chip"
            :maxSelectedLabels="1"
            class="w-full md:w-64"
          />
          <span class="p-input-icon-left w-full md:w-auto flex-grow">
            <i class="pi pi-search" />
            <InputText 
              v-model="filters.search" 
              placeholder="Search transactions..." 
              class="w-full"
              @keyup.enter="fetchTransactions"
            />
          </span>
          <Dropdown
            v-model="filters.status"
            :options="statusOptions"
            optionLabel="label"
            optionValue="value"
            placeholder="All Statuses"
            class="w-full md:w-48"
          />
          <Dropdown
            v-model="filters.category"
            :options="categoryOptions"
            optionLabel="label"
            optionValue="value"
            placeholder="All Categories"
            class="w-full md:w-52"
          />
          <Calendar 
            v-model="filters.dateRange" 
            selectionMode="range" 
            :manualInput="false"
            dateFormat="yy-mm-dd"
            placeholder="Date Range"
            class="w-full md:w-64"
            :showIcon="true"
          />
          <Button 
            label="Clear" 
            icon="pi pi-filter-slash" 
            class="p-button-outlined w-full md:w-auto"
            @click="clearFilters"
          />
        </div>

        <!-- Transactions Table -->
        <DataTable 
          :value="transactions" 
          :paginator="true" 
          :rows="25"
          :loading="loading"
          :totalRecords="totalRecords"
          :lazy="true"
          responsiveLayout="scroll"
          class="p-datatable-sm"
          @page="onPage($event)"
          @sort="onSort($event)"
        >
          <Column field="transaction_date" header="Date" :sortable="true" style="min-width: 120px">
            <template #body="{ data }">
              {{ formatDate(data.transaction_date) }}
            </template>
          </Column>
          
          <Column field="account" header="Account" :sortable="true" style="min-width: 180px">
            <template #body="{ data }">
              <div class="flex items-center">
                <div class="mr-2">
                  <i class="pi" :class="getAccountIcon(data.account?.account_type)"></i>
                </div>
                <div>
                  <div class="font-medium">{{ data.account?.name }}</div>
                  <div class="text-xs text-gray-500">{{ data.account?.account_number }}</div>
                </div>
              </div>
            </template>
          </Column>
          
          <Column field="reference" header="Reference" :sortable="true" style="min-width: 160px">
            <template #body="{ data }">
              <div class="font-medium">{{ data.reference || '—' }}</div>
              <div class="text-xs text-gray-500 line-clamp-1">{{ data.description || 'No description' }}</div>
            </template>
          </Column>
          
          <Column field="category" header="Category" :sortable="true" style="min-width: 140px">
            <template #body="{ data }">
              <Tag 
                :value="data.category || 'Uncategorized'" 
                :severity="getCategorySeverity(data.category)"
                class="text-xs"
              />
            </template>
          </Column>
          
          <Column field="amount" header="Amount" :sortable="true" style="min-width: 140px">
            <template #body="{ data }">
              <div class="text-right">
                <div 
                  class="font-bold" 
                  :class="data.amount >= 0 ? 'text-green-600' : 'text-red-600'"
                >
                  {{ formatCurrency(data.amount, data.currency?.code) }}
                </div>
                <div v-if="data.currency?.code !== 'USD'" class="text-xs text-gray-500">
                  {{ formatCurrency(data.amount / (data.exchange_rate || 1), 'USD') }}
                </div>
              </div>
            </template>
          </Column>
          
          <Column field="status" header="Status" :sortable="true" style="min-width: 120px">
            <template #body="{ data }">
              <div class="flex items-center">
                <i 
                  class="pi mr-2" 
                  :class="{
                    'pi-check-circle text-green-500': data.status === 'posted',
                    'pi-clock text-amber-500': data.status === 'pending',
                    'pi-times-circle text-red-500': data.status === 'cancelled',
                    'pi-question-circle text-gray-500': !data.status
                  }"
                ></i>
                <span class="capitalize">{{ data.status || 'unknown' }}</span>
                <i 
                  v-if="data.is_reconciled" 
                  class="pi pi-lock ml-2 text-blue-500" 
                  v-tooltip.top="'Reconciled'"
                ></i>
              </div>
            </template>
          </Column>
          
          <Column header="Actions" style="width: 80px">
            <template #body="{ data }">
              <Button 
                icon="pi pi-ellipsis-v" 
                class="p-button-text p-button-sm"
                @click="toggleActionMenu($event, data)"
                v-tooltip.top="'Actions'"
              />
              
              <Menu 
                ref="actionMenu" 
                :model="actionItems" 
                :popup="true"
                @hide="selectedTransaction = null"
              />
            </template>
          </Column>
          
          <template #empty>
            <div class="p-4 text-center text-gray-500">
              <i class="pi pi-inbox text-4xl mb-2"></i>
              <p>No transactions found</p>
              <Button 
                label="Create Transaction" 
                icon="pi pi-plus" 
                class="mt-4 p-button-sm"
                @click="showTransactionForm()"
              />
            </div>
          </template>
          
          <template #loading>
            <div class="p-4 text-center">
              <i class="pi pi-spin pi-spinner text-2xl"></i>
              <p class="mt-2">Loading transactions...</p>
            </div>
          </template>
        </DataTable>
      </template>
    </Card>

    <!-- Transaction Form Dialog -->
    <TransactionFormDialog 
      v-model:visible="displayTransactionForm"
      :transaction="selectedTransaction"
      :editing="editingTransaction"
      :accounts="bankAccounts"
      @saved="onTransactionSaved"
      @closed="resetTransactionForm"
    />

    <!-- Import Dialog -->
    <ImportDialog 
      v-model:visible="displayImportDialog"
      :accounts="bankAccounts"
      @imported="onImportComplete"
      @closed="resetImportForm"
    />

    <!-- Transaction Details Sidebar -->
    <TransactionDetails 
      v-model:visible="displayTransactionDetails"
      :transaction="selectedTransaction"
      @edit="editSelectedTransaction"
      @delete="confirmDeleteTransaction"
    />

    <!-- Delete Confirmation Dialog -->
    <ConfirmDialog />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import { useCurrency } from '@/composables/useCurrency';
import { useDate } from '@/composables/useDate';
import BankAccountService from '@/services/BankAccountService';
import TransactionService from '@/services/TransactionService';
import TransactionFormDialog from '@/components/transactions/TransactionFormDialog.vue';
import ImportDialog from '@/components/transactions/ImportDialog.vue';
import TransactionDetails from '@/components/transactions/TransactionDetails.vue';

const toast = useToast();
const confirm = useConfirm();
const { formatCurrency, getCurrencyCode } = useCurrency();
const { formatDate, formatDateTime } = useDate();

// State
const transactions = ref([]);
const loading = ref(false);
const totalRecords = ref(0);
const displayTransactionForm = ref(false);
const displayTransactionDetails = ref(false);
const displayImportDialog = ref(false);
const submitted = ref(false);
const editingTransaction = ref(false);
const selectedTransaction = ref(null);
const bankAccounts = ref([]);

// Summary data
const summary = ref({
  total_balance: 0,
  monthly_net: 0,
  monthly_income: 0,
  monthly_expense: 0,
  unreconciled: 0,
  unreconciled_count: 0,
  upcoming: 0,
  upcoming_count: 0
});

// Filter state
const filters = ref({
  accounts: [],
  search: '',
  status: null,
  category: null,
  dateRange: null,
  sortField: 'transaction_date',
  sortOrder: -1,
  page: 1,
  limit: 25
});

// Action menu items
const actionItems = computed(() => [
  {
    label: 'View Details',
    icon: 'pi pi-eye',
    command: () => showTransactionDetails(selectedTransaction.value)
  },
  {
    label: 'Edit',
    icon: 'pi pi-pencil',
    command: () => showTransactionForm(selectedTransaction.value, true)
  },
  {
    label: 'Delete',
    icon: 'pi pi-trash',
    command: () => confirmDeleteTransaction(selectedTransaction.value)
  },
  {
    separator: true
  },
  {
    label: 'Reconcile',
    icon: 'pi pi-check',
    disabled: selectedTransaction.value?.is_reconciled,
    command: () => reconcileTransaction(selectedTransaction.value)
  },
  {
    label: 'Print Receipt',
    icon: 'pi pi-print'
  }
]);

// Lifecycle hooks
onMounted(async () => {
  await Promise.all([
    fetchBankAccounts(),
    fetchTransactions(),
    fetchSummary()
  ]);
});

// Methods
const fetchBankAccounts = async () => {
  try {
    const response = await BankAccountService.getBankAccounts({ is_active: true });
    bankAccounts.value = response.data;
  } catch (error) {
    console.error('Error fetching bank accounts:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load bank accounts',
      life: 3000
    });
  }
};

const fetchTransactions = async () => {
  try {
    loading.value = true;
    
    // Prepare query params
    const params = {
      page: filters.value.page,
      limit: filters.value.limit,
      sort_by: filters.value.sortField,
      sort_order: filters.value.sortOrder === 1 ? 'asc' : 'desc',
      search: filters.value.search,
      status: filters.value.status,
      category: filters.value.category,
      account_ids: filters.value.accounts.join(',')
    };

    // Add date range if set
    if (filters.value.dateRange && filters.value.dateRange.length === 2) {
      params.start_date = formatDate(filters.value.dateRange[0], 'yyyy-MM-dd');
      params.end_date = formatDate(filters.value.dateRange[1], 'yyyy-MM-dd');
    }

    const response = await TransactionService.getTransactions(params);
    transactions.value = response.data.items;
    totalRecords.value = response.data.total;
  } catch (error) {
    console.error('Error fetching transactions:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load transactions',
      life: 3000
    });
  } finally {
    loading.value = false;
  }
};

const fetchSummary = async () => {
  try {
    const response = await TransactionService.getSummary();
    summary.value = response.data;
  } catch (error) {
    console.error('Error fetching transaction summary:', error);
  }
};

const showTransactionForm = (transaction = null, isEditing = false) => {
  selectedTransaction.value = transaction;
  editingTransaction.value = isEditing;
  displayTransactionForm.value = true;
};

const showTransactionDetails = (transaction) => {
  selectedTransaction.value = transaction;
  displayTransactionDetails.value = true;
};

const showImportDialog = () => {
  displayImportDialog.value = true;
};

const resetTransactionForm = () => {
  selectedTransaction.value = null;
  editingTransaction.value = false;
  submitted.value = false;
};

const resetImportForm = () => {
  importFile.value = null;
  importSubmitted.value = false;
};

const clearFilters = () => {
  filters.value = {
    accounts: [],
    search: '',
    status: null,
    category: null,
    dateRange: null,
    sortField: 'transaction_date',
    sortOrder: -1,
    page: 1,
    limit: 25
  };
  fetchTransactions();
};

const onPage = (event) => {
  filters.value.page = event.page + 1;
  filters.value.limit = event.rows;
  fetchTransactions();
};

const onSort = (event) => {
  filters.value.sortField = event.sortField;
  filters.value.sortOrder = event.sortOrder;
  fetchTransactions();
};

const onTransactionSaved = () => {
  fetchTransactions();
  fetchSummary();
  displayTransactionForm.value = false;
};

const onImportComplete = () => {
  fetchTransactions();
  fetchSummary();
  displayImportDialog.value = false;
};

const toggleActionMenu = (event, rowData) => {
  selectedTransaction.value = rowData;
  actionMenu.value.toggle(event);
};

const editSelectedTransaction = () => {
  if (selectedTransaction.value) {
    showTransactionForm(selectedTransaction.value, true);
    displayTransactionDetails.value = false;
  }
};

const confirmDeleteTransaction = (transaction) => {
  selectedTransaction.value = transaction;
  
  confirm.require({
    message: 'Are you sure you want to delete this transaction?',
    header: 'Confirm Delete',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    accept: deleteTransaction,
    reject: () => {
      selectedTransaction.value = null;
    }
  });
};

const deleteTransaction = async () => {
  if (!selectedTransaction.value) return;
  
  try {
    await TransactionService.deleteTransaction(selectedTransaction.value.id);
    
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Transaction deleted successfully',
      life: 3000
    });
    
    // Refresh data
    await Promise.all([
      fetchTransactions(),
      fetchSummary()
    ]);
    
    // Close details if open
    displayTransactionDetails.value = false;
    selectedTransaction.value = null;
  } catch (error) {
    console.error('Error deleting transaction:', error);
    
    let errorMessage = 'Failed to delete transaction';
    if (error.response?.data?.detail) {
      errorMessage = error.response.data.detail;
    }
    
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: errorMessage,
      life: 5000
    });
  }
};

const reconcileTransaction = async (transaction) => {
  if (!transaction) return;
  
  try {
    await TransactionService.reconcileTransaction(transaction.id);
    
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Transaction reconciled successfully',
      life: 3000
    });
    
    // Refresh data
    await Promise.all([
      fetchTransactions(),
      fetchSummary()
    ]);
    
    // Update selected transaction if in details view
    if (selectedTransaction.value && selectedTransaction.value.id === transaction.id) {
      const updated = await TransactionService.getTransaction(transaction.id);
      selectedTransaction.value = updated.data;
    }
  } catch (error) {
    console.error('Error reconciling transaction:', error);
    
    let errorMessage = 'Failed to reconcile transaction';
    if (error.response?.data?.detail) {
      errorMessage = error.response.data.detail;
    }
    
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: errorMessage,
      life: 5000
    });
  }
};

// Helper methods
const getAccountIcon = (accountType) => {
  switch (accountType) {
    case 'savings':
      return 'pi pi-wallet';
    case 'credit_card':
      return 'pi pi-credit-card';
    case 'loan':
      return 'pi pi-money-bill';
    default:
      return 'pi pi-bank';
  }
};

const getCategorySeverity = (category) => {
  if (!category) return 'info';
  
  const severityMap = {
    income: 'success',
    expense: 'danger',
    transfer: 'info',
    fee: 'warning',
    interest: 'success',
    payment: 'primary',
    refund: 'help',
    deposit: 'success',
    withdrawal: 'danger'
  };
  
  return severityMap[category] || 'info';
};

const getStatusSeverity = (status) => {
  switch (status) {
    case 'posted':
      return 'success';
    case 'pending':
      return 'warning';
    case 'cancelled':
      return 'danger';
    default:
      return 'info';
  }
};

const getAccountById = (id) => {
  return bankAccounts.value.find(account => account.id === id);
};

const getAccountCurrency = (accountId) => {
  const account = bankAccounts.value.find(a => a.id === accountId);
  return account?.currency || { code: 'USD', symbol: '$' };
};

// Refs for template
const actionMenu = ref(null);
</script>

<style scoped>
.p-card {
  box-shadow: none;
  border: 1px solid var(--surface-d);
}

:deep(.p-datatable .p-datatable-tbody > tr) {
  cursor: pointer;
}

:deep(.p-datatable .p-datatable-tbody > tr:hover) {
  background-color: rgba(0, 0, 0, 0.02);
}

.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
