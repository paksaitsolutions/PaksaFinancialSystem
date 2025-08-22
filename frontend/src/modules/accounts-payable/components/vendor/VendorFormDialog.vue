<template>
  <v-dialog v-model="dialogModel" max-width="800px" persistent>
    <v-card>
      <v-card-title>
        <span class="text-h5">{{ isEdit ? 'Edit Vendor' : 'New Vendor' }}</span>
      </v-card-title>
      
      <v-card-text>
        <v-form ref="form" v-model="valid" @submit.prevent="save">
          <v-container>
            <!-- Basic Information -->
            <v-row>
              <v-col cols="12">
                <h3 class="text-subtitle-1 font-weight-bold">Basic Information</h3>
              </v-col>
              
              <v-col cols="12" md="4">
                <v-text-field
                  v-model="formData.code"
                  label="Vendor Code*"
                  :rules="[v => !!v || 'Code is required']"
                  :disabled="isEdit"
                  required
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="8">
                <v-text-field
                  v-model="formData.name"
                  label="Vendor Name*"
                  :rules="[v => !!v || 'Name is required']"
                  required
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="8">
                <v-text-field
                  v-model="formData.legal_name"
                  label="Legal Name"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="4">
                <v-text-field
                  v-model="formData.tax_id"
                  label="Tax ID"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="4">
                <v-select
                  v-model="formData.status"
                  label="Status*"
                  :items="statusOptions"
                  :rules="[v => !!v || 'Status is required']"
                  required
                ></v-select>
              </v-col>
              
              <v-col cols="12" md="4">
                <v-checkbox
                  v-model="formData.is_1099"
                  label="1099 Vendor"
                  hide-details
                ></v-checkbox>
              </v-col>
            </v-row>
            
            <!-- Contact Information -->
            <v-row>
              <v-col cols="12">
                <h3 class="text-subtitle-1 font-weight-bold mt-4">Contact Information</h3>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="formData.email"
                  label="Email"
                  :rules="emailRules"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="formData.phone"
                  label="Phone"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12">
                <v-text-field
                  v-model="formData.website"
                  label="Website"
                ></v-text-field>
              </v-col>
            </v-row>
            
            <!-- Address -->
            <v-row>
              <v-col cols="12">
                <h3 class="text-subtitle-1 font-weight-bold mt-4">Address</h3>
              </v-col>
              
              <v-col cols="12">
                <v-text-field
                  v-model="formData.address_line1"
                  label="Address Line 1"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12">
                <v-text-field
                  v-model="formData.address_line2"
                  label="Address Line 2"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="formData.city"
                  label="City"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="formData.state"
                  label="State/Province"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="formData.postal_code"
                  label="Postal Code"
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="formData.country"
                  label="Country"
                ></v-text-field>
              </v-col>
            </v-row>
            
            <!-- Payment Information -->
            <v-row>
              <v-col cols="12">
                <h3 class="text-subtitle-1 font-weight-bold mt-4">Payment Information</h3>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-select
                  v-model="formData.payment_terms"
                  label="Payment Terms"
                  :items="paymentTermsOptions"
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
            </v-row>
            
            <!-- Notes -->
            <v-row>
              <v-col cols="12">
                <h3 class="text-subtitle-1 font-weight-bold mt-4">Additional Information</h3>
              </v-col>
              
              <v-col cols="12">
                <v-textarea
                  v-model="formData.notes"
                  label="Notes"
                  rows="3"
                ></v-textarea>
              </v-col>
            </v-row>
          </v-container>
        </v-form>
      </v-card-text>
      
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="primary" variant="text" @click="close">Cancel</v-btn>
        <v-btn
          color="primary"
          :loading="loading"
          :disabled="!valid"
          @click="save"
        >
          {{ isEdit ? 'Update' : 'Create' }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue';
import { useSnackbar } from '@/composables/useSnackbar';
import { apiClient } from '@/utils/apiClient';

// Props
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  vendor: {
    type: Object,
    default: null,
  },
  isEdit: {
    type: Boolean,
    default: false,
  },
});

// Emits
const emit = defineEmits(['update:modelValue', 'saved', 'closed']);

// Composables
const { showSnackbar } = useSnackbar();

// Data
const form = ref(null);
const valid = ref(false);
const loading = ref(false);
const currencies = ref([]);

// Form data
const formData = reactive({
  code: '',
  name: '',
  legal_name: '',
  tax_id: '',
  status: 'active',
  email: '',
  phone: '',
  website: '',
  address_line1: '',
  address_line2: '',
  city: '',
  state: '',
  postal_code: '',
  country: '',
  payment_terms: 'net_30',
  currency_id: null,
  is_1099: false,
  tax_classification: '',
  notes: '',
});

// Options
const statusOptions = [
  { title: 'Active', value: 'active' },
  { title: 'Inactive', value: 'inactive' },
  { title: 'Hold', value: 'hold' },
  { title: 'Pending Approval', value: 'pending_approval' },
  { title: 'Blocked', value: 'blocked' },
];

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

// Validation rules
const emailRules = [
  v => !v || /^\w+([.-]\w+)*@\w+([.-]\w+)*(\.\w{2,3})+$/.test(v) || 'Email must be valid',
];

// Computed
const dialogModel = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
});

// Methods
const fetchCurrencies = async () => {
  try {
    const response = await apiClient.get('/api/v1/currencies');
    currencies.value = response.data || [];
  } catch (error) {
    console.error('Error fetching currencies:', error);
    showSnackbar('Failed to load currencies', 'error');
  }
};

const resetForm = () => {
  Object.keys(formData).forEach(key => {
    if (key === 'status') {
      formData[key] = 'active';
    } else if (key === 'payment_terms') {
      formData[key] = 'net_30';
    } else if (key === 'is_1099') {
      formData[key] = false;
    } else {
      formData[key] = '';
    }
  });
  
  if (form.value) {
    form.value.resetValidation();
  }
};

const populateForm = () => {
  if (!props.vendor) return;
  
  Object.keys(formData).forEach(key => {
    if (props.vendor[key] !== undefined) {
      formData[key] = props.vendor[key];
    }
  });
};

const save = async () => {
  if (!valid.value) return;
  
  loading.value = true;
  try {
    const payload = { ...formData };
    
    if (props.isEdit) {
      await apiClient.put(`/api/v1/accounts-payable/vendors/${props.vendor.id}`, payload);
      showSnackbar('Vendor updated successfully', 'success');
    } else {
      await apiClient.post('/api/v1/accounts-payable/vendors', payload);
      showSnackbar('Vendor created successfully', 'success');
    }
    
    emit('saved');
    close();
  } catch (error) {
    console.error('Error saving vendor:', error);
    showSnackbar(error.response?.data?.message || 'Failed to save vendor', 'error');
  } finally {
    loading.value = false;
  }
};

const close = () => {
  resetForm();
  emit('closed');
};

// Watchers
watch(() => props.vendor, (newValue) => {
  if (newValue) {
    populateForm();
  } else {
    resetForm();
  }
}, { immediate: true });

// Lifecycle hooks
onMounted(() => {
  fetchCurrencies();
});
</script>