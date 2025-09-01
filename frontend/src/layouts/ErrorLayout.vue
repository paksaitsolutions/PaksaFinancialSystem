<template>
  <div class="error-layout">
    <div class="error-container">
      <router-view />
      <div class="error-footer">
        <router-link to="/" class="back-home">
          <i class="pi pi-home"></i>
          Back to Home
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// No script needed
</script>

<style scoped>
.error-layout {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--surface-ground);
  padding: 1rem;
}

.error-container {
  text-align: center;
  max-width: 500px;
}

.error-footer {
  margin-top: 2rem;
}

.back-home {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 500;
}

.back-home:hover {
  text-decoration: underline;
}
</style>