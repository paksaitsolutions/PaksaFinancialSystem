<template>
  <div class="login-content">
    <div class="login-brand">
      <h2>Welcome Back</h2>
      <p>Sign in to continue to Paksa Financial System</p>
    </div>

    <form @submit.prevent="handleLogin" class="login-form">
      <div class="mb-4">
        <label for="email" class="block text-600 text-sm font-medium mb-2">Email</label>
        <InputText
          id="email"
          v-model="form.email"
          type="email"
          class="w-full"
          placeholder="Enter your email"
          required
        />
      </div>

      <div class="mb-4">
        <div class="flex justify-content-between align-items-center mb-2">
          <label for="password" class="block text-600 text-sm font-medium">Password</label>
          <router-link to="/forgot-password" class="text-primary-500 text-sm font-medium hover:underline">
            Forgot password?
          </router-link>
        </div>
        <Password
          id="password"
          v-model="form.password"
          class="w-full"
          inputClass="w-full"
          :feedback="false"
          toggleMask
          placeholder="Enter your password"
          required
        />
      </div>

      <div class="flex align-items-center mb-6">
        <Checkbox
          v-model="form.remember"
          :binary="true"
          class="mr-2"
          inputId="remember-checkbox"
        />
        <label for="remember-checkbox" class="text-600 text-sm">Remember me</label>
      </div>

      <Button
        type="submit"
        :label="loading ? 'Signing in...' : 'Sign In'"
        class="w-full p-button-primary mb-4"
        :loading="loading"
      />

      <div class="text-center mt-4">
        <span class="text-600 text-sm">Don't have an account? </span>
        <router-link to="/auth/register" class="text-primary-500 font-medium hover:underline">
          Sign up
        </router-link>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/store/auth';
import { useToast } from 'primevue/usetoast';
import InputText from 'primevue/inputtext';
import Password from 'primevue/password';
import Button from 'primevue/button';
import Checkbox from 'primevue/checkbox';

interface LoginCredentials {
  email: string;
  password: string;
  remember: boolean;
}

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const toast = useToast();

const form = reactive<LoginCredentials>({
  email: '',
  password: '',
  remember: false,
});

const loading = ref(false);
const errors = reactive<Record<string, string>>({});

const validateForm = (): boolean => {
  let isValid = true;
  errors['email'] = '';
  errors['password'] = '';

  // Email validation
  if (!form.email) {
    errors['email'] = 'Email is required';
    isValid = false;
  } else if (!/\S+@\S+\.\S+/.test(form.email)) {
    errors['email'] = 'Please enter a valid email address';
    isValid = false;
  }

  // Password validation
  if (!form.password) {
    errors['password'] = 'Password is required';
    isValid = false;
  } else if (form.password.length < 6) {
    errors['password'] = 'Password must be at least 6 characters';
    isValid = false;
  }

  return isValid;
};

const handleLogin = async () => {
  if (!validateForm()) {
    return;
  }

  try {
    loading.value = true;
    
    await authStore.login({
      email: form.email,
      password: form.password,
      remember: form.remember
    });

    // Show success message
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Login successful',
      life: 3000
    } as any);

    // Redirect to dashboard or intended route
    const redirectTo = route.query['redirect'] || '/';
    await router.push({ path: redirectTo as string });
  } catch (error: any) {
    const errorMessage = error.response?.data?.message || 'An error occurred during login';
    
    // Show error message
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: errorMessage,
      life: 5000
    } as any);
  } finally {
    loading.value = false;
  }
};

// Check for remembered email
onMounted(async () => {
  const rememberedEmail = localStorage.getItem('rememberedEmail');
  if (rememberedEmail) {
    form.email = rememberedEmail;
    form.remember = true;
  }
  
  // Clear any existing auth state on login page load
  if (authStore.isAuthenticated && router.currentRoute.value.path === '/login') {
    await router.push('/dashboard');
  }
});
</script>

<style scoped>
/* Base Layout */
.login-content {
  width: 100%;
  max-width: 400px;
  margin: 2rem auto;
  padding: 0 1.5rem;
}

/* Form Styles */
.login-form {
  background: var(--surface-card);
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.login-brand {
  text-align: center;
  margin-bottom: 2rem;
}

.login-brand h2 {
  font-size: 1.75rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  line-height: 1.2;
  color: var(--text-color);
}

.login-brand p {
  font-size: 1rem;
  line-height: 1.5;
  color: var(--text-color-secondary);
  margin: 0;
}

/* Form Elements */
:deep(.p-button) {
  font-weight: 500;
  letter-spacing: 0.025em;
  transition: all 0.2s ease;
  padding: 0.75rem 1.5rem;
}

:deep(.p-button:not(:disabled):hover) {
  transform: translateY(-1px);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

:deep(.p-inputtext) {
  border-radius: 6px;
  border: 1px solid var(--surface-300);
  transition: all 0.2s ease;
  padding: 0.75rem 1rem;
  font-size: 0.9375rem;
  background-color: var(--surface-a);
  color: var(--text-color);
}

:deep(.p-inputtext:enabled:hover) {
  border-color: var(--primary-300);
}

:deep(.p-inputtext:enabled:focus) {
  border-color: var(--primary-500);
  box-shadow: 0 0 0 1px var(--primary-500);
  outline: none;
}

:deep(.p-password) {
  display: block;
  width: 100%;
}

:deep(.p-password-input) {
  width: 100%;
}

/* Checkbox */
:deep(.p-checkbox .p-checkbox-box) {
  border-radius: 4px;
  border: 1px solid var(--surface-300);
  width: 1.25rem;
  height: 1.25rem;
}

:deep(.p-checkbox .p-checkbox-box.p-highlight) {
  background-color: var(--primary-500);
  border-color: var(--primary-500);
}

:deep(.p-checkbox:not(.p-checkbox-disabled) .p-checkbox-box.p-highlight:hover) {
  background-color: var(--primary-600);
  border-color: var(--primary-600);
}

/* Responsive adjustments */
@media (max-width: 576px) {
  .login-content {
    padding: 0 1rem;
  }
  
  .login-form {
    padding: 1.5rem;
  }
}
</style>
