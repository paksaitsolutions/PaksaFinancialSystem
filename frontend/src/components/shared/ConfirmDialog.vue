<template>
  <Dialog
    v-model:visible="modelValue"
    :style="{ width: '450px' }"
    :header="header"
    :modal="true"
    :closable="!loading"
    :close-on-escape="!loading"
  >
    <div class="confirmation-content">
      <i class="pi pi-exclamation-triangle mr-3" style="font-size: 2rem" />
      <span v-if="message">{{ message }}</span>
      <slot v-else>
        <span>{{ $t('common.areYouSure') }}</span>
      </slot>
    </div>
    
    <template #footer>
      <Button 
        :label="$t('common.no')" 
        icon="pi pi-times" 
        class="p-button-text" 
        :disabled="loading"
        @click="$emit('update:visible', false)" 
      />
      <Button 
        :label="$t('common.yes')" 
        icon="pi pi-check" 
        class="p-button-danger" 
        :loading="loading"
        @click="$emit('confirm')" 
      />
    </template>
  </Dialog>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'ConfirmDialog',
  props: {
    modelValue: {
      type: Boolean,
      default: false
    },
    header: {
      type: String,
      default: 'Confirm'
    },
    message: {
      type: String,
      default: ''
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:modelValue', 'confirm']
});
</script>

<style scoped>
.confirmation-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 1rem 0;
}
</style>
