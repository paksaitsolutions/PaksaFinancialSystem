<template>
  <v-dialog v-model="dialog" max-width="500px">
    <v-card>
      <v-card-title>Change Password</v-card-title>
      <v-card-text>
        <v-form ref="form" v-model="valid">
          <v-text-field
            v-model="currentPassword"
            label="Current Password"
            type="password"
            :rules="[rules.required]"
            required
          />
          <v-text-field
            v-model="newPassword"
            label="New Password"
            type="password"
            :rules="[rules.required, rules.minLength]"
            required
          />
          <v-text-field
            v-model="confirmPassword"
            label="Confirm Password"
            type="password"
            :rules="[rules.required, rules.match]"
            required
          />
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn text @click="dialog = false">Cancel</v-btn>
        <v-btn color="primary" :disabled="!valid" @click="changePassword">Change</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';

const dialog = ref(false);
const valid = ref(false);
const currentPassword = ref('');
const newPassword = ref('');
const confirmPassword = ref('');

const rules = {
  required: (value: string) => !!value || 'Required',
  minLength: (value: string) => value.length >= 8 || 'Minimum 8 characters',
  match: computed(() => (value: string) => value === newPassword.value || 'Passwords must match')
};

const changePassword = () => {
  // Implementation
  dialog.value = false;
};
</script>