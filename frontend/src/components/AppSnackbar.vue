<template>
  <v-snackbar
    v-model="show"
    :timeout="timeout"
    :color="color"
    :multi-line="message.length > 50"
    :vertical="message.length > 100"
    location="bottom right"
    class="app-snackbar"
  >
    <div class="d-flex align-center">
      <v-icon v-if="color === 'success'" class="me-2">mdi-check-circle</v-icon>
      <v-icon v-else-if="color === 'error'" class="me-2">mdi-alert-circle</v-icon>
      <v-icon v-else-if="color === 'warning'" class="me-2">mdi-alert</v-icon>
      <v-icon v-else class="me-2">mdi-information</v-icon>
      
      <span class="text-body-2">{{ message }}</span>
    </div>

    <template v-if="showClose" #actions>
      <v-btn
        :icon="true"
        variant="text"
        size="small"
        @click="close"
      >
        <v-icon>mdi-close</v-icon>
      </v-btn>
    </template>
  </v-snackbar>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useSnackbar } from '../shared/composables/useSnackbar';

const { 
  message, 
  color, 
  show, 
  timeout, 
  showClose, 
  close 
} = useSnackbar();
</script>

<style scoped>
.app-snackbar {
  margin-bottom: 16px;
  margin-right: 16px;
}

.app-snackbar :deep(.v-snackbar__content) {
  padding: 8px 0;
}
</style>
