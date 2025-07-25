<template>
  <v-app>
    <v-main>
      <v-container fluid class="fill-height">
        <v-row align="center" justify="center">
          <v-col cols="12" sm="8" md="6" lg="4">
            <v-card class="elevation-12">
              <v-card-title class="text-h4 text-center pa-6">
                Paksa Financial System
              </v-card-title>
              <v-card-text>
                <v-alert type="success" class="mb-4">
                  🎉 System is running successfully!
                </v-alert>
                <v-list>
                  <v-list-item>
                    <v-list-item-title>Backend API</v-list-item-title>
                    <v-list-item-subtitle>Running on port 8000</v-list-item-subtitle>
                  </v-list-item>
                  <v-list-item>
                    <v-list-item-title>Frontend</v-list-item-title>
                    <v-list-item-subtitle>Vue.js 3 + Vuetify</v-list-item-subtitle>
                  </v-list-item>
                  <v-list-item>
                    <v-list-item-title>Database</v-list-item-title>
                    <v-list-item-subtitle>PostgreSQL Ready</v-list-item-subtitle>
                  </v-list-item>
                </v-list>
              </v-card-text>
              <v-card-actions class="justify-center pb-6">
                <v-btn color="primary" size="large" href="/api/v1" target="_blank">
                  View API Docs
                </v-btn>
              </v-card-actions>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
// Simple app component for testing
</script>

<style scoped>
.v-card {
  border-radius: 12px;
}
</style>