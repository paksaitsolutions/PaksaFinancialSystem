<template>
  <div class="invoice-form">
    <Card>
      <template #title>
        <div class="flex justify-content-between align-items-center">
          <h2>{{ isEdit ? 'Edit Invoice' : 'New Invoice' }}</h2>
          <div class="flex gap-2">
            <Button
              v-if="isEdit && canSubmit"
              icon="pi pi-send"
              label="Submit for Approval"
              severity="info"
              @click="submitInvoice"
            />
            <Button
              :label="isEdit ? 'Update' : 'Create'"
              :loading="saving"
              :disabled="!isFormValid || saving"
              @click="saveInvoice"
            />
          </div>
        </div>
      </template>
      
      <template #content>
        <form @submit.prevent="saveInvoice">
          <div class="grid">
            <!-- Invoice Header -->
            <div class="col-12">
              <h3 class="text-lg font-semibold mb-3">Invoice Information</h3>
            </div>
            
            <div class="col-12 md:col-6">
              <div class="field">
                <label for="vendor" class="font-semibold">Vendor *</label>
                <Dropdown
                  id="vendor"
                  v-model="formData.vendor_id"
                  :options="vendors"
                  optionLabel="name"
                  optionValue="id"
                  placeholder="Select vendor"
                  :class="{ 'p-invalid': !formData.vendor_id }"
                  :disabled="isEdit"
                  class="w-full"
                />
                <small v-if="!formData.vendor_id" class="p-error">Vendor is required</small>
              </div>
            </div>
            
            <div class="col-12 md:col-6">
              <div class="field">
                <label for="invoice_number" class="font-semibold">Invoice Number *</label>
                <InputText
                  id="invoice_number"
                  v-model="formData.invoice_number"
                  :class="{ 'p-invalid': !formData.invoice_number }"
                  :disabled="isEdit"
                  class="w-full"
                />
                <small v-if="!formData.invoice_number" class="p-error">Invoice number is required</small>
              </div>
            </div>
            
            <div class="col-12 md:col-6">
              <div class="field">
                <label for="invoice_date" class="font-semibold">Invoice Date *</label>
                <Calendar
                  id="invoice_date"
                  v-model="formData.invoice_date"
                  :class="{ 'p-invalid': !formData.invoice_date }"
                  showIcon
                  class="w-full"
                />
                <small v-if="!formData.invoice_date" class="p-error">Invoice date is required</small>
              </div>
            </div>
            
            <div class="col-12 md:col-6">
              <div class="field">
                <label for="due_date" class="font-semibold">Due Date *</label>
                <Calendar
                  id="due_date"
                  v-model="formData.due_date"
                  :class="{ 'p-invalid': !formData.due_date }"
                  showIcon
                  class="w-full"
                />
                <small v-if="!formData.due_date" class="p-error">Due date is required</small>
              </div>
            </div>
            
            <div class="col-12 md:col-6">
              <div class="field">
                <label for="payment_terms" class="font-semibold">Payment Terms</label>
                <Dropdown
                  id="payment_terms"
                  v-model="formData.payment_terms"
                  :options="paymentTermsOptions"
                  optionLabel="title"
                  optionValue="value"
                  placeholder="Select payment terms"
                  class="w-full"
                  @change="updateDueDate"
                />
              </div>
            </div>
            
            <div class="col-12 md:col-6">
              <div class="field">
                <label for="currency" class="font-semibold">Currency</label>
                <Dropdown
                  id="currency"
                  v-model="formData.currency_id"
                  :options="currencies"
                  optionLabel="name"
                  optionValue="id"
                  placeholder="Select currency"
                  class="w-full"
                />
              </div>
            </div>
            
            <div class="col-12">
              <div class="field">
                <label for="reference" class="font-semibold">Reference</label>
                <InputText
                  id="reference"
                  v-model="formData.reference"
                  class="w-full"
                />
              </div>
            </div>
            
            <div class="col-12">
              <div class="field">
                <label for="description" class="font-semibold">Description</label>
                <Textarea
                  id="description"
                  v-model="formData.description"
                  rows="2"
                  class="w-full"
                />
              </div>
            </div>
            
            <div class="col-12">
              <div class="field-checkbox">
                <Checkbox
                  id="requires_approval"
                  v-model="formData.requires_approval"
                  :binary="true"
                />
                <label for="requires_approval">Requires Approval</label>
              </div>
            </div>
            
            <!-- Line Items -->
            <div class="col-12 mt-4">
              <h3 class="text-lg font-semibold mb-3">Line Items</h3>
              
              <DataTable
                :value="formData.line_items"
                class="mb-3"
                responsiveLayout="scroll"
              >
                <template #empty>No line items added.</template>
                <Column field="description" header="Description" />
                <Column field="quantity" header="Quantity" />
                <Column field="unit_price" header="Unit Price">
                  <template #body="{ data }">
                    {{ formatCurrency(data.unit_price) }}
                  </template>
                </Column>
                <Column field="amount" header="Amount">
                  <template #body="{ data }">
                    {{ formatCurrency(data.amount) }}
                  </template>
                </Column>
                <Column header="Actions" style="width: 4rem">
                  <template #body="{ data }">
                    <Button
                      icon="pi pi-trash"
                      class="p-button-text p-button-sm p-button-danger"
                      @click="removeLineItem(data)"
                    />
                  </template>
                </Column>
              </DataTable>
              
              <Button
                icon="pi pi-plus"
                label="Add Line Item"
                class="p-button-outlined"
                @click="openLineItemDialog"
              />
            </div>
            
            <!-- Totals -->
            <div class="col-12 md:col-6 md:col-offset-6 mt-4">
              <Card class="bg-primary-50">
                <template #content>
                  <div class="flex justify-content-between align-items-center mb-2">
                    <span class="font-medium">Subtotal:</span>
                    <span>{{ formatCurrency(calculateSubtotal) }}</span>
                  </div>
                  <div class="flex justify-content-between align-items-center mb-2">
                    <span class="font-medium">Tax:</span>
                    <span>{{ formatCurrency(0) }}</span>
                  </div>
                  <div class="flex justify-content-between align-items-center">
                    <span class="font-bold">Total:</span>
                    <span class="font-bold text-primary">{{ formatCurrency(calculateTotal) }}</span>
                  </div>
                </template>
              </Card>
            </div>
          </div>
        </form>
      </template>
      
      <template #footer>
        <div class="flex justify-content-end gap-2">
          <Button label="Cancel" severity="secondary" @click="cancel" />
          <Button
            :label="isEdit ? 'Update' : 'Create'"
            :loading="saving"
            :disabled="!isFormValid || saving"
            @click="saveInvoice"
          />
        </div>
      </template>
    </Card>
    
    <!-- Line Item Dialog -->
    <Dialog
      v-model:visible="lineItemDialog.show"
      :style="{width: '600px'}"
      :header="lineItemDialog.isEdit ? 'Edit Line Item' : 'Add Line Item'"
      :modal="true"
      class="p-fluid"
    >
      <div class="grid">
        <div class="col-12">
          <div class="field">
            <label for="item_description" class="font-semibold">Description *</label>
            <InputText
              id="item_description"
              v-model="lineItemDialog.item.description"
              :class="{ 'p-invalid': !lineItemDialog.item.description }"
              class="w-full"
            />
            <small v-if="!lineItemDialog.item.description" class="p-error">Description is required</small>
          </div>
        </div>
        
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="quantity" class="font-semibold">Quantity *</label>
            <InputNumber
              id="quantity"
              v-model="lineItemDialog.item.quantity"
              :min="0"
              class="w-full"
              @input="calculateLineItemAmount"
            />
          </div>
        </div>
        
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="unit_price" class="font-semibold">Unit Price *</label>
            <InputNumber
              id="unit_price"
              v-model="lineItemDialog.item.unit_price"
              mode="currency"
              currency="USD"
              locale="en-US"
              :min="0"
              class="w-full"
              @input="calculateLineItemAmount"
            />
          </div>
        </div>
        
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="amount" class="font-semibold">Amount</label>
            <InputNumber
              id="amount"
              v-model="lineItemDialog.item.amount"
              mode="currency"
              currency="USD"
              locale="en-US"
              readonly
              class="w-full"
            />
          </div>
        </div>
        
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="account" class="font-semibold">GL Account *</label>
            <Dropdown
              id="account"
              v-model="lineItemDialog.item.account_id"
              :options="glAccounts"
              optionLabel="name"
              optionValue="id"
              placeholder="Select account"
              class="w-full"
            />
          </div>
        </div>
        
        <div class="col-12 md:col-6">
          <div class="field">
            <label for="tax_code" class="font-semibold">Tax Code</label>
            <Dropdown
              id="tax_code"
              v-model="lineItemDialog.item.tax_code_id"
              :options="taxCodes"
              optionLabel="name"
              optionValue="id"
              placeholder="Select tax code"
              class="w-full"
            />
          </div>
        </div>
      </div>
      
      <template #footer>
        <Button
          label="Cancel"
          severity="secondary"
          @click="lineItemDialog.show = false"
        />
        <Button
          :label="lineItemDialog.isEdit ? 'Update' : 'Add'"
          :disabled="!isLineItemValid"
          @click="saveLineItem"
        />
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useToast } from 'primevue/usetoast'
import { formatCurrency } from '@/utils/formatters'
import { apiClient } from '@/utils/apiClient'
import { addToDate } from '@/utils/date'
import Card from 'primevue/card'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Textarea from 'primevue/textarea'
import Calendar from 'primevue/calendar'
import Dropdown from 'primevue/dropdown'
import Checkbox from 'primevue/checkbox'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Dialog from 'primevue/dialog'

// Props
const props = defineProps({
  invoiceId: {
    type: String,
    default: null,
  },
});

// Emits
const emit = defineEmits(['saved', 'cancelled']);

// Composables
const toast = useToast()

// Refs
const saving = ref(false)

// Data
const vendors = ref([]);
const currencies = ref([]);
const glAccounts = ref([]);
const taxCodes = ref([]);
const isEdit = computed(() => !!props.invoiceId);
const canSubmit = computed(() => isEdit.value && formData.status === 'draft');

// Form data
const formData = reactive({
  vendor_id: null,
  invoice_number: '',
  invoice_date: new Date(),
  due_date: new Date(),
  description: '',
  reference: '',
  payment_terms: 'net_30',
  currency_id: null,
  requires_approval: false,
  status: 'draft',
  line_items: [],
})

// Line item dialog
const lineItemDialog = reactive({
  show: false,
  isEdit: false,
  index: -1,
  item: {
    description: '',
    quantity: 1,
    unit_price: 0,
    amount: 0,
    account_id: null,
    tax_code_id: null,
  },
})

// Computed
const isFormValid = computed(() => {
  return formData.vendor_id && formData.invoice_number && formData.invoice_date && formData.due_date
})

const isLineItemValid = computed(() => {
  return lineItemDialog.item.description && lineItemDialog.item.quantity > 0 && lineItemDialog.item.unit_price >= 0
})

// Payment terms options
const paymentTermsOptions = [
  { title: 'Net 15', value: 'net_15' },
  { title: 'Net 30', value: 'net_30' },
  { title: 'Net 45', value: 'net_45' },
  { title: 'Net 60', value: 'net_60' },
  { title: 'Due on Receipt', value: 'due_on_receipt' },
  { title: 'Prepaid', value: 'prepaid' },
  { title: 'COD', value: 'cod' },
  { title: 'Custom', value: 'custom' },
];

// Computed
const calculateSubtotal = computed(() => {
  return formData.line_items.reduce((sum, item) => sum + Number(item.amount), 0);
});

const calculateTotal = computed(() => {
  return calculateSubtotal.value;
});

// Methods
const fetchVendors = async () => {
  try {
    const response = await apiClient.get('/api/v1/accounts-payable/vendors', { 
      params: { page_size: 100 } 
    });
    vendors.value = response.data;
  } catch (error) {
    console.error('Error fetching vendors:', error);
  }
};

const fetchCurrencies = async () => {
  try {
    const response = await apiClient.get('/api/v1/currencies');
    currencies.value = response.data || [];
  } catch (error) {
    console.error('Error fetching currencies:', error);
  }
};

const fetchGLAccounts = async () => {
  try {
    const response = await apiClient.get('/api/v1/general-ledger/accounts', {
      params: { page_size: 100 }
    });
    glAccounts.value = response.data || [];
  } catch (error) {
    console.error('Error fetching GL accounts:', error);
  }
};

const fetchTaxCodes = async () => {
  try {
    const response = await apiClient.get('/api/v1/tax/codes');
    taxCodes.value = response.data || [];
  } catch (error) {
    console.error('Error fetching tax codes:', error);
  }
};

const fetchInvoice = async () => {
  if (!props.invoiceId) return;
  
  try {
    const response = await apiClient.get(`/api/v1/accounts-payable/invoices/${props.invoiceId}`);
    const invoice = response.data;
    
    // Populate form data
    Object.keys(formData).forEach(key => {
      if (key !== 'line_items' && invoice[key] !== undefined) {
        formData[key] = invoice[key];
      }
    });
    
    // Populate line items
    formData.line_items = invoice.line_items || [];
    
    // Set status
    formData.status = invoice.status;
    
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load invoice' })
    console.error('Error fetching invoice:', error);
  }
};

const updateDueDate = () => {
  if (!formData.invoice_date) return;
  
  const invoiceDate = new Date(formData.invoice_date);
  let daysToAdd = 0;
  
  switch (formData.payment_terms) {
    case 'net_15':
      daysToAdd = 15;
      break;
    case 'net_30':
      daysToAdd = 30;
      break;
    case 'net_45':
      daysToAdd = 45;
      break;
    case 'net_60':
      daysToAdd = 60;
      break;
    case 'due_on_receipt':
      daysToAdd = 0;
      break;
    default:
      daysToAdd = 30;
  }
  
  formData.due_date = addToDate(invoiceDate, daysToAdd, 'days')
};

const openLineItemDialog = () => {
  lineItemDialog.isEdit = false;
  lineItemDialog.index = -1;
  lineItemDialog.item = {
    description: '',
    quantity: 1,
    unit_price: 0,
    amount: 0,
    account_id: null,
    tax_code_id: null,
  };
  lineItemDialog.show = true;
};

const editLineItem = (item, index) => {
  lineItemDialog.isEdit = true;
  lineItemDialog.index = index;
  lineItemDialog.item = { ...item };
  lineItemDialog.show = true;
};

const removeLineItem = (item) => {
  const index = formData.line_items.indexOf(item);
  if (index !== -1) {
    formData.line_items.splice(index, 1);
  }
};

const calculateLineItemAmount = () => {
  const quantity = Number(lineItemDialog.item.quantity) || 0;
  const unitPrice = Number(lineItemDialog.item.unit_price) || 0;
  lineItemDialog.item.amount = quantity * unitPrice;
};

const saveLineItem = () => {
  if (!isLineItemValid.value) return
  
  if (lineItemDialog.isEdit && lineItemDialog.index !== -1) {
    // Update existing line item
    formData.line_items[lineItemDialog.index] = { ...lineItemDialog.item };
  } else {
    // Add new line item
    formData.line_items.push({ ...lineItemDialog.item });
  }
  
  lineItemDialog.show = false;
};

const saveInvoice = async () => {
  if (!valid.value) return;
  
  // Validate line items
  if (formData.line_items.length === 0) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'At least one line item is required' })
    return
  }
  
  saving.value = true;
  try {
    const payload = { ...formData };
    
    if (isEdit.value) {
      await apiClient.put(`/api/v1/accounts-payable/invoices/${props.invoiceId}`, payload);
      toast.add({ severity: 'success', summary: 'Success', detail: 'Invoice updated successfully' })
    } else {
      await apiClient.post('/api/v1/accounts-payable/invoices', payload);
      toast.add({ severity: 'success', summary: 'Success', detail: 'Invoice created successfully' })
    }
    
    emit('saved');
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: error.response?.data?.message || 'Failed to save invoice' })
    console.error('Error saving invoice:', error);
  } finally {
    saving.value = false;
  }
};

const submitInvoice = async () => {
  if (!isEdit.value || !props.invoiceId) return;
  
  try {
    await apiClient.post(`/api/v1/accounts-payable/invoices/${props.invoiceId}/submit`);
    toast.add({ severity: 'success', summary: 'Success', detail: 'Invoice submitted for approval' })
    emit('saved');
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to submit invoice' })
    console.error('Error submitting invoice:', error);
  }
};

const cancel = () => {
  emit('cancelled');
};

// Watchers
watch(() => formData.invoice_date, () => {
  updateDueDate();
});

// Lifecycle hooks
onMounted(() => {
  fetchVendors();
  fetchCurrencies();
  fetchGLAccounts();
  fetchTaxCodes();
  
  if (isEdit.value) {
    fetchInvoice();
  } else {
    updateDueDate();
  }
});
</script>

<style scoped>
.invoice-form {
  padding: 1.5rem;
}

.field {
  margin-bottom: 1.5rem;
}

.field-checkbox {
  margin-bottom: 1.5rem;
}
</style>