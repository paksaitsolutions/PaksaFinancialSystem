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
                    Paksa Financial System
                  </h2>
                  <p class="text-subtitle-1 text-center mt-2">
                    Sign in to your account
                  </p>
                </div>
              </v-card-title>

              <v-card-text>
                <v-form ref="form" v-model="valid" @submit.prevent="login">
                  <v-text-field
                    v-model="email"
                    label="Email"
                    type="email"
                    prepend-inner-icon="mdi-email"
                    :rules="emailRules"
                    required
                    outlined
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
                    outlined
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
                      @click="$router.push('/auth/forgot-password')"
                    >
                      Forgot Password?
                    </v-btn>
                  </div>

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
                    :disabled="!valid"
                    class="mb-3"
                  >
                    Sign In
                  </v-btn>

                  <div class="text-center">
                    <span class="text-body-2">Don't have an account?</span>
                    <v-btn
                      text
                      color="primary"
                      @click="$router.push('/auth/register')"
                    >
                      Sign Up
                    </v-btn>
                  </div>
                </v-form>
              </v-card-text>
            </v-card>

            <!-- Demo Credentials Card -->
            <v-card class="mt-4 elevation-4">
              <v-card-title class="text-h6 text-center">
                <v-icon class="mr-2">mdi-information</v-icon>
                Demo Credentials
              </v-card-title>
              <v-card-text>
                <v-row>
                  <v-col cols="12" md="6">
                    <v-card outlined class="pa-3">
                      <div class="text-subtitle-2 font-weight-bold mb-2">Admin User</div>
                      <div class="text-body-2">Email: admin@paksa.com</div>
                      <div class="text-body-2">Password: admin123</div>
                      <v-btn
                        size="small"
                        color="primary"
                        variant="outlined"
                        class="mt-2"
                        @click="fillDemoCredentials('admin')"
                      >
                        Use Admin
                      </v-btn>
                    </v-card>
                  </v-col>
                  <v-col cols="12" md="6">
                    <v-card outlined class="pa-3">
                      <div class="text-subtitle-2 font-weight-bold mb-2">Regular User</div>
                      <div class="text-body-2">Email: user@paksa.com</div>
                      <div class="text-body-2">Password: user123</div>
                      <v-btn
                        size="small"
                        color="secondary"
                        variant="outlined"
                        class="mt-2"
                        @click="fillDemoCredentials('user')"
                      >
                        Use User
                      </v-btn>
                    </v-card>
                  </v-col>
                </v-row>
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
import { useRouter } from 'vue-router'

const router = useRouter()

// Form data
const email = ref('')
const password = ref('')
const rememberMe = ref(false)
const showPassword = ref(false)
const valid = ref(false)
const loading = ref(false)
const errorMessage = ref('')

// Validation rules
const emailRules = [
  (v: string) => !!v || 'Email is required',
  (v: string) => /.+@.+\..+/.test(v) || 'Email must be valid'
]

const passwordRules = [
  (v: string) => !!v || 'Password is required',
  (v: string) => v.length >= 6 || 'Password must be at least 6 characters'
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
  if (!valid.value) return

  loading.value = true
  errorMessage.value = ''

  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    // Mock authentication logic
    if (email.value === 'admin@paksa.com' && password.value === 'admin123') {
      // Store auth data
      localStorage.setItem('user', JSON.stringify({
        email: email.value,
        name: 'Admin User',
        role: 'admin'
      }))
      localStorage.setItem('token', 'mock-jwt-token-admin')
      
      // Redirect to dashboard
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
      errorMessage.value = 'Invalid email or password. Please try the demo credentials.'
    }
  } catch (error) {
    errorMessage.value = 'Login failed. Please try again.'
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