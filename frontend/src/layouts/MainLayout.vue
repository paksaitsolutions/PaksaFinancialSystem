<template>
  <div class="main-layout">
    <left-sidebar />
    
    <v-main>
      <router-view />
    </v-main>
  </div>
</template>

<script setup>
import LeftSidebar from '../components/layout/LeftSidebar.vue';
</script>

<style scoped>
.main-layout {
  display: flex;
  min-height: 100vh;
}
</style>