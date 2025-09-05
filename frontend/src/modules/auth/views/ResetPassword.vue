<template>
  <div class="reset-password-container">
    <Card class="reset-password-card">
      <template #header>
        <div class="reset-password-header">
          <img src="/logo.svg" alt="Paksa Financial" class="logo" />
          <h2>Set New Password</h2>
          <p>Enter your new password</p>
        </div>
      </template>
      
      <template #content>
        <form @submit.prevent="handleSubmit" class="reset-password-form">
          <div class="field">
            <label for="password">New Password</label>
            <Password 
              id="password"
              v-model="form.password" 
              placeholder="Enter new password"
              class="w-full"
              :class="{ 'p-invalid': errors.password }"
              :feedback="true"
              toggleMask
              required
            />
            <small v-if="errors.password" class="p-error">{{ errors.password }}</small>
          </div>
          
          <div class="field">
            <label for="confirmPassword">Confirm Password</label>
            <Password 
              id="confirmPassword"
              v-model="form.confirmPassword" 
              placeholder="Confirm new password"
              class="w-full"
              :class="{ 'p-invalid': errors.confirmPassword }"
              :feedback="false"
              toggleMask
              required
            />
            <small v-if="errors.confirmPassword" class="p-error">{{ errors.confirmPassword }}</small>
          </div>
          
          <Button 
            type="submit" 
            label="Update Password" 
            class="w-full reset-btn"
            :loading="loading"
            :disabled="!isFormValid"
          />
        </form>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useToast } from 'primevue/usetoast'

const router = useRouter()
const route = useRoute()
const toast = useToast()

const loading = ref(false)
const form = ref({
  password: '',
  confirmPassword: ''
})

const errors = ref({
  password: '',
  confirmPassword: ''
})

const isFormValid = computed(() => {
  return form.value.password && 
         form.value.confirmPassword && 
         !errors.value.password && 
         !errors.value.confirmPassword
})

const validateForm = () => {
  errors.value = {
    password: '',
    confirmPassword: ''
  }
  
  if (!form.value.password) {
    errors.value.password = 'Password is required'
  } else if (form.value.password.length < 8) {
    errors.value.password = 'Password must be at least 8 characters'
  }
  
  if (!form.value.confirmPassword) {
    errors.value.confirmPassword = 'Please confirm your password'
  } else if (form.value.password !== form.value.confirmPassword) {
    errors.value.confirmPassword = 'Passwords do not match'
  }
  
  return !errors.value.password && !errors.value.confirmPassword
}

const handleSubmit = async () => {
  if (!validateForm()) return
  
  loading.value = true
  try {
    // Simulate API call with token from route params
    const token = route.params.token
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    toast.add({ 
      severity: 'success', 
      summary: 'Success', 
      detail: 'Password updated successfully', 
      life: 5000 
    })
    
    router.push('/auth/login')
  } catch (error: any) {
    toast.add({ 
      severity: 'error', 
      summary: 'Error', 
      detail: 'Failed to update password', 
      life: 5000 
    })
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.reset-password-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
}

.reset-password-card {
  width: 100%;
  max-width: 400px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.reset-password-header {
  text-align: center;
  padding: 2rem 2rem 0;
}

.logo {
  height: 60px;
  margin-bottom: 1rem;
}

.reset-password-header h2 {
  margin: 0 0 0.5rem 0;
  color: var(--text-color);
  font-size: 1.75rem;
  font-weight: 600;
}

.reset-password-header p {
  margin: 0;
  color: var(--text-color-secondary);
}

.reset-password-form {
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
</style>