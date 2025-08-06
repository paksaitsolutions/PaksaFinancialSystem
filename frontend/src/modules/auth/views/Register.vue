<template>
  <div class="register-brand">
    <h2>Create Account</h2>
    <p>Join Paksa Financial System</p>
  </div>

  <form @submit.prevent="handleRegister" class="register-form">
    <div class="form-field">
      <label for="name">Full Name</label>
      <input
        id="name"
        v-model="form.name"
        type="text"
        class="form-input"
        :class="{ error: errors.name }"
        placeholder="Enter your full name"
        required
      />
      <div v-if="errors.name" class="error-message">{{ errors.name }}</div>
    </div>

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

    <div class="form-field">
      <label for="password">Password</label>
      <input
        id="password"
        v-model="form.password"
        type="password"
        class="form-input"
        :class="{ error: errors.password }"
        placeholder="Enter your password"
        required
      />
      <div v-if="errors.password" class="error-message">{{ errors.password }}</div>
    </div>

    <div class="form-field">
      <label for="confirmPassword">Confirm Password</label>
      <input
        id="confirmPassword"
        v-model="form.confirmPassword"
        type="password"
        class="form-input"
        :class="{ error: errors.confirmPassword }"
        placeholder="Confirm your password"
        required
      />
      <div v-if="errors.confirmPassword" class="error-message">{{ errors.confirmPassword }}</div>
    </div>

    <button
      type="submit"
      class="submit-button"
      :disabled="loading"
    >
      {{ loading ? 'Creating Account...' : 'Create Account' }}
    </button>

    <div class="login-link">
      <span>Already have an account? </span>
      <router-link to="/auth/login">Sign in</router-link>
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

const form = reactive({
  name: '',
  email: '',
  password: '',
  confirmPassword: '',
});

const loading = ref(false);
const errors = reactive({
  name: '',
  email: '',
  password: '',
  confirmPassword: ''
});

const validateForm = (): boolean => {
  let isValid = true;
  Object.keys(errors).forEach(key => errors[key] = '');

  if (!form.name.trim()) {
    errors.name = 'Full name is required';
    isValid = false;
  }

  if (!form.email.trim()) {
    errors.email = 'Email is required';
    isValid = false;
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email.trim())) {
    errors.email = 'Please enter a valid email address';
    isValid = false;
  }

  if (!form.password) {
    errors.password = 'Password is required';
    isValid = false;
  } else if (form.password.length < 6) {
    errors.password = 'Password must be at least 6 characters';
    isValid = false;
  }

  if (!form.confirmPassword) {
    errors.confirmPassword = 'Please confirm your password';
    isValid = false;
  } else if (form.password !== form.confirmPassword) {
    errors.confirmPassword = 'Passwords do not match';
    isValid = false;
  }

  return isValid;
};

const handleRegister = async () => {
  if (!validateForm()) return;

  try {
    loading.value = true;
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // Redirect to login after successful registration
    await router.push('/auth/login');
  } catch (error) {
    errors.email = 'Registration failed. Please try again.';
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.register-brand {
  text-align: center;
  margin-bottom: 2rem;
}

.register-brand h2 {
  font-size: 1.75rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  color: #1f2937;
}

.register-brand p {
  font-size: 1rem;
  color: #6b7280;
  margin: 0;
}

.register-form {
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

.login-link {
  text-align: center;
  font-size: 0.875rem;
  color: #6b7280;
}

.login-link a {
  color: #3b82f6;
  text-decoration: none;
  font-weight: 500;
}

.login-link a:hover {
  text-decoration: underline;
}
</style>