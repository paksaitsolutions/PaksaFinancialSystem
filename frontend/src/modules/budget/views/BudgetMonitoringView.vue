<template>
  <div class="budget-monitoring">
    <div class="dashboard-header">
      <h1>Budget Monitoring</h1>
      <p>Monitor budget performance and track spending against allocations.</p>
    </div>

    <div class="monitoring-content">
      <!-- Filter Section -->
      <Card class="filter-card">
        <template #content>
          <div class="grid">
            <div class="col-12 md:col-3">
              <div class="field">
                <label>Budget Type</label>
                <Dropdown v-model="filters.type" :options="budgetTypes" option-label="label" option-value="value" placeholder="All Types" />
              </div>
            </div>
            <div class="col-12 md:col-3">
              <div class="field">
                <label>Status</label>
                <Dropdown v-model="filters.status" :options="statusOptions" option-label="label" option-value="value" placeholder="All Status" />
              </div>
            </div>
            <div class="col-12 md:col-3">
              <div class="field">
                <label>Period</label>
                <Dropdown v-model="filters.period" :options="periodOptions" option-label="label" option-value="value" placeholder="Current Year" />
              </div>
            </div>
            <div class="col-12 md:col-3">
              <div class="field">
                <label>&nbsp;</label>
                <Button label="Apply Filters" icon="pi pi-filter" @click="applyFilters" class="w-full" />
              </div>
            </div>
          </div>
        </template>
      </Card>

      <!-- Budget Performance Cards -->
      <div class="performance-cards">
        <Card v-for="budget in budgets" :key="budget.id" class="performance-card">
          <template #title>
            <div class="card-header">
              <span>{{ budget.name }}</span>
              <Tag :value="budget.status" :severity="getStatusSeverity(budget.status)" />
            </div>
          </template>
          <template #content>
            <div class="budget-metrics">
              <div class="metric">
                <label>Budgeted</label>
                <span class="amount budgeted">{{ formatCurrency(budget.amount) }}</span>
              </div>
              <div class="metric">
                <label>Spent</label>
                <span class="amount spent">{{ formatCurrency(budget.spent || 0) }}</span>
              </div>
              <div class="metric">
                <label>Remaining</label>
                <span class="amount remaining">{{ formatCurrency(budget.amount - (budget.spent || 0)) }}</span>
              </div>
              <div class="metric">
                <label>Utilization</label>
                <span class="percentage">{{ getUtilization(budget) }}%</span>
              </div>
            </div>
            <div class="progress-section">
              <ProgressBar :value="getUtilization(budget)" :class="getProgressClass(budget)" />
            </div>
            <div class="actions">
              <Button label="View Details" icon="pi pi-eye" size="small" @click="viewDetails(budget.id)" />
              <Button label="Add Expense" icon="pi pi-plus" size="small" outlined @click="addExpense(budget.id)" />
            </div>
          </template>
        </Card>
      </div>

      <!-- Detailed Analysis -->
      <Card class="analysis-card">
        <template #title>
          <span>Budget vs Actual Analysis</span>
        </template>
        <template #content>
          <Chart type="bar" :data="chartData" :options="chartOptions" />
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useBudgetStore } from '../store/budgetStore'

// PrimeVue Components
import Card from 'primevue/card'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import Dropdown from 'primevue/dropdown'
import ProgressBar from 'primevue/progressbar'
import Chart from 'primevue/chart'

const budgetStore = useBudgetStore()

const filters = ref({
  type: null,
  status: null,
  period: 'current_year'
})

const budgetTypes = [
  { label: 'Operational', value: 'OPERATIONAL' },
  { label: 'Capital', value: 'CAPITAL' },
  { label: 'Project', value: 'PROJECT' },
  { label: 'Department', value: 'DEPARTMENT' }
]

const statusOptions = [
  { label: 'Draft', value: 'DRAFT' },
  { label: 'Approved', value: 'APPROVED' },
  { label: 'Pending', value: 'PENDING_APPROVAL' }
]

const periodOptions = [
  { label: 'Current Year', value: 'current_year' },
  { label: 'Last Year', value: 'last_year' },
  { label: 'Q1 2024', value: 'q1_2024' },
  { label: 'Q2 2024', value: 'q2_2024' }
]

const budgets = ref([
  { id: 1, name: 'Marketing Q1', amount: 50000, spent: 35000, status: 'APPROVED', type: 'OPERATIONAL' },
  { id: 2, name: 'IT Infrastructure', amount: 100000, spent: 75000, status: 'APPROVED', type: 'CAPITAL' },
  { id: 3, name: 'HR Training', amount: 25000, spent: 18000, status: 'APPROVED', type: 'DEPARTMENT' }
])

const chartData = ref({
  labels: ['Marketing', 'IT', 'HR', 'Operations', 'Finance'],
  datasets: [
    {
      label: 'Budgeted',
      backgroundColor: '#42A5F5',
      data: [50000, 100000, 25000, 75000, 40000]
    },
    {
      label: 'Actual',
      backgroundColor: '#FFA726',
      data: [35000, 75000, 18000, 65000, 35000]
    }
  ]
})

const chartOptions = ref({
  responsive: true,
  plugins: {
    legend: { position: 'top' }
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: {
        callback: function(value) {
          return '$' + value.toLocaleString()
        }
      }
    }
  }
})

const getUtilization = (budget) => {
  return Math.round(((budget.spent || 0) / budget.amount) * 100)
}

const getProgressClass = (budget) => {
  const utilization = getUtilization(budget)
  if (utilization > 90) return 'progress-danger'
  if (utilization > 75) return 'progress-warning'
  return 'progress-success'
}

const getStatusSeverity = (status) => {
  switch (status) {
    case 'APPROVED': return 'success'
    case 'DRAFT': return 'secondary'
    case 'PENDING_APPROVAL': return 'warning'
    default: return 'info'
  }
}

const formatCurrency = (amount) => 
  new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount)

const applyFilters = () => {
  // Apply filters logic
}

const viewDetails = (id) => {
  // Navigate to budget details
}

const addExpense = (id) => {
  // Open expense dialog
}

onMounted(() => {
  budgetStore.fetchBudgets()
})
</script>

<style scoped>
.budget-monitoring {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard-header {
  margin-bottom: 2rem;
}

.dashboard-header h1 {
  font-size: 2rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 0.5rem 0;
}

.filter-card {
  margin-bottom: 2rem;
}

.field {
  margin-bottom: 1rem;
}

.field label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.performance-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.budget-metrics {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-bottom: 1rem;
}

.metric {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.metric label {
  font-size: 0.875rem;
  color: #6b7280;
}

.amount {
  font-weight: 600;
  font-size: 1.125rem;
}

.budgeted { color: #3b82f6; }
.spent { color: #f59e0b; }
.remaining { color: #10b981; }
.percentage { color: #8b5cf6; font-weight: 600; }

.progress-section {
  margin: 1rem 0;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.analysis-card {
  margin-top: 2rem;
}

.progress-success :deep(.p-progressbar-value) { background: #10b981; }
.progress-warning :deep(.p-progressbar-value) { background: #f59e0b; }
.progress-danger :deep(.p-progressbar-value) { background: #ef4444; }
</style>