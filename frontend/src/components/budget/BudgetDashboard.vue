<template>
  <div class="budget-dashboard">
    <!-- Budget Overview Cards -->
    <div class="dashboard-cards">
      <BudgetOverviewCard 
        v-for="card in overviewCards" 
        :key="card.id"
        :title="card.title"
        :value="card.value"
        :percentage="card.percentage"
        :icon="card.icon"
        :color="card.color"
      />
    </div>

    <!-- Departmental Analysis -->
    <div class="department-analysis">
      <h3>Departmental Budget Analysis</h3>
      <BudgetDepartmentAnalysis 
        :data="departmentData"
        :loading="loading"
      />
    </div>

    <!-- Project Analysis -->
    <div class="project-analysis">
      <h3>Project Budget Analysis</h3>
      <BudgetProjectAnalysis 
        :data="projectData"
        :loading="loading"
      />
    </div>

    <!-- Budget Trend Analysis -->
    <div class="trend-analysis">
      <h3>Budget Trend Analysis</h3>
      <BudgetTrendChart 
        :data="trendData"
        :loading="loading"
      />
    </div>

    <!-- Allocation Analysis -->
    <div class="allocation-analysis">
      <h3>Budget Allocation Analysis</h3>
      <BudgetAllocationAnalysis 
        :data="allocationData"
        :loading="loading"
      />
    </div>

    <!-- Variance Analysis -->
    <div class="variance-analysis">
      <h3>Budget Variance Analysis</h3>
      <BudgetVarianceAnalysis 
        :data="varianceData"
        :loading="loading"
      />
    </div>

    <!-- Export Options -->
    <div class="export-options">
      <ExportButton 
        :formats="['pdf', 'excel', 'csv']"
        :data="exportData"
        @export="handleExport"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useBudgetStore } from '@/stores/budget'
import BudgetOverviewCard from './BudgetOverviewCard.vue'
import BudgetDepartmentAnalysis from './BudgetDepartmentAnalysis.vue'
import BudgetProjectAnalysis from './BudgetProjectAnalysis.vue'
import BudgetTrendChart from './BudgetTrendChart.vue'
import BudgetAllocationAnalysis from './BudgetAllocationAnalysis.vue'
import BudgetVarianceAnalysis from './BudgetVarianceAnalysis.vue'
import ExportButton from '@/components/common/ExportButton.vue'
import type { BudgetAnalysisData } from '@/types/budget'

const budgetStore = useBudgetStore()
const loading = ref(true)

// Overview cards data
const overviewCards = ref([
  {
    id: 1,
    title: 'Total Budgeted',
    value: 0,
    percentage: 0,
    icon: 'mdi-chart-box',
    color: '#4CAF50'
  },
  {
    id: 2,
    title: 'Total Spent',
    value: 0,
    percentage: 0,
    icon: 'mdi-currency-usd',
    color: '#2196F3'
  },
  {
    id: 3,
    title: 'Variance',
    value: 0,
    percentage: 0,
    icon: 'mdi-trending-up',
    color: '#FF9800'
  }
])

// Analysis data
const departmentData = ref<BudgetAnalysisData[]>([])
const projectData = ref<BudgetAnalysisData[]>([])
const trendData = ref<BudgetAnalysisData[]>([])
const allocationData = ref<BudgetAnalysisData[]>([])
const varianceData = ref<BudgetAnalysisData>({})
const exportData = ref({})

const fetchData = async () => {
  try {
    loading.value = true
    
    // Fetch all analysis data
    const [performance, deptAnalysis, projAnalysis, trendAnalysis, 
           allocationAnalysis, varianceAnalysis] = await Promise.all([
      budgetStore.getBudgetPerformance(),
      budgetStore.getDepartmentalAnalysis(),
      budgetStore.getProjectAnalysis(),
      budgetStore.getTrendAnalysis(),
      budgetStore.getAllocationAnalysis(),
      budgetStore.getVarianceAnalysis()
    ])

    // Update overview cards
    overviewCards.value = overviewCards.value.map(card => {
      switch (card.id) {
        case 1:
          return { ...card, value: performance.budgeted_amount }
        case 2:
          return { ...card, value: performance.actual_amount }
        case 3:
          return { ...card, value: performance.variance, percentage: performance.variance_percentage }
        default:
          return card
      }
    })

    // Update analysis data
    departmentData.value = deptAnalysis
    projectData.value = projAnalysis
    trendData.value = trendAnalysis
    allocationData.value = allocationAnalysis
    varianceData.value = varianceAnalysis
    exportData.value = {
      performance,
      deptAnalysis,
      projAnalysis,
      trendAnalysis,
      allocationAnalysis,
      varianceAnalysis
    }

  } catch (error) {
    console.error('Error fetching budget data:', error)
  } finally {
    loading.value = false
  }
}

const handleExport = async (format: string) => {
  try {
    await budgetStore.exportData(format, exportData.value)
  } catch (error) {
    console.error('Error exporting budget data:', error)
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.budget-dashboard {
  padding: 2rem;
  background: var(--background-color);
}

.dashboard-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.department-analysis,
.project-analysis,
.trend-analysis,
.allocation-analysis,
.variance-analysis {
  background: var(--card-background);
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

h3 {
  color: var(--text-color);
  margin-bottom: 1rem;
  font-size: 1.25rem;
}

.export-options {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  z-index: 1000;
}
</style>
