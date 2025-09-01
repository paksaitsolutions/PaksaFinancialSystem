<template>
  <div class="main-layout">
    <div class="main-content">
      <router-view />
    </div>
  </div>
</template>

<script setup lang="ts">
// Simple layout for module pages that don't need sidebar
</script>

<style scoped>
.main-layout {
  min-height: 100vh;
  padding: 1rem;
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
}
</style>