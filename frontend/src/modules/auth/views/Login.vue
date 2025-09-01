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
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/api/auth'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(false)
const form = reactive({
  email: 'admin@paksa.com',
  password: 'admin123',
  remember: false
})

const errors = reactive({
  email: '',
  password: ''
})

const handleLogin = async () => {
  // Clear previous errors
  errors.email = ''
  errors.password = ''

  // Basic validation
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
      password: form.password
    })

    // Store token and user data
    authStore.setToken(response.access_token)
    authStore.setUser(response.user)

    // Redirect to dashboard
    router.push('/')
  } catch (error: any) {
    console.error('Login error:', error)
    console.error('Error details:', {
      message: error.message,
      status: error.response?.status,
      data: error.response?.data,
      url: error.config?.url
    })
    if (error.response?.status === 401) {
      errors.password = 'Invalid email or password'
    } else if (error.code === 'ECONNREFUSED' || error.message.includes('Network Error')) {
      errors.password = 'Cannot connect to server. Please check if backend is running.'
    } else {
      errors.password = `Login failed: ${error.message}`
    }
  } finally {
    loading.value = false
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