<template>
  <v-card>
    <v-card-title>GL Analytics</v-card-title>
    <v-card-text>
      <chart-js :data="glData" />
      <div v-if="multiCurrency">
        <h4>Multi-Currency Balances</h4>
        <ul>
          <li v-for="(amount, currency) in multiCurrency" :key="currency">
            {{ currency }}: {{ amount }}
          </li>
        </ul>
      </div>
      <div v-if="budgetReport">
        <h4>Budget Report</h4>
        <ul>
          <li v-for="budget in budgetReport.budgets" :key="budget.account">
            {{ budget.account }}: Budget {{ budget.budget }}, Actual {{ budget.actual }}
          </li>
        </ul>
      </div>
      <div v-if="consolidation">
        <h4>Consolidation</h4>
        <ul>
          <li v-for="entity in consolidation.entities" :key="entity.name">
            {{ entity.name }}: {{ entity.total }}
          </li>
        </ul>
      </div>
    </v-card-text>
  </v-card>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { getMultiCurrencyBalances, getBudgetReport, getConsolidationReport } from '@/services/glAnalyticsService';
const glData = ref([]);
const multiCurrency = ref(null);
const budgetReport = ref(null);
const consolidation = ref(null);
onMounted(async () => {
  multiCurrency.value = await getMultiCurrencyBalances();
  budgetReport.value = await getBudgetReport();
  consolidation.value = await getConsolidationReport();
});
</script>
