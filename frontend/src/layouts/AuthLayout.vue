<template>
  <div class="auth-layout">
    <router-view />
  </div>
</template>

<script setup lang="ts">
// No script needed for this simple layout
</script>

<style scoped>
.auth-layout {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
</style>