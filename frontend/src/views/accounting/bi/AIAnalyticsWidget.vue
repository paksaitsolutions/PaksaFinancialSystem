<template>
  <v-card>
    <v-card-title>AI Analytics</v-card-title>
    <v-card-text>
      <div>
        <h4>Anomaly Detection</h4>
        <ul>
          <li v-for="anomaly in anomalies" :key="anomaly.type">
            {{ anomaly.type }}: {{ anomaly.value }}
          </li>
        </ul>
      </div>
      <div>
        <h4>Forecasting</h4>
        <ul>
          <li v-for="(value, idx) in forecast" :key="idx">
            Period {{ idx + 1 }}: {{ value }}
          </li>
        </ul>
      </div>
      <div>
        <h4>Recommendations</h4>
        <ul>
          <li v-for="rec in recommendations" :key="rec.action">
            {{ rec.action }}
          </li>
        </ul>
      </div>
    </v-card-text>
  </v-card>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { detectAnomalies, runForecasting, getRecommendations } from '@/services/aiAnalyticsService';
const anomalies = ref([]);
const forecast = ref([]);
const recommendations = ref([]);
onMounted(async () => {
  anomalies.value = (await detectAnomalies({ data: [] })).anomalies;
  forecast.value = (await runForecasting({ data: [] })).forecast;
  recommendations.value = (await getRecommendations({ context: {} })).recommendations;
});
</script>
