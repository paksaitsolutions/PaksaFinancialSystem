<!--
  Paksa Financial System - Lazy Error Component
  Copyright (c) 2025 Paksa IT Solutions. All rights reserved.
-->
<template>
  <div class="lazy-error">
    <i class="pi pi-exclamation-triangle" style="font-size: 2rem; color: var(--red-500)"></i>
    <p>Failed to load component</p>
    <Button label="Retry" size="small" @click="retry" />
  </div>
</template>

<script setup lang="ts">
const emit = defineEmits<{
  retry: []
}>();

const retry = () => {
  emit('retry');
  window.location.reload();
};
</script>

<style scoped>
.lazy-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  gap: 1rem;
}
</style>
