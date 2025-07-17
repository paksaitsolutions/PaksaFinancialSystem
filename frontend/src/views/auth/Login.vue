<template>
  <auth-layout>
    <template #header>
      <h1 class="text-h4 font-weight-bold">Welcome Back</h1>
      <p class="text-body-1 text-medium-emphasis">Sign in to your account</p>
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
      v-if="successMessage"
      type="success"
      variant="tonal"
      closable
      class="mb-4"
    >
      {{ successMessage }}
    </v-alert>

    <v-form @submit.prevent="handleLogin">
      <v-text-field
        v-model="email"
        label="Email"
        prepend-inner-icon="mdi-email"
        variant="outlined"
        :rules="[v => !!v || 'Email is required', v => /.+@.+\..+/.test(v) || 'Email must be valid']"
        required
        autocomplete="email"
        :disabled="loading"
      ></v-text-field>

      <v-text-field
        v-model="password"
        label="Password"
        prepend-inner-icon="mdi-lock"
        :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
        @click:append-inner="showPassword = !showPassword"
        :type="showPassword ? 'text' : 'password'"
        variant="outlined"
        :rules="[v => !!v || 'Password is required']"
        required
        autocomplete="current-password"
        :disabled="loading"
      ></v-text-field>

      <div class="d-flex align-center justify-space-between mb-6">
        <v-checkbox
          v-model="rememberMe"
          label="Remember me"
          hide-details
          density="compact"
        ></v-checkbox>
        <v-btn variant="text" color="primary" size="small" to="/auth/forgot-password">
          Forgot Password?
        </v-btn>
      </div>

      <v-btn
        type="submit"
        color="primary"
        block
        size="large"
        :loading="loading"
      >
        Sign In
      </v-btn>
    </v-form>

    <div class="text-center mt-6">
      <p class="text-body-2">
        Don't have an account?
        <v-btn variant="text" color="primary" to="/auth/register">
          Sign Up
        </v-btn>
      </p>
    </div>
  </auth-layout>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useAuth } from '@/composables/useAuth';
import AuthLayout from '@/layouts/AuthLayout.vue';

const route = useRoute();
const { login, loading } = useAuth(); // ✅ using loading from composable

// Form state
const email = ref('admin@example.com');
const password = ref('password');
const showPassword = ref(false);
const rememberMe = ref(false);
const error = ref('');
const successMessage = ref('');

// Display success messages based on query params
onMounted(() => {
  if (route.query.registered === 'true') {
    successMessage.value = 'Registration successful! Please sign in with your new account.';
  }
  if (route.query.reset === 'true') {
    successMessage.value = 'Password reset successful! Please sign in with your new password.';
  }
});

// Login submission
const handleLogin = async () => {
  error.value = '';
  try {
    const success = await login({
      email: email.value,
      password: password.value,
      rememberMe: rememberMe.value
    });

    if (!success) {
      error.value = 'Invalid email or password';
    }
  } catch (err) {
    console.error('Login error:', err);
    error.value = 'An error occurred during login';
  }
};
</script>
