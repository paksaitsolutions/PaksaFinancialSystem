<template>
  <v-card>
    <v-card-title>AP Analytics</v-card-title>
    <v-card-text>
      <div v-if="apReport">
        <h4>AP Report</h4>
        <ul>
          <li>Total Bills: {{ apReport.summary.total_bills }}</li>
          <li>Total Paid: {{ apReport.summary.total_paid }}</li>
        </ul>
      </div>
      <div v-if="threeWayMatch">
        <h4>Three-Way Match Status</h4>
        <ul>
          <li v-for="match in threeWayMatch" :key="match.bill_id">
            Bill {{ match.bill_id }}: {{ match.matched ? 'Matched' : 'Mismatch' }}
          </li>
        </ul>
      </div>
    </v-card-text>
  </v-card>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { getAPReport, getThreeWayMatchStatus } from '@/services/apAnalyticsService';
const apReport = ref(null);
const threeWayMatch = ref([]);
onMounted(async () => {
  apReport.value = await getAPReport();
  threeWayMatch.value = await getThreeWayMatchStatus();
});
</script>
