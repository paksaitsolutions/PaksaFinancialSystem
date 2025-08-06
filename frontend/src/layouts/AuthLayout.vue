<template>
  <div class="auth-layout">
    <div class="auth-background">
      <div class="auth-background-overlay"></div>
    </div>

    <div class="auth-content">
      <div class="auth-branding hidden lg:flex">
        <div class="branding-content">
          <div class="logo-section mb-8">
            <img
              src="@/assets/logo.svg"
              alt="Paksa Financial System"
              class="logo mb-4"
            />
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
            <img
              src="@/assets/logo.svg"
              alt="Paksa Financial System"
              class="mobile-logo-img mx-auto mb-3"
            />
            <h2 class="text-2xl font-bold text-primary">
              Paksa Financial System
            </h2>
          </div>

          <router-view />

          <div class="auth-footer text-center mt-8">
            <div class="flex justify-content-center align-items-center flex-wrap mb-4">
              <a href="#" class="text-primary text-sm mx-2">Privacy Policy</a>
              <span class="text-300 mx-2">|</span>
              <a href="#" class="text-primary text-sm mx-2">Terms of Service</a>
              <span class="text-300 mx-2">|</span>
              <a href="#" class="text-primary text-sm mx-2">Support</a>
            </div>
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

.logo {
  width: 80px;
  height: auto;
}

.mobile-logo-img {
  width: 60px;
  height: auto;
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