<template>
  <v-form ref="form" v-model="valid" @submit.prevent="submit">
    <v-card flat>
      <v-card-title class="text-h6">
        {{ isEdit ? 'Edit' : 'Add' }} Tax Exemption Certificate
      </v-card-title>
      
      <v-card-text>
        <v-container>
          <v-row>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="formData.certificate_number"
                :rules="[v => !!v || 'Certificate number is required']"
                label="Certificate Number"
                required
                outlined
                dense
              />
            </v-col>
            
            <v-col cols="12" md="6">
              <v-autocomplete
                v-model="formData.customer_id"
                :items="customers"
                item-text="name"
                item-value="id"
                :rules="[v => !!v || 'Customer is required']"
                label="Customer"
                required
                outlined
                dense
                clearable
                :loading="loadingCustomers"
                @update:search-input="searchCustomers"
              />
            </v-col>
            
            <v-col cols="12" md="6">
              <v-text-field
                v-model="formData.customer_tax_id"
                label="Customer Tax ID"
                outlined
                dense
              />
            </v-col>
            
            <v-col cols="12" md="6">
              <v-text-field
                v-model="formData.customer_name"
                label="Customer Name"
                outlined
                dense
              />
            </v-col>
            
            <v-col cols="12" md="6">
              <v-select
                v-model="formData.exemption_type"
                :items="exemptionTypes"
                :rules="[v => !!v || 'Exemption type is required']"
                label="Exemption Type"
                required
                outlined
                dense
              />
            </v-col>
            
            <v-col cols="12" md="6">
              <v-text-field
                v-model="formData.issuing_jurisdiction"
                label="Issuing Jurisdiction"
                outlined
                dense
              />
            </v-col>
            
            <v-col cols="12" md="6">
              <v-menu
                v-model="menuIssueDate"
                :close-on-content-click="false"
                :nudge-right="40"
                transition="scale-transition"
                offset-y
                min-width="auto"
              >
                <template v-slot:activator="{ on, attrs }">
                  <v-text-field
                    v-model="formData.issue_date"
                    label="Issue Date"
                    prepend-icon="mdi-calendar"
                    readonly
                    v-bind="attrs"
                    v-on="on"
                    outlined
                    dense
                  />
                </template>
                <v-date-picker
                  v-model="formData.issue_date"
                  @input="menuIssueDate = false"
                />
              </v-menu>
            </v-col>
            
            <v-col cols="12" md="6">
              <v-menu
                v-model="menuExpiryDate"
                :close-on-content-click="false"
                :nudge-right="40"
                transition="scale-transition"
                offset-y
                min-width="auto"
              >
                <template v-slot:activator="{ on, attrs }">
                  <v-text-field
                    v-model="formData.expiry_date"
                    label="Expiry Date"
                    prepend-icon="mdi-calendar"
                    readonly
                    v-bind="attrs"
                    v-on="on"
                    outlined
                    dense
                  />
                </template>
                <v-date-picker
                  v-model="formData.expiry_date"
                  @input="menuExpiryDate = false"
                />
              </v-menu>
            </v-col>
            
            <v-col cols="12">
              <v-combobox
                v-model="formData.tax_codes"
                :items="availableTaxCodes"
                label="Applicable Tax Codes"
                multiple
                chips
                small-chips
                outlined
                dense
              />
            </v-col>
            
            <v-col cols="12">
              <v-textarea
                v-model="formData.notes"
                label="Notes"
                outlined
                dense
                rows="2"
              />
            </v-col>
            
            <v-col cols="12">
              <v-switch
                v-model="formData.is_active"
                label="Is Active"
                color="primary"
              />
            </v-col>
          </v-row>
        </v-container>
      </v-card-text>
      
      <v-card-actions>
        <v-spacer />
        <v-btn
          color="grey darken-1"
          text
          @click="$emit('cancel')"
        >
          Cancel
        </v-btn>
        <v-btn
          color="primary"
          type="submit"
          :loading="loading"
          :disabled="!valid"
        >
          {{ isEdit ? 'Update' : 'Save' }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-form>
</template>

<script lang="ts">
import { defineComponent, ref, watch, onMounted } from '@vue/composition-api';
import { useApi } from '@/composables/useApi';
import { useSnackbar } from '@/composables/useSnackbar';

interface TaxExemptionCertificateFormData {
  id?: string;
  certificate_number: string;
  customer_id: string | null;
  customer_tax_id: string;
  customer_name: string;
  exemption_type: string;
  issuing_jurisdiction: string;
  issue_date: string;
  expiry_date: string;
  tax_codes: string[];
  notes: string;
  is_active: boolean;
  metadata?: Record<string, any>;
}

export default defineComponent({
  name: 'TaxExemptionCertificateForm',
  
  props: {
    certificate: {
      type: Object as () => TaxExemptionCertificateFormData | null,
      default: null,
    },
    loading: {
      type: Boolean,
      default: false,
    },
  },

  setup(props, { emit }) {
    const { showError } = useSnackbar();
    const { get } = useApi();
    
    const form = ref<any>(null);
    const valid = ref(false);
    const menuIssueDate = ref(false);
    const menuExpiryDate = ref(false);
    const loadingCustomers = ref(false);
    const customers = ref<Array<{id: string; name: string}>>([]);
    
    const exemptionTypes = [
      'GOVERNMENT',
      'NONPROFIT',
      'RESALE',
      'DIPLOMAT',
      'MANUFACTURING',
      'OTHER',
    ];
    
    const availableTaxCodes = [
      'VAT',
      'GST',
      'SALES_TAX',
      'USE_TAX',
      'DUTY',
      'EXCISE',
    ];
    
    const formData = ref<TaxExemptionCertificateFormData>({
      certificate_number: '',
      customer_id: null,
      customer_tax_id: '',
      customer_name: '',
      exemption_type: '',
      issuing_jurisdiction: '',
      issue_date: new Date().toISOString().substr(0, 10),
      expiry_date: new Date(new Date().setFullYear(new Date().getFullYear() + 1)).toISOString().substr(0, 10),
      tax_codes: [],
      notes: '',
      is_active: true,
    });
    
    const isEdit = ref(false);
    
    // Load initial data
    onMounted(async () => {
      if (props.certificate) {
        isEdit.value = true;
        formData.value = { ...props.certificate };
      }
      await searchCustomers('');
    });
    
    // Watch for changes in customer_id to update customer details
    watch(() => formData.value.customer_id, async (newVal) => {
      if (newVal) {
        const customer = customers.value.find(c => c.id === newVal);
        if (customer) {
          formData.value.customer_name = customer.name;
          // Optionally fetch customer details including tax ID
          // This would require an API call to get customer details
        }
      }
    });
    
    const searchCustomers = async (search: string) => {
      try {
        loadingCustomers.value = true;
        // This is a simplified example - adjust according to your API
        const response = await get('/api/customers', { 
          params: { search, limit: 10 } 
        });
        customers.value = response.data.results || [];
      } catch (error) {
        showError('Failed to load customers');
        console.error('Error loading customers:', error);
      } finally {
        loadingCustomers.value = false;
      }
    };
    
    const submit = () => {
      if (form.value.validate()) {
        emit('submit', formData.value);
      }
    };
    
    const reset = () => {
      form.value?.reset();
    };
    
    return {
      form,
      valid,
      formData,
      isEdit,
      menuIssueDate,
      menuExpiryDate,
      customers,
      loadingCustomers,
      exemptionTypes,
      availableTaxCodes,
      searchCustomers,
      submit,
      reset,
    };
  },
});
</script>
