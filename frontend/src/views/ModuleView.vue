<template>
  <v-container fluid class="module-container">
    <v-card class="module-card" elevation="2">
      <v-card-title class="d-flex align-center">
        <v-icon class="mr-3" size="28" color="primary">mdi-cog</v-icon>
        <h1 class="text-h4 font-weight-bold">Module</h1>
      </v-card-title>
      <v-card-text class="text-center pa-8">
        <v-icon size="64" color="grey">mdi-construction</v-icon>
        <h2 class="text-h5 mt-4 mb-2">Under Development</h2>
        <p class="text-body-1 text-medium-emphasis">This module is currently being developed.</p>
        <v-btn color="primary" @click="$router.push('/dashboard')" class="mt-4">
          <v-icon start>mdi-arrow-left</v-icon>
          Back to Dashboard
        </v-btn>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<style scoped>
.module-container {
  background: #fafafa;
  min-height: 100vh;
  padding: 16px;
}

.module-card {
  border-radius: 12px;
}
</style>