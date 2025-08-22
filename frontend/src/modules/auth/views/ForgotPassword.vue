<template>
  <v-container fluid class="forgot-password-container">
    <v-row justify="center" align="center" class="fill-height">
      <v-col cols="12" sm="8" md="6" lg="4" xl="3">
        <v-card class="forgot-password-card" elevation="12" rounded="lg">
          <!-- Header Section -->
          <v-card-title class="forgot-password-header">
            <div class="text-center w-100">
              <v-avatar size="64" class="mb-4" color="primary">
                <v-icon size="32" color="white">mdi-lock-reset</v-icon>
              </v-avatar>
              <h2 class="text-h4 font-weight-bold mb-2">Reset Password</h2>
              <p class="text-body-1 text-medium-emphasis">
                Enter your email to receive reset instructions
              </p>
            </div>
          </v-card-title>

          <!-- Form Section -->
          <v-card-text class="forgot-password-form">
            <v-form ref="forgotPasswordForm" v-model="formValid" @submit.prevent="handleForgotPassword">
              <!-- Email Field -->
              <v-text-field
                v-model="form.email"
                :rules="emailRules"
                label="Email Address"
                type="email"
                prepend-inner-icon="mdi-email"
                variant="outlined"
                color="primary"
                class="mb-4"
                :disabled="emailSent"
                required
              />

              <!-- Success Message -->
              <v-alert
                v-if="emailSent"
                type="success"
                variant="tonal"
                class="mb-4"
                icon="mdi-check-circle"
              >
                <div class="text-body-2">
                  <strong>Email sent successfully!</strong><br>
                  Please check your inbox for password reset instructions.
                  If you don't see the email, check your spam folder.
                </div>
              </v-alert>

              <!-- Send Instructions Button -->
              <v-btn
                v-if="!emailSent"
                type="submit"
                color="primary"
                size="large"
                block
                :loading="loading"
                :disabled="!formValid"
                class="mb-4"
              >
                <v-icon start>mdi-email-send</v-icon>
                Send Reset Instructions
              </v-btn>

              <!-- Resend Button -->
              <v-btn
                v-else
                color="primary"
                variant="outlined"
                size="large"
                block
                :loading="loading"
                :disabled="resendCooldown > 0"
                @click="handleResend"
                class="mb-4"
              >
                <v-icon start>mdi-email-sync</v-icon>
                {{ resendCooldown > 0 ? `Resend in ${resendCooldown}s` : 'Resend Email' }}
              </v-btn>

              <!-- Divider -->
              <v-divider class="mb-4">
                <span class="text-medium-emphasis px-4">or</span>
              </v-divider>

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
import { ref, reactive, onUnmounted } from 'vue'

// Form data
const form = reactive({
  email: ''
})

// Form validation
const formValid = ref(false)
const forgotPasswordForm = ref()
const loading = ref(false)
const emailSent = ref(false)
const resendCooldown = ref(0)

// Snackbar for notifications
const snackbar = reactive({
  show: false,
  message: '',
  color: 'error',
  timeout: 5000
})

// Timer for resend cooldown
let cooldownTimer: NodeJS.Timeout | null = null

// Validation rules
const emailRules = [
  (v: string) => !!v || 'Email is required',
  (v: string) => /.+@.+\..+/.test(v) || 'Email must be valid'
]

// Methods
const showNotification = (message: string, color: string = 'error') => {
  snackbar.message = message
  snackbar.color = color
  snackbar.show = true
}

const startResendCooldown = () => {
  resendCooldown.value = 60 // 60 seconds cooldown
  cooldownTimer = setInterval(() => {
    resendCooldown.value--
    if (resendCooldown.value <= 0) {
      clearInterval(cooldownTimer!)
      cooldownTimer = null
    }
  }, 1000)
}

const handleForgotPassword = async () => {
  if (!forgotPasswordForm.value?.validate()) return

  try {
    loading.value = true

    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000))

    emailSent.value = true
    startResendCooldown()
    showNotification('Password reset email sent successfully!', 'success')

  } catch (error) {
    console.error('Forgot password error:', error)
    showNotification('Failed to send reset email. Please try again.')
  } finally {
    loading.value = false
  }
}

const handleResend = async () => {
  try {
    loading.value = true

    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500))

    startResendCooldown()
    showNotification('Reset email sent again!', 'success')

  } catch (error) {
    console.error('Resend error:', error)
    showNotification('Failed to resend email. Please try again.')
  } finally {
    loading.value = false
  }
}

// Cleanup
onUnmounted(() => {
  if (cooldownTimer) {
    clearInterval(cooldownTimer)
  }
})
</script>

<style scoped>
.forgot-password-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
}

.forgot-password-container::before {
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

.forgot-password-card {
  position: relative;
  z-index: 1;
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.95) !important;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.forgot-password-header {
  padding: 2rem 2rem 1rem 2rem;
  background: transparent;
}

.forgot-password-form {
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
  .forgot-password-header {
    padding: 1.5rem 1.5rem 1rem 1.5rem;
  }
  
  .forgot-password-form {
    padding: 0 1.5rem 1.5rem 1.5rem;
  }
  
  .forgot-password-card {
    margin: 1rem;
  }
}
</style>