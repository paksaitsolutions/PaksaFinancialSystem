<template>
  <component :is="layout">
    <router-view />
  </component>
</template>

<script setup lang="ts">
import { computed, defineAsyncComponent, onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import { usePrimeVue } from 'primevue/config';

const route = useRoute();
const primevue = usePrimeVue();
const theme = ref(localStorage.getItem('theme') || 'lara-light-blue');

// Import all layout components statically
import AppLayout from './layouts/AppLayout.vue';
import AuthLayout from './layouts/AuthLayout.vue';
import ErrorLayout from './layouts/ErrorLayout.vue';

// Map of layout names to their components
const layouts = {
  AppLayout,
  AuthLayout,
  ErrorLayout,
  // Add other layouts here as needed
};

// Determine which layout to use based on the route
const layout = computed(() => {
  // Get the layout name from route meta or default to 'AppLayout'
  const layoutName = (route.meta.layout || 'AppLayout') as keyof typeof layouts;
  
  // Return the corresponding layout component or fallback to AppLayout
  return layouts[layoutName] || AppLayout;
});

onMounted(() => {
  // Initialize theme from localStorage or use default
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme) {
    theme.value = savedTheme;
    document.documentElement.setAttribute('data-theme', savedTheme);
  }
  
  // Apply PrimeVue ripple effect
  primevue.config.ripple = true;
});
</script>

<style>
/* Base styles */
.app-container {
  display: flex;
  min-height: 100vh;
  background-color: var(--surface-ground);
  color: var(--text-color);
  font-family: var(--font-family);
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  margin-left: 16rem; /* Match sidebar width */
  transition: margin-left 0.3s;
}

.content-container {
  flex: 1;
  padding: 1.5rem;
  background-color: var(--surface-ground);
  overflow-y: auto;
}

/* Responsive adjustments */
@media (max-width: 991px) {
  .main-content {
    margin-left: 0;
  }
  
  .content-container {
    padding: 1rem;
  }
}

/* PrimeVue overrides */
.p-component {
  font-family: var(--font-family);
}

/* Ensure proper spacing for the app bar */
.p-toolbar {
  background: var(--surface-card);
  border-bottom: 1px solid var(--surface-border);
  padding: 0.75rem 1.5rem;
}

/* Animation for page transitions */
.page-enter-active,
.page-leave-active {
  transition: opacity 0.2s;
}
.page-enter-from,
.page-leave-to {
  opacity: 0;
}
</style>
