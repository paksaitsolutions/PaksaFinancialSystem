<template>
  <div class="auth-layout">
    <!-- Left Panel with Branding and Features -->
    <div class="left-panel">
      <div class="logo-container">
        <img 
          src="@/assets/logo.png" 
          alt="Paksa Financial System" 
          class="logo"
        >
        <h1 class="system-title">
          Paksa Financial System
        </h1>
        <p class="system-tagline">
          Complete Enterprise Financial Management
        </p>
      </div>

      <div class="features-section">
        <div class="feature-item" v-for="feature in features" :key="feature.title">
          <i :class="feature.icon"></i>
          <h3>{{ feature.title }}</h3>
          <p>{{ feature.description }}</p>
        </div>
      </div>
    </div>

    <!-- Right Panel with Authentication Form -->
    <div class="right-panel">
      <div class="form-container">
        <slot />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const currentYear = ref(new Date().getFullYear());

const features = [
  {
    icon: 'pi pi-shield',
    title: 'Secure & Reliable',
    description: 'Enterprise-grade security to protect your financial data'
  },
  {
    icon: 'pi pi-chart-line',
    title: 'Real-time Analytics',
    description: 'Get instant insights into your financial performance'
  },
  {
    icon: 'pi pi-cog',
    title: 'Customizable',
    description: 'Tailor the system to fit your business needs'
  }
];

// Add meta tag to prevent layout shift on mobile
onMounted(() => {
  const viewportMeta = document.createElement('meta');
  viewportMeta.name = 'viewport';
  viewportMeta.content = 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no';
  document.head.appendChild(viewportMeta);
  
  return () => {
    document.head.removeChild(viewportMeta);
  };
});
</script>

<style scoped>
/* Base Layout */
.auth-layout {
  display: flex;
  min-height: 100vh;
  margin: 0;
  padding: 0;
  overflow: auto;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  line-height: 1.5;
  color: #2c3e50;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: #f8f9fa;
}

/* Ensure form container takes full height */
.form-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-height: 100%;
  padding: 2rem;
  width: 100%;
  max-width: 500px;
  margin: 0 auto;
}

/* Left Panel */
.left-panel {
  flex: 1;
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
  color: white;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: relative;
  overflow: hidden;
  min-height: 100vh;
}

.logo-container {
  text-align: center;
  margin-bottom: 3rem;
  z-index: 1;
  padding: 0 2rem;
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