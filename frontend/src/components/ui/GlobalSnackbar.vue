<template>
  <v-snackbar
    v-model="show"
    :color="color"
    :timeout="timeout"
    :location="location"
  >
    {{ text }}
    
    <template v-slot:actions>
      <v-btn
        variant="text"
        @click="show = false"
      >
        Close
      </v-btn>
    </template>
  </v-snackbar>
</template>

<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  text: {
    type: String,
    default: ''
  },
  color: {
    type: String,
    default: 'success'
  },
  timeout: {
    type: Number,
    default: 5000
  },
  location: {
    type: String,
    default: 'bottom'
  }
});

const emit = defineEmits(['update:modelValue']);

const show = ref(props.modelValue);

watch(() => props.modelValue, (newVal) => {
  show.value = newVal;
});

watch(show, (newVal) => {
  emit('update:modelValue', newVal);
});
</script>