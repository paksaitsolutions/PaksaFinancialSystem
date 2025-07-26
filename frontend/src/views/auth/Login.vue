<template>
  <AuthLayout>
    <template #header>
      <h1 class="text-h4 font-weight-bold">Welcome Back</h1>
      <p class="text-body-1 text-medium-emphasis">Sign in to your account</p>
    </template>

    <v-form ref="form" v-model="valid" @submit.prevent="login" lazy-validation>
      <v-text-field
        v-model="email"
        label="Email"
        type="email"
        prepend-inner-icon="mdi-email"
        :rules="emailRules"
        required
        variant="outlined"
        class="mb-3"
      ></v-text-field>

      <v-text-field
        v-model="password"
        label="Password"
        :type="showPassword ? 'text' : 'password'"
        prepend-inner-icon="mdi-lock"
        :append-inner-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
        @click:append-inner="showPassword = !showPassword"
        :rules="passwordRules"
        required
        variant="outlined"
        class="mb-3"
      ></v-text-field>

      <div class="d-flex justify-space-between align-center mb-4">
        <v-checkbox
          v-model="rememberMe"
          label="Remember me"
          hide-details
        ></v-checkbox>
        
        <v-btn
          text
          color="primary"
          size="small"
          @click="$router.push('/auth/forgot-password')"
        >
          Forgot Password?
        </v-btn>
      </div>

      <v-alert
        v-if="errorMessage"
        type="error"
        class="mb-4"
        closable
        @click:close="errorMessage = ''"
      >
        {{ errorMessage }}
      </v-alert>

      <v-btn
        type="submit"
        color="primary"
        size="large"
        block
        :loading="loading"
        class="mb-4"
      >
        Sign In
      </v-btn>

      <v-divider class="mb-4"></v-divider>

      <!-- Demo Credentials -->
      <div class="text-center mb-4">
        <p class="text-caption text-medium-emphasis mb-3">Demo Credentials</p>
        <div class="d-flex gap-2 justify-center flex-wrap">
          <v-btn
            size="small"
            color="primary"
            variant="outlined"
            @click="fillDemoCredentials('admin')"
          >
            Admin Login
          </v-btn>
          <v-btn
            size="small"
            color="secondary"
            variant="outlined"
            @click="fillDemoCredentials('user')"
          >
            User Login
          </v-btn>
        </div>
      </div>

      <div class="text-center">
        <span class="text-body-2">Don't have an account?</span>
        <v-btn
          text
          color="primary"
          size="small"
          @click="$router.push('/auth/register')"
        >
          Sign Up
        </v-btn>
      </div>
    </v-form>
  </AuthLayout>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import AuthLayout from '@/layouts/AuthLayout.vue'

const router = useRouter()

// Form data
const email = ref('')
const password = ref('')
const rememberMe = ref(false)
const showPassword = ref(false)
const valid = ref(true)
const loading = ref(false)
const errorMessage = ref('')

// Validation rules
const emailRules = [
  (v: string) => !!v || 'Email is required'
]

const passwordRules = [
  (v: string) => !!v || 'Password is required'
]

// Demo credentials
const fillDemoCredentials = (type: 'admin' | 'user') => {
  if (type === 'admin') {
    email.value = 'admin@paksa.com'
    password.value = 'admin123'
  } else {
    email.value = 'user@paksa.com'
    password.value = 'user123'
  }
}

// Login function
const login = async () => {
  if (!email.value || !password.value) {
    errorMessage.value = 'Please enter both email and password'
    return
  }

  loading.value = true
  errorMessage.value = ''

  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // Mock authentication logic
    if (email.value === 'admin@paksa.com' && password.value === 'admin123') {
      localStorage.setItem('user', JSON.stringify({
        email: email.value,
        name: 'Admin User',
        role: 'admin'
      }))
      localStorage.setItem('token', 'mock-jwt-token-admin')
      router.push('/')
    } else if (email.value === 'user@paksa.com' && password.value === 'user123') {
      localStorage.setItem('user', JSON.stringify({
        email: email.value,
        name: 'Regular User',
        role: 'user'
      }))
      localStorage.setItem('token', 'mock-jwt-token-user')
      router.push('/')
    } else {
      errorMessage.value = 'Invalid credentials. Use demo accounts: admin@paksa.com/admin123 or user@paksa.com/user123'
    }
  } catch (error) {
    errorMessage.value = 'Login failed. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.gap-2 {
  gap: 0.5rem;
}
</style>