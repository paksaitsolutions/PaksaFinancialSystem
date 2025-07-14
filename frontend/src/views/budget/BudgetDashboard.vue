<template>
  <v-container fluid>
    <!-- Overview Cards -->
    <v-row>
      <v-col cols="12" sm="6" md="3">
        <BudgetOverviewCard
          title="Total Budgets"
          :value="totalBudgets"
          :percentage="budgetPerformance.variance_percentage"
          icon="mdi-chart-box"
          color="#2196F3"
        />
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <BudgetOverviewCard
          title="Total Amount"
          :value="totalAmount"
          :percentage="budgetPerformance.variance_percentage"
          icon="mdi-currency-usd"
          color="#4CAF50"
        />
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <BudgetOverviewCard
          title="Approved"
          :value="approvedBudgets"
          :percentage="approvedPercentage"
          icon="mdi-check-circle"
          color="#4CAF50"
        />
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <BudgetOverviewCard
          title="Pending"
          :value="pendingBudgets"
          :percentage="pendingPercentage"
          icon="mdi-clock-alert"
          color="#FFC107"
        />
      </v-col>
    </v-row>

    <!-- Departmental Analysis -->
    <v-row>
      <v-col cols="12">
        <BudgetDepartmentAnalysis
          :data="departmentalAnalysis"
        />
      </v-col>
    </v-row>

    <!-- Project Analysis -->
    <v-row>
      <v-col cols="12">
        <BudgetProjectAnalysis
          :data="projectAnalysis"
        />
      </v-col>
    </v-row>

    <!-- Trend Analysis -->
    <v-row>
      <v-col cols="12">
        <BudgetTrendChart
          :data="trendAnalysis"
        />
      </v-col>
    </v-row>

    <!-- Allocation Analysis -->
    <v-row>
      <v-col cols="12">
        <BudgetAllocationAnalysis
          :data="allocationAnalysis"
        />
      </v-col>
    </v-row>

    <!-- Variance Analysis -->
    <v-row>
      <v-col cols="12">
        <BudgetVarianceAnalysis
          :data="varianceAnalysis"
        />
      </v-col>
    </v-row>

    <!-- Recent Budgets -->
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title>Recent Budgets</v-card-title>
          <v-card-text>
            <v-data-table
              :headers="recentHeaders"
              :items="recentBudgets"
              :items-per-page="5"
              class="elevation-1"
            >
              <template v-slot:item.status="{ item }">
                <v-chip :color="getStatusColor(item.status)" small>
                  {{ item.status }}
                </v-chip>
              </template>
              <template v-slot:item.amount="{ item }">
                ${{ formatCurrency(item.total_amount) }}
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useBudgetStore } from '@/stores/budget'
import { 
  BudgetStatus, 
  BudgetType,
  BudgetAnalysisData,
  BudgetTrendData,
  BudgetAllocationAnalysis,
  BudgetVarianceAnalysis
} from '@/types/budget'

import BudgetOverviewCard from '@/components/budget/BudgetOverviewCard.vue'
import BudgetDepartmentAnalysis from '@/components/budget/BudgetDepartmentAnalysis.vue'
import BudgetProjectAnalysis from '@/components/budget/BudgetProjectAnalysis.vue'
import BudgetTrendChart from '@/components/budget/BudgetTrendChart.vue'
import BudgetAllocationAnalysis from '@/components/budget/BudgetAllocationAnalysis.vue'
import BudgetVarianceAnalysis from '@/components/budget/BudgetVarianceAnalysis.vue'

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
const totalBudgets = computed(() => budgetStore.totalBudgets)
const totalAmount = computed(() => {
  return budgetStore.budgets.reduce((sum: number, budget: Budget) => sum + budget.total_amount, 0)
})

const approvedBudgets = computed(() => {
  return budgetStore.budgets.filter((b: Budget) => b.status === BudgetStatus.APPROVED).length
})

const pendingBudgets = computed(() => {
  return budgetStore.budgets.filter((b: Budget) => b.status === BudgetStatus.DRAFT).length
})

const recentBudgets = computed(() => {
  return budgetStore.budgets
    .sort((a: Budget, b: Budget) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 5)
})

// Analytics data
const budgetPerformance = computed(() => budgetStore.getBudgetPerformance())
const departmentalAnalysis = computed(() => budgetStore.getDepartmentalAnalysis())
const projectAnalysis = computed(() => budgetStore.getProjectAnalysis())
const trendAnalysis = computed(() => budgetStore.getTrendAnalysis())
const allocationAnalysis = computed(() => budgetStore.getAllocationAnalysis())
const varianceAnalysis = computed(() => budgetStore.getVarianceAnalysis())

// Helper functions
const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount)
}

const getStatusColor = (status: BudgetStatus) => {
  switch (status) {
    case BudgetStatus.DRAFT:
      return 'primary'
    case BudgetStatus.APPROVED:
      return 'success'
    case BudgetStatus.REJECTED:
      return 'error'
    case BudgetStatus.ARCHIVED:
      return 'grey'
    default:
      return 'grey'
  }
}

// Fetch data on mount
onMounted(async () => {
  try {
    await Promise.all([
      budgetStore.fetchBudgets(),
      budgetStore.getBudgetPerformance(),
      budgetStore.getDepartmentalAnalysis(),
      budgetStore.getProjectAnalysis(),
      budgetStore.getTrendAnalysis(),
      budgetStore.getAllocationAnalysis(),
      budgetStore.getVarianceAnalysis()
    ])
  } catch (error) {
    console.error('Error fetching budget data:', error)
  }
})

// Table headers
const recentHeaders = [
  { text: 'Name', value: 'name' },
  { text: 'Type', value: 'budget_type' },
  { text: 'Status', value: 'status' },
  { text: 'Amount', value: 'amount', align: 'right' },
  { text: 'Created At', value: 'created_at' }
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
</script>
