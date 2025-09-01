<template>
  <div class="login-container">
    <Card class="login-card">
      <template #header>
        <div class="login-header">
          <Avatar icon="pi pi-user" size="xlarge" />
          <h2>Welcome Back</h2>
          <p>Sign in to continue to Paksa Financial System</p>
        </div>
      </template>

      <template #content>
        <form @submit.prevent="handleLogin" class="login-form">
          <div class="field">
            <label for="email">Email Address</label>
            <InputText
              id="email"
              :model-value="formData.email"
              @update:model-value="(val: string | undefined) => { if (val !== undefined) formData.email = val }"
              type="email"
              placeholder="Enter your email"
              :class="{ 'p-invalid': formErrors.email }"
              required
              autocomplete="username"
            />
            <small v-if="formErrors.email" class="p-error">{{ formErrors.email }}</small>
          </div>

          <div class="field">
            <div class="password-header">
              <label for="password">Password</label>
              <router-link to="/auth/forgot-password" class="forgot-link">
                Forgot password?
              </router-link>
            </div>
            <Password
              id="password"
              :model-value="formData.password"
              @update:model-value="(val: string | undefined) => { if (val !== undefined) formData.password = val }"
              placeholder="Enter your password"
              :feedback="false"
              toggleMask
              :class="{ 'p-invalid': formErrors.password }"
              required
              autocomplete="current-password"
            />
            <small v-if="formErrors.password" class="p-error">{{ formErrors.password }}</small>
          </div>

          <div class="field-checkbox">
            <Checkbox
              :model-value="formData.remember"
              @update:model-value="(val: boolean | undefined) => { if (val !== undefined) formData.remember = val }"
              :binary="true"
              input-id="remember"
            />
            <label for="remember" class="ml-2">Remember me for 30 days</label>
          </div>

          <div v-if="loginMessage" :class="['login-message', messageType]">
            {{ loginMessage }}
          </div>

          <Button
            type="submit"
            :label="isLoading ? 'Signing in...' : 'Sign In'"
            :icon="isLoading ? 'pi pi-spin pi-spinner' : 'pi pi-sign-in'"
            :loading="isLoading"
            :disabled="!isFormValid || isLoading"
            class="submit-btn"
          />

          <div class="signup-link">
            <span>Don't have an account? </span>
            <router-link to="/auth/register">Create account</router-link>
          </div>
        </form>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import { useAuthStore } from '@/stores/auth'
import Card from 'primevue/card'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Checkbox from 'primevue/checkbox'
import Avatar from 'primevue/avatar'
import axios, { AxiosError } from 'axios'

interface LoginForm {
  email: string;
  password: string;
  remember: boolean;
}

const defaultFormData: LoginForm = {
  email: '',
  password: '',
  remember: false
};

interface FormErrors {
  email?: string
  password?: string
  [key: string]: string | undefined
}

interface LoginResponse {
  access_token: string
  user?: {
    id: string
    email: string
    firstName: string
    lastName: string
    roles: string[]
    permissions: string[]
    isAdmin: boolean
  }
}

const router = useRouter()
const toast = useToast()
const authStore = useAuthStore()

const formData = ref<LoginForm>({ ...defaultFormData });

const formErrors = ref<FormErrors>({})
const isLoading = ref(false)
const loginMessage = ref('')
const messageType = ref('')

const isFormValid = computed((): boolean => {
  return Boolean(
    formData.value.email && 
    formData.value.password && 
    formData.value.email.includes('@') && 
    formData.value.password.length >= 8
  )
})

const validateForm = (): boolean => {
  formErrors.value = {}
  
  if (!formData.value.email) {
    formErrors.value.email = 'Email is required'
  } else if (!/\S+@\S+\.\S+/.test(formData.value.email)) {
    formErrors.value.email = 'Please enter a valid email address'
  }
  
  if (!formData.value.password) {
    formErrors.value.password = 'Password is required'
  } else if (formData.value.password.length < 8) {
    formErrors.value.password = 'Password must be at least 8 characters'
  }
  
  return Object.keys(formErrors.value).length === 0
}

const handleLogin = async (): Promise<void> => {
  if (!validateForm()) return
  
  isLoading.value = true
  loginMessage.value = ''
  messageType.value = ''
  
  try {
    const response = await axios.post<LoginResponse>(
      '/api/v1/auth/login',
      {
        email: formData.value.email,
        password: formData.value.password
      },
      {
        headers: {
          'Content-Type': 'application/json'
        }
      }
    )
    
    if (response.data.access_token) {
      // Store the token
      authStore.setToken(response.data.access_token)
      
      // Store user data if available
      if (response.data.user) {
        const userData = {
          ...response.data.user,
          // Ensure all required user properties are set
          firstName: response.data.user.firstName || '',
          lastName: response.data.user.lastName || '',
          roles: response.data.user.roles || [],
          permissions: response.data.user.permissions || [],
          isAdmin: response.data.user.isAdmin || false
        }
        authStore.setUser(userData)
      }
      
      // Handle remember me
      if (formData.value.remember) {
        localStorage.setItem('rememberedEmail', formData.value.email)
      } else {
        localStorage.removeItem('rememberedEmail')
      }
      
      // Show success message
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Login successful!',
        life: 3000
      })
      
      // Redirect to dashboard or intended URL
      const redirectPath = router.currentRoute.value.query['redirect'] as string || '/dashboard'
      await router.push(redirectPath)
    }
  } catch (error) {
    const axiosError = error as AxiosError<{ message?: string }>
    
    if (axiosError.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      loginMessage.value = axiosError.response.data?.message || 'Login failed. Please check your credentials.'
      messageType.value = 'error'
      
      toast.add({
        severity: 'error',
        summary: 'Error',
        detail: loginMessage.value,
        life: 5000
      })
    } else if (axiosError.request) {
      // The request was made but no response was received
      loginMessage.value = 'No response from server. Please try again later.'
      messageType.value = 'error'
    } else {
      // Something happened in setting up the request that triggered an Error
      loginMessage.value = 'An error occurred. Please try again.'
      messageType.value = 'error'
    }
  } finally {
    isLoading.value = false
  }
}

// Check for remembered email on component mount
onMounted(() => {
  const rememberedEmail = localStorage.getItem('rememberedEmail')
  if (rememberedEmail) {
    formData.value = {
      ...formData.value,
      email: rememberedEmail,
      remember: true
    }
  }
})
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f7fa;
  padding: 1rem;
  background-image: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
}

.login-card {
  width: 100%;
  max-width: 420px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08);
  border: none;
  border-radius: 12px;
  overflow: hidden;
  background: white;
}

.login-header {
  text-align: center;
  padding: 2rem 1.5rem 1.5rem;
  background: linear-gradient(135deg, #3498db 0%, #2c3e50 100%);
  color: white;
  margin: -1px -1px 0 -1px;
  border-radius: 12px 12px 0 0;
}

.login-header h2 {
  margin: 1rem 0 0.5rem;
  color: white;
  font-size: 1.75rem;
  font-weight: 600;
}

.login-header p {
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
  font-size: 0.95rem;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 2rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

:deep(.p-password-input) {
  width: 100%;
}

:deep(.p-checkbox .p-checkbox-box) {
  border-color: var(--surface-400);
}

:deep(.p-checkbox .p-checkbox-box.p-highlight) {
  background: var(--primary-color);
  border-color: var(--primary-color);
}

:deep(.p-checkbox:not(.p-checkbox-disabled) .p-checkbox-box.p-focus) {
  box-shadow: 0 0 0 0.2rem var(--primary-100);
  border-color: var(--primary-color);
}

.field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--text-color);
}

.password-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.forgot-link {
  color: var(--primary-color);
  text-decoration: none;
  font-size: 0.875rem;
}

.forgot-link:hover {
  text-decoration: underline;
}

.field-checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.field-checkbox label {
  margin: 0;
  font-size: 0.875rem;
}

.submit-btn {
  width: 100%;
  padding: 0.75rem;
  background: var(--primary-color, #007bff);
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  margin-bottom: 1rem;
  transition: background-color 0.2s;
}

.submit-btn:hover:not(:disabled) {
  background: var(--primary-color-dark, #0056b3);
}

.submit-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.signup-link {
  text-align: center;
  font-size: 0.875rem;
}

.signup-link a {
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 500;
}

.signup-link a:hover {
  text-decoration: underline;
}

input[type="email"], input[type="password"] {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

input[type="email"]:focus, input[type="password"]:focus {
  outline: none;
  border-color: var(--primary-color);
}

input.error {
  border-color: #e74c3c;
}

.error-text {
  color: #e74c3c;
  font-size: 0.75rem;
  margin-top: 0.25rem;
  display: block;
}

.message {
  padding: 0.75rem;
  margin: 1rem 2rem;
  border-radius: 4px;
  text-align: center;
}

.message.success {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.message.error {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}
</style>
