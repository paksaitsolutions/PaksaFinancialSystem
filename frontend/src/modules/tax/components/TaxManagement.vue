<template>
  <div class="tax-management">
    <v-tabs v-model="activeTab" bg-color="primary">
      <v-tab value="rates">Tax Rates</v-tab>
      <v-tab value="exemptions">Exemptions</v-tab>
      <v-tab value="policies">Policies</v-tab>
      <v-tab value="calculator">Tax Calculator</v-tab>
      <v-tab value="reports">Reports</v-tab>
    </v-tabs>
    
    <v-window v-model="activeTab">
      <!-- Tax Rates -->
      <v-window-item value="rates">
        <v-card>
          <v-card-title class="d-flex align-center justify-space-between">
            <h3>Tax Rates</h3>
            <v-btn color="primary" prepend-icon="mdi-plus" @click="openTaxRateDialog">
              Add Tax Rate
            </v-btn>
          </v-card-title>
          
          <v-data-table
            :headers="taxRateHeaders"
            :items="taxRates"
            :loading="loadingRates"
            class="elevation-1"
          >
            <template v-slot:item.rate="{ item }">
              {{ (item.rate * 100).toFixed(2) }}%
            </template>
            
            <template v-slot:item.is_active="{ item }">
              <v-chip :color="item.is_active ? 'success' : 'error'" size="small">
                {{ item.is_active ? 'Active' : 'Inactive' }}
              </v-chip>
            </template>
            
            <template v-slot:item.actions="{ item }">
              <v-btn icon size="small" @click="editTaxRate(item)">
                <v-icon>mdi-pencil</v-icon>
              </v-btn>
            </template>
          </v-data-table>
        </v-card>
      </v-window-item>
      
      <!-- Tax Exemptions -->
      <v-window-item value="exemptions">
        <v-card>
          <v-card-title class="d-flex align-center justify-space-between">
            <h3>Tax Exemptions</h3>
            <v-btn color="primary" prepend-icon="mdi-plus" @click="openExemptionDialog">
              Add Exemption
            </v-btn>
          </v-card-title>
          
          <v-data-table
            :headers="exemptionHeaders"
            :items="exemptions"
            :loading="loadingExemptions"
            class="elevation-1"
          >
            <template v-slot:item.is_active="{ item }">
              <v-chip :color="item.is_active ? 'success' : 'error'" size="small">
                {{ item.is_active ? 'Active' : 'Inactive' }}
              </v-chip>
            </template>
            
            <template v-slot:item.actions="{ item }">
              <v-btn icon size="small" @click="editExemption(item)">
                <v-icon>mdi-pencil</v-icon>
              </v-btn>
            </template>
          </v-data-table>
        </v-card>
      </v-window-item>
      
      <!-- Tax Calculator -->
      <v-window-item value="calculator">
        <v-card>
          <v-card-title>Tax Calculator</v-card-title>
          <v-card-text>
            <v-form @submit.prevent="calculateTax">
              <v-row>
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="calculator.amount"
                    label="Amount"
                    type="number"
                    step="0.01"
                    prepend-inner-icon="mdi-currency-usd"
                    required
                  ></v-text-field>
                </v-col>
                
                <v-col cols="12" md="6">
                  <v-select
                    v-model="calculator.tax_type"
                    label="Tax Type"
                    :items="taxTypes"
                    required
                  ></v-select>
                </v-col>
                
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="calculator.jurisdiction"
                    label="Jurisdiction (Optional)"
                  ></v-text-field>
                </v-col>
                
                <v-col cols="12" md="6">
                  <v-btn
                    color="primary"
                    :loading="calculatingTax"
                    @click="calculateTax"
                  >
                    Calculate Tax
                  </v-btn>
                </v-col>
              </v-row>
            </v-form>
            
            <div v-if="taxResult" class="mt-6">
              <v-card variant="outlined">
                <v-card-title>Tax Calculation Result</v-card-title>
                <v-card-text>
                  <v-row>
                    <v-col cols="12" md="4">
                      <div class="text-center">
                        <div class="text-h6">{{ formatCurrency(taxResult.subtotal) }}</div>
                        <div class="text-caption">Subtotal</div>
                      </div>
                    </v-col>
                    <v-col cols="12" md="4">
                      <div class="text-center">
                        <div class="text-h6">{{ formatCurrency(taxResult.tax_amount) }}</div>
                        <div class="text-caption">Tax Amount</div>
                      </div>
                    </v-col>
                    <v-col cols="12" md="4">
                      <div class="text-center">
                        <div class="text-h6">{{ formatCurrency(taxResult.total_amount) }}</div>
                        <div class="text-caption">Total Amount</div>
                      </div>
                    </v-col>
                  </v-row>
                  
                  <div v-if="taxResult.tax_details.length > 0" class="mt-4">
                    <h4>Tax Breakdown:</h4>
                    <div
                      v-for="detail in taxResult.tax_details"
                      :key="detail.tax_rate_id"
                      class="d-flex justify-space-between mt-2"
                    >
                      <span>{{ detail.name }} ({{ (detail.rate * 100).toFixed(2) }}%)</span>
                      <span>{{ formatCurrency(detail.amount) }}</span>
                    </div>
                  </div>
                </v-card-text>
              </v-card>
            </div>
          </v-card-text>
        </v-card>
      </v-window-item>
      
      <!-- Reports -->
      <v-window-item value="reports">
        <v-card>
          <v-card-title>Tax Reports</v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="12" md="4">
                <v-btn color="primary" block prepend-icon="mdi-file-chart">
                  Tax Summary Report
                </v-btn>
              </v-col>
              <v-col cols="12" md="4">
                <v-btn color="secondary" block prepend-icon="mdi-file-table">
                  Tax Rate Analysis
                </v-btn>
              </v-col>
              <v-col cols="12" md="4">
                <v-btn color="info" block prepend-icon="mdi-certificate">
                  Exemption Report
                </v-btn>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-window-item>
    </v-window>
    
    <!-- Tax Rate Dialog -->
    <v-dialog v-model="taxRateDialog.show" max-width="600px">
      <v-card>
        <v-card-title>{{ taxRateDialog.isEdit ? 'Edit' : 'Add' }} Tax Rate</v-card-title>
        <v-card-text>
          <v-form ref="taxRateForm" v-model="taxRateDialog.valid">
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="taxRateDialog.formData.name"
                  label="Name*"
                  :rules="[v => !!v || 'Name is required']"
                  required
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="taxRateDialog.formData.code"
                  label="Code*"
                  :rules="[v => !!v || 'Code is required']"
                  required
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="taxRateDialog.formData.rate"
                  label="Rate (%)*"
                  type="number"
                  step="0.0001"
                  :rules="[v => !!v || 'Rate is required']"
                  required
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-select
                  v-model="taxRateDialog.formData.tax_type"
                  label="Tax Type*"
                  :items="taxTypes"
                  :rules="[v => !!v || 'Tax type is required']"
                  required
                ></v-select>
              </v-col>
              <v-col cols="12">
                <v-text-field
                  v-model="taxRateDialog.formData.jurisdiction"
                  label="Jurisdiction"
                ></v-text-field>
              </v-col>
              <v-col cols="12">
                <v-textarea
                  v-model="taxRateDialog.formData.description"
                  label="Description"
                  rows="2"
                ></v-textarea>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="taxRateDialog.show = false">Cancel</v-btn>
          <v-btn
            color="primary"
            :loading="taxRateDialog.saving"
            :disabled="!taxRateDialog.valid"
            @click="saveTaxRate"
          >
            {{ taxRateDialog.isEdit ? 'Update' : 'Create' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { useSnackbar } from '@/composables/useSnackbar';
import { formatCurrency } from '@/utils/formatters';
import { apiClient } from '@/utils/apiClient';

// Composables
const { showSnackbar } = useSnackbar();

// Data
const activeTab = ref('rates');
const taxRates = ref([]);
const exemptions = ref([]);
const loadingRates = ref(false);
const loadingExemptions = ref(false);
const calculatingTax = ref(false);
const taxResult = ref(null);

// Tax Rate Dialog
const taxRateDialog = reactive({
  show: false,
  isEdit: false,
  valid: false,
  saving: false,
  formData: {
    name: '',
    code: '',
    rate: 0,
    tax_type: '',
    jurisdiction: '',
    description: '',
  },
  editId: null,
});

// Calculator
const calculator = reactive({
  amount: 0,
  tax_type: '',
  jurisdiction: '',
});

// Headers
const taxRateHeaders = [
  { title: 'Name', key: 'name', sortable: true },
  { title: 'Code', key: 'code', sortable: true },
  { title: 'Rate', key: 'rate', sortable: true },
  { title: 'Type', key: 'tax_type', sortable: true },
  { title: 'Jurisdiction', key: 'jurisdiction', sortable: true },
  { title: 'Status', key: 'is_active', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false },
];

const exemptionHeaders = [
  { title: 'Certificate #', key: 'certificate_number', sortable: true },
  { title: 'Type', key: 'exemption_type', sortable: true },
  { title: 'Tax Type', key: 'tax_type', sortable: true },
  { title: 'Status', key: 'is_active', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false },
];

const taxTypes = [
  { title: 'Sales Tax', value: 'sales' },
  { title: 'VAT', value: 'vat' },
  { title: 'GST', value: 'gst' },
  { title: 'Income Tax', value: 'income' },
];

// Methods
const fetchTaxRates = async () => {
  loadingRates.value = true;
  try {
    const response = await apiClient.get('/api/v1/tax/rates');
    taxRates.value = response.data;
  } catch (error) {
    showSnackbar('Failed to load tax rates', 'error');
  } finally {
    loadingRates.value = false;
  }
};

const fetchExemptions = async () => {
  loadingExemptions.value = true;
  try {
    const response = await apiClient.get('/api/v1/tax/exemptions');
    exemptions.value = response.data;
  } catch (error) {
    showSnackbar('Failed to load exemptions', 'error');
  } finally {
    loadingExemptions.value = false;
  }
};

const openTaxRateDialog = () => {
  taxRateDialog.isEdit = false;
  taxRateDialog.editId = null;
  taxRateDialog.formData = {
    name: '',
    code: '',
    rate: 0,
    tax_type: '',
    jurisdiction: '',
    description: '',
  };
  taxRateDialog.show = true;
};

const editTaxRate = (taxRate) => {
  taxRateDialog.isEdit = true;
  taxRateDialog.editId = taxRate.id;
  taxRateDialog.formData = {
    name: taxRate.name,
    code: taxRate.code,
    rate: taxRate.rate * 100, // Convert to percentage
    tax_type: taxRate.tax_type,
    jurisdiction: taxRate.jurisdiction || '',
    description: taxRate.description || '',
  };
  taxRateDialog.show = true;
};

const saveTaxRate = async () => {
  if (!taxRateDialog.valid) return;
  
  taxRateDialog.saving = true;
  try {
    const payload = {
      ...taxRateDialog.formData,
      rate: taxRateDialog.formData.rate / 100, // Convert back to decimal
      effective_date: new Date().toISOString().split('T')[0],
    };
    
    if (taxRateDialog.isEdit) {
      await apiClient.put(`/api/v1/tax/rates/${taxRateDialog.editId}`, payload);
      showSnackbar('Tax rate updated successfully', 'success');
    } else {
      await apiClient.post('/api/v1/tax/rates', payload);
      showSnackbar('Tax rate created successfully', 'success');
    }
    
    taxRateDialog.show = false;
    fetchTaxRates();
  } catch (error) {
    showSnackbar('Failed to save tax rate', 'error');
  } finally {
    taxRateDialog.saving = false;
  }
};

const calculateTax = async () => {
  if (!calculator.amount || !calculator.tax_type) return;
  
  calculatingTax.value = true;
  try {
    const response = await apiClient.post('/api/v1/tax/calculate', calculator);
    taxResult.value = response.data;
  } catch (error) {
    showSnackbar('Failed to calculate tax', 'error');
  } finally {
    calculatingTax.value = false;
  }
};

const openExemptionDialog = () => {
  showSnackbar('Exemption management coming soon', 'info');
};

const editExemption = () => {
  showSnackbar('Exemption editing coming soon', 'info');
};

// Lifecycle hooks
onMounted(() => {
  fetchTaxRates();
  fetchExemptions();
});
</script>

<style scoped>
.tax-management {
  padding: 16px;
}
</style>