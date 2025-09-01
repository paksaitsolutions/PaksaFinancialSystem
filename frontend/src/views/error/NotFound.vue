<template>
  <div class="error-page">
    <div class="error-content">
      <h1 class="error-code">404</h1>
      <h2 class="error-title">Page Not Found</h2>
      <p class="error-message">
        The page you are looking for might have been removed, had its name changed, or is temporarily unavailable.
      </p>
      <Button 
        label="Go to Dashboard" 
        icon="pi pi-home"
        @click="$router.push('/')"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
// No script needed
</script>

<style scoped>
.error-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 50vh;
  text-align: center;
}

.error-content {
  max-width: 500px;
}

.error-code {
  font-size: 6rem;
  font-weight: 700;
  color: var(--primary-color);
  margin: 0;
  line-height: 1;
}

.error-title {
  font-size: 2rem;
  color: var(--text-color);
  margin: 1rem 0;
}

.error-message {
  color: var(--text-color-secondary);
  margin-bottom: 2rem;
  line-height: 1.6;
}
</style>