<template>
  <auth-layout>
    <template #header>
      <h1 class="text-h4 font-weight-bold">Set New Password</h1>
      <p class="text-body-1 text-medium-emphasis">Create a new secure password</p>
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

    <v-form @submit.prevent="handleSubmit" ref="form">
      <v-text-field
        v-model="password"
        label="New Password"
        prepend-inner-icon="mdi-lock"
        :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
        @click:append-inner="showPassword = !showPassword"
        :type="showPassword ? 'text' : 'password'"
        variant="outlined"
        :rules="[
          v => !!v || 'Password is required',
          v => v.length >= 8 || 'Password must be at least 8 characters',
          v => /[A-Z]/.test(v) || 'Password must contain at least one uppercase letter',
          v => /[0-9]/.test(v) || 'Password must contain at least one number'
        ]"
        required
        autocomplete="new-password"
        :disabled="loading || success"
      ></v-text-field>
      
      <v-text-field
        v-model="confirmPassword"
        label="Confirm Password"
        prepend-inner-icon="mdi-lock-check"
        :type="showPassword ? 'text' : 'password'"
        variant="outlined"
        :rules="[
          v => !!v || 'Please confirm your password',
          v => v === password || 'Passwords do not match'
        ]"
        required
        autocomplete="new-password"
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
        Reset Password
      </v-btn>
    </v-form>

    <div class="text-center mt-6">
      <p class="text-body-2">
        <v-btn variant="text" color="primary" to="/auth/login">
          Back to Login
        </v-btn>
      </p>
    </div>
  </auth-layout>
</template>

<script setup>
import { ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import AuthLayout from '@/layouts/AuthLayout.vue';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

// Form state
const form = ref(null);
const password = ref('');
const confirmPassword = ref('');
const showPassword = ref(false);
const error = ref('');
const success = ref('');
const loading = ref(false);

// Get token from URL
const token = route.query.token;

// Handle form submission
const handleSubmit = async () => {
  const { valid } = await form.value.validate();
  
  if (!valid) return;
  
  if (!token) {
    error.value = 'Invalid or expired password reset token';
    return;
  }
  
  try {
    error.value = '';
    loading.value = true;
    
    // Use auth store to reset password
    const result = await authStore.resetPassword(token, password.value);
    
    if (result) {
      success.value = 'Your password has been reset successfully';
      
      // Redirect to login after 2 seconds
      setTimeout(() => {
        router.push('/auth/login');
      }, 2000);
    } else {
      error.value = authStore.error || 'Failed to reset password';
    }
    
  } catch (err) {
    console.error('Password reset failed:', err);
    error.value = 'An error occurred while resetting your password';
  } finally {
    loading.value = false;
  }
};
</script>