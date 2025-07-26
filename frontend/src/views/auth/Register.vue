<template>
  <v-app>
    <v-main>
      <v-container fluid class="fill-height">
        <v-row align="center" justify="center" class="fill-height">
          <v-col cols="12" sm="8" md="5">
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
                    Create Account
                  </h2>
                  <p class="text-subtitle-1 text-center mt-2">
                    Join Paksa Financial System
                  </p>
                </div>
              </v-card-title>

              <v-card-text>
                <v-form ref="form" v-model="valid" @submit.prevent="register">
                  <v-row>
                    <v-col cols="12" md="6">
                      <v-text-field
                        v-model="firstName"
                        label="First Name"
                        prepend-inner-icon="mdi-account"
                        :rules="nameRules"
                        required
                        outlined
                      ></v-text-field>
                    </v-col>
                    <v-col cols="12" md="6">
                      <v-text-field
                        v-model="lastName"
                        label="Last Name"
                        prepend-inner-icon="mdi-account"
                        :rules="nameRules"
                        required
                        outlined
                      ></v-text-field>
                    </v-col>
                  </v-row>

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

                  <v-text-field
                    v-model="confirmPassword"
                    label="Confirm Password"
                    :type="showConfirmPassword ? 'text' : 'password'"
                    prepend-inner-icon="mdi-lock-check"
                    :append-inner-icon="showConfirmPassword ? 'mdi-eye' : 'mdi-eye-off'"
                    @click:append-inner="showConfirmPassword = !showConfirmPassword"
                    :rules="confirmPasswordRules"
                    required
                    outlined
                    class="mb-3"
                  ></v-text-field>

                  <v-checkbox
                    v-model="agreeToTerms"
                    :rules="termsRules"
                    required
                  >
                    <template v-slot:label>
                      <div>
                        I agree to the 
                        <a href="#" @click.prevent>Terms of Service</a>
                        and 
                        <a href="#" @click.prevent>Privacy Policy</a>
                      </div>
                    </template>
                  </v-checkbox>

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
                    Create Account
                  </v-btn>

                  <div class="text-center">
                    <span class="text-body-2">Already have an account?</span>
                    <v-btn
                      text
                      color="primary"
                      @click="$router.push('/auth/login')"
                    >
                      Sign In
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
import { useRouter } from 'vue-router'

const router = useRouter()

// Form data
const firstName = ref('')
const lastName = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const agreeToTerms = ref(false)
const showPassword = ref(false)
const showConfirmPassword = ref(false)
const valid = ref(false)
const loading = ref(false)
const errorMessage = ref('')

// Validation rules
const nameRules = [
  (v: string) => !!v || 'Name is required',
  (v: string) => v.length >= 2 || 'Name must be at least 2 characters'
]

const emailRules = [
  (v: string) => !!v || 'Email is required',
  (v: string) => /.+@.+\..+/.test(v) || 'Email must be valid'
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
  (v: string) => v === password.value || 'Passwords do not match'
]

const termsRules = [
  (v: boolean) => !!v || 'You must agree to the terms and conditions'
]

// Register function
const register = async () => {
  if (!valid.value) return

  loading.value = true
  errorMessage.value = ''

  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // Mock registration logic
    const userData = {
      email: email.value,
      name: `${firstName.value} ${lastName.value}`,
      role: 'user'
    }
    
    // Store auth data
    localStorage.setItem('user', JSON.stringify(userData))
    localStorage.setItem('token', 'mock-jwt-token-new-user')
    
    // Redirect to dashboard
    router.push('/')
  } catch (error) {
    errorMessage.value = 'Registration failed. Please try again.'
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

a {
  color: #1976d2;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}
</style>