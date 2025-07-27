<template>
  <v-app class="login-app">
    <div class="login-wrapper">
      <!-- Background Elements -->
      <div class="bg-shapes">
        <div class="shape shape-1"></div>
        <div class="shape shape-2"></div>
        <div class="shape shape-3"></div>
      </div>

      <v-container fluid class="login-container">
        <v-row no-gutters class="fill-height">
          <!-- Left Panel - Branding -->
          <v-col cols="12" lg="7" class="branding-panel d-none d-lg-flex">
            <div class="branding-content">
              <div class="brand-logo mb-8">
                <v-avatar size="120" class="brand-avatar">
                  <v-icon size="60" color="white">mdi-finance</v-icon>
                </v-avatar>
              </div>
              
              <h1 class="brand-title">
                Paksa Financial
                <span class="gradient-text">System</span>
              </h1>
              
              <p class="brand-description">
                Next-generation enterprise financial management platform with 
                AI-powered insights, real-time analytics, and seamless multi-tenant architecture.
              </p>

              <div class="features-grid">
                <div class="feature-item">
                  <v-icon size="24" class="feature-icon">mdi-shield-check</v-icon>
                  <span>Bank-level Security</span>
                </div>
                <div class="feature-item">
                  <v-icon size="24" class="feature-icon">mdi-lightning-bolt</v-icon>
                  <span>Real-time Processing</span>
                </div>
                <div class="feature-item">
                  <v-icon size="24" class="feature-icon">mdi-brain</v-icon>
                  <span>AI-Powered Insights</span>
                </div>
                <div class="feature-item">
                  <v-icon size="24" class="feature-icon">mdi-cloud-sync</v-icon>
                  <span>Cloud Native</span>
                </div>
              </div>

              <div class="stats-row">
                <div class="stat-item">
                  <div class="stat-number">99.9%</div>
                  <div class="stat-label">Uptime</div>
                </div>
                <div class="stat-item">
                  <div class="stat-number">500K+</div>
                  <div class="stat-label">Transactions</div>
                </div>
                <div class="stat-item">
                  <div class="stat-number">24/7</div>
                  <div class="stat-label">Support</div>
                </div>
              </div>
            </div>
          </v-col>

          <!-- Right Panel - Login Form -->
          <v-col cols="12" lg="5" class="form-panel">
            <div class="form-container">
              <!-- Mobile Logo -->
              <div class="mobile-logo d-lg-none mb-6">
                <v-avatar size="80" class="brand-avatar">
                  <v-icon size="40" color="white">mdi-finance</v-icon>
                </v-avatar>
                <h2 class="mobile-title">Paksa Financial</h2>
              </div>

              <div class="form-card">
                <div class="form-header">
                  <h1 class="form-title">Welcome Back</h1>
                  <p class="form-subtitle">Sign in to access your financial dashboard</p>
                </div>

                <v-form ref="form" v-model="valid" @submit.prevent="login" class="login-form">
                  <!-- Email Field -->
                  <div class="input-group">
                    <label class="input-label">Email Address</label>
                    <v-text-field
                      v-model="email"
                      type="email"
                      :rules="emailRules"
                      variant="outlined"
                      density="comfortable"
                      class="modern-input"
                      hide-details="auto"
                      placeholder="Enter your email"
                    >
                      <template #prepend-inner>
                        <v-icon color="primary" size="20">mdi-email-outline</v-icon>
                      </template>
                    </v-text-field>
                  </div>

                  <!-- Password Field -->
                  <div class="input-group">
                    <label class="input-label">Password</label>
                    <v-text-field
                      v-model="password"
                      :type="showPassword ? 'text' : 'password'"
                      :rules="passwordRules"
                      variant="outlined"
                      density="comfortable"
                      class="modern-input"
                      hide-details="auto"
                      placeholder="Enter your password"
                    >
                      <template #prepend-inner>
                        <v-icon color="primary" size="20">mdi-lock-outline</v-icon>
                      </template>
                      <template #append-inner>
                        <v-btn
                          icon
                          variant="text"
                          size="small"
                          @click="showPassword = !showPassword"
                        >
                          <v-icon size="20">{{ showPassword ? 'mdi-eye-off' : 'mdi-eye' }}</v-icon>
                        </v-btn>
                      </template>
                    </v-text-field>
                  </div>

                  <!-- Options Row -->
                  <div class="form-options">
                    <v-checkbox
                      v-model="rememberMe"
                      label="Remember me"
                      color="primary"
                      hide-details
                      density="compact"
                    />
                    <v-btn
                      variant="text"
                      color="primary"
                      size="small"
                      class="forgot-btn"
                    >
                      Forgot Password?
                    </v-btn>
                  </div>

                  <!-- Error Alert -->
                  <v-alert
                    v-if="errorMessage"
                    type="error"
                    variant="tonal"
                    class="error-alert"
                    closable
                    @click:close="errorMessage = ''"
                  >
                    {{ errorMessage }}
                  </v-alert>

                  <!-- Login Button -->
                  <v-btn
                    type="submit"
                    color="primary"
                    size="x-large"
                    block
                    :loading="loading"
                    class="login-button"
                    elevation="0"
                  >
                    <v-icon start size="20">mdi-login</v-icon>
                    Sign In to Dashboard
                  </v-btn>

                  <!-- Divider -->
                  <div class="divider-section">
                    <v-divider />
                    <span class="divider-text">Demo Access</span>
                    <v-divider />
                  </div>

                  <!-- Demo Buttons -->
                  <div class="demo-section">
                    <v-btn
                      variant="outlined"
                      color="primary"
                      size="large"
                      class="demo-button"
                      @click="fillDemoCredentials('admin')"
                    >
                      <v-icon start size="18">mdi-shield-crown</v-icon>
                      Admin Demo
                    </v-btn>
                    <v-btn
                      variant="outlined"
                      color="secondary"
                      size="large"
                      class="demo-button"
                      @click="fillDemoCredentials('user')"
                    >
                      <v-icon start size="18">mdi-account</v-icon>
                      User Demo
                    </v-btn>
                  </div>
                </v-form>

                <!-- Footer -->
                <div class="form-footer">
                  <p class="footer-text">
                    Don't have an account? 
                    <v-btn variant="text" color="primary" size="small" class="signup-btn">
                      Contact Sales
                    </v-btn>
                  </p>
                  <p class="copyright">© 2024 Paksa IT Solutions. All rights reserved.</p>
                </div>
              </div>
            </div>
          </v-col>
        </v-row>
      </v-container>
    </div>
  </v-app>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const router = useRouter()

const email = ref('')
const password = ref('')
const rememberMe = ref(false)
const showPassword = ref(false)
const valid = ref(true)
const loading = ref(false)
const errorMessage = ref('')

const emailRules = [
  (v: string) => !!v || 'Email is required',
  (v: string) => /.+@.+\..+/.test(v) || 'Please enter a valid email'
]

const passwordRules = [
  (v: string) => !!v || 'Password is required',
  (v: string) => v.length >= 6 || 'Password must be at least 6 characters'
]

const fillDemoCredentials = (type: 'admin' | 'user') => {
  if (type === 'admin') {
    email.value = 'admin@paksa.com'
    password.value = 'admin123'
  } else {
    email.value = 'user@paksa.com'
    password.value = 'user123'
  }
}

const login = async () => {
  if (!valid.value) return

  loading.value = true
  errorMessage.value = ''

  try {
    const response = await api.post('/api/v1/auth/login', {
      username: email.value,
      password: password.value
    })

    const { access_token, user } = response.data
    
    localStorage.setItem('token', access_token)
    localStorage.setItem('user', JSON.stringify(user))
    
    router.push('/dashboard')
  } catch (error: any) {
    console.error('Login error:', error)
    errorMessage.value = error.response?.data?.detail || 'Invalid credentials. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-app {
  background: #0f0f23;
  min-height: 100vh;
  overflow: hidden;
}

.login-wrapper {
  position: relative;
  min-height: 100vh;
}

/* Background Shapes */
.bg-shapes {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 0;
}

.shape {
  position: absolute;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(168, 85, 247, 0.1));
  animation: float 20s infinite ease-in-out;
}

.shape-1 {
  width: 300px;
  height: 300px;
  top: 10%;
  left: 10%;
  animation-delay: 0s;
}

.shape-2 {
  width: 200px;
  height: 200px;
  top: 60%;
  right: 15%;
  animation-delay: -7s;
}

.shape-3 {
  width: 150px;
  height: 150px;
  bottom: 20%;
  left: 60%;
  animation-delay: -14s;
}

@keyframes float {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  33% { transform: translateY(-30px) rotate(120deg); }
  66% { transform: translateY(20px) rotate(240deg); }
}

.login-container {
  position: relative;
  z-index: 1;
  min-height: 100vh;
}

/* Branding Panel */
.branding-panel {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow: hidden;
}

.branding-panel::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="0.5"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
  opacity: 0.3;
}

.branding-content {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
  padding: 4rem;
  text-align: center;
  color: white;
}

.brand-logo {
  animation: pulse 2s infinite;
}

.brand-avatar {
  background: linear-gradient(135deg, rgba(255,255,255,0.2), rgba(255,255,255,0.1));
  backdrop-filter: blur(20px);
  border: 2px solid rgba(255,255,255,0.2);
  box-shadow: 0 20px 40px rgba(0,0,0,0.2);
}

.brand-title {
  font-size: 4rem;
  font-weight: 800;
  line-height: 1.1;
  margin-bottom: 1.5rem;
  letter-spacing: -0.02em;
}

.gradient-text {
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.brand-description {
  font-size: 1.25rem;
  line-height: 1.6;
  margin-bottom: 3rem;
  opacity: 0.9;
  max-width: 500px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
  margin-bottom: 3rem;
  width: 100%;
  max-width: 400px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background: rgba(255,255,255,0.1);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.2);
  transition: all 0.3s ease;
}

.feature-item:hover {
  background: rgba(255,255,255,0.15);
  transform: translateY(-2px);
}

.feature-icon {
  color: #fbbf24;
}

.stats-row {
  display: flex;
  gap: 3rem;
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  color: #fbbf24;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.875rem;
  opacity: 0.8;
}

/* Form Panel */
.form-panel {
  background: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.form-container {
  width: 100%;
  max-width: 480px;
}

.mobile-logo {
  text-align: center;
}

.mobile-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1e293b;
  margin-top: 1rem;
}

.form-card {
  background: #ffffff;
  border-radius: 24px;
  padding: 3rem;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(0,0,0,0.05);
}

.form-header {
  text-align: center;
  margin-bottom: 2.5rem;
}

.form-title {
  font-size: 2.5rem;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 0.5rem;
  letter-spacing: -0.025em;
}

.form-subtitle {
  font-size: 1rem;
  color: #64748b;
  line-height: 1.5;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.input-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.25rem;
}

:deep(.modern-input .v-field) {
  border-radius: 12px;
  border: 2px solid #e5e7eb;
  background: #f9fafb;
  transition: all 0.2s ease;
}

:deep(.modern-input .v-field:hover) {
  border-color: #d1d5db;
  background: #ffffff;
}

:deep(.modern-input.v-field--focused .v-field) {
  border-color: rgb(var(--v-theme-primary));
  background: #ffffff;
  box-shadow: 0 0 0 3px rgba(var(--v-theme-primary), 0.1);
}

:deep(.modern-input .v-field__input) {
  padding: 1rem 1rem 1rem 3rem;
  font-size: 1rem;
  color: #1f2937;
}

:deep(.modern-input .v-field__prepend-inner) {
  padding-left: 1rem;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 0.5rem 0;
}

.forgot-btn {
  text-decoration: none;
  font-weight: 500;
}

.error-alert {
  margin: 1rem 0;
  border-radius: 12px;
}

.login-button {
  height: 56px;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  text-transform: none;
  letter-spacing: 0.025em;
  background: linear-gradient(135deg, rgb(var(--v-theme-primary)), rgb(var(--v-theme-secondary)));
  box-shadow: 0 10px 25px rgba(var(--v-theme-primary), 0.3);
  transition: all 0.3s ease;
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 15px 35px rgba(var(--v-theme-primary), 0.4);
}

.divider-section {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin: 2rem 0 1.5rem;
}

.divider-text {
  font-size: 0.875rem;
  color: #9ca3af;
  white-space: nowrap;
}

.demo-section {
  display: flex;
  gap: 1rem;
}

.demo-button {
  flex: 1;
  height: 48px;
  border-radius: 12px;
  text-transform: none;
  font-weight: 500;
  border: 2px solid;
  transition: all 0.3s ease;
}

.demo-button:hover {
  transform: translateY(-1px);
}

.form-footer {
  text-align: center;
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #e5e7eb;
}

.footer-text {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 0.5rem;
}

.signup-btn {
  text-decoration: none;
  font-weight: 600;
}

.copyright {
  font-size: 0.75rem;
  color: #9ca3af;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

/* Responsive Design */
@media (max-width: 1264px) {
  .brand-title {
    font-size: 3rem;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-row {
    gap: 2rem;
  }
}

@media (max-width: 960px) {
  .form-card {
    padding: 2rem;
  }
  
  .form-title {
    font-size: 2rem;
  }
}

@media (max-width: 600px) {
  .form-panel {
    padding: 1rem;
  }
  
  .demo-section {
    flex-direction: column;
  }
  
  .stats-row {
    flex-direction: column;
    gap: 1rem;
  }
}
</style>