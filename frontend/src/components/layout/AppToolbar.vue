<template>
    <v-app-bar app color="white" flat class="elevation-2">
      <v-app-bar-title class="font-weight-bold text-primary">
        <img src="/logo.svg" alt="Logo" style="height: 28px;" class="mr-3" />
        Paksa Financial System
      </v-app-bar-title>
      <v-spacer />
      <v-btn icon><v-icon>mdi-bell</v-icon></v-btn>
      <!-- <v-avatar size="32"><img src="/user.jpg" /></v-avatar> -->
    </v-app-bar>
  </template>
  
  <script setup lang="ts">
  // No extra logic yet; add user/account/notification logic here as needed.
  </script>
  
  <style scoped>
  .v-app-bar-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #1976d2;
    letter-spacing: 0.01em;
  }
  </style>
  