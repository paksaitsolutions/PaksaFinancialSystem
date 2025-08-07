<template>
  <div class="login-container">
    <Toast position="top-right" />
    <div class="login-card">
      <div class="login-header">
        <h2>Welcome Back</h2>
        <p>Please enter your credentials to continue</p>
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="email">Email</label>
          <InputText
            id="email"
            v-model="form.email"
            type="email"
            placeholder="Enter your email"
            :class="{ 'p-invalid': errors.email }"
            class="w-full"
          />
          <small v-if="errors.email" class="error-message">{{ errors.email }}</small>
        </div>

        <div class="form-group">
          <div class="password-header">
            <label for="password">Password</label>
            <router-link to="/forgot-password" class="forgot-password">
              Forgot password?
            </router-link>
          </div>
          <Password
            id="password"
            v-model="form.password"
            :feedback="false"
            :toggleMask="true"
            placeholder="Enter your password"
            :class="{ 'p-invalid': errors.password }"
            class="w-full"
            inputClass="w-full"
            @keyup.enter="handleLogin"
          />
          <small v-if="errors.password" class="error-message">{{ errors.password }}</small>
        </div>

        <div class="remember-me">
          <Checkbox
            v-model="form.remember"
            :binary="true"
            inputId="remember"
            class="mr-2"
          />
          <label for="remember">Remember me</label>
        </div>

        <Button
          type="submit"
          label="Sign In"
          icon="pi pi-sign-in"
          :loading="loading"
          :disabled="!isFormValid"
          class="login-button"
        />

        <div class="signup-link">
          Don't have an account? 
          <router-link to="/register">Sign up</router-link>
        </div>
      </form>
      
      <div class="divider">
        <span>OR</span>
      </div>
      
      <Button
        label="Try Demo Account"
        icon="pi pi-user"
        class="demo-button"
        @click="handleDemoLogin"
        :loading="loading"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useToast } from 'primevue/usetoast';
import { useAuthStore } from '@/modules/auth/store/auth.store';
import InputText from 'primevue/inputtext';
import Password from 'primevue/password';
import Button from 'primevue/button';
import Checkbox from 'primevue/checkbox';
import Toast from 'primevue/toast';

// Types
interface LoginForm {
  email: string;
  password: string;
  remember: boolean;
}

type FormErrors = {
  email?: string;
  password?: string;
};

// Composables
const router = useRouter();
const toast = useToast();
const authStore = useAuthStore();

// Form state
const form = reactive<LoginForm>({
  email: '',
  password: '',
  remember: false
});

const loading = ref(false);
const errors = reactive<FormErrors>({});

// Computed Properties
const isFormValid = computed<boolean>(() => {
  return (
    form.email.trim() !== '' &&
    /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email.trim()) &&
    form.password.length >= 6
  );
});

// Methods
const validateForm = (): boolean => {
  // Reset errors with proper type safety
  const errorKeys: Array<keyof FormErrors> = Object.keys(errors) as Array<keyof FormErrors>;
  errorKeys.forEach((key) => {
    errors[key] = ''; // Use empty string instead of undefined for type safety
  });

  let isValid = true;

  // Email validation
  if (!form.email.trim()) {
    errors.email = 'Email is required';
    isValid = false;
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email.trim())) {
    errors.email = 'Please enter a valid email address';
    isValid = false;
  }

  // Password validation
  if (!form.password) {
    errors.password = 'Password is required';
    isValid = false;
  } else if (form.password.length < 6) {
    errors.password = 'Password must be at least 6 characters';
    isValid = false;
  }

  return isValid;
};

const handleLogin = async (): Promise<void> => {
  if (!validateForm()) {
    return;
  }
  
  loading.value = true;
  
  try {
    const success = await authStore.login({
      email: form.email.trim(),
      password: form.password,
      rememberMe: form.remember
    });
    
    if (success) {
      // Redirect to dashboard or intended route
      const redirectPath = (router.currentRoute.value.query['redirect'] as string) || '/dashboard';
      await router.push(redirectPath);
      
      // Show success message
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Login successful',
        life: 3000
      });
    } else if (authStore.error) {
      // Show error from auth store
      toast.add({
        severity: 'error',
        summary: 'Login Failed',
        detail: authStore.error,
        life: 5000
      });
    }
  } catch (error) {
    console.error('Login error:', error);
    
    // Show generic error message
    toast.add({
      severity: 'error',
      summary: 'Login Failed',
      detail: 'An unexpected error occurred. Please try again.',
      life: 5000
    });
  } finally {
    loading.value = false;
  }
};

// Demo login handler
const handleDemoLogin = async (): Promise<void> => {
  // Set demo credentials
  form.email = 'demo@example.com';
  form.password = 'demo123';
  form.remember = false;
  
  // Small delay to show the demo credentials in the form
  await new Promise(resolve => setTimeout(resolve, 300));
  
  // Trigger login with demo credentials
  await handleLogin();
};

// Handle form submission on enter key
const onFormKeyDown = (event: KeyboardEvent) => {
  if (event.key === 'Enter' && isFormValid) {
    handleLogin();
  }
};

// Lifecycle hooks
onMounted(async () => {
  // Initialize auth store
  const isAuthenticated = await authStore.initialize();
  
  // If already authenticated, redirect to dashboard
  if (isAuthenticated) {
    router.push('/dashboard');
    return;
  }
  
  // Check for remembered email
  const rememberedEmail = localStorage.getItem('rememberedEmail');
  if (rememberedEmail) {
    form.email = rememberedEmail;
    form.remember = true;
  }
  
  // Check for password reset success message
  const resetSuccess = router.currentRoute.value.query['reset_success'];
  if (resetSuccess) {
    toast.add({
      severity: 'success',
      summary: 'Password Reset',
      detail: 'Your password has been reset successfully. Please log in with your new password.',
      life: 5000
    });
  }
});
</script>

<style scoped>
/* Base Styles */
.login-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 1rem;
  background-color: var(--surface-ground);
}

.login-card {
  width: 100%;
  max-width: 400px;
  background: var(--surface-card);
  padding: 2rem;
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-2);
}

/* Header */
.login-header {
  text-align: center;
  margin-bottom: 2rem;
}

.login-header h2 {
  color: var(--text-color);
  margin: 0 0 0.5rem;
  font-size: 1.75rem;
}

.login-header p {
  color: var(--text-color-secondary);
  margin: 0;
}

/* Form */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

label {
  font-weight: 500;
  color: var(--text-color);
}

/* Password Header */
.password-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.forgot-password {
  font-size: 0.875rem;
  color: var(--primary-color);
  text-decoration: none;
}

.forgot-password:hover {
  text-decoration: underline;
}

/* Remember Me */
.remember-me {
  display: flex;
  align-items: center;
  margin: 0.5rem 0;
}

/* Buttons */
.login-button,
.demo-button {
  width: 100%;
  margin-top: 1rem;
}

.demo-button {
  background: transparent;
  border: 1px solid var(--primary-color);
  color: var(--primary-color);
}

.demo-button:hover {
  background: rgba(var(--primary-color-rgb), 0.05);
}

/* Sign Up Link */
.signup-link {
  text-align: center;
  margin-top: 1rem;
  color: var(--text-color-secondary);
}

.signup-link a {
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 500;
  margin-left: 0.25rem;
}

.signup-link a:hover {
  text-decoration: underline;
}

/* Divider */
.divider {
  display: flex;
  align-items: center;
  margin: 1.5rem 0;
  color: var(--text-color-secondary);
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  border-bottom: 1px solid var(--surface-border);
}

.divider span {
  padding: 0 1rem;
  font-size: 0.875rem;
}

/* Error Message */
.error-message {
  color: var(--red-500);
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

/* Responsive */
@media (max-width: 576px) {
  .login-card {
    padding: 1.5rem;
  }
  
  .login-header h2 {
    font-size: 1.5rem;
  }
  
  .login-header p {
    font-size: 0.9rem;
  }
}

@media (max-height: 700px) {
  .login-container {
    align-items: flex-start;
    padding: 1rem;
  }
  
  .login-card {
    margin: 1rem 0;
  }
}

/* Register link */
.register-link {
  display: block;
  text-align: center;
  margin-top: 1.5rem;
  color: var(--text-color-secondary);
}

.register-link a {
  color: var(--primary-color);
  font-weight: 500;
  text-decoration: none;
  margin-left: 0.25rem;
}

.register-link a:hover {
  text-decoration: underline;
}

/* Responsive adjustments */
@media (max-width: 480px) {
  .login-container {
    padding: 1rem;
  }
  
  .login-card {
    padding: 1.5rem;
  }
  
  .login-header h1 {
    font-size: 1.5rem;
  }
}
</style>

