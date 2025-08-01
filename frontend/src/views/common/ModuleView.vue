<template>
  <v-container class="fill-height">
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="6" class="text-center">
        <v-icon size="120" color="info" class="mb-4">mdi-cog</v-icon>
        <h1 class="text-h4 mb-4">Module Under Development</h1>
        <p class="text-body-1 mb-6">This module is currently being developed and will be available soon.</p>
        <v-btn color="primary" @click="$router.go(-1)">Go Back</v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
// Generic module placeholder for routes under development
</script>