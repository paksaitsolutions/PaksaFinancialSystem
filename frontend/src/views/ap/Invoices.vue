<template>
  <div class="ap-invoices">
    <div class="page-header">
      <div class="container">
        <div class="header-content">
          <div>
            <h1>AP Invoices</h1>
            <p>Manage accounts payable invoices and payments</p>
          </div>
          <button class="btn btn-primary" @click="showCreateModal = true">
            + Create Invoice
          </button>
        </div>
      </div>
    </div>

    <div class="container">
      <!-- Summary Cards -->
      <div class="summary-section">
        <div class="summary-grid">
          <div class="summary-card">
            <h3>Total Outstanding</h3>
            <div class="amount red">{{ formatCurrency(summaryData.totalOutstanding) }}</div>
          </div>
          <div class="summary-card">
            <h3>Overdue Amount</h3>
            <div class="amount red">{{ formatCurrency(summaryData.overdueAmount) }}</div>
          </div>
          <div class="summary-card">
            <h3>This Month</h3>
            <div class="amount">{{ formatCurrency(summaryData.thisMonth) }}</div>
          </div>
          <div class="summary-card">
            <h3>Pending Approval</h3>
            <div class="amount orange">{{ formatCurrency(summaryData.pendingApproval) }}</div>
          </div>
        </div>
      </div>

      <!-- Filters -->
      <div class="filters-section">
        <div class="filters-grid">
          <input type="text" v-model="searchQuery" placeholder="Search invoices..." class="filter-input">
          <select v-model="selectedStatus" class="filter-input">
            <option value="">All Status</option>
            <option value="draft">Draft</option>
            <option value="pending">Pending Approval</option>
            <option value="approved">Approved</option>
            <option value="paid">Paid</option>
            <option value="overdue">Overdue</option>
          </select>
          <select v-model="selectedVendor" class="filter-input">
            <option value="">All Vendors</option>
            <option v-for="vendor in vendors" :key="vendor.id" :value="vendor.id">
              {{ vendor.name }}
            </option>
          </select>
          <input type="date" v-model="dateFilter" class="filter-input">
        </div>
      </div>

      <!-- Invoices Table -->
      <div class="table-card">
        <div class="table-header">
          <h3>Invoices ({{ filteredInvoices.length }})</h3>
          <div class="table-actions">
            <button class="btn btn-outline">Export</button>
            <button class="btn btn-outline">Bulk Actions</button>
          </div>
        </div>
        
        <div class="table-container">
          <table class="invoices-table">
            <thead>
              <tr>
                <th>Invoice #</th>
                <th>Vendor</th>
                <th>Date</th>
                <th>Due Date</th>
                <th>Amount</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="invoice in filteredInvoices" :key="invoice.id">
                <td class="invoice-number">{{ invoice.invoiceNumber }}</td>
                <td class="vendor-name">{{ invoice.vendorName }}</td>
                <td>{{ formatDate(invoice.invoiceDate) }}</td>
                <td :class="{ 'overdue': isOverdue(invoice.dueDate) }">
                  {{ formatDate(invoice.dueDate) }}
                </td>
                <td class="amount">{{ formatCurrency(invoice.amount) }}</td>
                <td>
                  <span class="status-badge" :class="invoice.status">
                    {{ invoice.status }}
                  </span>
                </td>
                <td>
                  <div class="action-buttons">
                    <button class="btn-icon" @click="viewInvoice(invoice)" title="View">👁️</button>
                    <button class="btn-icon" @click="editInvoice(invoice)" title="Edit">✏️</button>
                    <button class="btn-icon" @click="approveInvoice(invoice)" title="Approve" v-if="invoice.status === 'pending'">✅</button>
                    <button class="btn-icon" @click="payInvoice(invoice)" title="Pay" v-if="invoice.status === 'approved'">💰</button>
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
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h3>{{ editingInvoice ? 'Edit' : 'Create' }} Invoice</h3>
          <button class="modal-close" @click="closeModal">×</button>
        </div>
        
        <form @submit.prevent="saveInvoice" class="invoice-form">
          <div class="form-grid">
            <div class="form-group">
              <label>Vendor *</label>
              <select v-model="invoiceForm.vendorId" required class="form-input">
                <option value="">Select Vendor</option>
                <option v-for="vendor in vendors" :key="vendor.id" :value="vendor.id">
                  {{ vendor.name }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label>Invoice Number *</label>
              <input type="text" v-model="invoiceForm.invoiceNumber" required class="form-input">
            </div>
          </div>
          
          <div class="form-grid">
            <div class="form-group">
              <label>Invoice Date *</label>
              <input type="date" v-model="invoiceForm.invoiceDate" required class="form-input">
            </div>
            <div class="form-group">
              <label>Due Date *</label>
              <input type="date" v-model="invoiceForm.dueDate" required class="form-input">
            </div>
          </div>
          
          <div class="form-group">
            <label>Description</label>
            <textarea v-model="invoiceForm.description" class="form-input" rows="3"></textarea>
          </div>

          <!-- Invoice Lines -->
          <div class="invoice-lines">
            <h4>Invoice Lines</h4>
            <div v-for="(line, index) in invoiceForm.lines" :key="index" class="invoice-line">
              <div class="line-grid">
                <input type="text" v-model="line.description" placeholder="Description" class="form-input">
                <input type="number" v-model="line.quantity" placeholder="Qty" class="form-input" step="0.01">
                <input type="number" v-model="line.unitPrice" placeholder="Unit Price" class="form-input" step="0.01">
                <input type="number" :value="line.quantity * line.unitPrice" readonly class="form-input total">
                <button type="button" @click="removeLine(index)" class="btn-remove">×</button>
              </div>
            </div>
            <button type="button" @click="addLine" class="btn btn-outline">+ Add Line</button>
          </div>

          <div class="invoice-totals">
            <div class="totals-grid">
              <div class="total-row">
                <span>Subtotal:</span>
                <span>{{ formatCurrency(calculateSubtotal()) }}</span>
              </div>
              <div class="total-row">
                <span>Tax:</span>
                <input type="number" v-model="invoiceForm.taxAmount" class="form-input small" step="0.01">
              </div>
              <div class="total-row final">
                <span>Total:</span>
                <span>{{ formatCurrency(calculateTotal()) }}</span>
              </div>
            </div>
          </div>

          <div class="form-actions">
            <button type="button" @click="closeModal" class="btn btn-secondary">Cancel</button>
            <button type="submit" class="btn btn-primary">Save Invoice</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const showCreateModal = ref(false)
const editingInvoice = ref(null)
const searchQuery = ref('')
const selectedStatus = ref('')
const selectedVendor = ref('')
const dateFilter = ref('')

const summaryData = ref({
  totalOutstanding: 48500,
  overdueAmount: 12000,
  thisMonth: 25000,
  pendingApproval: 8500
})

const invoiceForm = ref({
  vendorId: '',
  invoiceNumber: '',
  invoiceDate: new Date().toISOString().split('T')[0],
  dueDate: '',
  description: '',
  taxAmount: 0,
  lines: [
    { description: '', quantity: 1, unitPrice: 0 }
  ]
})

const vendors = ref([
  { id: 1, name: 'ABC Supplies Inc.' },
  { id: 2, name: 'Tech Solutions LLC' },
  { id: 3, name: 'Construction Pro' }
])

const invoices = ref([
  {
    id: 1,
    invoiceNumber: 'INV-2024-001',
    vendorName: 'ABC Supplies Inc.',
    invoiceDate: '2024-01-15',
    dueDate: '2024-02-14',
    amount: 15000,
    status: 'approved'
  },
  {
    id: 2,
    invoiceNumber: 'INV-2024-002',
    vendorName: 'Tech Solutions LLC',
    invoiceDate: '2024-01-10',
    dueDate: '2024-01-25',
    amount: 8500,
    status: 'overdue'
  },
  {
    id: 3,
    invoiceNumber: 'INV-2024-003',
    vendorName: 'Construction Pro',
    invoiceDate: '2024-01-20',
    dueDate: '2024-02-19',
    amount: 25000,
    status: 'pending'
  }
])

const filteredInvoices = computed(() => {
  let filtered = invoices.value
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(invoice => 
      invoice.invoiceNumber.toLowerCase().includes(query) ||
      invoice.vendorName.toLowerCase().includes(query)
    )
  }
  
  if (selectedStatus.value) {
    filtered = filtered.filter(invoice => invoice.status === selectedStatus.value)
  }
  
  if (selectedVendor.value) {
    filtered = filtered.filter(invoice => invoice.vendorId === selectedVendor.value)
  }
  
  return filtered
})

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString()
}

const isOverdue = (dueDate: string) => {
  return new Date(dueDate) < new Date()
}

const calculateSubtotal = () => {
  return invoiceForm.value.lines.reduce((sum, line) => sum + (line.quantity * line.unitPrice), 0)
}

const calculateTotal = () => {
  return calculateSubtotal() + (invoiceForm.value.taxAmount || 0)
}

const addLine = () => {
  invoiceForm.value.lines.push({ description: '', quantity: 1, unitPrice: 0 })
}

const removeLine = (index: number) => {
  if (invoiceForm.value.lines.length > 1) {
    invoiceForm.value.lines.splice(index, 1)
  }
}

const viewInvoice = (invoice: any) => {
  console.log('Viewing invoice:', invoice.invoiceNumber)
}

const editInvoice = (invoice: any) => {
  editingInvoice.value = invoice
  showCreateModal.value = true
}

const approveInvoice = (invoice: any) => {
  invoice.status = 'approved'
}

const payInvoice = (invoice: any) => {
  invoice.status = 'paid'
}

const saveInvoice = () => {
  console.log('Saving invoice:', invoiceForm.value)
  closeModal()
}

const closeModal = () => {
  showCreateModal.value = false
  editingInvoice.value = null
  invoiceForm.value = {
    vendorId: '',
    invoiceNumber: '',
    invoiceDate: new Date().toISOString().split('T')[0],
    dueDate: '',
    description: '',
    taxAmount: 0,
    lines: [{ description: '', quantity: 1, unitPrice: 0 }]
  }
}
</script>

<style scoped>
.ap-invoices {
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

.summary-section {
  margin: 30px 0;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.summary-card {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  text-align: center;
}

.summary-card h3 {
  margin: 0 0 12px 0;
  color: #4a5568;
  font-size: 1rem;
}

.summary-card .amount {
  font-size: 1.8rem;
  font-weight: 700;
  color: #2d3748;
}

.amount.red {
  color: #e53e3e;
}

.amount.orange {
  color: #dd6b20;
}

.filters-section {
  margin: 20px 0;
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
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

.table-actions {
  display: flex;
  gap: 12px;
}

.invoices-table {
  width: 100%;
  border-collapse: collapse;
}

.invoices-table th,
.invoices-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #f7fafc;
}

.invoices-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #4a5568;
}

.invoice-number {
  font-family: monospace;
  font-weight: 600;
  color: #2d3748;
}

.vendor-name {
  font-weight: 500;
  color: #2d3748;
}

.amount {
  text-align: right;
  font-weight: 500;
}

.overdue {
  color: #e53e3e;
  font-weight: 600;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
  text-transform: capitalize;
}

.status-badge.draft {
  background: #f7fafc;
  color: #4a5568;
}

.status-badge.pending {
  background: #fff3e0;
  color: #ef6c00;
}

.status-badge.approved {
  background: #e3f2fd;
  color: #1565c0;
}

.status-badge.paid {
  background: #c6f6d5;
  color: #22543d;
}

.status-badge.overdue {
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

.modal-content.large {
  max-width: 1000px;
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

.invoice-form {
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

.form-input.small {
  width: 120px;
}

.invoice-lines {
  margin: 30px 0;
}

.invoice-lines h4 {
  margin-bottom: 15px;
  color: #2d3748;
}

.invoice-line {
  margin-bottom: 15px;
}

.line-grid {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr auto;
  gap: 10px;
  align-items: center;
}

.total {
  background: #f8f9fa;
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

.invoice-totals {
  margin: 30px 0;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.totals-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-width: 300px;
  margin-left: auto;
}

.total-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.total-row.final {
  border-top: 2px solid #e2e8f0;
  padding-top: 10px;
  font-weight: 600;
  font-size: 1.1rem;
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
  
  .summary-grid {
    grid-template-columns: 1fr;
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