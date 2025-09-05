<template>
  <div class="register-container">
    <Card class="register-card">
      <template #header>
        <div class="register-header">
          <img src="/logo.svg" alt="Paksa Financial" class="logo" />
          <h2>Create Account</h2>
          <p>Join Paksa Financial System</p>
        </div>
      </template>
      
      <template #content>
        <form @submit.prevent="handleRegister" class="register-form">
          <div class="grid">
            <div class="col-6">
              <div class="field">
                <label for="firstName">First Name</label>
                <InputText 
                  id="firstName"
                  v-model="form.firstName" 
                  placeholder="First name"
                  class="w-full"
                  :class="{ 'p-invalid': errors.firstName }"
                  required
                />
                <small v-if="errors.firstName" class="p-error">{{ errors.firstName }}</small>
              </div>
            </div>
            <div class="col-6">
              <div class="field">
                <label for="lastName">Last Name</label>
                <InputText 
                  id="lastName"
                  v-model="form.lastName" 
                  placeholder="Last name"
                  class="w-full"
                  :class="{ 'p-invalid': errors.lastName }"
                  required
                />
                <small v-if="errors.lastName" class="p-error">{{ errors.lastName }}</small>
              </div>
            </div>
          </div>
          
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
              placeholder="Create password"
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
              placeholder="Confirm password"
              class="w-full"
              :class="{ 'p-invalid': errors.confirmPassword }"
              :feedback="false"
              toggleMask
              required
            />
            <small v-if="errors.confirmPassword" class="p-error">{{ errors.confirmPassword }}</small>
          </div>
          
          <div class="field-checkbox">
            <Checkbox v-model="form.acceptTerms" inputId="terms" binary />
            <label for="terms">I agree to the Terms and Conditions</label>
          </div>
          
          <Button 
            type="submit" 
            label="Create Account" 
            class="w-full register-btn"
            :loading="loading"
            :disabled="!isFormValid"
          />
        </form>
        
        <div class="register-footer">
          <div class="login-link">
            Already have an account? 
            <router-link to="/auth/login">Sign in</router-link>
          </div>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'

const router = useRouter()
const toast = useToast()

const loading = ref(false)
const form = ref({
  firstName: '',
  lastName: '',
  email: '',
  password: '',
  confirmPassword: '',
  acceptTerms: false
})

const errors = ref({
  firstName: '',
  lastName: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const isFormValid = computed(() => {
  return form.value.firstName && 
         form.value.lastName && 
         form.value.email && 
         form.value.password && 
         form.value.confirmPassword &&
         form.value.acceptTerms &&
         !Object.values(errors.value).some(error => error)
})

const validateForm = () => {
  errors.value = {
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: ''
  }
  
  if (!form.value.firstName) {
    errors.value.firstName = 'First name is required'
  }
  
  if (!form.value.lastName) {
    errors.value.lastName = 'Last name is required'
  }
  
  if (!form.value.email) {
    errors.value.email = 'Email is required'
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.value.email)) {
    errors.value.email = 'Please enter a valid email'
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
  
  return !Object.values(errors.value).some(error => error)
}

const handleRegister = async () => {
  if (!validateForm()) return
  
  loading.value = true
  try {
    // Simulate registration API call
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    toast.add({ 
      severity: 'success', 
      summary: 'Success', 
      detail: 'Account created successfully! Please check your email to verify your account.', 
      life: 5000 
    })
    
    router.push('/auth/login')
  } catch (error: any) {
    toast.add({ 
      severity: 'error', 
      summary: 'Error', 
      detail: error.message || 'Registration failed', 
      life: 5000 
    })
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
}

.register-card {
  width: 100%;
  max-width: 500px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.register-header {
  text-align: center;
  padding: 2rem 2rem 0;
}

.logo {
  height: 60px;
  margin-bottom: 1rem;
}

.register-header h2 {
  margin: 0 0 0.5rem 0;
  color: var(--text-color);
  font-size: 1.75rem;
  font-weight: 600;
}

.register-header p {
  margin: 0;
  color: var(--text-color-secondary);
}

.register-form {
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

.register-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  padding: 0.75rem;
  font-weight: 600;
}

.register-footer {
  text-align: center;
  padding: 0 2rem 2rem;
}

.login-link {
  font-size: 0.875rem;
  color: var(--text-color-secondary);
}

.login-link a {
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 500;
}

.login-link a:hover {
  text-decoration: underline;
}
</style>