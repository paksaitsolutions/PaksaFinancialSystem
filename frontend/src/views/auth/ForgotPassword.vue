<template>
  <div class="forgot-password-container">
    <v-card class="forgot-password-card" max-width="450" elevation="2">
      <v-card-item>
        <div class="d-flex justify-center mb-4">
          <v-img src="/favicon.svg" width="60" height="60" alt="Logo"></v-img>
        </div>
        <v-card-title class="text-center text-h4 font-weight-bold">
          Reset Password
        </v-card-title>
        
        <v-card-subtitle class="text-center">
          {{ currentStep === 1 ? 'Enter your email to receive a verification code' : 
             currentStep === 2 ? 'Enter the verification code sent to your email' : 
             'Create a new password' }}
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
          v-if="success"
          type="success"
          variant="tonal"
          closable
          class="mb-4"
          @click:close="success = ''"
        >
          {{ success }}
        </v-alert>
        
        <!-- Step 1: Email Input -->
        <v-window v-model="currentStep">
          <v-window-item :value="1">
            <v-form @submit.prevent="requestCode" ref="emailForm">
              <v-text-field
                v-model="email"
                label="Email"
                prepend-inner-icon="mdi-email"
                variant="outlined"
                :rules="[validationRules.required, validationRules.email]"
                required
                autocomplete="email"
                :disabled="loading"
                hint="Enter your registered email address"
                persistent-hint
              ></v-text-field>
              
              <v-btn
                type="submit"
                color="primary"
                block
                size="large"
                :loading="loading"
                :disabled="!isEmailValid"
              >
                Send Verification Code
              </v-btn>
            </v-form>
          </v-window-item>
          
          <!-- Step 2: Verification Code -->
          <v-window-item :value="2">
            <v-form @submit.prevent="verifyCode" ref="codeForm">
              <div class="text-center mb-4">
                <p>We've sent a verification code to <strong>{{ email }}</strong></p>
              </div>
              
              <div class="verification-code-container">
                <v-otp-input
                  v-model="verificationCode"
                  length="6"
                  :disabled="loading"
                  type="number"
                ></v-otp-input>
              </div>
              
              <div class="d-flex justify-center mb-4">
                <v-btn
                  variant="text"
                  :disabled="resendDisabled || loading"
                  @click="requestCode"
                >
                  {{ resendDisabled ? `Resend code in ${resendCountdown}s` : 'Resend code' }}
                </v-btn>
              </div>
              
              <div class="d-flex gap-2">
                <v-btn
                  variant="outlined"
                  @click="currentStep = 1"
                  :disabled="loading"
                >
                  Back
                </v-btn>
                
                <v-btn
                  type="submit"
                  color="primary"
                  block
                  :loading="loading"
                  :disabled="!isCodeValid"
                >
                  Verify Code
                </v-btn>
              </div>
            </v-form>
          </v-window-item>
          
          <!-- Step 3: New Password -->
          <v-window-item :value="3">
            <v-form @submit.prevent="resetPassword" ref="passwordForm">
              <v-text-field
                v-model="newPassword"
                label="New Password"
                prepend-inner-icon="mdi-lock"
                :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
                @click:append-inner="showPassword = !showPassword"
                :type="showPassword ? 'text' : 'password'"
                variant="outlined"
                :rules="[validationRules.required, v => v.length >= 8 || 'Password must be at least 8 characters']"
                required
                :disabled="loading"
              ></v-text-field>
              
              <password-strength-meter :password="newPassword" />
              
              <v-text-field
                v-model="confirmNewPassword"
                label="Confirm New Password"
                prepend-inner-icon="mdi-lock-check"
                :type="showPassword ? 'text' : 'password'"
                variant="outlined"
                :rules="[validationRules.required, v => v === newPassword || 'Passwords do not match']"
                required
                :disabled="loading"
              ></v-text-field>
              
              <div class="d-flex gap-2">
                <v-btn
                  variant="outlined"
                  @click="currentStep = 2"
                  :disabled="loading"
                >
                  Back
                </v-btn>
                
                <v-btn
                  type="submit"
                  color="primary"
                  block
                  :loading="loading"
                  :disabled="!isPasswordValid"
                >
                  Reset Password
                </v-btn>
              </div>
            </v-form>
          </v-window-item>
        </v-window>
      </v-card-text>
      
      <v-divider></v-divider>
      
      <v-card-actions class="justify-center pa-4">
        <div class="text-center">
          <p class="text-body-2">
            Remember your password?
            <v-btn variant="text" color="primary" to="/auth/login">
              Back to Login
            </v-btn>
          </p>
        </div>
      </v-card-actions>
    </v-card>
  </div>
</template>

<script>
import PasswordStrengthMeter from '@/components/auth/PasswordStrengthMeter.vue';
import formValidation from '@/mixins/formValidation.js';

export default {
  components: {
    PasswordStrengthMeter
  },
  mixins: [formValidation],
  data() {
    return {
      currentStep: 1,
      email: '',
      verificationCode: '',
      newPassword: '',
      confirmNewPassword: '',
      showPassword: false,
      error: '',
      success: '',
      loading: false,
      resendDisabled: false,
      resendCountdown: 60,
      countdownInterval: null
    }
  },
  computed: {
    isEmailValid() {
      return this.email && /.+@.+\..+/.test(this.email);
    },
    isCodeValid() {
      return this.verificationCode && this.verificationCode.length === 6;
    },
    isPasswordValid() {
      return this.newPassword && 
             this.newPassword.length >= 8 && 
             this.newPassword === this.confirmNewPassword;
    }
  },
  beforeUnmount() {
    if (this.countdownInterval) {
      clearInterval(this.countdownInterval);
    }
  },
  methods: {
    async requestCode() {
      if (!this.isEmailValid) return;
      
      try {
        this.error = '';
        this.loading = true;
        
        // Mock API call to request verification code
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // For demo, we'll just move to the next step
        this.currentStep = 2;
        this.success = `Verification code sent to ${this.email}`;
        
        // Start resend countdown
        this.startResendCountdown();
      } catch (err) {
        console.error('Failed to send verification code:', err);
        this.error = 'Failed to send verification code. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    
    async verifyCode() {
      if (!this.isCodeValid) return;
      
      try {
        this.error = '';
        this.loading = true;
        
        // Mock API call to verify code
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // For demo purposes, we'll accept any 6-digit code
        if (this.verificationCode.length === 6) {
          this.currentStep = 3;
          this.success = 'Code verified successfully';
        } else {
          this.error = 'Invalid verification code';
        }
      } catch (err) {
        console.error('Failed to verify code:', err);
        this.error = 'Failed to verify code. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    
    async resetPassword() {
      if (!this.isPasswordValid) return;
      
      try {
        this.error = '';
        this.loading = true;
        
        // Mock API call to reset password
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        // Redirect to login with success message
        this.$router.push('/auth/login?reset=true');
      } catch (err) {
        console.error('Failed to reset password:', err);
        this.error = 'Failed to reset password. Please try again.';
      } finally {
        this.loading = false;
      }
    },
    
    startResendCountdown() {
      this.resendDisabled = true;
      this.resendCountdown = 60;
      
      if (this.countdownInterval) {
        clearInterval(this.countdownInterval);
      }
      
      this.countdownInterval = setInterval(() => {
        this.resendCountdown -= 1;
        if (this.resendCountdown <= 0) {
          clearInterval(this.countdownInterval);
          this.resendDisabled = false;
        }
      }, 1000);
    }
  }
}
</script>

<style>
.forgot-password-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
  padding: 20px;
}

.forgot-password-card {
  width: 100%;
}

.verification-code-container {
  display: flex;
  justify-content: center;
  margin: 20px 0;
}
</style>