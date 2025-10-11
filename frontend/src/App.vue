<template>
  <div id="app" data-theme="light">
    <component :is="layout" v-if="layout">
      <router-view />
    </component>
    <router-view v-else />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

// Import all layout components
import AppLayout from './layouts/AppLayout.vue'
import AuthLayout from './layouts/AuthLayout.vue'
import ErrorLayout from './layouts/ErrorLayout.vue'
import MainLayout from './layouts/MainLayout.vue'

// Map of layout names to their components
const layouts = {
  AppLayout,
  AuthLayout,
  ErrorLayout,
  MainLayout
}

// Determine which layout to use based on the route
const layout = computed(() => {
  // If layout is explicitly null, return null (no wrapper)
  if (route.meta.layout === null) {
    return null
  }
  
  // Get the layout name from route meta or default to 'AppLayout'
  const layoutName = (route.meta.layout || 'AppLayout') as keyof typeof layouts
  
  // Return the corresponding layout component or fallback to AppLayout
  return layouts[layoutName] || AppLayout
})
</script>

<style>
/* Global styles */
* {
  box-sizing: border-box;
}

html, body {
  margin: 0;
  padding: 0;
  font-family: 'Roboto', sans-serif;
  height: 100%;
  overflow-x: hidden;
}

#app {
  min-height: 100vh;
  width: 100%;
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