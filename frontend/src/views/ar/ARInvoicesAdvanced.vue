<template>
  <div class="ar-invoices-advanced">
    <div class="page-header">
      <div class="container">
        <div class="header-content">
          <div>
            <h1>AR Invoices</h1>
            <p>Advanced invoice management with AI insights</p>
          </div>
          <div class="header-actions">
            <button class="btn btn-outline" @click="bulkSend">Bulk Send</button>
            <button class="btn btn-secondary" @click="exportInvoices">Export</button>
            <button class="btn btn-primary" @click="showCreateModal = true">+ Create Invoice</button>
          </div>
        </div>
      </div>
    </div>

    <div class="container">
      <!-- Summary Cards -->
      <div class="summary-section">
        <div class="summary-grid">
          <div class="summary-card">
            <h3>Total Outstanding</h3>
            <div class="amount">{{ formatCurrency(summaryData.totalOutstanding) }}</div>
            <div class="trend positive">↗ +5.2%</div>
          </div>
          <div class="summary-card">
            <h3>Overdue Amount</h3>
            <div class="amount orange">{{ formatCurrency(summaryData.overdueAmount) }}</div>
            <div class="trend negative">↗ +12.1%</div>
          </div>
          <div class="summary-card">
            <h3>This Month Sales</h3>
            <div class="amount green">{{ formatCurrency(summaryData.thisMonthSales) }}</div>
            <div class="trend positive">↗ +8.5%</div>
          </div>
          <div class="summary-card">
            <h3>Collection Rate</h3>
            <div class="amount blue">{{ summaryData.collectionRate }}%</div>
            <div class="trend positive">↗ +2.3%</div>
          </div>
        </div>
      </div>

      <!-- Invoices Table -->
      <div class="table-card">
        <div class="table-header">
          <h3>Invoices ({{ invoices.length }})</h3>
          <div class="table-actions">
            <button class="btn btn-outline">Export</button>
            <button class="btn btn-outline">Print</button>
          </div>
        </div>
        
        <div class="table-container">
          <table class="invoices-table">
            <thead>
              <tr>
                <th>Invoice #</th>
                <th>Customer</th>
                <th>Date</th>
                <th>Due Date</th>
                <th>Amount</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="invoice in invoices" :key="invoice.id">
                <td class="invoice-number">{{ invoice.invoiceNumber }}</td>
                <td class="customer-name">{{ invoice.customerName }}</td>
                <td>{{ formatDate(invoice.invoiceDate) }}</td>
                <td>{{ formatDate(invoice.dueDate) }}</td>
                <td class="amount">{{ formatCurrency(invoice.totalAmount) }}</td>
                <td>
                  <span class="status-badge" :class="invoice.status">{{ invoice.status }}</span>
                </td>
                <td>
                  <div class="action-buttons">
                    <button class="btn-icon" @click="viewInvoice(invoice)" title="View">👁️</button>
                    <button class="btn-icon" @click="editInvoice(invoice)" title="Edit">✏️</button>
                    <button class="btn-icon" @click="sendInvoice(invoice)" title="Send">📧</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Create/Edit Invoice Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content large-modal" @click.stop>
        <div class="modal-header">
          <h3>{{ editingInvoice ? 'Edit' : 'Create' }} Invoice</h3>
          <button class="modal-close" @click="closeModal">×</button>
        </div>
        
        <div class="modal-tabs">
          <button class="tab-btn" :class="{ active: activeTab === 'basic' }" @click="activeTab = 'basic'">
            Basic Info
          </button>
          <button class="tab-btn" :class="{ active: activeTab === 'items' }" @click="activeTab = 'items'">
            Line Items
          </button>
          <button class="tab-btn" :class="{ active: activeTab === 'totals' }" @click="activeTab = 'totals'">
            Totals & Terms
          </button>
        </div>
        
        <form @submit.prevent="saveInvoice" class="invoice-form">
          <!-- Basic Info Tab -->
          <div v-if="activeTab === 'basic'" class="tab-content">
            <div class="form-grid">
              <div class="form-group">
                <label>Customer *</label>
                <select v-model="invoiceForm.customerId" required class="form-input" @change="loadCustomerInfo">
                  <option value="">Select Customer</option>
                  <option v-for="customer in customers" :key="customer.id" :value="customer.id">
                    {{ customer.name }} ({{ customer.customerId }})
                  </option>
                </select>
              </div>
              <div class="form-group">
                <label>Invoice Number *</label>
                <input type="text" v-model="invoiceForm.invoiceNumber" required class="form-input" placeholder="Auto-generated if empty">
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

            <div class="form-grid">
              <div class="form-group">
                <label>PO Number</label>
                <input type="text" v-model="invoiceForm.poNumber" class="form-input" placeholder="Customer PO Number">
              </div>
              <div class="form-group">
                <label>Currency</label>
                <select v-model="invoiceForm.currency" class="form-input">
                  <option value="USD">USD - US Dollar</option>
                  <option value="PKR">PKR - Pakistani Rupee</option>
                  <option value="SAR">SAR - Saudi Riyal</option>
                  <option value="EUR">EUR - Euro</option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <label>Description</label>
              <textarea v-model="invoiceForm.description" class="form-input" rows="3" placeholder="Invoice description or notes"></textarea>
            </div>

            <!-- Customer Info Display -->
            <div v-if="selectedCustomer" class="customer-info-display">
              <h4>Customer Information</h4>
              <div class="customer-details">
                <div class="detail-row">
                  <span class="label">Name:</span>
                  <span>{{ selectedCustomer.name }}</span>
                </div>
                <div class="detail-row">
                  <span class="label">Contact:</span>
                  <span>{{ selectedCustomer.contactPerson }}</span>
                </div>
                <div class="detail-row">
                  <span class="label">Email:</span>
                  <span>{{ selectedCustomer.email }}</span>
                </div>
                <div class="detail-row">
                  <span class="label">Payment Terms:</span>
                  <span>{{ formatPaymentTerms(selectedCustomer.paymentTerms) }}</span>
                </div>
                <div class="detail-row">
                  <span class="label">Credit Limit:</span>
                  <span>{{ formatCurrency(selectedCustomer.creditLimit) }}</span>
                </div>
                <div class="detail-row">
                  <span class="label">Outstanding:</span>
                  <span class="amount" :class="{ 'high-amount': selectedCustomer.outstanding > selectedCustomer.creditLimit * 0.8 }">
                    {{ formatCurrency(selectedCustomer.outstanding) }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Line Items Tab -->
          <div v-if="activeTab === 'items'" class="tab-content">
            <div class="line-items-section">
              <div class="section-header">
                <h4>Invoice Line Items</h4>
                <button type="button" @click="addLineItem" class="btn btn-outline btn-sm">
                  + Add Line Item
                </button>
              </div>
              
              <div class="line-items-table">
                <table>
                  <thead>
                    <tr>
                      <th style="width: 40%">Description *</th>
                      <th style="width: 10%">Qty *</th>
                      <th style="width: 15%">Unit Price *</th>
                      <th style="width: 10%">Discount</th>
                      <th style="width: 10%">Tax %</th>
                      <th style="width: 15%">Line Total</th>
                      <th style="width: 5%">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(line, index) in invoiceForm.lineItems" :key="index" class="line-item-row">
                      <td>
                        <div class="line-item-description">
                          <input type="text" v-model="line.description" class="form-input" required placeholder="Item description">
                          <input type="text" v-model="line.productCode" class="form-input form-input-sm" placeholder="Product code (optional)">
                        </div>
                      </td>
                      <td>
                        <input type="number" v-model="line.quantity" class="form-input" min="0.01" step="0.01" required @input="calculateLineTotal(index)">
                      </td>
                      <td>
                        <input type="number" v-model="line.unitPrice" class="form-input" min="0" step="0.01" required @input="calculateLineTotal(index)">
                      </td>
                      <td>
                        <input type="number" v-model="line.discountAmount" class="form-input" min="0" step="0.01" @input="calculateLineTotal(index)" placeholder="0.00">
                      </td>
                      <td>
                        <input type="number" v-model="line.taxRate" class="form-input" min="0" max="100" step="0.01" @input="calculateLineTotal(index)" placeholder="0">
                      </td>
                      <td class="line-total">
                        <span class="total-amount">{{ formatCurrency(line.lineTotal || 0) }}</span>
                      </td>
                      <td>
                        <button type="button" @click="removeLineItem(index)" class="btn-icon btn-danger" :disabled="invoiceForm.lineItems.length === 1">
                          🗑️
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              
              <div class="line-items-summary">
                <div class="summary-row">
                  <span>Subtotal ({{ invoiceForm.lineItems.length }} items):</span>
                  <span class="amount">{{ formatCurrency(calculateSubtotal()) }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Totals & Terms Tab -->
          <div v-if="activeTab === 'totals'" class="tab-content">
            <div class="totals-section">
              <h4>Invoice Totals</h4>
              
              <div class="totals-grid">
                <div class="totals-left">
                  <div class="form-group">
                    <label>Additional Discount</label>
                    <input type="number" v-model="invoiceForm.additionalDiscount" class="form-input" min="0" step="0.01" @input="calculateTotals">
                  </div>
                  
                  <div class="form-group">
                    <label>Shipping & Handling</label>
                    <input type="number" v-model="invoiceForm.shippingAmount" class="form-input" min="0" step="0.01" @input="calculateTotals">
                  </div>
                  
                  <div class="form-group">
                    <label>Additional Tax</label>
                    <input type="number" v-model="invoiceForm.additionalTax" class="form-input" min="0" step="0.01" @input="calculateTotals">
                  </div>
                  
                  <div class="form-group">
                    <label>Payment Terms</label>
                    <select v-model="invoiceForm.paymentTerms" class="form-input">
                      <option value="net15">Net 15 Days</option>
                      <option value="net30">Net 30 Days</option>
                      <option value="net45">Net 45 Days</option>
                      <option value="net60">Net 60 Days</option>
                      <option value="due_on_receipt">Due on Receipt</option>
                      <option value="cod">Cash on Delivery</option>
                    </select>
                  </div>
                </div>
                
                <div class="totals-right">
                  <div class="invoice-totals-display">
                    <div class="total-row">
                      <span>Subtotal:</span>
                      <span>{{ formatCurrency(calculateSubtotal()) }}</span>
                    </div>
                    <div class="total-row" v-if="invoiceForm.additionalDiscount > 0">
                      <span>Additional Discount:</span>
                      <span class="discount">-{{ formatCurrency(invoiceForm.additionalDiscount) }}</span>
                    </div>
                    <div class="total-row" v-if="invoiceForm.shippingAmount > 0">
                      <span>Shipping & Handling:</span>
                      <span>{{ formatCurrency(invoiceForm.shippingAmount) }}</span>
                    </div>
                    <div class="total-row">
                      <span>Tax Total:</span>
                      <span>{{ formatCurrency(calculateTaxTotal()) }}</span>
                    </div>
                    <div class="total-row total-final">
                      <span>Total Amount:</span>
                      <span class="final-amount">{{ formatCurrency(calculateFinalTotal()) }}</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="form-group">
                <label>Terms & Conditions</label>
                <textarea v-model="invoiceForm.terms" class="form-input" rows="4" placeholder="Enter payment terms, conditions, or additional notes..."></textarea>
              </div>
            </div>
          </div>

          <div class="form-actions">
            <button type="button" @click="closeModal" class="btn btn-secondary">Cancel</button>
            <button type="button" @click="saveDraft" class="btn btn-outline">Save as Draft</button>
            <button type="submit" class="btn btn-primary">{{ editingInvoice ? 'Update' : 'Create' }} Invoice</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const showCreateModal = ref(false)
const editingInvoice = ref(null)
const activeTab = ref('basic')
const selectedCustomer = ref(null)

const summaryData = ref({
  totalOutstanding: 485000,
  overdueAmount: 125000,
  thisMonthSales: 350000,
  collectionRate: 87.5
})

const invoiceForm = ref({
  customerId: '',
  invoiceNumber: '',
  invoiceDate: new Date().toISOString().split('T')[0],
  dueDate: '',
  description: '',
  poNumber: '',
  currency: 'USD',
  paymentTerms: 'net30',
  additionalDiscount: 0,
  shippingAmount: 0,
  additionalTax: 0,
  terms: '',
  lineItems: [
    {
      description: '',
      productCode: '',
      quantity: 1,
      unitPrice: 0,
      discountAmount: 0,
      taxRate: 0,
      lineTotal: 0
    }
  ]
})

const customers = ref([
  { 
    id: 1, 
    name: 'ABC Corporation',
    customerId: 'C001',
    contactPerson: 'John Smith',
    email: 'john@abccorp.com',
    paymentTerms: 'net30',
    creditLimit: 50000,
    outstanding: 25000
  },
  { 
    id: 2, 
    name: 'XYZ Retail Store',
    customerId: 'C002',
    contactPerson: 'Sarah Johnson',
    email: 'sarah@xyzretail.com',
    paymentTerms: 'net15',
    creditLimit: 30000,
    outstanding: 12000
  },
  { 
    id: 3, 
    name: 'Tech Solutions Inc.',
    customerId: 'C003',
    contactPerson: 'Mike Wilson',
    email: 'mike@techsolutions.com',
    paymentTerms: 'net45',
    creditLimit: 75000,
    outstanding: 8500
  }
])

const invoices = ref([
  {
    id: 1,
    invoiceNumber: 'INV-2024-001',
    customerName: 'ABC Corporation',
    invoiceDate: '2024-01-15',
    dueDate: '2024-02-14',
    totalAmount: 15000,
    status: 'sent'
  },
  {
    id: 2,
    invoiceNumber: 'INV-2024-002',
    customerName: 'XYZ Retail Store',
    invoiceDate: '2024-01-20',
    dueDate: '2024-02-19',
    totalAmount: 8500,
    status: 'overdue'
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

const viewInvoice = (invoice: any) => {
  window.open(`/ar/invoices/${invoice.id}`, '_blank')
}

const editInvoice = (invoice: any) => {
  editingInvoice.value = invoice
  
  // Populate form with invoice data
  const customer = customers.value.find(c => c.name === invoice.customerName)
  
  invoiceForm.value = {
    customerId: customer?.id || '',
    invoiceNumber: invoice.invoiceNumber,
    invoiceDate: invoice.invoiceDate,
    dueDate: invoice.dueDate,
    description: invoice.description || '',
    poNumber: invoice.poNumber || '',
    currency: invoice.currency || 'USD',
    paymentTerms: invoice.paymentTerms || 'net30',
    additionalDiscount: invoice.discountAmount || 0,
    shippingAmount: invoice.shippingAmount || 0,
    additionalTax: 0,
    terms: invoice.terms || '',
    lineItems: invoice.lineItems || [
      {
        description: invoice.description || 'Service',
        productCode: '',
        quantity: 1,
        unitPrice: invoice.totalAmount || 0,
        discountAmount: 0,
        taxRate: 0,
        lineTotal: invoice.totalAmount || 0
      }
    ]
  }
  
  if (customer) {
    selectedCustomer.value = customer
  }
  
  activeTab.value = 'basic'
  showCreateModal.value = true
}

const sendInvoice = (invoice: any) => {
  if (confirm(`Send invoice ${invoice.invoiceNumber}?`)) {
    invoice.status = 'sent'
    alert('Invoice sent successfully')
  }
}

const loadCustomerInfo = () => {
  if (invoiceForm.value.customerId) {
    selectedCustomer.value = customers.value.find(c => c.id == invoiceForm.value.customerId)
    
    // Auto-calculate due date based on payment terms
    if (selectedCustomer.value) {
      const invoiceDate = new Date(invoiceForm.value.invoiceDate)
      let daysToAdd = 30 // default
      
      switch (selectedCustomer.value.paymentTerms) {
        case 'net15': daysToAdd = 15; break
        case 'net30': daysToAdd = 30; break
        case 'net45': daysToAdd = 45; break
        case 'net60': daysToAdd = 60; break
        case 'due_on_receipt': daysToAdd = 0; break
        default: daysToAdd = 30
      }
      
      const dueDate = new Date(invoiceDate)
      dueDate.setDate(dueDate.getDate() + daysToAdd)
      invoiceForm.value.dueDate = dueDate.toISOString().split('T')[0]
      invoiceForm.value.paymentTerms = selectedCustomer.value.paymentTerms
    }
  } else {
    selectedCustomer.value = null
  }
}

const addLineItem = () => {
  invoiceForm.value.lineItems.push({
    description: '',
    productCode: '',
    quantity: 1,
    unitPrice: 0,
    discountAmount: 0,
    taxRate: 0,
    lineTotal: 0
  })
}

const removeLineItem = (index) => {
  if (invoiceForm.value.lineItems.length > 1) {
    invoiceForm.value.lineItems.splice(index, 1)
  }
}

const calculateLineTotal = (index) => {
  const line = invoiceForm.value.lineItems[index]
  const subtotal = (line.quantity || 0) * (line.unitPrice || 0)
  const afterDiscount = subtotal - (line.discountAmount || 0)
  const taxAmount = afterDiscount * ((line.taxRate || 0) / 100)
  line.lineTotal = afterDiscount + taxAmount
}

const calculateSubtotal = () => {
  return invoiceForm.value.lineItems.reduce((sum, line) => {
    const subtotal = (line.quantity || 0) * (line.unitPrice || 0)
    return sum + subtotal - (line.discountAmount || 0)
  }, 0)
}

const calculateTaxTotal = () => {
  const lineTax = invoiceForm.value.lineItems.reduce((sum, line) => {
    const subtotal = (line.quantity || 0) * (line.unitPrice || 0) - (line.discountAmount || 0)
    return sum + (subtotal * ((line.taxRate || 0) / 100))
  }, 0)
  return lineTax + (invoiceForm.value.additionalTax || 0)
}

const calculateFinalTotal = () => {
  const subtotal = calculateSubtotal()
  const taxTotal = calculateTaxTotal()
  const shipping = invoiceForm.value.shippingAmount || 0
  const additionalDiscount = invoiceForm.value.additionalDiscount || 0
  return subtotal + taxTotal + shipping - additionalDiscount
}

const calculateTotals = () => {
  // Recalculate all line totals
  invoiceForm.value.lineItems.forEach((_, index) => {
    calculateLineTotal(index)
  })
}

const formatPaymentTerms = (terms) => {
  const termMap = {
    'net15': 'Net 15 Days',
    'net30': 'Net 30 Days',
    'net45': 'Net 45 Days',
    'net60': 'Net 60 Days',
    'due_on_receipt': 'Due on Receipt',
    'cod': 'Cash on Delivery'
  }
  return termMap[terms] || terms
}

const saveDraft = () => {
  if (!invoiceForm.value.customerId) {
    alert('Please select a customer')
    return
  }
  
  saveInvoiceWithStatus('draft')
}

const saveInvoice = () => {
  if (!invoiceForm.value.customerId) {
    alert('Please select a customer')
    return
  }
  
  if (invoiceForm.value.lineItems.length === 0 || !invoiceForm.value.lineItems[0].description) {
    alert('Please add at least one line item')
    return
  }
  
  saveInvoiceWithStatus('sent')
}

const saveInvoiceWithStatus = (status) => {
  // Generate invoice number if not provided
  if (!invoiceForm.value.invoiceNumber) {
    const year = new Date().getFullYear()
    const nextNumber = invoices.value.length + 1
    invoiceForm.value.invoiceNumber = `INV-${year}-${String(nextNumber).padStart(6, '0')}`
  }
  
  const customer = customers.value.find(c => c.id == invoiceForm.value.customerId)
  const totalAmount = calculateFinalTotal()
  
  const newInvoice = {
    id: editingInvoice.value ? editingInvoice.value.id : Math.max(...invoices.value.map(i => i.id)) + 1,
    invoiceNumber: invoiceForm.value.invoiceNumber,
    customerName: customer?.name || '',
    invoiceDate: invoiceForm.value.invoiceDate,
    dueDate: invoiceForm.value.dueDate,
    totalAmount: totalAmount,
    status: status,
    description: invoiceForm.value.description,
    poNumber: invoiceForm.value.poNumber,
    currency: invoiceForm.value.currency,
    lineItems: [...invoiceForm.value.lineItems],
    subtotal: calculateSubtotal(),
    taxAmount: calculateTaxTotal(),
    shippingAmount: invoiceForm.value.shippingAmount || 0,
    discountAmount: invoiceForm.value.additionalDiscount || 0
  }
  
  if (editingInvoice.value) {
    const index = invoices.value.findIndex(i => i.id === editingInvoice.value.id)
    if (index > -1) {
      invoices.value[index] = newInvoice
    }
    alert('Invoice updated successfully')
  } else {
    invoices.value.push(newInvoice)
    alert(`Invoice ${status === 'draft' ? 'saved as draft' : 'created'} successfully`)
  }
  
  closeModal()
}

const closeModal = () => {
  showCreateModal.value = false
  editingInvoice.value = null
  selectedCustomer.value = null
  activeTab.value = 'basic'
  
  invoiceForm.value = {
    customerId: '',
    invoiceNumber: '',
    invoiceDate: new Date().toISOString().split('T')[0],
    dueDate: '',
    description: '',
    poNumber: '',
    currency: 'USD',
    paymentTerms: 'net30',
    additionalDiscount: 0,
    shippingAmount: 0,
    additionalTax: 0,
    terms: '',
    lineItems: [
      {
        description: '',
        productCode: '',
        quantity: 1,
        unitPrice: 0,
        discountAmount: 0,
        taxRate: 0,
        lineTotal: 0
      }
    ]
  }
}

const bulkSend = () => {
  alert('Bulk send functionality')
}

const exportInvoices = () => {
  alert('Export functionality')
}
</script>

<style>
@import '/src/assets/styles/ar-advanced.css';
</style>