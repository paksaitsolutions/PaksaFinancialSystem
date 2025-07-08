<template>
  <Dialog 
    :modelValue="modelValue" 
    @update:modelValue="$emit('update:modelValue', $event)"
    header="Rotate Encryption Keys"
    :modal="true"
    :style="{ width: '650px' }"
    :closable="!loading && !rotationInProgress"
  >
    <div v-if="!results">
      <!-- Step 1: Selection -->
      <div v-if="step === 1">
        <h3 class="font-semibold text-lg mb-3">Step 1: Select Keys to Rotate</h3>
        <p class="text-gray-600 mb-4">Select the keys you want to include in this rotation cycle. Only active keys are listed.</p>
        
        <DataTable 
          v-model:selection="selectedKeys"
          :value="activeKeys"
          dataKey="id"
          responsiveLayout="scroll"
          class="p-datatable-sm"
        >
          <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>
          <Column field="name" header="Key Name"></Column>
          <Column field="algorithm" header="Algorithm"></Column>
          <Column field="expiresAt" header="Expires">
            <template #body="{ data }">
              {{ formatDateTime(data.expiresAt) }}
            </template>
          </Column>
        </DataTable>
      </div>

      <!-- Step 2: Configuration -->
      <div v-if="step === 2">
        <h3 class="font-semibold text-lg mb-3">Step 2: Configure Rotation</h3>
        <div class="formgrid grid gap-4">
          <div class="field col-12">
            <label for="strategy" class="block text-sm font-medium text-gray-700 mb-1">Rotation Strategy</label>
            <Dropdown 
              v-model="rotationConfig.strategy"
              :options="rotationStrategies"
              optionLabel="name"
              optionValue="value"
              placeholder="Select a strategy"
              class="w-full"
            />
          </div>
          <div class="field col-12">
            <label for="rotationDate" class="block text-sm font-medium text-gray-700 mb-1">Scheduled Rotation Date</label>
            <Calendar 
              v-model="rotationConfig.rotationDate"
              dateFormat="yy-mm-dd"
              showIcon
              class="w-full"
              :minDate="new Date()"
            />
          </div>
          <div class="field col-12">
            <label for="notes" class="block text-sm font-medium text-gray-700 mb-1">Notes (Optional)</label>
            <Textarea v-model="rotationConfig.notes" rows="3" class="w-full" />
          </div>
        </div>
      </div>
    </div>

    <!-- Step 3: Results -->
    <div v-if="results">
      <h3 class="font-semibold text-lg mb-3">Rotation {{ rotationConfig.dryRun ? 'Dry Run' : '' }} Results</h3>
      <Message :severity="results.success ? 'success' : 'error'" :closable="false">{{ results.message }}</Message>
      
      <div class="mt-4 max-h-60 overflow-y-auto">
        <h4 class="font-medium mb-2">Details:</h4>
        <ul class="list-disc pl-5 space-y-2">
          <li v-for="detail in results.details" :key="detail.keyId">
            <div class="flex justify-between items-center">
              <span>
                <i :class="['pi', getResultIcon(detail.status), 'mr-2']"></i>
                <strong>{{ detail.keyName }}</strong>: {{ detail.message }}
              </span>
              <Tag :value="detail.status" :severity="detail.status" />
            </div>
          </li>
        </ul>
      </div>
    </div>

    <template #footer>
      <div class="flex justify-between w-full">
        <div>
          <Button 
            v-if="step > 1 && !results"
            label="Back" 
            icon="pi pi-arrow-left" 
            class="p-button-text"
            @click="step--"
            :disabled="loading || rotationInProgress"
          />
        </div>
        <div class="flex gap-2">
          <Button 
            label="Cancel" 
            icon="pi pi-times" 
            class="p-button-outlined p-button-secondary"
            @click="cancel"
            :disabled="loading || rotationInProgress"
          />
          <Button 
            v-if="step === 1"
            label="Next"
            icon="pi pi-arrow-right"
            @click="step++"
            :disabled="!selectedKeys.length"
          />
          <Button 
            v-if="step === 2 && !results"
            label="Run Dry Run"
            icon="pi pi-play"
            class="p-button-outlined"
            @click="runRotation(true)"
            :loading="loading && rotationConfig.dryRun"
            :disabled="rotationInProgress"
          />
          <Button 
            v-if="(step === 2 && !results) || (results && results.canProceed)"
            label="Confirm Rotation"
            icon="pi pi-check"
            class="p-button-primary"
            @click="runRotation(false)"
            :loading="loading && !rotationConfig.dryRun"
            :disabled="rotationInProgress"
          />
          <Button 
            v-if="results"
            label="Close"
            icon="pi pi-check"
            class="p-button-primary"
            @click="cancel"
          />
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, watch, defineProps, defineEmits } from 'vue';
import { format, parseISO } from 'date-fns';

// --- TYPE DEFINITIONS ---
interface EncryptionKey {
  id: string;
  name: string;
  algorithm: string;
  expiresAt: string;
}

interface RotationConfig {
  strategy: string;
  rotationDate: Date;
  notes: string;
  dryRun: boolean;
}

interface RotationPayload {
  keyIds: string[];
  strategy: string;
  rotationDate: string;
  notes: string;
  dryRun: boolean;
}

interface RotationResultDetail {
  keyId: string;
  keyName: string;
  status: 'success' | 'warning' | 'error';
  message: string;
}

interface RotationResult {
  success: boolean;
  message: string;
  canProceed?: boolean;
  details: RotationResultDetail[];
}

// --- PROPS & EMITS ---
const props = defineProps<{
  modelValue: boolean;
  activeKeys: EncryptionKey[];
  loading: boolean;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
  (e: 'rotate', payload: RotationPayload, callback: (results: RotationResult) => void): void;
  (e: 'cancel'): void;
}>();

// --- STATE ---
const step = ref(1);
const selectedKeys = ref<EncryptionKey[]>([]);
const rotationConfig = ref<RotationConfig>({
  strategy: 'IMMEDIATE_REPLACE',
  rotationDate: new Date(),
  notes: '',
  dryRun: false,
});
const rotationInProgress = ref(false);
const results = ref<RotationResult | null>(null);

// --- STATIC DATA ---
const rotationStrategies = [
  { name: 'Immediate Replacement', value: 'IMMEDIATE_REPLACE' },
  { name: 'Phased Rollout (Overlap)', value: 'PHASED_ROLLOUT' },
];

// --- METHODS ---
const formatDateTime = (dateString?: string) => {
  if (!dateString) return 'N/A';
  return format(parseISO(dateString), 'MMM d, yyyy');
};

const runRotation = (isDryRun: boolean) => {
  rotationConfig.value.dryRun = isDryRun;
  rotationInProgress.value = true;

  const payload: RotationPayload = {
    keyIds: selectedKeys.value.map(k => k.id),
    strategy: rotationConfig.value.strategy,
    rotationDate: rotationConfig.value.rotationDate.toISOString(),
    notes: rotationConfig.value.notes,
    dryRun: isDryRun,
  };

  emit('rotate', payload, (rotationResults: RotationResult) => {
    results.value = rotationResults;
    rotationInProgress.value = false;
    if (!isDryRun && rotationResults.success) {
      // On successful final rotation, we might want to keep the dialog open to show results
      // but prevent further action except closing.
    } else if (isDryRun && !rotationResults.success) {
      // If dry run fails, allow user to go back and fix.
      results.value.canProceed = false;
    }
  });
};

const cancel = () => {
  resetState();
  emit('cancel');
};

const getResultIcon = (status: RotationResultDetail['status']) => {
  switch (status) {
    case 'success': return 'pi-check-circle text-green-500';
    case 'warning': return 'pi-exclamation-triangle text-yellow-500';
    case 'error': return 'pi-times-circle text-red-500';
  }
};

const resetState = () => {
  step.value = 1;
  selectedKeys.value = [];
  rotationConfig.value = {
    strategy: 'IMMEDIATE_REPLACE',
    rotationDate: new Date(),
    notes: '',
    dryRun: false,
  };
  results.value = null;
  rotationInProgress.value = false;
};

// --- WATCHERS ---
watch(() => props.modelValue, (newValue) => {
  if (!newValue) {
    // Use a timeout to ensure the dialog closing animation completes before state is reset
    setTimeout(resetState, 300);
  }
});
</script>

<style scoped>
.p-datatable-sm :deep(.p-datatable-thead > tr > th) {
    padding: 0.5rem 0.5rem;
}
.p-datatable-sm :deep(.p-datatable-tbody > tr > td) {
    padding: 0.5rem 0.5rem;
}
</style>
