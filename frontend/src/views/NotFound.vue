<template>
  <div class="not-found">
    <v-container class="text-center">
      <v-row justify="center">
        <v-col cols="12" md="6">
          <v-card class="pa-6">
            <v-card-title class="text-h3 mb-4">404</v-card-title>
            <v-card-subtitle class="text-h5 mb-4">Page Not Found</v-card-subtitle>
            <v-card-text>
              <p class="text-body-1 mb-4">
                The page you are looking for does not exist or has been moved.
              </p>
              <v-btn color="primary" to="/" size="large">
                Go to Home
              </v-btn>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup>
// No additional logic needed
</script>

<style scoped>
.not-found {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>