<template>
  <v-form ref="form" v-model="valid" @submit.prevent="submit">
    <v-card flat>
      <v-card-title class="text-h6 primary--text">
        <v-icon left color="primary">mdi-certificate</v-icon>
        {{ isEdit ? 'Edit' : 'Add New' }} Tax Exemption Certificate
      </v-card-title>
      
      <v-card-text>
        <v-container class="px-0" fluid>
          <v-alert
            v-if="error"
            type="error"
            class="mb-4"
            dense
            outlined
            dismissible
            @input="error = ''"
          >
            {{ error }}
          </v-alert>
          
          <v-row>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="formData.certificate_number"
                :rules="[
                  v => !!v || 'Certificate number is required',
                  v => !v || v.length <= 50 || 'Max 50 characters',
                  validateCertificateNumber
                ]"
                label="Certificate Number *"
                required
                outlined
                dense
                :disabled="loading"
                :loading="loading && !formData.certificate_number"
                hint="Enter the official certificate number"
                persistent-hint
              />
            </v-col>
            
            <v-col cols="12" md="6">
              <v-autocomplete
                v-model="formData.customer_id"
                :items="filteredCustomers"
                item-text="display_name"
                item-value="id"
                :rules="[v => !!v || 'Customer is required']"
                label="Customer *"
                required
                outlined
                dense
                clearable
                :loading="loadingCustomers"
                :search-input.sync="customerSearch"
                :filter="filterCustomers"
                :disabled="loading"
                return-object
                @update:search-input="searchCustomers"
                @change="onCustomerSelect"
              >
                <template v-slot:item="{ item }">
                  <v-list-item-content>
                    <v-list-item-title>{{ item.name }}</v-list-item-title>
                    <v-list-item-subtitle v-if="item.tax_id">
                      Tax ID: {{ item.tax_id }}
                    </v-list-item-subtitle>
                    <v-list-item-subtitle v-if="item.email">
                      {{ item.email }}
                    </v-list-item-subtitle>
                  </v-list-item-content>
                </template>
              </v-autocomplete>
            </v-col>
            
            <v-col cols="12" md="6">
              <v-text-field
                v-model="formData.customer_tax_id"
                label="Customer Tax ID"
                outlined
                dense
                :disabled="loading"
                :rules="[v => !v || validateTaxId(v) === true || validateTaxId(v)]"
                hint="Enter the customer's tax identification number"
                persistent-hint
                :loading="loading && !formData.customer_tax_id"
                :error-messages="formData.customer_tax_id && validateTaxId(formData.customer_tax_id) !== true ? [validateTaxId(formData.customer_tax_id)] : []"
              >
                <template v-slot:append-outer v-if="formData.customer_tax_id">
                  <v-tooltip bottom>
                    <template v-slot:activator="{ on, attrs }">
                      <v-icon
                        v-bind="attrs"
                        v-on="on"
                        :color="validateTaxId(formData.customer_tax_id) === true ? 'success' : 'error'"
                        small
                      >
                        {{ validateTaxId(formData.customer_tax_id) === true ? 'mdi-check-circle' : 'mdi-alert-circle' }}
                      </v-icon>
                    </template>
                    <span>{{ validateTaxId(formData.customer_tax_id) === true ? 'Valid tax ID format' : validateTaxId(formData.customer_tax_id) }}</span>
                  </v-tooltip>
                </template>
              </v-text-field>
            </v-col>
            
            <v-col cols="12" md="6">
              <v-text-field
                v-model="formData.customer_name"
                label="Customer Name"
                outlined
                dense
                :disabled="loading"
                :rules="[v => !v || v.length <= 100 || 'Max 100 characters']"
              />
            </v-col>
            
            <v-col cols="12" md="6">
              <v-select
                v-model="formData.exemption_type"
                :items="exemptionTypes"
                :rules="[v => !!v || 'Exemption type is required']"
                label="Exemption Type *"
                required
                outlined
                dense
                :disabled="loading"
                :loading="loading && !formData.exemption_type"
                item-text="name"
                item-value="code"
                :hint="getExemptionTypeHint(formData.exemption_type)"
                persistent-hint
              >
                <template v-slot:item="{ item }">
                  <v-list-item-content>
                    <v-list-item-title>{{ item.name }}</v-list-item-title>
                    <v-list-item-subtitle v-if="item.description" class="text-caption">
                      {{ item.description }}
                    </v-list-item-subtitle>
                  </v-list-item-content>
                </template>
              </v-select>
            </v-col>
            
            <v-col cols="12" md="6">
              <v-autocomplete
                v-model="formData.issuing_jurisdiction"
                :items="jurisdictions"
                :loading="loadingJurisdictions"
                :search-input.sync="jurisdictionSearch"
                label="Issuing Jurisdiction"
                outlined
                dense
                :disabled="loading"
                :rules="[v => !v || v.length <= 100 || 'Max 100 characters']"
                hint="Country/State/Province that issued the certificate"
                persistent-hint
                clearable
                cache-items
                :filter="filterJurisdictions"
                @update:search-input="searchJurisdictions"
              >
                <template v-slot:no-data>
                  <v-list-item>
                    <v-list-item-title>
                      Press enter to add "<strong>{{ jurisdictionSearch }}"</strong>
                    </v-list-item-title>
                  </v-list-item>
                </template>
              </v-autocomplete>
            </v-col>
            
            <v-col cols="12" md="6">
              <v-menu
                v-model="menuIssueDate"
                :close-on-content-click="false"
                :nudge-right="40"
                transition="scale-transition"
                offset-y
                min-width="auto"
                :disabled="loading"
              >
                <template v-slot:activator="{ on, attrs }">
                  <v-text-field
                    v-model="formattedIssueDate"
                    label="Issue Date *"
                    prepend-icon="mdi-calendar"
                    readonly
                    v-bind="attrs"
                    v-on="on"
                    outlined
                    dense
                    :disabled="loading"
                    :rules="[v => !!v || 'Issue date is required', validateIssueDate]"
                    hint="Date when the certificate was issued"
                    persistent-hint
                  />
                </template>
                <v-date-picker
                  v-model="formData.issue_date"
                  @input="menuIssueDate = false"
                  :max="new Date().toISOString().substr(0, 10)"
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
                :disabled="loading"
              >
                <template v-slot:activator="{ on, attrs }">
                  <v-text-field
                    v-model="formattedExpiryDate"
                    label="Expiry Date *"
                    prepend-icon="mdi-calendar"
                    readonly
                    v-bind="attrs"
                    v-on="on"
                    outlined
                    dense
                    :disabled="loading"
                    :rules="[v => !!v || 'Expiry date is required', validateExpiryDate]"
                    hint="Date when the certificate expires"
                    persistent-hint
                  />
                </template>
                <v-date-picker
                  v-model="formData.expiry_date"
                  :min="formData.issue_date || new Date().toISOString().substr(0, 10)"
                  @input="menuExpiryDate = false"
                />
              </v-menu>
            </v-col>
            
            <v-col cols="12">
              <v-combobox
                v-model="formData.tax_codes"
                :items="availableTaxCodes"
                label="Applicable Tax Codes *"
                multiple
                chips
                small-chips
                outlined
                dense
                :disabled="loading"
                :loading="loadingTaxCodes"
                :rules="[v => v && v.length > 0 || 'At least one tax code is required']"
                :hint="`Selected: ${formData.tax_codes ? formData.tax_codes.length : 0} tax codes`"
                persistent-hint
                :search-input.sync="taxCodeSearch"
                @update:search-input="searchTaxCodes"
              >
                <template v-slot:selection="{ item, index, selected, disabled }" v-if="typeof item === 'object'">
                  <v-chip
                    :key="item.code"
                    :color="item.is_active ? 'primary' : 'grey lighten-1'"
                    :text-color="item.is_active ? 'white' : 'white'"
                    small
                    close
                    @click:close="removeTaxCode(index)"
                  >
                    <v-avatar left v-if="!item.is_active">
                      <v-icon small>mdi-alert-circle</v-icon>
                    </v-avatar>
                    {{ item.code }}: {{ item.name }}
                  </v-chip>
                </template>
                <template v-slot:item="{ item }" v-if="typeof item === 'object'">
                  <v-list-item-content>
                    <v-list-item-title>{{ item.code }}: {{ item.name }}</v-list-item-title>
                    <v-list-item-subtitle class="text-caption">
                      {{ item.rate }}% • {{ item.description || 'No description' }}
                      <v-chip v-if="!item.is_active" x-small color="error" text-color="white" class="ml-2">
                        Inactive
                      </v-chip>
                    </v-list-item-subtitle>
                  </v-list-item-content>
                </template>
              </v-combobox>
            </v-col>
            
            <v-col cols="12">
              <v-textarea
                v-model="formData.notes"
                label="Notes"
                outlined
                dense
                rows="2"
                counter="1000"
                :disabled="loading"
                :rules="[v => !v || v.length <= 1000 || 'Notes must be less than 1000 characters']"
                hint="Additional information about this certificate"
                persistent-hint
              />
            </v-col>
            
            <v-col cols="12">
              <v-switch
                v-model="formData.is_active"
                label="Certificate is active"
                color="primary"
                :disabled="loading"
                :hint="formData.is_active ? 'This certificate is currently active and will be applied to transactions' : 'This certificate is inactive and will not be applied to transactions'"
                persistent-hint
              />
            </v-col>
          </v-row>
        </v-container>
      </v-card-text>
      
      <v-card-actions class="px-4 pb-4">
        <v-spacer />
        <v-btn
          color="grey darken-1"
          text
          @click="$emit('cancel')"
          :disabled="loading"
          :loading="loading && loadingType === 'cancel'"
          class="text-capitalize"
        >
          <v-icon left>mdi-close</v-icon>
          Cancel
        </v-btn>
        <v-btn
          color="primary"
          type="submit"
          :loading="loading"
          :disabled="!valid || loading"
          :class="{ 'primary--text': !valid }"
          class="text-capitalize"
          elevation="0"
        >
          <v-icon left>{{ isEdit ? 'mdi-content-save' : 'mdi-plus' }}</v-icon>
          {{ isEdit ? 'Update' : 'Save' }} Certificate
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-form>
</template>

<script lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useRouter } from 'vue-router';
import { get, post, put } from '@/utils/api';
import { formatDate, parseDate } from '@/utils/dateUtils';
import { debounce } from 'lodash';

// Simple snackbar implementation to avoid module import errors
const useSnackbar = () => {
  const showMessage = (options: { text: string; color?: string; timeout?: number }) => {
    console.log(`[Snackbar] ${options.text}`, options);
  };
  
  const showError = (message: string) => {
    console.error(`[Error] ${message}`);
    showMessage({ text: message, color: 'error' });
  };
  
  return { showMessage, showError };
};

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
  metadata?: Record<string, unknown>;
}

interface Customer {
  id: string;
  name: string;
  tax_id?: string;
  email?: string;
  display_name?: string;
}

interface TaxCode {
  code: string;
  name: string;
  rate: number;
  description: string;
  is_active: boolean;
}

type ValidationRule = (v: any) => boolean | string;

export default defineComponent({
  name: 'TaxExemptionCertificateForm',
  
  props: {
    certificate: {
      type: Object as PropType<TaxExemptionCertificateFormData | null>,
      default: null
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  
  emits: ['submit', 'cancel', 'update:loading'],
  
  setup(props, { emit }) {
    // Define reactive references
    const form = ref<HTMLFormElement | null>(null);
    const { showError } = useSnackbar();
    const router = useRouter();
    
    const form = ref<any>(null);
    const valid = ref(false);
    const menuIssueDate = ref(false);
    const menuExpiryDate = ref(false);
    const loadingCustomers = ref(false);
    const customers = ref<Customer[]>([]);
    const customerSearch = ref('');
    const jurisdictions = ref<string[]>([]);
    const loadingJurisdictions = ref(false);
    const jurisdictionSearch = ref('');
    const availableTaxCodes = ref<TaxCode[]>([]);
    const loadingTaxCodes = ref(false);
    const taxCodeSearch = ref('');
    const error = ref('');
    
    const exemptionTypes = [
      'GOVERNMENT',
      'NONPROFIT',
      'RESALE',
      'DIPLOMAT',
      'MANUFACTURING',
      'OTHER',
    ];
    
    const initialFormData: TaxExemptionCertificateFormData = {
      certificate_number: '',
      customer_id: null,
      customer_tax_id: '',
      customer_name: '',
      exemption_type: '',
      issuing_jurisdiction: '',
      issue_date: new Date().toISOString().split('T')[0],
      expiry_date: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      tax_codes: [],
      notes: '',
      is_active: true
    };
    
    const formData = ref<TaxExemptionCertificateFormData>({ ...initialFormData });
    
    const isEdit = ref(false);
    
    // Get help text for exemption types
    const getExemptionTypeHint = (type: string): string => {
      const typeMap: Record<string, string> = {
        'GOVERNMENT': 'For government entities',
        'NONPROFIT': 'For registered non-profit organizations',
        'RESALE': 'For items purchased for resale',
        'DIPLOMAT': 'For diplomatic missions',
        'MANUFACTURING': 'For manufacturing inputs',
        'OTHER': 'Other exemption types'
      };
      return type ? (typeMap[type] || 'Select an exemption type') : 'Select an exemption type';
    };
    
    // Validate certificate number format
    const validateCertificateNumber = (value: string): boolean | string => {
      if (!value) return 'Certificate number is required';
      if (value.length < 6) return 'Certificate number must be at least 6 characters';
      if (!/^[A-Z0-9\-\s]+$/i.test(value)) return 'Only letters, numbers, and hyphens are allowed';
      return true;
    };
    
    // Validate tax ID format
    const validateTaxId = (value: string): boolean | string => {
      if (!value) return 'Tax ID is required';
      if (!/^[A-Z0-9\-\s]+$/i.test(value)) return 'Invalid tax ID format';
      return true;
    };
    
    // Validate that expiry date is after issue date
    const validateDateRange = (issueDate: string | undefined, expiryDate: string | undefined): boolean | string => {
      if (!issueDate || !expiryDate) return 'Both issue and expiry dates are required';
      const issue = new Date(issueDate);
      const expiry = new Date(expiryDate);
      return expiry > issue ? true : 'Expiry date must be after issue date';
    };
    
    // Handle customer selection from autocomplete
    const onCustomerSelect = (customer: Customer) => {
      if (customer) {
        formData.value.customer_name = customer.name;
        formData.value.customer_tax_id = customer.tax_id || '';
      }
    };
    
    // Remove a tax code from the selected list
    const removeTaxCode = (index: number): void => {
      const newTaxCodes = [...formData.value.tax_codes];
      newTaxCodes.splice(index, 1);
      formData.value.tax_codes = newTaxCodes;
    };
    
    // Filter jurisdictions in autocomplete
    const filterJurisdictions = (item: string, queryText: string): boolean => {
      if (!queryText) return true;
      return item.toLowerCase().includes(queryText.toLowerCase());
    };
    
    // Used in v-autocomplete for customer search
    const filterCustomers = (item: Customer, queryText: string): boolean => {
      if (!queryText) return true;
      const searchText = queryText.toLowerCase();
      return (
        item.name.toLowerCase().includes(searchText) ||
        (item.email && item.email.toLowerCase().includes(searchText)) ||
        (item.tax_id && item.tax_id.toLowerCase().includes(searchText))
      );
    };
    
    // Filter tax codes in autocomplete
    const filterTaxCodes = (item: TaxCode, queryText: string): boolean => {
      if (!queryText) return true;
      const searchText = queryText.toLowerCase();
      return (
        item.code.toLowerCase().includes(searchText) ||
        (item.name && item.name.toLowerCase().includes(searchText)) ||
        (item.description && item.description.toLowerCase().includes(searchText))
      );
    };
    
    // Search for customers by name or tax ID
    const searchCustomers = async (search: string) => {
      try {
        loadingCustomers.value = true;
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
    
    // Load tax codes from API
    const loadTaxCodes = async (search = ''): Promise<void> => {
      try {
        loadingTaxCodes.value = true;
        const response = await get('/api/tax/codes', { 
          params: { 
            search, 
            limit: 100,
            active: true // Only load active tax codes by default
          } 
        });
        availableTaxCodes.value = response.data?.items || [];
      } catch (error) {
        console.error('Error loading tax codes:', error);
        const errorMessage = error instanceof Error ? error.message : 'Failed to load tax codes';
        showError(errorMessage);
      } finally {
        loadingTaxCodes.value = false;
      }
    };
    
    // Load jurisdictions from API
    const loadJurisdictions = async (search = ''): Promise<void> => {
      try {
        loadingJurisdictions.value = true;
        const response = await get('/api/tax/jurisdictions', { 
          params: { 
            search, 
            limit: 100,
            active: true // Only load active jurisdictions by default
          } 
        });
        jurisdictions.value = response.data?.items || [];
      } catch (error) {
        console.error('Error loading jurisdictions:', error);
        const errorMessage = error instanceof Error ? error.message : 'Failed to load jurisdictions';
        showError(errorMessage);
      } finally {
        loadingJurisdictions.value = false;
      }
    };
    
    // Handle form submission
    const submit = async (): Promise<void> => {
      if (!form.value) {
        showError('Form reference is not available');
        return;
      }

      // Validate form
      const { valid } = await form.value.validate();
      if (!valid) {
        return;
      }

      try {
        emit('update:loading', true);
        
        // Format dates if needed
        const payload = {
          ...formData.value,
          issue_date: formData.value.issue_date ? formatDate(formData.value.issue_date) : null,
          expiry_date: formData.value.expiry_date ? formatDate(formData.value.expiry_date) : null
        };

        let response;
        if (isEdit.value && formData.value.id) {
          response = await put(`/api/tax/exemptions/${formData.value.id}`, payload);
        } else {
          response = await post('/api/tax/exemptions', payload);
        }

        emit('submit', response.data);
        showError({ text: `Certificate ${isEdit.value ? 'updated' : 'created'} successfully` });
        
        if (!isEdit.value) {
          resetForm();
        }
      } catch (error) {
        console.error('Error saving tax exemption certificate:', error);
        const errorMessage = error instanceof Error ? error.message : 'Failed to save certificate';
        showError(errorMessage);
      } finally {
        emit('update:loading', false);
      }
    };
    
    // Reset form to initial state
    const resetForm = (): void => {
      if (form.value) {
        form.value.reset();
        formData.value = { ...initialFormData };
      }
    };
    
    // Debounced search for tax codes
    const searchTaxCodes = debounce((search: string) => {
      if (search && search.length >= 2) {
        loadTaxCodes(search);
      } else if (!search) {
        // Reload with empty search to reset the list
        loadTaxCodes('');
      }
    }, 300);
    
    // Debounced search for jurisdictions
    const searchJurisdictions = debounce((search: string) => {
      if (search && search.length >= 2) {
        loadJurisdictions(search);
      } else if (!search) {
        // Reload with empty search to reset the list
        loadJurisdictions('');
      }
    }, 300);
    
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
