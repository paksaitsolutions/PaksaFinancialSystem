<template>
  <v-container fluid class="fill-height">
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="6" lg="4">
        <v-card class="login-card" elevation="4">
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

            <v-form @submit.prevent="handleLogin" ref="form" v-if="!isLocked">
              <v-text-field
                v-model="email"
                label="Email"
                type="email"
                prepend-icon="mdi-account"
                :error-messages="emailError ? [emailError] : []"
                @input="emailError = ''"
                required
              ></v-text-field>

              <v-text-field
                v-model="password"
                label="Password"
                :type="showPassword ? 'text' : 'password'"
                prepend-icon="mdi-lock"
                :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
                @click:append-inner="showPassword = !showPassword"
                :error-messages="passwordError ? [passwordError] : []"
                @input="passwordError = ''"
                required
                class="mt-4"
              ></v-text-field>

              <div class="d-flex justify-space-between align-center mt-2">
                <v-checkbox
                  v-model="rememberMe"
                  label="Remember me"
                  hide-details
                  class="mt-0"
                ></v-checkbox>
                <router-link to="/forgot-password" class="text-caption text-decoration-none">
                  Forgot password?
                </router-link>
              </div>

              <v-btn
                type="submit"
                color="primary"
                size="large"
                block
                class="mt-6"
                :loading="loading"
                :disabled="loading"
              >
                Sign In
              </v-btn>
            </v-form>

            <div v-else class="text-center">
              <v-alert
                type="warning"
                variant="tonal"
                class="mb-4"
              >
                Account locked. Please try again in {{ countdown }} seconds.
              </v-alert>
              <v-btn
                color="primary"
                @click="checkAccountLockout"
                :disabled="isLocked"
              >
                Try Again
              </v-btn>
            </div>

            <div class="text-center mt-4">
              <span class="text-caption">Don't have an account? </span>
              <router-link to="/register" class="text-caption text-primary text-decoration-none">
                Sign Up
              </router-link>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, onUnmounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/modules/auth/store';

export default defineComponent({
  name: 'LoginView',
  
  setup() {
    const authStore = useAuthStore();
    const router = useRouter();
    const route = useRoute(); // Add route to setup
    const form = ref<HTMLFormElement | null>(null);
    
    return { 
      authStore, 
      router,
      route, // Add route to return
      form
    };
  },
  
  data() {
    return {
      email: '',
      password: '',
      showPassword: false,
      rememberMe: false,
      error: '',
      loading: false,
      loginAttempts: 0,
      isLocked: false,
      lockoutTime: 0,
      countdown: 0,
      countdownInterval: null as number | null,
      emailError: '',
      passwordError: ''
    };
  },
  
  mounted(): void {
    // Check if account is locked on component mount
    this.checkAccountLockout();
    
    // Load remembered email if exists
    const rememberedEmail = localStorage.getItem('rememberedEmail');
    if (rememberedEmail) {
      this.email = rememberedEmail;
      this.rememberMe = true;
    }
    
    // Load login attempts from localStorage
    this.loginAttempts = parseInt(localStorage.getItem('loginAttempts') || '0', 10);
  },
  
  beforeUnmount(): void {
    if (this.countdownInterval) {
      clearInterval(this.countdownInterval);
      this.countdownInterval = null;
    }
  },
  
  methods: {
    validateForm(): boolean {
      this.emailError = '';
      this.passwordError = '';
      
      let isValid = true;
      
      if (!this.email) {
        this.emailError = 'Email is required';
        isValid = false;
      } else if (!this.validateEmail(this.email)) {
        this.emailError = 'Must be a valid email';
        isValid = false;
      }
      
      if (!this.password) {
        this.passwordError = 'Password is required';
        isValid = false;
      } else if (this.password.length < 6) {
        this.passwordError = 'Password must be at least 6 characters';
        isValid = false;
      }
      
      return isValid;
    },
    
    validateEmail(email: string): boolean {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return emailRegex.test(email);
    },
    
    checkAccountLockout(): boolean {
      const lockoutInfo = JSON.parse(localStorage.getItem('loginLockout') || '{}');
      if (lockoutInfo.timestamp) {
        const lockoutDuration = 5 * 60 * 1000; // 5 minutes in milliseconds
        const timeElapsed = Date.now() - lockoutInfo.timestamp;
        
        if (timeElapsed < lockoutDuration) {
          this.isLocked = true;
          this.lockoutTime = Math.ceil((lockoutDuration - timeElapsed) / 1000);
          this.startCountdown();
          return true;
        } else {
          localStorage.removeItem('loginLockout');
          this.isLocked = false;
        }
      }
      return false;
    },
    
    startCountdown(): void {
      this.countdown = this.lockoutTime;
      this.countdownInterval = window.setInterval(() => {
        this.countdown -= 1;
        if (this.countdown <= 0) {
          if (this.countdownInterval) {
            clearInterval(this.countdownInterval);
            this.countdownInterval = null;
          }
          this.isLocked = false;
          this.error = '';
          localStorage.removeItem('loginLockout');
        }
      }, 1000);
    },
    
    async handleLogin(): Promise<void> {
      if (!this.validateForm()) {
        return;
      }
      
      this.loading = true;
      this.error = '';
      
      try {
        // Handle remember me
        if (this.rememberMe) {
          localStorage.setItem('rememberedEmail', this.email);
        } else {
          localStorage.removeItem('rememberedEmail');
        }
        
        // Use the auth store to handle login
        await this.authStore.login({
          email: this.email,
          password: this.password,
        });
        
        // Reset login attempts on successful login
        this.loginAttempts = 0;
        localStorage.removeItem('loginAttempts');
        
        // Redirect to dashboard or intended route
        const redirectTo = this.$route?.query?.redirect || '/';
        this.$router.push(redirectTo as string);
        
      } catch (error: any) {
        this.handleFailedLogin();
        if (error.response && error.response.data && error.response.data.message) {
          this.error = error.response.data.message;
        } else {
          this.error = 'An error occurred during login. Please try again.';
        }
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
        const lockoutInfo = {
          timestamp: Date.now(),
          duration: 30 * 60 * 1000 // 30 minutes in milliseconds
        };
        localStorage.setItem('loginLockout', JSON.stringify(lockoutInfo));
        
        this.isLocked = true;
        this.lockoutTime = Math.ceil(lockoutInfo.duration / 1000);
        this.startCountdown();
        this.error = 'Too many failed attempts. Account locked for 30 minutes.';
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