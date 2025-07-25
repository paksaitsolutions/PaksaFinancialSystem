<template>
  <v-app>
    <v-main>
      <v-container fluid class="fill-height">
        <v-row align="center" justify="center" class="fill-height">
          <v-col cols="12" sm="8" md="4">
            <v-card class="elevation-12 pa-4">
              <v-card-title class="text-center">
                <div class="d-flex flex-column align-center">
                  <v-img
                    src="/logo.png"
                    alt="Paksa Financial System"
                    max-width="80"
                    class="mb-4"
                  ></v-img>
                  <h2 class="text-h4 font-weight-bold primary--text">
                    Reset Password
                  </h2>
                  <p class="text-subtitle-1 text-center mt-2">
                    Enter your email to receive reset instructions
                  </p>
                </div>
              </v-card-title>

              <v-card-text>
                <v-form ref="form" v-model="valid" @submit.prevent="resetPassword">
                  <v-text-field
                    v-model="email"
                    label="Email Address"
                    type="email"
                    prepend-inner-icon="mdi-email"
                    :rules="emailRules"
                    required
                    outlined
                    class="mb-3"
                  ></v-text-field>

                  <v-alert
                    v-if="successMessage"
                    type="success"
                    class="mb-4"
                  >
                    {{ successMessage }}
                  </v-alert>

                  <v-alert
                    v-if="errorMessage"
                    type="error"
                    class="mb-4"
                    dismissible
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
                    :disabled="!valid || successMessage"
                    class="mb-3"
                  >
                    Send Reset Instructions
                  </v-btn>

                  <div class="text-center">
                    <v-btn
                      text
                      color="primary"
                      @click="$router.push('/auth/login')"
                    >
                      <v-icon class="mr-2">mdi-arrow-left</v-icon>
                      Back to Login
                    </v-btn>
                  </div>
                </v-form>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import { ref } from 'vue'

// Form data
const email = ref('')
const valid = ref(false)
const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

// Validation rules
const emailRules = [
  (v: string) => !!v || 'Email is required',
  (v: string) => /.+@.+\..+/.test(v) || 'Email must be valid'
]

// Reset password function
const resetPassword = async () => {
  if (!valid.value) return

  loading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    // Mock success response
    successMessage.value = `Password reset instructions have been sent to ${email.value}. Please check your email and follow the instructions to reset your password.`
  } catch (error) {
    errorMessage.value = 'Failed to send reset instructions. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.fill-height {
  min-height: 100vh;
}

.v-card {
  border-radius: 12px;
}

.primary--text {
  color: #1976d2 !important;
}
</style>