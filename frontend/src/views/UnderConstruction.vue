<template>
  <div class="under-construction">
    <div class="construction-content">
      <i class="pi pi-cog" style="font-size: 3rem; color: var(--primary-color)"></i>
      <h2>Feature Under Construction</h2>
      <p>This feature is currently under development and will be available soon.</p>
      <Button 
        label="Back to Dashboard" 
        icon="pi pi-arrow-left" 
        @click="$router.push('/')"
        class="p-button-text"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import Button from 'vue/button';
</script>

<style scoped>
.under-construction {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  min-height: 300px;
  text-align: center;
  padding: 2rem;
}

.construction-content {
  max-width: 500px;
  margin: 0 auto;
}

h2 {
  margin: 1rem 0 0.5rem;
  color: var(--text-color);
}

p {
  color: var(--text-color-secondary);
  margin-bottom: 1.5rem;
}
</style>
