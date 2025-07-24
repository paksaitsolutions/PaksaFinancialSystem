<template>
  <ResponsiveContainer>
    <v-card>
      <v-card-title>Depreciation Schedule</v-card-title>
      
      <v-card-text>
        <v-row class="mb-4">
          <v-col cols="12" md="4">
            <v-select
              v-model="selectedAsset"
              :items="assets"
              item-title="name"
              item-value="id"
              label="Select Asset"
              @update:modelValue="loadDepreciationSchedule"
            ></v-select>
          </v-col>
          
          <v-col cols="12" md="4">
            <v-text-field
              v-model="periodDate"
              label="Period Date"
              type="date"
            ></v-text-field>
          </v-col>
          
          <v-col cols="12" md="4">
            <v-btn 
              color="primary" 
              @click="calculateDepreciation" 
              :loading="calculating"
              block
            >
              Calculate Depreciation
            </v-btn>
          </v-col>
        </v-row>
        
        <div v-if="selectedAssetData">
          <!-- Asset Summary -->
          <v-row class="mb-4">
            <v-col cols="12" md="3">
              <v-card variant="outlined">
                <v-card-text class="text-center">
                  <div class="text-h6">{{ formatCurrency(selectedAssetData.purchase_cost) }}</div>
                  <div class="text-caption">Purchase Cost</div>
                </v-card-text>
              </v-card>
            </v-col>
            
            <v-col cols="12" md="3">
              <v-card variant="outlined">
                <v-card-text class="text-center">
                  <div class="text-h6">{{ formatCurrency(selectedAssetData.accumulated_depreciation) }}</div>
                  <div class="text-caption">Accumulated Depreciation</div>
                </v-card-text>
              </v-card>
            </v-col>
            
            <v-col cols="12" md="3">
              <v-card variant="outlined">
                <v-card-text class="text-center">
                  <div class="text-h6">{{ formatCurrency(bookValue) }}</div>
                  <div class="text-caption">Book Value</div>
                </v-card-text>
              </v-card>
            </v-col>
            
            <v-col cols="12" md="3">
              <v-card variant="outlined">
                <v-card-text class="text-center">
                  <div class="text-h6">{{ selectedAssetData.useful_life_years }} years</div>
                  <div class="text-caption">Useful Life</div>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
          
          <!-- Depreciation Method Info -->
          <v-alert type="info" class="mb-4">
            <strong>Depreciation Method:</strong> {{ formatDepreciationMethod(selectedAssetData.depreciation_method) }}
            <br>
            <strong>Monthly Depreciation:</strong> {{ formatCurrency(monthlyDepreciation) }}
          </v-alert>
        </div>
        
        <!-- Depreciation Entries Table -->
        <v-data-table
          :headers="depreciationHeaders"
          :items="depreciationEntries"
          :loading="loading"
          class="elevation-1"
        >
          <template v-slot:item.period_date="{ item }">
            {{ formatDate(item.period_date) }}
          </template>
          
          <template v-slot:item.depreciation_amount="{ item }">
            {{ formatCurrency(item.depreciation_amount) }}
          </template>
          
          <template v-slot:item.accumulated_depreciation="{ item }">
            {{ formatCurrency(item.accumulated_depreciation) }}
          </template>
          
          <template v-slot:item.book_value="{ item }">
            {{ formatCurrency(item.book_value) }}
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>
  </ResponsiveContainer>
</template>

<script>
import ResponsiveContainer from '@/components/layout/ResponsiveContainer.vue'
import { fixedAssetApiService } from '../services/fixedAssetApiService'

export default {
  name: 'DepreciationSchedule',
  components: { ResponsiveContainer },
  
  data: () => ({
    loading: false,
    calculating: false,
    assets: [],
    selectedAsset: null,
    selectedAssetData: null,
    periodDate: new Date().toISOString().substr(0, 10),
    depreciationEntries: [],
    depreciationHeaders: [
      { title: 'Period Date', key: 'period_date' },
      { title: 'Depreciation Amount', key: 'depreciation_amount' },
      { title: 'Accumulated Depreciation', key: 'accumulated_depreciation' },
      { title: 'Book Value', key: 'book_value' }
    ]
  }),
  
  computed: {
    bookValue() {
      if (!this.selectedAssetData) return 0
      return this.selectedAssetData.purchase_cost - this.selectedAssetData.accumulated_depreciation
    },
    
    monthlyDepreciation() {
      if (!this.selectedAssetData) return 0
      const depreciableAmount = this.selectedAssetData.purchase_cost - this.selectedAssetData.salvage_value
      return depreciableAmount / (this.selectedAssetData.useful_life_years * 12)
    }
  },
  
  async mounted() {
    await this.loadAssets()
  },
  
  methods: {
    async loadAssets() {
      try {
        this.loading = true
        this.assets = await fixedAssetApiService.getAssets()
      } catch (error) {
        console.error('Error loading assets:', error)
      } finally {
        this.loading = false
      }
    },
    
    async loadDepreciationSchedule() {
      if (!this.selectedAsset) return
      
      try {
        this.selectedAssetData = await fixedAssetApiService.getAsset(this.selectedAsset)
        // In a real implementation, you would load actual depreciation entries
        this.generateMockDepreciationSchedule()
      } catch (error) {
        console.error('Error loading asset:', error)
      }
    },
    
    generateMockDepreciationSchedule() {
      if (!this.selectedAssetData) return
      
      const entries = []
      const monthlyDepreciation = this.monthlyDepreciation
      let accumulatedDepreciation = 0
      
      for (let i = 0; i < this.selectedAssetData.useful_life_years * 12; i++) {
        const periodDate = new Date(this.selectedAssetData.purchase_date)
        periodDate.setMonth(periodDate.getMonth() + i + 1)
        
        accumulatedDepreciation += monthlyDepreciation
        const bookValue = this.selectedAssetData.purchase_cost - accumulatedDepreciation
        
        entries.push({
          period_date: periodDate.toISOString().substr(0, 10),
          depreciation_amount: monthlyDepreciation,
          accumulated_depreciation: accumulatedDepreciation,
          book_value: Math.max(bookValue, this.selectedAssetData.salvage_value)
        })
        
        if (bookValue <= this.selectedAssetData.salvage_value) break
      }
      
      this.depreciationEntries = entries
    },
    
    async calculateDepreciation() {
      if (!this.selectedAsset || !this.periodDate) return
      
      try {
        this.calculating = true
        await fixedAssetApiService.createDepreciationEntry(this.selectedAsset, this.periodDate)
        await this.loadDepreciationSchedule()
      } catch (error) {
        console.error('Error calculating depreciation:', error)
      } finally {
        this.calculating = false
      }
    },
    
    formatDepreciationMethod(method) {
      const methods = {
        straight_line: 'Straight Line',
        declining_balance: 'Declining Balance',
        units_of_production: 'Units of Production'
      }
      return methods[method] || method
    },
    
    formatCurrency(amount) {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(amount)
    },
    
    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString()
    }
  }
}
</script>