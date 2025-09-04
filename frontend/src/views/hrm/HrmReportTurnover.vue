<template>
  <div class="hrm-report-turnover">
    <Card>
      <template #header>
        Hrm Report Turnover
      </template>
      <div v-if="turnoverData">
        <p>Turnover Rate: {{ turnoverData.turnover_rate }}</p>
        <p>Report Date: {{ turnoverData.report_date }}</p>
        <p>Employee Count: {{ turnoverData.employee_count }}</p>
        <p>Departed Count: {{ turnoverData.departed_count }}</p>
      </div>
      <p v-else>Loading...</p>
    </Card>
  </div>
</template>

<script setup lang="ts">
import Card from 'primevue/card';
import { ref, onMounted } from 'vue';
import axios from 'axios';

interface TurnoverData {
  turnover_rate: number;
  report_date: string;
  employee_count: number;
  departed_count: number;
}

const turnoverData = ref<TurnoverData | null>(null);

onMounted(async () => {
  try {
    const response = await axios.get('/api/v1/hrm/reports/turnover');
    turnoverData.value = response.data;
  } catch (error) {
    console.error('Error fetching turnover data:', error);
  }
});
</script>

<style scoped>
.hrm-report-turnover {
  padding: 1rem;
}
</style>