<template>
  <v-card>
    <v-card-title>AR Analytics</v-card-title>
    <v-card-text>
      <div v-if="arReport">
        <h4>AR Report</h4>
        <ul>
          <li>Total Invoices: {{ arReport.summary.total_invoices }}</li>
          <li>Total Received: {{ arReport.summary.total_received }}</li>
        </ul>
      </div>
      <div v-if="dunning">
        <h4>Dunning & Dispute Status</h4>
        <ul>
          <li v-for="item in dunning" :key="item.invoice_id">
            Invoice {{ item.invoice_id }}: {{ item.status }}
          </li>
        </ul>
      </div>
    </v-card-text>
  </v-card>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { getARReport, getDunningStatus } from '@/services/arAnalyticsService';
const arReport = ref(null);
const dunning = ref([]);
onMounted(async () => {
  arReport.value = await getARReport();
  dunning.value = await getDunningStatus();
});
</script>
