<template>
  <div class="register-container">
    <v-card class="register-card" max-width="550" elevation="2">
      <v-card-item>
        <div class="d-flex justify-center mb-4">
          <v-img src="/favicon.svg" width="60" height="60" alt="Logo"></v-img>
        </div>
        <v-card-title class="text-center text-h4 font-weight-bold">
          Create Account
        </v-card-title>
        
        <v-card-subtitle class="text-center">
          Join Paksa Financial System
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
        
        <v-stepper v-model="step" class="elevation-0">
          <v-stepper-header class="mb-4">
            <v-stepper-item value="1" title="Account"></v-stepper-item>
            <v-divider></v-divider>
            <v-stepper-item value="2" title="Profile"></v-stepper-item>
            <v-divider></v-divider>
            <v-stepper-item value="3" title="Verification"></v-stepper-item>
          </v-stepper-header>
          
          <v-stepper-window>
            <!-- Step 1: Account Information -->
            <v-stepper-window-item value="1">
              <v-form @submit.prevent="nextStep" ref="accountForm">
                <v-text-field
                  v-model="email"
                  label="Email"
                  prepend-inner-icon="mdi-email"
                  variant="outlined"
                  :rules="[validationRules.required, validationRules.email]"
                  required
                  autocomplete="email"
                  hint="We'll send a verification code to this email"
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
                  :rules="[validationRules.required, v => v.length >= 8 || 'Password must be at least 8 characters']"
                  required
                ></v-text-field>
                
                <password-strength-meter :password="password" />
                
                <v-text-field
                  v-model="confirmPassword"
                  label="Confirm Password"
                  prepend-inner-icon="mdi-lock-check"
                  :type="showPassword ? 'text' : 'password'"
                  variant="outlined"
                  :rules="[validationRules.required, v => v === password || 'Passwords do not match']"
                  required
                ></v-text-field>
                
                <v-btn
                  type="submit"
                  color="primary"
                  block
                  size="large"
                  :disabled="!isStep1Valid"
                >
                  Continue
                </v-btn>
                
                <social-login-buttons @social-login="handleSocialLogin" />
              </v-form>
            </v-stepper-window-item>
            
            <!-- Step 2: Profile Information -->
            <v-stepper-window-item value="2">
              <v-form @submit.prevent="nextStep" ref="profileForm">
                <v-row>
                  <v-col cols="12" sm="6">
                    <v-text-field
                      v-model="firstName"
                      label="First Name"
                      prepend-inner-icon="mdi-account"
                      variant="outlined"
                      :rules="[validationRules.required]"
                      required
                    ></v-text-field>
                  </v-col>
                  
                  <v-col cols="12" sm="6">
                    <v-text-field
                      v-model="lastName"
                      label="Last Name"
                      variant="outlined"
                      :rules="[validationRules.required]"
                      required
                    ></v-text-field>
                  </v-col>
                </v-row>
                
                <v-text-field
                  v-model="phone"
                  label="Phone Number"
                  prepend-inner-icon="mdi-phone"
                  variant="outlined"
                  :rules="[v => !v || /^\+?[0-9]{10,15}$/.test(v) || 'Phone number must be valid']"
                  hint="Optional: For account recovery"
                  persistent-hint
                ></v-text-field>
                
                <v-select
                  v-model="role"
                  label="Role"
                  prepend-inner-icon="mdi-badge-account"
                  variant="outlined"
                  :items="['Individual', 'Business Owner', 'Accountant', 'Administrator']"
                  :rules="[validationRules.required]"
                  required
                ></v-select>
                
                <div class="d-flex gap-2 mt-4">
                  <v-btn
                    variant="outlined"
                    @click="step = '1'"
                  >
                    Back
                  </v-btn>
                  
                  <v-btn
                    type="submit"
                    color="primary"
                    block
                    :disabled="!isStep2Valid"
                  >
                    Continue
                  </v-btn>
                </div>
              </v-form>
            </v-stepper-window-item>
            
            <!-- Step 3: Verification -->
            <v-stepper-window-item value="3">
              <v-form @submit.prevent="handleRegister" ref="verificationForm">
                <div class="text-center mb-4">
                  <p>Please review your information before submitting</p>
                </div>
                
                <v-list>
                  <v-list-item>
                    <template v-slot:prepend>
                      <v-icon color="primary">mdi-email</v-icon>
                    </template>
                    <v-list-item-title>Email</v-list-item-title>
                    <v-list-item-subtitle>{{ email }}</v-list-item-subtitle>
                  </v-list-item>
                  
                  <v-list-item>
                    <template v-slot:prepend>
                      <v-icon color="primary">mdi-account</v-icon>
                    </template>
                    <v-list-item-title>Name</v-list-item-title>
                    <v-list-item-subtitle>{{ firstName }} {{ lastName }}</v-list-item-subtitle>
                  </v-list-item>
                  
                  <v-list-item v-if="phone">
                    <template v-slot:prepend>
                      <v-icon color="primary">mdi-phone</v-icon>
                    </template>
                    <v-list-item-title>Phone</v-list-item-title>
                    <v-list-item-subtitle>{{ phone }}</v-list-item-subtitle>
                  </v-list-item>
                  
                  <v-list-item>
                    <template v-slot:prepend>
                      <v-icon color="primary">mdi-badge-account</v-icon>
                    </template>
                    <v-list-item-title>Role</v-list-item-title>
                    <v-list-item-subtitle>{{ role }}</v-list-item-subtitle>
                  </v-list-item>
                </v-list>
                
                <v-checkbox
                  v-model="agreeTerms"
                  :rules="[v => !!v || 'You must agree to continue']"
                  required
                >
                  <template v-slot:label>
                    <div>
                      I agree to the
                      <a href="#" @click.prevent="showTerms = true">Terms of Service</a>
                      and
                      <a href="#" @click.prevent="showPrivacy = true">Privacy Policy</a>
                    </div>
                  </template>
                </v-checkbox>
                
                <v-checkbox
                  v-model="agreeMarketing"
                >
                  <template v-slot:label>
                    <div>
                      I agree to receive marketing communications
                    </div>
                  </template>
                </v-checkbox>
                
                <div class="d-flex gap-2 mt-4">
                  <v-btn
                    variant="outlined"
                    @click="step = '2'"
                  >
                    Back
                  </v-btn>
                  
                  <v-btn
                    type="submit"
                    color="primary"
                    block
                    :loading="loading"
                    :disabled="!isStep3Valid"
                  >
                    Create Account
                  </v-btn>
                </div>
              </v-form>
            </v-stepper-window-item>
          </v-stepper-window>
        </v-stepper>
      </v-card-text>
      
      <v-divider></v-divider>
      
      <v-card-actions class="justify-center pa-4">
        <div class="text-center">
          <p class="text-body-2">
            Already have an account?
            <v-btn variant="text" color="primary" to="/auth/login">
              Sign In
            </v-btn>
          </p>
        </div>
      </v-card-actions>
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
import PasswordStrengthMeter from '@/components/auth/PasswordStrengthMeter.vue';
import formValidation from '@/mixins/formValidation.js';

export default {
  components: {
    SocialLoginButtons,
    PasswordStrengthMeter
  },
  mixins: [formValidation],
  data() {
    return {
      step: '1',
      email: '',
      password: '',
      confirmPassword: '',
      firstName: '',
      lastName: '',
      phone: '',
      role: 'Individual',
      showPassword: false,
      agreeTerms: false,
      agreeMarketing: false,
      error: '',
      loading: false,
      showTerms: false,
      showPrivacy: false
    }
  },
  computed: {
    isStep1Valid() {
      return this.email && 
             /.+@.+\..+/.test(this.email) && 
             this.password && 
             this.password.length >= 8 &&
             this.password === this.confirmPassword;
    },
    isStep2Valid() {
      return this.firstName && this.lastName && this.role;
    },
    isStep3Valid() {
      return this.agreeTerms;
    }
  },
  methods: {
    nextStep() {
      if (this.step === '1' && this.isStep1Valid) {
        this.step = '2';
      } else if (this.step === '2' && this.isStep2Valid) {
        this.step = '3';
      }
    },
    
    async handleRegister() {
      if (!this.isStep3Valid) return;
      
      try {
        this.error = '';
        this.loading = true;
        
        // Mock registration delay
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        // Redirect to login with success message
        this.$router.push('/auth/login?registered=true');
      } catch (err) {
        console.error('Registration failed:', err);
        this.error = 'An error occurred during registration';
      } finally {
        this.loading = false;
      }
    },
    
    handleSocialLogin(provider) {
      this.loading = true;
      
      // Mock social registration
      setTimeout(() => {
        this.$router.push('/auth/login?registered=true');
        this.loading = false;
      }, 1000);
    }
  }
}
</script>

<style>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
  padding: 20px;
}

.register-card {
  width: 100%;
}

a {
  text-decoration: none;
  color: var(--v-primary-base);
}
</style>