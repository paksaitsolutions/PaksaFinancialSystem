<template>
  <div class="not-found-container">
    <Card class="not-found-card">
      <template #content>
        <div class="text-center p-4">
          <i class="pi pi-exclamation-circle" style="font-size: 6rem; color: var(--red-500)"></i>
          <h1 class="text-6xl font-bold my-4">404</h1>
          <h2 class="text-2xl font-medium mb-4">Page Not Found</h2>
          <p class="text-color-secondary mb-6">The page you're looking for doesn't exist.</p>
          <Button 
            label="Go to Dashboard" 
            icon="pi pi-home" 
            @click="goToDashboard"
            class="p-button-primary"
          />
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import Card from 'primevue/card';
import Button from 'primevue/button';

const router = useRouter();

const goToDashboard = () => {
  router.push('/dashboard');
};
</script>

<style scoped>
.not-found-container {
  background: var(--surface-ground);
  min-height: 100vh;
  padding: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.not-found-card {
  border-radius: 12px;
  max-width: 500px;
  width: 100%;
}

:deep(.p-card-content) {
  padding: 2rem;
}

:deep(.p-button) {
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
}
</style>