<template>
  <v-card>
    <v-card-title>
      <v-icon left>mdi-chart-line</v-icon>
      Vendor Performance Dashboard
    </v-card-title>
    
    <v-card-text>
      <v-row>
        <v-col cols="12" md="3" v-for="metric in performanceMetrics" :key="metric.title">
          <v-card outlined>
            <v-card-text class="text-center">
              <div class="text-h4" :class="metric.color">{{ metric.value }}</div>
              <div class="text-subtitle-1">{{ metric.title }}</div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
      
      <v-row class="mt-4">
        <v-col cols="12" md="6">
          <v-card outlined>
            <v-card-title>Top Performing Vendors</v-card-title>
            <v-card-text>
              <v-list>
                <v-list-item v-for="vendor in topVendors" :key="vendor.id">
                  <template v-slot:prepend>
                    <v-avatar color="primary">
                      {{ vendor.name.charAt(0) }}
                    </v-avatar>
                  </template>
                  <v-list-item-title>{{ vendor.name }}</v-list-item-title>
                  <v-list-item-subtitle>Score: {{ vendor.score }}/5.0</v-list-item-subtitle>
                  <template v-slot:append>
                    <v-rating
                      :model-value="vendor.score"
                      readonly
                      size="small"
                      density="compact"
                    />
                  </template>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>
        </v-col>
        
        <v-col cols="12" md="6">
          <v-card outlined>
            <v-card-title>Performance Trends</v-card-title>
            <v-card-text>
              <div class="chart-placeholder">
                <v-icon size="100" color="grey lighten-2">mdi-chart-line</v-icon>
                <p class="text-center mt-2">Performance chart will be displayed here</p>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
      
      <v-row class="mt-4">
        <v-col cols="12">
          <v-card outlined>
            <v-card-title>Vendor Performance Details</v-card-title>
            <v-card-text>
              <v-data-table
                :headers="performanceHeaders"
                :items="vendorPerformance"
                :loading="loading"
                class="elevation-1"
              >
                <template v-slot:item.performance_score="{ item }">
                  <v-rating
                    :model-value="item.performance_score"
                    readonly
                    size="small"
                    density="compact"
                  />
                </template>
                
                <template v-slot:item.on_time_delivery="{ item }">
                  <v-progress-linear
                    :model-value="item.on_time_delivery"
                    color="success"
                    height="20"
                  >
                    {{ item.on_time_delivery }}%
                  </v-progress-linear>
                </template>
                
                <template v-slot:item.actions="{ item }">
                  <v-btn icon small @click="viewDetails(item)">
                    <v-icon>mdi-eye</v-icon>
                  </v-btn>
                  <v-btn icon small @click="evaluate(item)">
                    <v-icon>mdi-star</v-icon>
                  </v-btn>
                </template>
              </v-data-table>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useVendorStore } from '../../store/vendors'

const vendorStore = useVendorStore()
const loading = ref(false)
const vendorPerformance = ref([])

const performanceMetrics = ref([
  { title: 'Average Score', value: '4.2', color: 'text-success' },
  { title: 'On-Time Delivery', value: '95%', color: 'text-info' },
  { title: 'Active Vendors', value: '156', color: 'text-primary' },
  { title: 'Total Orders', value: '2,340', color: 'text-warning' }
])

const topVendors = ref([
  { id: 1, name: 'ABC Supplies Inc', score: 4.8 },
  { id: 2, name: 'XYZ Services LLC', score: 4.6 },
  { id: 3, name: 'Tech Solutions Co', score: 4.5 },
  { id: 4, name: 'Office Depot Pro', score: 4.3 },
  { id: 5, name: 'Global Logistics', score: 4.2 }
])

const performanceHeaders = [
  { title: 'Vendor', key: 'name' },
  { title: 'Performance Score', key: 'performance_score' },
  { title: 'On-Time Delivery', key: 'on_time_delivery' },
  { title: 'Total Orders', key: 'total_orders' },
  { title: 'Total Spent', key: 'total_spent' },
  { title: 'Actions', key: 'actions', sortable: false }
]

const viewDetails = (vendor) => {
  console.log('View details for:', vendor)
}

const evaluate = (vendor) => {
  console.log('Evaluate vendor:', vendor)
}

const loadPerformanceData = async () => {
  loading.value = true
  try {
    // Mock data - replace with actual API call
    vendorPerformance.value = [
      {
        id: 1,
        name: 'ABC Supplies Inc',
        performance_score: 4.8,
        on_time_delivery: 98,
        total_orders: 150,
        total_spent: '$125,000'
      },
      {
        id: 2,
        name: 'XYZ Services LLC',
        performance_score: 4.6,
        on_time_delivery: 95,
        total_orders: 89,
        total_spent: '$75,000'
      },
      {
        id: 3,
        name: 'Tech Solutions Co',
        performance_score: 4.5,
        on_time_delivery: 92,
        total_orders: 67,
        total_spent: '$95,000'
      }
    ]
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadPerformanceData()
})
</script>

<style scoped>
.chart-placeholder {
  height: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
  border-radius: 4px;
}
</style>