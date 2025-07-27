<template>
  <v-container fluid class="dashboard-container">
    <v-row>
      <v-col cols="12">
        <v-card class="dashboard-card" elevation="2">
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-3" size="28" color="primary">mdi-view-dashboard</v-icon>
            <h1 class="text-h4 font-weight-bold">Dashboard</h1>
          </v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="12" sm="6" md="3" v-for="stat in stats" :key="stat.title">
                <v-card class="stat-card" elevation="1">
                  <v-card-text class="pa-4">
                    <div class="d-flex align-center">
                      <v-avatar :color="stat.color" size="40">
                        <v-icon color="white" size="20">{{ stat.icon }}</v-icon>
                      </v-avatar>
                      <div class="ml-3">
                        <div class="text-h6 font-weight-bold">{{ stat.value }}</div>
                        <div class="text-caption text-medium-emphasis">{{ stat.title }}</div>
                      </div>
                    </div>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const stats = ref([
  { title: 'Total Revenue', value: '$125,000', icon: 'mdi-trending-up', color: 'success' },
  { title: 'Total Expenses', value: '$85,000', icon: 'mdi-trending-down', color: 'error' },
  { title: 'Net Profit', value: '$40,000', icon: 'mdi-chart-line', color: 'primary' },
  { title: 'Active Accounts', value: '156', icon: 'mdi-account-multiple', color: 'info' }
])
</script>

<style scoped>
.dashboard-container {
  background: #fafafa;
  min-height: 100vh;
  padding: 16px;
}

.dashboard-card {
  border-radius: 12px;
}

.stat-card {
  border-radius: 8px;
  transition: all 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
</style>