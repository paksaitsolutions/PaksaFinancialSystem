<template>
  <div class="auth-layout">
    <div class="auth-container">
      <!-- Left Side: Form Container -->
      <div class="form-container">
        <div class="form-content">
          <!-- Branding (mobile only) -->
          <div class="mobile-branding">
            <img 
              :src="logoSrc" 
              alt="Paksa Financial System" 
              class="logo"
            />
            <h1 class="brand-title">Paksa Financial System</h1>
          </div>
          
          <!-- Page Header Slot -->
          <slot name="header"></slot>
          
          <!-- Main Content Slot -->
          <div class="content-slot">
            <slot></slot>
          </div>
        </div>
      </div>

      <!-- Right Side: Hero Background (Desktop Only) -->
      <div class="hero-sidebar">
        <div class="hero-background" :style="{ backgroundImage: `url(${loginBg})` }"></div>
        <div class="hero-overlay"></div>

        <div class="hero-content">
          <div class="hero-inner">
            <img 
              :src="logoSrc" 
              alt="Paksa Financial System" 
              class="hero-logo"
            />
            <h2 class="hero-title">Paksa Financial System</h2>
            <p class="hero-subtitle">
              Streamline your financial operations with our comprehensive suite of tools.
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import loginBg from '@/assets/login-bg.jpg';
import logoSrc from '@/assets/logo.svg';
</script>

<style scoped>
/* Base Layout */
.auth-layout {
  min-height: 100vh;
  background: linear-gradient(135deg, var(--primary-50) 0%, var(--primary-100) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.auth-container {
  display: flex;
  width: 100%;
  max-width: 1100px;
  min-height: 650px;
  background: var(--surface-card);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

/* Form Container */
.form-container {
  flex: 1;
  padding: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--surface-card);
  position: relative;
  z-index: 2;
}

.form-content {
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
}

/* Mobile Branding */
.mobile-branding {
  text-align: center;
  margin-bottom: 2rem;
  display: none;
}

.mobile-branding .logo {
  height: 64px;
  margin-bottom: 1rem;
}

.mobile-branding .brand-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--primary-color);
  margin: 0;
}

/* Hero Sidebar */
.hero-sidebar {
  flex: 1;
  position: relative;
  display: none;
  background: var(--primary-color);
}

.hero-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-size: cover;
  background-position: center;
  opacity: 0.9;
}

.hero-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, var(--primary-600) 0%, var(--primary-900) 100%);
  opacity: 0.9;
}

.hero-content {
  position: relative;
  z-index: 2;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  color: white;
  text-align: center;
}

.hero-inner {
  max-width: 400px;
}

.hero-logo {
  height: 80px;
  margin-bottom: 1.5rem;
}

.hero-title {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 1rem;
  line-height: 1.2;
}

.hero-subtitle {
  font-size: 1.1rem;
  opacity: 0.9;
  line-height: 1.6;
  margin: 0;
}

/* Content Slot */
.content-slot {
  margin-top: 1.5rem;
}

/* Responsive Styles */
@media (min-width: 992px) {
  .auth-layout {
    padding: 2rem;
  }
  
  .hero-sidebar {
    display: flex;
  }
  
  .mobile-branding {
    display: none;
  }
  
  .form-container {
    flex: 0 0 50%;
    max-width: 50%;
  }
}

@media (max-width: 991px) {
  .mobile-branding {
    display: block;
  }
  
  .auth-container {
    min-height: auto;
    max-width: 500px;
  }
  
  .form-container {
    padding: 2rem 1.5rem;
  }
}

/* Print Styles */
@media print {
  .hero-sidebar {
    display: none;
  }
  
  .form-container {
    flex: 1;
    max-width: 100%;
  }
}
</style>
