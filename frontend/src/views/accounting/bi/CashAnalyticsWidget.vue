<template>
  <v-card>
    <v-card-title>Cash Management Analytics</v-card-title>
    <v-card-text>
      <div v-if="cashForecast">
        <h4>Cash Forecast</h4>
        <ul>
          <li v-for="item in cashForecast.forecast" :key="item.date">
            {{ item.date }}: {{ item.amount }}
          </li>
        </ul>
      </div>
      <div v-if="reconciliation">
        <h4>Enhanced Reconciliation</h4>
        <ul>
          <li v-for="detail in reconciliation.details" :key="detail.bank">
            Bank {{ detail.bank }}: {{ detail.matched ? 'Matched' : 'Unmatched' }}
          </li>
        </ul>
      </div>
    </v-card-text>
  </v-card>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { getCashForecast, getEnhancedReconciliation } from '@/services/cashAnalyticsService';
const cashForecast = ref(null);
const reconciliation = ref(null);
onMounted(async () => {
  cashForecast.value = await getCashForecast();
  reconciliation.value = await getEnhancedReconciliation();
});
</script>
