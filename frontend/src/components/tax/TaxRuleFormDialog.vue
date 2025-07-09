<template>
  <v-dialog
    v-model="dialog"
    max-width="800"
    persistent
    scrollable
  >
    <v-card>
      <v-toolbar
        :title="isEditing ? 'Edit Tax Rule' : 'Create New Tax Rule'"
        color="primary"
        density="comfortable"
      >
        <v-btn
          icon
          @click="closeDialog"
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-toolbar>

      <v-card-text class="pa-6">
        <v-form ref="form" v-model="isFormValid" @submit.prevent="save">
          <v-row>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="formData.code"
                label="Code *"
                :rules="[v => !!v || 'Code is required']"
                variant="outlined"
                density="comfortable"
                class="mb-4"
              />
            </v-col>
            <v-col cols="12" md="6">
              <v-select
                v-model="formData.type"
                :items="taxTypes"
                item-title="name"
                item-value="type"
                label="Tax Type *"
                :rules="[v => !!v || 'Tax type is required']"
                variant="outlined"
                density="comfortable"
                class="mb-4"
                @update:model-value="onTaxTypeChange"
              />
            </v-col>

            <v-col cols="12" md="6">
              <v-text-field
                v-model="formData.name"
                label="Name *"
                :rules="[v => !!v || 'Name is required']"
                variant="outlined"
                density="comfortable"
                class="mb-4"
              />
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="formData.category"
                label="Category"
                variant="outlined"
                density="comfortable"
                class="mb-4"
                :hint="categoryHint"
                persistent-hint
              />
            </v-col>

            <v-col cols="12">
              <v-textarea
                v-model="formData.description"
                label="Description"
                variant="outlined"
                rows="2"
                auto-grow
                class="mb-4"
              />
            </v-col>

            <v-col cols="12">
              <v-divider class="my-4" />
              <h3 class="text-h6 mb-4">Jurisdiction</h3>
            </v-col>

            <v-col cols="12" md="6">
              <v-select
                v-model="formData.jurisdiction.countryCode"
                :items="countries"
                item-title="name"
                item-value="code"
                label="Country *"
                :rules="[v => !!v || 'Country is required']"
                variant="outlined"
                density="comfortable"
                class="mb-4"
                @update:model-value="onCountryChange"
              />
            </v-col>
            <v-col v-if="hasStates" cols="12" md="6">
              <v-select
                v-model="formData.jurisdiction.stateCode"
                :items="filteredStates"
                item-title="name"
                item-value="code"
                label="State/Region"
                variant="outlined"
                density="comfortable"
                class="mb-4"
                clearable
              />
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="formData.jurisdiction.city"
                label="City"
                variant="outlined"
                density="comfortable"
                class="mb-4"
              />
            </v-col>
            <v-col cols="12" md="6">
              <v-checkbox
                v-model="formData.jurisdiction.isEu"
                label="EU Member State"
                color="primary"
                hide-details
                class="mt-0"
              />
            </v-col>

            <v-col cols="12">
              <v-divider class="my-4" />
              <div class="d-flex justify-space-between align-center mb-4">
                <h3 class="text-h6 mb-0">Tax Rates</h3>
                <v-btn
                  color="primary"
                  variant="tonal"
                  size="small"
                  prepend-icon="mdi-plus"
                  @click="addRate"
                >
                  Add Rate
                </v-btn>
              </div>

              <v-table density="comfortable" class="elevation-1 mb-4">
                <thead>
                  <tr>
                    <th>Rate (%) *</th>
                    <th>Effective From *</th>
                    <th>Effective To</th>
                    <th>Description</th>
                    <th>Standard</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(rate, index) in formData.rates" :key="index">
                    <td>
                      <v-text-field
                        v-model.number="rate.rate"
                        type="number"
                        step="0.01"
                        min="0"
                        max="100"
                        variant="underlined"
                        density="compact"
                        hide-details
                        :rules="[v => v !== null && v >= 0 && v <= 100 || 'Valid rate required']"
                        @update:model-value="onRateChange(index)"
                      >
                        <template #append>
                          <span class="text-caption">%</span>
                        </template>
                      </v-text-field>
                    </td>
                    <td>
                      <v-text-field
                        v-model="rate.effectiveFrom"
                        type="date"
                        variant="underlined"
                        density="compact"
                        hide-details
                        :rules="[v => !!v || 'Required']"
                      />
                    </td>
                    <td>
                      <v-text-field
                        v-model="rate.effectiveTo"
                        type="date"
                        variant="underlined"
                        density="compact"
                        hide-details
                        :min="rate.effectiveFrom"
                      />
                    </td>
                    <td>
                      <v-text-field
                        v-model="rate.description"
                        variant="underlined"
                        density="compact"
                        hide-details
                        placeholder="e.g., Standard rate"
                      />
                    </td>
                    <td class="text-center">
                      <v-checkbox
                        v-model="rate.isStandardRate"
                        color="primary"
                        hide-details
                        :true-value="true"
                        :false-value="false"
                        @change="onStandardRateChange(index)"
                      />
                    </td>
                    <td class="text-center">
                      <v-btn
                        icon
                        variant="text"
                        size="small"
                        color="error"
                        :disabled="formData.rates.length <= 1"
                        @click="removeRate(index)"
                      >
                        <v-icon>mdi-delete</v-icon>
                        <v-tooltip activator="parent" location="top">Remove Rate</v-tooltip>
                      </v-btn>
                    </td>
                  </tr>
                </tbody>
              </v-table>
            </v-col>

            <v-col cols="12">
              <v-divider class="my-4" />
              <h3 class="text-h6 mb-4">Advanced Settings</h3>
            </v-col>

            <v-col cols="12" md="6">
              <v-switch
                v-model="formData.isActive"
                color="primary"
                label="Active"
                hide-details
                class="mt-0"
              />
            </v-col>
            <v-col cols="12" md="6">
              <v-switch
                v-model="formData.requiresTaxId"
                color="primary"
                label="Requires Tax ID"
                hide-details
                class="mt-0"
              />
            </v-col>

            <v-col v-if="formData.requiresTaxId" cols="12" md="6">
              <v-text-field
                v-model="formData.taxIdFormat"
                label="Tax ID Format (Regex)"
                variant="outlined"
                density="comfortable"
                placeholder="^[A-Z]{2}\\d{2}[A-Z0-9]{8,10}$"
                hint="Regular expression pattern for validating tax IDs"
                persistent-hint
              />
            </v-col>
            <v-col v-if="formData.requiresTaxId" cols="12" md="6">
              <v-text-field
                v-model="formData.taxIdValidationRegex"
                label="Tax ID Validation Regex"
                variant="outlined"
                density="comfortable"
                placeholder="^[A-Z]{2}\\d{2}[A-Z0-9]{8,10}$"
                hint="Regular expression pattern for validating tax IDs"
                persistent-hint
              />
            </v-col>

            <v-col cols="12" md="6">
              <v-text-field
                v-model="formData.accountingCode"
                label="Accounting Code"
                variant="outlined"
                density="comfortable"
                hint="Code used in accounting entries"
                persistent-hint
              />
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="formData.glAccountCode"
                label="GL Account Code"
                variant="outlined"
                density="comfortable"
                hint="General ledger account code for this tax"
                persistent-hint
              />
            </v-col>

            <v-col cols="12">
              <v-combobox
                v-model="formData.tags"
                label="Tags"
                variant="outlined"
                density="comfortable"
                multiple
                chips
                closable-chips
                hint="Add tags to categorize this tax rule"
                persistent-hint
              />
            </v-col>
          </v-row>
        </v-form>
      </v-card-text>

      <v-card-actions class="pa-4">
        <v-spacer />
        <v-btn
          variant="text"
          @click="closeDialog"
        >
          Cancel
        </v-btn>
        <v-btn
          color="primary"
          :loading="saving"
          @click="save"
        >
          {{ isEditing ? 'Update' : 'Create' }} Tax Rule
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts" setup>
import { ref, computed, watch, onMounted } from 'vue';
import { useToast } from 'vue-toastification';
import type { TaxRule, TaxType, TaxRuleFormData } from '@/types/tax';
import { taxPolicyService } from '@/services/taxPolicyService';

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true,
  },
  taxRule: {
    type: Object as () => TaxRule | null,
    default: null,
  },
  countries: {
    type: Array as () => Array<{ code: string; name: string }>,
    default: () => [],
  },
  states: {
    type: Array as () => Array<{ code: string; name: string }>,
    default: () => [],
  },
  taxTypes: {
    type: Array as () => Array<{ type: string; name: string }>,
    default: () => [],
  },
});

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
  (e: 'saved', rule: TaxRule): void;
  (e: 'closed'): void;
}>();

const toast = useToast();
const form = ref<HTMLFormElement | null>(null);
const isFormValid = ref(false);
const saving = ref(false);

// Form data with defaults
const formData = ref<TaxRuleFormData>({
  code: '',
  name: '',
  description: '',
  type: 'sales',
  jurisdiction: {
    countryCode: '',
    stateCode: '',
    city: '',
    isEu: false,
  },
  rates: [
    {
      rate: 0,
      effectiveFrom: new Date().toISOString().split('T')[0],
      effectiveTo: undefined,
      description: 'Standard rate',
      isStandardRate: true,
    },
  ],
  category: '',
  isActive: true,
  requiresTaxId: false,
  taxIdFormat: '',
  taxIdValidationRegex: '',
  accountingCode: '',
  glAccountCode: '',
  tags: [],
  metadata: {},
});

// Computed
const dialog = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
});

const isEditing = computed(() => !!props.taxRule);
const hasStates = computed(() => props.states.length > 0);
const filteredStates = computed(() => {
  if (!formData.value.jurisdiction.countryCode) return [];
  return props.states;
});

const categoryHint = computed(() => {
  if (!formData.value.type) return '';
  
  const hints: Record<string, string> = {
    sales: 'e.g., Standard, Reduced, Zero, Exempt',
    vat: 'e.g., Standard, Reduced, Super Reduced, Zero',
    gst: 'e.g., GST, HST, QST, PST',
    income: 'e.g., Federal, State, Local',
    withholding: 'e.g., WHT, Dividend, Interest',
    excise: 'e.g., Alcohol, Tobacco, Fuel',
    custom: 'Custom category for this tax rule',
  };
  
  return hints[formData.value.type] || '';
});

// Watchers
watch(
  () => props.taxRule,
  (newRule) => {
    if (newRule) {
      // Convert the TaxRule to form data
      formData.value = {
        code: newRule.code,
        name: newRule.name,
        description: newRule.description || '',
        type: newRule.type,
        jurisdiction: { ...newRule.jurisdiction },
        rates: newRule.rates.map(rate => ({
          rate: rate.rate,
          effectiveFrom: rate.effectiveFrom,
          effectiveTo: rate.effectiveTo,
          description: rate.description || '',
          isStandardRate: rate.isStandardRate || false,
        })),
        category: newRule.category || '',
        isActive: newRule.isActive,
        requiresTaxId: newRule.requiresTaxId || false,
        taxIdFormat: newRule.taxIdFormat || '',
        taxIdValidationRegex: newRule.taxIdValidationRegex || '',
        accountingCode: newRule.accountingCode || '',
        glAccountCode: newRule.glAccountCode || '',
        tags: [...(newRule.tags || [])],
        metadata: { ...(newRule.metadata || {}) },
      };
    } else if (dialog.value) {
      // Reset form when opening a new dialog
      resetForm();
    }
  },
  { immediate: true }
);

// Methods
const resetForm = () => {
  formData.value = {
    code: '',
    name: '',
    description: '',
    type: 'sales',
    jurisdiction: {
      countryCode: '',
      stateCode: '',
      city: '',
      isEu: false,
    },
    rates: [
      {
        rate: 0,
        effectiveFrom: new Date().toISOString().split('T')[0],
        effectiveTo: undefined,
        description: 'Standard rate',
        isStandardRate: true,
      },
    ],
    category: '',
    isActive: true,
    requiresTaxId: false,
    taxIdFormat: '',
    taxIdValidationRegex: '',
    accountingCode: '',
    glAccountCode: '',
    tags: [],
    metadata: {},
  };
};

const closeDialog = () => {
  dialog.value = false;
  emit('closed');
};

const onCountryChange = (countryCode: string) => {
  // Reset state when country changes
  formData.value.jurisdiction.stateCode = '';
  
  // If the country is in the EU, set isEu to true
  const euCountries = ['AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 'DE', 'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL', 'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE'];
  formData.value.jurisdiction.isEu = euCountries.includes(countryCode);
};

const onTaxTypeChange = (type: TaxType) => {
  // Set default category based on tax type
  const defaultCategories: Record<string, string> = {
    sales: 'Standard',
    vat: 'Standard',
    gst: 'GST',
    income: 'Federal',
    withholding: 'WHT',
    excise: 'Standard',
    custom: 'Custom',
  };
  
  if (!formData.value.category || Object.values(defaultCategories).includes(formData.value.category)) {
    formData.value.category = defaultCategories[type] || '';
  }
};

const addRate = () => {
  formData.value.rates.push({
    rate: 0,
    effectiveFrom: new Date().toISOString().split('T')[0],
    effectiveTo: undefined,
    description: 'Additional rate',
    isStandardRate: formData.value.rates.every(rate => !rate.isStandardRate),
  });
};

const removeRate = (index: number) => {
  if (formData.value.rates.length <= 1) return;
  
  const wasStandard = formData.value.rates[index].isStandardRate;
  formData.value.rates.splice(index, 1);
  
  // If we removed the standard rate and there are other rates, make the first one standard
  if (wasStandard && formData.value.rates.length > 0) {
    formData.value.rates[0].isStandardRate = true;
  }
};

const onRateChange = (index: number) => {
  // Ensure rate is a number and within valid range
  if (typeof formData.value.rates[index].rate !== 'number') {
    formData.value.rates[index].rate = 0;
  } else if (formData.value.rates[index].rate < 0) {
    formData.value.rates[index].rate = 0;
  } else if (formData.value.rates[index].rate > 100) {
    formData.value.rates[index].rate = 100;
  }
};

const onStandardRateChange = (index: number) => {
  if (formData.value.rates[index].isStandardRate) {
    // Unset standard rate from other rates
    formData.value.rates.forEach((rate, i) => {
      if (i !== index) {
        rate.isStandardRate = false;
      }
    });
  } else if (formData.value.rates.every(rate => !rate.isStandardRate)) {
    // If no standard rate is selected, make this one standard
    formData.value.rates[index].isStandardRate = true;
  }
};

const validateForm = async (): Promise<boolean> => {
  if (!form.value) return false;
  
  const { valid } = await form.value.validate();
  
  // Additional validation for rates
  if (formData.value.rates.length === 0) {
    toast.error('At least one tax rate is required');
    return false;
  }
  
  // Ensure at least one rate is marked as standard
  if (!formData.value.rates.some(rate => rate.isStandardRate)) {
    formData.value.rates[0].isStandardRate = true;
    toast.warning('First rate set as standard');
  }
  
  return valid;
};

const save = async () => {
  if (!(await validateForm())) {
    toast.error('Please fix the errors in the form');
    return;
  }
  
  try {
    saving.value = true;
    
    // Prepare the data for API
    const data = {
      ...formData.value,
      // Ensure rates are properly formatted
      rates: formData.value.rates.map(rate => ({
        ...rate,
        // Ensure rate is a number
        rate: Number(rate.rate),
      })),
    };
    
    let savedRule: TaxRule;
    
    if (isEditing.value && props.taxRule) {
      // Update existing rule
      savedRule = await taxPolicyService.updateTaxRule(props.taxRule.id, data);
      toast.success('Tax rule updated successfully');
    } else {
      // Create new rule
      savedRule = await taxPolicyService.createTaxRule(data);
      toast.success('Tax rule created successfully');
    }
    
    emit('saved', savedRule);
    closeDialog();
  } catch (error) {
    console.error('Error saving tax rule:', error);
    toast.error(`Failed to save tax rule: ${error instanceof Error ? error.message : 'Unknown error'}`);
  } finally {
    saving.value = false;
  }
};

// Initialize form when component is mounted
onMounted(() => {
  if (props.taxRule) {
    // If editing, the watcher will handle populating the form
    return;
  }
  
  // Set default values for new tax rule
  resetForm();
});
</script>

<style scoped>
/* Add any custom styles here */
</style>
