<template>
  <div class="auth-layout">
    <!-- No header, navigation, or any other layout elements -->
    <div class="auth-background">
      <div class="auth-background-overlay"></div>
    </div>

    <div class="auth-content">
      <div class="auth-branding hidden lg:flex">
        <div class="branding-content">
          <div class="logo-section mb-8">
            <div class="logo-placeholder mb-4"></div>
            <h1 class="text-4xl font-bold text-white mb-2">
              Paksa Financial System
            </h1>
            <p class="text-xl text-white opacity-90">
              Complete Enterprise Financial Management
            </p>
          </div>

          <div class="features-section">
            <div class="feature-item mb-6" v-for="feature in features" :key="feature.title">
              <i :class="feature.icon" class="text-4xl text-white mb-3"></i>
              <h3 class="text-xl font-medium text-white mb-2">
                {{ feature.title }}
              </h3>
              <p class="text-white opacity-80">
                {{ feature.description }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div class="auth-form-section">
        <div class="form-container">
          <div class="mobile-logo lg:hidden text-center mb-8">
            <div class="mobile-logo-placeholder mx-auto mb-3"></div>
            <h2 class="text-2xl font-bold text-primary">
              Paksa Financial System
            </h2>
          </div>

          <router-view />

          <div class="auth-footer text-center mt-8">
            <p class="text-600 text-sm">
              © {{ currentYear }} Paksa IT Solutions. All rights reserved.
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const currentYear = computed(() => new Date().getFullYear())

const features = [
  {
    icon: 'pi pi-chart-line',
    title: 'Advanced Analytics',
    description: 'Real-time financial insights and comprehensive reporting tools.'
  },
  {
    icon: 'pi pi-shield',
    title: 'Enterprise Security',
    description: 'Bank-level security with multi-factor authentication and encryption.'
  },
  {
    icon: 'pi pi-cloud',
    title: 'Cloud Integration',
    description: 'Seamless synchronization across all your devices and platforms.'
  }
]
</script>

<style scoped>
.auth-layout {
  min-height: 100vh;
  position: relative;
  overflow: hidden;
}

.auth-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  z-index: 0;
}

.auth-background-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.3);
  z-index: 1;
}

.auth-content {
  position: relative;
  z-index: 3;
  display: flex;
  min-height: 100vh;
}

.auth-branding {
  flex: 1;
  padding: 3rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.branding-content {
  max-width: 500px;
  width: 100%;
}

.logo-placeholder {
  width: 80px;
  height: 80px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.mobile-logo-placeholder {
  width: 60px;
  height: 60px;
  background: var(--primary-color);
  border-radius: 8px;
  opacity: 0.8;
}

.auth-form-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
}

.form-container {
  width: 100%;
  max-width: 450px;
}

.feature-item {
  text-align: center;
}

.auth-footer {
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  padding-top: 1.5rem;
}

@media (max-width: 1024px) {
  .auth-form-section {
    flex: none;
    width: 100%;
    min-height: 100vh;
  }
}

@media (max-width: 600px) {
  .auth-form-section {
    padding: 1rem;
  }
  
  .form-container {
    max-width: 100%;
  }
}
</style>