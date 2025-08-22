<template>
  <div class="analytics-dashboard">
    <v-row>
      <!-- KPI Cards -->
      <v-col cols="12">
        <v-row>
          <v-col
            v-for="kpi in keyMetrics"
            :key="kpi.kpi_id"
            cols="12"
            md="3"
          >
            <v-card class="kpi-card">
              <v-card-text>
                <div class="d-flex align-center justify-space-between">
                  <div>
                    <div class="text-h4 font-weight-bold">{{ kpi.current_value }}</div>
                    <div class="text-subtitle-2 text-grey">{{ kpi.name }}</div>
                    <div v-if="kpi.target_value" class="text-caption">
                      Target: {{ kpi.target_value }}
                    </div>
                  </div>
                  <div class="text-right">
                    <v-icon
                      :color="getTrendColor(kpi.trend)"
                      size="large"
                    >
                      {{ getTrendIcon(kpi.trend) }}
                    </v-icon>
                    <div
                      v-if="kpi.change_percentage"
                      :class="getTrendColor(kpi.trend)"
                      class="text-caption font-weight-bold"
                    >
                      {{ kpi.change_percentage > 0 ? '+' : '' }}{{ kpi.change_percentage }}%
                    </div>
                  </div>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-col>
      
      <!-- Revenue Trend Chart -->
      <v-col cols="12" md="8">
        <v-card>
          <v-card-title>Revenue Trend</v-card-title>
          <v-card-text>
            <canvas ref="revenueChart" height="300"></canvas>
          </v-card-text>
        </v-card>
      </v-col>
      
      <!-- Expense Breakdown -->
      <v-col cols="12" md="4">
        <v-card>
          <v-card-title>Expense Breakdown</v-card-title>
          <v-card-text>
            <canvas ref="expenseChart" height="300"></canvas>
          </v-card-text>
        </v-card>
      </v-col>
      
      <!-- AI Insights -->
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2">mdi-brain</v-icon>
            AI Insights
          </v-card-title>
          <v-card-text>
            <div v-if="loading.insights" class="text-center py-4">
              <v-progress-circular indeterminate></v-progress-circular>
            </div>
            <div v-else>
              <v-expansion-panels v-if="insights.length">
                <v-expansion-panel
                  v-for="(insight, index) in insights"
                  :key="index"
                >
                  <v-expansion-panel-title>
                    <div class="d-flex align-center">
                      <v-chip
                        :color="getImpactColor(insight.impact)"
                        size="small"
                        class="mr-2"
                      >
                        {{ insight.impact.toUpperCase() }}
                      </v-chip>
                      {{ insight.title }}
                    </div>
                  </v-expansion-panel-title>
                  <v-expansion-panel-text>
                    <p>{{ insight.description }}</p>
                    <v-divider class="my-2"></v-divider>
                    <p><strong>Recommendation:</strong> {{ insight.recommendation }}</p>
                    <div class="text-caption text-grey">
                      Confidence: {{ Math.round(insight.confidence * 100) }}%
                    </div>
                  </v-expansion-panel-text>
                </v-expansion-panel>
              </v-expansion-panels>
              <div v-else class="text-center text-grey">
                No insights available
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <!-- Anomalies -->
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title class="d-flex align-center justify-space-between">
            <div class="d-flex align-center">
              <v-icon class="mr-2">mdi-alert-circle</v-icon>
              Anomalies Detected
            </div>
            <v-btn
              size="small"
              color="primary"
              @click="detectAnomalies"
              :loading="loading.anomalies"
            >
              Scan Now
            </v-btn>
          </v-card-title>
          <v-card-text>
            <div v-if="anomalies.length">
              <v-list>
                <v-list-item
                  v-for="anomaly in anomalies"
                  :key="anomaly.id"
                >
                  <template v-slot:prepend>
                    <v-avatar :color="getSeverityColor(anomaly.severity)">
                      <v-icon>mdi-alert</v-icon>
                    </v-avatar>
                  </template>
                  
                  <v-list-item-title>{{ anomaly.metric_name }}</v-list-item-title>
                  <v-list-item-subtitle>
                    {{ anomaly.description }}
                  </v-list-item-subtitle>
                  
                  <template v-slot:append>
                    <v-chip
                      :color="getSeverityColor(anomaly.severity)"
                      size="small"
                    >
                      {{ anomaly.severity.toUpperCase() }}
                    </v-chip>
                  </template>
                </v-list-item>
              </v-list>
            </div>
            <div v-else class="text-center text-grey py-4">
              No anomalies detected
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <!-- Predictions -->
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex align-center justify-space-between">
            <div class="d-flex align-center">
              <v-icon class="mr-2">mdi-crystal-ball</v-icon>
              AI Predictions
            </div>
            <v-btn
              size="small"
              color="primary"
              @click="generatePredictions"
              :loading="loading.predictions"
            >
              Generate
            </v-btn>
          </v-card-title>
          <v-card-text>
            <v-row v-if="predictions.length">
              <v-col
                v-for="prediction in predictions"
                :key="prediction.id"
                cols="12"
                md="6"
              >
                <v-card variant="outlined">
                  <v-card-text>
                    <div class="d-flex align-center justify-space-between mb-2">
                      <h4>{{ prediction.target_metric }}</h4>
                      <v-chip size="small" color="info">
                        {{ prediction.confidence_score }}% confidence
                      </v-chip>
                    </div>
                    <div class="prediction-data">
                      <pre>{{ JSON.stringify(prediction.prediction_data, null, 2) }}</pre>
                    </div>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
            <div v-else class="text-center text-grey py-4">
              No predictions available
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue';
import { useSnackbar } from '@/composables/useSnackbar';
import { apiClient } from '@/utils/apiClient';
import Chart from 'chart.js/auto';

const { showSnackbar } = useSnackbar();

// Data
const keyMetrics = ref([]);
const insights = ref([]);
const anomalies = ref([]);
const predictions = ref([]);
const revenueChart = ref(null);
const expenseChart = ref(null);

const loading = reactive({
  analytics: false,
  insights: false,
  anomalies: false,
  predictions: false
});

// Methods
const fetchAnalyticsData = async () => {
  loading.analytics = true;
  try {
    const response = await apiClient.get('/api/v1/bi-ai/analytics');
    const data = response.data;
    
    keyMetrics.value = data.key_metrics || [];
    anomalies.value = data.anomalies || [];
    predictions.value = data.predictions || [];
    
    // Create charts
    await nextTick();
    createRevenueChart(data.revenue_trend || []);
    createExpenseChart(data.expense_breakdown || []);
    
  } catch (error) {
    showSnackbar('Failed to load analytics data', 'error');
    console.error('Error fetching analytics:', error);
  } finally {
    loading.analytics = false;
  }
};

const fetchInsights = async () => {
  loading.insights = true;
  try {
    const response = await apiClient.get('/api/v1/bi-ai/insights');
    insights.value = response.data;
  } catch (error) {
    showSnackbar('Failed to load insights', 'error');
    console.error('Error fetching insights:', error);
  } finally {
    loading.insights = false;
  }
};

const detectAnomalies = async () => {
  loading.anomalies = true;
  try {
    const response = await apiClient.post('/api/v1/bi-ai/anomalies/detect');
    anomalies.value = response.data;
    showSnackbar(`Detected ${response.data.length} anomalies`, 'info');
  } catch (error) {
    showSnackbar('Failed to detect anomalies', 'error');
    console.error('Error detecting anomalies:', error);
  } finally {
    loading.anomalies = false;
  }
};

const generatePredictions = async () => {
  loading.predictions = true;
  try {
    const response = await apiClient.post('/api/v1/bi-ai/predictions/generate');
    predictions.value = response.data;
    showSnackbar(`Generated ${response.data.length} predictions`, 'success');
  } catch (error) {
    showSnackbar('Failed to generate predictions', 'error');
    console.error('Error generating predictions:', error);
  } finally {
    loading.predictions = false;
  }
};

const createRevenueChart = (data) => {
  if (!revenueChart.value) return;
  
  new Chart(revenueChart.value, {
    type: 'line',
    data: {
      labels: data.map(d => d.month),
      datasets: [{
        label: 'Revenue',
        data: data.map(d => d.revenue),
        borderColor: '#1976d2',
        backgroundColor: 'rgba(25, 118, 210, 0.1)',
        tension: 0.4
      }, {
        label: 'Target',
        data: data.map(d => d.target),
        borderColor: '#ff9800',
        borderDash: [5, 5],
        fill: false
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: false,
          ticks: {
            callback: function(value) {
              return '$' + value.toLocaleString();
            }
          }
        }
      }
    }
  });
};

const createExpenseChart = (data) => {
  if (!expenseChart.value) return;
  
  new Chart(expenseChart.value, {
    type: 'doughnut',
    data: {
      labels: data.map(d => d.category),
      datasets: [{
        data: data.map(d => d.amount),
        backgroundColor: [
          '#1976d2',
          '#388e3c',
          '#f57c00',
          '#d32f2f',
          '#7b1fa2'
        ]
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom'
        }
      }
    }
  });
};

// Utility methods
const getTrendIcon = (trend) => {
  switch (trend) {
    case 'up': return 'mdi-trending-up';
    case 'down': return 'mdi-trending-down';
    default: return 'mdi-trending-neutral';
  }
};

const getTrendColor = (trend) => {
  switch (trend) {
    case 'up': return 'success';
    case 'down': return 'error';
    default: return 'info';
  }
};

const getImpactColor = (impact) => {
  switch (impact) {
    case 'high': return 'error';
    case 'medium': return 'warning';
    default: return 'info';
  }
};

const getSeverityColor = (severity) => {
  switch (severity) {
    case 'critical': return 'error';
    case 'high': return 'warning';
    case 'medium': return 'info';
    default: return 'success';
  }
};

// Lifecycle
onMounted(() => {
  fetchAnalyticsData();
  fetchInsights();
});
</script>

<style scoped>
.analytics-dashboard {
  padding: 16px;
}

.kpi-card {
  height: 120px;
}

.prediction-data {
  background-color: #f5f5f5;
  padding: 8px;
  border-radius: 4px;
  font-size: 12px;
  max-height: 200px;
  overflow-y: auto;
}
</style>