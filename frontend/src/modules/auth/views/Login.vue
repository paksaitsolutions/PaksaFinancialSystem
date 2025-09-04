<template>
  <div class="login-form">
    <form @submit.prevent="handleLogin">
      <div class="field">
        <label for="email">Email</label>
        <InputText 
          id="email"
          v-model="form.email" 
          type="email"
          placeholder="Enter your email"
          :class="{ 'p-invalid': errors.email }"
          required
        />
        <small v-if="errors.email" class="p-error">{{ errors.email }}</small>
      </div>

      <div class="field">
        <label for="password">Password</label>
        <Password 
          id="password"
          v-model="form.password" 
          placeholder="Enter your password"
          :class="{ 'p-invalid': errors.password }"
          :feedback="false"
          toggleMask
          required
        />
        <small v-if="errors.password" class="p-error">{{ errors.password }}</small>
      </div>

      <div class="field-checkbox">
        <Checkbox id="remember" v-model="form.remember" :binary="true" />
        <label for="remember">Remember me</label>
      </div>

      <Button 
        type="submit" 
        :label="loading ? 'Signing In...' : 'Sign In'"
        class="w-full"
        :loading="loading"
        :disabled="loading"
      />

      <!-- MFA Section -->
      <div v-if="showMFA" class="mfa-section">
        <Divider />
        <div class="field">
          <label for="mfa-code">Two-Factor Authentication</label>
          <InputText
            id="mfa-code"
            v-model="mfaCode"
            placeholder="Enter 6-digit code"
            maxlength="6"
            class="text-center"
          />
        </div>
        <Button
          label="Verify"
          @click="verifyMFA"
          :loading="verifyingMFA"
          class="w-full"
        />
      </div>

      <div class="login-links">
        <router-link to="/auth/forgot-password" class="text-primary">
          Forgot your password?
        </router-link>
        <router-link to="/auth/register" class="text-primary">
          Don't have an account? Sign up
        </router-link>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/api/auth'

const router = useRouter()
const toast = useToast()
const authStore = useAuthStore()

const loading = ref(false)
const showMFA = ref(false)
const mfaCode = ref('')
const verifyingMFA = ref(false)

const form = reactive({
  email: 'admin@paksa.com',
  password: 'admin123',
  remember: false
})

const errors = reactive({
  email: '',
  password: ''
})

const validatePassword = (password: string) => {
  const errors = []
  if (password.length < 8) errors.push('At least 8 characters')
  if (!/[A-Z]/.test(password)) errors.push('One uppercase letter')
  if (!/[a-z]/.test(password)) errors.push('One lowercase letter')
  if (!/\d/.test(password)) errors.push('One number')
  if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) errors.push('One special character')
  return errors
}

const handleLogin = async () => {
  errors.email = ''
  errors.password = ''

  if (!form.email) {
    errors.email = 'Email is required'
    return
  }
  if (!form.password) {
    errors.password = 'Password is required'
    return
  }

  loading.value = true

  try {
    const response = await authApi.login({
      email: form.email,
      password: form.password,
      remember_me: form.remember
    })

    if (response.requiresMFA) {
      showMFA.value = true
      loading.value = false
      return
    }

    authStore.setToken(response.access_token)
    authStore.setUser(response.user)

    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Login successful'
    })

    router.push('/')
  } catch (error: any) {
    if (error.response?.status === 401) {
      errors.password = 'Invalid email or password'
    } else if (error.code === 'ECONNREFUSED') {
      errors.password = 'Cannot connect to server'
    } else {
      errors.password = error.message || 'Login failed'
    }
  } finally {
    loading.value = false
  }
}

const verifyMFA = async () => {
  if (!mfaCode.value || mfaCode.value.length !== 6) {
    toast.add({
      severity: 'error',
      summary: 'Invalid Code',
      detail: 'Please enter a 6-digit code'
    })
    return
  }

  verifyingMFA.value = true

  try {
    const response = await authApi.verifyMFA(mfaCode.value)
    authStore.setToken(response.access_token)
    authStore.setUser(response.user)
    
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Login successful'
    })
    
    router.push('/')
  } catch (error: any) {
    toast.add({
      severity: 'error',
      summary: 'Verification Failed',
      detail: 'Invalid code'
    })
  } finally {
    verifyingMFA.value = false
  }
}
</script>

<style scoped>
.login-form {
  width: 100%;
}

.field {
  margin-bottom: 1rem;
}

.field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: var(--text-color);
}

.field-checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.mfa-section {
  margin-top: 1rem;
}

.text-center {
  text-align: center;
  font-size: 1.2rem;
  letter-spacing: 0.2rem;
}

.login-links {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: 1rem;
  text-align: center;
}

.login-links a {
  text-decoration: none;
  font-size: 0.875rem;
}

.w-full {
  width: 100%;
}
</style>