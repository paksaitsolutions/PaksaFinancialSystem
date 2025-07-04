<template>
  <div class="error-layout" :class="{ 'rtl': isRTL }">
    <!-- Background -->
    <div class="error-bg">
      <div class="error-bg-overlay"></div>
    </div>
    
    <!-- Content -->
    <div class="error-container">
      <!-- Logo -->
      <div class="text-center mb-8">
        <router-link to="/">
          <img 
            src="@/assets/images/logo.png" 
            alt="Paksa Financial System" 
            class="error-logo"
          >
        </router-link>
      </div>
      
      <!-- Error Card -->
      <div class="error-card">
        <!-- Language Switcher -->
        <div class="flex justify-end mb-6">
          <LanguageSwitcher />
        </div>
        
        <!-- Router View -->
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
        
        <!-- Back to Home -->
        <div class="mt-8 text-center">
          <router-link 
            to="/" 
            class="inline-flex items-center text-primary-600 hover:text-primary-800 font-medium"
          >
            <i class="pi pi-arrow-left mr-2"></i>
            {{ $t('common.backToHome') }}
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useAppStore } from '@/store/app';
import LanguageSwitcher from '@/components/common/LanguageSwitcher.vue';

const appStore = useAppStore();

// Computed
const isRTL = computed(() => appStore.isRTL);
</script>

<style scoped>
.error-layout {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  background-color: #f5f7fa;
  padding: 2rem;
}

.error-bg {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 0;
  background: linear-gradient(135deg, #f0f4f8 0%, #e6ebf1 100%);
}

.error-bg-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI1NiIgaGVpZ2h0PSI1NiIgdmlld0JveD0iMCAwIDU2IDU2Ij48cmVjdCB3aWR0aD0iNTYiIGhlaWdodD0iNTYiIGZpbGw9IiNlNmU2ZTYiIGZpbGwtb3BhY2l0eT0iMC4yIi8+PC9zdmc+');
  opacity: 0.3;
  z-index: 1;
}

.error-container {
  position: relative;
  z-index: 10;
  width: 100%;
  max-width: 500px;
}

.error-logo {
  height: 50px;
  width: auto;
  margin: 0 auto;
  transition: transform 0.3s ease;
}

a:hover .error-logo {
  transform: scale(1.05);
}

.error-card {
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
  padding: 2.5rem;
  position: relative;
  overflow: hidden;
  text-align: center;
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
.rtl .error-card {
  direction: rtl;
  text-align: center;
}

/* Responsive */
@media (max-width: 640px) {
  .error-layout {
    padding: 1rem;
  }
  
  .error-card {
    padding: 1.5rem;
  }
  
  .error-logo {
    height: 40px;
  }
}
</style>
