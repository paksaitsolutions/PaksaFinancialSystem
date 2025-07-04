<template>
  <div class="auth-layout" :class="{ 'rtl': isRTL }">
    <!-- Background -->
    <div class="auth-bg">
      <div class="auth-bg-overlay"></div>
      <div class="auth-bg-pattern"></div>
    </div>
    
    <!-- Content -->
    <div class="auth-container">
      <!-- Logo -->
      <div class="text-center mb-6">
        <img 
          src="@/assets/images/logo-white.png" 
          alt="Paksa Financial System" 
          class="auth-logo"
        >
        <h1 class="text-3xl font-bold text-white mt-4">Paksa Financial System</h1>
      </div>
      
      <!-- Auth Card -->
      <div class="auth-card">
        <!-- Language Switcher -->
        <div class="flex justify-end mb-4">
          <LanguageSwitcher />
        </div>
        
        <!-- Page Title -->
        <h2 class="text-2xl font-semibold text-gray-800 mb-6 text-center">
          {{ pageTitle }}
        </h2>
        
        <!-- Router View -->
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
        
        <!-- Footer Links -->
        <div class="mt-6 pt-6 border-t border-gray-200 text-center">
          <p class="text-sm text-gray-600">
            &copy; {{ currentYear }} Paksa IT Solutions. All rights reserved.
          </p>
          <div class="mt-2">
            <router-link 
              to="/privacy-policy" 
              class="text-sm text-primary-600 hover:text-primary-800 mr-4"
            >
              Privacy Policy
            </router-link>
            <router-link 
              to="/terms" 
              class="text-sm text-primary-600 hover:text-primary-800"
            >
              Terms of Service
            </router-link>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Loading Overlay -->
    <div v-if="isLoading" class="loading-overlay">
      <ProgressSpinner />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useAppStore } from '@/store/app';
import LanguageSwitcher from '@/components/common/LanguageSwitcher.vue';
import ProgressSpinner from 'primevue/progressspinner';

const appStore = useAppStore();
const route = useRoute();

// Computed
const isLoading = computed(() => appStore.isLoading);
const isRTL = computed(() => appStore.isRTL);
const currentYear = computed(() => new Date().getFullYear());
const pageTitle = computed(() => {
  return route.meta.title || 'Authentication';
});

// Set page title on mount
onMounted(() => {
  document.title = `${pageTitle.value} | Paksa Financial System`;
});
</script>

<style scoped>
.auth-layout {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  background-color: #f5f7fa;
  overflow: hidden;
}

.auth-bg {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 0;
  background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%);
}

.auth-bg-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1;
}

.auth-bg-pattern {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI1NiIgaGVpZ2h0PSI1NiIgdmlld0JveD0iMCAwIDU2IDU2Ij48cmVjdCB3aWR0aD0iNTYiIGhlaWdodD0iNTYiIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4wNSIvPjwvc3ZnPg==');
  opacity: 0.15;
  z-index: 2;
}

.auth-container {
  position: relative;
  z-index: 10;
  width: 100%;
  max-width: 480px;
  padding: 2rem;
  margin: 0 auto;
}

.auth-logo {
  height: 60px;
  width: auto;
  margin: 0 auto;
}

.auth-card {
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  padding: 2.5rem;
  position: relative;
  overflow: hidden;
}

/* Loading overlay */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1100;
  backdrop-filter: blur(2px);
}

/* Animations */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* RTL Support */
.rtl .auth-card {
  direction: rtl;
  text-align: right;
}

/* Responsive */
@media (max-width: 640px) {
  .auth-container {
    padding: 1rem;
  }
  
  .auth-card {
    padding: 1.5rem;
  }
}
</style>
