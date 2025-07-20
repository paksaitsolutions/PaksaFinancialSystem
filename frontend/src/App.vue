<template>
  <v-app>
    <v-app-bar app color="primary" dark v-if="isAuthenticated">
      <v-toolbar-title>Paksa Financial System</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn text @click="handleLogout" v-if="isAuthenticated">
        <v-icon left>mdi-logout</v-icon>
        Logout
      </v-btn>
    </v-app-bar>
    
    <v-main>
      <v-container fluid class="fill-height">
        <v-row align="center" justify="center" v-if="isLoading">
          <v-progress-circular indeterminate color="primary"></v-progress-circular>
        </v-row>
        <router-view v-else />
      </v-container>
    </v-main>
    
    <app-snackbar />
  </v-app>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from './modules/auth/store';
import AppSnackbar from './components/AppSnackbar.vue';

const router = useRouter();
const authStore = useAuthStore();
const isAuthenticated = ref(false);
const isLoading = ref(true);

// Initialize auth state
const initialize = async () => {
  try {
    await authStore.initialize();
    isAuthenticated.value = authStore.isAuthenticated;
    
    // Redirect to login if not authenticated and not on login page
    if (!isAuthenticated.value && !window.location.pathname.includes('/auth')) {
      router.push({ name: 'Login', query: { redirect: window.location.pathname } });
    }
  } catch (error) {
    console.error('Error initializing app:', error);
  } finally {
    isLoading.value = false;
  }
};

// Handle logout
const handleLogout = async () => {
  try {
    await authStore.logout();
    isAuthenticated.value = false;
    router.push({ name: 'Login' });
  } catch (error) {
    console.error('Error during logout:', error);
  }
};

// Watch for auth state changes
const unsubscribe = authStore.$onAction(({ name, after }) => {
  if (name === 'setAuth' || name === 'clearAuth') {
    after(() => {
      isAuthenticated.value = authStore.isAuthenticated;
    });
  }
});

// Initialize on mount
onMounted(initialize);

// Clean up on unmount
onUnmounted(() => {
  unsubscribe();
});
</script>

<style scoped>
.fill-height {
  min-height: calc(100vh - 64px);
}
</style>