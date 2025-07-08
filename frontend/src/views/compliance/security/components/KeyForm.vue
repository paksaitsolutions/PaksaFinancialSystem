<template>
  <form @submit.prevent="handleSubmit">
    <div class="formgrid grid gap-4">
      <div class="field col-12">
        <label for="keyName" class="block text-sm font-medium text-gray-700 mb-1">Key Name</label>
        <InputText 
          id="keyName" 
          v-model.trim="editableData.name" 
          :class="{ 'p-invalid': submitted && !editableData.name }"
          class="w-full"
          placeholder="e.g., Primary Database Key"
        />
        <small v-if="submitted && !editableData.name" class="p-error">Key Name is required.</small>
      </div>

      <div class="field col-12">
        <label for="description" class="block text-sm font-medium text-gray-700 mb-1">Description</label>
        <Textarea 
          id="description"
          v-model="editableData.description"
          rows="3"
          class="w-full"
          placeholder="A brief description of the key's purpose"
        />
      </div>

      <div class="field col-12 md:col-6">
        <label for="algorithm" class="block text-sm font-medium text-gray-700 mb-1">Algorithm</label>
        <Dropdown 
          id="algorithm" 
          v-model="editableData.algorithm" 
          :options="algorithms"
          optionLabel="name"
          optionValue="value"
          placeholder="Select an Algorithm"
          :class="{ 'p-invalid': submitted && !editableData.algorithm }"
          class="w-full"
        />
        <small v-if="submitted && !editableData.algorithm" class="p-error">Algorithm is required.</small>
      </div>

      <div class="field col-12 md:col-6">
        <label for="keySize" class="block text-sm font-medium text-gray-700 mb-1">Key Size (bits)</label>
        <InputNumber 
          id="keySize" 
          v-model="editableData.keySize" 
          :class="{ 'p-invalid': submitted && !editableData.keySize }"
          class="w-full"
          placeholder="e.g., 256"
        />
        <small v-if="submitted && !editableData.keySize" class="p-error">Key Size is required.</small>
      </div>

      <div class="field col-12">
        <label for="keyType" class="block text-sm font-medium text-gray-700 mb-1">Key Type</label>
        <Dropdown 
          id="keyType" 
          v-model="editableData.type" 
          :options="keyTypes"
          optionLabel="name"
          optionValue="value"
          placeholder="Select a Key Type"
          :class="{ 'p-invalid': submitted && !editableData.type }"
          class="w-full"
        />
      </div>

      <div class="field col-12">
        <label for="expiresAt" class="block text-sm font-medium text-gray-700 mb-1">Expiration Date</label>
        <Calendar 
          id="expiresAt" 
          v-model="editableData.expiresAt" 
          dateFormat="yy-mm-dd"
          showIcon
          class="w-full"
          :minDate="new Date()"
        />
      </div>

      <div class="field col-12">
        <div class="flex items-center gap-4">
          <div class="flex items-center">
            <Checkbox v-model="editableData.protected" inputId="protectedKey" :binary="true" />
            <label for="protectedKey" class="ml-2">Protected Key</label>
          </div>
          <div class="flex items-center">
            <Checkbox v-model="editableData.enabled" inputId="enabledKey" :binary="true" />
            <label for="enabledKey" class="ml-2">Enabled</label>
          </div>
        </div>
        <p class="text-xs text-gray-500 mt-2">Protected keys have deletion restrictions.</p>
      </div>
    </div>

    <div class="flex justify-end gap-2 mt-6">
        <Button label="Cancel" icon="pi pi-times" class="p-button-text" @click="$emit('cancel')" />
        <Button type="submit" label="Save Key" icon="pi pi-check" class="p-button-primary" />
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref, watch, defineProps, defineEmits } from 'vue';

// --- TYPE DEFINITIONS ---
export interface KeyFormModel {
  name: string;
  description: string;
  algorithm: string | null;
  keySize: number | null;
  type: string | null;
  expiresAt: Date | null;
  protected: boolean;
  enabled: boolean;
}

// --- PROPS & EMITS ---
const props = defineProps<{
  modelValue: KeyFormModel;
  submitted: boolean;
  algorithms: { name: string; value: string }[];
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: KeyFormModel): void;
  (e: 'submit'): void;
  (e: 'cancel'): void;
}>();

// --- STATE ---
const editableData = ref<KeyFormModel>({ ...props.modelValue });

const keyTypes = [
  { name: 'Symmetric', value: 'SYMMETRIC' },
  { name: 'Asymmetric', value: 'ASYMMETRIC' },
];

// --- METHODS ---
const handleSubmit = () => {
  emit('submit');
};

// --- WATCHERS ---
watch(() => props.modelValue, (newValue) => {
  // Ensure dates are correctly handled when the model is updated externally.
  // The incoming value could be a string, so we robustly convert it to a Date object or null.
  let expiresAtDate: Date | null = null;
  if (newValue.expiresAt) {
      const d = new Date(newValue.expiresAt as string | Date);
      if (d && !isNaN(d.getTime())) {
          expiresAtDate = d;
      }
  }
  editableData.value = { ...newValue, expiresAt: expiresAtDate };
}, { deep: true, immediate: true });

watch(editableData, (newValue) => {
  emit('update:modelValue', newValue);
}, { deep: true });

</script>
