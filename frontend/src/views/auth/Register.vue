<template>
  <auth-layout>
    <template #header>
      <h1 class="text-h4 font-weight-bold">Create Account</h1>
      <p class="text-body-1 text-medium-emphasis">Join Paksa Financial System</p>
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

    <v-form @submit.prevent="handleRegister" ref="form">
      <v-row>
        <v-col cols="12" sm="6">
          <v-text-field
            v-model="firstName"
            label="First Name"
            prepend-inner-icon="mdi-account"
            variant="outlined"
            :rules="[v => !!v || 'First name is required']"
            required
          ></v-text-field>
        </v-col>
        
        <v-col cols="12" sm="6">
          <v-text-field
            v-model="lastName"
            label="Last Name"
            variant="outlined"
            :rules="[v => !!v || 'Last name is required']"
            required
          ></v-text-field>
        </v-col>
      </v-row>
      
      <v-text-field
        v-model="email"
        label="Email"
        prepend-inner-icon="mdi-email"
        variant="outlined"
        :rules="[
          v => !!v || 'Email is required', 
          v => /.+@.+\..+/.test(v) || 'Email must be valid'
        ]"
        required
        autocomplete="email"
      ></v-text-field>
      
      <v-text-field
        v-model="password"
        label="Password"
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
      ></v-text-field>
      
      <v-checkbox
        v-model="agreeTerms"
        :rules="[v => !!v || 'You must agree to continue']"
        label="I agree to the Terms of Service and Privacy Policy"
        required
      ></v-checkbox>
      
      <v-btn
        type="submit"
        color="primary"
        block
        size="large"
        :loading="loading"
        :disabled="!formValid"
      >
        Create Account
      </v-btn>
    </v-form>

    <div class="text-center mt-6">
      <p class="text-body-2">
        Already have an account?
        <v-btn variant="text" color="primary" to="/auth/login">
          Sign In
        </v-btn>
      </p>
    </div>
  </auth-layout>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import AuthLayout from '@/layouts/AuthLayout.vue';

const authStore = useAuthStore();

const router = useRouter();

// Form state
const form = ref(null);
const firstName = ref('');
const lastName = ref('');
const email = ref('');
const password = ref('');
const confirmPassword = ref('');
const showPassword = ref(false);
const agreeTerms = ref(false);
const error = ref('');
const loading = ref(false);

// Form validation
const formValid = computed(() => {
  return firstName.value && 
         lastName.value && 
         email.value && 
         password.value && 
         confirmPassword.value === password.value && 
         agreeTerms.value;
});

// Handle registration submission
const handleRegister = async () => {
  const { valid } = await form.value.validate();
  
  if (!valid) return;
  
  try {
    error.value = '';
    loading.value = true;
    
    // Use auth store to register user
    const userData = {
      firstName: firstName.value,
      lastName: lastName.value,
      email: email.value,
      password: password.value
    };
    
    const success = await authStore.register(userData);
    
    if (success) {
      // Show success message and redirect to login
      setTimeout(() => {
        router.push('/auth/login?registered=true');
      }, 1500);
    } else {
      error.value = authStore.error || 'Registration failed';
    }
    
  } catch (err) {
    console.error('Registration failed:', err);
    error.value = 'An error occurred during registration';
  } finally {
    loading.value = false;
  }
};
</script>