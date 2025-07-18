<template>
  <v-alert
    v-if="show"
    :type="type"
    variant="tonal"
    closable
    class="mb-4"
    @click:close="onClose"
  >
    {{ message }}
  </v-alert>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  message: {
    type: String,
    default: ''
  },
  type: {
    type: String,
    default: 'info',
    validator: (value) => ['success', 'info', 'warning', 'error'].includes(value)
  }
});

const emit = defineEmits(['close']);

const onClose = () => {
  emit('close');
};
</script>