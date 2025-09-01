<template>
  <ResponsiveContainer>
    <Card>
      <template #header>
        <h2 class="p-4 m-0">Depreciation Schedule</h2>
      </template>
      
      <template #content>
        <div class="grid mb-4">
          <div class="col-12 md:col-4">
            <Dropdown
              v-model="selectedAsset"
              :options="assets"
              optionLabel="name"
              optionValue="id"
              placeholder="Select Asset"
              @change="loadDepreciationSchedule"
              class="w-full"
            />
          </div>
          
          <div class="col-12 md:col-4">
            <Calendar
              v-model="periodDate"
              placeholder="Period Date"
              dateFormat="yy-mm-dd"
              class="w-full"
            />
          </div>
          
          <div class="col-12 md:col-4">
            <Button 
              label="Calculate Depreciation"
              @click="calculateDepreciation" 
              :loading="calculating"
              class="w-full"
            />
          </div>
        </div>
        
        <div v-if="selectedAssetData">
          <!-- Asset Summary -->
          <div class="grid mb-4">
            <div class="col-12 md:col-3">
              <Card class="text-center">
                <template #content>
                  <div class="text-2xl font-semibold">{{ formatCurrency(selectedAssetData.purchase_cost) }}</div>
                  <div class="text-sm text-500">Purchase Cost</div>
                </template>
              </Card>
            </div>
            
            <div class="col-12 md:col-3">
              <Card class="text-center">
                <template #content>
                  <div class="text-2xl font-semibold">{{ formatCurrency(selectedAssetData.accumulated_depreciation) }}</div>
                  <div class="text-sm text-500">Accumulated Depreciation</div>
                </template>
              </Card>
            </div>
            
            <div class="col-12 md:col-3">
              <Card class="text-center">
                <template #content>
                  <div class="text-2xl font-semibold">{{ formatCurrency(bookValue) }}</div>
                  <div class="text-sm text-500">Book Value</div>
                </template>
              </Card>
            </div>
            
            <div class="col-12 md:col-3">
              <Card class="text-center">
                <template #content>
                  <div class="text-2xl font-semibold">{{ selectedAssetData.useful_life_years }} years</div>
                  <div class="text-sm text-500">Useful Life</div>
                </template>
              </Card>
            </div>
          </div>
          
          <!-- Depreciation Method Info -->
          <Message severity="info" class="mb-4">
            <strong>Depreciation Method:</strong> {{ formatDepreciationMethod(selectedAssetData.depreciation_method) }}
            <br>
            <strong>Monthly Depreciation:</strong> {{ formatCurrency(monthlyDepreciation) }}
          </Message>
        </div>
        
        <!-- Depreciation Entries Table -->
        <DataTable
          :value="depreciationEntries"
          :loading="loading"
          responsiveLayout="scroll"
        >
          <Column field="period_date" header="Period Date">
            <template #body="{ data }">
              {{ formatDate(data.period_date) }}
            </template>
          </Column>
          
          <Column field="depreciation_amount" header="Depreciation Amount">
            <template #body="{ data }">
              {{ formatCurrency(data.depreciation_amount) }}
            </template>
          </Column>
          
          <Column field="accumulated_depreciation" header="Accumulated Depreciation">
            <template #body="{ data }">
              {{ formatCurrency(data.accumulated_depreciation) }}
            </template>
          </Column>
          
          <Column field="book_value" header="Book Value">
            <template #body="{ data }">
              {{ formatCurrency(data.book_value) }}
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>
  </ResponsiveContainer>
</template>

<script>
import ResponsiveContainer from '@/components/layout/ResponsiveContainer.vue'
import { fixedAssetApiService } from '../services/fixedAssetApiService'

export default {
  name: 'DepreciationSchedule',
  components: { ResponsiveContainer },
  
  data() {
    return {
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
    }
  },
  
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
  
  mounted() {
    console.log('DepreciationSchedule mounted')
    this.loadAssets()
  },
  
  methods: {
    loadMockData() {
      this.assets = [
        { id: 1, name: 'Office Computer', purchase_cost: 1500, accumulated_depreciation: 300 },
        { id: 2, name: 'Office Printer', purchase_cost: 500, accumulated_depreciation: 100 },
        { id: 3, name: 'Company Car', purchase_cost: 25000, accumulated_depreciation: 5000 }
      ]
    },
    
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