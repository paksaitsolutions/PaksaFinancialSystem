<template>
  <v-dialog
    v-model="dialog"
    max-width="800"
    persistent
    scrollable
  >
    <v-card>
      <v-toolbar
        :title="isEditing ? 'Edit Tax Exemption' : 'Create New Tax Exemption'"
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
                v-model="formData.exemptionCode"
                label="Exemption Code *"
                :rules="[v => !!v || 'Exemption code is required']"
                variant="outlined"
                density="comfortable"
                class="mb-4"
                :disabled="isEditing"
              />
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="formData.description"
                label="Description *"
                :rules="[v => !!v || 'Description is required']"
                variant="outlined"
                density="comfortable"
                class="mb-4"
              />
            </v-col>

            <v-col cols="12">
              <v-divider class="my-4" />
              <h3 class="text-h6 mb-4">Validity Period</h3>
            </v-col>

            <v-col cols="12" md="6">
              <v-text-field
                v-model="formData.validFrom"
                label="Valid From *"
                type="date"
                :rules="[v => !!v || 'Valid from date is required']"
                variant="outlined"
                density="comfortable"
                class="mb-4"
              />
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="formData.validTo"
                label="Valid To"
                type="date"
                :min="formData.validFrom"
                hint="Leave empty for no expiration"
                persistent-hint
                variant="outlined"
                density="comfortable"
                class="mb-4"
              />
            </v-col>

            <v-col cols="12">
              <v-divider class="my-4" />
              <div class="d-flex justify-space-between align-center mb-4">
                <h3 class="text-h6 mb-0">Applicable Tax Types</h3>
                <v-btn
                  v-if="availableTaxTypes.length > 0"
                  color="primary"
                  variant="tonal"
                  size="small"
                  prepend-icon="mdi-plus"
                  @click="addAllTaxTypes"
                >
                  Add All
                </v-btn>
              </div>

              <v-combobox
                v-model="formData.taxTypes"
                :items="availableTaxTypes"
                item-title="name"
                item-value="type"
                label="Select Tax Types *"
                :rules="[v => v && v.length > 0 || 'At least one tax type is required']"
                variant="outlined"
                density="comfortable"
                multiple
                chips
                closable-chips
                clearable
              >
                <template #selection="{ item, index }">
                  <v-chip
                    :color="getTaxTypeColor(item.raw.type)"
                    size="small"
                    class="mr-2 text-uppercase"
                    close
                    @click:close="removeTaxType(index)"
                  >
                    {{ item.raw.name }}
                  </v-chip>
                </template>
              </v-combobox>
            </v-col>

            <v-col cols="12">
              <v-divider class="my-4" />
              <h3 class="text-h6 mb-4">Jurisdictions</h3>
              <p class="text-caption text-grey mb-4">
                Select the jurisdictions where this exemption applies. If no jurisdictions are selected, the exemption will apply globally.
              </p>

              <v-card variant="outlined" class="mb-4">
                <v-card-text>
                  <v-row>
                    <v-col cols="12" md="6">
                      <v-select
                        v-model="newJurisdiction.countryCode"
                        :items="countries"
                        item-title="name"
                        item-value="code"
                        label="Country"
                        variant="outlined"
                        density="comfortable"
                        hide-details
                        clearable
                        @update:model-value="onCountryChange"
                      />
                    </v-col>
                    <v-col v-if="hasStates" cols="12" md="4">
                      <v-select
                        v-model="newJurisdiction.stateCode"
                        :items="filteredStates"
                        item-title="name"
                        item-value="code"
                        label="State/Region"
                        variant="outlined"
                        density="comfortable"
                        hide-details
                        clearable
                      />
                    </v-col>
                    <v-col cols="12" md="2" class="d-flex align-center">
                      <v-btn
                        color="primary"
                        variant="tonal"
                        :disabled="!newJurisdiction.countryCode"
                        @click="addJurisdiction"
                        block
                      >
                        Add
                      </v-btn>
                    </v-col>
                  </v-row>

                  <v-list v-if="formData.jurisdictions.length > 0" class="mt-4">
                    <v-list-item
                      v-for="(jurisdiction, index) in formData.jurisdictions"
                      :key="index"
                      class="border rounded mb-2"
                    >
                      <template #prepend>
                        <v-icon class="mr-2">mdi-earth</v-icon>
                      </template>
                      <v-list-item-title>
                        {{ getJurisdictionDisplay(jurisdiction) }}
                      </v-list-item-title>
                      <template #append>
                        <v-btn
                          icon
                          variant="text"
                          size="small"
                          color="error"
                          @click="removeJurisdiction(index)"
                        >
                          <v-icon>mdi-delete</v-icon>
                        </v-btn>
                      </template>
                    </v-list-item>
                  </v-list>
                </v-card-text>
              </v-card>
            </v-col>

            <v-col cols="12">
              <v-divider class="my-4" />
              <h3 class="text-h6 mb-4">Additional Settings</h3>
            </v-col>

            <v-col cols="12" md="6">
              <v-switch
                v-model="formData.certificateRequired"
                color="primary"
                label="Certificate Required"
                hint="Check if customers must provide a certificate to use this exemption"
                persistent-hint
                hide-details="auto"
                class="mt-0"
              />
            </v-col>

            <v-col cols="12">
              <v-textarea
                v-model="formData.notes"
                label="Notes"
                variant="outlined"
                rows="2"
                auto-grow
                class="mb-4"
                hint="Internal notes about this exemption"
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
          {{ isEditing ? 'Update' : 'Create' }} Exemption
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts" setup>
import { ref, computed, watch, onMounted } from 'vue';
import { useToast } from 'vue-toastification';
import type { TaxExemption, TaxType } from '@/types/tax';
import { taxPolicyService } from '@/services/taxPolicyService';

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true,
  },
  exemption: {
    type: Object as () => TaxExemption | null,
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
  (e: 'saved', exemption: TaxExemption): void;
  (e: 'closed'): void;
}>();

const toast = useToast();
const form = ref<HTMLFormElement | null>(null);
const isFormValid = ref(false);
const saving = ref(false);

// Form data with defaults
const formData = ref<{
  exemptionCode: string;
  description: string;
  validFrom: string;
  validTo: string | null;
  taxTypes: string[];
  jurisdictions: Array<{
    countryCode: string;
    stateCode?: string;
    city?: string;
  }>;
  certificateRequired: boolean;
  notes?: string;
}>({
  exemptionCode: '',
  description: '',
  validFrom: new Date().toISOString().split('T')[0],
  validTo: null,
  taxTypes: [],
  jurisdictions: [],
  certificateRequired: false,
  notes: '',
});

// New jurisdiction form
const newJurisdiction = ref({
  countryCode: '',
  stateCode: '',
  city: '',
});

// Computed
const dialog = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
});

const isEditing = computed(() => !!props.exemption);
const hasStates = computed(() => {
  if (!newJurisdiction.value.countryCode) return false;
  return props.states.length > 0;
});

const filteredStates = computed(() => {
  if (!newJurisdiction.value.countryCode) return [];
  return props.states;
});

const availableTaxTypes = computed(() => {
  return props.taxTypes.filter(
    type => !formData.value.taxTypes.includes(type.type)
  );
});

// Watchers
watch(
  () => props.exemption,
  (newExemption) => {
    if (newExemption) {
      // Convert the TaxExemption to form data
      formData.value = {
        exemptionCode: newExemption.exemptionCode,
        description: newExemption.description,
        validFrom: newExemption.validFrom,
        validTo: newExemption.validTo || null,
        taxTypes: [...newExemption.taxTypes],
        jurisdictions: newExemption.jurisdictions.map(j => ({
          countryCode: j.countryCode,
          stateCode: j.stateCode,
          city: j.city,
        })),
        certificateRequired: newExemption.certificateRequired,
        notes: newExemption.metadata?.notes || '',
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
    exemptionCode: '',
    description: '',
    validFrom: new Date().toISOString().split('T')[0],
    validTo: null,
    taxTypes: [],
    jurisdictions: [],
    certificateRequired: false,
    notes: '',
  };
  
  newJurisdiction.value = {
    countryCode: '',
    stateCode: '',
    city: '',
  };
};

const closeDialog = () => {
  dialog.value = false;
  emit('closed');
};

const onCountryChange = (countryCode: string) => {
  // Reset state when country changes
  newJurisdiction.value.stateCode = '';
  newJurisdiction.value.city = '';
};

const addJurisdiction = () => {
  if (!newJurisdiction.value.countryCode) return;
  
  const jurisdiction = {
    countryCode: newJurisdiction.value.countryCode,
    stateCode: newJurisdiction.value.stateCode || undefined,
    city: newJurisdiction.value.city || undefined,
  };
  
  // Check if this jurisdiction already exists
  const exists = formData.value.jurisdictions.some(j => 
    j.countryCode === jurisdiction.countryCode &&
    j.stateCode === jurisdiction.stateCode &&
    j.city === jurisdiction.city
  );
  
  if (!exists) {
    formData.value.jurisdictions.push(jurisdiction);
  } else {
    toast.warning('This jurisdiction has already been added');
  }
  
  // Reset the form
  newJurisdiction.value = {
    countryCode: '',
    stateCode: '',
    city: '',
  };
};

const removeJurisdiction = (index: number) => {
  formData.value.jurisdictions.splice(index, 1);
};

const addAllTaxTypes = () => {
  const allTypes = props.taxTypes.map(t => t.type);
  formData.value.taxTypes = [...new Set([...formData.value.taxTypes, ...allTypes])];
};

const removeTaxType = (index: number) => {
  formData.value.taxTypes.splice(index, 1);
};

const getJurisdictionDisplay = (jurisdiction: any) => {
  let result = '';
  const country = props.countries.find(c => c.code === jurisdiction.countryCode);
  
  if (country) {
    result = country.name;
    
    if (jurisdiction.stateCode) {
      const state = props.states.find(s => s.code === jurisdiction.stateCode);
      if (state) {
        result += `, ${state.name}`;
      } else {
        result += `, ${jurisdiction.stateCode}`;
      }
    }
    
    if (jurisdiction.city) {
      result += `, ${jurisdiction.city}`;
    }
  } else {
    result = 'Unknown Jurisdiction';
  }
  
  return result;
};

const getTaxTypeColor = (type: string) => {
  const colorMap: Record<string, string> = {
    sales: 'blue',
    vat: 'purple',
    gst: 'teal',
    income: 'orange',
    withholding: 'red',
    excise: 'deep-orange',
    custom: 'grey',
  };
  return colorMap[type] || 'grey';
};

const validateForm = async (): Promise<boolean> => {
  if (!form.value) return false;
  
  const { valid } = await form.value.validate();
  
  // Additional validation for tax types
  if (formData.value.taxTypes.length === 0) {
    toast.error('At least one tax type is required');
    return false;
  }
  
  // Validate validTo is after validFrom if both are set
  if (formData.value.validTo && formData.value.validFrom > formData.value.validTo) {
    toast.error('Valid To date must be after Valid From date');
    return false;
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
      // Ensure validTo is undefined if empty
      validTo: formData.value.validTo || undefined,
      // Include metadata
      metadata: {
        ...(props.exemption?.metadata || {}),
        notes: formData.value.notes,
        updatedAt: new Date().toISOString(),
      },
    };
    
    let savedExemption: TaxExemption;
    
    if (isEditing.value && props.exemption) {
      // Update existing exemption
      // TODO: Implement update exemption in service
      // savedExemption = await taxPolicyService.updateTaxExemption(props.exemption.id, data);
      savedExemption = {
        ...props.exemption,
        ...data,
        validTo: data.validTo || undefined,
        metadata: data.metadata,
      };
      toast.success('Tax exemption updated successfully');
    } else {
      // Create new exemption
      // TODO: Implement create exemption in service
      // savedExemption = await taxPolicyService.createTaxExemption(data);
      savedExemption = {
        id: `exempt-${Date.now()}`,
        exemptionCode: data.exemptionCode,
        description: data.description,
        validFrom: data.validFrom,
        validTo: data.validTo || undefined,
        taxTypes: data.taxTypes,
        jurisdictions: data.jurisdictions,
        certificateRequired: data.certificateRequired,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        createdBy: 'system',
        updatedBy: 'system',
        metadata: data.metadata,
      };
      toast.success('Tax exemption created successfully');
    }
    
    emit('saved', savedExemption);
    closeDialog();
  } catch (error) {
    console.error('Error saving tax exemption:', error);
    toast.error(`Failed to save tax exemption: ${error instanceof Error ? error.message : 'Unknown error'}`);
  } finally {
    saving.value = false;
  }
};

// Initialize form when component is mounted
onMounted(() => {
  if (props.exemption) {
    // If editing, the watcher will handle populating the form
    return;
  }
  
  // Set default values for new exemption
  resetForm();
});
</script>

<style scoped>
/* Add any custom styles here */
</style>
