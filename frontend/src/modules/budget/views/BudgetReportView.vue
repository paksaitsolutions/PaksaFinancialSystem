<template>
  <ResponsiveContainer>
    <v-card>
      <v-card-title>Budget vs Actual Report</v-card-title>
      
      <v-card-text>
        <v-row class="mb-4">
          <v-col cols="12" md="4">
            <v-select
              v-model="selectedBudget"
              :items="budgets"
              item-title="name"
              item-value="id"
              label="Select Budget"
              @update:modelValue="loadReport"
            ></v-select>
          </v-col>
          
          <v-col cols="12" md="4">
            <v-select
              v-model="selectedPeriod"
              :items="periods"
              label="Period"
              @update:modelValue="loadReport"
            ></v-select>
          </v-col>
          
          <v-col cols="12" md="4">
            <v-btn color="primary" @click="loadReport" :loading="loading" block>
              Generate Report
            </v-btn>
          </v-col>
        </v-row>
        
        <div v-if="reportData">
          <!-- Summary Cards -->
          <v-row class="mb-6">
            <v-col cols="12" md="3">
              <v-card color="primary" dark>
                <v-card-text class="text-center">
                  <div class="text-h6">{{ formatCurrency(reportData.budgetAmount) }}</div>
                  <div class="text-caption">Budget Amount</div>
                </v-card-text>
              </v-card>
            </v-col>
            
            <v-col cols="12" md="3">
              <v-card color="info" dark>
                <v-card-text class="text-center">
                  <div class="text-h6">{{ formatCurrency(reportData.actualAmount) }}</div>
                  <div class="text-caption">Actual Amount</div>
                </v-card-text>
              </v-card>
            </v-col>
            
            <v-col cols="12" md="3">
              <v-card :color="reportData.variance >= 0 ? 'success' : 'error'" dark>
                <v-card-text class="text-center">
                  <div class="text-h6">{{ formatCurrency(reportData.variance) }}</div>
                  <div class="text-caption">Variance</div>
                </v-card-text>
              </v-card>
            </v-col>
            
            <v-col cols="12" md="3">
              <v-card :color="reportData.variancePercent >= 0 ? 'success' : 'warning'" dark>
                <v-card-text class="text-center">
                  <div class="text-h6">{{ reportData.variancePercent.toFixed(1) }}%</div>
                  <div class="text-caption">Variance %</div>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
          
          <!-- Line Items Table -->
          <v-data-table
            :headers="lineItemHeaders"
            :items="reportData.lineItems"
            class="elevation-1"
          >
            <template v-slot:item.budgetAmount="{ item }">
              {{ formatCurrency(item.budgetAmount) }}
            </template>
            
            <template v-slot:item.actualAmount="{ item }">
              {{ formatCurrency(item.actualAmount) }}
            </template>
            
            <template v-slot:item.variance="{ item }">
              <span :class="item.variance >= 0 ? 'text-success' : 'text-error'">
                {{ formatCurrency(item.variance) }}
              </span>
            </template>
            
            <template v-slot:item.variancePercent="{ item }">
              <span :class="getVariancePercentClass(item)">
                {{ calculateVariancePercent(item).toFixed(1) }}%
              </span>
            </template>
          </v-data-table>
        </div>
        
        <div v-else-if="!loading" class="text-center py-8">
          <v-icon size="64" color="grey">mdi-chart-line</v-icon>
          <p class="text-h6 mt-4">Select a budget and period to generate report</p>
        </div>
      </v-card-text>
    </v-card>
  </ResponsiveContainer>
</template>

<script>
import ResponsiveContainer from '@/components/layout/ResponsiveContainer.vue'
import { useBudgetStore } from '../store/budget'

export default {
  name: 'BudgetReportView',
  components: { ResponsiveContainer },
  
  data: () => ({
    loading: false,
    selectedBudget: null,
    selectedPeriod: 'current_month',
    reportData: null,
    periods: [
      { title: 'Current Month', value: 'current_month' },
      { title: 'Current Quarter', value: 'current_quarter' },
      { title: 'Current Year', value: 'current_year' },
      { title: 'Last Month', value: 'last_month' },
      { title: 'Last Quarter', value: 'last_quarter' },
      { title: 'Last Year', value: 'last_year' }
    ],
    lineItemHeaders: [
      { title: 'Category', key: 'category' },
      { title: 'Budget Amount', key: 'budgetAmount' },
      { title: 'Actual Amount', key: 'actualAmount' },
      { title: 'Variance', key: 'variance' },
      { title: 'Variance %', key: 'variancePercent' }
    ]
  }),
  
  computed: {
    budgets() {
      return this.budgetStore.budgets.filter(budget => budget.status === 'APPROVED')
    }
  },
  
  async mounted() {
    this.budgetStore = useBudgetStore()
    await this.budgetStore.fetchBudgets()
  },
  
  methods: {
    async loadReport() {
      if (!this.selectedBudget || !this.selectedPeriod) return
      
      try {
        this.loading = true
        this.reportData = await this.budgetStore.getBudgetVsActual(
          this.selectedBudget, 
          this.selectedPeriod
        )
      } catch (error) {
        console.error('Error loading report:', error)
      } finally {
        this.loading = false
      }
    },
    
    calculateVariancePercent(item) {
      return item.budgetAmount > 0 ? (item.variance / item.budgetAmount) * 100 : 0
    },
    
    getVariancePercentClass(item) {
      const percent = this.calculateVariancePercent(item)
      return percent >= 0 ? 'text-success' : 'text-error'
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