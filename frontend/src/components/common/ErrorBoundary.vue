<template>
  <div v-if="hasError" class="error-boundary">
    <div class="error-content">
      <i class="pi pi-exclamation-triangle error-icon"></i>
      <h3>Something went wrong</h3>
      <p>{{ errorMessage }}</p>
      <div class="error-actions">
        <Button label="Retry" @click="retry" class="p-button-outlined" />
        <Button label="Go Home" @click="goHome" class="p-button-text" />
      </div>
    </div>
  </div>
  <slot v-else />
</template>

<script setup lang="ts">
import { ref, onErrorCaptured } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const hasError = ref(false);
const errorMessage = ref('An unexpected error occurred.');

onErrorCaptured((error: Error) => {
  hasError.value = true;
  errorMessage.value = error.message || 'An unexpected error occurred.';
  console.error('Error caught by boundary:', error);
  return false;
});

const retry = () => {
  hasError.value = false;
  errorMessage.value = 'An unexpected error occurred.';
};

const goHome = () => {
  router.push('/');
};
</script>

<style scoped>
.error-boundary {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  padding: 2rem;
}

.error-content {
  text-align: center;
  max-width: 400px;
}

.error-icon {
  font-size: 3rem;
  color: var(--red-500);
  margin-bottom: 1rem;
}

.error-content h3 {
  margin: 0 0 1rem 0;
  color: var(--text-color);
}

.error-content p {
  margin: 0 0 2rem 0;
  color: var(--text-color-secondary);
}

.error-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}
</style>