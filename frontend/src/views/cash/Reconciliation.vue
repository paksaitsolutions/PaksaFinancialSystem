<template>
  <div class="reconciliation">
    <div class="flex justify-content-between align-items-center mb-4">
      <h1>Bank Reconciliation</h1>
      <Button 
        label="New Reconciliation" 
        icon="pi pi-plus" 
        @click="startNewReconciliation"
        :disabled="activeReconciliation !== null"
      />
    </div>

    <!-- Reconciliation Status Card -->
    <Card v-if="activeReconciliation" class="mb-4">
      <template #title>
        <div class="flex justify-content-between align-items-center">
          <span>Active Reconciliation</span>
          <Tag 
            :value="formatStatus(activeReconciliation.status)" 
            :severity="getStatusSeverity(activeReconciliation.status)" 
          />
        </div>
      </template>
      <template #content>
        <div class="grid">
          <div class="col-12 md:col-4">
            <div class="text-500 font-medium mb-1">Account</div>
            <div class="text-900">{{ getAccountName(activeReconciliation.account_id) }}</div>
          </div>
          <div class="col-12 md:col-4">
            <div class="text-500 font-medium mb-1">Statement Date</div>
            <div class="text-900">{{ formatDate(activeReconciliation.statement_date) }}</div>
          </div>
          <div class="col-12 md:col-4">
            <div class="text-500 font-medium mb-1">Ending Balance</div>
            <div class="text-900">
              {{ formatCurrency(activeReconciliation.closing_balance, activeReconciliation.currency) }}
            </div>
          </div>
        </div>
      </template>
    </Card>

    <!-- Reconciliation Content -->
    <div class="grid">
      <!-- Unreconciled Transactions -->
      <div class="col-12 md:col-6">
        <Card>
          <template #title>Unreconciled Transactions</template>
          <template #content>
            <DataTable 
              :value="unreconciledTransactions" 
              :loading="loading"
              :scrollable="true"
              scrollHeight="500px"
              selectionMode="multiple"
              v-model:selection="selectedTransactions"
              dataKey="id"
            >
              <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>
              <Column field="transaction_date" header="Date" style="min-width: 100px">
                <template #body="{ data }">
                  {{ formatDate(data.transaction_date) }}
                </template>
              </Column>
              <Column field="reference" header="Reference" style="min-width: 120px"></Column>
              <Column field="description" header="Description" style="min-width: 200px">
                <template #body="{ data }">
                  <div class="truncate" :title="data.description">
                    {{ data.description || 'No description' }}
                  </div>
                </template>
              </Column>
              <Column field="amount" header="Amount" style="min-width: 120px" class="text-right">
                <template #body="{ data }">
                  <span :class="{ 'text-green-500': data.amount >= 0, 'text-red-500': data.amount < 0 }">
                    {{ formatCurrency(data.amount, activeReconciliation?.currency) }}
                  </span>
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </div>

      <!-- Statement Items -->
      <div class="col-12 md:col-6">
        <Card>
          <template #title>Bank Statement Items</template>
          <template #content>
            <div class="mb-3">
              <FileUpload 
                mode="basic" 
                :auto="true"
                :chooseLabel="statementFile ? statementFile.name : 'Import Bank Statement'"
                accept=".csv,.ofx,.qif"
                :maxFileSize="1000000"
                @select="onFileSelect"
                class="mb-3"
              />
            </div>
            
            <DataTable 
              :value="statementItems" 
              :loading="loadingStatement"
              :scrollable="true"
              scrollHeight="400px"
              selectionMode="multiple"
              v-model:selection="selectedStatementItems"
              dataKey="id"
            >
              <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>
              <Column field="date" header="Date" style="min-width: 100px">
                <template #body="{ data }">
                  {{ formatDate(data.date) }}
                </template>
              </Column>
              <Column field="reference" header="Reference" style="min-width: 120px"></Column>
              <Column field="description" header="Description" style="min-width: 200px">
                <template #body="{ data }">
                  <div class="truncate" :title="data.description">
                    {{ data.description || 'No description' }}
                  </div>
                </template>
              </Column>
              <Column field="amount" header="Amount" style="min-width: 120px" class="text-right">
                <template #body="{ data }">
                  <span :class="{ 'text-green-500': data.amount >= 0, 'text-red-500': data.amount < 0 }">
                    {{ formatCurrency(data.amount, activeReconciliation?.currency) }}
                  </span>
                </template>
              </Column>
            </DataTable>
          </template>
        </Card>
      </div>
    </div>

    <!-- New Reconciliation Dialog -->
    <Dialog 
      v-model:visible="showNewReconciliationDialog" 
      header="New Bank Reconciliation" 
      :modal="true"
      :style="{ width: '500px' }"
      @hide="closeNewReconciliationDialog"
    >
      <div class="field">
        <label for="account">Bank Account <span class="text-red-500">*</span></label>
        <Dropdown 
          id="account"
          v-model="newReconciliation.account_id"
          :options="bankAccounts"
          optionLabel="name"
          optionValue="id"
          placeholder="Select account"
          class="w-full"
          :class="{ 'p-invalid': submitted && !newReconciliation.account_id }"
        />
        <small v-if="submitted && !newReconciliation.account_id" class="p-error">
          Account is required.
        </small>
      </div>
      
      <div class="field">
        <label for="statementDate">Statement Date <span class="text-red-500">*</span></label>
        <Calendar 
          id="statementDate"
          v-model="newReconciliation.statement_date"
          dateFormat="yy-mm-dd"
          showIcon
          class="w-full"
          :class="{ 'p-invalid': submitted && !newReconciliation.statement_date }"
        />
        <small v-if="submitted && !newReconciliation.statement_date" class="p-error">
          Statement date is required.
        </small>
      </div>
      
      <div class="field">
        <label for="closingBalance">Ending Balance <span class="text-red-500">*</span></label>
        <InputNumber 
          id="closingBalance"
          v-model="newReconciliation.closing_balance"
          mode="decimal"
          :minFractionDigits="2"
          :maxFractionDigits="2"
          class="w-full"
          :class="{ 'p-invalid': submitted && newReconciliation.closing_balance === null }"
        />
        <small v-if="submitted && newReconciliation.closing_balance === null" class="p-error">
          Ending balance is required.
        </small>
      </div>
      
      <template #footer>
        <Button 
          label="Cancel" 
          icon="pi pi-times" 
          class="p-button-text"
          @click="closeNewReconciliationDialog"
        />
        <Button 
          label="Start Reconciliation" 
          icon="pi pi-check"
          @click="createReconciliation"
          :loading="loading"
        />
      </template>
    </Dialog>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import BankAccountService from '@/services/BankAccountService';
import { formatDate, formatCurrency } from '@/utils/formatters';

export default {
  name: 'ReconciliationView',
  
  setup() {
    const toast = useToast();
    const confirm = useConfirm();
    
    // State
    const loading = ref(false);
    const loadingStatement = ref(false);
    const submitted = ref(false);
    const bankAccounts = ref([]);
    const activeReconciliation = ref(null);
    const unreconciledTransactions = ref([]);
    const statementItems = ref([]);
    const selectedTransactions = ref([]);
    const selectedStatementItems = ref([]);
    const showNewReconciliationDialog = ref(false);
    const statementFile = ref(null);
    
    // New reconciliation form
    const newReconciliation = ref({
      account_id: null,
      statement_date: new Date(),
      closing_balance: null
    });
    
    // Load data on component mount
    onMounted(() => {
      loadBankAccounts();
      loadReconciliationStatus();
    });
    
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
    
    const loadReconciliationStatus = async () => {
      try {
        // In a real app, fetch from API
        // For demo, use mock data
        activeReconciliation.value = null; // Set to null to show the new reconciliation button
        
        // Load sample data for demo
        await loadUnreconciledTransactions();
        await loadStatementItems();
        
      } catch (error) {
        console.error('Error loading reconciliation status:', error);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to load reconciliation status',
          life: 5000
        });
      }
    };
    
    const loadUnreconciledTransactions = async () => {
      // Mock data for demo
      unreconciledTransactions.value = [
        {
          id: 'txn1',
          transaction_date: new Date('2025-07-15'),
          reference: 'INV-1001',
          description: 'Payment from ABC Corp',
          amount: 1500.00,
          currency: 'USD'
        },
        {
          id: 'txn2',
          transaction_date: new Date('2025-07-16'),
          reference: 'CHK-1001',
          description: 'Office supplies',
          amount: -250.75,
          currency: 'USD'
        }
      ];
    };
    
    const loadStatementItems = async () => {
      // Mock data for demo
      statementItems.value = [
        {
          id: 'stmt1',
          date: new Date('2025-07-10'),
          reference: 'DEP-1001',
          description: 'Deposit',
          amount: 1000.00,
          currency: 'USD'
        },
        {
          id: 'stmt2',
          date: new Date('2025-07-12'),
          reference: 'CHK-1000',
          description: 'Check payment',
          amount: -1200.00,
          currency: 'USD'
        }
      ];
    };
    
    const startNewReconciliation = () => {
      newReconciliation.value = {
        account_id: null,
        statement_date: new Date(),
        closing_balance: null
      };
      submitted.value = false;
      showNewReconciliationDialog.value = true;
    };
    
    const createReconciliation = async () => {
      submitted.value = true;
      
      // Validate form
      if (!newReconciliation.value.account_id || !newReconciliation.value.statement_date || 
          newReconciliation.value.closing_balance === null) {
        return;
      }
      
      try {
        loading.value = true;
        
        // In a real app, call the API here
        // const response = await ReconciliationService.startReconciliation(...);
        
        // For demo, just update the UI
        activeReconciliation.value = {
          id: 'rec' + Math.floor(Math.random() * 10000),
          account_id: newReconciliation.value.account_id,
          statement_date: newReconciliation.value.statement_date,
          closing_balance: newReconciliation.value.closing_balance,
          status: 'in_progress',
          currency: 'USD'
        };
        
        toast.add({
          severity: 'success',
          summary: 'Success',
          detail: 'Reconciliation started successfully',
          life: 3000
        });
        
        closeNewReconciliationDialog();
        
      } catch (error) {
        console.error('Error creating reconciliation:', error);
        
        let errorMessage = 'Failed to start reconciliation';
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
        loading.value = false;
      }
    };
    
    const closeNewReconciliationDialog = () => {
      showNewReconciliationDialog.value = false;
    };
    
    const onFileSelect = (event) => {
      const file = event.files[0];
      if (!file) return;
      
      statementFile.value = file;
      
      // In a real app, upload the file to the server
      // For demo, we'll just show a success message
      toast.add({
        severity: 'success',
        summary: 'File Selected',
        detail: 'Bank statement file ready for import',
        life: 3000
      });
    };
    
    const getAccountName = (accountId) => {
      const account = bankAccounts.value.find(acc => acc.id === accountId);
      return account ? account.name : 'Unknown Account';
    };
    
    const formatStatus = (status) => {
      if (!status) return 'Unknown';
      return status.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
    };
    
    const getStatusSeverity = (status) => {
      switch (status) {
        case 'completed': return 'success';
        case 'in_progress': return 'info';
        case 'cancelled': return 'danger';
        default: return 'warning';
      }
    };
    
    return {
      // State
      loading,
      loadingStatement,
      activeReconciliation,
      unreconciledTransactions,
      statementItems,
      selectedTransactions,
      selectedStatementItems,
      showNewReconciliationDialog,
      statementFile,
      newReconciliation,
      bankAccounts,
      submitted,
      
      // Methods
      startNewReconciliation,
      createReconciliation,
      closeNewReconciliationDialog,
      onFileSelect,
      formatDate,
      formatCurrency,
      getAccountName,
      formatStatus,
      getStatusSeverity
    };
  }
};
</script>

<style scoped>
.truncate {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 200px;
}
</style>
