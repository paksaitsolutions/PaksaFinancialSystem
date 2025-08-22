<template>
  <ResponsiveContainer>
    <v-card>
      <v-card-title>Asset Reports</v-card-title>
      
      <v-card-text>
        <v-row v-if="reportData">
          <!-- Summary Cards -->
          <v-col cols="12" md="3">
            <v-card color="primary" dark>
              <v-card-text class="text-center">
                <div class="text-h4">{{ reportData.total_assets }}</div>
                <div class="text-caption">Total Assets</div>
              </v-card-text>
            </v-card>
          </v-col>
          
          <v-col cols="12" md="3">
            <v-card color="success" dark>
              <v-card-text class="text-center">
                <div class="text-h4">{{ formatCurrency(reportData.total_cost) }}</div>
                <div class="text-caption">Total Cost</div>
              </v-card-text>
            </v-card>
          </v-col>
          
          <v-col cols="12" md="3">
            <v-card color="warning" dark>
              <v-card-text class="text-center">
                <div class="text-h4">{{ formatCurrency(reportData.total_accumulated_depreciation) }}</div>
                <div class="text-caption">Total Depreciation</div>
              </v-card-text>
            </v-card>
          </v-col>
          
          <v-col cols="12" md="3">
            <v-card color="info" dark>
              <v-card-text class="text-center">
                <div class="text-h4">{{ formatCurrency(reportData.total_book_value) }}</div>
                <div class="text-caption">Total Book Value</div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
        
        <v-row class="mt-6">
          <!-- Assets by Category -->
          <v-col cols="12" md="6">
            <v-card>
              <v-card-title>Assets by Category</v-card-title>
              <v-card-text>
                <v-simple-table>
                  <thead>
                    <tr>
                      <th>Category</th>
                      <th>Count</th>
                      <th>Total Cost</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="category in reportData.assets_by_category" :key="category.category">
                      <td>{{ category.category }}</td>
                      <td>{{ category.count }}</td>
                      <td>{{ formatCurrency(category.total_cost) }}</td>
                    </tr>
                  </tbody>
                </v-simple-table>
              </v-card-text>
            </v-card>
          </v-col>
          
          <!-- Assets by Status -->
          <v-col cols="12" md="6">
            <v-card>
              <v-card-title>Assets by Status</v-card-title>
              <v-card-text>
                <v-simple-table>
                  <thead>
                    <tr>
                      <th>Status</th>
                      <th>Count</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="status in reportData.assets_by_status" :key="status.status">
                      <td>
                        <v-chip :color="getStatusColor(status.status)" small>
                          {{ status.status.replace('_', ' ').toUpperCase() }}
                        </v-chip>
                      </td>
                      <td>{{ status.count }}</td>
                    </tr>
                  </tbody>
                </v-simple-table>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
        
        <v-row class="mt-4">
          <v-col cols="12">
            <v-btn color="primary" @click="loadReport" :loading="loading">
              <v-icon left>mdi-refresh</v-icon>
              Refresh Report
            </v-btn>
            <v-btn color="secondary" @click="exportReport" class="ml-2">
              <v-icon left>mdi-download</v-icon>
              Export Report
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </ResponsiveContainer>
</template>

<script>
import ResponsiveContainer from '@/components/layout/ResponsiveContainer.vue'
import { fixedAssetApiService } from '../services/fixedAssetApiService'

export default {
  name: 'AssetReports',
  components: { ResponsiveContainer },
  
  data: () => ({
    loading: false,
    reportData: null
  }),
  
  async mounted() {
    await this.loadReport()
  },
  
  methods: {
    async loadReport() {
      try {
        this.loading = true
        this.reportData = await fixedAssetApiService.getAssetReport()
      } catch (error) {
        console.error('Error loading report:', error)
        // Mock data for demonstration
        this.reportData = {
          total_assets: 25,
          total_cost: 125000,
          total_accumulated_depreciation: 35000,
          total_book_value: 90000,
          assets_by_category: [
            { category: 'IT Equipment', count: 10, total_cost: 50000 },
            { category: 'Office Furniture', count: 8, total_cost: 25000 },
            { category: 'Vehicles', count: 4, total_cost: 40000 },
            { category: 'Machinery', count: 3, total_cost: 10000 }
          ],
          assets_by_status: [
            { status: 'active', count: 22 },
            { status: 'under_maintenance', count: 2 },
            { status: 'disposed', count: 1 }
          ]
        }
      } finally {
        this.loading = false
      }
    },
    
    exportReport() {
      console.log('Exporting asset report...')
      // Implement export functionality
    },
    
    getStatusColor(status) {
      const colors = {
        active: 'success',
        disposed: 'error',
        under_maintenance: 'warning',
        retired: 'secondary'
      }
      return colors[status] || 'grey'
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