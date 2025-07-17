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
          label="Export" 
          icon="pi pi-download" 
          class="p-button-outlined p-button-success mr-2"
          @click="showExportDialog"
        />
        <Button 
          label="Print" 
          icon="pi pi-print" 
          class="p-button-outlined p-button-info mr-2"
          @click="printTransactions"
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
    <!-- Export Dialog -->
    <ReportExportDialog
      v-model:visible="displayExportDialog"
      :current-item-count="transactions.length"
      :total-items="totalRecords"
      :total-pages="Math.ceil(totalRecords / rowsPerPage)"
      :has-pagination="true"
      :export-formats="['pdf', 'excel', 'csv']"
      :export-callback="handleExport"
      @schedule="handleScheduleExport"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useToast } from 'primevue/usetoast';
import ReportExportDialog from '@/components/reports/ReportExportDialog.vue';
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
    
    // Prepare data based on scope
    if (scope === 'current') {
      exportData = [...transactions.value];
    } else if (scope === 'all') {
      // In a real app, you would fetch all data from the server
      const response = await TransactionService.getTransactions({
        page: 1,
        pageSize: 10000, // Large number to get all records
        ...filters.value
      });
      exportData = response.data;
    } else if (scope === 'range' && params.pageRange) {
      // Fetch data for the specified page range
      const { start, end } = params.pageRange;
      const pageSize = rowsPerPage.value;
      
      // In a real app, you would fetch each page's data
      const allData = [];
      for (let page = start; page <= end; page++) {
        const response = await TransactionService.getTransactions({
          page,
          pageSize,
          ...filters.value
        });
        allData.push(...response.data);
      }
      exportData = allData;
    }
    
    // Format data for export
    const formattedData = exportData.map(tx => ({
      'Date': formatDate(tx.transaction_date),
      'Account': getAccountById(tx.account_id)?.name || 'N/A',
      'Reference': tx.reference_number || 'N/A',
      'Description': tx.description || 'N/A',
      'Category': tx.category || 'Uncategorized',
      'Amount': formatCurrency(tx.amount),
      'Type': tx.transaction_type,
      'Status': tx.status,
      'Reconciled': tx.is_reconciled ? 'Yes' : 'No',
      'Created At': formatDateTime(tx.created_at)
    }));
    
    // In a real app, you would use a library like xlsx, jsPDF, etc.
    // This is a simplified example
    console.log(`Exporting ${formattedData.length} transactions to ${format} format`, options);
    
    // Simulate export
    toast.add({
      severity: 'success',
      summary: 'Export Started',
      detail: `Preparing to export ${formattedData.length} transactions to ${format.toUpperCase()} format`,
      life: 3000
    });
    
    // In a real app, you would generate and download the file here
    // For now, we'll just log it
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
      detail: 'Failed to export transactions. Please try again.',
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
  });};

// Print transactions
const printTransactions = () => {
  // In a real app, you would open a print dialog with a formatted version of the transactions
  const printWindow = window.open('', '_blank');
  
  // Get the current table data
  const table = document.querySelector('.p-datatable-table');
  if (!table) {
    toast.add({
      severity: 'warn',
      summary: 'Print Error',
      detail: 'No transaction data available to print.',
      life: 5000
    });
    return;
  }
  
  // Create a print-friendly version
  const printContent = `
    <!DOCTYPE html>
    <html>
    <head>
      <title>Bank Transactions - ${new Date().toLocaleDateString()}</title>
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
      <h1>Bank Transactions</h1>
      <div>Generated on: ${new Date().toLocaleString()}</div>
      
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Account</th>
            <th>Reference</th>
            <th>Description</th>
            <th>Category</th>
            <th class="text-right">Amount</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          ${transactions.value.map(tx => `
            <tr>
              <td>${formatDate(tx.transaction_date)}</td>
              <td>${getAccountById(tx.account_id)?.name || 'N/A'}</td>
              <td>${tx.reference_number || 'N/A'}</td>
              <td>${tx.description || 'N/A'}</td>
              <td>${tx.category || 'Uncategorized'}</td>
              <td class="text-right" style="color: ${tx.amount >= 0 ? 'green' : 'red'}">
                ${formatCurrency(tx.amount)}
              </td>
              <td>${tx.status}</td>
            </tr>
          `).join('')}
        </tbody>
        <tfoot>
          <tr>
            <td colspan="5" class="text-right"><strong>Total:</strong></td>
            <td class="text-right">
              <strong>${formatCurrency(transactions.value.reduce((sum, tx) => sum + parseFloat(tx.amount || 0), 0))}</strong>
            </td>
            <td></td>
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
