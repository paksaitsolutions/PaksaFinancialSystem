<template>
  <v-btn
    :icon="themeStore.isDark ? 'mdi-weather-sunny' : 'mdi-weather-night'"
    variant="text"
    @click="themeStore.toggleTheme()"
    :title="themeStore.isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'"
  >
  </v-btn>
</template>

<script setup>
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()
</script>