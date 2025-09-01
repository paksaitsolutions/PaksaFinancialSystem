<template>
  <div class="journal-entry-view p-4">
    <Card>
      <template #title>
        <div class="card-header">
          <h2>Journal Entries</h2>
          <Button 
            label="New Entry" 
            icon="pi pi-plus" 
            @click="handleNewEntry"
            class="new-entry-btn"
          />
        </div>
      </template>
      
      <template #content>
        <DataTable 
          :value="journalEntries" 
          :loading="loading"
          :paginator="true"
          :rows="10"
          responsiveLayout="scroll"
          class="journal-table"
        >
          <Column field="reference" header="Reference" sortable />
          <Column field="date" header="Date" sortable>
            <template #body="{ data }">
              {{ formatDate(data.date) }}
            </template>
          </Column>
          <Column field="memo" header="Memo" sortable />
          <Column field="status" header="Status" sortable>
            <template #body="{ data }">
              <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
            </template>
          </Column>
          <Column field="total_amount" header="Amount" sortable>
            <template #body="{ data }">
              {{ formatCurrency(data.total_amount || 0) }}
            </template>
          </Column>
          <Column header="Actions" style="width: 10rem">
            <template #body="{ data }">
              <Button 
                icon="pi pi-pencil" 
                class="p-button-text p-button-sm" 
                @click="editEntry(data)" 
              />
              <Button 
                icon="pi pi-trash" 
                class="p-button-text p-button-sm p-button-danger" 
                @click="confirmDelete(data)" 
              />
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>

    <!-- Journal Entry Dialog -->
    <Dialog 
      v-model:visible="journalDialog" 
      modal 
      :style="{ width: '90vw', maxWidth: '1000px' }"
      :closable="false"
    >
      <template #header>
        <div class="dialog-header">
          <i class="pi pi-book header-icon"></i>
          <div>
            <h3>{{ editingEntry ? 'Edit Journal Entry' : 'New Journal Entry' }}</h3>
            <p>{{ editingEntry ? 'Modify existing journal entry' : 'Create a new journal entry with balanced debits and credits' }}</p>
          </div>
        </div>
      </template>
      <div class="journal-form">
        <div class="form-section">
          <h4 class="section-title">
            <i class="pi pi-info-circle"></i>
            Entry Details
          </h4>
          <div class="form-grid">
            <div class="form-field">
              <label for="reference" class="required">Reference # *</label>
              <InputText 
                id="reference"
                v-model="editedEntry.reference" 
                placeholder="Enter reference number"
              />
            </div>
            <div class="form-field">
              <label for="date" class="required">Date *</label>
              <Calendar 
                id="date"
                v-model="editedEntry.date"
                dateFormat="mm/dd/yy"
                showIcon
              />
            </div>
            <div class="form-field">
              <label for="status">Status</label>
              <Dropdown 
                id="status"
                v-model="editedEntry.status" 
                :options="statusOptions" 
                optionLabel="label"
                optionValue="value"
                placeholder="Select Status"
              />
            </div>
            <div class="form-field full-width">
              <label for="memo">Description/Memo</label>
              <Textarea 
                id="memo" 
                v-model="editedEntry.memo" 
                :rows="2"
                placeholder="Enter description or memo for this journal entry"
              />
            </div>
          </div>
        </div>

        <div class="form-section">
          <div class="section-header">
            <h4 class="section-title">
              <i class="pi pi-list"></i>
              Journal Lines
            </h4>
            <Button 
              label="Add Line" 
              icon="pi pi-plus" 
              class="p-button-sm p-button-outlined" 
              @click="addLine" 
            />
          </div>
          
          <div class="journal-lines">
            <div class="lines-header">
              <div>Account</div>
              <div>Debit</div>
              <div>Credit</div>
              <div>Actions</div>
            </div>
            
            <div v-for="(line, index) in editedEntry.lines" :key="index" class="journal-line">
              <div>
                <Dropdown 
                  v-model="line.account_id"
                  :options="mockAccounts"
                  optionLabel="name"
                  optionValue="id"
                  placeholder="Select Account"
                  filter
                  @change="updateAccountName(line, $event)"
                />
              </div>
              <div>
                <InputNumber 
                  v-model="line.debit" 
                  mode="currency" 
                  currency="USD"
                  :minFractionDigits="2"
                  @input="clearCredit(line)"
                />
              </div>
              <div>
                <InputNumber 
                  v-model="line.credit" 
                  mode="currency" 
                  currency="USD"
                  :minFractionDigits="2"
                  @input="clearDebit(line)"
                />
              </div>
              <div>
                <Button 
                  icon="pi pi-trash" 
                  class="p-button-text p-button-danger p-button-sm" 
                  @click="removeLine(index)" 
                  :disabled="editedEntry.lines.length <= 2"
                />
              </div>
            </div>
          </div>
        </div>

        <div class="form-section">
          <div class="totals-container">
            <div class="totals-grid">
              <div class="total-item">
                <span class="total-label">Total Debits:</span>
                <span class="total-value">{{ formatCurrency(totalDebits) }}</span>
              </div>
              <div class="total-item">
                <span class="total-label">Total Credits:</span>
                <span class="total-value">{{ formatCurrency(totalCredits) }}</span>
              </div>
              <div class="total-item balance-check" :class="{ 'balanced': isBalanced, 'unbalanced': !isBalanced }">
                <span class="total-label">
                  <i :class="isBalanced ? 'pi pi-check-circle' : 'pi pi-exclamation-triangle'"></i>
                  {{ isBalanced ? 'Balanced' : 'Out of Balance' }}
                </span>
                <span class="total-value">
                  {{ isBalanced ? formatCurrency(0) : formatCurrency(Math.abs(totalDebits - totalCredits)) }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <Button
            label="Cancel"
            icon="pi pi-times"
            class="p-button-text"
            @click="closeDialog"
          />
          <Button
            label="Save as Draft"
            icon="pi pi-save"
            class="p-button-outlined"
            @click="saveDraft"
            :disabled="!editedEntry.reference"
          />
          <Button
            label="Save & Post"
            icon="pi pi-check"
            :loading="saving"
            :disabled="!isBalanced || !editedEntry.reference"
            @click="saveEntry"
          />
        </div>
      </template>
    </Dialog>
    
    <!-- Floating Action Button -->
    <Button 
      icon="pi pi-plus" 
      class="floating-btn"
      @click="handleNewEntry"
      v-tooltip="'New Journal Entry'"
    />
  </div>
</template>

<style scoped>
.journal-entry-view {
  position: relative;
  padding: 1rem;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.card-header h2 {
  margin: 0;
  color: #1f2937;
  font-size: 1.5rem;
  font-weight: 600;
}

.new-entry-btn {
  background: #3b82f6;
  border-color: #3b82f6;
  color: white;
  font-weight: 500;
  padding: 0.5rem 1rem;
}

.new-entry-btn:hover {
  background: #2563eb;
  border-color: #2563eb;
}

.floating-btn {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: #3b82f6;
  border-color: #3b82f6;
  color: white;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.floating-btn:hover {
  background: #2563eb;
  border-color: #2563eb;
  transform: scale(1.05);
  box-shadow: 0 6px 16px rgba(59, 130, 246, 0.5);
}

.floating-btn i {
  font-size: 1.25rem;
}

.dialog-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  width: 100%;
}

.dialog-header h3 {
  margin: 0;
  color: #1f2937;
  font-size: 1.25rem;
  font-weight: 600;
}

.dialog-header p {
  margin: 0.25rem 0 0 0;
  color: #6b7280;
  font-size: 0.875rem;
}

.header-icon {
  color: #3b82f6;
  font-size: 1.5rem;
}

.journal-form {
  padding: 0;
}

.form-section {
  margin-bottom: 2rem;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 0 1rem 0;
  color: #374151;
  font-size: 1rem;
  font-weight: 600;
}

.section-title i {
  color: #3b82f6;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 1rem;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-field.full-width {
  grid-column: 1 / -1;
}

.form-field label {
  font-weight: 500;
  color: #374151;
  font-size: 0.875rem;
}

.required::after {
  content: ' *';
  color: #ef4444;
}

.journal-lines {
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  overflow: hidden;
}

.lines-header {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 80px;
  gap: 1rem;
  padding: 0.75rem 1rem;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
  font-weight: 600;
  color: #374151;
  font-size: 0.875rem;
}

.journal-line {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 80px;
  gap: 1rem;
  padding: 1rem;
  border-bottom: 1px solid #f3f4f6;
  align-items: center;
}

.journal-line:last-child {
  border-bottom: none;
}

.totals-container {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1.5rem;
}

.totals-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 1rem;
}

.total-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: white;
  border-radius: 0.375rem;
  border: 1px solid #e5e7eb;
}

.total-label {
  font-weight: 500;
  color: #374151;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.total-value {
  font-weight: 600;
  font-size: 1rem;
}

.balance-check.balanced {
  background: #f0fdf4;
  border-color: #22c55e;
}

.balance-check.balanced .total-label,
.balance-check.balanced .total-value {
  color: #16a34a;
}

.balance-check.unbalanced {
  background: #fef2f2;
  border-color: #ef4444;
}

.balance-check.unbalanced .total-label,
.balance-check.unbalanced .total-value {
  color: #dc2626;
}

.dialog-footer {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}

@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .new-entry-btn {
    width: 100%;
  }
  
  .floating-btn {
    bottom: 1rem;
    right: 1rem;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .lines-header,
  .journal-line {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }
  
  .totals-grid {
    grid-template-columns: 1fr;
  }
}
</style>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';

// Types
interface JournalEntryLine {
  id?: string;
  account_id: string | null;
  account_name?: string;
  debit: number;
  credit: number;
  memo: string;
}

interface JournalEntry {
  id?: string;
  reference: string;
  date: Date;
  status: string;
  memo: string;
  lines: JournalEntryLine[];
  total_amount?: number;
}

// Initialize services
const toast = useToast();

// Initialize with default values
const defaultEntry: Omit<JournalEntry, 'id'> = {
  reference: '',
  date: new Date(),
  memo: '',
  status: 'draft',
  lines: [
    { account_id: null, account_name: '', debit: 0, credit: 0, memo: '' },
    { account_id: null, account_name: '', debit: 0, credit: 0, memo: '' }
  ],
  total_amount: 0
};

// State
const journalEntries = ref<JournalEntry[]>([]);
const loading = ref(false);
const saving = ref(false);
const journalDialog = ref(false);
const editingEntry = ref<JournalEntry | null>(null);
const editedEntry = ref<Omit<JournalEntry, 'id'>>(JSON.parse(JSON.stringify(defaultEntry)));

// Status options
const statusOptions = [
  { label: 'Draft', value: 'draft' },
  { label: 'Posted', value: 'posted' },
  { label: 'Void', value: 'void' }
];

// Computed
const isBalanced = computed((): boolean => {
  if (!editedEntry.value?.lines) return false;
  const total = editedEntry.value.lines.reduce(
    (sum, line) => sum + (Number(line.debit) || 0) - (Number(line.credit) || 0),
    0
  );
  return Math.abs(total) < 0.01;
});

const totalDebits = computed((): number => {
  return editedEntry.value.lines.reduce((sum, line) => sum + (Number(line.debit) || 0), 0);
});

const totalCredits = computed((): number => {
  return editedEntry.value.lines.reduce((sum, line) => sum + (Number(line.credit) || 0), 0);
});

// Utility functions
const formatDate = (date: Date | string | null | undefined): string => {
  if (!date) return '-';
  try {
    const dateObj = date instanceof Date ? date : new Date(date);
    if (isNaN(dateObj.getTime())) return '-';
    return dateObj.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: '2-digit',
    });
  } catch (e) {
    console.error('Error formatting date:', e);
    return '-';
  }
};

const formatCurrency = (value: number | string | null | undefined): string => {
  if (value === null || value === undefined) return '$0.00';
  const numValue = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(numValue)) return '$0.00';
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(numValue);
};

const getStatusSeverity = (status: string): 'success' | 'info' | 'danger' | 'warning' | 'secondary' | 'contrast' | undefined => {
  switch (status) {
    case 'posted':
      return 'success';
    case 'draft':
      return 'info';
    case 'void':
      return 'danger';
    default:
      return undefined;
  }
};

// Mock accounts for dropdown
const mockAccounts = [
  { id: '1000', name: '1000 - Cash', type: 'Asset' },
  { id: '1100', name: '1100 - Accounts Receivable', type: 'Asset' },
  { id: '1200', name: '1200 - Inventory', type: 'Asset' },
  { id: '2000', name: '2000 - Accounts Payable', type: 'Liability' },
  { id: '3000', name: '3000 - Owner Equity', type: 'Equity' },
  { id: '4000', name: '4000 - Sales Revenue', type: 'Revenue' },
  { id: '5000', name: '5000 - Cost of Goods Sold', type: 'Expense' },
  { id: '6000', name: '6000 - Office Expenses', type: 'Expense' }
];

// Methods
const handleNewEntry = (): void => {
  editingEntry.value = null;
  editedEntry.value = {
    reference: `JE-${new Date().getFullYear()}-${String(Date.now()).slice(-6)}`,
    date: new Date(),
    memo: '',
    status: 'draft',
    lines: [
      { account_id: null, account_name: '', debit: 0, credit: 0, memo: '' },
      { account_id: null, account_name: '', debit: 0, credit: 0, memo: '' }
    ]
  };
  journalDialog.value = true;
};

const updateAccountName = (line: JournalEntryLine, accountId: string) => {
  const account = mockAccounts.find(acc => acc.id === accountId);
  if (account) {
    line.account_name = account.name;
  }
};

const clearCredit = (line: JournalEntryLine) => {
  if (line.debit && line.debit > 0) {
    line.credit = 0;
  }
};

const clearDebit = (line: JournalEntryLine) => {
  if (line.credit && line.credit > 0) {
    line.debit = 0;
  }
};

const saveDraft = async (): Promise<void> => {
  if (!editedEntry.value.reference) return;
  
  editedEntry.value.status = 'draft';
  await saveEntry();
};

const editEntry = (entry: JournalEntry): void => {
  editingEntry.value = { ...entry };
  editedEntry.value = { 
    ...entry,
    date: entry.date instanceof Date ? entry.date : new Date(entry.date)
  };
  journalDialog.value = true;
};

const confirmDelete = async (entry: JournalEntry): Promise<void> => {
  if (entry.id) {
    try {
      journalEntries.value = journalEntries.value.filter(e => e.id !== entry.id);
      toast.add({ severity: 'success', summary: 'Success', detail: 'Journal entry deleted', life: 3000 });
    } catch (error) {
      toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to delete journal entry', life: 3000 });
    }
  }
};

const addLine = (): void => {
  editedEntry.value.lines.push({ 
    account_id: null, 
    account_name: '',
    debit: 0, 
    credit: 0, 
    memo: '' 
  });
};

const removeLine = (index: number): void => {
  if (editedEntry.value.lines.length > 2) {
    editedEntry.value.lines.splice(index, 1);
  }
};

const saveEntry = async (): Promise<void> => {
  if (!editedEntry.value) return;
  
  saving.value = true;
  try {
    const entry = { ...editedEntry.value };
    const total_amount = entry.lines.reduce((sum, line) => sum + (Number(line.debit) || 0), 0);
    const payload = { ...entry, total_amount, id: editingEntry.value?.id || `${Date.now()}` };

    if (editingEntry.value?.id) {
      const index = journalEntries.value.findIndex(e => e.id === editingEntry.value?.id);
      if (index !== -1) journalEntries.value[index] = payload;
      toast.add({ severity: 'success', summary: 'Success', detail: 'Journal entry updated successfully', life: 3000 });
    } else {
      journalEntries.value.push(payload);
      toast.add({ severity: 'success', summary: 'Success', detail: 'Journal entry created successfully', life: 3000 });
    }

    journalDialog.value = false;
    closeDialog();
  } catch (error) {
    console.error('Error saving journal entry:', error);
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to save journal entry', life: 3000 });
  } finally {
    saving.value = false;
  }
};

const closeDialog = (): void => {
  journalDialog.value = false;
  editingEntry.value = null;
  editedEntry.value = JSON.parse(JSON.stringify(defaultEntry));
};

const loadJournalEntries = async () => {
  loading.value = true;
  try {
    // Mock data
    journalEntries.value = [
      {
        id: '1',
        reference: 'JE-001',
        date: new Date(),
        memo: 'Test entry',
        status: 'draft',
        lines: [
          { account_id: '1000', account_name: 'Cash', debit: 1000, credit: 0, memo: '' },
          { account_id: '4000', account_name: 'Revenue', debit: 0, credit: 1000, memo: '' }
        ],
        total_amount: 1000
      }
    ];
  } finally {
    loading.value = false;
  }
};

// Lifecycle hooks
onMounted(() => {
  loadJournalEntries();
});
</script>