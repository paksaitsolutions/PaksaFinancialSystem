<template>
  <div class="invoice-form">
    <v-card>
      <v-card-title>{{ isEdit ? 'Edit Invoice' : 'Create Invoice' }}</v-card-title>
      
      <v-card-text>
        <v-form ref="form" v-model="valid">
          <v-row>
            <!-- Customer Selection -->
            <v-col cols="12" md="6">
              <v-select
                v-model="invoice.customer_id"
                label="Customer*"
                :items="customers"
                item-title="name"
                item-value="id"
                :rules="[v => !!v || 'Customer is required']"
                required
              ></v-select>
            </v-col>
            
            <!-- Template Selection -->
            <v-col cols="12" md="6">
              <v-select
                v-model="invoice.template_id"
                label="Template"
                :items="templates"
                item-title="name"
                item-value="id"
                clearable
              ></v-select>
            </v-col>
            
            <!-- Dates -->
            <v-col cols="12" md="6">
              <v-text-field
                v-model="invoice.issue_date"
                label="Issue Date*"
                type="date"
                :rules="[v => !!v || 'Issue date is required']"
                required
              ></v-text-field>
            </v-col>
            
            <v-col cols="12" md="6">
              <v-text-field
                v-model="invoice.due_date"
                label="Due Date*"
                type="date"
                :rules="[v => !!v || 'Due date is required']"
                required
              ></v-text-field>
            </v-col>
            
            <!-- Recurring Options -->
            <v-col cols="12" md="6">
              <v-checkbox
                v-model="invoice.is_recurring"
                label="Recurring Invoice"
              ></v-checkbox>
            </v-col>
            
            <v-col cols="12" md="6" v-if="invoice.is_recurring">
              <v-select
                v-model="invoice.recurring_frequency"
                label="Frequency"
                :items="frequencies"
                item-title="text"
                item-value="value"
              ></v-select>
            </v-col>
          </v-row>
          
          <!-- Invoice Items -->
          <v-divider class="my-4"></v-divider>
          <h3 class="mb-4">Invoice Items</h3>
          
          <div v-for="(item, index) in invoice.items" :key="index" class="mb-4">
            <v-card variant="outlined">
              <v-card-text>
                <v-row>
                  <v-col cols="12" md="4">
                    <v-text-field
                      v-model="item.description"
                      label="Description*"
                      :rules="[v => !!v || 'Description is required']"
                      required
                    ></v-text-field>
                  </v-col>
                  
                  <v-col cols="12" md="2">
                    <v-text-field
                      v-model.number="item.quantity"
                      label="Quantity*"
                      type="number"
                      step="0.01"
                      :rules="[v => !!v || 'Quantity is required']"
                      @input="calculateItemTotal(item)"
                      required
                    ></v-text-field>
                  </v-col>
                  
                  <v-col cols="12" md="2">
                    <v-text-field
                      v-model.number="item.unit_price"
                      label="Unit Price*"
                      type="number"
                      step="0.01"
                      :rules="[v => !!v || 'Unit price is required']"
                      @input="calculateItemTotal(item)"
                      required
                    ></v-text-field>
                  </v-col>
                  
                  <v-col cols="12" md="2">
                    <v-text-field
                      v-model.number="item.total_price"
                      label="Total"
                      type="number"
                      readonly
                    ></v-text-field>
                  </v-col>
                  
                  <v-col cols="12" md="2" class="d-flex align-center">
                    <v-btn
                      color="error"
                      icon
                      size="small"
                      @click="removeItem(index)"
                      :disabled="invoice.items.length === 1"
                    >
                      <v-icon>mdi-delete</v-icon>
                    </v-btn>
                  </v-col>
                </v-row>
              </v-card-text>
            </v-card>
          </div>
          
          <v-btn
            color="primary"
            prepend-icon="mdi-plus"
            @click="addItem"
            class="mb-4"
          >
            Add Item
          </v-btn>
          
          <!-- Totals -->
          <v-divider class="my-4"></v-divider>
          <v-row>
            <v-col cols="12" md="6">
              <!-- Notes and Terms -->
              <v-textarea
                v-model="invoice.notes"
                label="Notes"
                rows="3"
              ></v-textarea>
              
              <v-textarea
                v-model="invoice.terms"
                label="Terms & Conditions"
                rows="3"
              ></v-textarea>
            </v-col>
            
            <v-col cols="12" md="6">
              <v-card variant="outlined">
                <v-card-text>
                  <div class="d-flex justify-space-between mb-2">
                    <span>Subtotal:</span>
                    <span>{{ formatCurrency(invoice.subtotal) }}</span>
                  </div>
                  
                  <v-text-field
                    v-model.number="invoice.tax_amount"
                    label="Tax Amount"
                    type="number"
                    step="0.01"
                    @input="calculateTotal"
                    density="compact"
                  ></v-text-field>
                  
                  <v-divider class="my-2"></v-divider>
                  
                  <div class="d-flex justify-space-between">
                    <strong>Total:</strong>
                    <strong>{{ formatCurrency(invoice.total_amount) }}</strong>
                  </div>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </v-form>
      </v-card-text>
      
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn @click="$emit('cancel')">Cancel</v-btn>
        <v-btn
          color="primary"
          :loading="loading"
          :disabled="!valid"
          @click="saveInvoice"
        >
          {{ isEdit ? 'Update' : 'Create' }} Invoice
        </v-btn>
      </v-card-actions>
    </v-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue';
import { useSnackbar } from '@/composables/useSnackbar';
import { formatCurrency } from '@/utils/formatters';
import { apiClient } from '@/utils/apiClient';

const { showSnackbar } = useSnackbar();

const props = defineProps({
  invoiceData: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['saved', 'cancel']);

const valid = ref(false);
const loading = ref(false);
const customers = ref([]);
const templates = ref([]);

const isEdit = computed(() => !!props.invoiceData);

const invoice = reactive({
  customer_id: null,
  template_id: null,
  issue_date: new Date().toISOString().split('T')[0],
  due_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
  subtotal: 0,
  tax_amount: 0,
  total_amount: 0,
  notes: '',
  terms: '',
  is_recurring: false,
  recurring_frequency: null,
  items: [
    {
      description: '',
      quantity: 1,
      unit_price: 0,
      total_price: 0
    }
  ]
});

const frequencies = [
  { text: 'Monthly', value: 'monthly' },
  { text: 'Quarterly', value: 'quarterly' },
  { text: 'Yearly', value: 'yearly' }
];

// Methods
const addItem = () => {
  invoice.items.push({
    description: '',
    quantity: 1,
    unit_price: 0,
    total_price: 0
  });
};

const removeItem = (index) => {
  if (invoice.items.length > 1) {
    invoice.items.splice(index, 1);
    calculateSubtotal();
  }
};

const calculateItemTotal = (item) => {
  item.total_price = (item.quantity || 0) * (item.unit_price || 0);
  calculateSubtotal();
};

const calculateSubtotal = () => {
  invoice.subtotal = invoice.items.reduce((sum, item) => sum + (item.total_price || 0), 0);
  calculateTotal();
};

const calculateTotal = () => {
  invoice.total_amount = invoice.subtotal + (invoice.tax_amount || 0);
};

const saveInvoice = async () => {
  loading.value = true;
  try {
    const endpoint = isEdit.value 
      ? `/api/v1/invoicing/${props.invoiceData.id}`
      : '/api/v1/invoicing/';
    
    const method = isEdit.value ? 'put' : 'post';
    
    const response = await apiClient[method](endpoint, invoice);
    
    showSnackbar(
      `Invoice ${isEdit.value ? 'updated' : 'created'} successfully`, 
      'success'
    );
    emit('saved', response.data);
  } catch (error) {
    showSnackbar('Failed to save invoice', 'error');
    console.error('Save invoice error:', error);
  } finally {
    loading.value = false;
  }
};

const fetchCustomers = async () => {
  try {
    // Mock customers - replace with actual API call
    customers.value = [
      { id: '1', name: 'Customer A' },
      { id: '2', name: 'Customer B' },
      { id: '3', name: 'Customer C' }
    ];
  } catch (error) {
    console.error('Error fetching customers:', error);
  }
};

const fetchTemplates = async () => {
  try {
    const response = await apiClient.get('/api/v1/invoicing/templates');
    templates.value = response.data;
  } catch (error) {
    console.error('Error fetching templates:', error);
  }
};

// Watchers
watch(() => invoice.items, calculateSubtotal, { deep: true });

// Lifecycle
onMounted(() => {
  fetchCustomers();
  fetchTemplates();
  
  if (props.invoiceData) {
    Object.assign(invoice, props.invoiceData);
  }
});
</script>

<style scoped>
.invoice-form {
  max-width: 1200px;
  margin: 0 auto;
}
</style>