<!--
  Paksa Financial System - Lazy Loading Component
  Copyright (c) 2025 Paksa IT Solutions. All rights reserved.
-->
<template>
  <div class="lazy-loading">
    <i class="pi pi-spin pi-spinner" style="font-size: 2rem"></i>
    <p>Loading...</p>
  </div>
</template>

<style scoped>
.lazy-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  gap: 1rem;
  color: var(--primary-color);
}
</style>
