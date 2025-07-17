<template>
  <auth-layout>
    <template #header>
      <h1 class="text-h4 font-weight-bold">Reset Password</h1>
      <p class="text-body-1 text-medium-emphasis">Enter your email to receive reset instructions</p>
    </template>

    <v-alert
      v-if="error"
      type="error"
      variant="tonal"
      closable
      class="mb-4"
    >
      {{ error }}
    </v-alert>

    <v-alert
      v-if="success"
      type="success"
      variant="tonal"
      closable
      class="mb-4"
    >
      {{ success }}
    </v-alert>

    <v-form @submit.prevent="handleSubmit">
      <v-text-field
        v-model="email"
        label="Email"
        prepend-inner-icon="mdi-email"
        variant="outlined"
        :rules="[v => !!v || 'Email is required', v => /.+@.+\..+/.test(v) || 'Email must be valid']"
        required
        autocomplete="email"
        :disabled="loading || success"
      ></v-text-field>
      
      <v-btn
        type="submit"
        color="primary"
        block
        size="large"
        :loading="loading"
        :disabled="success"
      >
        Send Reset Link
      </v-btn>
    </v-form>

    <div class="text-center mt-6">
      <p class="text-body-2">
        Remember your password?
        <v-btn variant="text" color="primary" to="/auth/login">
          Back to Login
        </v-btn>
      </p>
    </div>
  </auth-layout>
</template>

<script setup>
import { ref } from 'vue';
import { useAuth } from '@/composables/useAuth';
import AuthLayout from '@/layouts/AuthLayout.vue';

const { forgotPassword, loading } = useAuth();

// Form state
const email = ref('');
const error = ref('');
const success = ref('');

// Handle form submission
const handleSubmit = async () => {
  if (!email.value || !/.+@.+\..+/.test(email.value)) {
    error.value = 'Please enter a valid email address';
    return;
  }
  
  try {
    error.value = '';
    success.value = '';
    
    // Use forgotPassword from useAuth composable
    const result = await forgotPassword(email.value);
    
    if (result) {
      success.value = `Password reset instructions have been sent to ${email.value}`;
    } else {
      error.value = 'Failed to send reset instructions';
    }
    
  } catch (err) {
    console.error('Password reset request failed:', err);
    error.value = 'An error occurred while processing your request';
  }
};
</script>