<template>
  <div class="flex align-items-center justify-content-center min-h-screen w-full bg-surface-ground">
    <Toast position="top-right" />
    
    <div class="surface-card p-4 shadow-2 border-round w-full max-w-30rem">
      <div class="text-center mb-5">
        <div class="text-900 text-3xl font-medium mb-2">Welcome Back</div>
        <span class="text-600 font-medium">Please enter your credentials to continue</span>
      </div>

      <form @submit.prevent="handleLogin" @keydown.enter="onFormKeyDown" class="w-full">
        <div class="mb-3">
          <label for="email" class="block text-900 font-medium mb-2">Email</label>
          <InputText
            id="email"
            v-model="form.email"
            type="email"
            placeholder="Enter your email"
            :class="{ 'p-invalid': errors.email }"
            class="w-full"
            autocomplete="username"
          />
          <small v-if="errors.email" class="p-error">{{ errors.email }}</small>
        </div>

        <div class="mb-3">
          <div class="flex align-items-center justify-content-between mb-2">
            <label for="password" class="block text-900 font-medium">Password</label>
            <router-link 
              to="/forgot-password" 
              class="font-medium text-primary hover:underline cursor-pointer"
              style="font-size: 0.875rem"
            >
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
            autocomplete="current-password"
            @keyup.enter="handleLogin"
          />
          <small v-if="errors.password" class="p-error">{{ errors.password }}</small>
        </div>

        <div class="flex align-items-center justify-content-between mb-4">
          <div class="flex align-items-center">
            <Checkbox
              v-model="form.remember"
              :binary="true"
              inputId="remember"
              class="mr-2"
            />
            <label for="remember" class="text-900">Remember me</label>
          </div>
        </div>

        <Button
          type="submit"
          label="Sign In"
          icon="pi pi-sign-in"
          :loading="loading"
          :disabled="!isFormValid"
          class="w-full mb-3"
        />

        <div class="text-center">
          <span class="text-600 font-medium">Don't have an account? </span>
          <router-link to="/register" class="font-medium text-primary hover:underline cursor-pointer">
            Sign up
          </router-link>
        </div>
      </form>
      
      <Divider align="center" class="my-4">
        <span class="text-600 font-normal text-sm">OR</span>
      </Divider>
      
      <Button
        label="Try Demo Account"
        icon="pi pi-user"
        class="p-button-outlined w-full"
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
/* Using PrimeVue and project SCSS variables */
.field {
  margin-bottom: 1.25rem;
}

.field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--text-color);
}

/* Input fields */
:deep(.p-inputtext) {
  width: 100%;
}

/* Error messages */
.p-error {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.875rem;
  color: var(--red-500);
}

/* Forgot password link */
.forgot-password {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--primary-color);
  text-decoration: none;
  transition: color 0.2s;
}

.forgot-password:hover {
  color: var(--primary-600);
  text-decoration: underline;
}

/* Remember me checkbox */
.remember-me {
  display: flex;
  align-items: center;
  margin: 1rem 0;
}

.remember-me label {
  margin-left: 0.5rem;
  cursor: pointer;
  user-select: none;
}

/* Login button */
.login-btn {
  width: 100%;
  margin-top: 1rem;
}

/* Demo login button */
.demo-login-btn {
  width: 100%;
  margin-top: 1rem;
  background-color: var(--surface-ground);
  color: var(--text-color);
  border: 1px solid var(--surface-border);
}

.demo-login-btn:hover {
  background-color: var(--surface-100);
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

