<template>
  <div class="invoice-form">
    <v-form ref="form" v-model="valid" @submit.prevent="saveInvoice">
      <v-card>
        <v-card-title class="d-flex align-center justify-space-between">
          <h2>{{ isEdit ? 'Edit Invoice' : 'New Invoice' }}</h2>
          <div>
            <v-btn
              v-if="isEdit && canSubmit"
              color="info"
              class="mr-2"
              prepend-icon="mdi-send"
              @click="submitInvoice"
            >
              Submit for Approval
            </v-btn>
            <v-btn
              color="primary"
              type="submit"
              :loading="saving"
              :disabled="!valid || saving"
            >
              {{ isEdit ? 'Update' : 'Create' }} Invoice
            </v-btn>
          </div>
        </v-card-title>
        
        <v-card-text>
          <v-row>
            <!-- Invoice Header -->
            <v-col cols="12">
              <h3 class="text-subtitle-1 font-weight-bold">Invoice Information</h3>
            </v-col>
            
            <v-col cols="12" md="6">
              <v-select
                v-model="formData.vendor_id"
                label="Vendor*"
                :items="vendors"
                item-title="name"
                item-value="id"
                :rules="[v => !!v || 'Vendor is required']"
                required
                :disabled="isEdit"
              ></v-select>
            </v-col>
            
            <v-col cols="12" md="6">
              <v-text-field
                v-model="formData.invoice_number"
                label="Invoice Number*"
                :rules="[v => !!v || 'Invoice number is required']"
                required
                :disabled="isEdit"
              ></v-text-field>
            </v-col>
            
            <v-col cols="12" md="6">
              <v-menu
                ref="invoiceDateMenu"
                v-model="invoiceDateMenu"
                :close-on-content-click="false"
                transition="scale-transition"
                offset-y
                min-width="auto"
              >
                <template v-slot:activator="{ props }">
                  <v-text-field
                    v-model="formData.invoice_date"
                    label="Invoice Date*"
                    prepend-inner-icon="mdi-calendar"
                    readonly
                    v-bind="props"
                    :rules="[v => !!v || 'Invoice date is required']"
                    required
                  ></v-text-field>
                </template>
                <v-date-picker
                  v-model="formData.invoice_date"
                  @update:model-value="invoiceDateMenu = false"
                ></v-date-picker>
              </v-menu>
            </v-col>
            
            <v-col cols="12" md="6">
              <v-menu
                ref="dueDateMenu"
                v-model="dueDateMenu"
                :close-on-content-click="false"
                transition="scale-transition"
                offset-y
                min-width="auto"
              >
                <template v-slot:activator="{ props }">
                  <v-text-field
                    v-model="formData.due_date"
                    label="Due Date*"
                    prepend-inner-icon="mdi-calendar"
                    readonly
                    v-bind="props"
                    :rules="[v => !!v || 'Due date is required']"
                    required
                  ></v-text-field>
                </template>
                <v-date-picker
                  v-model="formData.due_date"
                  @update:model-value="dueDateMenu = false"
                ></v-date-picker>
              </v-menu>
            </v-col>
            
            <v-col cols="12" md="6">
              <v-select
                v-model="formData.payment_terms"
                label="Payment Terms"
                :items="paymentTermsOptions"
                @update:model-value="updateDueDate"
              ></v-select>
            </v-col>
            
            <v-col cols="12" md="6">
              <v-select
                v-model="formData.currency_id"
                label="Currency"
                :items="currencies"
                item-title="name"
                item-value="id"
              ></v-select>
            </v-col>
            
            <v-col cols="12">
              <v-text-field
                v-model="formData.reference"
                label="Reference"
              ></v-text-field>
            </v-col>
            
            <v-col cols="12">
              <v-textarea
                v-model="formData.description"
                label="Description"
                rows="2"
                auto-grow
              ></v-textarea>
            </v-col>
            
            <v-col cols="12">
              <v-checkbox
                v-model="formData.requires_approval"
                label="Requires Approval"
                hide-details
              ></v-checkbox>
            </v-col>
            
            <!-- Line Items -->
            <v-col cols="12" class="mt-4">
              <h3 class="text-subtitle-1 font-weight-bold">Line Items</h3>
              
              <v-data-table
                :headers="lineItemHeaders"
                :items="formData.line_items"
                class="elevation-1 mt-2"
              >
                <template v-slot:item.actions="{ item }">
                  <v-btn
                    icon
                    variant="text"
                    size="small"
                    color="error"
                    @click="removeLineItem(item)"
                  >
                    <v-icon>mdi-delete</v-icon>
                  </v-btn>
                </template>
                
                <template v-slot:item.amount="{ item }">
                  {{ formatCurrency(item.amount) }}
                </template>
                
                <template v-slot:bottom>
                  <v-row class="mt-2">
                    <v-col cols="12">
                      <v-btn
                        color="primary"
                        prepend-icon="mdi-plus"
                        @click="openLineItemDialog"
                      >
                        Add Line Item
                      </v-btn>
                    </v-col>
                  </v-row>
                </template>
              </v-data-table>
            </v-col>
            
            <!-- Totals -->
            <v-col cols="12" md="6" offset-md="6" class="mt-4">
              <v-list>
                <v-list-item>
                  <template v-slot:prepend>
                    <div class="font-weight-medium">Subtotal:</div>
                  </template>
                  <v-list-item-title class="text-right">
                    {{ formatCurrency(calculateSubtotal) }}
                  </v-list-item-title>
                </v-list-item>
                
                <v-list-item>
                  <template v-slot:prepend>
                    <div class="font-weight-medium">Tax:</div>
                  </template>
                  <v-list-item-title class="text-right">
                    {{ formatCurrency(0) }}
                  </v-list-item-title>
                </v-list-item>
                
                <v-list-item>
                  <template v-slot:prepend>
                    <div class="font-weight-bold">Total:</div>
                  </template>
                  <v-list-item-title class="text-right font-weight-bold">
                    {{ formatCurrency(calculateTotal) }}
                  </v-list-item-title>
                </v-list-item>
              </v-list>
            </v-col>
          </v-row>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" variant="text" @click="cancel">Cancel</v-btn>
          <v-btn
            color="primary"
            type="submit"
            :loading="saving"
            :disabled="!valid || saving"
          >
            {{ isEdit ? 'Update' : 'Create' }} Invoice
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-form>
    
    <!-- Line Item Dialog -->
    <v-dialog v-model="lineItemDialog.show" max-width="600px">
      <v-card>
        <v-card-title>{{ lineItemDialog.isEdit ? 'Edit' : 'Add' }} Line Item</v-card-title>
        <v-card-text>
          <v-form ref="lineItemForm" v-model="lineItemDialog.valid">
            <v-row>
              <v-col cols="12">
                <v-text-field
                  v-model="lineItemDialog.item.description"
                  label="Description*"
                  :rules="[v => !!v || 'Description is required']"
                  required
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="lineItemDialog.item.quantity"
                  label="Quantity*"
                  type="number"
                  :rules="[
                    v => !!v || 'Quantity is required',
                    v => v > 0 || 'Quantity must be greater than 0'
                  ]"
                  required
                  @input="calculateLineItemAmount"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="lineItemDialog.item.unit_price"
                  label="Unit Price*"
                  type="number"
                  :rules="[
                    v => !!v || 'Unit price is required',
                    v => v >= 0 || 'Unit price must be non-negative'
                  ]"
                  required
                  @input="calculateLineItemAmount"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="lineItemDialog.item.amount"
                  label="Amount*"
                  type="number"
                  :rules="[v => !!v || 'Amount is required']"
                  required
                  readonly
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-select
                  v-model="lineItemDialog.item.account_id"
                  label="GL Account*"
                  :items="glAccounts"
                  item-title="name"
                  item-value="id"
                  :rules="[v => !!v || 'GL Account is required']"
                  required
                ></v-select>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-select
                  v-model="lineItemDialog.item.tax_code_id"
                  label="Tax Code"
                  :items="taxCodes"
                  item-title="name"
                  item-value="id"
                ></v-select>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" variant="text" @click="lineItemDialog.show = false">Cancel</v-btn>
          <v-btn
            color="primary"
            :disabled="!lineItemDialog.valid"
            @click="saveLineItem"
          >
            {{ lineItemDialog.isEdit ? 'Update' : 'Add' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue';
import { useSnackbar } from '@/composables/useSnackbar';
import { formatCurrency } from '@/utils/formatters';
import { apiClient } from '@/utils/apiClient';
import { addDays } from '@/utils/dateUtils';

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
const { showSnackbar } = useSnackbar();

// Refs
const form = ref(null);
const lineItemForm = ref(null);
const valid = ref(false);
const saving = ref(false);
const invoiceDateMenu = ref(false);
const dueDateMenu = ref(false);

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
  invoice_date: new Date().toISOString().substr(0, 10),
  due_date: '',
  description: '',
  reference: '',
  payment_terms: 'net_30',
  currency_id: null,
  requires_approval: false,
  status: 'draft',
  line_items: [],
});

// Line item dialog
const lineItemDialog = reactive({
  show: false,
  isEdit: false,
  index: -1,
  valid: false,
  item: {
    description: '',
    quantity: 1,
    unit_price: 0,
    amount: 0,
    account_id: null,
    tax_code_id: null,
  },
});

// Line item headers
const lineItemHeaders = [
  { title: 'Description', key: 'description', sortable: true },
  { title: 'Quantity', key: 'quantity', sortable: true },
  { title: 'Unit Price', key: 'unit_price', sortable: true },
  { title: 'Amount', key: 'amount', sortable: true, align: 'end' },
  { title: 'Actions', key: 'actions', sortable: false, align: 'center' },
];

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
    showSnackbar('Failed to load invoice', 'error');
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
  
  formData.due_date = addDays(invoiceDate, daysToAdd).toISOString().substr(0, 10);
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
  if (!lineItemDialog.valid) return;
  
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
    showSnackbar('At least one line item is required', 'error');
    return;
  }
  
  saving.value = true;
  try {
    const payload = { ...formData };
    
    if (isEdit.value) {
      await apiClient.put(`/api/v1/accounts-payable/invoices/${props.invoiceId}`, payload);
      showSnackbar('Invoice updated successfully', 'success');
    } else {
      await apiClient.post('/api/v1/accounts-payable/invoices', payload);
      showSnackbar('Invoice created successfully', 'success');
    }
    
    emit('saved');
  } catch (error) {
    showSnackbar(error.response?.data?.message || 'Failed to save invoice', 'error');
    console.error('Error saving invoice:', error);
  } finally {
    saving.value = false;
  }
};

const submitInvoice = async () => {
  if (!isEdit.value || !props.invoiceId) return;
  
  try {
    await apiClient.post(`/api/v1/accounts-payable/invoices/${props.invoiceId}/submit`);
    showSnackbar('Invoice submitted for approval', 'success');
    emit('saved');
  } catch (error) {
    showSnackbar('Failed to submit invoice', 'error');
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
  padding: 16px;
}
</style>