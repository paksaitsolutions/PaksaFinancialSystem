<template>
  <div class="forgot-brand">
    <h2>Reset Password</h2>
    <p>Enter your email to receive reset instructions</p>
  </div>

  <form @submit.prevent="handleReset" class="forgot-form">
    <div class="form-field">
      <label for="email">Email Address</label>
      <input
        id="email"
        v-model="form.email"
        type="email"
        class="form-input"
        :class="{ error: errors.email }"
        placeholder="Enter your email"
        required
      />
      <div v-if="errors.email" class="error-message">{{ errors.email }}</div>
    </div>

    <div v-if="successMessage" class="success-message">
      {{ successMessage }}
    </div>

    <button
      type="submit"
      class="submit-button"
      :disabled="loading || !!successMessage"
    >
      {{ loading ? 'Sending...' : 'Send Reset Instructions' }}
    </button>

    <div class="back-link">
      <router-link to="/auth/login">← Back to Login</router-link>
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';

const form = reactive({
  email: '',
});

const loading = ref(false);
const successMessage = ref('');
const errors = reactive({
  email: ''
});

const validateForm = (): boolean => {
  let isValid = true;
  errors.email = '';

  if (!form.email.trim()) {
    errors.email = 'Email is required';
    isValid = false;
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email.trim())) {
    errors.email = 'Please enter a valid email address';
    isValid = false;
  }

  return isValid;
};

const handleReset = async () => {
  if (!validateForm()) return;

  try {
    loading.value = true;
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    successMessage.value = `Password reset instructions have been sent to ${form.email}. Please check your email.`;
  } catch (error) {
    errors.email = 'Failed to send reset instructions. Please try again.';
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.forgot-brand {
  text-align: center;
  margin-bottom: 2rem;
}

.forgot-brand h2 {
  font-size: 1.75rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  color: #1f2937;
}

.forgot-brand p {
  font-size: 1rem;
  color: #6b7280;
  margin: 0;
}

.forgot-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #1f2937;
}

.form-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-input.error {
  border-color: #ef4444;
}

.error-message {
  color: #ef4444;
  font-size: 0.875rem;
  font-weight: 500;
}

.success-message {
  color: #10b981;
  font-size: 0.875rem;
  font-weight: 500;
  padding: 0.75rem;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 8px;
}

.submit-button {
  width: 100%;
  padding: 0.875rem 1.5rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.submit-button:hover:not(:disabled) {
  background: #2563eb;
}

.submit-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.back-link {
  text-align: center;
}

.back-link a {
  color: #3b82f6;
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
}

.back-link a:hover {
  text-decoration: underline;
}
</style>