<template>
  <div class="credit-memo-application">
    <v-form ref="form" v-model="valid" @submit.prevent="applyCreditMemo">
      <v-card>
        <v-card-title>
          <h2>Apply Credit Memo</h2>
        </v-card-title>
        
        <v-card-text>
          <v-row>
            <!-- Credit Memo Info -->
            <v-col cols="12">
              <v-card variant="outlined" class="mb-4">
                <v-card-title>Credit Memo Information</v-card-title>
                <v-card-text>
                  <v-row>
                    <v-col cols="12" md="6">
                      <div class="text-caption">Credit Memo Number</div>
                      <div class="text-body-1 font-weight-medium">{{ creditMemo.credit_memo_number }}</div>
                    </v-col>
                    <v-col cols="12" md="6">
                      <div class="text-caption">Vendor</div>
                      <div class="text-body-1">{{ creditMemo.vendor?.name }}</div>
                    </v-col>
                    <v-col cols="12" md="6">
                      <div class="text-caption">Total Amount</div>
                      <div class="text-body-1 font-weight-bold">{{ formatCurrency(creditMemo.amount) }}</div>
                    </v-col>
                    <v-col cols="12" md="6">
                      <div class="text-caption">Remaining Amount</div>
                      <div class="text-body-1 font-weight-bold text-success">{{ formatCurrency(creditMemo.remaining_amount) }}</div>
                    </v-col>
                  </v-row>
                </v-card-text>
              </v-card>
            </v-col>
            
            <!-- Invoice Selection -->
            <v-col cols="12">
              <h3 class="text-subtitle-1 font-weight-bold">Select Invoices to Apply Credit</h3>
              
              <v-data-table
                v-model="selectedInvoices"
                :headers="invoiceHeaders"
                :items="availableInvoices"
                :loading="loadingInvoices"
                item-value="id"
                show-select
                class="elevation-1 mt-2"
                @update:model-value="handleInvoiceSelection"
              >
                <template v-slot:item.invoice_date="{ item }">
                  {{ formatDate(item.invoice_date) }}
                </template>
                
                <template v-slot:item.due_date="{ item }">
                  {{ formatDate(item.due_date) }}
                </template>
                
                <template v-slot:item.total_amount="{ item }">
                  {{ formatCurrency(item.total_amount) }}
                </template>
                
                <template v-slot:item.balance_due="{ item }">
                  {{ formatCurrency(item.balance_due) }}
                </template>
                
                <template v-slot:item.credit_amount="{ item }">
                  <v-text-field
                    v-model="invoiceCredits[item.id]"
                    type="number"
                    step="0.01"
                    density="compact"
                    hide-details
                    :disabled="!isInvoiceSelected(item.id)"
                    :rules="[
                      v => !isInvoiceSelected(item.id) || !!v || 'Amount is required',
                      v => !isInvoiceSelected(item.id) || v > 0 || 'Amount must be greater than 0',
                      v => !isInvoiceSelected(item.id) || v <= item.balance_due || 'Amount cannot exceed balance due'
                    ]"
                    @input="updateTotalCreditAmount"
                  ></v-text-field>
                </template>
              </v-data-table>
            </v-col>
            
            <!-- Totals -->
            <v-col cols="12" md="6" offset-md="6" class="mt-4">
              <v-list>
                <v-list-item>
                  <template v-slot:prepend>
                    <div class="font-weight-medium">Available Credit:</div>
                  </template>
                  <v-list-item-title class="text-right">
                    {{ formatCurrency(creditMemo.remaining_amount) }}
                  </v-list-item-title>
                </v-list-item>
                
                <v-list-item>
                  <template v-slot:prepend>
                    <div class="font-weight-bold">Total Application:</div>
                  </template>
                  <v-list-item-title class="text-right font-weight-bold">
                    {{ formatCurrency(totalCreditAmount) }}
                  </v-list-item-title>
                </v-list-item>
                
                <v-list-item>
                  <template v-slot:prepend>
                    <div class="font-weight-medium">Remaining After:</div>
                  </template>
                  <v-list-item-title class="text-right">
                    {{ formatCurrency(creditMemo.remaining_amount - totalCreditAmount) }}
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
            :disabled="!valid || saving || !hasSelectedInvoices || totalCreditAmount <= 0 || totalCreditAmount > creditMemo.remaining_amount"
          >
            Apply Credit
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-form>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { useSnackbar } from '@/composables/useSnackbar';
import { formatCurrency, formatDate } from '@/utils/formatters';
import { apiClient } from '@/utils/apiClient';

// Props
const props = defineProps({
  creditMemo: {
    type: Object,
    required: true,
  },
});

// Emits
const emit = defineEmits(['saved', 'cancelled']);

// Composables
const { showSnackbar } = useSnackbar();

// Refs
const form = ref(null);
const valid = ref(false);
const saving = ref(false);

// Data
const availableInvoices = ref([]);
const selectedInvoices = ref([]);
const invoiceCredits = reactive({});
const loadingInvoices = ref(false);

// Invoice headers
const invoiceHeaders = [
  { title: 'Invoice #', key: 'invoice_number', sortable: true },
  { title: 'Date', key: 'invoice_date', sortable: true },
  { title: 'Due Date', key: 'due_date', sortable: true },
  { title: 'Total', key: 'total_amount', sortable: true, align: 'end' },
  { title: 'Balance Due', key: 'balance_due', sortable: true, align: 'end' },
  { title: 'Credit Amount', key: 'credit_amount', sortable: false, align: 'end' },
];

// Computed
const totalCreditAmount = computed(() => {
  let total = 0;
  for (const invoiceId of selectedInvoices.value) {
    total += Number(invoiceCredits[invoiceId] || 0);
  }
  return total;
});

const hasSelectedInvoices = computed(() => {
  return selectedInvoices.value.length > 0;
});

// Methods
const fetchVendorInvoices = async () => {
  if (!props.creditMemo.vendor_id) return;
  
  loadingInvoices.value = true;
  try {
    const response = await apiClient.get('/api/v1/accounts-payable/invoices', {
      params: {
        vendor_id: props.creditMemo.vendor_id,
        status: 'approved',
        page_size: 100,
      }
    });
    
    // Filter invoices with balance due > 0
    availableInvoices.value = response.data.filter(invoice => invoice.balance_due > 0);
    
    // Initialize credit amounts to minimum of balance due and remaining credit
    for (const invoice of availableInvoices.value) {
      invoiceCredits[invoice.id] = Math.min(invoice.balance_due, props.creditMemo.remaining_amount);
    }
  } catch (error) {
    showSnackbar('Failed to load invoices', 'error');
    console.error('Error fetching invoices:', error);
  } finally {
    loadingInvoices.value = false;
  }
};

const handleInvoiceSelection = (selected) => {
  // Update credit amounts based on selection
  for (const invoiceId of Object.keys(invoiceCredits)) {
    if (!selected.includes(invoiceId)) {
      invoiceCredits[invoiceId] = 0;
    } else if (invoiceCredits[invoiceId] === 0) {
      // If newly selected, set to minimum of balance due and remaining credit
      const invoice = availableInvoices.value.find(inv => inv.id === invoiceId);
      if (invoice) {
        invoiceCredits[invoiceId] = Math.min(invoice.balance_due, props.creditMemo.remaining_amount);
      }
    }
  }
  
  updateTotalCreditAmount();
};

const isInvoiceSelected = (invoiceId) => {
  return selectedInvoices.value.includes(invoiceId);
};

const updateTotalCreditAmount = () => {
  // Ensure total doesn't exceed remaining credit
  const total = totalCreditAmount.value;
  if (total > props.creditMemo.remaining_amount) {
    // Proportionally reduce amounts
    const ratio = props.creditMemo.remaining_amount / total;
    for (const invoiceId of selectedInvoices.value) {
      invoiceCredits[invoiceId] = Math.round(invoiceCredits[invoiceId] * ratio * 100) / 100;
    }
  }
};

const applyCreditMemo = async () => {
  if (!valid.value || !hasSelectedInvoices.value || totalCreditAmount.value <= 0) return;
  
  saving.value = true;
  try {
    // Prepare applications
    const applications = selectedInvoices.value.map(invoiceId => ({
      invoice_id: invoiceId,
      amount: Number(invoiceCredits[invoiceId]),
      notes: `Applied from credit memo ${props.creditMemo.credit_memo_number}`
    })).filter(item => item.amount > 0);
    
    const payload = {
      applications: applications
    };
    
    await apiClient.post(`/api/v1/accounts-payable/credit-memos/${props.creditMemo.id}/apply`, payload);
    showSnackbar('Credit memo applied successfully', 'success');
    emit('saved');
  } catch (error) {
    showSnackbar(error.response?.data?.message || 'Failed to apply credit memo', 'error');
    console.error('Error applying credit memo:', error);
  } finally {
    saving.value = false;
  }
};

const cancel = () => {
  emit('cancelled');
};

// Lifecycle hooks
onMounted(() => {
  fetchVendorInvoices();
});
</script>

<style scoped>
.credit-memo-application {
  padding: 16px;
}
</style>