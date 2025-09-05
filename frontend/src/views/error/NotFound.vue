<template>
  <div class="not-found">
    <div class="error-container">
      <div class="error-content">
        <div class="error-icon">
          <i class="pi pi-exclamation-triangle"></i>
        </div>
        <h1 class="error-title">404</h1>
        <h2 class="error-subtitle">Page Not Found</h2>
        <p class="error-description">
          The page you are looking for might have been removed, had its name changed, or is temporarily unavailable.
        </p>
        <div class="error-actions">
          <Button label="Go Home" icon="pi pi-home" @click="$router.push('/')" />
          <Button label="Go Back" icon="pi pi-arrow-left" class="p-button-outlined" @click="$router.go(-1)" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// No additional logic needed
</script>

<style scoped>
.not-found {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
}

.error-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  padding: 3rem;
  text-align: center;
  max-width: 500px;
  width: 100%;
}

.error-icon {
  font-size: 4rem;
  color: #f59e0b;
  margin-bottom: 1rem;
}

.error-title {
  font-size: 6rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
  line-height: 1;
}

.error-subtitle {
  font-size: 2rem;
  font-weight: 600;
  color: #374151;
  margin: 1rem 0;
}

.error-description {
  color: #6b7280;
  font-size: 1.1rem;
  line-height: 1.6;
  margin-bottom: 2rem;
}

.error-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

@media (max-width: 640px) {
  .error-container {
    padding: 2rem;
  }
  
  .error-title {
    font-size: 4rem;
  }
  
  .error-subtitle {
    font-size: 1.5rem;
  }
  
  .error-actions {
    flex-direction: column;
  }
}
</style>