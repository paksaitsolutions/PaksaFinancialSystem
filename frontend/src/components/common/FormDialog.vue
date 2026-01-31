<!--
  Paksa Financial System - Form Dialog Component
  Copyright (c) 2025 Paksa IT Solutions. All rights reserved.
-->
<template>
  <Dialog
    v-model:visible="visible"
    :header="title"
    :modal="true"
    :closable="true"
    :style="{ width: width }"
    @hide="onHide"
  >
    <form @submit.prevent="onSubmit">
      <slot :formData="formData" :errors="errors" :hasError="hasError" :getError="getError" />
    </form>

    <template #footer>
      <Button label="Cancel" icon="pi pi-times" text @click="onCancel" />
      <Button 
        :label="submitLabel" 
        icon="pi pi-check" 
        :loading="loading" 
        @click="onSubmit" 
      />
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useFormValidation } from '@/composables/useFormValidation';
import type { FieldValidation } from '@/composables/useFormValidation';

interface Props {
  modelValue: boolean;
  title: string;
  initialData?: Record<string, any>;
  validationRules?: FieldValidation;
  loading?: boolean;
  submitLabel?: string;
  width?: string;
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  submitLabel: 'Save',
  width: '50vw'
});

const emit = defineEmits(['update:modelValue', 'submit', 'cancel']);

const visible = ref(props.modelValue);
const formData = ref({ ...props.initialData });

const { errors, validate, hasError, getError, clearErrors } = useFormValidation(
  formData,
  props.validationRules || {}
);

watch(() => props.modelValue, (val) => {
  visible.value = val;
  if (val) {
    formData.value = { ...props.initialData };
    clearErrors();
  }
});

watch(visible, (val) => {
  emit('update:modelValue', val);
});

const onSubmit = () => {
  if (validate()) {
    emit('submit', formData.value);
  }
};

const onCancel = () => {
  visible.value = false;
  emit('cancel');
};

const onHide = () => {
  visible.value = false;
};
</script>
