<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex align-center">
            <h2>Intercompany Transactions</h2>
            <v-spacer></v-spacer>
            <v-btn
              color="primary"
              prepend-icon="mdi-plus"
              @click="openTransactionDialog()"
            >
              New Transaction
            </v-btn>
          </v-card-title>
          
          <v-card-text>
            <v-data-table
              :headers="headers"
              :items="transactions"
              :loading="loading"
              class="elevation-1"
            >
              <template v-slot:item.transaction_type="{ item }">
                <v-chip
                  :color="getTypeColor(item.transaction_type)"
                  size="small"
                >
                  {{ formatTransactionType(item.transaction_type) }}
                </v-chip>
              </template>
              
              <template v-slot:item.status="{ item }">
                <v-chip
                  :color="getStatusColor(item.status)"
                  size="small"
                >
                  {{ item.status.toUpperCase() }}
                </v-chip>
              </template>
              
              <template v-slot:item.amount="{ item }">
                {{ formatCurrency(item.amount) }}
              </template>
              
              <template v-slot:item.transaction_date="{ item }">
                {{ formatDate(item.transaction_date) }}
              </template>
              
              <template v-slot:item.actions="{ item }">
                <v-btn
                  icon
                  variant="text"
                  @click="viewTransaction(item)"
                >
                  <v-icon>mdi-eye</v-icon>
                </v-btn>
                <v-btn
                  v-if="item.status === 'pending'"
                  icon
                  variant="text"
                  @click="approveTransaction(item)"
                >
                  <v-icon>mdi-check</v-icon>
                </v-btn>
                <v-btn
                  v-if="item.status === 'approved'"
                  icon
                  variant="text"
                  @click="postTransaction(item)"
                >
                  <v-icon>mdi-send</v-icon>
                </v-btn>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    
    <!-- Transaction Dialog -->
    <v-dialog v-model="transactionDialog" max-width="800px">
      <v-card>
        <v-card-title>
          <span class="text-h5">{{ editMode ? 'View Transaction' : 'New Intercompany Transaction' }}</span>
        </v-card-title>
        
        <v-card-text>
          <v-form ref="transactionForm">
            <v-row>
              <v-col cols="12" md="6">
                <v-select
                  v-model="editedTransaction.transaction_type"
                  :items="transactionTypes"
                  item-title="text"
                  item-value="value"
                  label="Transaction Type"
                  :rules="[v => !!v || 'Transaction type is required']"
                  :disabled="editMode"
                ></v-select>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="editedTransaction.amount"
                  label="Amount"
                  type="number"
                  min="0.01"
                  step="0.01"
                  :rules="[v => !!v || 'Amount is required', v => parseFloat(v) > 0 || 'Amount must be positive']"
                  :disabled="editMode"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-select
                  v-model="editedTransaction.source_company_id"
                  :items="companies"
                  item-title="name"
                  item-value="id"
                  label="Source Company"
                  :rules="[v => !!v || 'Source company is required']"
                  :disabled="editMode"
                ></v-select>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-select
                  v-model="editedTransaction.target_company_id"
                  :items="companies"
                  item-title="name"
                  item-value="id"
                  label="Target Company"
                  :rules="[v => !!v || 'Target company is required', v => v !== editedTransaction.source_company_id || 'Companies must be different']"
                  :disabled="editMode"
                ></v-select>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-select
                  v-model="editedTransaction.source_account_id"
                  :items="accounts"
                  item-title="name"
                  item-value="id"
                  label="Source Account"
                  :rules="[v => !!v || 'Source account is required']"
                  :disabled="editMode"
                ></v-select>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-select
                  v-model="editedTransaction.target_account_id"
                  :items="accounts"
                  item-title="name"
                  item-value="id"
                  label="Target Account"
                  :rules="[v => !!v || 'Target account is required']"
                  :disabled="editMode"
                ></v-select>
              </v-col>
              
              <v-col cols="12">
                <v-textarea
                  v-model="editedTransaction.description"
                  label="Description"
                  rows="3"
                  :disabled="editMode"
                ></v-textarea>
              </v-col>
              
              <v-col cols="12">
                <v-text-field
                  v-model="editedTransaction.reference_number"
                  label="Reference Number"
                  :disabled="editMode"
                ></v-text-field>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="blue-darken-1"
            variant="text"
            @click="closeTransactionDialog"
          >
            {{ editMode ? 'Close' : 'Cancel' }}
          </v-btn>
          <v-btn
            v-if="!editMode"
            color="blue-darken-1"
            variant="text"
            @click="saveTransaction"
            :loading="saving"
          >
            Save
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
import { ref, onMounted } from 'vue';
import { format } from 'date-fns';
import intercompanyService from '@/services/intercompanyService';
import { useSnackbar } from '@/composables/useSnackbar';

export default {
  name: 'IntercompanyTransactionsView',
  
  setup() {
    const { showSnackbar } = useSnackbar();
    
    const headers = [
      { title: 'Transaction #', key: 'transaction_number', sortable: true },
      { title: 'Type', key: 'transaction_type', sortable: true },
      { title: 'Status', key: 'status', sortable: true },
      { title: 'Amount', key: 'amount', sortable: true },
      { title: 'Date', key: 'transaction_date', sortable: true },
      { title: 'Description', key: 'description', sortable: false },
      { title: 'Actions', key: 'actions', sortable: false }
    ];
    
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
        { id: '3', name: 'Intercompany Revenue' },
        { id: '4', name: 'Intercompany Expense' }
      ];
    });
    
    return {
      headers,
      transactions,
      companies,
      accounts,
      loading,
      saving,
      transactionTypes,
      transactionDialog,
      editMode,
      editedTransaction,
      transactionForm,
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