<template>
  <Card>
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
            v-model="form.email"
            type="email"
            placeholder="Enter your email"
            :class="{ 'p-invalid': errors.email }"
            required
          />
          <small v-if="errors.email" class="p-error">{{ errors.email }}</small>
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
            v-model="form.password"
            placeholder="Enter your password"
            :feedback="false"
            toggleMask
            :class="{ 'p-invalid': errors.password }"
            required
          />
          <small v-if="errors.password" class="p-error">{{ errors.password }}</small>
        </div>
        <div class="field-checkbox">
          <Checkbox
            v-model="form.remember"
            :binary="true"
          />
          <label for="remember">Remember me for 30 days</label>
        </div>
        <Button
          type="submit"
          label="Sign In"
          icon="pi pi-sign-in"
          :loading="loading"
          :disabled="!isFormValid || loading"
          class="submit-btn"
        />
        <div class="signup-link">
          <span>Don't have an account? </span>
          <router-link to="/auth/register">Create account</router-link>
        </div>
      </form>
    </template>
  </Card>
  <Toast />
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import axios from 'axios'
import Card from 'primevue/card'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'
import Checkbox from 'primevue/checkbox'
import Avatar from 'primevue/avatar'
import Toast from 'primevue/toast'

const router = useRouter()
const toast = useToast()

const form = reactive({
  email: '',
  password: '',
  remember: false
})

const loading = ref(false)
const errors = reactive({
  email: '',
  password: ''
})

const isFormValid = computed(() => {
  return (
    !!form.email &&
    /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email.trim()) &&
    !!form.password &&
    form.password.length >= 6
  )
})

const validateForm = (): boolean => {
  let isValid = true
  errors.email = ''
  errors.password = ''

  if (!form.email.trim()) {
    errors.email = 'Email is required'
    isValid = false
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email.trim())) {
    errors.email = 'Please enter a valid email address'
    isValid = false
  }

  if (!form.password) {
    errors.password = 'Password is required'
    isValid = false
  } else if (form.password.length < 6) {
    errors.password = 'Password must be at least 6 characters'
    isValid = false
  }

  return isValid
}

const handleLogin = async (): Promise<void> => {
  if (!validateForm()) return

  try {
    loading.value = true

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
    )

    if (response.data.access_token) {
      localStorage.setItem('auth_token', response.data.access_token)
      if (form.remember) {
        localStorage.setItem('rememberedEmail', form.email)
      } else {
        localStorage.removeItem('rememberedEmail')
      }
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Login successful! Redirecting...',
        life: 2000
      })
      setTimeout(() => {
        router.push('/')
      }, 1000)
    }
  } catch (error) {
    console.error('Login error:', error)
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Login failed. Please check your credentials.',
      life: 4000
    })
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  const rememberedEmail = localStorage.getItem('rememberedEmail')
  if (rememberedEmail) {
    form.email = rememberedEmail
    form.remember = true
  }
})
</script>