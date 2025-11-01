<template>
  <div class="login-container">
    <Card class="login-card">
      <template #header>
        <div class="login-header">
          <img src="/logo.svg" alt="Paksa Financial" class="logo" />
          <h2>Welcome Back</h2>
          <p>Sign in to your account</p>
        </div>
      </template>
      
      <template #content>
        <form @submit.prevent="handleLogin" class="login-form">
          <div class="field">
            <label for="email">Email</label>
            <InputText 
              id="email"
              v-model="form.email" 
              type="email"
              placeholder="Enter your email"
              class="w-full"
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
              class="w-full"
              :class="{ 'p-invalid': errors.password }"
              :feedback="false"
              toggleMask
              required
            />
            <small v-if="errors.password" class="p-error">{{ errors.password }}</small>
          </div>
          
          <div class="field-checkbox">
            <Checkbox v-model="form.rememberMe" inputId="remember" binary />
            <label for="remember">Remember me</label>
          </div>
          
          <Button 
            type="submit" 
            label="Sign In" 
            class="w-full login-btn"
            :loading="loading"
            :disabled="!isFormValid"
          />
        </form>
        
        <div class="login-footer">
          <router-link to="/auth/forgot-password" class="forgot-link">
            Forgot your password?
          </router-link>
          <div class="signup-link">
            Don't have an account? 
            <router-link to="/auth/register">Sign up</router-link>
          </div>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'primevue/usetoast'

const router = useRouter()
const authStore = useAuthStore()
const toast = useToast()

const loading = ref(false)
const form = ref({
  email: '',
  password: '',
  rememberMe: false
})

const errors = ref({
  email: '',
  password: ''
})

const isFormValid = computed(() => {
  return form.value.email && form.value.password && !errors.value.email && !errors.value.password
})

const validateForm = () => {
  errors.value = { email: '', password: '' }
  
  if (!form.value.email) {
    errors.value.email = 'Email is required'
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.value.email)) {
    errors.value.email = 'Please enter a valid email'
  }
  
  if (!form.value.password) {
    errors.value.password = 'Password is required'
  } else if (form.value.password.length < 6) {
    errors.value.password = 'Password must be at least 6 characters'
  }
  
  return !errors.value.email && !errors.value.password
}

const handleLogin = async () => {
  if (!validateForm()) return
  
  loading.value = true
  
  try {
    console.log('Form submission - attempting login...')
    
    const result = await authStore.login({
      email: form.value.email,
      password: form.value.password,
      remember_me: form.value.rememberMe
    })
    
    console.log('Login result:', result)
    
    if (result && result.access_token) {
      console.log('Login successful, showing success message')
      
      toast.add({ 
        severity: 'success', 
        summary: 'Welcome!', 
        detail: 'Login successful', 
        life: 3000 
      })
      
      // Small delay to show success message
      setTimeout(() => {
        console.log('Redirecting to dashboard...')
        router.push('/')
      }, 500)
    } else {
      console.error('No access token in result:', result)
      throw new Error('Invalid response from server')
    }
  } catch (error: any) {
    console.error('Login error in component:', error)
    
    let errorMessage = 'Login failed. Please try again.'
    
    if (error.message) {
      errorMessage = error.message
    } else if (error.response?.data?.detail) {
      errorMessage = error.response.data.detail
    } else if (error.response?.status === 401) {
      errorMessage = 'Invalid email or password'
    } else if (error.response?.status >= 500) {
      errorMessage = 'Server error. Please try again later.'
    }
    
    console.log('Showing error message:', errorMessage)
    
    toast.add({ 
      severity: 'error', 
      summary: 'Login Failed', 
      detail: errorMessage, 
      life: 5000 
    })
    
    // Clear password field on error
    form.value.password = ''
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
}

.login-card {
  width: 100%;
  max-width: 400px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.login-header {
  text-align: center;
  padding: 2rem 2rem 0;
}

.logo {
  height: 60px;
  margin-bottom: 1rem;
}

.login-header h2 {
  margin: 0 0 0.5rem 0;
  color: var(--text-color);
  font-size: 1.75rem;
  font-weight: 600;
}

.login-header p {
  margin: 0;
  color: var(--text-color-secondary);
}

.login-form {
  padding: 2rem;
}

.field {
  margin-bottom: 1.5rem;
}

.field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--text-color);
}

.field-checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.login-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  padding: 0.75rem;
  font-weight: 600;
}

.login-footer {
  text-align: center;
  padding: 0 2rem 2rem;
}

.forgot-link {
  color: var(--primary-color);
  text-decoration: none;
  font-size: 0.875rem;
}

.forgot-link:hover {
  text-decoration: underline;
}

.signup-link {
  margin-top: 1rem;
  font-size: 0.875rem;
  color: var(--text-color-secondary);
}

.signup-link a {
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 500;
}

.signup-link a:hover {
  text-decoration: underline;
}
</style>