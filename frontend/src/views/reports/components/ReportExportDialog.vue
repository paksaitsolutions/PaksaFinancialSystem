<template>
  <v-dialog v-model="dialog" max-width="500px">
    <v-card>
      <v-card-title>Export Report</v-card-title>
      <v-card-text>
        <v-select
          v-model="selectedFormat"
          :items="formats"
          label="Export Format"
          item-title="label"
          item-value="value"
        />
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn text @click="dialog = false">Cancel</v-btn>
        <v-btn color="primary" @click="exportReport">Export</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const dialog = ref(false);
const selectedFormat = ref('pdf');

const formats = [
  { label: 'PDF', value: 'pdf' },
  { label: 'Excel', value: 'xlsx' },
  { label: 'CSV', value: 'csv' }
];

const exportReport = () => {
  // Implementation
  dialog.value = false;
};
</script>