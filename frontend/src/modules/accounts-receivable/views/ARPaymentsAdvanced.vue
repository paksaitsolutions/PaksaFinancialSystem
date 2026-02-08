<template>
  <div class="ar-payments-advanced">
    <div class="page-header">
      <div class="container">
        <div class="header-content">
          <div>
            <h1>AR Payments</h1>
            <p>Advanced payment processing and management</p>
          </div>
          <div class="header-actions">
            <button class="btn btn-outline" @click="bulkProcess">Bulk Process</button>
            <button class="btn btn-secondary" @click="exportPayments" :disabled="payments.length === 0">
              <i class="pi pi-download mr-2"></i>
              {{ isExporting ? 'Exporting...' : 'Export' }}
            </button>
            <button class="btn btn-primary" @click="showCreateModal = true">+ Record Payment</button>
          </div>
        </div>
      </div>
    </div>

    <div class="container">
      <!-- Summary Cards -->
      <div class="summary-section">
        <div class="summary-grid">
          <div class="summary-card">
            <h3>Payments This Month</h3>
            <div class="amount">{{ formatCurrency(summaryData.thisMonth) }}</div>
            <div class="trend positive">↗ +15.2%</div>
          </div>
          <div class="summary-card">
            <h3>Pending Payments</h3>
            <div class="amount orange">{{ formatCurrency(summaryData.pending) }}</div>
            <div class="trend">{{ summaryData.pendingCount }} items</div>
          </div>
          <div class="summary-card">
            <h3>Failed Payments</h3>
            <div class="amount red">{{ formatCurrency(summaryData.failed) }}</div>
            <div class="trend negative">{{ summaryData.failedCount }} items</div>
          </div>
          <div class="summary-card">
            <h3>Success Rate</h3>
            <div class="amount green">{{ summaryData.successRate }}%</div>
            <div class="trend positive">↗ +2.1%</div>
          </div>
        </div>
      </div>

      <!-- Payments Table -->
      <div class="table-card">
        <div class="table-header">
          <h3>Payments ({{ payments.length }})</h3>
          <div class="table-actions">
            <button class="btn btn-outline">Export</button>
            <button class="btn btn-outline">Print</button>
          </div>
        </div>
        
        <div class="table-container">
          <table class="payments-table">
            <thead>
              <tr>
                <th>Payment #</th>
                <th>Customer</th>
                <th>Invoice #</th>
                <th>Amount</th>
                <th>Method</th>
                <th>Date</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="payment in payments" :key="payment.id">
                <td class="payment-number">{{ payment.paymentNumber }}</td>
                <td class="customer-name">{{ payment.customerName }}</td>
                <td class="invoice-number">{{ payment.invoiceNumber }}</td>
                <td class="amount">{{ formatCurrency(payment.amount) }}</td>
                <td>
                  <span class="method-badge" :class="payment.method">
                    {{ formatMethod(payment.method) }}
                  </span>
                </td>
                <td>{{ formatDate(payment.paymentDate) }}</td>
                <td>
                  <span class="status-badge" :class="payment.status">
                    {{ formatStatus(payment.status) }}
                  </span>
                </td>
                <td>
                  <div class="action-buttons">
                    <button class="btn-icon" @click="viewPayment(payment)" title="View">👁️</button>
                    <button class="btn-icon" @click="editPayment(payment)" title="Edit">✏️</button>
                    <button class="btn-icon" @click="processPayment(payment)" title="Process">▶️</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Create Payment Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content advanced-modal" @click.stop>
        <div class="modal-header">
          <h3>Record Payment</h3>
          <button class="modal-close" @click="closeModal">×</button>
        </div>
        
        <form @submit.prevent="savePayment" class="payment-form">
          <ErrorPanel
            v-if="formError"
            :visible="!!formError"
            title="Unable to record payment"
            :message="formError.message"
            :request-id="formError.requestId"
            :details="formError.details"
          />
          <div class="form-grid">
            <div class="form-group">
              <label>Customer *</label>
              <select
                v-model="paymentForm.customerId"
                required
                class="form-input"
                :class="{ 'input-error': showValidation && formErrors.customerId }"
                :aria-invalid="showValidation && !!formErrors.customerId"
                :aria-describedby="formErrors.customerId ? 'payment_customer_error' : undefined"
                @change="loadCustomerInvoices"
              >
                <option value="">Select Customer</option>
                <option v-for="customer in customers" :key="customer.id" :value="customer.id">
                  {{ customer.name }}
                </option>
              </select>
              <small v-if="showValidation && formErrors.customerId" id="payment_customer_error" class="error-text">
                {{ formErrors.customerId }}
              </small>
            </div>
            <div class="form-group">
              <label>Payment Method *</label>
              <select
                v-model="paymentForm.method"
                required
                class="form-input"
                :class="{ 'input-error': showValidation && formErrors.method }"
                :aria-invalid="showValidation && !!formErrors.method"
                :aria-describedby="formErrors.method ? 'payment_method_error' : undefined"
              >
                <option value="">Select Method</option>
                <option value="cash">Cash</option>
                <option value="check">Check</option>
                <option value="credit_card">Credit Card</option>
                <option value="bank_transfer">Bank Transfer</option>
                <option value="digital_wallet">Digital Wallet</option>
              </select>
              <small v-if="showValidation && formErrors.method" id="payment_method_error" class="error-text">
                {{ formErrors.method }}
              </small>
            </div>
          </div>
          
          <div class="form-grid">
            <div class="form-group">
              <label>Payment Date *</label>
              <input
                type="date"
                v-model="paymentForm.paymentDate"
                required
                class="form-input"
                :class="{ 'input-error': showValidation && formErrors.paymentDate }"
                :aria-invalid="showValidation && !!formErrors.paymentDate"
                :aria-describedby="formErrors.paymentDate ? 'payment_date_error' : undefined"
              >
              <small v-if="showValidation && formErrors.paymentDate" id="payment_date_error" class="error-text">
                {{ formErrors.paymentDate }}
              </small>
            </div>
            <div class="form-group">
              <label>Reference Number</label>
              <input type="text" v-model="paymentForm.referenceNumber" class="form-input">
            </div>
          </div>

          <!-- Invoice Selection -->
          <div class="invoice-selection" v-if="paymentForm.customerId">
            <h4>Select Invoices to Pay</h4>
            <small v-if="showValidation && formErrors.totalAmount" class="error-text">
              {{ formErrors.totalAmount }}
            </small>
            <div class="invoice-list">
              <div v-for="invoice in customerInvoices" :key="invoice.id" class="invoice-item">
                <label class="invoice-checkbox">
                  <input type="checkbox" v-model="invoice.selected" @change="updatePaymentAmount">
                  <div class="invoice-details">
                    <div class="invoice-info">
                      <span class="invoice-num">{{ invoice.invoiceNumber }}</span>
                      <span class="invoice-date">{{ formatDate(invoice.dueDate) }}</span>
                    </div>
                    <div class="invoice-amount">{{ formatCurrency(invoice.balanceDue) }}</div>
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
            <button type="submit" class="btn btn-primary">Record Payment</button>
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
import { useReportExport } from '@/composables/useReportExport'
import { api } from '@/utils/api'
import ErrorPanel from '@/components/common/ErrorPanel.vue'
import { validateSchema } from '@/utils/formValidation'

const showCreateModal = ref(false)
const formError = ref<{ message: string; requestId?: string; details?: string[] } | null>(null)
const showValidation = ref(false)
const formErrors = ref<Record<string, string>>({})

const summaryData = ref({
  thisMonth: 285000,
  pending: 45000,
  failed: 8500,
  successRate: 94.2,
  pendingCount: 12,
  failedCount: 3
})

const paymentForm = ref({
  customerId: '',
  method: '',
  paymentDate: new Date().toISOString().split('T')[0],
  referenceNumber: '',
  totalAmount: 0,
  notes: ''
})

const paymentSchema = {
  customerId: { required: true, label: 'Customer' },
  method: { required: true, label: 'Payment method' },
  paymentDate: { required: true, label: 'Payment date' },
  totalAmount: {
    label: 'Payment amount',
    custom: (value: number) => (value > 0 ? null : 'Select at least one invoice to pay')
  }
}

const customers = ref([
  { id: 1, name: 'ABC Corporation' },
  { id: 2, name: 'XYZ Retail Store' }
])

const customerInvoices = ref([])

const payments = ref([
  {
    id: 1,
    paymentNumber: 'PAY-2024-001',
    customerName: 'ABC Corporation',
    invoiceNumber: 'INV-2024-001',
    amount: 15000,
    method: 'bank_transfer',
    paymentDate: '2024-01-15',
    status: 'completed'
  },
  {
    id: 2,
    paymentNumber: 'PAY-2024-002',
    customerName: 'XYZ Retail Store',
    invoiceNumber: 'INV-2024-002',
    amount: 8500,
    method: 'credit_card',
    paymentDate: '2024-01-20',
    status: 'pending'
  }
])

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString()
}

const formatMethod = (method: string) => {
  return method.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const formatStatus = (status: string) => {
  return status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const loadCustomerInvoices = () => {
  customerInvoices.value = [
    { id: 1, invoiceNumber: 'INV-001', dueDate: '2024-02-15', balanceDue: 5000, selected: false },
    { id: 2, invoiceNumber: 'INV-002', dueDate: '2024-02-20', balanceDue: 3500, selected: false }
  ]
}

const updatePaymentAmount = () => {
  paymentForm.value.totalAmount = customerInvoices.value
    .filter(invoice => invoice.selected)
    .reduce((sum, invoice) => sum + invoice.balanceDue, 0)
}

const viewPayment = (payment: any) => {
  window.open(`/ar/payments/${payment.id}`, '_blank')
}

const editPayment = (payment: any) => {
  console.log('Edit payment:', payment.paymentNumber)
}

const processPayment = (payment: any) => {
  if (confirm(`Process payment ${payment.paymentNumber}?`)) {
    payment.status = 'completed'
    alert('Payment processed successfully')
  }
}

const savePayment = async () => {
  formError.value = null
  showValidation.value = true
  const validation = validateSchema(paymentForm.value, paymentSchema)
  formErrors.value = validation.errors

  if (!validation.isValid) {
    return
  }

  try {
    const payload = {
      customer_id: paymentForm.value.customerId,
      payment_method: paymentForm.value.method,
      amount: paymentForm.value.totalAmount,
      payment_date: paymentForm.value.paymentDate,
      reference_number: paymentForm.value.referenceNumber,
      invoice_numbers: customerInvoices.value.filter(i => i.selected).map(i => i.invoiceNumber)
    }

    const response = await api.post('/api/v1/ar/payments', payload, { idempotencyKey: true })
    const paymentNumber = response.payment_number || `PAY-${new Date().getFullYear()}-${String(payments.value.length + 1).padStart(3, '0')}`

    const newPayment = {
      id: response.id || Math.max(...payments.value.map(p => p.id)) + 1,
      paymentNumber,
      customerName: customers.value.find(c => c.id == paymentForm.value.customerId)?.name || '',
      invoiceNumber: payload.invoice_numbers.join(', '),
      amount: paymentForm.value.totalAmount,
      method: paymentForm.value.method,
      paymentDate: paymentForm.value.paymentDate,
      status: 'pending'
    }

    payments.value = [newPayment, ...payments.value]
    alert('Payment recorded successfully')
    closeModal()
  } catch (error: any) {
    formError.value = {
      message: error.message || 'Failed to record payment',
      requestId: error.requestId || error.response?.headers?.['x-request-id']
    }
  }
}

const closeModal = () => {
  showCreateModal.value = false
  formError.value = null
  showValidation.value = false
  formErrors.value = {}
  customerInvoices.value = []
  paymentForm.value = {
    customerId: '',
    method: '',
    paymentDate: new Date().toISOString().split('T')[0],
    referenceNumber: '',
    totalAmount: 0,
    notes: ''
  }
}

const bulkProcess = () => {
  alert('Bulk process functionality')
}

// Export functionality
const toast = useToast()
const exportDialog = ref(false)
const isExporting = ref(false)

// Define export columns with proper formatting
const exportColumns = [
  { field: 'paymentNumber', header: 'Payment #', width: '120px' },
  { field: 'customerName', header: 'Customer', width: '180px' },
  { field: 'invoiceNumber', header: 'Invoice #', width: '120px' },
  { field: 'date', header: 'Date', width: '100px', type: 'date' },
  { field: 'method', header: 'Method', width: '120px' },
  { field: 'reference', header: 'Reference', width: '150px' },
  { field: 'amount', header: 'Amount', width: '120px', type: 'currency', format: { symbol: '$', decimal: 2 } },
  { field: 'status', header: 'Status', width: '120px' },
  { field: 'notes', header: 'Notes', width: '200px' }
]

// Prepare data for export
const exportData = computed(() => {
  return payments.value.map(payment => ({
    paymentNumber: payment.paymentNumber,
    customerName: payment.customerName,
    invoiceNumber: payment.invoiceNumber,
    date: payment.date,
    method: formatMethod(payment.method),
    reference: payment.reference || 'N/A',
    amount: payment.amount,
    status: formatStatus(payment.status),
    notes: payment.notes || ''
  }))
})

const exportPayments = () => {
  exportDialog.value = true
}

const handleExport = async (format: string, options: any = {}) => {
  try {
    isExporting.value = true
    
    // Use the useReportExport composable
    const { exportData: exportFn } = useReportExport()
    
    // Prepare export options
    const exportOptions = {
      title: 'AR Payments',
      columns: exportColumns,
      data: exportData.value,
      filename: `ar-payments-${new Date().toISOString().split('T')[0]}`,
      ...options
    }
    
    // Perform the export
    await exportFn(format, exportOptions)
    
    // Show success message
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
</script>

<style>
@import '/src/assets/styles/ar-advanced.css';

.ar-payments-advanced {
  min-height: 100vh;
  background: #f5f7fa;
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
  margin-bottom: 8px;
}

.amount.orange { color: #dd6b20; }
.amount.red { color: #e53e3e; }
.amount.green { color: #38a169; }

.trend {
  font-size: 0.8rem;
  font-weight: 600;
}

.trend.positive { color: #38a169; }
.trend.negative { color: #e53e3e; }

.method-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
}

.method-badge.cash {
  background: #f1f8e9;
  color: #33691e;
}

.method-badge.check {
  background: #e3f2fd;
  color: #1565c0;
}

.method-badge.credit_card {
  background: #f3e5f5;
  color: #7b1fa2;
}

.method-badge.bank_transfer {
  background: #e0f2f1;
  color: #00695c;
}

.method-badge.digital_wallet {
  background: #e8eaf6;
  color: #3f51b5;
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

.input-error {
  border-color: #dc2626;
}

.error-text {
  color: #dc2626;
  font-size: 0.8rem;
  margin-top: 0.35rem;
  display: inline-block;
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

.advanced-modal {
  max-width: 800px;
}
</style>
