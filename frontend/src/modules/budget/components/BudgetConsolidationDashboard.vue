<template>
  <div class="budget-consolidation-dashboard">
    <Card>
      <template #title>Budget Consolidation</template>
      <template #content>
        <div class="consolidation-controls mb-4">
          <div class="grid">
            <div class="col-12 md:col-4">
              <div class="field">
                <label>Consolidation Period</label>
                <Dropdown 
                  v-model="selectedPeriod"
                  :options="periodOptions"
                  optionLabel="label"
                  optionValue="value"
                  placeholder="Select period"
                  class="w-full"
                />
              </div>
            </div>
            <div class="col-12 md:col-4">
              <div class="field">
                <label>Department Filter</label>
                <MultiSelect 
                  v-model="selectedDepartments"
                  :options="departments"
                  optionLabel="name"
                  optionValue="id"
                  placeholder="All Departments"
                  class="w-full"
                />
              </div>
            </div>
            <div class="col-12 md:col-4">
              <div class="field">
                <label>Actions</label>
                <div class="flex gap-2">
                  <Button 
                    label="Consolidate" 
                    icon="pi pi-sync"
                    @click="consolidateBudgets"
                    :loading="consolidating"
                  />
                  <Button 
                    label="Export" 
                    icon="pi pi-download"
                    class="p-button-outlined"
                    @click="exportConsolidation"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div v-if="consolidationData" class="consolidation-results">
          <div class="summary-section mb-4">
            <div class="grid">
              <div class="col-12 md:col-3">
                <Card class="text-center h-full">
                  <template #content>
                    <div class="text-3xl font-bold text-primary">
                      {{ consolidationData.totalBudgets }}
                    </div>
                    <div class="text-sm text-500">Total Budgets</div>
                  </template>
                </Card>
              </div>
              <div class="col-12 md:col-3">
                <Card class="text-center h-full">
                  <template #content>
                    <div class="text-3xl font-bold text-green-500">
                      {{ formatCurrency(consolidationData.totalAmount) }}
                    </div>
                    <div class="text-sm text-500">Total Amount</div>
                  </template>
                </Card>
              </div>
              <div class="col-12 md:col-3">
                <Card class="text-center h-full">
                  <template #content>
                    <div class="text-3xl font-bold text-orange-500">
                      {{ formatCurrency(consolidationData.totalSpent) }}
                    </div>
                    <div class="text-sm text-500">Total Spent</div>
                  </template>
                </Card>
              </div>
              <div class="col-12 md:col-3">
                <Card class="text-center h-full">
                  <template #content>
                    <div class="text-3xl font-bold" :class="consolidationData.totalRemaining >= 0 ? 'text-green-500' : 'text-red-500'">
                      {{ formatCurrency(consolidationData.totalRemaining) }}
                    </div>
                    <div class="text-sm text-500">Remaining</div>
                  </template>
                </Card>
              </div>
            </div>
          </div>
          
          <div class="department-breakdown">
            <h4>Department Breakdown</h4>
            <DataTable :value="consolidationData.departmentBreakdown" class="p-datatable-sm">
              <Column field="department" header="Department" :sortable="true" />
              <Column field="budgetCount" header="Budgets" :sortable="true" />
              <Column field="totalAmount" header="Total Budget" :sortable="true">
                <template #body="{ data }">
                  {{ formatCurrency(data.totalAmount) }}
                </template>
              </Column>
              <Column field="spent" header="Spent" :sortable="true">
                <template #body="{ data }">
                  {{ formatCurrency(data.spent) }}
                </template>
              </Column>
              <Column field="remaining" header="Remaining" :sortable="true">
                <template #body="{ data }">
                  <span :class="data.remaining >= 0 ? 'text-green-500' : 'text-red-500'" class="font-bold">
                    {{ formatCurrency(data.remaining) }}
                  </span>
                </template>
              </Column>
              <Column field="utilizationRate" header="Utilization %" :sortable="true">
                <template #body="{ data }">
                  <div class="flex align-items-center gap-2">
                    <ProgressBar 
                      :value="data.utilizationRate" 
                      :showValue="false"
                      style="width: 100px; height: 8px"
                    />
                    <span class="text-sm">{{ data.utilizationRate }}%</span>
                  </div>
                </template>
              </Column>
            </DataTable>
          </div>
          
          <div class="category-analysis mt-4">
            <h4>Category Analysis</h4>
            <DataTable :value="consolidationData.categoryAnalysis" class="p-datatable-sm">
              <Column field="category" header="Category" :sortable="true" />
              <Column field="totalBudget" header="Total Budget" :sortable="true">
                <template #body="{ data }">
                  {{ formatCurrency(data.totalBudget) }}
                </template>
              </Column>
              <Column field="totalSpent" header="Total Spent" :sortable="true">
                <template #body="{ data }">
                  {{ formatCurrency(data.totalSpent) }}
                </template>
              </Column>
              <Column field="variance" header="Variance" :sortable="true">
                <template #body="{ data }">
                  <span :class="data.variance >= 0 ? 'text-green-500' : 'text-red-500'" class="font-bold">
                    {{ formatCurrency(data.variance) }}
                  </span>
                </template>
              </Column>
            </DataTable>
          </div>
        </div>
        
        <div v-else class="text-center p-4">
          <i class="pi pi-chart-pie text-4xl text-500 mb-3"></i>
          <p class="text-500">Click "Consolidate" to generate consolidated budget view</p>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface ConsolidationData {
  totalBudgets: number
  totalAmount: number
  totalSpent: number
  totalRemaining: number
  departmentBreakdown: any[]
  categoryAnalysis: any[]
}

const selectedPeriod = ref('current')
const selectedDepartments = ref([])
const consolidating = ref(false)
const consolidationData = ref<ConsolidationData | null>(null)

const periodOptions = [
  { label: 'Current Period', value: 'current' },
  { label: 'Q1 2024', value: 'q1_2024' },
  { label: 'Q2 2024', value: 'q2_2024' },
  { label: 'Q3 2024', value: 'q3_2024' },
  { label: 'Q4 2024', value: 'q4_2024' },
  { label: 'FY 2024', value: 'fy_2024' }
]

const departments = ref([
  { id: 1, name: 'Finance' },
  { id: 2, name: 'Marketing' },
  { id: 3, name: 'Operations' },
  { id: 4, name: 'HR' },
  { id: 5, name: 'IT' }
])

const consolidateBudgets = async () => {
  consolidating.value = true
  try {
    // Mock consolidation process
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // Mock consolidated data
    consolidationData.value = {
      totalBudgets: 15,
      totalAmount: 2500000,
      totalSpent: 1875000,
      totalRemaining: 625000,
      departmentBreakdown: [
        {
          department: 'Finance',
          budgetCount: 3,
          totalAmount: 500000,
          spent: 375000,
          remaining: 125000,
          utilizationRate: 75
        },
        {
          department: 'Marketing',
          budgetCount: 4,
          totalAmount: 750000,
          spent: 600000,
          remaining: 150000,
          utilizationRate: 80
        },
        {
          department: 'Operations',
          budgetCount: 5,
          totalAmount: 800000,
          spent: 640000,
          remaining: 160000,
          utilizationRate: 80
        },
        {
          department: 'HR',
          budgetCount: 2,
          totalAmount: 300000,
          spent: 180000,
          remaining: 120000,
          utilizationRate: 60
        },
        {
          department: 'IT',
          budgetCount: 1,
          totalAmount: 150000,
          spent: 80000,
          remaining: 70000,
          utilizationRate: 53
        }
      ],
      categoryAnalysis: [
        {
          category: 'Personnel',
          totalBudget: 1200000,
          totalSpent: 900000,
          variance: 300000
        },
        {
          category: 'Equipment',
          totalBudget: 500000,
          totalSpent: 450000,
          variance: 50000
        },
        {
          category: 'Marketing',
          totalBudget: 400000,
          totalSpent: 380000,
          variance: 20000
        },
        {
          category: 'Travel',
          totalBudget: 200000,
          totalSpent: 145000,
          variance: 55000
        },
        {
          category: 'Miscellaneous',
          totalBudget: 200000,
          totalSpent: 200000,
          variance: 0
        }
      ]
    }
  } finally {
    consolidating.value = false
  }
}

const exportConsolidation = () => {
  // Mock export functionality
  console.log('Exporting consolidation data...')
}

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(value)
}
</script>

<style scoped>
.field {
  margin-bottom: 1rem;
}

.field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--text-color-secondary);
}
</style>