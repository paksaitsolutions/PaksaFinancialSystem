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
          
          <v-text-field
            v-model="password"
            label="Password"
            prepend-inner-icon="mdi-lock"
            :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
            @click:append-inner="showPassword = !showPassword"
            :type="showPassword ? 'text' : 'password'"
            variant="outlined"
            :rules="[validationRules.required]"
            required
            autocomplete="current-password"
            :disabled="loading"
            @keyup.enter="handleLogin"
          ></v-text-field>
          
          <div class="d-flex align-center justify-space-between mb-6">
            <v-checkbox
              v-model="rememberMe"
              label="Remember me"
              hide-details
              density="compact"
            ></v-checkbox>
            <v-btn variant="text" color="primary" size="small" to="/auth/forgot-password">
              Forgot Password?
            </v-btn>
          </div>
          
          <v-btn
            type="submit"
            color="primary"
            block
            size="large"
            :loading="loading"
            :disabled="!isFormValid"
          >
            <v-icon start>mdi-login</v-icon>
            Sign In
          </v-btn>
        </v-form>
        
        <social-login-buttons @social-login="handleSocialLogin" />
      </v-card-text>
      
      <v-divider></v-divider>
      
      <v-card-actions class="justify-center pa-4">
        <div class="text-center">
          <p class="text-body-2">
            Don't have an account?
            <v-btn variant="text" color="primary" to="/auth/register">
              Sign Up
            </v-btn>
          </p>
        </div>
      </v-card-actions>
      
      <v-card-text class="text-center text-caption text-medium-emphasis">
        By signing in, you agree to our 
        <a href="#" @click.prevent="showTerms = true">Terms of Service</a> and 
        <a href="#" @click.prevent="showPrivacy = true">Privacy Policy</a>
      </v-card-text>
    </v-card>
    
    <!-- Terms Dialog -->
    <v-dialog v-model="showTerms" max-width="600">
      <v-card>
        <v-card-title>Terms of Service</v-card-title>
        <v-card-text>
          <p>These Terms of Service govern your use of the Paksa Financial System.</p>
          <p>By accessing or using the service, you agree to be bound by these Terms.</p>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" @click="showTerms = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
    <!-- Privacy Dialog -->
    <v-dialog v-model="showPrivacy" max-width="600">
      <v-card>
        <v-card-title>Privacy Policy</v-card-title>
        <v-card-text>
          <p>This Privacy Policy describes how your personal information is collected, used, and shared when you use the Paksa Financial System.</p>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" @click="showPrivacy = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import SocialLoginButtons from '@/components/auth/SocialLoginButtons.vue';
import formValidation from '@/mixins/formValidation.js';

export default {
  components: {
    SocialLoginButtons
  },
  mixins: [formValidation],
  data() {
    return {
      email: 'admin@example.com',
      password: 'password',
      showPassword: false,
      rememberMe: false,
      error: '',
      successMessage: '',
      loading: false,
      showTerms: false,
      showPrivacy: false,
      loginAttempts: 0,
      isLocked: false,
      lockoutTime: null
    }
  },
  computed: {
    isFormValid() {
      return this.email && 
             /.+@.+\..+/.test(this.email) && 
             this.password && 
             !this.isLocked;
    }
  },
  mounted() {
    // Show success message if redirected from registration
    if (this.$route.query.registered === 'true') {
      this.successMessage = 'Registration successful! Please sign in with your new account.';
    }
    
    // Show success message if redirected from password reset
    if (this.$route.query.reset === 'true') {
      this.successMessage = 'Password reset successful! Please sign in with your new password.';
    }
    
    // Check if account is locked
    const lockoutUntil = localStorage.getItem('lockoutUntil');
    if (lockoutUntil && new Date(lockoutUntil) > new Date()) {
      this.isLocked = true;
      this.error = `Account temporarily locked. Please try again later.`;
      
      // Set timer to unlock
      const timeLeft = new Date(lockoutUntil) - new Date();
      this.lockoutTime = setTimeout(() => {
        this.isLocked = false;
        this.error = '';
        localStorage.removeItem('lockoutUntil');
      }, timeLeft);
    }
  },
  beforeUnmount() {
    if (this.lockoutTime) {
      clearTimeout(this.lockoutTime);
    }
  },
  methods: {
    async handleLogin() {
      if (this.isLocked) {
        return;
      }
      
      try {
        this.error = '';
        this.loading = true;
        
        // Mock login with security features
        if (this.email === 'admin@example.com' && this.password === 'password') {
          // Successful login
          localStorage.setItem('token', 'mock-token');
          localStorage.setItem('user', JSON.stringify({
            name: 'Admin User',
            email: this.email,
            lastLogin: new Date().toISOString()
          }));
          
          // Reset login attempts
          this.loginAttempts = 0;
          localStorage.removeItem('loginAttempts');
          
          // Redirect to dashboard
          this.$router.push('/');
        } else {
          // Failed login
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
            this.error = 'Invalid email or password';
          }
        }
      } catch (err) {
        console.error('Login failed:', err);
        this.error = 'An error occurred during login';
      } finally {
        this.loading = false;
      }
    },
    
    handleSocialLogin(provider) {
      this.loading = true;
      
      // Mock social login
      setTimeout(() => {
        localStorage.setItem('token', `mock-${provider}-token`);
        localStorage.setItem('user', JSON.stringify({
          name: `${provider.charAt(0).toUpperCase() + provider.slice(1)} User`,
          email: `user@${provider}.com`,
          provider: provider,
          lastLogin: new Date().toISOString()
        }));
        
        this.loading = false;
        this.$router.push('/');
      }, 1000);
    }
  }
}
</script>

<style>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
  padding: 20px;
}

.login-card {
  width: 100%;
}

a {
  text-decoration: none;
  color: var(--v-primary-base);
}
</style>