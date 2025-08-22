<template>
  <ResponsiveContainer>
    <v-row>
      <!-- Anomaly Detection -->
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2" color="warning">mdi-alert-circle</v-icon>
            Anomaly Detection
          </v-card-title>
          <v-card-text>
            <v-list v-if="anomalies.length">
              <v-list-item v-for="anomaly in anomalies" :key="anomaly.id">
                <v-list-item-content>
                  <v-list-item-title>{{ anomaly.description }}</v-list-item-title>
                  <v-list-item-subtitle>{{ anomaly.anomaly_reason }}</v-list-item-subtitle>
                </v-list-item-content>
                <v-list-item-action>
                  <v-chip color="warning" small>{{ formatCurrency(anomaly.amount) }}</v-chip>
                </v-list-item-action>
              </v-list-item>
            </v-list>
            <div v-else class="text-center py-4">
              <v-icon size="48" color="success">mdi-check-circle</v-icon>
              <p class="mt-2">No anomalies detected</p>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Recommendations -->
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2" color="info">mdi-lightbulb</v-icon>
            AI Recommendations
          </v-card-title>
          <v-card-text>
            <v-list>
              <v-list-item v-for="rec in recommendations" :key="rec.title">
                <v-list-item-content>
                  <v-list-item-title>{{ rec.title }}</v-list-item-title>
                  <v-list-item-subtitle>{{ rec.description }}</v-list-item-subtitle>
                </v-list-item-content>
                <v-list-item-action>
                  <v-chip :color="getPriorityColor(rec.priority)" small>
                    {{ rec.priority }}
                  </v-chip>
                </v-list-item-action>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Predictive Analytics -->
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2" color="primary">mdi-chart-line</v-icon>
            Predictive Analytics
          </v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="12" md="4">
                <v-card variant="outlined">
                  <v-card-text class="text-center">
                    <div class="text-h6">{{ formatCurrency(cashFlowPrediction.prediction) }}</div>
                    <div class="text-caption">30-Day Cash Flow Forecast</div>
                    <v-progress-linear 
                      :value="cashFlowPrediction.confidence * 100" 
                      color="primary" 
                      class="mt-2"
                    ></v-progress-linear>
                    <div class="text-caption">{{ Math.round(cashFlowPrediction.confidence * 100) }}% Confidence</div>
                  </v-card-text>
                </v-card>
              </v-col>
              
              <v-col cols="12" md="8">
                <div class="text-subtitle-1 mb-2">Revenue Forecast (Next 3 Months)</div>
                <v-simple-table>
                  <thead>
                    <tr>
                      <th>Month</th>
                      <th>Forecasted Revenue</th>
                      <th>Confidence</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="forecast in revenueForecast" :key="forecast.month">
                      <td>{{ forecast.month }}</td>
                      <td>{{ formatCurrency(forecast.forecasted_revenue) }}</td>
                      <td>
                        <v-progress-linear 
                          :value="forecast.confidence * 100" 
                          color="success" 
                          height="20"
                        >
                          {{ Math.round(forecast.confidence * 100) }}%
                        </v-progress-linear>
                      </td>
                    </tr>
                  </tbody>
                </v-simple-table>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Natural Language Query -->
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2" color="success">mdi-message-question</v-icon>
            Ask AI Assistant
          </v-card-title>
          <v-card-text>
            <v-text-field
              v-model="nlQuery"
              label="Ask a question about your finances..."
              placeholder="e.g., Show me revenue for last month"
              @keyup.enter="processNLQuery"
              append-icon="mdi-send"
              @click:append="processNLQuery"
            ></v-text-field>
            
            <v-card v-if="nlResponse" variant="outlined" class="mt-4">
              <v-card-text>
                <div class="text-subtitle-2 mb-2">{{ nlResponse.response }}</div>
                <div v-if="nlResponse.intent" class="text-caption">
                  Intent: {{ nlResponse.intent }} | Entities: {{ nlResponse.entities.join(', ') }}
                </div>
              </v-card-text>
            </v-card>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </ResponsiveContainer>
</template>

<script>
import ResponsiveContainer from '@/components/layout/ResponsiveContainer.vue'

export default {
  name: 'AIInsights',
  components: { ResponsiveContainer },
  
  data: () => ({
    nlQuery: '',
    nlResponse: null,
    anomalies: [
      {
        id: 1,
        description: 'Unusual large payment',
        amount: 15000,
        anomaly_reason: 'Unusually high amount'
      }
    ],
    recommendations: [
      {
        title: 'Improve Cash Flow',
        description: 'Consider accelerating receivables collection',
        priority: 'high'
      },
      {
        title: 'Reduce Operating Expenses',
        description: 'Expenses are high relative to revenue',
        priority: 'medium'
      }
    ],
    cashFlowPrediction: {
      prediction: 25000,
      confidence: 0.85,
      trend: 'increasing'
    },
    revenueForecast: [
      { month: '2024-02', forecasted_revenue: 45000, confidence: 0.9 },
      { month: '2024-03', forecasted_revenue: 47000, confidence: 0.8 },
      { month: '2024-04', forecasted_revenue: 49000, confidence: 0.7 }
    ]
  }),

  methods: {
    processNLQuery() {
      if (!this.nlQuery.trim()) return
      
      // Mock NLP processing
      this.nlResponse = {
        query: this.nlQuery,
        intent: 'show_revenue',
        entities: ['revenue', 'time_period'],
        response: 'Here\'s the revenue information for the requested period:'
      }
      
      this.nlQuery = ''
    },

    getPriorityColor(priority) {
      const colors = {
        high: 'error',
        medium: 'warning',
        low: 'info'
      }
      return colors[priority] || 'grey'
    },

    formatCurrency(amount) {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(amount)
    }
  }
}
</script>