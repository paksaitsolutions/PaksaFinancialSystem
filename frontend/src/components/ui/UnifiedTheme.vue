<template>
  <div class="unified-theme-provider" :class="themeClasses">
    <slot />
  </div>
</template>

<script setup lang="ts">
import { computed, provide, onMounted } from 'vue'
import { useTheme } from '@/composables/useTheme'

const { isDarkMode, currentTheme } = useTheme()

const themeClasses = computed(() => ({
  'theme-light': !isDarkMode.value,
  'theme-dark': isDarkMode.value,
  'unified-theme': true
}))

// Provide theme context to child components
provide('theme', {
  isDark: isDarkMode,
  theme: currentTheme
})

onMounted(() => {
  // Apply unified CSS variables
  const root = document.documentElement
  
  if (isDarkMode.value) {
    // Dark theme variables
    root.style.setProperty('--primary-50', '#eff6ff')
    root.style.setProperty('--primary-500', '#3b82f6')
    root.style.setProperty('--primary-600', '#2563eb')
    root.style.setProperty('--surface-0', '#ffffff')
    root.style.setProperty('--surface-50', '#f8fafc')
    root.style.setProperty('--surface-100', '#f1f5f9')
    root.style.setProperty('--surface-200', '#e2e8f0')
    root.style.setProperty('--text-color', '#0f172a')
    root.style.setProperty('--text-color-secondary', '#64748b')
  } else {
    // Light theme variables
    root.style.setProperty('--primary-50', '#eff6ff')
    root.style.setProperty('--primary-500', '#3b82f6')
    root.style.setProperty('--primary-600', '#2563eb')
    root.style.setProperty('--surface-0', '#ffffff')
    root.style.setProperty('--surface-50', '#f8fafc')
    root.style.setProperty('--surface-100', '#f1f5f9')
    root.style.setProperty('--surface-200', '#e2e8f0')
    root.style.setProperty('--text-color', '#0f172a')
    root.style.setProperty('--text-color-secondary', '#64748b')
  }
})
</script>

<style>
.unified-theme {
  --border-radius: 8px;
  --border-radius-lg: 12px;
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;
  --font-size-xl: 1.25rem;
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  --transition-fast: 150ms ease;
  --transition-normal: 300ms ease;
}
</style>