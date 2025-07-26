<template>
  <div class="journal-entries">
    <div class="flex justify-content-between align-items-center mb-4">
      <h2>Journal Entries</h2>
      <Button 
        label="New Entry" 
        icon="pi pi-plus" 
        @click="openNewEntry"
        class="p-button-success"
      />
    </div>

    <div class="card">
      <DataTable 
        :value="journalEntries" 
        :loading="loading"
        :paginator="true" 
        :rows="10"
        :filters="filters"
        :globalFilterFields="['entry_number', 'description', 'status']"
        responsiveLayout="scroll"
      >
        <template #header>
          <div class="flex justify-content-between align-items-center">
            <span class="p-input-icon-left">
              <i class="pi pi-search" />
              <InputText 
                v-model="filters['global'].value" 
                placeholder="Search entries..." 
              />
            </span>
            <div>
              <Button 
                icon="pi pi-refresh" 
                class="p-button-text" 
                @click="loadJournalEntries"
                :loading="loading"
                v-tooltip="'Refresh data'"
              />
              <Button 
                icon="pi pi-download" 
                class="p-button-text" 
                label="Export" 
                @click="showExportDialog"
                v-tooltip="'Export data'"
              />
            </div>
          </div>
        </template>

        <Column field="entry_number" header="Entry #" :sortable="true" style="min-width:120px">
          <template #body="{ data }">
            <router-link 
              :to="{ name: 'journal-entry-detail', params: { id: data.id } }"
              class="font-medium text-primary hover:underline"
            >
              {{ data.entry_number }}
            </router-link>
          </template>
        </Column>
        
        <Column field="entry_date" header="Date" :sortable="true" style="min-width:120px">
          <template #body="{ data }">
            {{ formatDate(data.entry_date) }}
          </template>
        </Column>
        
        <Column field="description" header="Description" :sortable="true" style="min-width:250px" />
        
        <Column field="total_debit" header="Debit" :sortable="true" style="min-width:120px">
          <template #body="{ data }">
            {{ formatCurrency(data.total_debit) }}
          </template>
        </Column>
        
        <Column field="total_credit" header="Credit" :sortable="true" style="min-width:120px">
          <template #body="{ data }">
            {{ formatCurrency(data.total_credit) }}
          </template>
        </Column>
        
        <Column field="status" header="Status" :sortable="true" style="min-width:120px">
          <template #body="{ data }">
            <Tag 
              :value="data.status" 
              :severity="getStatusSeverity(data.status)" 
            />
          </template>
        </Column>
        
        <Column style="min-width:150px">
          <template #body="{ data }">
            <div class="flex gap-2">
              <Button 
                icon="pi pi-eye" 
                class="p-button-rounded p-button-text p-button-sm"
                @click="viewEntry(data)"
                v-tooltip.top="'View Details'"
              />
              <Button 
                icon="pi pi-pencil" 
                class="p-button-rounded p-button-text p-button-sm"
                @click="editEntry(data)"
                :disabled="data.status === 'Posted'"
                v-tooltip.top="'Edit Entry'"
              />
              <Button 
                icon="pi pi-trash" 
                class="p-button-rounded p-button-text p-button-sm p-button-danger"
                @click="confirmDeleteEntry(data)"
                :disabled="data.status === 'Posted'"
                v-tooltip.top="'Delete Entry'"
              />
            </div>
          </template>
        </Column>
      </DataTable>
    </div>

    <!-- Entry Dialog -->
    <Dialog 
      v-model:visible="showEntryDialog" 
      :header="editingEntry ? 'Edit Journal Entry' : 'New Journal Entry'"
      :modal="true"
      :style="{ width: '800px' }"
      :closable="!saving"
    >
      <div class="grid">
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="entry_number">Entry #</label>
            <InputText id="entry_number" v-model="entryForm.entry_number" disabled />
          </div>
        </div>
        
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="entry_date">Date <span class="text-red-500">*</span></label>
            <Calendar 
              id="entry_date" 
              v-model="entryForm.entry_date" 
              :showIcon="true"
              dateFormat="yy-mm-dd"
              class="w-full"
            />
          </div>
        </div>
        
        <div class="col-12">
          <div class="field">
            <label for="description">Description</label>
            <InputText 
              id="description" 
              v-model="entryForm.description" 
              class="w-full"
              placeholder="Enter a brief description"
            />
          </div>
        </div>
        
        <div class="col-12">
          <div class="flex justify-content-between align-items-center mb-2">
            <h4>Line Items</h4>
            <Button 
              label="Add Line" 
              icon="pi pi-plus" 
              @click="addLineItem"
              class="p-button-sm"
            />
          </div>
          
          <div class="line-items-table">
            <DataTable 
              :value="entryForm.line_items" 
              :scrollable="true"
              scrollHeight="200px"
              class="p-datatable-sm"
              :emptyMessage="'No line items added'"
            >
              <Column header="Account" style="min-width:250px">
                <template #body="{ data, index }">
                  <Dropdown
                    v-model="data.account_id"
                    :options="accounts"
                    optionLabel="name"
                    optionValue="id"
                    placeholder="Select Account"
                    :filter="true"
                    filterBy="name,code"
                    class="w-full"
                  >
                    <template #option="slotProps">
                      <div>{{ slotProps.option.code }} - {{ slotProps.option.name }}</div>
                    </template>
                  </Dropdown>
                </template>
              </Column>
              
              <Column header="Description" style="min-width:200px">
                <template #body="{ data }">
                  <InputText 
                    v-model="data.description" 
                    class="w-full"
                    placeholder="Description"
                  />
                </template>
              </Column>
              
              <Column header="Debit" style="width:120px">
                <template #body="{ data, index }">
                  <InputNumber 
                    v-model="data.debit" 
                    mode="currency" 
                    currency="USD" 
                    locale="en-US"
                    class="w-full"
                    @input="onAmountChange($event, index, 'debit')"
                  />
                </template>
              </Column>
              
              <Column header="Credit" style="width:120px">
                <template #body="{ data, index }">
                  <InputNumber 
                    v-model="data.credit" 
                    mode="currency" 
                    currency="USD" 
                    locale="en-US"
                    class="w-full"
                    @input="onAmountChange($event, index, 'credit')"
                  />
                </template>
              </Column>
              
              <Column header="Actions" style="width:80px">
                <template #body="{ index }">
                  <Button 
                    icon="pi pi-trash" 
                    class="p-button-text p-button-sm p-button-danger"
                    @click="removeLineItem(index)"
                    v-tooltip.top="'Remove line'"
                  />
                </template>
              </Column>
              
              <template #footer>
                <div class="flex justify-content-between align-items-center p-2">
                  <div class="font-bold">Total</div>
                  <div class="flex gap-4">
                    <div class="font-bold">
                      {{ formatCurrency(totalDebit) }}
                    </div>
                    <div class="font-bold">
                      {{ formatCurrency(totalCredit) }}
                    </div>
                    <div style="width: 2.5rem"></div>
                  </div>
                </div>
                
                <div class="flex justify-content-end p-2">
                  <div 
                    class="font-bold" 
                    :class="{ 'text-green-600': isBalanced, 'text-red-600': !isBalanced }"
                  >
                    {{ balanceStatus }}
                  </div>
                </div>
              </template>
            </DataTable>
          </div>
        </div>
        
        <div class="col-12">
          <div class="field">
            <label for="notes">Notes</label>
            <Textarea 
              id="notes" 
              v-model="entryForm.notes" 
              rows="2"
              class="w-full"
            />
          </div>
        </div>
      </div>
      
      <template #footer>
        <Button 
          label="Cancel" 
          @click="showEntryDialog = false"
          class="p-button-text"
          :disabled="saving"
        />
        <Button 
          label="Save as Draft" 
          @click="saveEntry('Draft')"
          class="p-button-secondary"
          :loading="saving"
        />
        <Button 
          label="Save & Post" 
          @click="saveEntry('Posted')"
          class="p-button-success"
          :loading="saving"
          :disabled="!isBalanced"
        />
      </template>
    </Dialog>
    
    <!-- Delete Confirmation Dialog -->
    <Dialog 
      v-model:visible="showDeleteDialog" 
      header="Confirm Delete" 
      :modal="true"
      :style="{ width: '450px' }"
    >
      <div class="confirmation-content">
        <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
        <span v-if="entryToDelete">
          Are you sure you want to delete journal entry <b>#{{ entryToDelete.entry_number }}</b>?
          <br><br>
          <small class="text-red-600">This action cannot be undone.</small>
        </span>
      </div>
      
      <template #footer>
        <Button 
          label="No" 
          @click="showDeleteDialog = false"
          class="p-button-text"
          :disabled="deleting"
        />
        <Button 
          label="Yes" 
          @click="deleteEntry"
          class="p-button-danger"
          :loading="deleting"
        />
      </template>
    </Dialog>
    <!-- Export Dialog -->
    <ExportDialog
      v-model:visible="exportDialogVisible"
      title="Export Journal Entries"
      :file-name="'journal-entries-export'"
      :columns="exportColumns"
      :data="filteredEntries"
      :meta="{
        title: 'Journal Entries',
        description: 'General Ledger Journal Entries',
        generatedOn: new Date().toLocaleString(),
        generatedBy: 'System',
        includeSummary: true,
        filters: {
          'Search Term': filters['global'].value || 'None',
          'Total Entries': journalEntries.length,
          'Status': selectedStatus || 'All',
          'Date Range': dateRange ? 
            `${new Date(dateRange[0]).toLocaleDateString()} - ${new Date(dateRange[1]).toLocaleDateString()}` : 
            'All Dates'
        }
      }"
      @export="handleExport"
    />
    
    <!-- Snackbar -->
    <v-snackbar v-model="snackbar" :color="snackbarColor" timeout="3000">
      {{ snackbarText }}
    </v-snackbar>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
// Removed PrimeVue useToast - using Vuetify snackbar instead
import { useRouter } from 'vue-router';
import ExportDialog from '@/components/common/ExportDialog.vue';
import { FilterMatchMode } from 'primevue/api';

// Mock data
const mockAccounts = [
  { id: '1', code: '1000', name: 'Cash and Cash Equivalents', type: 'asset' },
  { id: '2', code: '1100', name: 'Accounts Receivable', type: 'asset' },
  { id: '3', code: '2000', name: 'Accounts Payable', type: 'liability' },
  { id: '4', code: '3000', name: 'Owner\'s Equity', type: 'equity' },
  { id: '5', code: '4000', name: 'Revenue', type: 'revenue' },
  { id: '6', code: '5000', name: 'Expenses', type: 'expense' },
];

const mockJournalEntries = [
  {
    id: '1',
    entry_number: 'JE-2023-0001',
    entry_date: '2023-01-15',
    description: 'Initial capital investment',
    status: 'Posted',
    total_debit: 10000,
    total_credit: 10000,
    line_items: [
      { id: '1', account_id: '1', account_code: '1000', account_name: 'Cash', description: 'Initial investment', debit: 10000, credit: 0 },
      { id: '2', account_id: '4', account_code: '3000', account_name: 'Owner\'s Equity', description: 'Initial investment', debit: 0, credit: 10000 },
    ]
  },
  {
    id: '2',
    entry_number: 'JE-2023-0002',
    entry_date: '2023-01-20',
    description: 'Office equipment purchase',
    status: 'Posted',
    total_debit: 5000,
    total_credit: 5000,
    line_items: [
      { id: '3', account_id: '1500', account_code: '1500', account_name: 'Office Equipment', description: 'Computer and furniture', debit: 5000, credit: 0 },
      { id: '4', account_id: '1', account_code: '1000', account_name: 'Cash', description: 'Payment for equipment', debit: 0, credit: 5000 },
    ]
  },
  {
    id: '3',
    entry_number: 'JE-2023-0003',
    entry_date: '2023-01-25',
    description: 'Consulting revenue',
    status: 'Draft',
    total_debit: 7500,
    total_credit: 7500,
    line_items: [
      { id: '5', account_id: '1', account_code: '1000', account_name: 'Cash', description: 'Consulting services', debit: 7500, credit: 0 },
      { id: '6', account_id: '5', account_code: '4000', account_name: 'Revenue', description: 'Consulting revenue', debit: 0, credit: 7500 },
    ]
  }
];

export default {
  name: 'JournalEntriesView',
  components: {
    ExportDialog
  },
  
  setup() {
    const snackbar = ref(false);
    const snackbarText = ref('');
    const snackbarColor = ref('success');
    
    const showSnackbar = (text, color = 'success') => {
      snackbarText.value = text;
      snackbarColor.value = color;
      snackbar.value = true;
    };
    
    const journalEntries = ref([]);
    const accounts = ref([]);
    const loading = ref(false);
    const saving = ref(false);
    const exporting = ref(false);
    const exportProgress = ref(0);
    const showNewEntryDialog = ref(false);
    const exportDialogVisible = ref(false);
    const showDeleteDialog = ref(false);
    const editingEntry = ref(false);
    const entryToDelete = ref(null);
    
    const filters = ref({
      'global': { value: null, matchMode: FilterMatchMode.CONTAINS },
    });
    
    const exportColumns = [
      { field: 'entry_number', header: 'Entry #' },
      { field: 'entry_date', header: 'Date', format: (val) => formatDate(val) },
      { field: 'description', header: 'Description' },
      { field: 'total_debit', header: 'Debit', format: (val) => formatCurrency(val) },
      { field: 'total_credit', header: 'Credit', format: (val) => formatCurrency(val) },
      { field: 'status', header: 'Status' }
    ];

    const filteredEntries = computed(() => {
      return journalEntries.value.map(entry => ({
        ...entry,
        total_debit: formatCurrency(entry.total_debit, true),
        total_credit: formatCurrency(entry.total_credit, true)
      }));
    });
    
    const entryForm = ref({
      id: null,
      entry_number: '',
      entry_date: new Date(),
      description: '',
      status: 'Draft',
      notes: '',
      total_debit: 0,
      total_credit: 0,
      line_items: []
    });
    
    // Computed properties
    const totalDebit = computed(() => {
      return entryForm.value.line_items.reduce((sum, item) => sum + (parseFloat(item.debit) || 0), 0);
    });
    
    const totalCredit = computed(() => {
      return entryForm.value.line_items.reduce((sum, item) => sum + (parseFloat(item.credit) || 0), 0);
    });
    
    const isBalanced = computed(() => {
      return Math.abs(totalDebit.value - totalCredit.value) < 0.01;
    });
    
    const balanceStatus = computed(() => {
      const diff = totalDebit.value - totalCredit.value;
      if (Math.abs(diff) < 0.01) return 'Balanced';
      return `Out of Balance by: ${formatCurrency(Math.abs(diff))} ${diff > 0 ? 'Debit' : 'Credit'}`;
    });
    
    // Load data
    const loadJournalEntries = async () => {
      loading.value = true;
      try {
        // TODO: Replace with actual API calls
        journalEntries.value = [...mockJournalEntries];
        accounts.value = [...mockAccounts];
      } catch (error) {
        console.error('Error loading data:', error);
        showSnackbar('Failed to load data', 'error');
      } finally {
        loading.value = false;
      }
    };
    
    // Format date
    const formatDate = (value) => {
      if (!value) return '';
      return new Date(value).toLocaleDateString();
    };
    
    // Format currency
    const formatCurrency = (value, returnRaw = false) => {
      if (value === null || value === undefined) return '';
      if (returnRaw) return value;
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(value);
    };
    
    // Get status severity
    const getStatusSeverity = (status) => {
      switch (status) {
        case 'Posted': return 'success';
        case 'Draft': return 'info';
        case 'Reversed': return 'warning';
        case 'Void': return 'danger';
        default: return 'secondary';
      }
    };
    
    // Open new entry dialog
    const openNewEntry = () => {
      const nextNumber = journalEntries.value.length + 1;
      const entryNumber = `JE-${new Date().getFullYear()}-${String(nextNumber).padStart(4, '0')}`;
      
      entryForm.value = {
        id: null,
        entry_number: entryNumber,
        entry_date: new Date(),
        description: '',
        status: 'Draft',
        notes: '',
        total_debit: 0,
        total_credit: 0,
        line_items: []
      };
      
      // Add two empty line items
      addLineItem();
      addLineItem();
      
      editingEntry.value = false;
      showNewEntryDialog.value = true;
    };
    
    // Add line item
    const addLineItem = () => {
      entryForm.value.line_items.push({
        id: `temp-${Date.now()}-${Math.floor(Math.random() * 1000)}`,
        account_id: null,
        account_code: '',
        account_name: '',
        description: '',
        debit: null,
        credit: null
      });
    };
    
    // Remove line item
    const removeLineItem = (index) => {
      entryForm.value.line_items.splice(index, 1);
      updateTotals();
    };
    
    // Update totals
    const updateTotals = () => {
      entryForm.value.total_debit = totalDebit.value;
      entryForm.value.total_credit = totalCredit.value;
    };
    
    // Handle amount change
    const onAmountChange = (event, index, field) => {
      const value = event.value || 0;
      
      if (field === 'debit' && value > 0) {
        entryForm.value.line_items[index].credit = null;
      } else if (field === 'credit' && value > 0) {
        entryForm.value.line_items[index].debit = null;
      }
      
      updateTotals();
    };
    
    // View entry
    const viewEntry = (entry) => {
      // Navigate to detail view
      console.log('View entry:', entry.id);
    };
    
    // Edit entry
    const editEntry = (entry) => {
      entryForm.value = JSON.parse(JSON.stringify(entry));
      editingEntry.value = true;
      showNewEntryDialog.value = true;
    };
    
    // Confirm delete
    const confirmDeleteEntry = (entry) => {
      entryToDelete.value = entry;
      showDeleteDialog.value = true;
    };
    
    // Delete entry
    const deleteEntry = async () => {
      if (!entryToDelete.value) return;
      
      try {
        // TODO: Replace with actual API call
        journalEntries.value = journalEntries.value.filter(e => e.id !== entryToDelete.value.id);
        
        showSnackbar('Journal Entry deleted successfully', 'success');
      } catch (error) {
        console.error('Error deleting journal entry:', error);
        showSnackbar('Failed to delete journal entry', 'error');
      } finally {
        showDeleteDialog.value = false;
        entryToDelete.value = null;
      }
    };
    
    // Save entry
    const saveEntry = async (status) => {
      saving.value = true;
      
      try {
        entryForm.value.status = status;
        
        if (editingEntry.value) {
          const index = journalEntries.value.findIndex(e => e.id === entryForm.value.id);
          if (index !== -1) {
            journalEntries.value[index] = { ...entryForm.value };
          }
        } else {
          const newId = (journalEntries.value.length + 1).toString();
          entryForm.value.id = newId;
          
          entryForm.value.line_items = entryForm.value.line_items.map(item => ({
            ...item,
            id: `item-${Date.now()}-${Math.floor(Math.random() * 1000)}`,
            entry_id: newId
          }));
          
          journalEntries.value.unshift({ ...entryForm.value });
        }
        
        showSnackbar(`Journal Entry ${editingEntry.value ? 'updated' : 'created'} successfully`, 'success');
        
        showNewEntryDialog.value = false;
      } catch (error) {
        console.error('Error saving journal entry:', error);
        showSnackbar('Failed to save journal entry', 'error');
      } finally {
        saving.value = false;
      }
    };
    
    // Show export dialog
    const showExportDialog = () => {
      exportDialogVisible.value = true;
    };

    // Handle export
    const handleExport = async (format, options) => {
      exporting.value = true;
      exportProgress.value = 0;
      
      try {
        // Simulate export progress
        const interval = setInterval(() => {
          exportProgress.value = Math.min(exportProgress.value + 10, 90);
        }, 100);

        // Here you would typically make an API call to export the data
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        clearInterval(interval);
        exportProgress.value = 100;
        
        showSnackbar(`Exported ${filteredEntries.value.length} journal entries to ${format.toUpperCase()}`, 'success');
      } catch (error) {
        console.error('Export failed:', error);
        showSnackbar('An error occurred while exporting the data', 'error');
      } finally {
        setTimeout(() => {
          exporting.value = false;
          exportProgress.value = 0;
        }, 500);
      }
    };
    
    // Load data on component mount
    onMounted(() => {
      loadJournalEntries();
    });
    
    return {
      journalEntries,
      accounts,
      loading,
      saving,
      exporting,
      exportProgress,
      showNewEntryDialog,
      exportDialogVisible,
      showDeleteDialog,
      editingEntry,
      entryToDelete,
      filters,
      entryForm,
      totalDebit,
      totalCredit,
      isBalanced,
      balanceStatus,
      loadJournalEntries,
      formatDate,
      formatCurrency,
      getStatusSeverity,
      openNewEntry,
      addLineItem,
      removeLineItem,
      onAmountChange,
      viewEntry,
      editEntry,
      confirmDeleteEntry,
      deleteEntry,
      saveEntry,
      showExportDialog,
      handleExport,
      exportColumns,
      filteredEntries,
      snackbar,
      snackbarText,
      snackbarColor,
      showSnackbar
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
  font-size: 0.9rem;
}

:deep(.p-datatable .p-datatable-thead > tr > th) {
  background-color: #f8f9fa;
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.5px;
}

:deep(.p-datatable .p-datatable-tbody > tr > td) {
  padding: 0.75rem 1rem;
}

:deep(.p-datatable .p-datatable-tbody > tr:hover) {
  background-color: #f8f9fa;
  cursor: pointer;
}

.line-items-table {
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  overflow: hidden;
}
</style>
