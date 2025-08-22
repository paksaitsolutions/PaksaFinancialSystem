<template>
  <v-container fluid class="register-container">
    <v-row justify="center" align="center" class="fill-height">
      <v-col cols="12" sm="8" md="6" lg="5" xl="4">
        <v-card class="register-card" elevation="12" rounded="lg">
          <!-- Header Section -->
          <v-card-title class="register-header">
            <div class="text-center w-100">
              <v-avatar size="64" class="mb-4" color="primary">
                <v-icon size="32" color="white">mdi-account-plus</v-icon>
              </v-avatar>
              <h2 class="text-h4 font-weight-bold mb-2">Create Account</h2>
              <p class="text-body-1 text-medium-emphasis">
                Join Paksa Financial System today
              </p>
            </div>
          </v-card-title>

          <!-- Form Section -->
          <v-card-text class="register-form">
            <v-form ref="registerForm" v-model="formValid" @submit.prevent="handleRegister">
              <!-- Full Name Field -->
              <v-text-field
                v-model="form.fullName"
                :rules="nameRules"
                label="Full Name"
                prepend-inner-icon="mdi-account"
                variant="outlined"
                color="primary"
                class="mb-3"
                required
              />

              <!-- Email Field -->
              <v-text-field
                v-model="form.email"
                :rules="emailRules"
                label="Email Address"
                type="email"
                prepend-inner-icon="mdi-email"
                variant="outlined"
                color="primary"
                class="mb-3"
                required
              />

              <!-- Company Field -->
              <v-text-field
                v-model="form.company"
                :rules="companyRules"
                label="Company Name"
                prepend-inner-icon="mdi-office-building"
                variant="outlined"
                color="primary"
                class="mb-3"
                required
              />

              <!-- Password Field -->
              <v-text-field
                v-model="form.password"
                :rules="passwordRules"
                :type="showPassword ? 'text' : 'password'"
                label="Password"
                prepend-inner-icon="mdi-lock"
                :append-inner-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                @click:append-inner="showPassword = !showPassword"
                variant="outlined"
                color="primary"
                class="mb-3"
                required
              />

              <!-- Confirm Password Field -->
              <v-text-field
                v-model="form.confirmPassword"
                :rules="confirmPasswordRules"
                :type="showConfirmPassword ? 'text' : 'password'"
                label="Confirm Password"
                prepend-inner-icon="mdi-lock-check"
                :append-inner-icon="showConfirmPassword ? 'mdi-eye' : 'mdi-eye-off'"
                @click:append-inner="showConfirmPassword = !showConfirmPassword"
                variant="outlined"
                color="primary"
                class="mb-3"
                required
              />

              <!-- Terms and Conditions -->
              <v-checkbox
                v-model="form.acceptTerms"
                :rules="termsRules"
                color="primary"
                class="mb-4"
              >
                <template #label>
                  <span class="text-body-2">
                    I agree to the
                    <v-btn variant="text" color="primary" size="small" class="pa-0">
                      Terms of Service
                    </v-btn>
                    and
                    <v-btn variant="text" color="primary" size="small" class="pa-0">
                      Privacy Policy
                    </v-btn>
                  </span>
                </template>
              </v-checkbox>

              <!-- Register Button -->
              <v-btn
                type="submit"
                color="primary"
                size="large"
                block
                :loading="loading"
                :disabled="!formValid"
                class="mb-4"
              >
                <v-icon start>mdi-account-plus</v-icon>
                Create Account
              </v-btn>

              <!-- Divider -->
              <v-divider class="mb-4">
                <span class="text-medium-emphasis px-4">or</span>
              </v-divider>

              <!-- Login Link -->
              <div class="text-center">
                <span class="text-body-2 text-medium-emphasis">
                  Already have an account?
                </span>
                <v-btn
                  variant="text"
                  color="primary"
                  :to="{ name: 'Login' }"
                  class="ml-1"
                >
                  Sign in
                </v-btn>
              </div>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Loading Overlay -->
    <v-overlay v-model="loading" class="align-center justify-center">
      <v-progress-circular
        color="primary"
        indeterminate
        size="64"
      />
    </v-overlay>

    <!-- Snackbar for notifications -->
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="snackbar.timeout"
      location="top"
    >
      {{ snackbar.message }}
      <template #actions>
        <v-btn
          color="white"
          variant="text"
          @click="snackbar.show = false"
        >
          Close
        </v-btn>
      </template>
    </v-snackbar>
  </v-container>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/modules/auth/store/auth.store'

const router = useRouter()
const authStore = useAuthStore()

// Form data
const form = reactive({
  fullName: '',
  email: '',
  company: '',
  password: '',
  confirmPassword: '',
  acceptTerms: false
})

// Form validation
const formValid = ref(false)
const registerForm = ref()
const loading = ref(false)
const showPassword = ref(false)
const showConfirmPassword = ref(false)

// Snackbar for notifications
const snackbar = reactive({
  show: false,
  message: '',
  color: 'error',
  timeout: 5000
})

// Validation rules
const nameRules = [
  (v: string) => !!v || 'Full name is required',
  (v: string) => v.length >= 2 || 'Name must be at least 2 characters'
]

const emailRules = [
  (v: string) => !!v || 'Email is required',
  (v: string) => /.+@.+\..+/.test(v) || 'Email must be valid'
]

const companyRules = [
  (v: string) => !!v || 'Company name is required',
  (v: string) => v.length >= 2 || 'Company name must be at least 2 characters'
]

const passwordRules = [
  (v: string) => !!v || 'Password is required',
  (v: string) => v.length >= 8 || 'Password must be at least 8 characters',
  (v: string) => /(?=.*[a-z])/.test(v) || 'Password must contain lowercase letter',
  (v: string) => /(?=.*[A-Z])/.test(v) || 'Password must contain uppercase letter',
  (v: string) => /(?=.*\d)/.test(v) || 'Password must contain number'
]

const confirmPasswordRules = [
  (v: string) => !!v || 'Please confirm your password',
  (v: string) => v === form.password || 'Passwords do not match'
]

const termsRules = [
  (v: boolean) => !!v || 'You must accept the terms and conditions'
]

// Methods
const showNotification = (message: string, color: string = 'error') => {
  snackbar.message = message
  snackbar.color = color
  snackbar.show = true
}

const handleRegister = async () => {
  if (!registerForm.value?.validate()) return

  try {
    loading.value = true

    // Simulate registration API call
    await new Promise(resolve => setTimeout(resolve, 2000))

    showNotification('Account created successfully! Please check your email to verify your account.', 'success')
    
    // Redirect to login after successful registration
    setTimeout(() => {
      router.push({ name: 'Login' })
    }, 2000)

  } catch (error) {
    console.error('Registration error:', error)
    showNotification('Registration failed. Please try again.')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
}

.register-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('@/assets/login-bg.jpg') center/cover;
  opacity: 0.1;
  z-index: 0;
}

.register-card {
  position: relative;
  z-index: 1;
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.95) !important;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.register-header {
  padding: 2rem 2rem 1rem 2rem;
  background: transparent;
}

.register-form {
  padding: 0 2rem 2rem 2rem;
}

.v-card-title h2 {
  color: #1a1a1a;
}

.v-card-title p {
  color: #666;
}

/* Responsive adjustments */
@media (max-width: 600px) {
  .register-header {
    padding: 1.5rem 1.5rem 1rem 1.5rem;
  }
  
  .register-form {
    padding: 0 1.5rem 1.5rem 1.5rem;
  }
  
  .register-card {
    margin: 1rem;
  }
}
</style>