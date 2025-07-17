<template>
  <div class="ap-payments">
    <div class="page-header">
      <div class="container">
        <div class="header-content">
          <div>
            <h1>AP Payments</h1>
            <p>Process and manage vendor payments</p>
          </div>
          <div class="header-actions">
            <button class="btn btn-outline" @click="bulkProcess">Bulk Process</button>
            <button class="btn btn-secondary" @click="exportPayments" :disabled="payments.length === 0">
              <i class="pi pi-download mr-2"></i>
              {{ isExporting ? 'Exporting...' : 'Export' }}
            </button>
            <button class="btn btn-primary" @click="showCreateModal = true">
              + Create Payment
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="container">
      <!-- Payment Summary -->
      <div class="summary-section">
        <div class="summary-grid">
          <div class="summary-card">
            <h3>Payments This Month</h3>
            <div class="amount">{{ formatCurrency(summaryData.thisMonth) }}</div>
          </div>
          <div class="summary-card">
            <h3>Pending Payments</h3>
            <div class="amount orange">{{ formatCurrency(summaryData.pending) }}</div>
          </div>
          <div class="summary-card">
            <h3>Scheduled Payments</h3>
            <div class="amount blue">{{ formatCurrency(summaryData.scheduled) }}</div>
          </div>
          <div class="summary-card">
            <h3>Total Paid YTD</h3>
            <div class="amount green">{{ formatCurrency(summaryData.yearToDate) }}</div>
          </div>
        </div>
      </div>

      <!-- Filters -->
      <div class="filters-section">
        <div class="filters-grid">
          <input type="text" v-model="searchQuery" placeholder="Search payments..." class="filter-input">
          <select v-model="selectedStatus" class="filter-input">
            <option value="">All Status</option>
            <option value="pending">Pending</option>
            <option value="scheduled">Scheduled</option>
            <option value="processed">Processed</option>
            <option value="failed">Failed</option>
          </select>
          <select v-model="selectedMethod" class="filter-input">
            <option value="">All Methods</option>
            <option value="check">Check</option>
            <option value="ach">ACH</option>
            <option value="wire_transfer">Wire Transfer</option>
            <option value="ibft">IBFT</option>
            <option value="cash">Cash</option>
            <option value="debit_card">Debit Card</option>
            <option value="credit_card">Credit Card</option>
            <option value="digital_wallet">Digital Wallet</option>
            <option value="crypto">Cryptocurrency</option>
            <option value="mobile_payment">Mobile Payment</option>
            <option value="online_banking">Online Banking</option>
          </select>
          <input type="date" v-model="dateFilter" class="filter-input">
        </div>
      </div>

      <!-- Payments Table -->
      <div class="table-card">
        <div class="table-header">
          <h3>Payments ({{ filteredPayments.length }})</h3>
          <div class="table-actions">
            <button class="btn btn-outline">Export</button>
            <button class="btn btn-outline">Bulk Process</button>
          </div>
        </div>
        
        <div class="table-container">
          <table class="payments-table">
            <thead>
              <tr>
                <th>Payment #</th>
                <th>Vendor</th>
                <th>Invoice #</th>
                <th>Amount</th>
                <th>Method</th>
                <th>Date</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="payment in filteredPayments" :key="payment.id">
                <td class="payment-number">{{ payment.paymentNumber }}</td>
                <td class="vendor-name">{{ payment.vendorName }}</td>
                <td class="invoice-number">{{ payment.invoiceNumber }}</td>
                <td class="amount">{{ formatCurrency(payment.amount) }}</td>
                <td>
                  <span class="method-badge" :class="payment.method">
                    {{ payment.method.toUpperCase() }}
                  </span>
                </td>
                <td>{{ formatDate(payment.paymentDate) }}</td>
                <td>
                  <span class="status-badge" :class="payment.status">
                    {{ payment.status }}
                  </span>
                </td>
                <td>
                  <div class="action-buttons">
                    <button class="btn-icon" @click="viewPayment(payment)" title="View">👁️</button>
                    <button class="btn-icon" @click="editPayment(payment)" title="Edit" v-if="payment.status === 'pending'">✏️</button>
                    <button class="btn-icon" @click="processPayment(payment)" title="Process" v-if="payment.status === 'pending'">▶️</button>
                    <button class="btn-icon" @click="printCheck(payment)" title="Print" v-if="payment.method === 'check'">🖨️</button>
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
          <h3>{{ editingPayment ? 'Edit' : 'Create' }} Payment</h3>
          <button class="modal-close" @click="closeModal">×</button>
        </div>
        
        <form @submit.prevent="savePayment" class="payment-form">
          <div class="form-grid">
            <div class="form-group">
              <label>Vendor *</label>
              <select v-model="paymentForm.vendorId" required class="form-input" @change="loadVendorInvoices">
                <option value="">Select Vendor</option>
                <option v-for="vendor in vendors" :key="vendor.id" :value="vendor.id">
                  {{ vendor.name }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label>Payment Method *</label>
              <select v-model="paymentForm.method" required class="form-input">
                <option value="">Select Method</option>
                <option value="check">Check</option>
                <option value="ach">ACH Transfer</option>
                <option value="wire_transfer">Wire Transfer</option>
                <option value="ibft">IBFT (Interbank Fund Transfer)</option>
                <option value="cash">Cash</option>
                <option value="debit_card">Debit Card</option>
                <option value="credit_card">Credit Card</option>
                <option value="digital_wallet">Digital Wallet (PayPal, Stripe)</option>
                <option value="crypto">Cryptocurrency</option>
                <option value="bank_transfer">Bank Transfer</option>
                <option value="mobile_payment">Mobile Payment (Apple Pay, Google Pay)</option>
                <option value="online_banking">Online Banking</option>
              </select>
            </div>
          </div>
          
          <div class="form-grid">
            <div class="form-group">
              <label>Payment Date *</label>
              <input type="date" v-model="paymentForm.paymentDate" required class="form-input">
            </div>
            <div class="form-group">
              <label>Reference Number</label>
              <input type="text" v-model="paymentForm.referenceNumber" class="form-input">
            </div>
          </div>

          <!-- Invoice Selection -->
          <div class="invoice-selection" v-if="paymentForm.vendorId">
            <h4>Select Invoices to Pay</h4>
            <div class="invoice-list">
              <div v-for="invoice in vendorInvoices" :key="invoice.id" class="invoice-item">
                <label class="invoice-checkbox">
                  <input type="checkbox" v-model="invoice.selected" @change="updatePaymentAmount">
                  <div class="invoice-details">
                    <div class="invoice-info">
                      <span class="invoice-num">{{ invoice.invoiceNumber }}</span>
                      <span class="invoice-date">{{ formatDate(invoice.dueDate) }}</span>
                    </div>
                    <div class="invoice-amount">{{ formatCurrency(invoice.amount) }}</div>
                  </div>
                </label>
              </div>
            </div>
          </div>

          <div class="payment-summary">
            <div class="summary-row">
              <span>Total Payment Amount:</span>
              <span class="total-amount">{{ formatCurrency(paymentForm.totalAmount) }}</span>
            </div>
          </div>
          
          <div class="form-group">
            <label>Notes</label>
            <textarea v-model="paymentForm.notes" class="form-input" rows="3"></textarea>
          </div>

          <div class="form-actions">
            <button type="button" @click="closeModal" class="btn btn-secondary">Cancel</button>
            <button type="submit" class="btn btn-primary">Save Payment</button>
          </div>
        </form>
      </div>
    </div>
  </div>

  <!-- Export Dialog -->
  <ExportDialog 
    v-model:visible="exportDialog"
    :formats="['pdf', 'excel', 'csv']"
    :loading="isExporting"
    @export="handleExport"
    title="Export Payments"
    description="Select format and options for exporting payments data"
  />
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useExport } from '@/composables/useExport'
import ExportDialog from '@/components/common/ExportDialog.vue'

const showCreateModal = ref(false)
const editingPayment = ref(null)
const searchQuery = ref('')
const selectedStatus = ref('')
const selectedMethod = ref('')
const dateFilter = ref('')

const summaryData = ref({
  thisMonth: 45000,
  pending: 12500,
  scheduled: 8000,
  yearToDate: 125000
})

const paymentForm = ref({
  vendorId: '',
  method: '',
  paymentDate: new Date().toISOString().split('T')[0],
  referenceNumber: '',
  totalAmount: 0,
  notes: ''
})

const vendors = ref([
  { id: 1, name: 'ABC Supplies Inc.' },
  { id: 2, name: 'Tech Solutions LLC' },
  { id: 3, name: 'Construction Pro' }
])

const vendorInvoices = ref([])

const payments = ref([
  {
    id: 1,
    paymentNumber: 'PAY-2024-001',
    vendorName: 'ABC Supplies Inc.',
    invoiceNumber: 'INV-2024-001',
    amount: 15000,
    method: 'check',
    paymentDate: '2024-01-15',
    status: 'processed'
  },
  {
    id: 2,
    paymentNumber: 'PAY-2024-002',
    vendorName: 'Tech Solutions LLC',
    invoiceNumber: 'INV-2024-002',
    amount: 8500,
    method: 'ach',
    paymentDate: '2024-01-20',
    status: 'pending'
  },
  {
    id: 3,
    paymentNumber: 'PAY-2024-003',
    vendorName: 'Construction Pro',
    invoiceNumber: 'INV-2024-003',
    amount: 25000,
    method: 'wire_transfer',
    paymentDate: '2024-01-25',
    status: 'scheduled'
  },
  {
    id: 4,
    paymentNumber: 'PAY-2024-004',
    vendorName: 'Digital Services Co.',
    invoiceNumber: 'INV-2024-004',
    amount: 3200,
    method: 'digital_wallet',
    paymentDate: '2024-01-28',
    status: 'processed'
  },
  {
    id: 5,
    paymentNumber: 'PAY-2024-005',
    vendorName: 'Local Bank',
    invoiceNumber: 'INV-2024-005',
    amount: 1800,
    method: 'ibft',
    paymentDate: '2024-01-30',
    status: 'pending'
  },
  {
    id: 6,
    paymentNumber: 'PAY-2024-006',
    vendorName: 'Mobile Tech Ltd.',
    invoiceNumber: 'INV-2024-006',
    amount: 950,
    method: 'mobile_payment',
    paymentDate: '2024-02-01',
    status: 'processed'
  }
])

const filteredPayments = computed(() => {
  let filtered = payments.value
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(payment => 
      payment.paymentNumber.toLowerCase().includes(query) ||
      payment.vendorName.toLowerCase().includes(query) ||
      payment.invoiceNumber.toLowerCase().includes(query)
    )
  }
  
  if (selectedStatus.value) {
    filtered = filtered.filter(payment => payment.status === selectedStatus.value)
  }
  
  if (selectedMethod.value) {
    filtered = filtered.filter(payment => payment.method === selectedMethod.value)
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

const loadVendorInvoices = () => {
  // Mock data - in real app, fetch from API
  vendorInvoices.value = [
    { id: 1, invoiceNumber: 'INV-001', dueDate: '2024-02-15', amount: 5000, selected: false },
    { id: 2, invoiceNumber: 'INV-002', dueDate: '2024-02-20', amount: 3500, selected: false },
    { id: 3, invoiceNumber: 'INV-003', dueDate: '2024-02-25', amount: 7500, selected: false }
  ]
}

const updatePaymentAmount = () => {
  paymentForm.value.totalAmount = vendorInvoices.value
    .filter(invoice => invoice.selected)
    .reduce((sum, invoice) => sum + invoice.amount, 0)
}

const viewPayment = (payment: any) => {
  window.open(`/ap/payments/${payment.id}`, '_blank')
}

const editPayment = (payment: any) => {
  editingPayment.value = payment
  paymentForm.value = {
    vendorId: payment.vendorId,
    method: payment.method,
    paymentDate: payment.paymentDate,
    referenceNumber: payment.referenceNumber,
    totalAmount: payment.amount,
    notes: payment.notes || ''
  }
  showCreateModal.value = true
}

const processPayment = (payment: any) => {
  if (confirm(`Process payment ${payment.paymentNumber}?`)) {
    payment.status = 'processed'
    alert('Payment processed successfully')
  }
}

const printCheck = (payment: any) => {
  const checkData = {
    paymentNumber: payment.paymentNumber,
    vendorName: payment.vendorName,
    amount: payment.amount,
    date: payment.paymentDate
  }
  
  const printWindow = window.open('', '_blank')
  printWindow.document.write(`
    <html>
      <head><title>Check - ${payment.paymentNumber}</title></head>
      <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2>Payment Check</h2>
        <p><strong>Payment #:</strong> ${checkData.paymentNumber}</p>
        <p><strong>Pay to:</strong> ${checkData.vendorName}</p>
        <p><strong>Amount:</strong> $${checkData.amount}</p>
        <p><strong>Date:</strong> ${checkData.date}</p>
        <button onclick="window.print()">Print</button>
      </body>
    </html>
  `)
}

const savePayment = () => {
  if (!paymentForm.value.vendorId || !paymentForm.value.method) {
    alert('Please fill in required fields')
    return
  }
  
  if (editingPayment.value) {
    const index = payments.value.findIndex(p => p.id === editingPayment.value.id)
    if (index > -1) {
      payments.value[index] = {
        ...payments.value[index],
        ...paymentForm.value
      }
    }
    alert('Payment updated successfully')
  } else {
    const newPayment = {
      id: Math.max(...payments.value.map(p => p.id)) + 1,
      paymentNumber: `PAY-${new Date().getFullYear()}-${String(Math.max(...payments.value.map(p => parseInt(p.paymentNumber.split('-')[2]))) + 1).padStart(3, '0')}`,
      ...paymentForm.value,
      status: 'pending'
    }
    payments.value.push(newPayment)
    alert('Payment created successfully')
  }
  
  closeModal()
}

const closeModal = () => {
  editingPayment.value = null
  showCreateModal.value = false
  selectedVendor.value = null
  paymentAmount.value = ''
  paymentDate.value = ''
  paymentMethod.value = ''
  paymentReference.value = ''
  selectedInvoices.value = []
  paymentNotes.value = ''
  selectedBankAccount.value = null
  isProcessing.value = false
}

const toast = useToast()
const exportDialog = ref(false)
const isExporting = ref(false)

const exportColumns = [
  { field: 'paymentNumber', header: 'Payment #', width: '120px' },
  { field: 'vendorName', header: 'Vendor', width: '180px' },
  { field: 'invoiceNumber', header: 'Invoice #', width: '120px' },
  { field: 'paymentDate', header: 'Date', width: '100px', type: 'date' },
  { field: 'method', header: 'Method', width: '120px' },
  { field: 'reference', header: 'Reference', width: '150px' },
  { field: 'amount', header: 'Amount', width: '120px', type: 'currency', format: { symbol: '$', decimal: 2 } },
  { field: 'status', header: 'Status', width: '120px' },
  { field: 'notes', header: 'Notes', width: '200px' }
]

const exportData = computed(() => {
  return payments.value.map(payment => ({
    paymentNumber: payment.paymentNumber,
    vendorName: payment.vendorName,
    invoiceNumber: payment.invoiceNumber,
    paymentDate: payment.paymentDate,
    method: payment.method,
    reference: payment.reference || 'N/A',
    amount: payment.amount,
    status: payment.status,
    notes: payment.notes || ''
  }))
})

const exportPayments = () => {
  exportDialog.value = true
}

const handleExport = async (format: string, options: any = {}) => {
  try {
    isExporting.value = true
    
    const { exportData: exportFn } = useExport()
    
    const exportOptions = {
      title: 'AP Payments',
      columns: exportColumns,
      data: exportData.value,
      filename: `ap-payments-${new Date().toISOString().split('T')[0]}`,
      ...options
    }
    
    await exportFn(format, exportOptions)
    
    toast.add({
      severity: 'success',
      summary: 'Export Successful',
      detail: `Payments exported successfully as ${format.toUpperCase()}`,
      life: 3000
    })
  } catch (error) {
    console.error('Export failed:', error)
    toast.add({
      severity: 'error',
      summary: 'Export Failed',
      detail: 'Failed to export payments. Please try again.',
      life: 3000
    })
  } finally {
    isExporting.value = false
  }
}

const bulkProcess = () => {
  alert('Bulk process functionality')
}
</script>

<style scoped>
.ap-payments {
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

.amount.orange {
  color: #dd6b20;
}

.amount.blue {
  color: #3182ce;
}

.amount.green {
  color: #38a169;
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

.payments-table {
  width: 100%;
  border-collapse: collapse;
}

.payments-table th,
.payments-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #f7fafc;
}

.payments-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #4a5568;
}

.payment-number,
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

.method-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
}

.method-badge.check {
  background: #e3f2fd;
  color: #1565c0;
}

.method-badge.ach {
  background: #e8f5e8;
  color: #2e7d32;
}

.method-badge.wire_transfer {
  background: #fff3e0;
  color: #ef6c00;
}

.method-badge.ibft {
  background: #e1f5fe;
  color: #0277bd;
}

.method-badge.cash {
  background: #f1f8e9;
  color: #33691e;
}

.method-badge.debit_card {
  background: #fce4ec;
  color: #ad1457;
}

.method-badge.credit_card {
  background: #f3e5f5;
  color: #7b1fa2;
}

.method-badge.digital_wallet {
  background: #e8eaf6;
  color: #3f51b5;
}

.method-badge.crypto {
  background: #fff8e1;
  color: #f57f17;
}

.method-badge.bank_transfer {
  background: #e0f2f1;
  color: #00695c;
}

.method-badge.mobile_payment {
  background: #fafafa;
  color: #424242;
}

.method-badge.online_banking {
  background: #e8f5e8;
  color: #1b5e20;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
  text-transform: capitalize;
}

.status-badge.pending {
  background: #fff3e0;
  color: #ef6c00;
}

.status-badge.scheduled {
  background: #e3f2fd;
  color: #1565c0;
}

.status-badge.processed {
  background: #c6f6d5;
  color: #22543d;
}

.status-badge.failed {
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
  max-width: 700px;
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

.payment-form {
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

.invoice-selection {
  margin: 30px 0;
}

.invoice-selection h4 {
  margin-bottom: 15px;
  color: #2d3748;
}

.invoice-list {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  max-height: 200px;
  overflow-y: auto;
}

.invoice-item {
  border-bottom: 1px solid #f7fafc;
}

.invoice-item:last-child {
  border-bottom: none;
}

.invoice-checkbox {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  cursor: pointer;
}

.invoice-checkbox:hover {
  background: #f8f9fa;
}

.invoice-checkbox input {
  margin-right: 12px;
}

.invoice-details {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.invoice-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.invoice-num {
  font-weight: 500;
  color: #2d3748;
}

.invoice-date {
  font-size: 0.8rem;
  color: #718096;
}

.invoice-amount {
  font-weight: 500;
  color: #2d3748;
}

.payment-summary {
  margin: 20px 0;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.total-amount {
  font-size: 1.2rem;
  font-weight: 600;
  color: #2d3748;
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
}
</style>