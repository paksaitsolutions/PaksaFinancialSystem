<template>
  <div class="error-layout">
    <h1>Error</h1>
    <slot />
  </div>
</template>

<style scoped>
.error-layout {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  background-color: #f0f0f0;
}
</style>