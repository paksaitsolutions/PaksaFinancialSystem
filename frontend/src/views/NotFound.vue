<template>
  <v-container fluid class="not-found-container">
    <v-card class="not-found-card" elevation="2">
      <v-card-text class="text-center pa-8">
        <v-icon size="96" color="error">mdi-alert-circle</v-icon>
        <h1 class="text-h3 mt-4 mb-2">404</h1>
        <h2 class="text-h5 mb-4">Page Not Found</h2>
        <p class="text-body-1 text-medium-emphasis mb-6">The page you're looking for doesn't exist.</p>
        <v-btn color="primary" size="large" @click="$router.push('/dashboard')">
          <v-icon start>mdi-home</v-icon>
          Go to Dashboard
        </v-btn>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<style scoped>
.not-found-container {
  background: #fafafa;
  min-height: 100vh;
  padding: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.not-found-card {
  border-radius: 12px;
  max-width: 500px;
}
</style>