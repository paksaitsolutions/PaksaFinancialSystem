<template>
  <div class="ai-dashboard">
    <v-container fluid class="pa-4">
      <v-row>
        <v-col cols="12">
          <v-card class="elevation-2">
            <v-card-title class="d-flex align-center">
              <v-icon class="mr-2" color="primary">mdi-robot</v-icon>
              <span>AI Insights Dashboard</span>
              <v-spacer></v-spacer>
              <v-btn
                color="primary"
                prepend-icon="mdi-refresh"
                @click="refreshData"
                :loading="loading"
              >
                Refresh
              </v-btn>
            </v-card-title>
            <v-divider></v-divider>
            <v-card-text>
              <v-row>
                <v-col cols="12" md="4" v-for="(card, index) in insightCards" :key="index">
                  <v-card class="h-100">
                    <v-card-title class="text-subtitle-1 font-weight-medium">
                      <v-icon class="mr-2" :color="card.color">{{ card.icon }}</v-icon>
                      {{ card.title }}
                    </v-card-title>
                    <v-card-text>
                      <div class="text-h5 mb-2">{{ card.value }}</div>
                      <div class="text-caption text-medium-emphasis">{{ card.description }}</div>
                      <v-progress-linear
                        v-if="card.progress"
                        class="mt-2"
                        :color="card.color"
                        :model-value="card.progress"
                        height="6"
                        rounded
                      ></v-progress-linear>
                    </v-card-text>
                  </v-card>
                </v-col>
              </v-row>

              <v-row class="mt-4">
                <v-col cols="12" md="8">
                  <v-card class="h-100">
                    <v-card-title>Anomaly Detection</v-card-title>
                    <v-card-text>
                      <div class="text-center py-8">
                        <v-icon size="64" color="grey-lighten-1">mdi-chart-line</v-icon>
                        <div class="mt-2 text-grey">Anomaly detection visualization will be displayed here</div>
                      </div>
                    </v-card-text>
                  </v-card>
                </v-col>
                <v-col cols="12" md="4">
                  <v-card class="h-100">
                    <v-card-title>AI Recommendations</v-card-title>
                    <v-card-text>
                      <v-list lines="two" class="pa-0">
                        <v-list-item
                          v-for="(item, i) in recommendations"
                          :key="i"
                          :title="item.title"
                          :subtitle="item.description"
                          :prepend-icon="item.icon"
                          :color="item.color"
                        >
                          <template v-slot:append>
                            <v-btn
                              variant="text"
                              icon="mdi-arrow-right"
                              :to="item.action"
                            ></v-btn>
                          </template>
                        </v-list-item>
                      </v-list>
                    </v-card-text>
                  </v-card>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';

const loading = ref(false);

const insightCards = ref([
  {
    title: 'Cash Flow Forecast Accuracy',
    value: '92%',
    description: 'Based on last 30 days',
    progress: 92,
    icon: 'mdi-chart-timeline',
    color: 'primary'
  },
  {
    title: 'Anomalies Detected',
    value: '3',
    description: 'Potential issues found',
    progress: 30,
    icon: 'mdi-alert-circle',
    color: 'error'
  },
  {
    title: 'Cost Savings',
    value: '$12,450',
    description: 'Potential monthly savings',
    progress: 65,
    icon: 'mdi-cash-multiple',
    color: 'success'
  }
]);

const recommendations = ref([
  {
    title: 'Optimize Payment Terms',
    description: 'Extend payment terms with 3 vendors to improve cash flow',
    icon: 'mdi-cash-sync',
    color: 'primary',
    action: '/ap/optimization'
  },
  {
    title: 'Review Unusual Expenses',
    description: '3 expense categories show unusual patterns',
    icon: 'mdi-magnify',
    color: 'warning',
    action: '/reports/expense-analysis'
  },
  {
    title: 'Update Forecast Model',
    description: 'New data available to improve accuracy',
    icon: 'mdi-chart-box',
    color: 'info',
    action: '/settings/forecasting'
  }
]);

const refreshData = async () => {
  loading.value = true;
  // Simulate API call
  await new Promise(resolve => setTimeout(resolve, 1000));
  loading.value = false;
};

onMounted(() => {
  // Initial data load
  refreshData();
});
</script>

<style scoped>
.ai-dashboard {
  height: 100%;
}
.h-100 {
  height: 100%;
}
</style>
