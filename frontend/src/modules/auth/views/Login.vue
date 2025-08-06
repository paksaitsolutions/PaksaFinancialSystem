<template>
  <div class="login-brand">
    <h2>Welcome Back</h2>
    <p>Sign in to continue to Paksa Financial System</p>
  </div>

  <form @submit.prevent="handleLogin" class="login-form">
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
      <div class="field-header">
        <label for="password">Password</label>
        <router-link to="/auth/forgot-password" class="forgot-link">
          Forgot password?
        </router-link>
      </div>
      <div class="password-input-wrapper">
        <input
          id="password"
          v-model="form.password"
          :type="showPassword ? 'text' : 'password'"
          class="form-input"
          :class="{ error: errors.password }"
          placeholder="Enter your password"
          required
        />
        <button
          type="button"
          class="password-toggle"
          @click="showPassword = !showPassword"
        >
          {{ showPassword ? '👁️' : '👁️‍🗨️' }}
        </button>
      </div>
      <div v-if="errors.password" class="error-message">{{ errors.password }}</div>
    </div>

    <div class="checkbox-field">
      <input
        id="remember"
        v-model="form.remember"
        type="checkbox"
        class="checkbox"
      />
      <label for="remember">Remember me for 30 days</label>
    </div>

    <button
      type="submit"
      class="submit-button"
      :disabled="loading"
    >
      {{ loading ? 'Signing in...' : 'Sign In' }}
    </button>

    <div class="signup-link">
      <span>Don't have an account? </span>
      <router-link to="/auth/register">Create account</router-link>
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import axios from 'axios';

const router = useRouter();
const route = useRoute();

const form = reactive({
  email: '',
  password: '',
  remember: false,
});

const loading = ref(false);
const showPassword = ref(false);
const errors = reactive({
  email: '',
  password: ''
});

const validateForm = (): boolean => {
  let isValid = true;
  errors.email = '';
  errors.password = '';

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

  return isValid;
};

const handleLogin = async () => {
  if (!validateForm()) return;

  try {
    loading.value = true;
    
    const response = await axios.post('/auth/token', 
      new URLSearchParams({
        username: form.email.trim(),
        password: form.password
      }),
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      }
    );
    
    if (response.data.access_token) {
      localStorage.setItem('auth_token', response.data.access_token);
      window.location.href = '/';
    }
  } catch (error) {
    console.error('Login failed:', error);
    errors.password = 'Login failed. Please try again.';
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  const rememberedEmail = localStorage.getItem('rememberedEmail');
  if (rememberedEmail) {
    form.email = rememberedEmail;
    form.remember = true;
  }
});
</script>

<style scoped>
.login-brand {
  text-align: center;
  margin-bottom: 2rem;
}

.login-brand h2 {
  font-size: 1.75rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  color: #1f2937;
}

.login-brand p {
  font-size: 1rem;
  color: #6b7280;
  margin: 0;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.field-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #1f2937;
}

.password-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.form-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.password-input-wrapper .form-input {
  padding-right: 3rem;
}

.password-toggle {
  position: absolute;
  right: 0.75rem;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.2rem;
  color: #6b7280;
  padding: 0.25rem;
  border-radius: 4px;
  transition: color 0.2s;
}

.password-toggle:hover {
  color: #3b82f6;
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

.checkbox-field {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.checkbox {
  width: 1.25rem;
  height: 1.25rem;
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

.forgot-link,
.signup-link a {
  color: #3b82f6;
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
}

.forgot-link:hover,
.signup-link a:hover {
  text-decoration: underline;
}

.signup-link {
  text-align: center;
  font-size: 0.875rem;
  color: #6b7280;
}

@media (max-width: 768px) {
  .login-brand h2 {
    font-size: 1.5rem;
  }
  
  .field-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
}
</style>