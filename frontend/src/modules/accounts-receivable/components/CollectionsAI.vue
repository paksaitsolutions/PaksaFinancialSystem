<template>
  <div class="collections-ai">
    <v-row>
      <!-- Summary Cards -->
      <v-col cols="12" md="3">
        <v-card color="primary" dark>
          <v-card-text>
            <div class="text-h4">{{ formatCurrency(insights.total_outstanding) }}</div>
            <div class="text-subtitle-1">Total Outstanding</div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="3">
        <v-card color="warning" dark>
          <v-card-text>
            <div class="text-h4">{{ insights.high_risk_customers }}</div>
            <div class="text-subtitle-1">High Risk Customers</div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="3">
        <v-card color="success" dark>
          <v-card-text>
            <div class="text-h4">{{ formatCurrency(insights.predicted_collections_30_days) }}</div>
            <div class="text-subtitle-1">Predicted 30-Day Collections</div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="3">
        <v-card color="info" dark>
          <v-card-text>
            <div class="text-h4">{{ insights.collection_efficiency_score.toFixed(1) }}%</div>
            <div class="text-subtitle-1">Efficiency Score</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    
    <v-row class="mt-4">
      <!-- Risk Profiles -->
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title class="d-flex align-center justify-space-between">
            <h3>Customer Risk Profiles</h3>
            <v-btn color="primary" size="small" @click="refreshRiskProfiles" :loading="loadingRisk">
              <v-icon>mdi-refresh</v-icon>
            </v-btn>
          </v-card-title>
          <v-card-text>
            <div v-if="riskProfiles.length === 0" class="text-center py-4">
              <p class="text-grey">No risk data available</p>
            </div>
            <div v-else>
              <div
                v-for="profile in riskProfiles.slice(0, 5)"
                :key="profile.customer_id"
                class="d-flex justify-space-between align-center mb-3 pa-3"
                :class="getRiskCardClass(profile.risk_level)"
              >
                <div>
                  <div class="font-weight-medium">{{ profile.customer_name }}</div>
                  <div class="text-caption">{{ profile.payment_behavior }}</div>
                  <div class="text-caption">DSO: {{ profile.days_sales_outstanding }} days</div>
                </div>
                <div class="text-right">
                  <v-chip
                    :color="getRiskColor(profile.risk_level)"
                    size="small"
                    text-color="white"
                  >
                    {{ profile.risk_level.toUpperCase() }}
                  </v-chip>
                  <div class="text-caption mt-1">{{ formatCurrency(profile.total_outstanding) }}</div>
                  <div class="text-caption">{{ profile.recommended_action }}</div>
                </div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <!-- Collection Predictions -->
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>Collection Predictions</v-card-title>
          <v-card-text>
            <div v-if="predictions.length === 0" class="text-center py-4">
              <p class="text-grey">No predictions available</p>
            </div>
            <div v-else>
              <div
                v-for="prediction in predictions.slice(0, 5)"
                :key="prediction.invoice_id"
                class="d-flex justify-space-between align-center mb-3 pa-2 border rounded"
              >
                <div>
                  <div class="font-weight-medium">{{ prediction.invoice_number }}</div>
                  <div class="text-caption">{{ prediction.days_overdue }} days overdue</div>
                  <div class="text-caption">{{ prediction.recommended_strategy }}</div>
                </div>
                <div class="text-right">
                  <div class="text-h6" :class="getProbabilityColor(prediction.collection_probability)">
                    {{ (prediction.collection_probability * 100).toFixed(0) }}%
                  </div>
                  <div class="text-caption">{{ formatCurrency(prediction.amount) }}</div>
                  <div class="text-caption" v-if="prediction.predicted_collection_date">
                    {{ formatDate(prediction.predicted_collection_date) }}
                  </div>
                </div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    
    <v-row class="mt-4">
      <!-- Urgent Actions -->
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>Urgent Actions Required</v-card-title>
          <v-card-text>
            <div v-if="insights.urgent_actions.length === 0" class="text-center py-4">
              <p class="text-grey">No urgent actions required</p>
            </div>
            <div v-else>
              <v-alert
                v-for="(action, index) in insights.urgent_actions"
                :key="index"
                :type="getActionType(action.priority)"
                class="mb-2"
              >
                <div class="font-weight-medium">{{ action.action }}</div>
                <div class="text-caption">
                  {{ action.customer_name || action.invoice_number }} - {{ formatCurrency(action.amount) }}
                </div>
              </v-alert>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <!-- AI Insights -->
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>AI Insights & Trends</v-card-title>
          <v-card-text>
            <div class="mb-3">
              <div class="d-flex justify-space-between align-center">
                <span>Collection Rate Trend:</span>
                <v-chip color="success" size="small">{{ insights.trends.collection_rate_trend }}</v-chip>
              </div>
            </div>
            
            <div class="mb-3">
              <div class="d-flex justify-space-between align-center">
                <span>DSO Trend:</span>
                <v-chip color="info" size="small">{{ insights.trends.dso_trend }}</v-chip>
              </div>
            </div>
            
            <div class="mb-3">
              <div class="d-flex justify-space-between align-center">
                <span>Risk Score Trend:</span>
                <v-chip color="warning" size="small">{{ insights.trends.risk_score_trend }}</v-chip>
              </div>
            </div>
            
            <v-divider class="my-3"></v-divider>
            
            <div class="text-body-2">
              <strong>AI Recommendations:</strong>
              <ul class="mt-2">
                <li>Focus on {{ insights.high_risk_customers }} high-risk customers</li>
                <li>Implement automated reminders for overdue accounts</li>
                <li>Consider payment plans for large outstanding amounts</li>
              </ul>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { useSnackbar } from '@/composables/useSnackbar';
import { apiClient } from '@/utils/apiClient';

// Composables
const { showSnackbar } = useSnackbar();

// Data
const insights = reactive({
  total_outstanding: 0,
  high_risk_customers: 0,
  predicted_collections_30_days: 0,
  collection_efficiency_score: 0,
  top_risks: [],
  urgent_actions: [],
  trends: {}
});

const riskProfiles = ref([]);
const predictions = ref([]);
const loadingRisk = ref(false);

// Methods
const fetchInsights = async () => {
  try {
    const response = await apiClient.get('/api/v1/accounts-receivable/collections-ai/insights');
    Object.assign(insights, response.data);
  } catch (error) {
    showSnackbar('Failed to load collections insights', 'error');
    console.error('Error fetching insights:', error);
  }
};

const fetchRiskProfiles = async () => {
  loadingRisk.value = true;
  try {
    const response = await apiClient.get('/api/v1/accounts-receivable/collections-ai/risk-profiles');
    riskProfiles.value = response.data;
  } catch (error) {
    showSnackbar('Failed to load risk profiles', 'error');
    console.error('Error fetching risk profiles:', error);
  } finally {
    loadingRisk.value = false;
  }
};

const fetchPredictions = async () => {
  try {
    const response = await apiClient.get('/api/v1/accounts-receivable/collections-ai/predictions');
    predictions.value = response.data;
  } catch (error) {
    showSnackbar('Failed to load predictions', 'error');
    console.error('Error fetching predictions:', error);
  }
};

const refreshRiskProfiles = () => {
  fetchRiskProfiles();
};

// Helper methods
const getRiskColor = (riskLevel) => {
  const colors = {
    low: 'success',
    medium: 'warning',
    high: 'orange',
    critical: 'error',
  };
  return colors[riskLevel] || 'grey';
};

const getRiskCardClass = (riskLevel) => {
  const classes = {
    critical: 'bg-red-lighten-5 border-l-4 border-red',
    high: 'bg-orange-lighten-5 border-l-4 border-orange',
    medium: 'bg-yellow-lighten-5 border-l-4 border-yellow',
  };
  return classes[riskLevel] || '';
};

const getProbabilityColor = (probability) => {
  if (probability >= 0.7) return 'text-success';
  if (probability >= 0.4) return 'text-warning';
  return 'text-error';
};

const getActionType = (priority) => {
  if (priority === 1) return 'error';
  if (priority === 2) return 'warning';
  return 'info';
};

// Lifecycle hooks
onMounted(() => {
  fetchInsights();
  fetchRiskProfiles();
  fetchPredictions();
});
</script>

<style scoped>
.collections-ai {
  padding: 16px;
}
</style>