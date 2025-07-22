<template>
  <v-container fluid class="fill-height pa-0 gradient-bg">
    <v-row class="fill-height" no-gutters>
      <!-- Left Side (Form) -->
      <v-col cols="12" md="6" class="d-flex justify-center align-center">
        <v-card max-width="400" class="pa-6 elevation-10">
          <v-card-title class="text-h5 font-weight-bold">Login</v-card-title>
          <v-card-text>
            <v-form @submit.prevent="handleLogin">
              <v-text-field
                v-model="email"
                label="Email"
                type="email"
                required
                class="mb-4"
              ></v-text-field>

              <v-text-field
                v-model="password"
                label="Password"
                :type="showPassword ? 'text' : 'password'"
                :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
                @click:append-inner="showPassword = !showPassword"
                required
                class="mb-4"
              ></v-text-field>

              <v-row align="center" class="mb-2">
                <v-col cols="6">
                  <v-checkbox
                    v-model="keepLoggedIn"
                    label="Keep me logged in"
                    dense
                  ></v-checkbox>
                </v-col>
                <v-col cols="6" class="text-right">
                  <a class="text-subtitle-2" href="/auth/forgot-password">Forgot password?</a>
                </v-col>
              </v-row>

              <v-btn
                :loading="authStore.isLoading"
                type="submit"
                color="primary"
                block
                class="mt-2"
              >
                Login
              </v-btn>
            </v-form>
          </v-card-text>

          <v-card-actions class="justify-center">
            <span class="text-body-2">Don't have an account?</span>
            <router-link to="/auth/register" class="ml-1 text-primary">
              Sign up
            </router-link>
          </v-card-actions>
        </v-card>
      </v-col>

      <!-- Right Side (Banner) -->
      <v-col md="6" class="d-none d-md-flex align-center justify-center">
        <div class="px-10 py-8 text-center">
          <h2 class="text-h4 font-weight-bold mb-2">Welcome to Paksa Financial</h2>
          <p class="text-subtitle-1">Changing the way financial management works</p>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useAuthStore } from '@/modules/auth/store/auth.store';

const email = ref('');
const password = ref('');
const keepLoggedIn = ref(true);
const showPassword = ref(false);
const authStore = useAuthStore();

const handleLogin = async () => {
  await authStore.login(email.value, password.value);
};
</script>

<style scoped>
.gradient-bg {
  background: linear-gradient(135deg, #f5f7fa, #c3cfe2);
}
</style>
