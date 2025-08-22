<template>
  <v-container fluid class="reset-password-container">
    <v-row justify="center" align="center" class="fill-height">
      <v-col cols="12" sm="8" md="6" lg="4" xl="3">
        <v-card class="reset-password-card" elevation="12" rounded="lg">
          <!-- Header Section -->
          <v-card-title class="reset-password-header">
            <div class="text-center w-100">
              <v-avatar size="64" class="mb-4" color="primary">
                <v-icon size="32" color="white">mdi-lock-reset</v-icon>
              </v-avatar>
              <h2 class="text-h4 font-weight-bold mb-2">Set New Password</h2>
              <p class="text-body-1 text-medium-emphasis">
                Enter your new password below
              </p>
            </div>
          </v-card-title>

          <!-- Form Section -->
          <v-card-text class="reset-password-form">
            <v-form ref="resetPasswordForm" v-model="formValid" @submit.prevent="handleResetPassword">
              <!-- New Password Field -->
              <v-text-field
                v-model="form.password"
                :rules="passwordRules"
                :type="showPassword ? 'text' : 'password'"
                label="New Password"
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
                label="Confirm New Password"
                prepend-inner-icon="mdi-lock-check"
                :append-inner-icon="showConfirmPassword ? 'mdi-eye' : 'mdi-eye-off'"
                @click:append-inner="showConfirmPassword = !showConfirmPassword"
                variant="outlined"
                color="primary"
                class="mb-4"
                required
              />

              <!-- Password Strength Indicator -->
              <div class="password-strength mb-4">
                <div class="d-flex justify-space-between align-center mb-2">
                  <span class="text-body-2 text-medium-emphasis">Password Strength</span>
                  <span class="text-body-2" :class="strengthColor">{{ strengthText }}</span>
                </div>
                <v-progress-linear
                  :model-value="passwordStrength"
                  :color="strengthColor.replace('text-', '')"
                  height="4"
                  rounded
                />
              </div>

              <!-- Password Requirements -->
              <v-card variant="outlined" class="mb-4">
                <v-card-text class="pa-4">
                  <p class="text-body-2 font-weight-medium mb-3">Password Requirements:</p>
                  <div class="requirements-list">
                    <div 
                      v-for="requirement in passwordRequirements" 
                      :key="requirement.text"
                      class="d-flex align-center mb-1"
                    >
                      <v-icon 
                        :icon="requirement.met ? 'mdi-check-circle' : 'mdi-circle-outline'"
                        :color="requirement.met ? 'success' : 'grey'"
                        size="16"
                        class="mr-2"
                      />
                      <span 
                        class="text-body-2"
                        :class="requirement.met ? 'text-success' : 'text-medium-emphasis'"
                      >
                        {{ requirement.text }}
                      </span>
                    </div>
                  </div>
                </v-card-text>
              </v-card>

              <!-- Reset Password Button -->
              <v-btn
                type="submit"
                color="primary"
                size="large"
                block
                :loading="loading"
                :disabled="!formValid || passwordStrength < 60"
                class="mb-4"
              >
                <v-icon start>mdi-check</v-icon>
                Reset Password
              </v-btn>

              <!-- Back to Login -->
              <div class="text-center">
                <v-btn
                  variant="text"
                  color="primary"
                  :to="{ name: 'Login' }"
                  prepend-icon="mdi-arrow-left"
                >
                  Back to Login
                </v-btn>
              </div>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Success Dialog -->
    <v-dialog v-model="successDialog" max-width="400" persistent>
      <v-card>
        <v-card-text class="text-center pa-6">
          <v-icon icon="mdi-check-circle" color="success" size="64" class="mb-4" />
          <h3 class="text-h6 font-weight-bold mb-3">Password Reset Successful!</h3>
          <p class="text-body-2 text-medium-emphasis mb-4">
            Your password has been successfully reset. You can now sign in with your new password.
          </p>
          <v-btn
            color="primary"
            block
            @click="goToLogin"
          >
            Continue to Login
          </v-btn>
        </v-card-text>
      </v-card>
    </v-dialog>

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
import { ref, reactive, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/modules/auth/store/auth.store'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// Get reset token from route params
const resetToken = route.params.token as string

// Form data
const form = reactive({
  password: '',
  confirmPassword: ''
})

// Form validation
const formValid = ref(false)
const resetPasswordForm = ref()
const loading = ref(false)
const showPassword = ref(false)
const showConfirmPassword = ref(false)
const successDialog = ref(false)

// Snackbar for notifications
const snackbar = reactive({
  show: false,
  message: '',
  color: 'error',
  timeout: 5000
})

// Password strength calculation
const passwordStrength = computed(() => {
  const password = form.password
  let strength = 0
  
  if (password.length >= 8) strength += 20
  if (password.length >= 12) strength += 10
  if (/[a-z]/.test(password)) strength += 20
  if (/[A-Z]/.test(password)) strength += 20
  if (/\d/.test(password)) strength += 15
  if (/[^A-Za-z0-9]/.test(password)) strength += 15
  
  return Math.min(strength, 100)
})

const strengthText = computed(() => {
  if (passwordStrength.value < 30) return 'Weak'
  if (passwordStrength.value < 60) return 'Fair'
  if (passwordStrength.value < 80) return 'Good'
  return 'Strong'
})

const strengthColor = computed(() => {
  if (passwordStrength.value < 30) return 'text-error'
  if (passwordStrength.value < 60) return 'text-warning'
  if (passwordStrength.value < 80) return 'text-info'
  return 'text-success'
})

// Password requirements
const passwordRequirements = computed(() => [
  {
    text: 'At least 8 characters long',
    met: form.password.length >= 8
  },
  {
    text: 'Contains lowercase letter',
    met: /[a-z]/.test(form.password)
  },
  {
    text: 'Contains uppercase letter',
    met: /[A-Z]/.test(form.password)
  },
  {
    text: 'Contains number',
    met: /\d/.test(form.password)
  },
  {
    text: 'Contains special character',
    met: /[^A-Za-z0-9]/.test(form.password)
  }
])

// Validation rules
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

// Methods
const showNotification = (message: string, color: string = 'error') => {
  snackbar.message = message
  snackbar.color = color
  snackbar.show = true
}

const handleResetPassword = async () => {
  if (!resetPasswordForm.value?.validate()) return

  try {
    loading.value = true

    const success = await authStore.resetPassword(resetToken, form.password)

    if (success) {
      successDialog.value = true
    } else {
      const errorMessage = authStore.error || 'Password reset failed. Please try again.'
      showNotification(errorMessage)
    }
  } catch (error) {
    console.error('Reset password error:', error)
    showNotification('An unexpected error occurred. Please try again.')
  } finally {
    loading.value = false
  }
}

const goToLogin = () => {
  successDialog.value = false
  router.push({ name: 'Login' })
}

// Validate token on mount
if (!resetToken) {
  showNotification('Invalid reset token. Please request a new password reset.')
  setTimeout(() => {
    router.push({ name: 'ForgotPassword' })
  }, 3000)
}
</script>

<style scoped>
.reset-password-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
}

.reset-password-container::before {
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

.reset-password-card {
  position: relative;
  z-index: 1;
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.95) !important;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.reset-password-header {
  padding: 2rem 2rem 1rem 2rem;
  background: transparent;
}

.reset-password-form {
  padding: 0 2rem 2rem 2rem;
}

.v-card-title h2 {
  color: #1a1a1a;
}

.v-card-title p {
  color: #666;
}

.password-strength {
  margin-bottom: 1rem;
}

.requirements-list {
  max-height: 120px;
  overflow-y: auto;
}

/* Responsive adjustments */
@media (max-width: 600px) {
  .reset-password-header {
    padding: 1.5rem 1.5rem 1rem 1.5rem;
  }
  
  .reset-password-form {
    padding: 0 1.5rem 1.5rem 1.5rem;
  }
  
  .reset-password-card {
    margin: 1rem;
  }
}
</style>