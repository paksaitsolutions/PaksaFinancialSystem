<template>
  <div class="inventory-forecast">
    <!-- Summary Cards -->
    <div class="grid mb-4">
      <div class="col-12 md:col-3">
        <Card class="h-full bg-blue-500 text-white">
          <template #content>
            <div class="text-center">
              <div class="text-3xl font-bold mb-2">{{ summary.total_items_analyzed }}</div>
              <div class="text-blue-100">Items Analyzed</div>
            </div>
          </template>
        </Card>
      </div>
      
      <div class="col-12 md:col-3">
        <Card class="h-full bg-orange-500 text-white">
          <template #content>
            <div class="text-center">
              <div class="text-3xl font-bold mb-2">{{ summary.items_at_risk }}</div>
              <div class="text-orange-100">At Risk Items</div>
            </div>
          </template>
        </Card>
      </div>
      
      <div class="col-12 md:col-3">
        <Card class="h-full bg-red-500 text-white">
          <template #content>
            <div class="text-center">
              <div class="text-3xl font-bold mb-2">{{ summary.items_requiring_reorder }}</div>
              <div class="text-red-100">Need Reorder</div>
            </div>
          </template>
        </Card>
      </div>
      
      <div class="col-12 md:col-3">
        <Card class="h-full bg-green-500 text-white">
          <template #content>
            <div class="text-center">
              <div class="text-3xl font-bold mb-2">{{ formatCurrency(summary.total_recommended_order_value) }}</div>
              <div class="text-green-100">Order Value</div>
            </div>
          </template>
        </Card>
      </div>
    </div>
    
    <div class="grid">
      <!-- Stockout Risks -->
      <div class="col-12 md:col-6">
        <Card class="h-full">
          <template #title>
            <div class="flex justify-content-between align-items-center">
              <h3 class="m-0">Stockout Risks</h3>
              <Button
                icon="pi pi-refresh"
                size="small"
                @click="refreshRisks"
                :loading="loadingRisks"
              />
            </div>
          </template>
          
          <template #content>
            <div v-if="stockoutRisks.length === 0" class="text-center py-4">
              <i class="pi pi-check-circle text-4xl text-green-400 mb-3"></i>
              <p class="text-500">No items at risk of stockout</p>
            </div>
            <div v-else>
              <div
                v-for="risk in stockoutRisks.slice(0, 10)"
                :key="risk.item_id"
                class="flex justify-content-between align-items-center mb-3 p-3 border-round"
                :class="getRiskCardClass(risk.risk_level)"
              >
                <div>
                  <div class="font-semibold text-900">{{ risk.name }}</div>
                  <div class="text-sm text-600">{{ risk.sku }}</div>
                  <div class="text-sm text-600">{{ risk.days_remaining }} days remaining</div>
                </div>
                <div class="text-right">
                  <Tag
                    :value="risk.risk_level.toUpperCase()"
                    :severity="getRiskSeverity(risk.risk_level)"
                  />
                  <div class="text-sm text-600 mt-1">{{ risk.recommended_action }}</div>
                </div>
              </div>
            </div>
          </template>
        </Card>
      </div>
      
      <!-- Demand Forecast Chart -->
      <div class="col-12 md:col-6">
        <Card class="h-full">
          <template #title>Demand Forecast Trends</template>
          
          <template #content>
            <div v-if="demandForecast.length === 0" class="text-center py-4">
              <i class="pi pi-chart-line text-4xl text-400 mb-3"></i>
              <p class="text-500">No forecast data available</p>
            </div>
            <div v-else>
              <div
                v-for="item in demandForecast.slice(0, 5)"
                :key="item.item_id"
                class="mb-4"
              >
                <div class="flex justify-content-between align-items-center mb-2">
                  <div>
                    <div class="font-semibold text-900">{{ item.name }}</div>
                    <div class="text-sm text-600">Current: {{ formatQuantity(item.current_stock) }}</div>
                  </div>
                  <div class="text-right">
                    <div class="text-sm text-600">Daily Usage: {{ formatQuantity(item.average_daily_usage) }}</div>
                  </div>
                </div>
                
                <div class="forecast-bars">
                  <div class="flex justify-content-between text-sm text-600 mb-1">
                    <span>30 Days</span>
                    <span>60 Days</span>
                    <span>90 Days</span>
                  </div>
                  <div class="flex gap-2">
                    <div class="forecast-bar flex-1 bg-blue-500 border-round" style="height: 8px"></div>
                    <div class="forecast-bar flex-1 bg-orange-500 border-round" style="height: 8px"></div>
                    <div class="forecast-bar flex-1 bg-red-500 border-round" style="height: 8px"></div>
                  </div>
                  <div class="flex justify-content-between text-sm text-600 mt-1">
                    <span>{{ formatQuantity(item.forecasted_demand_30_days) }}</span>
                    <span>{{ formatQuantity(item.forecasted_demand_60_days) }}</span>
                    <span>{{ formatQuantity(item.forecasted_demand_90_days) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </Card>
      </div>
    </div>
    
    <!-- Detailed Forecast Table -->
    <div class="mt-4">
      <Card>
        <template #title>
          <div class="flex justify-content-between align-items-center">
            <h3 class="m-0">Detailed Forecast</h3>
            <div class="flex gap-2">
              <Button
                icon="pi pi-download"
                label="Export"
                severity="secondary"
                @click="exportForecast"
              />
              <Button
                icon="pi pi-refresh"
                label="Refresh"
                @click="refreshForecast"
                :loading="loadingForecast"
              />
            </div>
          </div>
        </template>
        
        <template #content>
          <DataTable
            :value="demandForecast"
            :loading="loadingForecast"
            responsiveLayout="scroll"
            class="p-datatable-sm"
          >
            <Column field="sku" header="SKU" sortable />
            <Column field="name" header="Name" sortable />
            
            <Column field="current_stock" header="Current Stock" sortable>
              <template #body="{ data }">
                {{ formatQuantity(data.current_stock) }}
              </template>
            </Column>
            
            <Column field="average_daily_usage" header="Daily Usage" sortable>
              <template #body="{ data }">
                {{ formatQuantity(data.average_daily_usage) }}
              </template>
            </Column>
            
            <Column field="forecasted_demand_30_days" header="30-Day Demand" sortable>
              <template #body="{ data }">
                {{ formatQuantity(data.forecasted_demand_30_days) }}
              </template>
            </Column>
            
            <Column field="days_until_stockout" header="Days to Stockout" sortable>
              <template #body="{ data }">
                <Tag
                  v-if="data.days_until_stockout !== null"
                  :value="`${data.days_until_stockout} days`"
                  :severity="getStockoutSeverity(data.days_until_stockout)"
                />
                <span v-else class="text-500">N/A</span>
              </template>
            </Column>
            
            <Column field="recommended_order_quantity" header="Recommended Order" sortable>
              <template #body="{ data }">
                {{ formatQuantity(data.recommended_order_quantity) }}
              </template>
            </Column>
          </DataTable>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { formatCurrency } from '@/utils/formatters'
import { apiClient } from '@/utils/apiClient'
import Card from 'primevue/card'
import Button from 'primevue/button'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'

// Composables
const toast = useToast()

// Data
const summary = reactive({
  total_items_analyzed: 180,
  items_at_risk: 23,
  items_requiring_reorder: 8,
  total_recommended_order_value: 45750,
  forecast_accuracy: 87.5
})

const stockoutRisks = ref([
  {
    item_id: 1,
    name: 'Critical Component A',
    sku: 'CCA-001',
    days_remaining: 5,
    risk_level: 'critical',
    recommended_action: 'Order immediately'
  },
  {
    item_id: 2,
    name: 'Widget Standard',
    sku: 'WS-002',
    days_remaining: 12,
    risk_level: 'high',
    recommended_action: 'Order within 3 days'
  },
  {
    item_id: 3,
    name: 'Component B',
    sku: 'CB-003',
    days_remaining: 25,
    risk_level: 'medium',
    recommended_action: 'Monitor closely'
  }
])

const demandForecast = ref([
  {
    item_id: 1,
    sku: 'WDG-001',
    name: 'Widget Pro Max',
    current_stock: 150,
    average_daily_usage: 5.2,
    forecasted_demand_30_days: 156,
    forecasted_demand_60_days: 312,
    forecasted_demand_90_days: 468,
    days_until_stockout: 29,
    recommended_order_quantity: 200
  },
  {
    item_id: 2,
    sku: 'CMP-002',
    name: 'Component X',
    current_stock: 8,
    average_daily_usage: 2.1,
    forecasted_demand_30_days: 63,
    forecasted_demand_60_days: 126,
    forecasted_demand_90_days: 189,
    days_until_stockout: 4,
    recommended_order_quantity: 150
  }
])

const loadingRisks = ref(false)
const loadingForecast = ref(false)

// Methods
const fetchSummary = async () => {
  try {
    // Mock API call
    // const response = await apiClient.get('/api/v1/inventory/forecast/summary')
    // Object.assign(summary, response.data)
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load forecast summary' })
    console.error('Error fetching summary:', error)
  }
}

const fetchStockoutRisks = async () => {
  loadingRisks.value = true
  try {
    // Mock API call
    await new Promise(resolve => setTimeout(resolve, 500))
    // const response = await apiClient.get('/api/v1/inventory/forecast/stockout-risks')
    // stockoutRisks.value = response.data
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load stockout risks' })
    console.error('Error fetching risks:', error)
  } finally {
    loadingRisks.value = false
  }
}

const fetchDemandForecast = async () => {
  loadingForecast.value = true
  try {
    // Mock API call
    await new Promise(resolve => setTimeout(resolve, 500))
    // const response = await apiClient.get('/api/v1/inventory/forecast/demand')
    // demandForecast.value = response.data
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Failed to load demand forecast' })
    console.error('Error fetching forecast:', error)
  } finally {
    loadingForecast.value = false
  }
}

const refreshRisks = () => {
  fetchStockoutRisks()
}

const refreshForecast = () => {
  fetchDemandForecast()
  fetchSummary()
}

const exportForecast = () => {
  toast.add({ severity: 'info', summary: 'Export', detail: 'Export functionality coming soon' })
}

// Helper methods
const formatQuantity = (quantity) => {
  return Number(quantity || 0).toLocaleString()
}

const getRiskSeverity = (riskLevel) => {
  const severities = {
    low: 'success',
    medium: 'warning',
    high: 'danger',
    critical: 'danger'
  }
  return severities[riskLevel] || 'info'
}

const getRiskCardClass = (riskLevel) => {
  const classes = {
    critical: 'bg-red-50 border-left-3 border-red-500',
    high: 'bg-orange-50 border-left-3 border-orange-500',
    medium: 'bg-yellow-50 border-left-3 border-yellow-500',
    low: 'bg-green-50 border-left-3 border-green-500'
  }
  return classes[riskLevel] || ''
}

const getStockoutSeverity = (days) => {
  if (days <= 7) return 'danger'
  if (days <= 14) return 'warning'
  if (days <= 30) return 'info'
  return 'success'
}

// Lifecycle hooks
onMounted(() => {
  fetchSummary()
  fetchStockoutRisks()
  fetchDemandForecast()
})
</script>

<style scoped>
.inventory-forecast {
  padding: 1.5rem;
}

.forecast-bars {
  margin: 0.5rem 0;
}

.forecast-bar {
  border-radius: 4px;
}

.border-left-3 {
  border-left: 3px solid;
}
</style>