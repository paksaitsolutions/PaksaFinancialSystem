<template>
  <div class="inventory-forecast">
    <v-row>
      <!-- Summary Cards -->
      <v-col cols="12" md="3">
        <v-card color="primary" dark>
          <v-card-text>
            <div class="text-h4">{{ summary.total_items_analyzed }}</div>
            <div class="text-subtitle-1">Items Analyzed</div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="3">
        <v-card color="warning" dark>
          <v-card-text>
            <div class="text-h4">{{ summary.items_at_risk }}</div>
            <div class="text-subtitle-1">At Risk Items</div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="3">
        <v-card color="error" dark>
          <v-card-text>
            <div class="text-h4">{{ summary.items_requiring_reorder }}</div>
            <div class="text-subtitle-1">Need Reorder</div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="3">
        <v-card color="success" dark>
          <v-card-text>
            <div class="text-h4">{{ formatCurrency(summary.total_recommended_order_value) }}</div>
            <div class="text-subtitle-1">Order Value</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    
    <v-row class="mt-4">
      <!-- Stockout Risks -->
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title class="d-flex align-center justify-space-between">
            <h3>Stockout Risks</h3>
            <v-btn
              color="primary"
              size="small"
              @click="refreshRisks"
              :loading="loadingRisks"
            >
              <v-icon>mdi-refresh</v-icon>
            </v-btn>
          </v-card-title>
          <v-card-text>
            <div v-if="stockoutRisks.length === 0" class="text-center py-4">
              <p class="text-grey">No items at risk of stockout</p>
            </div>
            <div v-else>
              <div
                v-for="risk in stockoutRisks.slice(0, 10)"
                :key="risk.item_id"
                class="d-flex justify-space-between align-center mb-3 pa-2"
                :class="getRiskCardClass(risk.risk_level)"
              >
                <div>
                  <div class="font-weight-medium">{{ risk.name }}</div>
                  <div class="text-caption">{{ risk.sku }}</div>
                  <div class="text-caption">{{ risk.days_remaining }} days remaining</div>
                </div>
                <div class="text-right">
                  <v-chip
                    :color="getRiskColor(risk.risk_level)"
                    size="small"
                    text-color="white"
                  >
                    {{ risk.risk_level.toUpperCase() }}
                  </v-chip>
                  <div class="text-caption mt-1">{{ risk.recommended_action }}</div>
                </div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <!-- Demand Forecast Chart -->
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>Demand Forecast Trends</v-card-title>
          <v-card-text>
            <div v-if="demandForecast.length === 0" class="text-center py-4">
              <p class="text-grey">No forecast data available</p>
            </div>
            <div v-else>
              <div
                v-for="item in demandForecast.slice(0, 5)"
                :key="item.item_id"
                class="mb-4"
              >
                <div class="d-flex justify-space-between align-center mb-2">
                  <div>
                    <div class="font-weight-medium">{{ item.name }}</div>
                    <div class="text-caption">Current: {{ formatQuantity(item.current_stock) }}</div>
                  </div>
                  <div class="text-right">
                    <div class="text-caption">Daily Usage: {{ formatQuantity(item.average_daily_usage) }}</div>
                  </div>
                </div>
                
                <div class="forecast-bars">
                  <div class="d-flex justify-space-between text-caption mb-1">
                    <span>30 Days</span>
                    <span>60 Days</span>
                    <span>90 Days</span>
                  </div>
                  <div class="d-flex gap-2">
                    <div class="forecast-bar flex-1 bg-info" :style="{ height: '8px' }"></div>
                    <div class="forecast-bar flex-1 bg-warning" :style="{ height: '8px' }"></div>
                    <div class="forecast-bar flex-1 bg-error" :style="{ height: '8px' }"></div>
                  </div>
                  <div class="d-flex justify-space-between text-caption mt-1">
                    <span>{{ formatQuantity(item.forecasted_demand_30_days) }}</span>
                    <span>{{ formatQuantity(item.forecasted_demand_60_days) }}</span>
                    <span>{{ formatQuantity(item.forecasted_demand_90_days) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    
    <v-row class="mt-4">
      <!-- Detailed Forecast Table -->
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex align-center justify-space-between">
            <h3>Detailed Forecast</h3>
            <div>
              <v-btn
                color="secondary"
                class="mr-2"
                prepend-icon="mdi-download"
                @click="exportForecast"
              >
                Export
              </v-btn>
              <v-btn
                color="primary"
                prepend-icon="mdi-refresh"
                @click="refreshForecast"
                :loading="loadingForecast"
              >
                Refresh
              </v-btn>
            </div>
          </v-card-title>
          
          <v-data-table
            :headers="forecastHeaders"
            :items="demandForecast"
            :loading="loadingForecast"
            class="elevation-1"
          >
            <template v-slot:item.current_stock="{ item }">
              {{ formatQuantity(item.current_stock) }}
            </template>
            
            <template v-slot:item.average_daily_usage="{ item }">
              {{ formatQuantity(item.average_daily_usage) }}
            </template>
            
            <template v-slot:item.forecasted_demand_30_days="{ item }">
              {{ formatQuantity(item.forecasted_demand_30_days) }}
            </template>
            
            <template v-slot:item.days_until_stockout="{ item }">
              <v-chip
                v-if="item.days_until_stockout !== null"
                :color="getStockoutColor(item.days_until_stockout)"
                size="small"
                text-color="white"
              >
                {{ item.days_until_stockout }} days
              </v-chip>
              <span v-else class="text-grey">N/A</span>
            </template>
            
            <template v-slot:item.recommended_order_quantity="{ item }">
              {{ formatQuantity(item.recommended_order_quantity) }}
            </template>
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { useSnackbar } from '@/composables/useSnackbar';
import { formatCurrency } from '@/utils/formatters';
import { apiClient } from '@/utils/apiClient';

// Composables
const { showSnackbar } = useSnackbar();

// Data
const summary = reactive({
  total_items_analyzed: 0,
  items_at_risk: 0,
  items_requiring_reorder: 0,
  total_recommended_order_value: 0,
  forecast_accuracy: 0,
});

const stockoutRisks = ref([]);
const demandForecast = ref([]);
const loadingRisks = ref(false);
const loadingForecast = ref(false);

// Headers
const forecastHeaders = [
  { title: 'SKU', key: 'sku', sortable: true },
  { title: 'Name', key: 'name', sortable: true },
  { title: 'Current Stock', key: 'current_stock', sortable: true, align: 'end' },
  { title: 'Daily Usage', key: 'average_daily_usage', sortable: true, align: 'end' },
  { title: '30-Day Demand', key: 'forecasted_demand_30_days', sortable: true, align: 'end' },
  { title: 'Days to Stockout', key: 'days_until_stockout', sortable: true, align: 'center' },
  { title: 'Recommended Order', key: 'recommended_order_quantity', sortable: true, align: 'end' },
];

// Methods
const fetchSummary = async () => {
  try {
    const response = await apiClient.get('/api/v1/inventory/forecast/summary');
    Object.assign(summary, response.data);
  } catch (error) {
    showSnackbar('Failed to load forecast summary', 'error');
    console.error('Error fetching summary:', error);
  }
};

const fetchStockoutRisks = async () => {
  loadingRisks.value = true;
  try {
    const response = await apiClient.get('/api/v1/inventory/forecast/stockout-risks');
    stockoutRisks.value = response.data;
  } catch (error) {
    showSnackbar('Failed to load stockout risks', 'error');
    console.error('Error fetching risks:', error);
  } finally {
    loadingRisks.value = false;
  }
};

const fetchDemandForecast = async () => {
  loadingForecast.value = true;
  try {
    const response = await apiClient.get('/api/v1/inventory/forecast/demand');
    demandForecast.value = response.data;
  } catch (error) {
    showSnackbar('Failed to load demand forecast', 'error');
    console.error('Error fetching forecast:', error);
  } finally {
    loadingForecast.value = false;
  }
};

const refreshRisks = () => {
  fetchStockoutRisks();
};

const refreshForecast = () => {
  fetchDemandForecast();
  fetchSummary();
};

const exportForecast = () => {
  // Implement export functionality
  showSnackbar('Export functionality coming soon', 'info');
};

// Helper methods
const formatQuantity = (quantity) => {
  return Number(quantity || 0).toLocaleString();
};

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

const getStockoutColor = (days) => {
  if (days <= 7) return 'error';
  if (days <= 14) return 'warning';
  if (days <= 30) return 'info';
  return 'success';
};

// Lifecycle hooks
onMounted(() => {
  fetchSummary();
  fetchStockoutRisks();
  fetchDemandForecast();
});
</script>

<style scoped>
.inventory-forecast {
  padding: 16px;
}

.forecast-bars {
  margin: 8px 0;
}

.forecast-bar {
  border-radius: 4px;
}
</style>