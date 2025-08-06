<template>
  <div class="auth-layout">
    <div class="auth-container">
      <div class="form-container">
        <div class="form-content">
          <router-view />
        </div>
      </div>
      <div class="hero-sidebar">
        <div class="hero-content">
          <h2>Paksa Financial System</h2>
          <p>Streamline your financial operations with our comprehensive suite of tools.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-layout {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.auth-container {
  display: flex;
  width: 100%;
  max-width: 1100px;
  height: 650px;
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.form-container {
  flex: 1;
  padding: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.form-content {
  width: 100%;
  max-width: 400px;
}

.hero-sidebar {
  flex: 1;
  background: linear-gradient(135deg, #3b82f6 0%, #1e3a8a 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  text-align: center;
  padding: 2rem;
}

.hero-content h2 {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 1rem;
}

.hero-content p {
  font-size: 1.1rem;
  opacity: 0.9;
  line-height: 1.6;
}

@media (max-width: 991px) {
  .auth-container {
    width: 100vw;
    height: 100vh;
    border-radius: 0;
    flex-direction: column;
  }
  
  .hero-sidebar {
    display: none;
  }
  
  .form-container {
    flex: 1;
  }
}
</style>