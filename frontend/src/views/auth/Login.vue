<template>
  <div class="login-container">
    <v-card class="login-card" max-width="450" elevation="2">
      <v-card-item>
        <div class="d-flex justify-center mb-4">
          <v-img src="/favicon.svg" width="60" height="60" alt="Logo"></v-img>
        </div>
        <v-card-title class="text-center text-h4 font-weight-bold">
          Welcome Back
        </v-card-title>
        
        <v-card-subtitle class="text-center">
          Sign in to your Paksa Financial account
        </v-card-subtitle>
      </v-card-item>
      
      <v-card-text>
        <v-alert
          v-if="error"
          type="error"
          variant="tonal"
          closable
          class="mb-4"
          @click:close="error = ''"
        >
          {{ error }}
        </v-alert>
        
        <v-alert
          v-if="successMessage"
          type="success"
          variant="tonal"
          closable
          class="mb-4"
          @click:close="successMessage = ''"
        >
          {{ successMessage }}
        </v-alert>
        
        <v-form @submit.prevent="handleLogin" ref="form">
          <v-text-field
            v-model="email"
            label="Email"
            prepend-inner-icon="mdi-email"
            variant="outlined"
            :rules="[validationRules.required, validationRules.email]"
            required
            autocomplete="email"
            :disabled="loading"
            @keyup.enter="handleLogin"
            hint="Enter your registered email address"
            persistent-hint
          ></v-text-field>
          
          <v-card-text>
            <v-alert
              v-if="error"
              type="error"
              class="mb-4"
              dismissible
              @input="error = ''"
            >
              {{ error }}
            </v-alert>
            
            <v-form @submit.prevent="handleLogin" v-if="!isLocked">
              <v-text-field
                v-model="email"
                label="Email"
                type="email"
                prepend-icon="mdi-account"
                :error-messages="emailErrors"
                @input="$v.email.$touch()"
                @blur="$v.email.$touch()"
                required
                outlined
                dense
                :disabled="loading"
              ></v-text-field>
              
              <v-text-field
                v-model="password"
                label="Password"
                type="password"
                prepend-icon="mdi-lock"
                :error-messages="passwordErrors"
                @input="$v.password.$touch()"
                @blur="$v.password.$touch()"
                :append-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
                @click:append="showPassword = !showPassword"
                :type="showPassword ? 'text' : 'password'"
                required
                outlined
                dense
                :disabled="loading"
              ></v-text-field>
              
              <v-checkbox
                v-model="rememberMe"
                label="Remember me"
                hide-details
                class="mt-0"
                :disabled="loading"
              ></v-checkbox>
              
              <v-btn
                type="submit"
                color="primary"
                block
                :loading="loading"
                :disabled="loading || $v.$invalid"
                class="mt-4"
                large
              >
                <v-icon left>mdi-login</v-icon>
                Login
              </v-btn>
            </v-form>
            
            <div v-else class="account-locked text-center py-4">
              <v-icon color="error" size="64" class="mb-4">mdi-lock-alert</v-icon>
              <div class="text-h6 mb-2">Account Locked</div>
              <div class="text-body-1">{{ error }}</div>
              <div class="text-caption mt-2">Please try again later or contact support.</div>
            </div>
            
            <v-divider class="my-4"></v-divider>
            
            <div class="text-center">
              <router-link to="/forgot-password" class="text-decoration-none">
                Forgot your password?
              </router-link>
              
              <div class="mt-2">
                Don't have an account? 
                <router-link to="/register" class="text-decoration-none">
                  Sign up
                </router-link>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import { required, email } from '@vuelidate/validators';
import { useVuelidate } from '@vuelidate/core';
import { useAuthStore } from '@/modules/auth/store';
import { useSnackbar } from '@/shared/composables/useSnackbar';

export default defineComponent({
  name: 'LoginView',
  
  setup() {
    const authStore = useAuthStore();
    const snackbar = useSnackbar();
    
    return { 
      authStore, 
      snackbar,
      v$: useVuelidate()
    };
  },
  
  data() {
    return {
      email: '',
      password: '',
      showPassword: false,
      rememberMe: false,
      loading: false,
      error: '',
      loginAttempts: 0,
      isLocked: false,
      lockoutTime: null as ReturnType<typeof setTimeout> | null
    };
  },
  
  validations() {
    return {
      email: { required, email },
      password: { required }
    };
  },
  
  computed: {
    emailErrors() {
      const errors: string[] = [];
      if (!this.v$.email?.$dirty) return errors;
      !this.v$.email.email && errors.push('Must be a valid email');
      !this.v$.email.required && errors.push('Email is required');
      return errors;
    },
    passwordErrors() {
      const errors: string[] = [];
      if (!this.v$.password?.$dirty) return errors;
      !this.v$.password.required && errors.push('Password is required');
      return errors;
    }
  },
  
  created() {
    // Check for existing lockout
    this.checkAccountLockout();
    
    // Check for existing login attempts
    this.loginAttempts = parseInt(localStorage.getItem('loginAttempts') || '0');
    
    // Check for remembered email
    const rememberedEmail = localStorage.getItem('rememberedEmail');
    if (rememberedEmail) {
      this.email = rememberedEmail;
      this.rememberMe = true;
    }
  },
  
  beforeUnmount() {
    if (this.lockoutTime) {
      clearTimeout(this.lockoutTime);
    }
  },
  
  methods: {
    checkAccountLockout() {
      const lockoutUntil = localStorage.getItem('lockoutUntil');
      if (lockoutUntil && new Date(lockoutUntil) > new Date()) {
        this.isLocked = true;
        this.error = 'Too many failed attempts. Account locked for 30 minutes.';
        
        // Set timer to unlock
        const timeLeft = new Date(lockoutUntil).getTime() - new Date().getTime();
        this.lockoutTime = setTimeout(() => {
          this.isLocked = false;
          this.error = '';
          localStorage.removeItem('lockoutUntil');
        }, timeLeft);
      }
    },
    
    async handleLogin() {
      if (this.isLocked) {
        return;
      }
      
      this.v$.$touch();
      if (this.v$.$invalid) {
        return;
      }
      
      try {
        this.error = '';
        this.loading = true;
        
        // Handle remember me
        if (this.rememberMe) {
          localStorage.setItem('rememberedEmail', this.email);
        } else {
          localStorage.removeItem('rememberedEmail');
        }
        
        // Use the auth store to handle login
        const success = await this.authStore.login({
          email: this.email,
          password: this.password,
        });
        
        if (success) {
          // Reset login attempts on successful login
          this.loginAttempts = 0;
          localStorage.removeItem('loginAttempts');
          
          // Show success message
          this.snackbar.showSuccess('Login successful');
          
          // Redirect to dashboard or intended route
          const redirect = typeof this.$route.query.redirect === 'string' 
            ? this.$route.query.redirect 
            : '/';
          this.$router.push(redirect);
        } else {
          // Handle failed login
          this.handleFailedLogin();
        }
      } catch (error: any) {
        console.error('Login error:', error);
        this.error = error.response?.data?.message || 'An error occurred during login';
      } finally {
        this.loading = false;
      }
    },
    
    handleFailedLogin() {
      this.loginAttempts = (parseInt(localStorage.getItem('loginAttempts') || '0')) + 1;
      localStorage.setItem('loginAttempts', this.loginAttempts.toString());
      
      // Check for account lockout (after 5 attempts)
      if (this.loginAttempts >= 5) {
        // Lock account for 30 minutes
        const lockoutUntil = new Date(new Date().getTime() + 30 * 60000);
        localStorage.setItem('lockoutUntil', lockoutUntil.toISOString());
        
        this.isLocked = true;
        this.error = 'Too many failed attempts. Account locked for 30 minutes.';
        
        // Set timer to unlock
        this.lockoutTime = setTimeout(() => {
          this.isLocked = false;
          this.error = '';
          localStorage.removeItem('lockoutUntil');
        }, 30 * 60000);
      } else {
        const attemptsLeft = 5 - this.loginAttempts;
        this.error = `Invalid email or password. ${attemptsLeft} attempt${attemptsLeft !== 1 ? 's' : ''} remaining.`;
      }
    }
  }
});
</script>

<style scoped>
.v-card {
  border-radius: 8px;
  overflow: hidden;
}

.v-toolbar {
  border-top-left-radius: 8px;
  border-top-right-radius: 8px;
}

.v-btn {
  text-transform: none;
  letter-spacing: 0.5px;
}

.account-locked {
  padding: 24px;
}

.v-icon {
  display: block;
  margin: 0 auto;
}

.v-divider {
  margin: 16px 0;
}

a {
  color: var(--v-primary-base);
  transition: opacity 0.2s ease-in-out;
}

a:hover {
  opacity: 0.8;
  text-decoration: underline;
}

.fill-height {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
}
</style>