<template>
  <div class="ar-invoices-advanced">
    <!-- Export Dialog -->
    <ExportDialog
      v-model:visible="showExportDialog"
      title="Export AR Invoices"
      :file-name="exportFileName"
      :columns="exportColumns"
      :data="exportData"
      :meta="{
        title: 'AR Invoices Report',
        description: 'List of accounts receivable invoices',
        generatedOn: new Date().toLocaleString(),
        generatedBy: 'System',
        includeSummary: true,
        filters: {
          status: selectedStatus || 'All',
          customer: searchQuery || 'All',
          dateRange: 'All dates'
        }
      }"
      @export="handleExport"
    />
    
    <div class="page-header">
      <div class="container">
        <div class="header-content">
          <div>
            <h1>AR Invoices</h1>
            <p>Advanced invoice management with AI insights</p>
          </div>
          <div class="header-actions" style="display: flex; gap: 0.5rem;">
            <Button 
              label="Bulk Send" 
              icon="pi pi-send" 
              @click="bulkSend" 
              class="p-button-outlined"
            />
            <Button 
              label="Export" 
              icon="pi pi-download" 
              @click="showExportDialog = true"
              class="p-button-outlined"
              :loading="exportInProgress"
              :disabled="!invoices.length"
              v-tooltip="invoices.length ? 'Export AR invoices' : 'No data to export'"
            />
            <Button 
              label="Create Invoice" 
              icon="pi pi-plus" 
              @click="showCreateModal = true"
              class="p-button-primary"
            />
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
import { ref, computed } from 'vue'
import { useToast } from 'primevue/usetoast'
import ExportDialog from '@/components/common/ExportDialog.vue'

// ...

const showExportDialog = ref(false)
const exportInProgress = ref(false)

// Export configuration
const exportColumns = [
  { field: 'invoiceNumber', header: 'Invoice #' },
  { field: 'customerName', header: 'Customer' },
  { field: 'invoiceDate', header: 'Date', format: (val) => formatDate(val) },
  { field: 'dueDate', header: 'Due Date', format: (val) => formatDate(val) },
  { field: 'totalAmount', header: 'Amount', format: (val) => formatCurrency(val) },
  { field: 'status', header: 'Status' },
  { field: 'reference', header: 'Reference' }
]

const exportFileName = computed(() => {
  return `AR-Invoices-${new Date().toISOString().split('T')[0]}`
})

const exportData = computed(() => {
  return invoices.value.map(invoice => ({
    ...invoice,
    customerName: invoice.customer?.name || 'N/A',
    totalAmount: invoice.total || 0
  }))
})

// Handle export
const handleExport = async ({ format, options }) => {
  exportInProgress.value = true
  try {
    // Simulate API call for export
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // In a real app, this would call an API endpoint to generate the export
    console.log(`Exporting ${exportData.value.length} invoices as ${format}`, options)
    
    // Show success message
    useToast().add({
      severity: 'success',
      summary: 'Export Successful',
      detail: `Exported ${exportData.value.length} invoices as ${format.toUpperCase()}`,
      life: 3000
    })
  } catch (error) {
    console.error('Export failed:', error)
    useToast().add({
      severity: 'error',
      summary: 'Export Failed',
      detail: 'Failed to export invoices. Please try again.',
      life: 5000
    })
  } finally {
    exportInProgress.value = false
    showExportDialog.value = false
  }
}

const exportInvoices = () => {
  showExportDialog.value = true
}
</script>

<style>
@import '/src/assets/styles/ar-advanced.css';
</style>