<template>
  <div class="p-4">
    <Card>
      <template #header>
        <h2 class="p-4 m-0">Budget vs Actual Report</h2>
      </template>
      
      <template #content>
        <div class="grid mb-4">
          <div class="col-12 md:col-4">
            <div class="field">
              <label class="block text-900 font-medium mb-2">Select Budget</label>
              <Dropdown
                v-model="selectedBudget"
                :options="budgets"
                optionLabel="name"
                optionValue="id"
                placeholder="Select Budget"
                class="w-full"
                @change="loadReport"
              />
            </div>
          </div>
          
          <div class="col-12 md:col-4">
            <div class="field">
              <label class="block text-900 font-medium mb-2">Period</label>
              <Dropdown
                v-model="selectedPeriod"
                :options="periods"
                optionLabel="title"
                optionValue="value"
                placeholder="Select Period"
                class="w-full"
                @change="loadReport"
              />
            </div>
          </div>
          
          <div class="col-12 md:col-4">
            <div class="field">
              <label class="block text-900 font-medium mb-2">&nbsp;</label>
              <Button 
                label="Generate Report" 
                @click="loadReport" 
                :loading="loading" 
                class="w-full"
              />
            </div>
          </div>
        </div>
        
        <div v-if="reportData">
          <!-- Summary Cards -->
          <div class="grid mb-6">
            <div class="col-12 md:col-3">
              <Card class="bg-blue-500 text-white">
                <template #content>
                  <div class="text-center">
                    <div class="text-2xl font-bold">{{ formatCurrency(reportData.budgetAmount) }}</div>
                    <div class="text-sm opacity-90">Budget Amount</div>
                  </div>
                </template>
              </Card>
            </div>
            
            <div class="col-12 md:col-3">
              <Card class="bg-cyan-500 text-white">
                <template #content>
                  <div class="text-center">
                    <div class="text-2xl font-bold">{{ formatCurrency(reportData.actualAmount) }}</div>
                    <div class="text-sm opacity-90">Actual Amount</div>
                  </div>
                </template>
              </Card>
            </div>
            
            <div class="col-12 md:col-3">
              <Card :class="reportData.variance >= 0 ? 'bg-green-500 text-white' : 'bg-red-500 text-white'">
                <template #content>
                  <div class="text-center">
                    <div class="text-2xl font-bold">{{ formatCurrency(reportData.variance) }}</div>
                    <div class="text-sm opacity-90">Variance</div>
                  </div>
                </template>
              </Card>
            </div>
            
            <div class="col-12 md:col-3">
              <Card :class="reportData.variancePercent >= 0 ? 'bg-green-500 text-white' : 'bg-orange-500 text-white'">
                <template #content>
                  <div class="text-center">
                    <div class="text-2xl font-bold">{{ reportData.variancePercent.toFixed(1) }}%</div>
                    <div class="text-sm opacity-90">Variance %</div>
                  </div>
                </template>
              </Card>
            </div>
          </div>
          
          <!-- Line Items Table -->
          <DataTable
            :value="reportData.lineItems"
            :paginator="true"
            :rows="10"
            responsiveLayout="scroll"
          >
            <Column field="category" header="Category"></Column>
            
            <Column field="budgetAmount" header="Budget Amount">
              <template #body="{ data }">
                {{ formatCurrency(data.budgetAmount) }}
              </template>
            </Column>
            
            <Column field="actualAmount" header="Actual Amount">
              <template #body="{ data }">
                {{ formatCurrency(data.actualAmount) }}
              </template>
            </Column>
            
            <Column field="variance" header="Variance">
              <template #body="{ data }">
                <span :class="data.variance >= 0 ? 'text-green-600' : 'text-red-600'">
                  {{ formatCurrency(data.variance) }}
                </span>
              </template>
            </Column>
            
            <Column field="variancePercent" header="Variance %">
              <template #body="{ data }">
                <span :class="getVariancePercentClass(data)">
                  {{ calculateVariancePercent(data).toFixed(1) }}%
                </span>
              </template>
            </Column>
          </DataTable>
        </div>
        
        <div v-else-if="!loading" class="text-center py-8">
          <i class="pi pi-chart-line text-6xl text-500"></i>
          <p class="text-xl mt-4">Select a budget and period to generate report</p>
        </div>
      </template>
    </Card>
  </div>
</template>

<script>
import { useBudgetStore } from '../store/budget'

export default {
  name: 'BudgetReportView',
  
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
      return percent >= 0 ? 'text-green-600' : 'text-red-600'
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