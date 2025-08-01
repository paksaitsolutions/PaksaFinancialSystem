<template>
  <v-container fluid class="business-intelligence pa-4">
    <v-row>
      <v-col cols="12">
        <v-toolbar color="transparent" density="compact" class="mb-4">
          <v-toolbar-title class="text-h5 font-weight-bold">Business Intelligence Dashboard</v-toolbar-title>
          <v-spacer></v-spacer>
          <v-btn-toggle v-model="timeRange" density="comfortable" variant="outlined" color="primary" mandatory>
            <v-btn value="7d">7D</v-btn>
            <v-btn value="30d">30D</v-btn>
            <v-btn value="90d">90D</v-btn>
            <v-btn value="1y">1Y</v-btn>
          </v-btn-toggle>
        </v-toolbar>
      </v-col>
    </v-row>

    <v-row>
      <!-- KPI Cards -->
      <v-col v-for="(kpi, i) in kpis" :key="i" cols="12" sm="6" md="3">
        <v-card height="100%">
          <v-card-text>
            <div class="d-flex justify-space-between align-center">
              <div>
                <div class="text-subtitle-2 text-medium-emphasis">{{ kpi.title }}</div>
                <div class="text-h4 font-weight-bold mt-1">{{ formatCurrency(kpi.value) }}</div>
              </div>
              <v-avatar :color="getTrendColor(kpi.trend)" size="48">
                <v-icon :color="kpi.trend >= 0 ? 'success' : 'error'">
                  {{ kpi.trend >= 0 ? 'mdi-arrow-up' : 'mdi-arrow-down' }}
                </v-icon>
              </v-avatar>
            </div>
            <div class="d-flex align-center mt-2">
              <span :class="kpi.trend >= 0 ? 'text-success' : 'text-error'" class="text-caption font-weight-bold">
                {{ Math.abs(kpi.trend) }}% {{ kpi.trend >= 0 ? 'increase' : 'decrease' }}
              </span>
              <span class="text-caption text-medium-emphasis ml-2">vs last period</span>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-row class="mt-4">
      <!-- Revenue Chart -->
      <v-col cols="12" md="8">
        <v-card height="100%">
          <v-card-title class="text-subtitle-1 font-weight-bold">Revenue vs Expenses</v-card-title>
          <v-card-text class="pa-0">
            <div class="chart-placeholder d-flex align-center justify-center" style="height: 300px;">
              <v-progress-circular indeterminate color="primary"></v-progress-circular>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Recent Transactions -->
      <v-col cols="12" md="4">
        <v-card height="100%">
          <v-card-title class="text-subtitle-1 font-weight-bold">Recent Transactions</v-card-title>
          <v-card-text class="pa-0">
            <v-table density="comfortable">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Description</th>
                  <th class="text-right">Amount</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(txn, i) in recentTransactions" :key="i">
                  <td>{{ formatDate(txn.date) }}</td>
                  <td>{{ txn.description }}</td>
                  <td class="text-right" :class="{ 'text-success': txn.amount > 0, 'text-error': txn.amount < 0 }">
                    {{ formatCurrency(txn.amount) }}
                  </td>
                </tr>
              </tbody>
            </v-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';

const timeRange = ref('30d');

// Sample data - replace with real API calls
const kpis = ref([
  { title: 'Total Revenue', value: 125000, trend: 12.5 },
  { title: 'Total Expenses', value: 87500, trend: -5.2 },
  { title: 'Net Profit', value: 37500, trend: 8.3 },
  { title: 'Cash Flow', value: 42500, trend: 15.7 }
]);

const recentTransactions = ref([
  { date: '2023-11-15', description: 'Client Payment - Project X', amount: 12500 },
  { date: '2023-11-14', description: 'Office Rent', amount: -2500 },
  { date: '2023-11-13', description: 'Software Subscription', amount: -499 },
  { date: '2023-11-12', description: 'Consulting Services', amount: 3500 },
  { date: '2023-11-11', description: 'Team Lunch', amount: -120 }
]);

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(value);
};

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric'
  });
};

const getTrendColor = (trend: number) => {
  if (trend > 0) return 'green-lighten-4';
  if (trend < 0) return 'red-lighten-4';
  return 'grey-lighten-3';
};

// Watch for time range changes
watch(timeRange, (newRange) => {
  // In a real app, this would trigger an API call to fetch data for the selected range
  console.log('Time range changed to:', newRange);
  // Simulate data loading
  kpis.value = kpis.value.map(kpi => ({
    ...kpi,
    value: Math.floor(kpi.value * (0.9 + Math.random() * 0.2)), // Randomize values slightly
    trend: kpi.trend * (0.8 + Math.random() * 0.4) // Randomize trends slightly
  }));
});
</script>

<style scoped>
.business-intelligence {
  max-width: 1600px;
  margin: 0 auto;
}

.chart-placeholder {
  background-color: rgba(0, 0, 0, 0.02);
  border-radius: 4px;
}
</style>
