<template>
  <v-card class="metric-card" elevation="2">
    <v-card-text>
      <div class="d-flex align-center justify-space-between">
        <div>
          <p class="text-subtitle-2 text-grey-600 mb-1">{{ title }}</p>
          <h3 class="text-h5 font-weight-bold">{{ value }}</h3>
          <div v-if="trend !== undefined" class="d-flex align-center mt-2">
            <v-icon 
              :color="trend >= 0 ? 'success' : 'error'" 
              size="small"
              class="mr-1"
            >
              {{ trend >= 0 ? 'mdi-trending-up' : 'mdi-trending-down' }}
            </v-icon>
            <span 
              :class="trend >= 0 ? 'text-success' : 'text-error'"
              class="text-caption font-weight-medium"
            >
              {{ Math.abs(trend) }}%
            </span>
          </div>
        </div>
        
        <div class="metric-icon">
          <v-avatar :color="color" size="48">
            <v-icon color="white" size="24">{{ icon }}</v-icon>
          </v-avatar>
        </div>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
interface Props {
  title: string
  value: string
  icon: string
  color: string
  trend?: number
}

defineProps<Props>()
</script>

<style scoped>
.metric-card {
  height: 120px;
  transition: transform 0.2s ease-in-out;
}

.metric-card:hover {
  transform: translateY(-2px);
}

.metric-icon {
  opacity: 0.9;
}
</style>