<template>
  <div class="forgot-password-container">
    <Card class="forgot-password-card">
      <template #header>
        <div class="forgot-password-header">
          <img src="/logo.svg" alt="Paksa Financial" class="logo" />
          <h2>Reset Password</h2>
          <p>Enter your email to receive reset instructions</p>
        </div>
      </template>
      
      <template #content>
        <form @submit.prevent="handleSubmit" class="forgot-password-form">
          <div class="field">
            <label for="email">Email Address</label>
            <InputText 
              id="email"
              v-model="email" 
              type="email"
              placeholder="Enter your email"
              class="w-full"
              :class="{ 'p-invalid': error }"
              required
            />
            <small v-if="error" class="p-error">{{ error }}</small>
          </div>
          
          <Button 
            type="submit" 
            label="Send Reset Link" 
            class="w-full reset-btn"
            :loading="loading"
            :disabled="!email"
          />
        </form>
        
        <div class="forgot-password-footer">
          <router-link to="/auth/login" class="back-link">
            <i class="pi pi-arrow-left mr-2"></i>
            Back to Login
          </router-link>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'

const router = useRouter()
const toast = useToast()

const loading = ref(false)
const email = ref('')
const error = ref('')

const validateEmail = () => {
  error.value = ''
  
  if (!email.value) {
    error.value = 'Email is required'
    return false
  }
  
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) {
    error.value = 'Please enter a valid email'
    return false
  }
  
  return true
}

const handleSubmit = async () => {
  if (!validateEmail()) return
  
  loading.value = true
  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    toast.add({ 
      severity: 'success', 
      summary: 'Success', 
      detail: 'Password reset link sent to your email', 
      life: 5000 
    })
    
    router.push('/auth/login')
  } catch (error: any) {
    toast.add({ 
      severity: 'error', 
      summary: 'Error', 
      detail: 'Failed to send reset link', 
      life: 5000 
    })
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.forgot-password-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
}

.forgot-password-card {
  width: 100%;
  max-width: 400px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.forgot-password-header {
  text-align: center;
  padding: 2rem 2rem 0;
}

.logo {
  height: 60px;
  margin-bottom: 1rem;
}

.forgot-password-header h2 {
  margin: 0 0 0.5rem 0;
  color: var(--text-color);
  font-size: 1.75rem;
  font-weight: 600;
}

.forgot-password-header p {
  margin: 0;
  color: var(--text-color-secondary);
}

.forgot-password-form {
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

.reset-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  padding: 0.75rem;
  font-weight: 600;
}

.forgot-password-footer {
  text-align: center;
  padding: 0 2rem 2rem;
}

.back-link {
  color: var(--primary-color);
  text-decoration: none;
  font-size: 0.875rem;
  display: inline-flex;
  align-items: center;
}

.back-link:hover {
  text-decoration: underline;
}
</style>