<template>
  <v-dialog
    v-model="dialog"
    max-width="1000"
    persistent
    scrollable
  >
    <v-card class="tax-exemption-dialog">
      <v-toolbar
        :title="isEditing ? $t('tax.editExemption') : $t('tax.newExemption')"
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
        <TaxExemptionForm
          ref="taxExemptionForm"
          :exemption="exemption"
          :is-submitting="isSaving"
          @submit="saveExemption"
          @cancel="closeDialog"
        />
      </v-card-text>

      <v-card-actions class="pa-4">
        <v-spacer />
        <v-btn
          variant="text"
          color="error"
          :disabled="isSaving"
          @click="closeDialog"
        >
          {{ $t('common.cancel') }}
        </v-btn>
        <v-btn
          color="primary"
          :loading="isSaving"
          :disabled="isSaving"
          @click="submitForm"
        >
          {{ isEditing ? $t('common.update') : $t('common.save') }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts" setup>
import { ref, computed, watch, onMounted, nextTick } from 'vue';
import { useI18n } from 'vue-i18n';
import { useToast } from 'primevue/usetoast';
import TaxExemptionForm from './TaxExemptionForm.vue';
import type { TaxExemption } from '@/types/tax';
import { useTaxPolicyStore } from '@/modules/tax/store/policy';
import axios, { type AxiosError } from 'axios';

const props = defineProps<{
  modelValue: boolean;
  exemption?: TaxExemption | null;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
  (e: 'saved', exemption: TaxExemption): void;
  (e: 'closed'): void;
}>();

const { t } = useI18n();
const toast = useToast();
const taxPolicyService = useTaxPolicyStore();
const taxExemptionForm = ref<InstanceType<typeof TaxExemptionForm> | null>(null);
const isSaving = ref(false);

// Computed properties
const dialog = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
});

const isEditing = computed(() => !!props.exemption);

// Methods
const closeDialog = () => {
  dialog.value = false;
  emit('closed');
};

const submitForm = async () => {
  if (!taxExemptionForm.value) return;
  
  // Trigger form validation
  await taxExemptionForm.value.validate();
};

const saveExemption = async (exemptionData: any) => {
  try {
    isSaving.value = true;
    
    // Here you would typically call your API to save the exemption
    // const savedExemption = await taxService.saveExemption(exemptionData);
    
    let savedExemption: TaxExemption;
    
    if (isEditing.value && props.exemption) {
      // Update existing exemption
      savedExemption = await taxPolicyService.updateTaxExemption(props.exemption.id, exemptionData);
      (toast as any).add({
        severity: 'success',
        summary: 'Success',
        detail: 'Tax exemption updated successfully',
        life: 5000
      });
    } else {
      // Create new exemption
      savedExemption = await taxPolicyService.createTaxExemption(exemptionData);
      (toast as any).add({
        severity: 'success',
        summary: 'Success',
        detail: 'Tax exemption created successfully',
        life: 5000
      });
    }
    
    emit('saved', savedExemption);
    closeDialog();
  } catch (error: unknown) {
    console.error('Error saving tax exemption:', error);
    
    let errorMessage = 'Failed to save tax exemption';
    
    if (axios.isAxiosError(error)) {
      errorMessage = error.response?.data?.message || error.message || errorMessage;
    } else if (error instanceof Error) {
      errorMessage = error.message;
    }
    
    (toast as any).add({
      severity: 'error',
      summary: 'Error',
      detail: errorMessage,
      life: 5000
    });
    
    // Re-throw the error to allow the calling component to handle it if needed
    throw error;
  } finally {
    isSaving.value = false;
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
.tax-exemption-dialog :deep(.v-dialog) {
  max-height: 90vh;
}

.tax-exemption-dialog :deep(.v-card) {
  display: flex;
  flex-direction: column;
  max-height: 90vh;
}

.tax-exemption-dialog :deep(.v-card-text) {
  flex: 1;
  overflow-y: auto;
}

.tax-exemption-dialog :deep(.v-card-actions) {
  flex-shrink: 0;
  border-top: 1px solid rgba(0, 0, 0, 0.12);
}
</style>
