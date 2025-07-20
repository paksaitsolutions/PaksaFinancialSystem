<template>
  <div class="journal-entries">
    <div class="page-header">
      <div class="container">
        <div class="header-content">
          <div>
            <h1>Journal Entries</h1>
            <p>Create and manage journal entries</p>
          </div>
          <button class="btn btn-primary" @click="showCreateModal = true">
            + New Entry
          </button>
        </div>
      </div>
    </div>

    <div class="container">
      <!-- Filters -->
      <div class="filters-section">
        <div class="filters-grid">
          <input type="date" v-model="filters.dateFrom" placeholder="From Date" class="filter-input">
          <input type="date" v-model="filters.dateTo" placeholder="To Date" class="filter-input">
          <select v-model="filters.status" class="filter-input">
            <option value="">All Status</option>
            <option value="draft">Draft</option>
            <option value="posted">Posted</option>
          </select>
          <button class="btn btn-secondary" @click="applyFilters">Filter</button>
        </div>
      </div>

      <!-- Entries Table -->
      <div class="table-card">
        <div class="table-header">
          <h3>Journal Entries</h3>
          <div class="table-actions">
            <button 
              class="btn btn-outline" 
              @click="showExportDialog = true"
              :disabled="!journalEntries.length"
            >
              <i class="pi pi-download mr-2"></i>Export
            </button>
          </div>
        </div>
        
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Entry #</th>
                <th>Date</th>
                <th>Description</th>
                <th>Reference</th>
                <th>Total Debit</th>
                <th>Total Credit</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="entry in journalEntries" :key="entry.id">
                <td>{{ entry.entryNumber }}</td>
                <td>{{ formatDate(entry.date) }}</td>
                <td>{{ entry.description }}</td>
                <td>{{ entry.reference }}</td>
                <td class="amount">{{ formatCurrency(entry.totalDebit) }}</td>
                <td class="amount">{{ formatCurrency(entry.totalCredit) }}</td>
                <td>
                  <span class="status-badge" :class="entry.status">
                    {{ entry.status }}
                  </span>
                </td>
                <td>
                  <div class="action-buttons">
                    <button class="btn-icon" @click="editEntry(entry)" title="Edit">✏️</button>
                    <button class="btn-icon" @click="viewEntry(entry)" title="View">👁️</button>
                    <button class="btn-icon" @click="deleteEntry(entry)" title="Delete">🗑️</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ editingEntry ? 'Edit' : 'Create' }} Journal Entry</h3>
          <button class="modal-close" @click="closeModal">×</button>
        </div>
        
        <form @submit.prevent="saveEntry" class="entry-form">
          <div class="form-grid">
            <div class="form-group">
              <label>Date</label>
              <input type="date" v-model="entryForm.date" required class="form-input">
            </div>
            <div class="form-group">
              <label>Reference</label>
              <input type="text" v-model="entryForm.reference" class="form-input">
            </div>
          </div>
          
          <div class="form-group">
            <label>Description</label>
            <textarea v-model="entryForm.description" required class="form-input" rows="3"></textarea>
          </div>

          <!-- Journal Lines -->
          <div class="journal-lines">
            <h4>Journal Lines</h4>
            <div v-for="(line, index) in entryForm.lines" :key="index" class="journal-line">
              <div class="line-grid">
                <select v-model="line.accountId" required class="form-input">
                  <option value="">Select Account</option>
                  <option v-for="account in accounts" :key="account.id" :value="account.id">
                    {{ account.code }} - {{ account.name }}
                  </option>
                </select>
                <input type="number" v-model="line.debit" placeholder="Debit" class="form-input" step="0.01">
                <input type="number" v-model="line.credit" placeholder="Credit" class="form-input" step="0.01">
                <button type="button" @click="removeLine(index)" class="btn-remove">×</button>
              </div>
            </div>
            <button type="button" @click="addLine" class="btn btn-outline">+ Add Line</button>
          </div>

          <div class="form-actions">
            <button type="button" @click="closeModal" class="btn btn-secondary">Cancel</button>
            <button type="submit" class="btn btn-primary">Save Entry</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Export Dialog -->
    <ExportDialog
      v-model:visible="showExportDialog"
      title="Export Journal Entries"
      :file-name="exportFileName"
      :columns="exportColumns"
      :data="journalEntries"
      :meta="{
        title: 'Journal Entries Report',
        description: 'List of all journal entries with details',
        generatedOn: new Date().toLocaleString(),
        generatedBy: 'System',
        includeSummary: true,
        filters: {
          'Date Range': filters.dateFrom && filters.dateTo 
            ? `${filters.dateFrom} to ${filters.dateTo}` 
            : 'All dates',
          'Status': filters.status || 'All statuses'
        }
      }"
      @export="handleExport"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useToast } from 'primevue/usetoast'
import ExportDialog from '@/components/common/ExportDialog.vue'
import { useExport } from '@/composables/useExport'

const showCreateModal = ref(false)
const showExportDialog = ref(false)
const editingEntry = ref(null)
const toast = useToast()

// Journal entries data
const journalEntries = ref([
  {
    id: 1,
    entryNumber: 'JE-2023-001',
    date: '2023-06-15',
    description: 'Monthly rent payment',
    reference: 'INV-001',
    totalDebit: 1200.00,
    totalCredit: 1200.00,
    status: 'posted'
  },
  // Add more mock entries as needed
])

// Form data
const entryForm = ref({
  date: '',
  reference: '',
  description: '',
  lines: [
    { account: '', description: '', debit: 0, credit: 0 }
  ]
})

// Filters
const filters = ref({
  dateFrom: '',
  dateTo: '',
  status: ''
})

// Export functionality
const exportFileName = computed(() => `journal-entries-${new Date().toISOString().split('T')[0]}`)

// Export columns configuration
const exportColumns = [
  { field: 'entryNumber', header: 'Entry #' },
  { field: 'date', header: 'Date' },
  { field: 'description', header: 'Description' },
  { field: 'reference', header: 'Reference' },
  { 
    field: 'totalDebit', 
    header: 'Total Debit',
    format: (val) => formatCurrency(val)
  },
  { 
    field: 'totalCredit', 
    header: 'Total Credit',
    format: (val) => formatCurrency(val)
  },
  { field: 'status', header: 'Status' }
]

// Initialize export functionality
const { exportData, exportProgress, exportInProgress } = useExport({
  data: journalEntries,
  columns: exportColumns,
  fileName: exportFileName,
  meta: {
    title: 'Journal Entries Report',
    description: 'List of all journal entries',
    generatedOn: new Date().toLocaleString(),
    generatedBy: 'System',
    filters: {
      'Date Range': filters.value.dateFrom && filters.value.dateTo 
        ? `${filters.value.dateFrom} to ${filters.value.dateTo}` 
        : 'All dates',
      'Status': filters.value.status || 'All statuses'
    }
  }
})

const accounts = ref([
  { id: 1, code: '1000', name: 'Cash' },
  { id: 2, code: '1200', name: 'Accounts Receivable' },
  { id: 3, code: '2000', name: 'Accounts Payable' },
  { id: 4, code: '5000', name: 'Office Expenses' },
  { id: 5, code: '6000', name: 'Rent Expense' }
])

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString()
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}

const addLine = () => {
  entryForm.value.lines.push({ account: '', description: '', debit: 0, credit: 0 })
}

const removeLine = (index: number) => {
  if (entryForm.value.lines.length > 2) {
    entryForm.value.lines.splice(index, 1)
  }
}

const closeModal = () => {
  showCreateModal.value = false
  editingEntry.value = null
  resetForm()
}

const resetForm = () => {
  entryForm.value = {
    date: '',
    reference: '',
    description: '',
    lines: [
      { account: '', description: '', debit: 0, credit: 0 }
    ]
  }
}

const saveEntry = () => {
  console.log('Saving entry:', entryForm.value)
  closeModal()
}

const editEntry = (entry: any) => {
  editingEntry.value = entry
  showCreateModal.value = true
}

const viewEntry = (entry: any) => {
  console.log('Viewing entry:', entry)
}

const deleteEntry = (entry: any) => {
  if (confirm('Are you sure you want to delete this entry?')) {
    const index = journalEntries.value.findIndex(e => e.id === entry.id)
    if (index > -1) {
      journalEntries.value.splice(index, 1)
    }
  }
}

const applyFilters = () => {
  console.log('Applying filters:', filters.value)
}

const handleExport = async ({ format, options }) => {
  try {
    await exportData(format, options)
    toast.add({
      severity: 'success',
      summary: 'Export Successful',
      detail: 'Journal entries exported successfully',
      life: 3000
    })
  } catch (error) {
    console.error('Export failed:', error)
    toast.add({
      severity: 'error',
      summary: 'Export Failed',
      detail: 'Failed to export journal entries. Please try again.',
      life: 5000
    })
  }
}

onMounted(() => {
  // Load data
})
</script>

<style scoped>
.journal-entries {
  min-height: 100vh;
  background: #f5f7fa;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.page-header {
  background: white;
  border-bottom: 1px solid #e0e6ed;
  padding: 20px 0;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content h1 {
  font-size: 2rem;
  font-weight: 600;
  color: #2d3748;
  margin: 0;
}

.header-content p {
  color: #718096;
  margin: 5px 0 0 0;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #1976D2;
  color: white;
}

.btn-secondary {
  background: #e2e8f0;
  color: #4a5568;
}

.btn-outline {
  background: transparent;
  border: 1px solid #e2e8f0;
  color: #4a5568;
}

.filters-section {
  margin: 20px 0;
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  align-items: end;
}

.filter-input {
  padding: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: white;
}

.table-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  overflow: hidden;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e2e8f0;
}

.table-header h3 {
  margin: 0;
  color: #2d3748;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #f7fafc;
}

.data-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #4a5568;
}

.amount {
  text-align: right;
  font-weight: 500;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}

.status-badge.posted {
  background: #c6f6d5;
  color: #22543d;
}

.status-badge.draft {
  background: #fed7d7;
  color: #742a2a;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
}

.btn-icon:hover {
  background: #f7fafc;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e2e8f0;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
}

.entry-form {
  padding: 24px;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #4a5568;
}

.form-input {
  width: 100%;
  padding: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
}

.journal-lines {
  margin: 30px 0;
}

.journal-lines h4 {
  margin-bottom: 15px;
  color: #2d3748;
}

.journal-line {
  margin-bottom: 15px;
}

.line-grid {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr auto;
  gap: 10px;
  align-items: center;
}

.btn-remove {
  background: #fed7d7;
  color: #742a2a;
  border: none;
  border-radius: 4px;
  width: 30px;
  height: 30px;
  cursor: pointer;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 30px;
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 16px;
    text-align: center;
  }
  
  .filters-grid {
    grid-template-columns: 1fr;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .line-grid {
    grid-template-columns: 1fr;
    gap: 8px;
  }
}
</style>