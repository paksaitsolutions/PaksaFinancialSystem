<template>
  <div class="p-4">
    <!-- Overview Cards -->
    <div class="grid">
      <div class="col-12 sm:col-6 md:col-3">
        <BudgetOverviewCard
          title="Total Budgets"
          :value="totalBudgets"
          :percentage="budgetPerformance.variance_percentage"
          icon="pi pi-chart-bar"
          color="#2196F3"
        />
      </div>

      <div class="col-12 sm:col-6 md:col-3">
        <BudgetOverviewCard
          title="Total Amount"
          :value="totalAmount"
          :percentage="budgetPerformance.variance_percentage"
          icon="pi pi-dollar"
          color="#4CAF50"
        />
      </div>

      <div class="col-12 sm:col-6 md:col-3">
        <BudgetOverviewCard
          title="Approved"
          :value="approvedBudgets"
          :percentage="approvedPercentage"
          icon="pi pi-check-circle"
          color="#4CAF50"
        />
      </div>

      <div class="col-12 sm:col-6 md:col-3">
        <BudgetOverviewCard
          title="Pending"
          :value="pendingBudgets"
          :percentage="pendingPercentage"
          icon="pi pi-clock"
          color="#FFC107"
        />
      </div>
    </div>

    <!-- Departmental Analysis -->
    <div class="grid">
      <div class="col-12">
        <BudgetDepartmentAnalysis
          :data="departmentalAnalysis"
        />
      </div>
    </div>

    <!-- Project Analysis -->
    <div class="grid">
      <div class="col-12">
        <BudgetProjectAnalysis
          :data="projectAnalysis"
        />
      </div>
    </div>

    <!-- Trend Analysis -->
    <div class="grid">
      <div class="col-12">
        <BudgetTrendChart
          :data="trendAnalysis"
        />
      </div>
    </div>

    <!-- Allocation Analysis -->
    <div class="grid">
      <div class="col-12">
        <BudgetAllocationAnalysis
          :data="allocationAnalysis"
        />
      </div>
    </div>

    <!-- Variance Analysis -->
    <div class="grid">
      <div class="col-12">
        <BudgetVarianceAnalysis
          :data="varianceAnalysis"
        />
      </div>
    </div>

    <!-- Recent Budgets -->
    <div class="grid">
      <div class="col-12">
        <Card>
          <template #header>
            <h3 class="p-4 m-0">Recent Budgets</h3>
          </template>
          <template #content>
            <DataTable
              :value="recentBudgets"
              :paginator="true"
              :rows="5"
              responsiveLayout="scroll"
            >
              <Column field="name" header="Name"></Column>
              <Column field="type" header="Type"></Column>
              <Column field="status" header="Status">
                <template #body="{ data }">
                  <Tag :value="data.status" :severity="getStatusSeverity(data.status)" />
                </template>
              </Column>
              <Column field="amount" header="Amount">
                <template #body="{ data }">
                  ${{ formatCurrency(data.amount || 0) }}
                </template>
              </Column>
              <Column field="createdAt" header="Created At"></Column>
            </DataTable>
          </template>
        </Card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useBudgetStore } from '../store/budget'
import { 
  BudgetStatus, 
  BudgetType,
  type BudgetAnalysisData,
  type BudgetTrendData,
  type BudgetAllocationAnalysis as BudgetAllocationAnalysisType,
  type BudgetVarianceAnalysis as BudgetVarianceAnalysisType
} from '../../types/budget'

import BudgetOverviewCard from '../components/BudgetOverviewCard.vue'
import BudgetDepartmentAnalysis from '../components/BudgetDepartmentAnalysis.vue'
import BudgetProjectAnalysis from '../components/BudgetProjectAnalysis.vue'
import BudgetTrendChart from '../components/BudgetTrendChart.vue'
import BudgetAllocationAnalysis from '../components/BudgetAllocationAnalysis.vue'
import BudgetVarianceAnalysis from '../components/BudgetVarianceAnalysis.vue'

// Define budget interface
interface Budget {
  id: number
  name: string
  budget_type: BudgetType
  status: BudgetStatus
  total_amount: number
  created_at: string
}

const budgetStore = useBudgetStore()

// Computed values
const totalBudgets = computed(() => budgetStore.budgets.length)
const totalAmount = computed(() => {
  return budgetStore.budgets.reduce((sum: number, budget: any) => sum + (budget.amount || 0), 0)
})

const approvedBudgets = computed(() => {
  return budgetStore.budgets.filter((b: any) => b.status === 'approved').length
})

const pendingBudgets = computed(() => {
  return budgetStore.budgets.filter((b: any) => b.status === 'draft').length
})

const recentBudgets = computed(() => {
  return budgetStore.budgets
    .sort((a: any, b: any) => new Date(b.createdAt || '').getTime() - new Date(a.createdAt || '').getTime())
    .slice(0, 5)
})

// Analytics data - using mock data for now
const budgetPerformance = ref({ variance_percentage: 0 })
const departmentalAnalysis = ref([])
const projectAnalysis = ref([])
const trendAnalysis = ref([])
const allocationAnalysis = ref([])
const varianceAnalysis = ref([])

// Helper functions
const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount)
}

const getStatusSeverity = (status: string) => {
  switch (status) {
    case 'draft':
      return 'info'
    case 'approved':
      return 'success'
    case 'rejected':
      return 'danger'
    case 'archived':
      return 'secondary'
    default:
      return 'info'
  }
}

// Fetch data on mount
onMounted(async () => {
  try {
    await budgetStore.fetchBudgets()
    // Mock analytics data
    budgetPerformance.value = { variance_percentage: 5.2 }
    departmentalAnalysis.value = [
      { department: 'IT', budget_amount: 100000, actual_amount: 95000, variance: -5 },
      { department: 'HR', budget_amount: 80000, actual_amount: 85000, variance: 6.25 }
    ]
    projectAnalysis.value = [
      { project: 'Project A', budget_amount: 50000, actual_amount: 48000, variance: -4, status: 'active' }
    ]
    trendAnalysis.value = [
      { period: '2024-01', budget: 100000, actual: 95000 },
      { period: '2024-02', budget: 110000, actual: 105000 }
    ]
    allocationAnalysis.value = [
      { category: 'Personnel', amount: 60000, percentage: 60 },
      { category: 'Equipment', amount: 40000, percentage: 40 }
    ]
    varianceAnalysis.value = [
      { category: 'Personnel', budget_amount: 60000, actual_amount: 58000, variance_amount: -2000, variance_percentage: -3.33, status: 'on track' }
    ]
  } catch (error) {
    console.error('Error fetching budget data:', error)
  }
})

// Table headers
const recentHeaders = [
  { text: 'Name', value: 'name' },
  { text: 'Type', value: 'type' },
  { text: 'Status', value: 'status' },
  { text: 'Amount', value: 'amount', align: 'right' },
  { text: 'Created At', value: 'createdAt' }
]

// Calculated percentages for overview cards
const approvedPercentage = computed(() => {
  const total = totalBudgets.value
  const approved = approvedBudgets.value
  return total > 0 ? ((approved / total) * 100).toFixed(1) : '0'
})

const pendingPercentage = computed(() => {
  const total = totalBudgets.value
  const pending = pendingBudgets.value
  return total > 0 ? ((pending / total) * 100).toFixed(1) : '0'
})
</script>
