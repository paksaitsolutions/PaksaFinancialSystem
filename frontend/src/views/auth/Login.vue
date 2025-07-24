<template>
  <v-app>
    <v-main>
      <v-container fluid class="pa-0 fill-height">
        <v-row no-gutters class="login-wrapper">
          <!-- Left Panel: Login -->
          <v-col cols="12" md="6" class="left-panel">
            <div class="login-box">
              <div class="logo-wrapper d-flex align-center mb-6">
                <v-img
                  src="@/assets/PFS Logo.png"
                  alt="Paksa Logo"
                  max-width="48"
                  max-height="48"
                  class="mr-2"
                  cover
                />
                <span class="logo-title">Welcome Back</span>
              </div>

              <h2 class="mb-4">Login to your account</h2>
              <p class="login-subtitle mb-6">Enter your credentials to continue</p>

              <v-form @submit.prevent="handleLogin" ref="form">
                <v-text-field
                  v-model="email"
                  label="Email"
                  type="email"
                  required
                  class="mb-4"
                  variant="outlined"
                />

                <v-text-field
                  v-model="password"
                  label="Password"
                  type="password"
                  required
                  class="mb-4"
                  variant="outlined"
                />

                <div class="d-flex justify-space-between align-center mb-4">
                  <v-checkbox
                    v-model="rememberMe"
                    label="Keep me logged in"
                    density="compact"
                    class="ma-0"
                  />
                  <a href="#" class="forgot">Forgot password?</a>
                </div>

                <v-btn
                  type="submit"
                  block
                  color="primary"
                  class="login-btn"
                  :loading="authStore.isLoading"
                >
                  Login
                </v-btn>
              </v-form>

              <div class="signup-link mt-4">
                Don’t have an account?
                <router-link to="/auth/register">Sign up</router-link>
              </div>
            </div>
          </v-col>

          <!-- Right Panel -->
          <v-col cols="12" md="6" class="right-panel d-flex align-center justify-center">
            <div class="slogan text-center">
              <h1>Welcome to Paksa Financial</h1>
              <p>Changing the way financial management works</p>
            </div>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useAuthStore } from '@/modules/auth/store/auth.store';

const authStore = useAuthStore();
const email = ref('');
const password = ref('');
const rememberMe = ref(false);

const handleLogin = async () => {
  if (!email.value || !password.value) return;
  await authStore.login(email.value, password.value);
};
</script>

<style scoped>
.login-wrapper {
  height: 100vh;
  background: #f5f7fa;
}

.left-panel {
  padding: 64px 48px;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-box {
  width: 100%;
  max-width: 400px;
  background: #fff;
  padding: 32px;
  border-radius: 12px;
  box-shadow: 0 2px 16px rgba(0, 0, 0, 0.05);
}

.logo-wrapper {
  display: flex;
  align-items: center;
}

.logo-title {
  font-size: 1.8rem;
  font-weight: 700;
  color: #7c3aed;
}

.login-subtitle {
  color: #6b7280;
  font-size: 0.95rem;
}

.right-panel {
  background: linear-gradient(to right, #56a8fa, #1976d2);
  color: #fff;
}

.slogan h1 {
  font-size: 2.5rem;
  font-weight: bold;
  margin-bottom: 16px;
}

.slogan p {
  font-size: 1.25rem;
  font-weight: 400;
  color: #f3e9ff;
}

.forgot {
  font-size: 0.9rem;
  color: #1976d2;
  text-decoration: none;
}

.signup-link {
  font-size: 0.9rem;
  text-align: center;
}

.login-btn {
  font-weight: 600;
  font-size: 1rem;
}
</style>
