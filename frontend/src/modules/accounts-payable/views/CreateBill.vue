<template>
  <div class="create-bill">
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <Button icon="pi pi-arrow-left" class="p-button-text" @click="$router.go(-1)" />
          <div>
            <h1>Create New Bill</h1>
            <p class="subtitle">Record a new vendor bill for payment processing</p>
          </div>
        </div>
        <div class="header-actions">
          <Button label="Save as Draft" icon="pi pi-save" class="p-button-outlined" @click="saveDraft" />
          <Button label="Create Bill" icon="pi pi-check" :loading="loading" @click="handleSubmit" />
        </div>
      </div>
    </div>

    <div class="form-container">
      <div class="form-grid">
        <!-- Vendor Information -->
        <Card class="vendor-section">
          <template #title>
            <div class="section-title">
              <i class="pi pi-building"></i>
              Vendor Information
            </div>
          </template>
          <template #content>
            <div class="p-fluid">
              <div class="field">
                <label for="vendor" class="required">Vendor *</label>
                <div class="vendor-input-group">
                  <Dropdown 
                    id="vendor"
                    v-model="form.vendorId" 
                    :options="vendors" 
                    optionLabel="name" 
                    optionValue="id"
                    placeholder="Select or search vendor"
                    :filter="true"
                    filterPlaceholder="Search vendors..."
                    :class="{ 'p-invalid': errors.vendorId }"
                    @change="onVendorChange"
                  />
                  <Button icon="pi pi-plus" class="p-button-outlined" @click="showAddVendor = true" v-tooltip="'Add New Vendor'" />
                </div>
                <small v-if="errors.vendorId" class="p-error">{{ errors.vendorId }}</small>
              </div>

              <div v-if="selectedVendor" class="vendor-details">
                <div class="vendor-info">
                  <div class="info-item">
                    <span class="label">Contact:</span>
                    <span>{{ selectedVendor.contact }}</span>
                  </div>
                  <div class="info-item">
                    <span class="label">Payment Terms:</span>
                    <span>{{ selectedVendor.paymentTerms }}</span>
                  </div>
                  <div class="info-item">
                    <span class="label">Tax ID:</span>
                    <span>{{ selectedVendor.taxId }}</span>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </Card>

        <!-- Bill Details -->
        <Card class="bill-section">
          <template #title>
            <div class="section-title">
              <i class="pi pi-file-text"></i>
              Bill Details
            </div>
          </template>
          <template #content>
            <div class="p-fluid">
              <div class="field-group">
                <div class="field">
                  <label for="billNumber" class="required">Bill Number *</label>
                  <InputText 
                    id="billNumber"
                    v-model="form.billNumber" 
                    placeholder="Enter bill/invoice number"
                    :class="{ 'p-invalid': errors.billNumber }"
                  />
                  <small v-if="errors.billNumber" class="p-error">{{ errors.billNumber }}</small>
                </div>

                <div class="field">
                  <label for="billDate">Bill Date</label>
                  <Calendar 
                    id="billDate"
                    v-model="form.billDate" 
                    dateFormat="mm/dd/yy"
                    :showIcon="true"
                  />
                </div>
              </div>

              <div class="field-group">
                <div class="field">
                  <label for="dueDate" class="required">Due Date *</label>
                  <Calendar 
                    id="dueDate"
                    v-model="form.dueDate" 
                    dateFormat="mm/dd/yy"
                    :showIcon="true"
                    :class="{ 'p-invalid': errors.dueDate }"
                  />
                  <small v-if="errors.dueDate" class="p-error">{{ errors.dueDate }}</small>
                </div>

                <div class="field">
                  <label for="category">Category</label>
                  <Dropdown 
                    id="category"
                    v-model="form.category" 
                    :options="categories" 
                    optionLabel="name" 
                    optionValue="id"
                    placeholder="Select category"
                  />
                </div>
              </div>

              <div class="field">
                <label for="description">Description</label>
                <Textarea 
                  id="description"
                  v-model="form.description" 
                  rows="3"
                  placeholder="Enter bill description or notes"
                />
              </div>
            </div>
          </template>
        </Card>

        <!-- Amount & Tax Information -->
        <Card class="amount-section">
          <template #title>
            <div class="section-title">
              <i class="pi pi-dollar"></i>
              Amount & Tax
            </div>
          </template>
          <template #content>
            <div class="p-fluid">
              <div class="field">
                <label for="subtotal" class="required">Subtotal *</label>
                <InputNumber 
                  id="subtotal"
                  v-model="form.subtotal" 
                  mode="currency" 
                  currency="USD"
                  :class="{ 'p-invalid': errors.subtotal }"
                  @input="calculateTotal"
                />
                <small v-if="errors.subtotal" class="p-error">{{ errors.subtotal }}</small>
              </div>

              <div class="tax-section">
                <div class="field">
                  <div class="tax-header">
                    <label>Tax</label>
                    <Checkbox v-model="form.taxable" inputId="taxable" @change="calculateTotal" />
                    <label for="taxable" class="checkbox-label">Taxable</label>
                  </div>
                  <div v-if="form.taxable" class="tax-inputs">
                    <div class="field-group">
                      <InputNumber 
                        v-model="form.taxRate" 
                        mode="decimal" 
                        :minFractionDigits="2"
                        :maxFractionDigits="4"
                        suffix="%"
                        placeholder="Tax Rate"
                        @input="calculateTotal"
                      />
                      <InputNumber 
                        v-model="form.taxAmount" 
                        mode="currency" 
                        currency="USD"
                        placeholder="Tax Amount"
                        :disabled="true"
                      />
                    </div>
                  </div>
                </div>
              </div>

              <Divider />

              <div class="total-section">
                <div class="total-row">
                  <span class="total-label">Total Amount</span>
                  <span class="total-amount">${{ formatCurrency(form.totalAmount) }}</span>
                </div>
              </div>
            </div>
          </template>
        </Card>

        <!-- Attachments -->
        <Card class="attachments-section">
          <template #title>
            <div class="section-title">
              <i class="pi pi-paperclip"></i>
              Attachments
            </div>
          </template>
          <template #content>
            <FileUpload 
              mode="advanced" 
              :multiple="true"
              accept="image/*,.pdf,.doc,.docx,.xls,.xlsx"
              :maxFileSize="5000000"
              @upload="onUpload"
              :auto="false"
              chooseLabel="Choose Files"
              uploadLabel="Upload"
              cancelLabel="Clear"
            >
              <template #empty>
                <p>Drag and drop files here or click to browse.</p>
                <small>Supported formats: PDF, DOC, XLS, Images (Max 5MB each)</small>
              </template>
            </FileUpload>
          </template>
        </Card>
      </div>
    </div>

    <!-- Add Vendor Dialog -->
    <Dialog v-model:visible="showAddVendor" modal header="Add New Vendor" :style="{width: '500px'}">
      <div class="p-fluid">
        <div class="field">
          <label for="newVendorName">Vendor Name</label>
          <InputText id="newVendorName" v-model="newVendor.name" />
        </div>
        <div class="field">
          <label for="newVendorContact">Contact</label>
          <InputText id="newVendorContact" v-model="newVendor.contact" />
        </div>
      </div>
      <template #footer>
        <Button label="Cancel" class="p-button-text" @click="showAddVendor = false" />
        <Button label="Add Vendor" @click="addNewVendor" />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'

const router = useRouter()
const toast = useToast()
const loading = ref(false)
const showAddVendor = ref(false)

const form = reactive({
  vendorId: null,
  billNumber: '',
  billDate: new Date(),
  dueDate: null,
  category: null,
  description: '',
  subtotal: null,
  taxable: false,
  taxRate: 8.25,
  taxAmount: 0,
  totalAmount: 0
})

const errors = reactive({
  vendorId: '',
  billNumber: '',
  subtotal: '',
  dueDate: ''
})

const newVendor = reactive({
  name: '',
  contact: ''
})

const vendors = ref([
  { id: 1, name: 'ABC Supplies Co.', contact: 'John Smith', paymentTerms: 'Net 30', taxId: '12-3456789' },
  { id: 2, name: 'XYZ Services Ltd.', contact: 'Jane Doe', paymentTerms: 'Net 15', taxId: '98-7654321' },
  { id: 3, name: 'Tech Solutions Inc.', contact: 'Mike Johnson', paymentTerms: 'Net 45', taxId: '55-1234567' },
  { id: 4, name: 'Office Depot', contact: 'Sarah Wilson', paymentTerms: 'Net 30', taxId: '77-9876543' },
  { id: 5, name: 'Utility Company', contact: 'David Brown', paymentTerms: 'Due on Receipt', taxId: '33-5678901' }
])

const categories = ref([
  { id: 1, name: 'Office Supplies' },
  { id: 2, name: 'Utilities' },
  { id: 3, name: 'Professional Services' },
  { id: 4, name: 'Equipment' },
  { id: 5, name: 'Travel & Entertainment' },
  { id: 6, name: 'Marketing' },
  { id: 7, name: 'Insurance' },
  { id: 8, name: 'Rent' }
])

const selectedVendor = computed(() => {
  return vendors.value.find(v => v.id === form.vendorId)
})

const formatCurrency = (amount: number) => {
  return (amount || 0).toFixed(2)
}

const calculateTotal = () => {
  const subtotal = form.subtotal || 0
  if (form.taxable && form.taxRate) {
    form.taxAmount = (subtotal * form.taxRate) / 100
  } else {
    form.taxAmount = 0
  }
  form.totalAmount = subtotal + form.taxAmount
}

const onVendorChange = () => {
  if (selectedVendor.value) {
    // Auto-calculate due date based on payment terms
    const terms = selectedVendor.value.paymentTerms
    if (terms.includes('Net')) {
      const days = parseInt(terms.match(/\d+/)?.[0] || '30')
      const dueDate = new Date(form.billDate)
      dueDate.setDate(dueDate.getDate() + days)
      form.dueDate = dueDate
    }
  }
}

const addNewVendor = () => {
  if (newVendor.name) {
    const newId = Math.max(...vendors.value.map(v => v.id)) + 1
    vendors.value.push({
      id: newId,
      name: newVendor.name,
      contact: newVendor.contact,
      paymentTerms: 'Net 30',
      taxId: ''
    })
    form.vendorId = newId
    showAddVendor.value = false
    newVendor.name = ''
    newVendor.contact = ''
    toast.add({ severity: 'success', summary: 'Success', detail: 'Vendor added successfully' })
  }
}

const onUpload = (event: any) => {
  toast.add({ severity: 'info', summary: 'Files Uploaded', detail: `${event.files.length} file(s) uploaded` })
}

const saveDraft = async () => {
  toast.add({ severity: 'info', summary: 'Draft Saved', detail: 'Bill saved as draft' })
}

const handleSubmit = async () => {
  // Clear errors
  Object.keys(errors).forEach(key => errors[key] = '')
  
  // Validate
  if (!form.vendorId) errors.vendorId = 'Vendor is required'
  if (!form.billNumber) errors.billNumber = 'Bill number is required'
  if (!form.subtotal) errors.subtotal = 'Subtotal is required'
  if (!form.dueDate) errors.dueDate = 'Due date is required'
  
  if (Object.values(errors).some(error => error)) {
    toast.add({ severity: 'error', summary: 'Validation Error', detail: 'Please fill in all required fields' })
    return
  }
  
  loading.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1500))
    toast.add({ severity: 'success', summary: 'Success', detail: 'Bill created successfully' })
    router.push('/ap')
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to create bill' })
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.create-bill {
  padding: 0;
}

.page-header {
  background: white;
  border-bottom: 1px solid #e5e7eb;
  padding: 1.5rem 2rem;
  margin-bottom: 2rem;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-left h1 {
  margin: 0;
  font-size: 1.75rem;
  font-weight: 600;
  color: #1f2937;
}

.subtitle {
  margin: 0.25rem 0 0 0;
  color: #6b7280;
  font-size: 0.875rem;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

.form-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem 2rem;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.vendor-section,
.bill-section {
  grid-column: span 1;
}

.amount-section,
.attachments-section {
  grid-column: span 2;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  color: #374151;
}

.section-title i {
  color: #3b82f6;
}

.field {
  margin-bottom: 1.5rem;
}

.field-group {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.required::after {
  content: ' *';
  color: #ef4444;
}

.vendor-input-group {
  display: flex;
  gap: 0.5rem;
}

.vendor-input-group .p-dropdown {
  flex: 1;
}

.vendor-details {
  margin-top: 1rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
}

.vendor-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.75rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.info-item .label {
  font-size: 0.75rem;
  font-weight: 500;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.tax-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.checkbox-label {
  margin: 0;
  font-size: 0.875rem;
  cursor: pointer;
}

.tax-inputs {
  margin-top: 0.75rem;
}

.total-section {
  background: #f9fafb;
  padding: 1rem;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
}

.total-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.total-label {
  font-weight: 600;
  color: #374151;
  font-size: 1.125rem;
}

.total-amount {
  font-weight: 700;
  color: #059669;
  font-size: 1.5rem;
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .vendor-section,
  .bill-section,
  .amount-section,
  .attachments-section {
    grid-column: span 1;
  }
  
  .field-group {
    grid-template-columns: 1fr;
  }
  
  .header-content {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
  
  .header-actions {
    width: 100%;
    justify-content: flex-end;
  }
  
  .form-container {
    padding: 0 1rem 2rem;
  }
}

:deep(.p-card-title) {
  margin-bottom: 1rem;
}

:deep(.p-fileupload) {
  border: 2px dashed #d1d5db;
  border-radius: 0.5rem;
}

:deep(.p-fileupload-content) {
  padding: 2rem;
  text-align: center;
}

:deep(.p-divider) {
  margin: 1.5rem 0;
}
</style>