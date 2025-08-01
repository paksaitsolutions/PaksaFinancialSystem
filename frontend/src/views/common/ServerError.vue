<template>
  <div class="error-container">
    <Card class="error-card">
      <template #content>
        <div class="text-center p-4">
          <i class="pi pi-exclamation-triangle" style="font-size: 6rem; color: var(--red-500)"></i>
          <h1 class="text-6xl font-bold my-4">500</h1>
          <h2 class="text-2xl font-medium mb-4">Server Error</h2>
          <p class="text-color-secondary mb-6">Something went wrong on our end. Please try again later.</p>
          <div class="flex justify-content-center gap-3">
            <Button 
              label="Go to Dashboard" 
              icon="pi pi-home" 
              @click="goToDashboard"
              class="p-button-primary"
            />
            <Button 
              label="Try Again" 
              icon="pi pi-refresh" 
              @click="reloadPage"
              class="p-button-secondary"
            />
          </div>
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

const reloadPage = () => {
  window.location.reload();
};
</script>

<style scoped>
.error-container {
  background: var(--surface-ground);
  min-height: 100vh;
  padding: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.error-card {
  border-radius: 12px;
  max-width: 500px;
  width: 100%;
}

:deep(.p-card-content) {
  padding: 0;
}
</style>
