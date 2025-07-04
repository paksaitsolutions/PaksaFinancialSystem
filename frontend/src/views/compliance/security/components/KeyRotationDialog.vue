<template>
  <Dialog 
    :visible="modelValue" 
    @update:visible="(val) => $emit('update:modelValue', val)"
    header="Rotate Encryption Keys" 
    :modal="true"
    :style="{ width: '600px' }"
    :closable="!loading"
  >
    <div class="key-rotation-dialog">
      <div class="mb-6">
        <p class="mb-4">Select the keys you want to rotate. This will generate new encryption keys and re-encrypt all data with the new keys.</p>
        
        <div class="p-4 border rounded-md mb-4">
          <div class="flex items-center mb-3">
            <Checkbox 
              id="selectAllKeys" 
              v-model="selectAll" 
              :binary="true"
              :disabled="loading"
              @change="toggleSelectAll"
            />
            <label for="selectAllKeys" class="ml-2 font-medium">Select All Keys</label>
          </div>
          
          <div class="max-h-60 overflow-y-auto border rounded">
            <DataTable 
              :value="filteredKeys" 
              :loading="loading"
              selectionMode="multiple"
              v-model:selection="selectedKeys"
              dataKey="id"
              :scrollable="true"
              scrollHeight="flex"
              class="p-datatable-sm"
            >
              <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>
              <Column field="name" header="Key Name" :sortable="true">
                <template #body="{ data }">
                  <div class="flex items-center">
                    <span>{{ data.name }}</span>
                    <Tag 
                      v-if="data.protected" 
                      value="Protected" 
                      severity="info" 
                      class="ml-2 text-xs"
                    />
                  </div>
                </template>
              </Column>
              <Column field="algorithm" header="Algorithm" :sortable="true" />
              <Column field="keySize" header="Size" :sortable="true">
                <template #body="{ data }">
                  {{ data.keySize }} bits
                </template>
              </Column>
              <Column field="expiresAt" header="Expires" :sortable="true">
                <template #body="{ data }">
                  {{ formatDate(data.expiresAt) }}
                </template>
              </Column>
            </DataTable>
          </div>
          
          <div class="mt-3 text-sm text-gray-600">
            <i class="pi pi-info-circle mr-1"></i>
            {{ selectedKeys.length }} key{{ selectedKeys.length !== 1 ? 's' : '' }} selected
            <span v-if="protectedCount > 0">
              ({{ protectedCount }} protected key{{ protectedCount !== 1 ? 's' : '' }} excluded)
            </span>
          </div>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label for="rotationStrategy" class="block text-sm font-medium text-gray-700 mb-1">
              Rotation Strategy
            </label>
            <Dropdown 
              id="rotationStrategy" 
              v-model="strategy" 
              :options="strategies" 
              optionLabel="name" 
              optionValue="value"
              class="w-full"
              :disabled="loading"
            />
            <small class="text-gray-500">
              {{ getStrategyDescription(strategy) }}
            </small>
          </div>
          
          <div>
            <label for="rotationDate" class="block text-sm font-medium text-gray-700 mb-1">
              Rotation Date
            </label>
            <Calendar 
              id="rotationDate" 
              v-model="rotationDate" 
              :minDate="new Date()"
              dateFormat="yy-mm-dd"
              showIcon
              class="w-full"
              :disabled="loading"
            />
            <small class="text-gray-500">
              When the rotation should take effect
            </small>
          </div>
        </div>
        
        <div class="mb-4">
          <label for="rotationNotes" class="block text-sm font-medium text-gray-700 mb-1">
            Notes (Optional)
          </label>
          <Textarea 
            id="rotationNotes" 
            v-model="notes" 
            rows="3" 
            class="w-full"
            :disabled="loading"
            placeholder="Add any notes about this key rotation..."
          />
          <small class="text-gray-500">
            Add any relevant information about this rotation
          </small>
        </div>
        
        <Message v-if="selectedKeys.length > 0" severity="warn" :closable="false">
          <div class="flex align-items-start">
            <i class="pi pi-exclamation-triangle mt-1 mr-2"></i>
            <span>
              <strong>Important:</strong> Key rotation is a critical operation. 
              Ensure you have proper backups and that this operation is performed during a maintenance window.
            </span>
          </div>
        </Message>
      </div>
      
      <template #footer>
        <div class="flex justify-between w-full">
          <Button 
            type="button" 
            label="Cancel" 
            icon="pi pi-times" 
            class="p-button-text" 
            @click="$emit('cancel')"
            :disabled="loading"
          />
          <div class="flex gap-2">
            <Button 
              type="button" 
              label="Dry Run" 
              icon="pi pi-search" 
              class="p-button-outlined p-button-help" 
              @click="startRotation(true)"
              :disabled="loading || selectedKeys.length === 0"
              :loading="loading && dryRun"
            />
            <Button 
              type="button" 
              label="Rotate Keys" 
              icon="pi pi-sync" 
              class="p-button-warning" 
              @click="confirmRotation"
              :disabled="loading || selectedKeys.length === 0"
              :loading="loading && !dryRun"
            />
          </div>
        </div>
      </template>
    </div>
    
    <!-- Confirmation Dialog -->
    <Dialog 
      v-model:visible="showConfirmDialog" 
      header="Confirm Key Rotation" 
      :modal="true"
      :style="{ width: '500px' }"
      :closable="!loading"
    >
      <div class="confirmation-content">
        <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
        <div>
          <p class="mb-3">
            You are about to rotate <strong>{{ selectedKeys.length }} encryption key{{ selectedKeys.length !== 1 ? 's' : '' }}</strong>.
            This operation cannot be undone.
          </p>
          <p class="font-medium">Are you sure you want to proceed?</p>
        </div>
      </div>
      <template #footer>
        <Button 
          label="No" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="showConfirmDialog = false"
          :disabled="loading"
        />
        <Button 
          label="Yes, Rotate Keys" 
          icon="pi pi-check" 
          class="p-button-warning" 
          @click="startRotation(false)"
          :loading="loading"
        />
      </template>
    </Dialog>
    
    <!-- Results Dialog -->
    <Dialog 
      v-model:visible="showResultsDialog" 
      :header="dryRun ? 'Dry Run Results' : 'Rotation Results'" 
      :modal="true"
      :style="{ width: '600px', maxWidth: '90vw' }"
    >
      <div class="results-content">
        <div v-if="rotationResults" class="space-y-4">
          <div class="p-3 border rounded-md" :class="{
            'bg-green-50 border-green-200': rotationResults.success,
            'bg-yellow-50 border-yellow-200': !rotationResults.success
          }">
            <div class="flex items-start">
              <i 
                class="mr-2 mt-0.5"
                :class="{
                  'pi pi-check-circle text-green-500': rotationResults.success,
                  'pi pi-exclamation-triangle text-yellow-500': !rotationResults.success
                }"
              ></i>
              <div>
                <h4 class="font-medium mb-1">
                  {{ rotationResults.success ? 'Rotation Ready' : 'Rotation Issues Found' }}
                </h4>
                <p class="text-sm">
                  {{ rotationResults.message }}
                </p>
              </div>
            </div>
          </div>
          
          <div v-if="rotationResults.details && rotationResults.details.length > 0" class="mt-4">
            <h5 class="font-medium mb-2">Key Rotation Details:</h5>
            <div class="space-y-3">
              <div 
                v-for="(detail, index) in rotationResults.details" 
                :key="index"
                class="flex items-start p-2 border rounded"
                :class="{
                  'bg-green-50 border-green-100': detail.status === 'success',
                  'bg-yellow-50 border-yellow-100': detail.status === 'warning',
                  'bg-red-50 border-red-100': detail.status === 'error'
                }"
              >
                <i 
                  class="mr-2 mt-0.5"
                  :class="{
                    'pi pi-check-circle text-green-500': detail.status === 'success',
                    'pi pi-exclamation-triangle text-yellow-500': detail.status === 'warning',
                    'pi pi-times-circle text-red-500': detail.status === 'error'
                  }"
                ></i>
                <div>
                  <div class="font-medium">{{ detail.keyName }}</div>
                  <div class="text-sm text-gray-600">{{ detail.message }}</div>
                  <div v-if="detail.details" class="text-xs text-gray-500 mt-1">{{ detail.details }}</div>
                </div>
              </div>
            </div>
          </div>
          
          <div v-if="rotationResults.warnings && rotationResults.warnings.length > 0" class="mt-4">
            <h5 class="font-medium mb-2 text-yellow-600">Warnings:</h5>
            <ul class="list-disc pl-5 space-y-1">
              <li v-for="(warning, index) in rotationResults.warnings" :key="'warn-'+index" class="text-sm text-yellow-700">
                {{ warning }}
              </li>
            </ul>
          </div>
          
          <div v-if="rotationResults.nextSteps && rotationResults.nextSteps.length > 0" class="mt-4">
            <h5 class="font-medium mb-2">Next Steps:</h5>
            <ul class="list-decimal pl-5 space-y-1">
              <li v-for="(step, index) in rotationResults.nextSteps" :key="'step-'+index" class="text-sm text-gray-700">
                {{ step }}
              </li>
            </ul>
          </div>
        </div>
      </div>
      <template #footer>
        <div class="flex justify-end w-full">
          <Button 
            label="Close" 
            icon="pi pi-times" 
            class="p-button-text" 
            @click="showResultsDialog = false"
          />
          <Button 
            v-if="dryRun && rotationResults && rotationResults.canProceed"
            label="Proceed with Rotation" 
            icon="pi pi-sync" 
            class="p-button-warning ml-2" 
            @click="proceedWithRotation"
          />
        </div>
      </template>
    </Dialog>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useToast } from 'primevue/usetoast';
import { format } from 'date-fns';

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  activeKeys: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['update:modelValue', 'rotate', 'cancel']);

// Initialize toast
const toast = useToast?.() || { add: console.log };

// State
const selectAll = ref(false);
const selectedKeys = ref([]);
const strategy = ref('in-place');
const rotationDate = ref(new Date());
const notes = ref('');
const dryRun = ref(true);
const showConfirmDialog = ref(false);
const showResultsDialog = ref(false);
const rotationResults = ref(null);

// Options
const strategies = [
  { name: 'In-place Rotation', value: 'in-place', description: 'Replace existing keys and re-encrypt data' },
  { name: 'Dual Key Transition', value: 'dual-key', description: 'Maintain both old and new keys during transition' },
  { name: 'Key Versioning', value: 'versioning', description: 'Create new key versions and phase out old ones' },
];

// Computed properties
const filteredKeys = computed(() => {
  // Filter out protected keys from being selected
  return props.activeKeys.filter(key => !key.protected);
});

const protectedCount = computed(() => {
  return props.activeKeys.filter(key => key.protected).length;
});

// Methods
const formatDate = (dateString: string) => {
  if (!dateString) return 'N/A';
  return format(new Date(dateString), 'PP');
};

const getStrategyDescription = (strategyValue: string) => {
  const strategy = strategies.find(s => s.value === strategyValue);
  return strategy ? strategy.description : '';
};

const toggleSelectAll = () => {
  if (selectAll.value) {
    selectedKeys.value = [...filteredKeys.value];
  } else {
    selectedKeys.value = [];
  }
};

const confirmRotation = () => {
  if (selectedKeys.value.length === 0) {
    toast.add({
      severity: 'warn',
      summary: 'No Keys Selected',
      detail: 'Please select at least one key to rotate.',
      life: 3000
    });
    return;
  }
  
  showConfirmDialog.value = true;
};

const startRotation = (isDryRun: boolean) => {
  dryRun.value = isDryRun;
  showConfirmDialog.value = false;
  
  // In a real app, this would be an API call
  // For now, we'll simulate a response
  setTimeout(() => {
    rotationResults.value = simulateRotationResponse(isDryRun);
    showResultsDialog.value = true;
  }, 1500);
  
  // In a real app, you would call the API like this:
  // try {
  //   const response = await api.post('/api/security/keys/rotate', {
  //     keyIds: selectedKeys.value.map(k => k.id),
  //     strategy: strategy.value,
  //     rotationDate: rotationDate.value,
  //     notes: notes.value,
  //     dryRun: isDryRun
  //   });
  //   
  //   rotationResults.value = response.data;
  //   showResultsDialog.value = true;
  // } catch (error) {
  //   console.error('Error during key rotation:', error);
  //   toast.add({
  //     severity: 'error',
  //     summary: 'Rotation Failed',
  //     detail: 'An error occurred during key rotation',
  //     life: 5000
  //   });
  // } finally {
  //   loading.value = false;
  // }
};

const proceedWithRotation = () => {
  showResultsDialog.value = false;
  startRotation(false);
};

const simulateRotationResponse = (isDryRun: boolean) => {
  if (isDryRun) {
    return {
      success: true,
      message: 'Dry run completed successfully. No changes were made to your keys.',
      canProceed: true,
      details: selectedKeys.value.map(key => ({
        keyId: key.id,
        keyName: key.name,
        status: Math.random() > 0.2 ? 'success' : 'warning',
        message: Math.random() > 0.2 
          ? 'Ready for rotation' 
          : 'Warning: This key was recently rotated',
        details: Math.random() > 0.8 
          ? 'Last rotated less than 7 days ago' 
          : null
      })),
      warnings: [
        'Some keys were recently rotated. Consider waiting before rotating them again.',
        'This operation may cause temporary performance degradation during the rotation process.'
      ],
      nextSteps: [
        'Review the key rotation details above.',
        'Schedule the rotation during a maintenance window.',
        'Ensure you have a recent backup before proceeding.'
      ]
    };
  } else {
    return {
      success: true,
      message: 'Key rotation completed successfully.',
      details: selectedKeys.value.map(key => ({
        keyId: key.id,
        keyName: key.name,
        status: 'success',
        message: 'Key rotated successfully',
        newKeyId: `key-${Math.random().toString(36).substring(2, 10)}`,
        timestamp: new Date().toISOString()
      })),
      nextSteps: [
        'Monitor the system for any issues after rotation.',
        'Update any hardcoded key references in your applications.',
        'Document this rotation in your change management system.'
      ]
    };
  }
};

// Watchers
watch(selectedKeys, (newVal) => {
  // Update selectAll state based on selection
  if (newVal.length === filteredKeys.value.length) {
    selectAll.value = true;
  } else if (newVal.length === 0) {
    selectAll.value = false;
  } else {
    selectAll.value = false;
  }
}, { deep: true });

// Reset state when dialog is closed
watch(() => props.modelValue, (newVal) => {
  if (!newVal) {
    // Reset state when dialog is closed
    selectAll.value = false;
    selectedKeys.value = [];
    strategy.value = 'in-place';
    rotationDate.value = new Date();
    notes.value = '';
    rotationResults.value = null;
    showConfirmDialog.value = false;
    showResultsDialog.value = false;
  }
});
</script>

<style scoped>
.key-rotation-dialog {
  max-height: 70vh;
  display: flex;
  flex-direction: column;
}

.confirmation-content {
  display: flex;
  align-items: flex-start;
  padding: 1rem 0;
}

.results-content {
  max-height: 60vh;
  overflow-y: auto;
  padding-right: 0.5rem;
}

/* Custom scrollbar */
.results-content::-webkit-scrollbar {
  width: 6px;
}

.results-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.results-content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.results-content::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* Responsive adjustments */
@media (max-width: 640px) {
  .key-rotation-dialog {
    max-height: none;
  }
  
  .results-content {
    max-height: 50vh;
  }
}
</style>
