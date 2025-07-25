<template>
  <v-dialog v-model="dialog" max-width="600px">
    <v-card>
      <v-card-title>Schedule Report</v-card-title>
      <v-card-text>
        <v-form ref="form" v-model="valid">
          <v-text-field
            v-model="scheduleName"
            label="Schedule Name"
            :rules="[rules.required]"
            required
          />
          <v-select
            v-model="frequency"
            :items="frequencies"
            label="Frequency"
            item-title="label"
            item-value="value"
            :rules="[rules.required]"
            required
          />
          <v-text-field
            v-model="email"
            label="Email Recipients"
            :rules="[rules.required, rules.email]"
            required
          />
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn text @click="dialog = false">Cancel</v-btn>
        <v-btn color="primary" :disabled="!valid" @click="scheduleReport">Schedule</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const dialog = ref(false);
const valid = ref(false);
const scheduleName = ref('');
const frequency = ref('');
const email = ref('');

const frequencies = [
  { label: 'Daily', value: 'daily' },
  { label: 'Weekly', value: 'weekly' },
  { label: 'Monthly', value: 'monthly' }
];

const rules = {
  required: (value: string) => !!value || 'Required',
  email: (value: string) => /.+@.+\..+/.test(value) || 'Invalid email'
};

const scheduleReport = () => {
  // Implementation
  dialog.value = false;
};
</script>