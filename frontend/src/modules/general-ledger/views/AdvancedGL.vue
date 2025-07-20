<template>
  <div class="advanced-gl">
    <div class="page-header">
      <div class="container">
        <div class="header-content">
          <div>
            <h1>🏛️ General Ledger</h1>
            <p>Multi-dimensional financial core with real-time processing</p>
          </div>
          <div class="header-actions">
            <button class="btn btn-outline" @click="showReconciliation = true">🔄 Reconcile</button>
            <button class="btn btn-secondary" @click="showPeriodClose = true">📅 Period Close</button>
            <button class="btn btn-primary" @click="showJournalEntry = true">+ Journal Entry</button>
          </div>
        </div>
      </div>
    </div>

    <div class="container">
      <!-- GL Dashboard -->
      <div class="gl-dashboard">
        <div class="dashboard-grid">
          <div class="dashboard-card">
            <h3>📊 Trial Balance Status</h3>
            <div class="metric-value">{{ trialBalanceStatus.isBalanced ? 'Balanced' : 'Out of Balance' }}</div>
            <div class="metric-detail">Difference: {{ formatCurrency(trialBalanceStatus.difference) }}</div>
          </div>
          
          <div class="dashboard-card">
            <h3>🔄 Reconciliation Status</h3>
            <div class="metric-value">{{ reconciliationStatus.reconciled }}/{{ reconciliationStatus.total }}</div>
            <div class="metric-detail">{{ reconciliationStatus.percentage }}% Complete</div>
          </div>
          
          <div class="dashboard-card">
            <h3>📅 Current Period</h3>
            <div class="metric-value">{{ currentPeriod.name }}</div>
            <div class="metric-detail">Status: {{ currentPeriod.status }}</div>
          </div>
          
          <div class="dashboard-card">
            <h3>📈 Journal Entries</h3>
            <div class="metric-value">{{ journalEntryStats.thisMonth }}</div>
            <div class="metric-detail">This Month</div>
          </div>
        </div>
      </div>

      <!-- Multi-Dimensional Chart of Accounts -->
      <div class="coa-section">
        <div class="section-header">
          <h3>📋 Multi-Dimensional Chart of Accounts</h3>
          <div class="section-actions">
            <button class="btn btn-outline" @click="expandAll">Expand All</button>
            <button class="btn btn-outline" @click="collapseAll">Collapse All</button>
            <button class="btn btn-primary" @click="showAccountForm = true">+ Add Account</button>
          </div>
        </div>
        
        <div class="coa-tree">
          <div v-for="account in accountHierarchy" :key="account.id" class="account-node">
            <div class="account-item" :class="{ 'has-children': account.has_children }" @click="toggleAccount(account)">
              <div class="account-info">
                <span class="account-code">{{ account.account_code }}</span>
                <span class="account-name">{{ account.account_name }}</span>
                <span class="account-type" :class="account.account_type">{{ formatAccountType(account.account_type) }}</span>
              </div>
              <div class="account-balance">{{ formatCurrency(account.balance || 0) }}</div>
            </div>
            
            <div v-if="account.expanded && account.children" class="account-children">
              <div v-for="child in account.children" :key="child.id" class="child-account">
                <div class="account-item">
                  <div class="account-info">
                    <span class="account-code">{{ child.account_code }}</span>
                    <span class="account-name">{{ child.account_name }}</span>
                  </div>
                  <div class="account-balance">{{ formatCurrency(child.balance || 0) }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Real-Time Journal Entries -->
      <div class="journal-entries-section">
        <div class="section-header">
          <h3>📝 Recent Journal Entries</h3>
          <div class="section-actions">
            <select v-model="journalFilter" class="filter-select">
              <option value="all">All Entries</option>
              <option value="manual">Manual</option>
              <option value="automatic">Automatic</option>
              <option value="pending">Pending Approval</option>
            </select>
          </div>
        </div>
        
        <div class="journal-table">
          <table>
            <thead>
              <tr>
                <th>Entry #</th>
                <th>Date</th>
                <th>Description</th>
                <th>Type</th>
                <th>Amount</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="entry in filteredJournalEntries" :key="entry.id">
                <td class="entry-number">{{ entry.entry_number }}</td>
                <td>{{ formatDate(entry.entry_date) }}</td>
                <td class="description">{{ entry.description }}</td>
                <td>
                  <span class="entry-type" :class="entry.entry_type">{{ formatEntryType(entry.entry_type) }}</span>
                </td>
                <td class="amount">{{ formatCurrency(entry.total_debit) }}</td>
                <td>
                  <span class="status-badge" :class="entry.status">{{ formatStatus(entry.status) }}</span>
                </td>
                <td>
                  <div class="action-buttons">
                    <button class="btn-icon" @click="viewEntry(entry)" title="View">👁️</button>
                    <button class="btn-icon" @click="editEntry(entry)" title="Edit" :disabled="entry.status === 'posted'">✏️</button>
                    <button v-if="entry.status === 'approved'" class="btn-icon" @click="postEntry(entry)" title="Post">📌</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Advanced Journal Entry Modal -->
    <div v-if="showJournalEntry" class="modal-overlay" @click="closeJournalEntry">
      <div class="modal-content large-modal" @click.stop>
        <div class="modal-header">
          <h3>📝 Journal Entry</h3>
          <button class="modal-close" @click="closeJournalEntry">×</button>
        </div>
        
        <form @submit.prevent="saveJournalEntry" class="journal-form">
          <div class="form-grid">
            <div class="form-group">
              <label>Entry Type *</label>
              <select v-model="journalForm.entry_type" required class="form-input">
                <option value="manual">Manual</option>
                <option value="automatic">Automatic</option>
                <option value="recurring">Recurring</option>
                <option value="reversing">Reversing</option>
                <option value="accrual">Accrual</option>
              </select>
            </div>
            <div class="form-group">
              <label>Entry Date *</label>
              <input type="date" v-model="journalForm.entry_date" required class="form-input">
            </div>
          </div>
          
          <div class="form-group">
            <label>Description *</label>
            <textarea v-model="journalForm.description" required class="form-input" rows="2"></textarea>
          </div>

          <!-- Journal Entry Lines -->
          <div class="journal-lines-section">
            <h4>Journal Entry Lines</h4>
            <div class="lines-table">
              <table>
                <thead>
                  <tr>
                    <th>Account</th>
                    <th>Department</th>
                    <th>Cost Center</th>
                    <th>Debit</th>
                    <th>Credit</th>
                    <th>Description</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(line, index) in journalForm.lines" :key="index">
                    <td>
                      <select v-model="line.account_id" class="form-input" required>
                        <option value="">Select Account</option>
                        <option v-for="account in accounts" :key="account.id" :value="account.id">
                          {{ account.account_code }} - {{ account.account_name }}
                        </option>
                      </select>
                    </td>
                    <td>
                      <select v-model="line.department_id" class="form-input">
                        <option value="">Select Department</option>
                        <option v-for="dept in departments" :key="dept.id" :value="dept.id">
                          {{ dept.dimension_name }}
                        </option>
                      </select>
                    </td>
                    <td>
                      <select v-model="line.cost_center_id" class="form-input">
                        <option value="">Select Cost Center</option>
                        <option v-for="cc in costCenters" :key="cc.id" :value="cc.id">
                          {{ cc.dimension_name }}
                        </option>
                      </select>
                    </td>
                    <td>
                      <input type="number" v-model="line.debit_amount" class="form-input" step="0.01" @input="calculateTotals">
                    </td>
                    <td>
                      <input type="number" v-model="line.credit_amount" class="form-input" step="0.01" @input="calculateTotals">
                    </td>
                    <td>
                      <input type="text" v-model="line.description" class="form-input">
                    </td>
                    <td>
                      <button type="button" @click="removeLine(index)" class="btn-icon btn-danger">🗑️</button>
                    </td>
                  </tr>
                </tbody>
              </table>
              <button type="button" @click="addLine" class="btn btn-outline">+ Add Line</button>
            </div>
          </div>

          <!-- Entry Totals -->
          <div class="entry-totals">
            <div class="totals-grid">
              <div class="total-item">
                <span>Total Debits:</span>
                <span class="amount">{{ formatCurrency(totalDebits) }}</span>
              </div>
              <div class="total-item">
                <span>Total Credits:</span>
                <span class="amount">{{ formatCurrency(totalCredits) }}</span>
              </div>
              <div class="total-item" :class="{ 'out-of-balance': !isBalanced }">
                <span>Difference:</span>
                <span class="amount">{{ formatCurrency(Math.abs(totalDebits - totalCredits)) }}</span>
              </div>
            </div>
          </div>

          <div class="form-actions">
            <button type="button" @click="closeJournalEntry" class="btn btn-secondary">Cancel</button>
            <button type="button" @click="saveDraft" class="btn btn-outline">Save Draft</button>
            <button type="submit" class="btn btn-primary" :disabled="!isBalanced">Save & Post</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

// Reactive state
const showJournalEntry = ref(false)
const showReconciliation = ref(false)
const showPeriodClose = ref(false)
const showAccountForm = ref(false)
const journalFilter = ref('all')

// Dashboard data
const trialBalanceStatus = ref({
  isBalanced: true,
  difference: 0
})

const reconciliationStatus = ref({
  reconciled: 8,
  total: 10,
  percentage: 80
})

const currentPeriod = ref({
  name: 'January 2024',
  status: 'Open'
})

const journalEntryStats = ref({
  thisMonth: 156
})

// Journal form
const journalForm = ref({
  entry_type: 'manual',
  entry_date: new Date().toISOString().split('T')[0],
  description: '',
  lines: [
    {
      account_id: '',
      department_id: '',
      cost_center_id: '',
      debit_amount: 0,
      credit_amount: 0,
      description: ''
    }
  ]
})

// Mock data
const accountHierarchy = ref([
  {
    id: 1,
    account_code: '1000',
    account_name: 'Assets',
    account_type: 'asset',
    balance: 500000,
    has_children: true,
    expanded: false,
    children: [
      { id: 11, account_code: '1100', account_name: 'Current Assets', balance: 300000 },
      { id: 12, account_code: '1200', account_name: 'Fixed Assets', balance: 200000 }
    ]
  },
  {
    id: 2,
    account_code: '2000',
    account_name: 'Liabilities',
    account_type: 'liability',
    balance: 200000,
    has_children: true,
    expanded: false,
    children: [
      { id: 21, account_code: '2100', account_name: 'Current Liabilities', balance: 150000 },
      { id: 22, account_code: '2200', account_name: 'Long-term Liabilities', balance: 50000 }
    ]
  }
])

const journalEntries = ref([
  {
    id: 1,
    entry_number: 'JE-2024-000001',
    entry_date: '2024-01-15',
    description: 'Monthly depreciation expense',
    entry_type: 'automatic',
    total_debit: 5000,
    status: 'posted'
  },
  {
    id: 2,
    entry_number: 'JE-2024-000002',
    entry_date: '2024-01-16',
    description: 'Accrued expenses adjustment',
    entry_type: 'manual',
    total_debit: 2500,
    status: 'approved'
  }
])

const accounts = ref([
  { id: 1, account_code: '1100', account_name: 'Cash' },
  { id: 2, account_code: '1200', account_name: 'Accounts Receivable' },
  { id: 3, account_code: '5000', account_name: 'Office Expenses' }
])

const departments = ref([
  { id: 1, dimension_name: 'Sales' },
  { id: 2, dimension_name: 'Marketing' },
  { id: 3, dimension_name: 'Operations' }
])

const costCenters = ref([
  { id: 1, dimension_name: 'CC-001 - Administration' },
  { id: 2, dimension_name: 'CC-002 - Production' }
])

// Computed properties
const filteredJournalEntries = computed(() => {
  if (journalFilter.value === 'all') {
    return journalEntries.value
  }
  return journalEntries.value.filter(entry => entry.entry_type === journalFilter.value || entry.status === journalFilter.value)
})

const totalDebits = computed(() => {
  return journalForm.value.lines.reduce((sum, line) => sum + (parseFloat(line.debit_amount) || 0), 0)
})

const totalCredits = computed(() => {
  return journalForm.value.lines.reduce((sum, line) => sum + (parseFloat(line.credit_amount) || 0), 0)
})

const isBalanced = computed(() => {
  return Math.abs(totalDebits.value - totalCredits.value) < 0.01
})

// Methods
const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString()
}

const formatAccountType = (type: string) => {
  return type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const formatEntryType = (type: string) => {
  return type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const formatStatus = (status: string) => {
  return status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const toggleAccount = (account: any) => {
  account.expanded = !account.expanded
}

const expandAll = () => {
  accountHierarchy.value.forEach(account => {
    account.expanded = true
  })
}

const collapseAll = () => {
  accountHierarchy.value.forEach(account => {
    account.expanded = false
  })
}

const addLine = () => {
  journalForm.value.lines.push({
    account_id: '',
    department_id: '',
    cost_center_id: '',
    debit_amount: 0,
    credit_amount: 0,
    description: ''
  })
}

const removeLine = (index: number) => {
  if (journalForm.value.lines.length > 1) {
    journalForm.value.lines.splice(index, 1)
  }
}

const calculateTotals = () => {
  // Totals are computed automatically
}

const viewEntry = (entry: any) => {
  alert(`Viewing entry: ${entry.entry_number}`)
}

const editEntry = (entry: any) => {
  alert(`Editing entry: ${entry.entry_number}`)
}

const postEntry = (entry: any) => {
  if (confirm(`Post entry ${entry.entry_number}?`)) {
    entry.status = 'posted'
    alert('Entry posted successfully')
  }
}

const saveJournalEntry = () => {
  if (!isBalanced.value) {
    alert('Journal entry must be balanced')
    return
  }
  
  alert('Journal entry saved and posted successfully')
  closeJournalEntry()
}

const saveDraft = () => {
  alert('Journal entry saved as draft')
  closeJournalEntry()
}

const closeJournalEntry = () => {
  showJournalEntry.value = false
  journalForm.value = {
    entry_type: 'manual',
    entry_date: new Date().toISOString().split('T')[0],
    description: '',
    lines: [
      {
        account_id: '',
        department_id: '',
        cost_center_id: '',
        debit_amount: 0,
        credit_amount: 0,
        description: ''
      }
    ]
  }
}

onMounted(() => {
  // Load GL data
})
</script>

<style>
@import '/src/assets/styles/ar-advanced.css';

.advanced-gl {
  min-height: 100vh;
  background: #f8fafc;
}

.gl-dashboard {
  margin: 30px 0;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.dashboard-card {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  border: 1px solid #e2e8f0;
}

.dashboard-card h3 {
  margin: 0 0 12px 0;
  color: #4a5568;
  font-size: 1rem;
}

.metric-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #2d3748;
  margin-bottom: 8px;
}

.metric-detail {
  font-size: 0.9rem;
  color: #6b7280;
}

.coa-section,
.journal-entries-section {
  margin: 40px 0;
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid #f7fafc;
}

.section-header h3 {
  margin: 0;
  color: #2d3748;
  font-size: 1.3rem;
}

.section-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.coa-tree {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.account-node {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
}

.account-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.account-item:hover {
  background: #f8f9fa;
}

.account-item.has-children {
  background: #f0f9ff;
}

.account-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.account-code {
  font-family: monospace;
  font-weight: 600;
  color: #2d3748;
  min-width: 80px;
}

.account-name {
  font-weight: 500;
  color: #2d3748;
}

.account-type {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
}

.account-type.asset {
  background: #dcfce7;
  color: #166534;
}

.account-type.liability {
  background: #fef3c7;
  color: #92400e;
}

.account-type.equity {
  background: #e0f2fe;
  color: #0277bd;
}

.account-balance {
  font-family: monospace;
  font-weight: 600;
  color: #2d3748;
}

.account-children {
  background: #f8f9fa;
  border-top: 1px solid #e2e8f0;
}

.child-account {
  padding-left: 32px;
  border-bottom: 1px solid #e2e8f0;
}

.child-account:last-child {
  border-bottom: none;
}

.journal-table table {
  width: 100%;
  border-collapse: collapse;
}

.journal-table th,
.journal-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
}

.journal-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #4a5568;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.entry-number {
  font-family: monospace;
  font-weight: 600;
}

.description {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.entry-type {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
}

.entry-type.manual {
  background: #e0f2fe;
  color: #0277bd;
}

.entry-type.automatic {
  background: #dcfce7;
  color: #166534;
}

.amount {
  text-align: right;
  font-family: monospace;
  font-weight: 600;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-badge.posted {
  background: #dcfce7;
  color: #166534;
}

.status-badge.approved {
  background: #fef3c7;
  color: #92400e;
}

.status-badge.draft {
  background: #f3f4f6;
  color: #6b7280;
}

.journal-form {
  padding: 32px;
}

.journal-lines-section {
  margin: 32px 0;
}

.journal-lines-section h4 {
  margin-bottom: 16px;
  color: #2d3748;
}

.lines-table {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 16px;
}

.lines-table table {
  width: 100%;
  border-collapse: collapse;
}

.lines-table th,
.lines-table td {
  padding: 8px 12px;
  border-bottom: 1px solid #e2e8f0;
  vertical-align: top;
}

.lines-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #4a5568;
  font-size: 0.85rem;
}

.entry-totals {
  margin: 24px 0;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.totals-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.total-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.total-item.out-of-balance {
  color: #dc2626;
  font-weight: 600;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 0.9rem;
}

.large-modal {
  max-width: 1200px;
  width: 95%;
}

.btn-danger {
  color: #dc2626;
}

.btn-danger:hover {
  background: #fef2f2;
}

@media (max-width: 768px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  
  .section-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }
  
  .account-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .totals-grid {
    grid-template-columns: 1fr;
  }
  
  .large-modal {
    width: 98%;
    margin: 10px;
  }
}
</style>