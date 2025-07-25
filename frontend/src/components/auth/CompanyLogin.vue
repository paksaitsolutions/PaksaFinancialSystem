<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="4">
        <v-card class="elevation-12">
          <v-toolbar color="primary" dark flat>
            <v-toolbar-title>Paksa Financial System</v-toolbar-title>
          </v-toolbar>
          
          <v-card-text>
            <v-form ref="form" v-model="valid" @submit.prevent="login">
              <!-- Company Selection -->
              <v-select
                v-model="selectedCompany"
                :items="companies"
                item-title="name"
                item-value="id"
                label="Select Company"
                prepend-icon="mdi-domain"
                :rules="[v => !!v || 'Company is required']"
                required
              />
              
              <!-- Email -->
              <v-text-field
                v-model="email"
                label="Email"
                prepend-icon="mdi-account"
                type="email"
                :rules="emailRules"
                required
              />
              
              <!-- Password -->
              <v-text-field
                v-model="password"
                label="Password"
                prepend-icon="mdi-lock"
                :type="showPassword ? 'text' : 'password'"
                :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                @click:append="showPassword = !showPassword"
                :rules="passwordRules"
                required
              />
              
              <!-- Remember Me -->
              <v-checkbox
                v-model="rememberMe"
                label="Remember me"
              />
            </v-form>
          </v-card-text>
          
          <v-card-actions>
            <v-spacer />
            <v-btn
              color="primary"
              :loading="loading"
              :disabled="!valid"
              @click="login"
            >
              Login
            </v-btn>
          </v-card-actions>
          
          <v-divider />
          
          <v-card-text class="text-center">
            <v-btn text @click="showForgotPassword = true">
              Forgot Password?
            </v-btn>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    
    <!-- Forgot Password Dialog -->
    <v-dialog v-model="showForgotPassword" max-width="400">
      <v-card>
        <v-card-title>Reset Password</v-card-title>
        <v-card-text>
          <v-text-field
            v-model="resetEmail"
            label="Email"
            type="email"
            :rules="emailRules"
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="showForgotPassword = false">Cancel</v-btn>
          <v-btn color="primary" @click="resetPassword">Send Reset Link</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useTenantStore } from '@/stores/tenant'
import { useSnackbar } from '@/composables/useSnackbar'

const router = useRouter()
const authStore = useAuthStore()
const tenantStore = useTenantStore()
const { showSnackbar } = useSnackbar()

const form = ref(null)
const valid = ref(false)
const loading = ref(false)
const showPassword = ref(false)
const showForgotPassword = ref(false)

const selectedCompany = ref('')
const email = ref('')
const password = ref('')
const rememberMe = ref(false)
const resetEmail = ref('')

const companies = ref([])

const emailRules = [
  v => !!v || 'Email is required',
  v => /.+@.+\..+/.test(v) || 'Email must be valid'
]

const passwordRules = [
  v => !!v || 'Password is required',
  v => v.length >= 6 || 'Password must be at least 6 characters'
]

const loadCompanies = async () => {
  try {
    companies.value = await tenantStore.getAvailableCompanies()
  } catch (error) {
    showSnackbar('Failed to load companies', 'error')
  }
}

const login = async () => {
  if (!form.value.validate()) return
  
  loading.value = true
  try {
    await authStore.login({
      email: email.value,
      password: password.value,
      company_id: selectedCompany.value,
      remember_me: rememberMe.value
    })
    
    // Set tenant context
    await tenantStore.setCurrentTenant(selectedCompany.value)
    
    showSnackbar('Login successful', 'success')
    router.push('/dashboard')
    
  } catch (error) {
    showSnackbar(error.message || 'Login failed', 'error')
  } finally {
    loading.value = false
  }
}

const resetPassword = async () => {
  try {
    await authStore.requestPasswordReset(resetEmail.value)
    showSnackbar('Password reset link sent to your email', 'success')
    showForgotPassword.value = false
    resetEmail.value = ''
  } catch (error) {
    showSnackbar('Failed to send reset link', 'error')
  }
}

onMounted(() => {
  loadCompanies()
})
</script>