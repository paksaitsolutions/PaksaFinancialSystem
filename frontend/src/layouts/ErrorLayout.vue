<template>
  <div class="error-layout">
    <div class="error-container">
      <router-view />
    </div>
  </div>
</template>

<script setup lang="ts">
// No script needed for this simple layout
</script>

<style scoped>
.error-layout {
  min-height: 100vh;
  background: var(--surface-ground, #f8f9fa);
  display: flex;
  align-items: center;
  justify-content: center;
}

.error-container {
  width: 100%;
  max-width: 600px;
  padding: 2rem;
}
</style>