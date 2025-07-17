<template>
  <div class="reconciliation">
    <div class="flex justify-content-between align-items-center mb-4">
      <h1>Bank Reconciliation</h1>
      <div class="flex gap-2">
        <Button 
          v-if="activeReconciliation"
          label="Export" 
          icon="pi pi-download" 
          class="p-button-outlined p-button-success"
          @click="showExportDialog"
          :disabled="!activeReconciliation"
        />
        <Button 
          v-if="activeReconciliation"
          label="Print" 
          icon="pi pi-print" 
          class="p-button-outlined p-button-info"
          @click="printReconciliation"
          :disabled="!activeReconciliation"
        />
        <Button 
          label="New Reconciliation" 
          icon="pi pi-plus" 
          @click="startNewReconciliation"
          :disabled="activeReconciliation !== null"
          class="p-button-outlined"
        />
        <Button 
          v-if="activeReconciliation"
          label="Complete Reconciliation" 
          icon="pi pi-check" 
          @click="completeReconciliation"
          :disabled="activeReconciliation?.status === 'completed'"
          class="p-button-success"
        />
      </div>
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

    <!-- Reconciliation Progress -->
    <div v-if="activeReconciliation" class="mb-4">
      <Card>
        <template #subtitle>Reconciliation Progress</template>
        <template #content>
          <div class="flex align-items-center gap-3">
            <ProgressBar 
              :value="reconciliationProgress.percentage" 
              :showValue="false" 
              style="height: 1.5rem; flex-grow: 1"
            />
            <div class="text-900 font-medium">
              {{ reconciliationProgress.matched }} of {{ reconciliationProgress.total }} items matched
              ({{ reconciliationProgress.percentage }}%)
            </div>
          </div>
        </template>
      </Card>
    </div>

    <!-- Reconciliation Content -->
    <div class="grid">
      <!-- Unreconciled Transactions -->
      <div class="col-12 md:col-6">
        <Card>
          <template #title>
            <div class="flex justify-content-between align-items-center">
              <span>Unreconciled Transactions</span>
              <span class="text-500 text-sm">{{ selectedTransactions.length }} selected</span>
            </div>
          </template>
          <template #content>
            <DataTable 
              :value="unreconciledTransactions" 
              :loading="loading"
              :scrollable="true"
              scrollHeight="400px"
              selectionMode="multiple"
              v-model:selection="selectedTransactions"
              dataKey="id"
              :rowClass="row => row.matched ? 'opacity-60' : ''"
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
          <template #title>
            <div class="flex justify-content-between align-items-center">
              <span>Bank Statement Items</span>
              <span class="text-500 text-sm">{{ selectedStatementItems.length }} selected</span>
            </div>
          </template>
          <template #content>
            <div class="mb-3">
              <FileUpload 
                mode="basic" 
                :auto="false"
                :chooseLabel="statementFile ? statementFile.name : 'Import Bank Statement'"
                accept=".csv,.ofx,.qif"
                :maxFileSize="1000000"
                @select="onFileSelect"
                :disabled="!activeReconciliation"
                :loading="loadingStatement"
                class="mb-3 w-full"
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
              :rowClass="row => row.matched ? 'opacity-60' : ''"
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
            
            <div class="mt-3 flex justify-content-end">
              <Button 
                label="Match Selected" 
                icon="pi pi-link" 
                @click="matchTransactions"
                :disabled="selectedTransactions.length === 0 || selectedStatementItems.value === 0"
                class="p-button-outlined"
              />
            </div>
          </template>
        </Card>
      </div>
    </div>

    <!-- New Reconciliation Dialog -->
    <Dialog 
      v-model:visible="showNewReconciliationDialog" 
      :style="{width: '500px'}" 
      header="New Reconciliation" 
      :modal="true" 
      class="p-fluid"
      :closable="!loading"
      :closeOnEscape="!loading"
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
        <label for="openingBalance">Opening Balance <span class="text-red-500">*</span></label>
        <InputNumber 
          id="openingBalance" 
          v-model="newReconciliation.opening_balance" 
          mode="currency" 
          :currency="'USD'" 
          :minFractionDigits="2"
          :maxFractionDigits="2"
          class="w-full"
          :class="{'p-invalid': submitted && !newReconciliation.opening_balance}"
        />
        <small class="p-invalid" v-if="submitted && !newReconciliation.opening_balance">Opening Balance is required.</small>
      </div>
      
      <div class="field">
        <label for="closingBalance">Closing Balance <span class="text-red-500">*</span></label>
        <InputNumber 
          id="closingBalance" 
          v-model="newReconciliation.closing_balance" 
          mode="currency" 
          :currency="'USD'" 
          :minFractionDigits="2"
          :maxFractionDigits="2"
          class="w-full"
          :class="{'p-invalid': submitted && !newReconciliation.closing_balance}"
        />
        <small class="p-invalid" v-if="submitted && !newReconciliation.closing_balance">Closing Balance is required.</small>
      </div>
      
      <template #footer>
        <Button 
          label="Cancel" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="closeNewReconciliationDialog" 
          :disabled="loading"
        />
        <Button 
          label="Start Reconciliation" 
          icon="pi pi-check" 
          class="p-button-text" 
          @click="createReconciliation" 
          :loading="loading"
        />
      </template>
    </Dialog>
  </div>

  <!-- Export Dialog -->
  <ReportExportDialog
    v-model:visible="displayExportDialog"
    :current-item-count="reconciliationItems.length"
    :total-items="reconciliationItems.length"
    :total-pages="1"
    :has-pagination="false"
    :export-formats="['pdf', 'excel', 'csv']"
    :export-callback="handleExport"
    @schedule="handleScheduleExport"
  />
</template>

<script>
import { ref, onMounted, computed, watch } from 'vue';
import { useToast } from 'primevue/usetoast';
import ReportExportDialog from '@/components/reports/ReportExportDialog.vue';
import { useConfirm } from 'primevue/useconfirm';
import BankAccountService from '@/services/BankAccountService';
import ReconciliationService from '@/services/ReconciliationService';
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
      opening_balance: null,
      closing_balance: null
    });
    
    // Track reconciliation progress
    const reconciliationProgress = ref({
      matched: 0,
      total: 0,
      percentage: 0
    });
    
    // Watch for changes in selected transactions and statement items
    watch([selectedTransactions, selectedStatementItems], () => {
      updateProgress();
    });
    
    // Load data on component mount
    onMounted(async () => {
      await loadBankAccounts();
      await loadReconciliationStatus();
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
        loading.value = true;
        
        // Check for active reconciliation for the selected account
        if (newReconciliation.value.account_id) {
          const status = await ReconciliationService.getReconciliationStatus(
            newReconciliation.value.account_id,
            new Date(new Date().setMonth(new Date().getMonth() - 1)), // Last month
            new Date()
          );
          
          if (status.active_reconciliation) {
            activeReconciliation.value = status.active_reconciliation;
            await loadUnreconciledTransactions();
            await loadStatementItems();
          } else {
            activeReconciliation.value = null;
          }
        }
      } catch (error) {
        console.error('Error loading reconciliation status:', error);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to load reconciliation status',
          life: 5000
        });
      } finally {
        loading.value = false;
      }
    };
    
    const loadUnreconciledTransactions = async () => {
      if (!activeReconciliation.value?.id) return;
      
      try {
        loading.value = true;
        const data = await ReconciliationService.getUnreconciledTransactions(
          activeReconciliation.value.account_id,
          activeReconciliation.value.id
        );
        unreconciledTransactions.value = data.transactions || [];
        updateProgress();
      } catch (error) {
        console.error('Error loading unreconciled transactions:', error);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to load unreconciled transactions',
          life: 5000
        });
      } finally {
        loading.value = false;
      }
    };
    
    const loadStatementItems = async () => {
      if (!activeReconciliation.value?.id) return;
      
      try {
        loadingStatement.value = true;
        // In a real app, fetch statement items from the API
        // For now, we'll use the existing mock data
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
      } catch (error) {
        console.error('Error loading statement items:', error);
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to load bank statement items',
          life: 5000
        });
      } finally {
        loadingStatement.value = false;
      }
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
          newReconciliation.value.opening_balance === null || 
          newReconciliation.value.closing_balance === null) {
        return;
      }
      
      try {
        loading.value = true;
        
        const response = await ReconciliationService.startReconciliation(
          newReconciliation.value.account_id,
          newReconciliation.value.statement_date,
          newReconciliation.value.opening_balance,
          newReconciliation.value.closing_balance
        );
        
        activeReconciliation.value = response.reconciliation;
        
        // Load transactions and statement items for the new reconciliation
        await loadUnreconciledTransactions();
        await loadStatementItems();
        
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
        } else if (error.message) {
          errorMessage = error.message;
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
    
    const onFileSelect = async (event) => {
      const file = event.files[0];
      if (!file) return;
      
      statementFile.value = file;
      
      try {
        loadingStatement.value = true;
        
        // Import the bank statement
        const result = await ReconciliationService.importBankStatement(
          activeReconciliation.value.account_id,
          file
        );
        
        // Reload statement items
        await loadStatementItems();
        
        toast.add({
          severity: 'success',
          summary: 'Success',
          detail: 'Bank statement imported successfully',
          life: 3000
        });
        
      } catch (error) {
        console.error('Error importing bank statement:', error);
        
        let errorMessage = 'Failed to import bank statement';
        if (error.response?.data?.detail) {
          errorMessage = error.response.data.detail;
        } else if (error.message) {
          errorMessage = error.message;
        }
        
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: errorMessage,
          life: 5000
        });
      } finally {
        loadingStatement.value = false;
      }
    };
    
    // Match selected transactions and statement items
    const matchTransactions = async () => {
      if (selectedTransactions.value.length === 0 || selectedStatementItems.value.length === 0) {
        toast.add({
          severity: 'warn',
          summary: 'Selection Required',
          detail: 'Please select at least one transaction and one statement item to match',
          life: 3000
        });
        return;
      }
      
      try {
        loading.value = true;
        
        const matches = selectedTransactions.value.map(txn => ({
          transaction_id: txn.id,
          statement_item_ids: selectedStatementItems.value.map(item => item.id)
        }));
        
        await ReconciliationService.matchTransactions(matches);
        
        // Clear selections
        selectedTransactions.value = [];
        selectedStatementItems.value = [];
        
        // Reload data
        await loadUnreconciledTransactions();
        
        toast.add({
          severity: 'success',
          summary: 'Success',
          detail: 'Transactions matched successfully',
          life: 3000
        });
        
      } catch (error) {
        console.error('Error matching transactions:', error);
        
        let errorMessage = 'Failed to match transactions';
        if (error.response?.data?.detail) {
          errorMessage = error.response.data.detail;
        } else if (error.message) {
          errorMessage = error.message;
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
    
    // Complete the reconciliation
    const completeReconciliation = async () => {
      confirm.require({
        message: 'Are you sure you want to complete this reconciliation? This action cannot be undone.',
        header: 'Confirm Completion',
        icon: 'pi pi-exclamation-triangle',
        accept: async () => {
          try {
            loading.value = true;
            
            await ReconciliationService.completeReconciliation(activeReconciliation.value.id);
            
            // Update the reconciliation status
            activeReconciliation.value.status = 'completed';
            
            toast.add({
              severity: 'success',
              summary: 'Success',
              detail: 'Reconciliation completed successfully',
              life: 3000
            });
            
          } catch (error) {
            console.error('Error completing reconciliation:', error);
            
            let errorMessage = 'Failed to complete reconciliation';
            if (error.response?.data?.detail) {
              errorMessage = error.response.data.detail;
            } else if (error.message) {
              errorMessage = error.message;
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
        }
      });
    };
    
    // Update reconciliation progress
    const updateProgress = () => {
      const total = unreconciledTransactions.value.length + statementItems.value.length;
      const matched = total - selectedTransactions.value.length - selectedStatementItems.value.length;
      
      reconciliationProgress.value = {
        matched,
        total,
        percentage: total > 0 ? Math.round((matched / total) * 100) : 0
      };
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
      matchTransactions,
      completeReconciliation,
      formatDate,
      formatCurrency,
      getAccountName,
      formatStatus,
      getStatusSeverity,
      reconciliationProgress
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
