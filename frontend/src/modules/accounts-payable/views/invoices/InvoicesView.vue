<template>
  <div class="ap-invoices">
    <div class="page-header">
      <div class="container">
        <div class="header-content">
          <div>
            <h1>AP Invoices</h1>
            <p>Manage accounts payable invoices and payments</p>
          </div>
          <div class="flex gap-2">
            <Button 
              icon="pi pi-download" 
              label="Export" 
              @click="showExportDialog = true"
              class="p-button-outlined"
              :loading="exportInProgress"
              :disabled="!filteredInvoices.length"
v-tooltip.top="{ value: filteredInvoices.length ? 'Export AP invoices' : 'No data to export', showDelay: 500 }"
            />
            <Button 
              label="Create Bill" 
              icon="pi pi-plus" 
              @click="showCreateModal = true"
              class="p-button-primary"
            />
          </div>
        </div>
      </div>
    </div>

    <div class="container">
      <!-- Export Dialog -->
      <Dialog 
        v-model:visible="showExportDialog" 
        header="Export AP Invoices"
        :modal="true"
        class="p-fluid"
        :style="{ width: '50vw' }"
      >
        <div class="field">
          <label for="exportFormat">Format</label>
          <Dropdown 
            v-model="exportFormat" 
            :options="['CSV', 'XLSX', 'PDF']" 
            optionLabel=""
            placeholder="Select Format"
            class="w-full"
          />
        </div>
        <template #footer>
          <Button 
            label="Cancel" 
            icon="pi pi-times" 
            @click="showExportDialog = false" 
            class="p-button-text"
          />
          <Button 
            label="Export" 
            icon="pi pi-download" 
            @click="handleExport({ format: exportFormat, data: exportData })" 
            class="p-button-primary"
            :loading="exportInProgress"
          />
        </template>
      </Dialog>

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
          <h3>{{ editingInvoice ? 'Edit' : 'Create' }} Bill</h3>
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
            <button type="submit" class="btn btn-primary">Save Bill</button>
          </div>
        </form>
      </div>
    </div>
  </div>
  
  <!-- Removed duplicate ExportDialog component since we're using PrimeVue Dialog -->
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import vendorService from '@/services/vendorService'
import { useAuthStore } from '@/stores/auth'

// Types
interface Vendor {
  id: string
  name: string
  email?: string
}

interface InvoiceLine {
  id?: number | string
  description: string
  quantity: number
  unitPrice: number
  amount: number
  taxRate?: number
  accountId?: string
}

interface Invoice {
  id: number
  invoiceNumber: string
  vendorId: string
  vendorName: string
  invoiceDate: string
  dueDate: string
  status: 'draft' | 'pending' | 'approved' | 'paid' | 'overdue' | 'void'
  reference?: string
  description?: string
  amount: number
  totalAmount?: number
  taxAmount: number
  lines: InvoiceLine[]
  createdAt?: string
  updatedAt?: string
}

// Removed unused ExportOptions interface

// State
const toast = useToast()
const authStore = useAuthStore()
const currentCompany = computed(() => authStore.currentCompany)
const showExportDialog = ref(false)
const showCreateModal = ref(false)
const exportInProgress = ref(false)
const searchQuery = ref('')
const selectedStatus = ref('')
const selectedVendor = ref('')
const dateFilter = ref('')
const editingInvoice = ref<Invoice | null>(null)
const exportFormat = ref('CSV')

// Data from API
const vendors = ref<Vendor[]>([])
const invoices = ref<Invoice[]>([])
const loading = ref(false)

// Load data from API
const loadVendors = async () => {
  try {
    const response = await vendorService.getVendors(currentCompany.value?.id || '')
    vendors.value = response.data.map(v => ({ id: v.id, name: v.name, email: v.email }))
  } catch (error) {
    console.error('Error loading vendors:', error)
  }
}

const loadInvoices = async () => {
  loading.value = true
  try {
    // Replace with actual invoice service call
    // const response = await invoiceService.getInvoices(currentCompany.value?.id || '')
    // invoices.value = response.data
    invoices.value = [] // Placeholder until invoice service is implemented
  } catch (error) {
    console.error('Error loading invoices:', error)
  } finally {
    loading.value = false
  }
}

// Filtered invoices - removed duplicate declaration

const exportFileName = computed(() => {
  return `ap-invoices-${new Date().toISOString().slice(0, 10)}`
})

const exportData = computed(() => {
  return filteredInvoices.value.map(invoice => ({
    'Invoice #': invoice.invoiceNumber,
    'Vendor': invoice.vendorName || '',
    'Date': formatDate(invoice.invoiceDate),
    'Due Date': formatDate(invoice.dueDate),
    'Amount': formatCurrency(invoice.totalAmount),
    'Status': invoice.status,
    'Reference': invoice.reference || ''
  }))
})

// Handle export
const handleExport = async ({ format, data }: { format: string; data: any[] }) => {
  try {
    exportInProgress.value = true
    
    // This would be replaced with actual export logic
    console.log(`Exporting ${data.length} invoices as ${format}`)
    
    // Simulate export delay
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    toast.add({
      severity: 'success',
      summary: 'Export Complete',
      detail: `Exported ${data.length} invoices to ${format}`,
      life: 3000
    })
    
    showExportDialog.value = false
  } catch (error) {
    console.error('Export failed:', error)
    toast.add({
      severity: 'error',
      summary: 'Export Failed',
      detail: 'Failed to export invoices. Please try again.',
      life: 3000
    })
  } finally {
    exportInProgress.value = false
  }
}
const summaryData = ref({
  totalOutstanding: 48500,
  overdueAmount: 12000,
  thisMonth: 25000,
  pendingApproval: 8500
})

interface InvoiceForm {
  vendorId: string
  invoiceNumber: string
  invoiceDate: string
  dueDate: string
  description: string
  reference: string
  taxAmount: number
  lines: Array<{
    id: number | string
    description: string
    quantity: number
    unitPrice: number
    amount: number
  }>
}

const invoiceForm = ref<Omit<InvoiceForm, 'lines'> & { lines: Array<Omit<InvoiceLine, 'id'> & { id?: number | string }> }>({
  vendorId: '',
  invoiceNumber: '',
  invoiceDate: new Date().toISOString().split('T')[0],
  dueDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
  description: '',
  reference: '',
  taxAmount: 0,
  lines: [
    { 
      id: Date.now(), 
      description: '', 
      quantity: 1, 
      unitPrice: 0, 
      amount: 0,
      taxRate: 0,
      accountId: ''
    }
  ]
})

// Filter invoices based on search query, status, and vendor
// Filter invoices based on search query, status, and vendor
const filteredInvoices = computed<Invoice[]>(() => {
  return invoices.value.filter(invoice => {
    // Filter by search query
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      const matchesNumber = invoice.invoiceNumber.toLowerCase().includes(query)
      const matchesVendor = invoice.vendorName.toLowerCase().includes(query)
      const matchesReference = invoice.reference?.toLowerCase().includes(query) || false
      
      if (!matchesNumber && !matchesVendor && !matchesReference) {
        return false
      }
    }
    
    // Filter by status
    if (selectedStatus.value && invoice.status !== selectedStatus.value) {
      return false
    }
    
    // Filter by vendor
    if (selectedVendor.value && invoice.vendorId !== selectedVendor.value) {
      return false
    }
    
    return true
  })
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
  const newLine: InvoiceLine = {
    id: Date.now(),
    description: '',
    quantity: 1,
    unitPrice: 0,
    amount: 0
  }
  invoiceForm.value.lines.push(newLine)
}

const removeLine = (index: number) => {
  if (invoiceForm.value.lines.length > 1) {
    invoiceForm.value.lines.splice(index, 1)
  }
}

const viewInvoice = (invoice: Invoice) => {
  window.open(`/ap/invoices/${invoice.id}`, '_blank')
}

const editInvoice = (invoice: Invoice) => {
  editingInvoice.value = { ...invoice }
  invoiceForm.value = {
    vendorId: invoice.vendorId,
    invoiceNumber: invoice.invoiceNumber,
    invoiceDate: invoice.invoiceDate,
    dueDate: invoice.dueDate,
    description: invoice.description || '',
    reference: invoice.reference || '',
    taxAmount: invoice.taxAmount,
    lines: invoice.lines.map(line => ({
      ...line,
      id: line.id || Date.now()
    }))
  }
  showCreateModal.value = true
}

const approveInvoice = (invoice: Invoice) => {
  if (confirm(`Approve invoice ${invoice.invoiceNumber}?`)) {
    invoice.status = 'approved'
    alert('Bill approved successfully')
  }
}

const payInvoice = (invoice: any) => {
  if (confirm(`Mark invoice ${invoice.invoiceNumber} as paid?`)) {
    invoice.status = 'paid'
    alert('Invoice marked as paid')
  }
}

const saveInvoice = () => {
  if (!invoiceForm.value.vendorId || !invoiceForm.value.invoiceNumber || !invoiceForm.value.invoiceDate || !invoiceForm.value.dueDate) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Please fill in all required fields', life: 3000 })
    return
  }

  // Calculate line amounts if not set
  const lines = invoiceForm.value.lines.map(line => ({
    ...line,
    amount: line.quantity * line.unitPrice,
    taxRate: line.taxRate || 0,
    accountId: line.accountId || ''
  }))

  const subtotal = lines.reduce((sum, line) => sum + line.amount, 0)
  const taxAmount = invoiceForm.value.taxAmount || 0
  const total = subtotal + taxAmount

  const invoiceData: Invoice = {
    id: editingInvoice.value?.id || Date.now(),
    invoiceNumber: invoiceForm.value.invoiceNumber,
    vendorId: invoiceForm.value.vendorId,
    vendorName: vendors.value.find(v => v.id === invoiceForm.value.vendorId)?.name || '',
    invoiceDate: invoiceForm.value.invoiceDate,
    dueDate: invoiceForm.value.dueDate,
    description: invoiceForm.value.description || '',
    reference: invoiceForm.value.reference || '',
    amount: total,
    taxAmount,
    status: editingInvoice.value?.status || 'pending',
    lines,
    createdAt: editingInvoice.value?.createdAt || new Date().toISOString(),
    updatedAt: new Date().toISOString()
  }

  if (editingInvoice.value) {
    // Update existing invoice
    const index = invoices.value.findIndex(i => i.id === editingInvoice.value?.id)
    if (index !== -1) {
      invoices.value[index] = invoiceData
      toast.add({ severity: 'success', summary: 'Success', detail: 'Invoice updated successfully', life: 3000 })
    }
  } else {
    // Add new invoice
    invoices.value.push(invoiceData)
    toast.add({ severity: 'success', summary: 'Success', detail: 'Invoice created successfully', life: 3000 })
  }

  // Reset form and close modal
  closeModal()
  toast.add({
    severity: 'success',
    summary: 'Success',
    detail: `Invoice ${editingInvoice.value ? 'updated' : 'created'} successfully`,
    life: 3000
  })
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
    reference: '',
    taxAmount: 0,
    lines: [{ description: '', quantity: 1, unitPrice: 0, amount: 0 }]
  }
}

// Lifecycle
onMounted(async () => {
  await loadVendors()
  await loadInvoices()
})
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