<template>
  <div class="inventory-reports">
    <v-row>
      <!-- Analytics Cards -->
      <v-col cols="12" md="3">
        <v-card color="primary" dark>
          <v-card-text>
            <div class="text-h4">{{ analytics.total_items }}</div>
            <div class="text-subtitle-1">Total Items</div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="3">
        <v-card color="success" dark>
          <v-card-text>
            <div class="text-h4">{{ formatCurrency(analytics.total_value) }}</div>
            <div class="text-subtitle-1">Total Value</div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="3">
        <v-card color="warning" dark>
          <v-card-text>
            <div class="text-h4">{{ analytics.low_stock_items }}</div>
            <div class="text-subtitle-1">Low Stock Items</div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="3">
        <v-card color="error" dark>
          <v-card-text>
            <div class="text-h4">{{ analytics.out_of_stock_items }}</div>
            <div class="text-subtitle-1">Out of Stock</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    
    <v-row class="mt-4">
      <!-- Transaction Summary Chart -->
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>Transaction Summary (Last 30 Days)</v-card-title>
          <v-card-text>
            <div v-if="analytics.transaction_summary.length === 0" class="text-center py-4">
              <p class="text-grey">No transactions in the last 30 days</p>
            </div>
            <div v-else>
              <div
                v-for="summary in analytics.transaction_summary"
                :key="summary.transaction_type"
                class="d-flex justify-space-between align-center mb-2"
              >
                <div>
                  <div class="font-weight-medium">{{ formatTransactionType(summary.transaction_type) }}</div>
                  <div class="text-caption">{{ summary.transaction_count }} transactions</div>
                </div>
                <div class="text-right">
                  <div>{{ formatQuantity(summary.total_quantity) }}</div>
                  <div class="text-caption">{{ formatCurrency(summary.total_value) }}</div>
                </div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <!-- Top Items by Value -->
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>Top Items by Value</v-card-title>
          <v-card-text>
            <div v-if="analytics.top_items_by_value.length === 0" class="text-center py-4">
              <p class="text-grey">No items found</p>
            </div>
            <div v-else>
              <div
                v-for="item in analytics.top_items_by_value.slice(0, 5)"
                :key="item.item_id"
                class="d-flex justify-space-between align-center mb-2"
              >
                <div>
                  <div class="font-weight-medium">{{ item.name }}</div>
                  <div class="text-caption">{{ item.sku }}</div>
                </div>
                <div class="text-right">
                  <div>{{ formatCurrency(item.total_value) }}</div>
                  <div class="text-caption">{{ formatQuantity(item.quantity_on_hand) }} @ {{ formatCurrency(item.unit_cost) }}</div>
                </div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    
    <v-row class="mt-4">
      <!-- Recent Transactions -->
      <v-col cols="12">
        <v-card>
          <v-card-title>Recent Transactions</v-card-title>
          <v-card-text>
            <v-data-table
              :headers="transactionHeaders"
              :items="analytics.recent_transactions"
              :items-per-page="10"
              class="elevation-1"
            >
              <template v-slot:item.transaction_type="{ item }">
                <v-chip
                  :color="getTransactionColor(item.transaction_type)"
                  size="small"
                  text-color="white"
                >
                  {{ formatTransactionType(item.transaction_type) }}
                </v-chip>
              </template>
              
              <template v-slot:item.transaction_date="{ item }">
                {{ formatDate(item.transaction_date) }}
              </template>
              
              <template v-slot:item.quantity="{ item }">
                {{ formatQuantity(item.quantity) }}
              </template>
              
              <template v-slot:item.total_cost="{ item }">
                {{ formatCurrency(item.total_cost) }}
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    
    <v-row class="mt-4">
      <!-- Reports Section -->
      <v-col cols="12">
        <v-card>
          <v-card-title>Inventory Reports</v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="12" md="4">
                <v-btn
                  color="primary"
                  block
                  prepend-icon="mdi-chart-line"
                  @click="showValuationReport"
                >
                  Inventory Valuation
                </v-btn>
              </v-col>
              
              <v-col cols="12" md="4">
                <v-btn
                  color="warning"
                  block
                  prepend-icon="mdi-alert"
                  @click="showStockLevelsReport"
                >
                  Stock Levels
                </v-btn>
              </v-col>
              
              <v-col cols="12" md="4">
                <v-btn
                  color="info"
                  block
                  prepend-icon="mdi-swap-horizontal"
                  @click="showTransactionReport"
                >
                  Transaction Summary
                </v-btn>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { useSnackbar } from '@/composables/useSnackbar';
import { formatCurrency, formatDate } from '@/utils/formatters';
import { apiClient } from '@/utils/apiClient';

// Composables
const { showSnackbar } = useSnackbar();

// Data
const analytics = reactive({
  total_items: 0,
  total_value: 0,
  low_stock_items: 0,
  out_of_stock_items: 0,
  transaction_summary: [],
  top_items_by_value: [],
  recent_transactions: [],
});

// Transaction headers
const transactionHeaders = [
  { title: 'Type', key: 'transaction_type', sortable: false },
  { title: 'Date', key: 'transaction_date', sortable: false },
  { title: 'Item', key: 'item_name', sortable: false },
  { title: 'SKU', key: 'sku', sortable: false },
  { title: 'Quantity', key: 'quantity', sortable: false, align: 'end' },
  { title: 'Cost', key: 'total_cost', sortable: false, align: 'end' },
];

// Methods
const fetchAnalytics = async () => {
  try {
    const response = await apiClient.get('/api/v1/inventory/reports/analytics');
    Object.assign(analytics, response.data);
  } catch (error) {
    showSnackbar('Failed to load inventory analytics', 'error');
    console.error('Error fetching analytics:', error);
  }
};

const formatQuantity = (quantity) => {
  return Number(quantity || 0).toLocaleString();
};

const formatTransactionType = (type) => {
  const types = {
    receipt: 'Receipt',
    issue: 'Issue',
    adjustment: 'Adjustment',
    transfer: 'Transfer',
  };
  return types[type] || type;
};

const getTransactionColor = (type) => {
  const colors = {
    receipt: 'success',
    issue: 'error',
    adjustment: 'warning',
    transfer: 'info',
  };
  return colors[type] || 'grey';
};

const showValuationReport = () => {
  // Navigate to valuation report or show dialog
  console.log('Show valuation report');
};

const showStockLevelsReport = () => {
  // Navigate to stock levels report or show dialog
  console.log('Show stock levels report');
};

const showTransactionReport = () => {
  // Navigate to transaction report or show dialog
  console.log('Show transaction report');
};

// Lifecycle hooks
onMounted(() => {
  fetchAnalytics();
});
</script>

<style scoped>
.inventory-reports {
  padding: 16px;
}
</style>