<template>
  <div class="credit-memo-form">
    <v-form ref="form" v-model="valid" @submit.prevent="saveCreditMemo">
      <v-card>
        <v-card-title>
          <h2>New Credit Memo</h2>
        </v-card-title>
        
        <v-card-text>
          <v-row>
            <!-- Credit Memo Header -->
            <v-col cols="12">
              <h3 class="text-subtitle-1 font-weight-bold">Credit Memo Information</h3>
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
              ></v-select>
            </v-col>
            
            <v-col cols="12" md="6">
              <v-menu
                ref="creditDateMenu"
                v-model="creditDateMenu"
                :close-on-content-click="false"
                transition="scale-transition"
                offset-y
                min-width="auto"
              >
                <template v-slot:activator="{ props }">
                  <v-text-field
                    v-model="formData.credit_date"
                    label="Credit Date*"
                    prepend-inner-icon="mdi-calendar"
                    readonly
                    v-bind="props"
                    :rules="[v => !!v || 'Credit date is required']"
                    required
                  ></v-text-field>
                </template>
                <v-date-picker
                  v-model="formData.credit_date"
                  @update:model-value="creditDateMenu = false"
                ></v-date-picker>
              </v-menu>
            </v-col>
            
            <v-col cols="12" md="6">
              <v-text-field
                v-model="formData.amount"
                label="Credit Amount*"
                type="number"
                step="0.01"
                min="0"
                :rules="[
                  v => !!v || 'Amount is required',
                  v => v > 0 || 'Amount must be greater than 0'
                ]"
                required
              ></v-text-field>
            </v-col>
            
            <v-col cols="12" md="6">
              <v-text-field
                v-model="formData.reference"
                label="Reference"
                placeholder="Original invoice number, etc."
              ></v-text-field>
            </v-col>
            
            <v-col cols="12" md="6">
              <v-select
                v-model="formData.original_invoice_id"
                label="Original Invoice (Optional)"
                :items="vendorInvoices"
                item-title="invoice_number"
                item-value="id"
                clearable
              ></v-select>
            </v-col>
            
            <v-col cols="12">
              <v-textarea
                v-model="formData.description"
                label="Description*"
                rows="3"
                auto-grow
                :rules="[v => !!v || 'Description is required']"
                required
                placeholder="Reason for credit memo..."
              ></v-textarea>
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
            Create Credit Memo
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-form>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue';
import { useSnackbar } from '@/composables/useSnackbar';
import { apiClient } from '@/utils/apiClient';

// Emits
const emit = defineEmits(['saved', 'cancelled']);

// Composables
const { showSnackbar } = useSnackbar();

// Refs
const form = ref(null);
const valid = ref(false);
const saving = ref(false);
const creditDateMenu = ref(false);

// Data
const vendors = ref([]);
const vendorInvoices = ref([]);

// Form data
const formData = reactive({
  vendor_id: null,
  credit_date: new Date().toISOString().substr(0, 10),
  amount: 0,
  description: '',
  reference: '',
  original_invoice_id: null,
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

const fetchVendorInvoices = async (vendorId) => {
  if (!vendorId) {
    vendorInvoices.value = [];
    return;
  }
  
  try {
    const response = await apiClient.get('/api/v1/accounts-payable/invoices', {
      params: {
        vendor_id: vendorId,
        page_size: 100,
      }
    });
    vendorInvoices.value = response.data;
  } catch (error) {
    console.error('Error fetching vendor invoices:', error);
  }
};

const saveCreditMemo = async () => {
  if (!valid.value) return;
  
  saving.value = true;
  try {
    const payload = {
      vendor_id: formData.vendor_id,
      credit_date: formData.credit_date,
      amount: Number(formData.amount),
      description: formData.description,
      reference: formData.reference,
      original_invoice_id: formData.original_invoice_id,
    };
    
    await apiClient.post('/api/v1/accounts-payable/credit-memos', payload);
    showSnackbar('Credit memo created successfully', 'success');
    emit('saved');
  } catch (error) {
    showSnackbar(error.response?.data?.message || 'Failed to create credit memo', 'error');
    console.error('Error creating credit memo:', error);
  } finally {
    saving.value = false;
  }
};

const cancel = () => {
  emit('cancelled');
};

// Watchers
watch(() => formData.vendor_id, (newVendorId) => {
  fetchVendorInvoices(newVendorId);
  formData.original_invoice_id = null;
});

// Lifecycle hooks
onMounted(() => {
  fetchVendors();
});
</script>

<style scoped>
.credit-memo-form {
  padding: 16px;
}
</style>