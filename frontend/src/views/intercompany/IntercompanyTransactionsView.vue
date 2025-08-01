<template>
  <div class="card">
    <Toolbar class="mb-4">
      <template #start>
        <h2>Intercompany Transactions</h2>
      </template>
      <template #end>
        <Button 
          label="New Transaction" 
          icon="pi pi-plus" 
          class="p-button-primary"
          @click="openTransactionDialog"
        />
      </template>
    </Toolbar>
    <!-- DataTable -->
    <DataTable 
      :value="transactions"
      :loading="loading"
      :paginator="true" 
      :rows="10"
      :rowsPerPageOptions="[5,10,25,50]"
      paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
      currentPageReportTemplate="Showing {first} to {last} of {totalRecords} transactions"
      responsiveLayout="scroll"
      class="p-datatable-sm"
    >
      <Column field="transaction_number" header="Transaction #" :sortable="true" />
      <Column field="transaction_date" header="Date" :sortable="true">
        <template #body="{ data }">
          {{ formatDate(data.transaction_date) }}
        </template>
      </Column>
      <Column field="source_company_name" header="Source Company" :sortable="true" />
      <Column field="target_company_name" header="Target Company" :sortable="true" />
      <Column field="amount" header="Amount" :sortable="true">
        <template #body="{ data }">
          {{ formatCurrency(data.amount, data.currency) }}
        </template>
      </Column>
      <Column field="status" header="Status" :sortable="true">
        <template #body="{ data }">
          <Tag :value="formatStatus(data.status)" :severity="statusSeverity(data.status)" />
        </template>
      </Column>
      <Column header="Actions" :exportable="false" style="min-width: 8rem">
        <template #body="{ data }">
          <Button 
            icon="pi pi-pencil" 
            class="p-button-rounded p-button-text p-button-sm p-mr-2"
            @click="editTransaction(data)"
            v-tooltip.top="'Edit'"
            :disabled="!canEditTransaction(data)"
          />
          <Button 
            icon="pi pi-trash" 
            class="p-button-rounded p-button-text p-button-sm p-button-danger"
            @click="confirmDeleteTransaction(data)"
            v-tooltip.top="'Delete'"
            :disabled="!canDeleteTransaction(data)"
          />
        </template>
      </Column>
    </DataTable>
                class="p-button-primary"
              />
            </div>
          </template>
          
          <template #content>
            <DataTable 
              :value="transactions" 
              :loading="loading"
              :paginator="true"
              :rows="10"
              :rowsPerPageOptions="[5, 10, 20, 50]"
              class="p-datatable-sm"
              stripedRows
            >
              <Column field="transaction_number" header="Transaction #" :sortable="true" />
              
              <Column field="transaction_type" header="Type" :sortable="true">
                <template #body="{ data }">
                  <Tag 
                    :value="formatTransactionType(data.transaction_type)"
                    :severity="getTypeSeverity(data.transaction_type)"
                  />
                </template>
              </Column>
              
              <Column field="status" header="Status" :sortable="true">
                <template #body="{ data }">
                  <Tag 
                    :value="data.status.toUpperCase()"
                    :severity="getStatusSeverity(data.status)"
                  />
                </template>
              </Column>
              
              <Column field="amount" header="Amount" :sortable="true">
                <template #body="{ data }">
                  {{ formatCurrency(data.amount) }}
                </template>
              </Column>
              
              <Column field="transaction_date" header="Date" :sortable="true">
                <template #body="{ data }">
                  {{ formatDate(data.transaction_date) }}
                </template>
              </Column>
              
              <Column field="description" header="Description" :sortable="false" />
              
              <Column header="Actions" :exportable="false" style="min-width: 10rem">
                <template #body="{ data }">
                  <Button 
                    icon="pi pi-eye" 
                    class="p-button-text p-button-rounded p-button-sm"
                    @click="viewTransaction(data)"
                    v-tooltip.top="'View Details'"
                  />
                  <Button 
                    v-if="data.status === 'pending'"
                    icon="pi pi-check" 
                    class="p-button-text p-button-rounded p-button-sm p-button-success"
                    @click="approveTransaction(data)"
                    v-tooltip.top="'Approve'"
                  />
                  <Button 
                    v-if="data.status === 'approved'"
                    icon="pi pi-send" 
                    class="p-button-text p-button-rounded p-button-sm p-button-info"
                    @click="postTransaction(data)"
                    v-tooltip.top="'Post Transaction'"
                  />
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </div>
    </div>
    
    <!-- Transaction Dialog -->
    <Dialog 
      v-model:visible="transactionDialog" 
      :header="editMode ? 'View Transaction' : 'New Intercompany Transaction'" 
      :modal="true" 
      :style="{ width: '800px' }"
      :closable="!saving"
      :closeOnEscape="!saving"
    >
      <form @submit.prevent="saveTransaction" ref="transactionForm">
        <div class="grid">
          <div class="col-12 md:col-6">
            <div class="field">
              <label for="transactionType">Transaction Type</label>
              <Dropdown
                id="transactionType"
                v-model="editedTransaction.transaction_type"
                :options="transactionTypes"
                optionLabel="text"
                optionValue="value"
                placeholder="Select a transaction type"
                :disabled="editMode"
                :class="{ 'p-invalid': submitted && !editedTransaction.transaction_type }"
              />
              <small v-if="submitted && !editedTransaction.transaction_type" class="p-error">
                Transaction type is required
              </small>
            </div>
          </div>
          
          <div class="col-12 md:col-6">
            <div class="field">
              <label for="amount">Amount</label>
              <InputNumber
                id="amount"
                v-model="editedTransaction.amount"
                mode="currency"
                currency="USD"
                :minFractionDigits="2"
                :maxFractionDigits="2"
                :disabled="editMode"
                :class="{ 'p-invalid': submitted && (!editedTransaction.amount || editedTransaction.amount <= 0) }"
              />
              <small 
                v-if="submitted && (!editedTransaction.amount || editedTransaction.amount <= 0)" 
                class="p-error"
              >
                Amount must be positive
              </small>
            </div>
          </div>
              
          <div class="col-12 md:col-6">
            <div class="field">
              <label for="sourceCompany">Source Company</label>
              <Dropdown
                id="sourceCompany"
                v-model="editedTransaction.source_company_id"
                :options="companies"
                optionLabel="name"
                optionValue="id"
                placeholder="Select source company"
                :disabled="editMode"
                :class="{ 'p-invalid': submitted && !editedTransaction.source_company_id }"
                @change="onSourceCompanyChange"
              />
              <small v-if="submitted && !editedTransaction.source_company_id" class="p-error">
                Source company is required
              </small>
            </div>
          </div>
          
          <div class="col-12 md:col-6">
            <div class="field">
              <label for="targetCompany">Target Company</label>
              <Dropdown
                id="targetCompany"
                v-model="editedTransaction.target_company_id"
                :options="filteredTargetCompanies"
                optionLabel="name"
                optionValue="id"
                placeholder="Select target company"
                :disabled="editMode"
                :class="{
                  'p-invalid': submitted && (
                    !editedTransaction.target_company_id || 
                    editedTransaction.target_company_id === editedTransaction.source_company_id
                  )
                }"
              />
              <small 
                v-if="submitted && !editedTransaction.target_company_id" 
                class="p-error"
              >
                Target company is required
              </small>
              <small 
                v-if="submitted && editedTransaction.target_company_id && 
                      editedTransaction.target_company_id === editedTransaction.source_company_id" 
                class="p-error"
              >
                Companies must be different
              </small>
            </div>
          </div>
              
          <div class="col-12 md:col-6">
            <div class="field">
              <label for="sourceAccount">Source Account</label>
              <Dropdown
                id="sourceAccount"
                v-model="editedTransaction.source_account_id"
                :options="accounts"
                optionLabel="name"
                optionValue="id"
                placeholder="Select source account"
                :disabled="editMode"
                :class="{ 'p-invalid': submitted && !editedTransaction.source_account_id }"
              />
              <small v-if="submitted && !editedTransaction.source_account_id" class="p-error">
                Source account is required
              </small>
            </div>
          </div>
          
          <div class="col-12 md:col-6">
            <div class="field">
              <label for="targetAccount">Target Account</label>
              <Dropdown
                id="targetAccount"
                v-model="editedTransaction.target_account_id"
                :options="accounts"
                optionLabel="name"
                optionValue="id"
                placeholder="Select target account"
                :disabled="editMode"
                :class="{ 'p-invalid': submitted && !editedTransaction.target_account_id }"
              />
              <small v-if="submitted && !editedTransaction.target_account_id" class="p-error">
                Target account is required
              </small>
            </div>
          </div>
              
          <div class="col-12">
            <div class="field">
              <label for="description">Description</label>
              <Textarea
                id="description"
                v-model="editedTransaction.description"
                :autoResize="true"
                rows="3"
                :disabled="editMode"
                placeholder="Enter transaction description"
              />
            </div>
          </div>
          
          <div class="col-12">
            <div class="field">
              <label for="referenceNumber">Reference Number</label>
              <InputText
                id="referenceNumber"
                v-model="editedTransaction.reference_number"
                :disabled="editMode"
                placeholder="Enter reference number"
              />
            </div>
          </div>
        </div>
      </form>
      
      <template #footer>
        <Button 
          :label="editMode ? 'Close' : 'Cancel'" 
          icon="pi pi-times" 
          @click="closeTransactionDialog" 
          class="p-button-text"
          :disabled="saving"
        />
        <Button 
          v-if="!editMode"
          label="Save" 
          icon="pi pi-check" 
          @click="saveTransaction" 
          class="p-button-primary"
          :loading="saving"
        />
      </template>
    </Dialog>
  </v-container>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import { useIntercompanyStore } from '@/stores/intercompany';
import { useCompanyStore } from '@/stores/company';

// PrimeVue Components
import Button from 'primevue/button';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Tag from 'primevue/tag';
import Dialog from 'primevue/dialog';
import Dropdown from 'primevue/dropdown';
import InputNumber from 'primevue/inputnumber';
import Calendar from 'primevue/calendar';
import Textarea from 'primevue/textarea';
import Toolbar from 'primevue/toolbar';
import Tooltip from 'primevue/tooltip';
    const companyStore = useCompanyStore();
    const authStore = useAuthStore();
    
    // Data properties
    const transactions = ref([]);
    const loading = ref(false);
    const transactionDialog = ref(false);
    const editMode = ref(false);
    const saving = ref(false);
    const submitted = ref(false);
    
    const defaultTransaction = {
      id: null,
      source_company_id: null,
      target_company_id: null,
      source_account_id: null,
      target_account_id: null,
      amount: null,
      currency: 'USD',
      transaction_date: new Date().toISOString().split('T')[0],
      description: '',
      reference_number: '',
      status: 'pending',
      created_by: null,
      created_at: null,
      updated_at: null
    };
    
    const editedTransaction = ref({ ...defaultTransaction });
    const companies = ref([]);
    const accounts = ref([]);
    
    const statuses = [
      { name: 'Pending', value: 'pending' },
      { name: 'Completed', value: 'completed' },
      { name: 'Rejected', value: 'rejected' },
      { name: 'Reversed', value: 'reversed' }
    ];
    
    const currencies = [
      { code: 'USD', name: 'US Dollar' },
      { code: 'EUR', name: 'Euro' },
      { code: 'GBP', name: 'British Pound' },
      { code: 'PKR', name: 'Pakistani Rupee' },
      { code: 'SAR', name: 'Saudi Riyal' },
      { code: 'AED', name: 'UAE Dirham' }
    ];
    
    const columns = [
      { field: 'transaction_number', header: 'Transaction #', sortable: true },
      { field: 'transaction_date', header: 'Date', sortable: true, dataType: 'date' },
      { field: 'source_company.name', header: 'Source Company', sortable: true },
      { field: 'target_company.name', header: 'Target Company', sortable: true },
      { 
        field: 'amount', 
        header: 'Amount', 
        sortable: true,
        body: (data) => formatCurrency(data.amount, data.currency)
      },
      { field: 'currency', header: 'Currency', sortable: true },
      { 
        field: 'status', 
        header: 'Status', 
        sortable: true,
        body: (data) => {
          const status = data.status || 'pending';
          return `<span class="status-badge status-${status}">${formatStatus(status)}</span>`;
        }
      },
      { 
        field: 'actions', 
        header: 'Actions',
        sortable: false,
        body: (data) => `
          <div class="flex gap-2">
            <Button 
              icon="pi pi-eye" 
              class="p-button-rounded p-button-text" 
              @click="viewTransaction(${JSON.stringify(data)})"
              v-tooltip.top="'View Details'"
            />
            <Button 
              icon="pi pi-pencil" 
              class="p-button-rounded p-button-text p-button-warning" 
              @click="editTransaction(${JSON.stringify(data)})"
              v-tooltip.top="'Edit'"
              v-if="canEditTransaction(data)"
            />
            <Button 
              icon="pi pi-trash" 
              class="p-button-rounded p-button-text p-button-danger" 
              @click="confirmDeleteTransaction(${JSON.stringify(data)})"
              v-tooltip.top="'Delete'"
              v-if="canDeleteTransaction(data)"
            />
          </div>
        `
      }
    ];

    const filteredTargetCompanies = computed(() => {
      if (!editedTransaction.value.source_company_id) return companies.value;
      return companies.value.filter(company => company.id !== editedTransaction.value.source_company_id);
    });

    // Helper methods
    const formatCurrency = (amount, currency = 'USD') => {
      if (amount === null || amount === undefined) return '';
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency || 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }).format(amount);
    };

    const formatStatus = (status) => {
      const statusMap = {
        'pending': 'Pending',
        'completed': 'Completed',
        'rejected': 'Rejected',
        'reversed': 'Reversed'
      };
      return statusMap[status] || status;
    };

    const canEditTransaction = (transaction) => {
      if (!authStore.user) return false;
      if (authStore.hasPermission('intercompany_transaction.update')) return true;
      return transaction.status === 'pending' && transaction.created_by === authStore.user.id;
    };

    const canDeleteTransaction = (transaction) => {
      if (!authStore.user) return false;
      if (authStore.hasPermission('intercompany_transaction.delete')) return true;
      return transaction.status === 'pending' && transaction.created_by === authStore.user.id;
    };

    // Event handlers
    const onSourceCompanyChange = () => {
      // Reset target company if it's the same as source
      if (editedTransaction.value.source_company_id === editedTransaction.value.target_company_id) {
        editedTransaction.value.target_company_id = null;
      }
    };

    const openNewTransaction = () => {
      editedTransaction.value = { ...defaultTransaction };
      submitted.value = false;
      transactionDialog.value = true;
      editMode.value = false;
    };

    const viewTransaction = (transaction) => {
      editedTransaction.value = { ...transaction };
      transactionDialog.value = true;
      editMode.value = true;
    };

    const editTransaction = (transaction) => {
      editedTransaction.value = { ...transaction };
      transactionDialog.value = true;
      editMode.value = true;
    };

    const confirmDeleteTransaction = (transaction) => {
      confirm.require({
        message: 'Are you sure you want to delete this transaction?',
        header: 'Confirm Delete',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'p-button-danger',
        accept: () => deleteTransaction(transaction),
        reject: () => {}
      });
    };

    const statusSeverity = (status) => {
      const statusMap = {
        'pending': 'warning',
        'completed': 'success',
        'rejected': 'danger',
        'reversed': 'info'
      };
      return statusMap[status] || 'secondary';
    };
    
    const transactions = ref([]);
    const companies = ref([]);
    const accounts = ref([]);
    const loading = ref(false);
    const saving = ref(false);
    
    const transactionDialog = ref(false);
    const editMode = ref(false);
    const editedTransaction = ref({
      transaction_type: '',
      source_company_id: '',
      target_company_id: '',
      amount: 0,
      currency_id: '1',
      transaction_date: new Date(),
      source_account_id: '',
      target_account_id: '',
      description: '',
      reference_number: ''
    });
    const transactionForm = ref(null);
    
    const transactionTypes = [
      { text: 'Sale', value: 'sale' },
      { text: 'Purchase', value: 'purchase' },
      { text: 'Loan', value: 'loan' },
      { text: 'Expense Allocation', value: 'expense_allocation' },
      { text: 'Revenue Sharing', value: 'revenue_sharing' },
      { text: 'Transfer', value: 'transfer' }
    ];
    
    const loadTransactions = async () => {
      loading.value = true;
      try {
        const response = await intercompanyService.listTransactions();
        transactions.value = response.data;
      } catch (error) {
        console.error('Failed to load transactions:', error);
        showSnackbar('Failed to load transactions', 'error');
      } finally {
        loading.value = false;
      }
    };
    
    const openTransactionDialog = (transaction = null) => {
      if (transaction) {
        editMode.value = true;
        editedTransaction.value = { ...transaction };
      } else {
        editMode.value = false;
        editedTransaction.value = {
          transaction_type: '',
          source_company_id: '',
          target_company_id: '',
          amount: 0,
          currency_id: '1',
          transaction_date: new Date(),
          source_account_id: '',
          target_account_id: '',
          description: '',
          reference_number: ''
        };
      }
      transactionDialog.value = true;
    };
    
    const closeTransactionDialog = () => {
      transactionDialog.value = false;
    };
    
    const saveTransaction = async () => {
      if (!transactionForm.value.validate()) return;
      
      saving.value = true;
      try {
        await intercompanyService.createTransaction(editedTransaction.value);
        showSnackbar('Transaction created successfully', 'success');
        closeTransactionDialog();
        loadTransactions();
      } catch (error) {
        console.error('Failed to save transaction:', error);
        showSnackbar(`Failed to save transaction: ${error.response?.data?.detail || error.message}`, 'error');
      } finally {
        saving.value = false;
      }
    };
    
    const viewTransaction = (transaction) => {
      openTransactionDialog(transaction);
    };
    
    const approveTransaction = async (transaction) => {
      try {
        await intercompanyService.approveTransaction(transaction.id);
        showSnackbar('Transaction approved successfully', 'success');
        loadTransactions();
      } catch (error) {
        console.error('Failed to approve transaction:', error);
        showSnackbar(`Failed to approve transaction: ${error.response?.data?.detail || error.message}`, 'error');
      }
    };
    
    const postTransaction = async (transaction) => {
      try {
        await intercompanyService.postTransaction(transaction.id);
        showSnackbar('Transaction posted successfully', 'success');
        loadTransactions();
      } catch (error) {
        console.error('Failed to post transaction:', error);
        showSnackbar(`Failed to post transaction: ${error.response?.data?.detail || error.message}`, 'error');
      }
    };
    
    const formatTransactionType = (type) => {
      return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    };
    
    const getTypeColor = (type) => {
      const colors = {
        sale: 'success',
        purchase: 'info',
        loan: 'warning',
        expense_allocation: 'orange',
        revenue_sharing: 'purple',
        transfer: 'blue'
      };
      return colors[type] || 'grey';
    };
    
    const getStatusColor = (status) => {
      const colors = {
        draft: 'grey',
        pending: 'orange',
        approved: 'blue',
        posted: 'success',
        reconciled: 'green',
        cancelled: 'red'
      };
      return colors[status] || 'grey';
    };
    
    const formatCurrency = (amount) => {
      return new Intl.NumberFormat(undefined, {
        style: 'currency',
        currency: 'USD'
      }).format(amount);
    };
    
    const formatDate = (dateString) => {
      if (!dateString) return '';
      return format(new Date(dateString), 'MMM dd, yyyy');
    };
    
    onMounted(() => {
      loadTransactions();
      companies.value = [
        { id: '1', name: 'Company A' },
        { id: '2', name: 'Company B' },
        { id: '3', name: 'Company C' }
      ];
      accounts.value = [
        { id: '1', name: 'Intercompany Receivable' },
        { id: '2', name: 'Intercompany Payable' },
    });

    // Expose template methods and data
    return {
      // Refs
      transactions,
      companies,
      accounts,
      loading,
      transactionDialog,
      editMode,
      saving,
      transactionTypes,
      editedTransaction,
      transactionForm,
      
      // Methods
      loadTransactions,
      openTransactionDialog,
      closeTransactionDialog,
      saveTransaction,
      viewTransaction,
      approveTransaction,
      postTransaction,
      formatTransactionType,
      getTypeColor,
      getStatusColor,
      formatCurrency,
      formatDate
    };
  }
};
</script>