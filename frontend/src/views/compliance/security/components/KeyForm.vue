<template>
  <div class="key-form">
    <form @submit.prevent="$emit('submit')">
      <div class="field">
        <label for="keyName" class="block text-sm font-medium text-gray-700 mb-1">
          Key Name <span class="text-red-500">*</span>
        </label>
        <InputText 
          id="keyName" 
          v-model="modelValue.name" 
          class="w-full" 
          :class="{ 'p-invalid': submitted && !modelValue.name }"
          placeholder="e.g., Database Encryption Key"
        />
        <small v-if="submitted && !modelValue.name" class="p-error">
          Key name is required.
        </small>
      </div>
      
      <div class="field mt-4">
        <label for="keyAlgorithm" class="block text-sm font-medium text-gray-700 mb-1">
          Algorithm <span class="text-red-500">*</span>
        </label>
        <Dropdown 
          id="keyAlgorithm" 
          v-model="modelValue.algorithm" 
          :options="algorithms" 
          optionLabel="name" 
          optionValue="value"
          placeholder="Select an algorithm"
          class="w-full"
          :class="{ 'p-invalid': submitted && !modelValue.algorithm }"
        />
        <small v-if="submitted && !modelValue.algorithm" class="p-error">
          Algorithm is required.
        </small>
      </div>
      
      <div class="field mt-4">
        <label for="keySize" class="block text-sm font-medium text-gray-700 mb-1">
          Key Size <span class="text-red-500">*</span>
        </label>
        <Dropdown 
          id="keySize" 
          v-model="modelValue.keySize" 
          :options="filteredKeySizes" 
          optionLabel="name" 
          optionValue="value"
          placeholder="Select key size"
          class="w-full"
          :class="{ 'p-invalid': submitted && !modelValue.keySize }"
          :disabled="!modelValue.algorithm"
        />
        <small v-if="submitted && !modelValue.keySize" class="p-error">
          Key size is required.
        </small>
        <small v-if="modelValue.algorithm && !filteredKeySizes.length" class="text-yellow-600 block mt-1">
          No valid key sizes available for the selected algorithm.
        </small>
      </div>
      
      <div class="field mt-4">
        <label for="keyType" class="block text-sm font-medium text-gray-700 mb-1">
          Key Type <span class="text-red-500">*</span>
        </label>
        <Dropdown 
          id="keyType" 
          v-model="modelValue.type" 
          :options="filteredKeyTypes" 
          optionLabel="name" 
          optionValue="value"
          placeholder="Select key type"
          class="w-full"
          :class="{ 'p-invalid': submitted && !modelValue.type }"
          :disabled="!modelValue.algorithm"
        />
        <small v-if="submitted && !modelValue.type" class="p-error">
          Key type is required.
        </small>
      </div>
      
      <div class="field mt-4">
        <label for="keyExpiry" class="block text-sm font-medium text-gray-700 mb-1">
          Expiration Date <span class="text-red-500">*</span>
        </label>
        <Calendar 
          id="keyExpiry" 
          v-model="modelValue.expiresAt" 
          :minDate="new Date()"
          dateFormat="yy-mm-dd"
          showIcon
          class="w-full"
          :class="{ 'p-invalid': submitted && !modelValue.expiresAt }"
        />
        <small v-if="submitted && !modelValue.expiresAt" class="p-error">
          Expiration date is required.
        </small>
      </div>
      
      <div class="field-checkbox mt-5 mb-6">
        <Checkbox 
          id="keyProtected" 
          v-model="modelValue.protected" 
          :binary="true"
          :disabled="modelValue.id && modelValue.protected"
        />
        <label for="keyProtected" class="ml-2">
          Protect this key from deletion
          <i 
            v-tooltip="modelValue.id && modelValue.protected ? 'This key is already protected and cannot be changed' : 'Prevents accidental deletion of this key'"
            class="pi pi-question-circle ml-1 text-gray-400"
          ></i>
        </label>
      </div>
      
      <div class="flex justify-end gap-3 pt-4 border-t">
        <Button 
          type="button" 
          label="Cancel" 
          icon="pi pi-times" 
          class="p-button-text" 
          @click="$emit('cancel')"
          :disabled="saving"
        />
        <Button 
          type="submit" 
          :label="modelValue.id ? 'Update Key' : 'Create Key'" 
          icon="pi pi-check" 
          class="p-button-primary" 
          :loading="saving"
        />
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue';

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  },
  submitted: {
    type: Boolean,
    default: false
  },
  saving: {
    type: Boolean,
    default: false
  },
  algorithms: {
    type: Array,
    default: () => [
      { name: 'AES', value: 'AES' },
      { name: 'RSA', value: 'RSA' },
      { name: 'ECDSA', value: 'ECDSA' },
      { name: 'HMAC', value: 'HMAC' },
      { name: 'PBKDF2', value: 'PBKDF2' },
    ]
  },
  keySizes: {
    type: Array,
    default: () => [
      { name: '128 bits', value: 128, algorithms: ['AES', 'HMAC'] },
      { name: '192 bits', value: 192, algorithms: ['AES'] },
      { name: '256 bits', value: 256, algorithms: ['AES', 'HMAC'] },
      { name: '384 bits', value: 384, algorithms: ['AES'] },
      { name: '512 bits', value: 512, algorithms: ['AES'] },
      { name: '1024 bits', value: 1024, algorithms: ['RSA', 'DSA'] },
      { name: '2048 bits', value: 2048, algorithms: ['RSA', 'DSA'] },
      { name: '3072 bits', value: 3072, algorithms: ['RSA'] },
      { name: '4096 bits', value: 4096, algorithms: ['RSA'] },
    ]
  },
  keyTypes: {
    type: Array,
    default: () => [
      { name: 'Symmetric', value: 'SYMMETRIC', algorithms: ['AES'] },
      { name: 'Asymmetric (Public/Private Key Pair)', value: 'ASYMMETRIC', algorithms: ['RSA', 'ECDSA'] },
      { name: 'HMAC Key', value: 'HMAC', algorithms: ['HMAC'] },
      { name: 'Password-based Key', value: 'PASSWORD_BASED', algorithms: ['PBKDF2'] },
    ]
  }
});

const emit = defineEmits(['update:modelValue', 'submit', 'cancel']);

// Filter key sizes based on selected algorithm
const filteredKeySizes = computed(() => {
  if (!props.modelValue.algorithm) return [];
  
  return props.keySizes.filter(size => 
    size.algorithms.includes(props.modelValue.algorithm)
  );
});

// Filter key types based on selected algorithm
const filteredKeyTypes = computed(() => {
  if (!props.modelValue.algorithm) return [];
  
  return props.keyTypes.filter(type => 
    type.algorithms.includes(props.modelValue.algorithm)
  );
});

// Watch for algorithm changes and reset key size and type if needed
watch(() => props.modelValue.algorithm, (newVal, oldVal) => {
  if (newVal !== oldVal) {
    // Reset key size if not valid for the new algorithm
    if (props.modelValue.keySize && !filteredKeySizes.value.some(s => s.value === props.modelValue.keySize)) {
      props.modelValue.keySize = null;
    }
    
    // Reset key type if not valid for the new algorithm
    if (props.modelValue.type && !filteredKeyTypes.value.some(t => t.value === props.modelValue.type)) {
      props.modelValue.type = '';
    }
  }
});
</script>

<style scoped>
.key-form {
  max-width: 100%;
}

.field {
  margin-bottom: 1.25rem;
}

.field-checkbox {
  display: flex;
  align-items: center;
}

:deep(.p-dropdown) {
  width: 100%;
}

:deep(.p-calendar) {
  width: 100%;
}

:deep(.p-inputtext) {
  width: 100%;
}

/* Responsive adjustments */
@media (max-width: 640px) {
  .field {
    margin-bottom: 1rem;
  }
}
</style>
