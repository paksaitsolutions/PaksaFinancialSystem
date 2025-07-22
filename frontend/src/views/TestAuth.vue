<template>
  <div class="p-4">
    <h1 class="text-2xl font-bold mb-4">Authentication Test</h1>
    
    <div v-if="!isAuthenticated" class="space-y-4">
      <div class="card p-4 shadow-md rounded-lg bg-white">
        <h2 class="text-xl font-semibold mb-4">Login</h2>
        <form @submit.prevent="handleLogin" class="space-y-4">
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700">Email</label>
            <input
              id="email"
              v-model="loginForm.email"
              type="email"
              required
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            />
          </div>
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700">Password</label>
            <input
              id="password"
              v-model="loginForm.password"
              type="password"
              required
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
            />
          </div>
          <div class="flex items-center">
            <input
              id="rememberMe"
              v-model="loginForm.rememberMe"
              type="checkbox"
              class="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <label for="rememberMe" class="ml-2 block text-sm text-gray-700">
              Remember me
            </label>
          </div>
          <button
            type="submit"
            :disabled="loading"
            class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
          >
            {{ loading ? 'Logging in...' : 'Log in' }}
          </button>
        </form>
        <div v-if="error" class="mt-4 p-3 bg-red-50 text-red-700 rounded-md">
          {{ error }}
        </div>
      </div>
    </div>
    
    <div v-else class="space-y-4">
      <div class="card p-4 shadow-md rounded-lg bg-white">
        <h2 class="text-xl font-semibold mb-4">User Information</h2>
        <div class="space-y-2">
          <p><span class="font-medium">Name:</span> {{ currentUser?.name || 'N/A' }}</p>
          <p><span class="font-medium">Email:</span> {{ currentUser?.email || 'N/A' }}</p>
          <p><span class="font-medium">User ID:</span> {{ currentUser?.id || 'N/A' }}</p>
          <p><span class="font-medium">Permissions:</span> {{ currentUser?.permissions?.join(', ') || 'None' }}</p>
        </div>
        <button
          @click="handleLogout"
          class="mt-4 w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
        >
          Logout
        </button>
      </div>
      
      <div class="card p-4 shadow-md rounded-lg bg-white">
        <h2 class="text-xl font-semibold mb-4">Test Protected API</h2>
        <button
          @click="testProtectedApi"
          :disabled="apiLoading"
          class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
        >
          {{ apiLoading ? 'Testing...' : 'Test Protected Endpoint' }}
        </button>
        <div v-if="apiResult" class="mt-4 p-3 bg-gray-50 rounded-md overflow-auto max-h-60">
          <pre class="text-sm">{{ JSON.stringify(apiResult, null, 2) }}</pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/modules/auth/store/auth.store';

const authStore = useAuthStore();
const router = useRouter();

const loginForm = ref({
  email: '',
  password: '',
  rememberMe: true
});

const loading = ref(false);
const error = ref('');
const apiLoading = ref(false);
const apiResult = ref(null);

const isAuthenticated = computed(() => authStore.isAuthenticated);
const currentUser = computed(() => authStore.currentUser);

onMounted(async () => {
  // If we're not authenticated but have a token, try to initialize
  if (!isAuthenticated.value && (localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token'))) {
    await authStore.initialize();
  }
});

const handleLogin = async () => {
  if (loading.value) return;
  
  loading.value = true;
  error.value = '';
  
  try {
    const success = await authStore.login({
      email: loginForm.value.email,
      password: loginForm.value.password,
      rememberMe: loginForm.value.rememberMe
    });
    
    if (!success) {
      throw new Error('Login failed. Please check your credentials.');
    }
    
    // Clear the form
    loginForm.value = { email: '', password: '', rememberMe: true };
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'An error occurred during login';
  } finally {
    loading.value = false;
  }
};

const handleLogout = async () => {
  await authStore.logout();
  // Clear any test results
  apiResult.value = null;
};

const testProtectedApi = async () => {
  if (apiLoading.value) return;
  
  apiLoading.value = true;
  apiResult.value = null;
  
  try {
    // Replace with your actual protected API endpoint
    const response = await fetch('/api/protected/me', {
      headers: {
        'Authorization': `Bearer ${authStore.token}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error(`API request failed with status ${response.status}`);
    }
    
    apiResult.value = await response.json();
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to fetch protected data';
  } finally {
    apiLoading.value = false;
  }
};
</script>
