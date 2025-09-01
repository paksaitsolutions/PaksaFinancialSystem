<template>
  <div class="auth-layout">
    <div class="auth-container">
      <div class="auth-content">
        <div class="auth-header">
          <img src="/logo.svg" alt="Paksa Financial" class="auth-logo" />
          <h1 class="auth-title">Paksa Financial System</h1>
        </div>
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// No script needed for this layout
</script>

<style scoped>
.auth-layout {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 1rem;
}

.auth-container {
  width: 100%;
  max-width: 400px;
}

.auth-content {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.auth-header {
  text-align: center;
  margin-bottom: 2rem;
}

.auth-logo {
  width: 60px;
  height: 60px;
  margin-bottom: 1rem;
}

.auth-title {
  color: #333;
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
}
</style>